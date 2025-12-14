"""
Celery tasks for sync service
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time
import uuid

from workers.celery_app import celery_app
from services.conflict_resolver import get_conflict_resolver

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/mental_health")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_UUID_NAMESPACE = uuid.UUID("b2b9b6e4-59d0-4f13-ae0a-9f7f0b0d9e1a")


def _to_uuid(value: Any, *, user_id: str, discriminator: str) -> uuid.UUID:
    """
    Convert a value to UUID.

    Purpose:
    - Support offline-first clients that generate local IDs before a UUID is assigned.

    Behavior:
    - If `value` is already a UUID or UUID-like string, parse it.
    - Otherwise, derive a stable UUIDv5 using (user_id, discriminator, value).
    """
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except Exception:
        seed = f"{user_id}:{discriminator}:{value}"
        return uuid.uuid5(_UUID_NAMESPACE, seed)


def _parse_iso_ts(value: Any) -> Optional[datetime]:
    """Parse an ISO timestamp (best-effort)."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return None


@celery_app.task(bind=True, max_retries=3)
def process_sync_operation(
    self,
    sync_id: str,
    user_id: str,
    operation_type: str,
    payload: Dict[str, Any]
):
    """
    Process a sync operation in the background.
    
    Args:
        sync_id: Sync operation ID
        user_id: User ID
        operation_type: Type of operation
        payload: Operation payload
    """
    db = SessionLocal()
    try:
        result, should_retry = _handle_sync_operation(db, sync_id, user_id, operation_type, payload)
        db.commit()
        if should_retry:
            raise Exception(result.get("error", "Sync operation failed"))
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing sync operation {sync_id}: {e}")

        # Retry with exponential backoff (Celery-managed).
        try:
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            # Mark as failed after max retries
            db.execute(
                text("""
                    UPDATE sync_queue
                    SET status = 'failed', retry_count = :retry_count
                    WHERE id = :id
                """),
                {"id": sync_id, "retry_count": 3}
            )
            db.commit()
            logger.error(f"Sync operation {sync_id} failed after max retries")
            return {"success": False, "error": str(e)}
    finally:
        db.close()


