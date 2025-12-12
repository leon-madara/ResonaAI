# Plan: Next Steps — Smoke Tests + Frontend Auth + Microservices Beyond MVP

**Date**: 2025-12-12  
**Status**: Active  
**Linked Report**: `ResonaAI/Progress Report/25-12-12-Phase1-Foundation-Execution-Report.md` (Next Steps items)

## Overview
Deliver the next set of platform-enabling work:
1) Add an end-to-end **docker-compose smoke test checklist** (and an optional script)  
2) Implement **real user flows in the frontend** (pages + auth integration against API Gateway)  
3) Improve key microservices **beyond MVP fallbacks** while keeping safe fallbacks when external keys are missing

## Objectives (Success Criteria)
- [ ] Smoke checklist exists and is runnable by a developer end-to-end (auth + one routed call + sync enqueue)
- [ ] Frontend can:
  - [ ] Register, login, persist token, logout
  - [ ] Guard protected pages/routes
  - [ ] Hit API Gateway with Authorization header
- [ ] Conversation Engine:
  - [ ] `/chat` works even without OpenAI key (explicit fallback)
  - [ ] When OpenAI key exists, requests are resilient (timeouts/errors handled consistently)
- [ ] Cultural Context:
  - [ ] `/context` provides retrieval-backed results from a local KB (no Pinecone required)
  - [ ] Optional caching path is in place (safe, no secrets in responses)

## Scope
- **Included**
  - Documentation: smoke checklist + command examples
  - Frontend pages necessary to avoid “blank app” experience (Login/Register/Home/Chat + basic navigation)
  - Auth integration to API Gateway `/auth/login` and `/auth/register`
  - Microservice robustness improvements without removing existing logic
- **Excluded**
  - Full vector DB + embeddings pipeline (Pinecone/Weaviate production RAG)
  - Full crisis escalation workflow (Twilio) automation
  - Full offline-first UI + background sync UX

## Implementation Steps
1. **Discovery**
   - [ ] Inspect existing `web-app/src/pages` and auth context/routing
   - [ ] Inspect existing API URLs/env configuration
2. **Smoke test checklist**
   - [ ] Create `docs/runbooks/docker-compose-smoke-test.md`
   - [ ] Add optional `scripts/smoke_test.py` that hits:
     - [ ] `POST /auth/register`
     - [ ] `POST /auth/login`
     - [ ] `GET /health`
     - [ ] `GET /cultural/context?query=...` (authorized)
     - [ ] `POST /sync/upload` (authorized; verify enqueue)
3. **Frontend pages + auth integration**
   - [ ] Ensure routes exist and render
   - [ ] Implement Login/Register pages calling API Gateway
   - [ ] Add protected route gating + token storage
   - [ ] Add a minimal Chat page that calls `POST /conversation/chat` via gateway
4. **Microservices beyond MVP**
   - [ ] Conversation Engine: harden OpenAI calls; consistent error payloads; safe fallback
   - [ ] Cultural Context: add local KB retrieval (simple keyword/TF-IDF) + optional caching
5. **Validation**
   - [ ] Run backend Python tests (already passing; keep green)
   - [ ] Manual smoke run (docker-compose) using the checklist

## Dependencies
- Docker + docker-compose available
- API Gateway running on `:8000` via `docker-compose.yml`
- Web app dev server run separately (existing project tooling)

## Files to Create/Modify
- **Create**
  - `ResonaAI/docs/runbooks/docker-compose-smoke-test.md`
  - `ResonaAI/scripts/smoke_test.py`
- **Modify**
  - `ResonaAI/web-app/src/pages/*` (as needed)
  - `ResonaAI/web-app/src/contexts/*` (auth/token handling if needed)
  - `ResonaAI/services/conversation-engine/*` (robustness)
  - `ResonaAI/services/cultural-context/*` (retrieval + caching)

## Testing Strategy
- **Automated**
  - Python unit tests remain green (`python -m pytest -q tests`)
- **Manual**
  - Follow smoke checklist and verify expected HTTP status codes + payload shapes

## Timeline
- Estimated: 2–5 days depending on depth of frontend + retrieval enhancements.

## Risks & Mitigation
- **Risk**: Frontend auth patterns already exist and we might duplicate
  - **Mitigation**: Inspect first; extend existing contexts/routes rather than rewriting.
- **Risk**: Local dev dependencies vary (Windows/Python versions)
  - **Mitigation**: Keep docker-compose smoke run as the primary “source of truth”.


