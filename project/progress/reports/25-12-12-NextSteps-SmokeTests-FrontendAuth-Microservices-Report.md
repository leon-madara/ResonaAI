# Progress Report: Next Steps — Smoke Tests + Frontend Auth + Microservices Beyond MVP

**Date**: 2025-12-12  
**Status**: Complete (for the specified Next Steps items)  
**Completion**: 100% of the requested “Next Steps” items (72–74)

**Plan Link**: `ResonaAI/Plans/Active/25-12-12-NextSteps-SmokeTests-FrontendAuth-Microservices.md`

## Summary
Completed the three Next Steps items from `25-12-12-Phase1-Foundation-Execution-Report.md`:
- Added a docker-compose **smoke test checklist** + a small Python runner script
- Wired the **web app** to the API Gateway for auth + key routes (no more `/api/*` placeholders)
- Improved microservices **beyond MVP fallbacks**:
  - Conversation engine OpenAI calls are safer (threaded for v1 client; robust when library/key missing)
  - Cultural context now supports local KB retrieval + best-effort DB cache (still falls back safely)

## Files Created
- `ResonaAI/docs/runbooks/docker-compose-smoke-test.md`
- `ResonaAI/scripts/smoke_test.py`
- `ResonaAI/web-app/src/utils/api.ts`
- `ResonaAI/services/cultural-context/data/kb.json`
- `ResonaAI/Progress Report/25-12-12-NextSteps-SmokeTests-FrontendAuth-Microservices-Report.md`

## Files Modified
- `ResonaAI/web-app/src/contexts/AuthContext.tsx`
  - Switched auth calls to API Gateway (`/auth/login`, `/auth/register`)
  - Fixed request payload keys (`consent_version`, `is_anonymous`)
  - Removed non-existent `/api/user/profile` call and uses a minimal stored user object
- `ResonaAI/web-app/src/components/ConversationUI/ConversationUI.tsx`
  - Uses API Gateway (`/conversation/chat`) with JSON payload and correct response field (`message`)
- `ResonaAI/web-app/src/components/VoiceRecorder/VoiceRecorder.tsx`
  - Uses API Gateway (`/speech/transcribe`) and shared auth header helper
- `ResonaAI/services/conversation-engine/services/gpt_service.py`
  - Robust handling when OpenAI library/key missing
  - OpenAI v1 calls run in a thread to avoid blocking the event loop
- `ResonaAI/services/cultural-context/main.py`
  - Added local KB retrieval (keyword-based) + DB cache support (best-effort)
  - Health now reports DB connectivity
- `ResonaAI/services/cultural-context/requirements.txt`
  - Added `pydantic-settings` to match config usage

## Testing
- **Python unit tests**: unchanged and remain green (`python -m pytest -q tests`)
- **Smoke testing**: documented in `docs/runbooks/docker-compose-smoke-test.md` and runnable via `scripts/smoke_test.py`

## Notes / Known Follow-ups
- Login endpoint does not return `user_id`; the frontend currently stores a minimal user object on login.
  - Follow-up: either decode JWT in the frontend or add a `/me` endpoint in API Gateway.


