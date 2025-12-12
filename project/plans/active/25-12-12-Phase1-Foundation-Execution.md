# Plan: Phase 1 Foundation Execution (Auth + DB + Service MVP Wiring)

**Date**: 2025-12-12  
**Status**: Active  
**Links**: Master plan: `ResonaAI/Plans/Active/00-Platform-Completion-Plan.md`

## Overview
Execute the minimum critical foundation work required to make the platform *run end-to-end*:
- Real (database-backed) authentication in the API Gateway
- Database schema alignment + migrations for auth and core tables
- Bring “skeleton” microservices to an MVP level so API Gateway routing succeeds (health + core endpoints)
- Validate with tests (existing + add minimal coverage where missing)

## Objectives (Success Criteria)
- [ ] `POST /auth/register` creates a user in Postgres with a secure password hash
- [ ] `POST /auth/login` validates password and returns a JWT for that user
- [ ] DB schema has `users.password_hash` and is compatible with fresh DB init **and** existing DB volumes (migration)
- [ ] API Gateway `/health` returns healthy when Postgres + Redis are available
- [ ] API Gateway routing to core service endpoints returns non-5xx responses for:
  - [ ] `POST /conversation/chat`
  - [ ] `POST /crisis/detect`
  - [ ] `POST /safety/validate`
  - [ ] `POST /sync/upload`
  - [ ] `GET /cultural/context`
- [ ] Automated test run passes locally (`pytest`)

## Scope
- **Included**:
  - API Gateway auth correctness + security basics (hashing, validation, duplicate handling)
  - Schema fixes required for auth and platform baseline tables
  - Minimal viable endpoint behavior for missing services (not full feature depth)
  - Basic tests around auth and service contract responses
- **Excluded** (explicitly not in this execution plan):
  - Full RAG/vector DB integration (Pinecone/Weaviate)
  - Full crisis escalation (Twilio) production workflows
  - Full offline-first client implementation (IndexedDB sync UI)
  - Model training pipelines for emotion classifier

## Implementation Steps
1. **Plan & repo alignment**
   - [ ] Confirm existing schema and migrations
   - [ ] Identify runtime blockers (import errors, config issues)
2. **Database schema alignment**
   - [ ] Update `database/init.sql` to include `users.password_hash`
   - [ ] Ensure schema remains compatible with optional email/phone (anonymous users)
3. **API Gateway: real authentication**
   - [ ] Fix runtime import/type issues in `services/api-gateway/main.py` (e.g., missing `Session` import)
   - [ ] Fix settings implementation to be compatible with current dependencies (`pydantic-settings`)
   - [ ] Ensure `auth_service.py` correctly hashes/verifies and normalizes email
4. **Migrations**
   - [ ] Verify/adjust Alembic migration `001_add_password_hash.py` for safe upgrades
   - [ ] Document how to apply migrations (dev workflow)
5. **Microservice MVP implementations**
   - [ ] Conversation Engine: implement `/health`, `/chat` with safe fallback behavior when OpenAI key missing
   - [ ] Crisis Detection: implement `/health`, `/detect` with keyword-based + heuristic scoring MVP
   - [ ] Safety Moderation: implement `/health`, `/validate` with blocklist + policy checks MVP
   - [ ] Sync Service: implement `/health`, `/upload` to enqueue ops in `sync_queue` MVP
   - [ ] Cultural Context: implement `/health`, `/context` with local KB fallback MVP
6. **Testing**
   - [ ] Run pytest
   - [ ] Add minimal tests for auth flows and at least one routed endpoint contract

## Dependencies
- Postgres + Redis running via `docker-compose.yml`
- `database/init.sql` mounted into Postgres container (fresh init)
- Existing Alembic setup under `services/api-gateway/alembic/`

## Files to Create/Modify
- **Modify**:
  - `ResonaAI/database/init.sql`
  - `ResonaAI/services/api-gateway/main.py`
  - `ResonaAI/services/api-gateway/config.py`
  - `ResonaAI/services/api-gateway/database.py`
  - `ResonaAI/services/conversation-engine/main.py`
  - `ResonaAI/services/crisis-detection/main.py`
  - `ResonaAI/services/safety-moderation/main.py`
  - `ResonaAI/services/sync-service/main.py`
  - `ResonaAI/services/cultural-context/main.py`
  - `ResonaAI/tests/*` (as needed, minimal)

## Testing Strategy
- **Unit tests**:
  - Auth service: password hashing/verification and email normalization
  - API Gateway endpoints: register/login basic success + failure cases
- **Integration smoke tests**:
  - Health checks return OK when dependencies are up
  - At least one routed call through API gateway to a microservice endpoint

## Timeline
- Estimated: 1–3 days (MVP foundation), excluding deep feature work.

## Risks & Mitigation
- **Risk**: Existing Postgres volume lacks new columns (init.sql won’t re-run)
  - **Mitigation**: Keep Alembic migration and document/apply upgrades; avoid destructive schema changes.
- **Risk**: Service config uses incompatible settings base classes (pydantic v2 migration)
  - **Mitigation**: Standardize on `pydantic_settings.BaseSettings`.
- **Risk**: “MVP” service behavior could mask missing real integrations
  - **Mitigation**: Make fallback responses explicit in payloads and logs; require keys for production paths.


