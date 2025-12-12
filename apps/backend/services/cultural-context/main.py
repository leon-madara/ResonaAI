"""
Cultural Context Service
Main FastAPI application for cultural context
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os
import json
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

KB_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "kb.json")
KB_MOUNT_PATH = "/app/data/cultural-knowledge-base/kb.json"


def _load_kb() -> Dict[str, Any]:
    """
    Load cultural knowledge base from either mounted volume path or repo fallback.

    Priority:
    1) Docker volume mount: /app/data/cultural-knowledge-base/kb.json
    2) Repo fallback: services/cultural-context/data/kb.json
    """
    path = KB_MOUNT_PATH if os.path.exists(KB_MOUNT_PATH) else KB_DEFAULT_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _detect_code_switching(text: str) -> Dict[str, Any]:
    """
    Detect code-switching between English and Swahili.
    
    Returns:
        Dictionary with code_switching detected flag and detected languages.
    """
    text_lower = text.lower()
    
    # Common Swahili words/phrases
    swahili_indicators = [
        "sawa", "nimechoka", "sijambo", "huzuni", "wasiwasi", "upweke",
        "asante", "asante sana", "hofu", "pole", "pole sana", "karibu",
        "mambo", "vipi", "poa", "shida", "hakuna", "hapana", "ndiyo"
    ]
    
    # Detect Swahili words
    swahili_words_found = [word for word in swahili_indicators if word in text_lower]
    
    # Detect English words (basic check)
    english_indicators = ["i", "am", "feel", "feeling", "sad", "happy", "tired", "okay", "fine"]
    english_words_found = [word for word in english_indicators if word in text_lower]
    
    # Code-switching detected if both languages present
    code_switching_detected = len(swahili_words_found) > 0 and len(english_words_found) > 0
    
    return {
        "code_switching_detected": code_switching_detected,
        "swahili_words": swahili_words_found,
        "english_words": english_words_found,
        "intensity": "high" if len(swahili_words_found) > 2 else "medium" if len(swahili_words_found) > 0 else "low"
    }


def _detect_deflection(text: str, language: str) -> Dict[str, Any]:
    """
    Detect deflection patterns, especially Swahili polite deflections.
    
    Returns:
        Dictionary with deflection detected flag and pattern matched.
    """
    text_lower = text.lower()
    
    # Swahili deflection patterns
    swahili_deflections = {
        "sawa": "Polite deflection - may indicate not ready to discuss",
        "sijambo": "Stoic response - may mask deeper feelings",
        "hakuna shida": "No problem - may minimize concerns",
        "poa": "Cool/fine - casual deflection"
    }
    
    # English deflection patterns
    english_deflections = {
        "i'm fine": "Common deflection",
        "it's okay": "Minimizing response",
        "no problem": "Dismissive response",
        "nothing": "Stoic response"
    }
    
    deflection_patterns = swahili_deflections if language == "sw" else english_deflections
    deflection_patterns.update(swahili_deflections)  # Always check Swahili patterns
    
    detected_deflections = []
    for pattern, meaning in deflection_patterns.items():
        if pattern in text_lower:
            detected_deflections.append({
                "pattern": pattern,
                "meaning": meaning,
                "language": "sw" if pattern in swahili_deflections else "en"
            })
    
    return {
        "deflection_detected": len(detected_deflections) > 0,
        "patterns": detected_deflections
    }


def _retrieve_entries(kb: Dict[str, Any], query: str, language: str) -> List[Dict[str, Any]]:
    """
    Simple keyword-based retrieval with enhanced pattern matching.

    Purpose:
    - Provide retrieval-backed responses without requiring a vector DB.
    - Includes code-switching and deflection detection.
    """
    q = query.lower()
    entries = kb.get("entries", []) or []

    scored: List[Dict[str, Any]] = []
    for e in entries:
        # Match language or allow cross-language matches for code-switching
        entry_language = e.get("language")
        if entry_language and entry_language not in (None, "", language):
            # Still check if it's a Swahili entry when query might have code-switching
            code_switching_info = _detect_code_switching(query)
            if not (code_switching_info["code_switching_detected"] and entry_language == "sw"):
                continue
        
        keywords = [k.lower() for k in (e.get("keywords") or [])]
        score = sum(1 for k in keywords if k in q)
        if score > 0:
            scored.append({"score": score, "entry": e})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return [s["entry"] for s in scored[:3]]


def _get_cache(context_key: str) -> Optional[Dict[str, Any]]:
    """Fetch cached context if present and not expired."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT context_data
                    FROM cultural_context_cache
                    WHERE context_key = :key
                      AND (expires_at IS NULL OR expires_at > NOW())
                    """
                ),
                {"key": context_key},
            ).fetchone()
        if not row:
            return None
        return row[0]
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
        return None


def _set_cache(context_key: str, payload: Dict[str, Any], language: str) -> None:
    """Upsert cached context payload (best-effort)."""
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO cultural_context_cache (context_key, context_data, language, region, created_at, updated_at)
                    VALUES (:key, :data::jsonb, :language, 'east_africa', NOW(), NOW())
                    ON CONFLICT (context_key)
                    DO UPDATE SET context_data = EXCLUDED.context_data, updated_at = NOW()
                    """
                ),
                {"key": context_key, "data": json.dumps(payload), "language": language},
            )
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Cultural Context Service...")
    yield
    logger.info("Shutting down Cultural Context Service...")

