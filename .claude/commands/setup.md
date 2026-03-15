---
description: Run all fresh setup steps for a newly cloned repo from the template — configure env, start infrastructure, create test DB, run migrations, and verify the server starts. Usage: /setup
argument-hint: ""
allowed-tools: Bash, Read, Write, Edit
---

You are performing a guided first-time setup for this FastAPI financial boilerplate project.
The user has already cloned their repo from the template and is in the correct Python environment.

Work through each step **in order**. After each step, verify it succeeded before continuing.
If a step fails, stop, explain the error clearly, and suggest a fix — do not proceed past failures.

---

## Step 1 — Verify Python environment

Check that the active Python is 3.12+ and that we're inside a virtual or conda environment (not the system Python).

```bash
python --version
which python
```

- If Python < 3.12 → stop and tell the user to activate the correct environment.
- Print which Python is active and confirm it looks correct.

---

## Step 2 — Install dependencies

```bash
make dev
```

This installs all production and dev/test dependencies. If `make` is not available:

```bash
pip install -r requirements-dev.txt
```

Verify the install succeeded by checking a key package:

```bash
python -c "import fastapi; print('FastAPI', fastapi.__version__)"
```

---

## Step 3 — Configure environment

Check whether `.env` already exists:

```bash
ls -la .env 2>/dev/null && echo "EXISTS" || echo "MISSING"
```

- If `.env` is **missing** → copy from the example:

```bash
cp .env.example .env
```

- If `.env` already exists → skip the copy, but still check it (Step 4).

---

## Step 4 — Validate `.env` required fields

Read `.env` and check that these critical fields are set (non-empty, not still the placeholder from `.env.example`):

```bash
python -c "
import os
from dotenv import dotenv_values
env = dotenv_values('.env')
required = ['DATABASE_URL', 'REDIS_URL', 'JWT_SECRET_KEY']
missing = [k for k in required if not env.get(k) or env[k].startswith('<')]
if missing:
    print('MISSING OR PLACEHOLDER:', missing)
else:
    print('OK - all required fields are set')
    jwt = env.get('JWT_SECRET_KEY', '')
    if len(jwt) < 32:
        print('WARNING: JWT_SECRET_KEY is too short (min 32 chars). Generate one with: openssl rand -hex 32')
"
```

If any required field is missing or still a placeholder, print the specific variable and the command to generate/set it:

- `JWT_SECRET_KEY` → `openssl rand -hex 32`
- `DATABASE_URL` → should match the Docker postgres service: `postgresql+asyncpg://postgres:postgres@localhost:5432/boilerplate_db`
- `REDIS_URL` → `redis://localhost:6379/0`

Do **not** write any values into `.env` automatically — tell the user what to set and let them edit it.

Wait for the user to confirm they have updated `.env` before continuing if any field was missing.

---

## Step 5 — Start infrastructure

Start PostgreSQL and Redis:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

Wait for health checks to pass (up to 30 seconds):

```bash
for i in $(seq 1 6); do
  STATUS=$(docker compose -f docker/docker-compose.yml ps --format json 2>/dev/null | python -c "
import sys, json
lines = sys.stdin.read().strip().split('\n')
services = [json.loads(l) for l in lines if l]
healthy = all(s.get('Health') == 'healthy' for s in services if s.get('Service') in ['postgres', 'redis'])
print('healthy' if healthy else 'waiting')
" 2>/dev/null || echo "waiting")
  if [ "$STATUS" = "healthy" ]; then
    echo "✓ All services healthy"
    break
  fi
  echo "Waiting for services... ($i/6)"
  sleep 5
done

docker compose -f docker/docker-compose.yml ps
```

If services are not healthy after 30 seconds, show the logs and stop:

```bash
docker compose -f docker/docker-compose.yml logs postgres redis
```

---

## Step 6 — Create the test database

Check whether the test database already exists:

```bash
docker compose -f docker/docker-compose.yml exec postgres \
  psql -U postgres -lqt | grep -c boilerplate_test_db || echo "0"
```

- If `0` (not found) → create it:

```bash
docker compose -f docker/docker-compose.yml exec postgres \
  psql -U postgres -c "CREATE DATABASE boilerplate_test_db;"
```

- If it already exists → print "Test database already exists — skipping."

---

## Step 7 — Run migrations

```bash
make migrate
```

Verify the schema is up to date:

```bash
python -m alembic current
```

If alembic reports an error (e.g. `Target database is not up to date`), run:

```bash
python -m alembic upgrade head
```

---

## Step 8 — Run unit tests

Confirm the codebase is in a working state before starting the server:

```bash
make test-unit
```

- If tests pass → continue.
- If tests fail → show the failure output and stop. The user may have modified template files; they should fix the failures before proceeding.

---

## Step 9 — Start the server (smoke test)

Start the server in the background for a quick smoke test:

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 4

# Hit the health check
HTTP_STATUS=$(curl -s -o /tmp/health_response.json -w "%{http_code}" http://localhost:8000/api/v1/health)
cat /tmp/health_response.json

# Stop the background server
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
```

- If `HTTP_STATUS` is `200` → setup is complete.
- If the health check shows any service as `"unavailable"` → print which service failed and link to the relevant troubleshooting section.
- If the server failed to start → show the startup error output.

---

## Step 10 — Setup complete summary

Print a summary of what was done:

```
✅ Setup complete!

  Python:      <version>
  Environment: <venv/conda path>
  Database:    postgresql://localhost:5432/boilerplate_db  (healthy)
  Redis:       redis://localhost:6379/0  (healthy)
  Migrations:  up to date
  Unit tests:  passed

Start the dev server:
  make run

Open the API:
  http://localhost:8000/docs        ← Swagger UI
  http://localhost:8000/redoc       ← ReDoc
  http://localhost:8000/api/v1/health

Next steps:
  - Edit .env and set your GCS credentials (needed for file uploads and health check storage)
  - Read docs/guide/adding-a-bounded-context.md to add your first feature
  - Run /plan <your feature> to start planning
```

If GCS was not configured (health check showed `storage: unavailable`), add:

```
⚠️  GCS not configured — storage operations will fail.
    See: docs/guide/getting-started.md#gcs-setup--create-a-service-account-and-bucket
```
