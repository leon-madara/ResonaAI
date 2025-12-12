# Docker Compose Smoke Test Checklist

This checklist verifies the minimal end-to-end functionality of the platform via the **API Gateway**.

## Prereqs
- Docker + docker-compose installed
- Env vars set (at minimum):
  - `JWT_SECRET_KEY`
  - Optional for deeper testing: `OPENAI_API_KEY`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`

## 1) Start the stack

From `ResonaAI/`:

```bash
docker compose up --build -d
```

Wait until containers are healthy.

## 2) Health check (Gateway)

```bash
curl -s http://localhost:8000/health
```

Expected:
- HTTP 200
- JSON includes `"status": "healthy"`

## 3) Register + Login

Register:

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"smoke_test@example.com\",\"password\":\"password123\",\"consent_version\":\"1.0\",\"is_anonymous\":true}"
```

Login:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"smoke_test@example.com\",\"password\":\"password123\"}"
```

Expected:
- `access_token` returned

## 4) Cultural context (authorized GET)

Replace `$TOKEN`:

```bash
curl -s "http://localhost:8000/cultural/context?query=I%20feel%20tired&language=en" \
  -H "Authorization: Bearer $TOKEN"
```

Expected:
- HTTP 200
- JSON contains `context`, `source`

## 5) Sync upload (authorized POST)

```bash
curl -s -X POST http://localhost:8000/sync/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"user_id\":\"00000000-0000-0000-0000-000000000000\",\"operation_type\":\"smoke_test\",\"data\":{\"hello\":\"world\"}}"
```

Expected:
- HTTP 200
- JSON contains `sync_id` and `status` (queued)

## Optional: use the helper script

Run:

```bash
python ResonaAI/scripts/smoke_test.py
```