app = FastAPI(title="Cultural Context Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")

    return {"status": "healthy", "service": "cultural-context", "db_connected": db_ok}

@app.get("/context")
async def get_cultural_context(
    query: str,
    language: str = "en",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cultural context for a query"""
    q = (query or "").strip()
    if not q:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="query is required")

    context_key = f"{language}:{q.lower()}"
    cached = _get_cache(context_key)
    if cached:
        cached["source"] = "db_cache"
        cached["timestamp"] = datetime.utcnow().isoformat()
        return cached

    kb = _load_kb()
    retrieved = _retrieve_entries(kb, q, language)
    
    # Detect code-switching and deflection
    code_switching_info = _detect_code_switching(q)
    deflection_info = _detect_deflection(q, language)

    context_lines = [
        "Be mindful of East African norms around privacy, respect, and indirect expression of distress.",
        "Avoid stigmatizing language; normalize help-seeking and community support.",
        "If the user prefers Swahili or code-switching, mirror their language style gently.",
    ]
    
    # Add code-switching context if detected
    if code_switching_info["code_switching_detected"]:
        context_lines.append(
            f"Code-switching detected (intensity: {code_switching_info['intensity']}). "
            "The user may be expressing something important that's easier to say in their native language. "
            "Pay attention to emotional intensity."
        )
    
    # Add deflection context if detected
    if deflection_info["deflection_detected"]:
        deflection_meanings = [p["meaning"] for p in deflection_info["patterns"]]
        context_lines.append(
            f"Deflection patterns detected: {', '.join(deflection_meanings)}. "
            "The user may not be ready to discuss their feelings directly. Be patient and offer gentle follow-up."
        )

    retrieval_text = "\n\n".join([e.get("content", "") for e in retrieved if e.get("content")]) if retrieved else ""
    full_context = "\n".join(context_lines) + (("\n\n" + retrieval_text) if retrieval_text else "")

    payload = {
        "context": full_context,
        "language": language,
        "query": q,
        "source": "local_kb_retrieval" if retrieved else "mvp_fallback",
        "matches": [{"id": e.get("id"), "keywords": e.get("keywords")} for e in retrieved],
        "code_switching": code_switching_info,
        "deflection": deflection_info,
        "timestamp": datetime.utcnow().isoformat(),
    }

    _set_cache(context_key, payload, language)
    return payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT)

