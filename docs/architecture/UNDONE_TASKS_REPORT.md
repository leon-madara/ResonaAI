# Pending Tasks Report (Current Reality)

**Last Updated**: 2025-12-14  
**Scope**: What’s left to do based on current repo state (code + tests + CI + docs).  

## Sources of Truth Used

- **System design**: `docs/architecture/system-design.md`
- **Project rules/status mapping**: `docs/architecture/PROJECT_RULES_AND_STATUS.md`
- **Test status**: `tests/TEST_STATUS_REPORT.md`, `tests/INTEGRATION_TESTS_SUMMARY.md`
- **Agent OS standards**: `.agent-os/standards/coding-standards.md`, `.agent-os/standards/testing-standards.md`, `.agent-os/standards/security-standards.md`
- **Code reality checks**:
  - Grep for TODOs in backend services
  - Verified encryption batch endpoints + tests use JSON body
  - Verified Cultural Context has tests but still has skip-based provider availability checks
  - Verified API Gateway interface config endpoints no longer use `sys.path` hacks and now return a real per-user salt when available
  - Verified sync-service workers persist conversation/emotion/baseline/preferences with idempotency + retry bookkeeping tests
  - Verified conversation-engine stores messages encrypted-at-rest via encryption-service (and decrypts history for GPT context)
  - Verified emotion-analysis local pipeline performs preprocess + feature extraction + prediction with deterministic fixture test
  - **Frontend TypeScript compilation errors fixed** (2025-12-14):
    - `ConversationUI.tsx`: Fixed missing `id` property when creating Message objects (TS2741)
    - `VoiceRecorder.tsx`: Fixed void expression truthiness check for `stopRecording()` return (TS1345)
    - `VoiceRecorder.tsx`: Fixed React hooks dependency for `processRecording` (react-hooks/exhaustive-deps)
    - `OfflineContext.tsx`: Fixed React hooks dependency for `processSyncQueue` using refs pattern (react-hooks/exhaustive-deps)

---

## Summary

Most core services, database schema/migrations, and major test coverage exist. The largest remaining gaps are:

- **Documentation drift** (several “status” docs contradict repo reality).
- **Auth context propagation** (services still use placeholders instead of extracting identity from JWT claims).
- **CI quality gates** (CI currently allows failures via `continue-on-error: true`).
- **E2E/performance/security automation** (standards mention them; implementation is incomplete).

---

## 🔴 P0 — Critical (Blocks production safety/security)

No P0 items currently outstanding (resolved 2025-12-14):

- **P0-01**: Crisis escalation workflow persisted + state transitions + tests (`apps/backend/services/crisis-detection/`)
- **P0-02**: Safety moderation JWT identity attribution + admin gating + tests (`apps/backend/services/safety-moderation/`)
- **P0-03**: API Gateway duplicate `POST /auth/register` removed (single canonical route) (`apps/backend/gateway/main.py`)

---

## 🟠 P1 — High (Core functionality correctness + offline-first)

No P1 items currently outstanding.

---

## 🟡 P2 — Medium (Quality, reliability, and developer velocity)

### P2-01 — Documentation drift cleanup (make docs match code)
- **Evidence**:
  - `tests/TEST_STATUS_REPORT.md` claims encryption batch tests are skipped, but current encryption tests call `/e2e/batch-encrypt` and `/e2e/batch-decrypt` with JSON bodies.
  - `project/backlog/03-Micro-Moment-Detector.md` claims `src/micro_moment_detector.py` “does not exist”, but it exists.
  - Multiple architecture/status docs are clearly written at different times and contradict each other.
- **Acceptance criteria**:
  - Update these to reflect current repo reality:
    - `docs/architecture/IMPLEMENTATION_REVIEW.md`
    - `docs/architecture/STATUS_SUMMARY.md`
    - `docs/architecture/PROJECT_RULES_AND_STATUS.md` (only outdated sections)
    - `tests/TEST_STATUS_REPORT.md` (remove outdated “batch endpoints skipped” note)
    - `project/backlog/*` items that still claim “does not exist” for implemented modules

### P2-02 — CI should enforce quality gates (stop allowing silent failures)
- **Evidence**: `.github/workflows/ci.yml` uses `continue-on-error: true` for lint, format, tests, and Codecov upload
- **Acceptance criteria**:
  - CI fails on lint failures and test failures
  - Coverage threshold enforced for critical modules (per `.agent-os/standards/testing-standards.md`)
  - CI test execution strategy matches current reality (per-service runs or isolated execution)

### P2-03 — Reduce/remove module caching conflicts in tests
- **Evidence**: tests manipulate `sys.path` and `sys.modules` to isolate services
- **Acceptance criteria**:
  - Services importable via stable package paths
  - “Run all tests” works in one command OR isolation is enforced in CI in a standardized way

### P2-04 — Cultural Context tests should not depend on external embedding/RAG availability
- **Evidence**: `tests/services/cultural-context/test_embeddings.py` and `test_integration.py` skip when embedding/RAG unavailable
- **Acceptance criteria**:
  - Deterministic unit tests using mocks or local fallback
  - Skips reserved only for optional provider integration tests

---

## 🟢 P3 — Low (Enhancements / future scale)

### P3-01 — True end-to-end (E2E) user journey tests
- **Acceptance criteria**:
  - E2E covers: register/login, voice upload → transcript → emotion → response → safety filter → crisis path
  - Runs as a separate CI job (on demand or nightly)

### P3-02 — Performance + security automation (align with Agent OS standards)
- **Acceptance criteria**:
  - Baseline performance tests for critical endpoints/services
  - Dependency vulnerability scanning and basic SAST in CI

---

## Notes

- This file intentionally lists **pending work only**. Older “completion claims” that conflict with current code/test reality should be moved into completed/progress reports, not kept here.