def _handle_sync_operation(
    db,
    sync_id: str,
    user_id: str,
    operation_type: str,
    payload: Dict[str, Any],
) -> tuple[Dict[str, Any], bool]:
    """
    Handle a sync operation within an existing DB session.

    Returns:
      (result, should_retry)
    """
    logger.info(f"Processing sync operation: {sync_id}")

    # Update status to processing
    db.execute(
        text("""
            UPDATE sync_queue
            SET status = 'processing', processed_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {"id": sync_id}
    )

    # Process based on operation type
    if operation_type == "conversation_sync":
        result = _process_conversation_sync(db, user_id, payload)
    elif operation_type == "emotion_data_sync":
        result = _process_emotion_sync(db, user_id, payload)
    elif operation_type == "baseline_update":
        result = _process_baseline_update(db, user_id, payload)
    elif operation_type == "user_preference_sync":
        result = _process_preference_sync(db, user_id, payload)
    else:
        result = {"success": False, "error": f"Unknown operation type: {operation_type}"}

    # Update status based on result
    if result.get("success"):
        db.execute(
            text("""
                UPDATE sync_queue
                SET status = 'completed', processed_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {"id": sync_id}
        )
        logger.info(f"Sync operation completed: {sync_id}")
        return result, False

    # Failure: increment retry count and re-queue
    db.execute(
        text("""
            UPDATE sync_queue
            SET status = 'pending',
                retry_count = retry_count + 1,
                processed_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {"id": sync_id}
    )
    logger.error(f"Sync operation failed: {sync_id}, error: {result.get('error')}")

    retry_count = db.execute(
        text("SELECT retry_count FROM sync_queue WHERE id = :id"),
        {"id": sync_id}
    ).scalar()

    should_retry = bool(retry_count is not None and int(retry_count) < 3)
    return result, should_retry


def _process_conversation_sync(db, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process conversation sync operation"""
    try:
        conversation_id = payload.get("conversation_id")
        messages = payload.get("messages", [])

        if not conversation_id:
            return {"success": False, "error": "Missing conversation_id"}

        user_uuid = _to_uuid(user_id, user_id=user_id, discriminator="user")
        conv_uuid = _to_uuid(conversation_id, user_id=user_id, discriminator="conversation")

        # Ensure conversation exists (idempotent).
        existing = db.execute(
            text("SELECT id FROM conversations WHERE id = :id"),
            {"id": str(conv_uuid)},
        ).fetchone()
        if not existing:
            db.execute(
                text(
                    """
                    INSERT INTO conversations (id, user_id, started_at, emotion_summary, crisis_detected, escalated_to_human)
                    VALUES (:id, :user_id, CURRENT_TIMESTAMP, NULL, false, false)
                    """
                ),
                {"id": str(conv_uuid), "user_id": str(user_uuid)},
            )

        inserted = 0
        skipped = 0
        errors: list[str] = []

        for msg in messages if isinstance(messages, list) else []:
            if not isinstance(msg, dict):
                errors.append("Invalid message entry (not an object)")
                continue

            client_msg_id = msg.get("id") or msg.get("message_id")
            if not client_msg_id:
                errors.append("Message missing id")
                continue

            msg_uuid = _to_uuid(client_msg_id, user_id=user_id, discriminator=f"message:{conv_uuid}")
            msg_type = msg.get("message_type") or msg.get("type") or "user"
            msg_type = msg_type if msg_type in ("user", "ai") else "user"
            content = msg.get("content")
            if content is None:
                errors.append(f"Message {client_msg_id} missing content")
                continue

            created_at = _parse_iso_ts(msg.get("timestamp") or msg.get("created_at")) or datetime.now(timezone.utc)
            emotion_data = msg.get("emotion_data")

            # Idempotent insert: if message exists, skip.
            exists = db.execute(
                text("SELECT id FROM messages WHERE id = :id"),
                {"id": str(msg_uuid)},
            ).fetchone()
            if exists:
                skipped += 1
                continue

            db.execute(
                text(
                    """
                    INSERT INTO messages (id, conversation_id, message_type, encrypted_content, emotion_data, created_at)
                    VALUES (:id, :conversation_id, :message_type, :encrypted_content, :emotion_data, :created_at)
                    """
                ),
                {
                    "id": str(msg_uuid),
                    "conversation_id": str(conv_uuid),
                    "message_type": msg_type,
                    # NOTE: plaintext bytes for MVP; conversation-engine P1-02 will make this encrypted-at-rest.
                    "encrypted_content": str(content).encode("utf-8"),
                    "emotion_data": json.dumps(emotion_data) if isinstance(emotion_data, dict) else None,
                    "created_at": created_at,
                },
            )
            inserted += 1

        logger.info(
            f"Synced conversation {conv_uuid} for user {user_uuid}: inserted={inserted}, skipped={skipped}, errors={len(errors)}"
        )
        return {
            "success": True,
            "conversation_id": str(conv_uuid),
            "messages_inserted": inserted,
            "messages_skipped": skipped,
            "messages_failed": len(errors),
            "errors": errors,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _process_emotion_sync(db, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process emotion data sync operation"""
    try:
        emotion_data = payload.get("emotion_data", [])
        user_uuid = _to_uuid(user_id, user_id=user_id, discriminator="user")

        inserted = 0
        skipped = 0
        errors: list[str] = []

        for i, entry in enumerate(emotion_data if isinstance(emotion_data, list) else []):
            if not isinstance(entry, dict):
                errors.append(f"emotion_data[{i}] invalid (not an object)")
                continue

            record_id = entry.get("id") or entry.get("emotion_id")
            conversation_id = entry.get("conversation_id")
            message_id = entry.get("message_id")
            emotion_type = entry.get("emotion") or entry.get("emotion_type") or "neutral"
            confidence = entry.get("confidence") or entry.get("confidence_score") or 0.5
            created_at = _parse_iso_ts(entry.get("timestamp") or entry.get("created_at")) or datetime.now(timezone.utc)

            conv_uuid = _to_uuid(conversation_id, user_id=user_id, discriminator="conversation") if conversation_id else None
            msg_uuid = _to_uuid(message_id, user_id=user_id, discriminator=f"message:{conv_uuid}") if message_id else None

            if record_id:
                rec_uuid = _to_uuid(record_id, user_id=user_id, discriminator="emotion")
            else:
                rec_uuid = uuid.uuid5(
                    _UUID_NAMESPACE,
                    f"{user_id}:emotion:{conv_uuid}:{msg_uuid}:{emotion_type}:{created_at.isoformat()}",
                )

            exists = db.execute(
                text("SELECT id FROM emotion_history WHERE id = :id"),
                {"id": str(rec_uuid)},
            ).fetchone()
            if exists:
                skipped += 1
                continue

            db.execute(
                text(
                    """
                    INSERT INTO emotion_history (
                        id, user_id, conversation_id, message_id,
                        emotion_type, confidence_score, voice_emotion, text_sentiment, created_at
                    )
                    VALUES (
                        :id, :user_id, :conversation_id, :message_id,
                        :emotion_type, :confidence_score, :voice_emotion, :text_sentiment, :created_at
                    )
                    """
                ),
                {
                    "id": str(rec_uuid),
                    "user_id": str(user_uuid),
                    "conversation_id": str(conv_uuid) if conv_uuid else None,
                    "message_id": str(msg_uuid) if msg_uuid else None,
                    "emotion_type": str(emotion_type),
                    "confidence_score": float(confidence),
                    "voice_emotion": json.dumps(entry.get("voice_emotion")) if isinstance(entry.get("voice_emotion"), dict) else None,
                    "text_sentiment": json.dumps(entry.get("text_sentiment")) if isinstance(entry.get("text_sentiment"), dict) else None,
                    "created_at": created_at,
                },
            )
            inserted += 1

        logger.info(f"Synced emotion history for user {user_uuid}: inserted={inserted}, skipped={skipped}, errors={len(errors)}")
        return {
            "success": True,
            "emotions_inserted": inserted,
            "emotions_skipped": skipped,
            "emotions_failed": len(errors),
            "errors": errors,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _process_baseline_update(db, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process baseline update operation"""
    try:
        baseline_data = payload.get("baseline_data")

        if not isinstance(baseline_data, dict):
            return {"success": False, "error": "baseline_data must be an object"}

        user_uuid = _to_uuid(user_id, user_id=user_id, discriminator="user")
        baseline_type = baseline_data.get("baseline_type") or payload.get("baseline_type") or "voice"
        local_ts = _parse_iso_ts(baseline_data.get("updated_at") or baseline_data.get("timestamp") or payload.get("timestamp"))
        session_count = int(baseline_data.get("session_count") or baseline_data.get("sessions_analyzed") or 0)

        existing = db.execute(
            text(
                """
                SELECT baseline_value, updated_at, session_count
                FROM user_baselines
                WHERE user_id = :user_id AND baseline_type = :baseline_type
                """
            ),
            {"user_id": str(user_uuid), "baseline_type": str(baseline_type)},
        ).fetchone()

        resolver = get_conflict_resolver()

        if existing:
            remote_value = existing.baseline_value
            if isinstance(remote_value, (str, bytes)):
                try:
                    remote_value = json.loads(remote_value)
                except Exception:
                    # Keep as-is if it's not JSON.
                    pass
            remote_ts = existing.updated_at
            if not isinstance(remote_ts, datetime):
                remote_ts = _parse_iso_ts(remote_ts)
            remote_count = int(existing.session_count or 0)
            resolved = resolver.resolve(
                local_data={**baseline_data, "updated_at": local_ts.isoformat() if local_ts else None},
                remote_data={"baseline_value": remote_value, "updated_at": remote_ts.isoformat() if remote_ts else None},
                strategy=payload.get("strategy") or "last_write_wins",
                user_preference=payload.get("user_preference"),
            )
            resolved_value = resolved.get("baseline_value") if "baseline_value" in resolved else baseline_data
            resolved_count = max(remote_count, session_count)

            db.execute(
                text(
                    """
                    UPDATE user_baselines
                    SET baseline_value = :baseline_value,
                        session_count = :session_count,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id AND baseline_type = :baseline_type
                    """
                ),
                {
                    "baseline_value": json.dumps(resolved_value),
                    "session_count": resolved_count,
                    "user_id": str(user_uuid),
                    "baseline_type": str(baseline_type),
                },
            )
        else:
            db.execute(
                text(
                    """
                    INSERT INTO user_baselines (user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
                    VALUES (:user_id, :baseline_type, :baseline_value, :session_count, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                ),
                {
                    "user_id": str(user_uuid),
                    "baseline_type": str(baseline_type),
                    "baseline_value": json.dumps(baseline_data),
                    "session_count": session_count,
                },
            )

        logger.info(f"Baseline updated for user {user_uuid} type={baseline_type}")
        return {"success": True, "baseline_updated": True, "baseline_type": str(baseline_type)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _process_preference_sync(db, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process user preference sync operation"""
    try:
        preferences = payload.get("preferences", {})

        if not isinstance(preferences, dict):
            return {"success": False, "error": "preferences must be an object"}

        user_uuid = _to_uuid(user_id, user_id=user_id, discriminator="user")
        local_ts = _parse_iso_ts(payload.get("updated_at") or payload.get("timestamp"))
        resolver = get_conflict_resolver()

        existing = db.execute(
            text("SELECT preferences, updated_at FROM user_preferences WHERE user_id = :user_id"),
            {"user_id": str(user_uuid)},
        ).fetchone()

        if existing:
            remote_prefs = existing.preferences
            if isinstance(remote_prefs, (str, bytes)):
                try:
                    remote_prefs = json.loads(remote_prefs)
                except Exception:
                    pass
            remote_ts = existing.updated_at
            if not isinstance(remote_ts, datetime):
                remote_ts = _parse_iso_ts(remote_ts)
            resolved = resolver.resolve(
                local_data={**preferences, "updated_at": local_ts.isoformat() if local_ts else None},
                remote_data={"preferences": remote_prefs, "updated_at": remote_ts.isoformat() if remote_ts else None},
                strategy=payload.get("strategy") or "last_write_wins",
                user_preference=payload.get("user_preference"),
            )
            resolved_prefs = resolved.get("preferences") if "preferences" in resolved else resolved
            db.execute(
                text(
                    """
                    UPDATE user_preferences
                    SET preferences = :preferences, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                    """
                ),
                {"preferences": json.dumps(resolved_prefs), "user_id": str(user_uuid)},
            )
        else:
            db.execute(
                text(
                    """
                    INSERT INTO user_preferences (user_id, preferences, created_at, updated_at)
                    VALUES (:user_id, :preferences, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                ),
                {"user_id": str(user_uuid), "preferences": json.dumps(preferences)},
            )

        logger.info(f"Preferences synced for user {user_uuid}")
        return {"success": True, "preferences_synced": len(preferences)}
    except Exception as e:
        return {"success": False, "error": str(e)}

