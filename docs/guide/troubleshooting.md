# Troubleshooting

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Configuration](configuration.md)

---

## `make: uvicorn: No such file or directory`

**Symptom:** `make run` (or any make target) fails with `No such file or directory`.

**Cause:** `make` runs in a clean shell that doesn't inherit conda environment activation. The tool binaries are not on its `PATH`.

**Fix:** All Makefile targets already use `python -m <tool>` to resolve through the active Python. Make sure your conda environment is activated before running `make`:

```bash
conda activate <your-env>
make run
```

---

## `ALLOWED_ORIGINS` parse error on startup

**Symptom:** `pydantic_settings.exceptions.SettingsError: error parsing value for field "allowed_origins"`

**Cause:** pydantic-settings v2 parses `list[str]` fields as JSON. A bare comma-separated string is not valid JSON.

**Fix:** Use a JSON array in your `.env`. See [Configuration — Application](configuration.md#application):

```env
# ✅ Correct
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# ❌ Wrong — fails to parse
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## `Connection refused` on startup

**Symptom:** The app crashes immediately with a database or Redis connection error.

**Fix:** Make sure the infrastructure containers are running and healthy:

```bash
docker compose -f docker/docker-compose.yml ps
# Both postgres and redis should show status: healthy

# If not started:
make docker-up
```

See [Docker — Local Development](docker.md#local-development).

---

## `JWT_SECRET_KEY` validation error

**Symptom:** `pydantic_core.ValidationError: JWT_SECRET_KEY: String should have at least 32 characters`

**Fix:** Generate a proper secret and set it in `.env`. See [Configuration — JWT Authentication](configuration.md#jwt-authentication):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output into JWT_SECRET_KEY in your .env
```

---

## `501 Not Implemented` on `POST /auth/token`

**Symptom:** Auth endpoint returns 501 in production.

**Cause:** The credential stub is intentionally blocked when `APP_ENV=production`. See [API Reference — Auth stub in production](api-reference.md#auth-stub-in-production).

**Fix:** Implement real user validation in `src/infrastructure/auth/router.py`:

```python
# Replace the stub block with:
user = await user_repository.get_by_username(body.username)
if not user or not verify_password(body.password, user.hashed_password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
return jwt_service.issue_token_pair(user_id=user.id, scopes=user.scopes)
```

---

## `409 Conflict` on settle — concurrent update

**Symptom:** Settle request returns 409 with "modified concurrently".

**Cause:** Another request modified the transaction between your read and write (optimistic locking). See [Architecture — Optimistic locking](architecture.md#optimistic-locking-prevents-lost-updates).

**Fix:** Re-fetch the transaction and retry the settle if it is still in `pending` status.

---

## Alembic `Target database is not up to date`

**Fix:**

```bash
alembic upgrade head
```

If out of sync:

```bash
alembic current    # check current revision
alembic history    # check available revisions
```

See [Database Migrations](database-migrations.md).

---

## `asyncpg.exceptions.UndefinedTableError`

**Symptom:** SQLAlchemy queries fail with "relation does not exist".

**Fix:** You haven't run migrations yet:

```bash
make migrate
```

---

## Tests fail with `FATAL: database "boilerplate_test_db" does not exist`

**Fix:** Create the test database as described in [Getting Started — Step 4](getting-started.md#4-create-the-test-database):

```bash
docker compose -f docker/docker-compose.yml exec postgres \
  psql -U postgres -c "CREATE DATABASE boilerplate_test_db;"
```

---

## Mypy errors on third-party libraries

Mypy runs in strict mode. Libraries without type stubs need to be suppressed explicitly in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["your_library.*"]
ignore_missing_imports = true
```

---

## GCS `DefaultCredentialsError`

**Symptom:** `google.auth.exceptions.DefaultCredentialsError` on startup.

**Fix:** Set one of the GCS auth options in `.env`. See [Configuration — Google Cloud Storage](configuration.md#google-cloud-storage):

```env
# Option 1: path to service account file
GCS_CREDENTIALS_PATH=/path/to/service-account.json

# Option 2: inline JSON (useful for secrets managers / CI)
GCS_CREDENTIALS_JSON={"type": "service_account", ...}

# Option 3: running on GCP (GKE, Cloud Run) — leave both empty, ADC is used automatically
```

---

## Health check shows `storage: unavailable`

**Symptom:** `/api/v1/health` returns `storage: "unavailable"` even though GCS is configured.

**Cause:** The health check performs a real `exists()` probe against GCS. It will fail if credentials are wrong, the bucket doesn't exist, or GCS is unreachable.

**Fix:** Verify your GCS credentials and bucket name:

```bash
# Test with gcloud CLI
gcloud storage ls gs://your-bucket-name

# Or check the app logs for the specific GCS error
docker compose -f docker/docker-compose.yml logs app | grep gcs
```

See [Configuration — Google Cloud Storage](configuration.md#google-cloud-storage) and [Getting Started — GCS setup](getting-started.md#gcs-setup--create-a-service-account-and-bucket).

---

## Related Guides

- [Getting Started](getting-started.md) — initial setup steps
- [Configuration](configuration.md) — all environment variables
- [Docker](docker.md) — running infrastructure
- [Database Migrations](database-migrations.md) — Alembic workflow
- [API Reference](api-reference.md) — endpoint behaviour
- [Back to README](../../README.md)
