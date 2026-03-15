# Configuration

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Troubleshooting](troubleshooting.md)

All configuration is managed through environment variables loaded by `src/settings.py` via Pydantic BaseSettings. Copy `.env.example` to `.env` and customise as needed.

---

## Table of Contents

- [Application](#application)
- [Database](#database)
- [Redis](#redis)
- [JWT Authentication](#jwt-authentication)
- [Rate Limiting](#rate-limiting)
- [Google Cloud Storage](#google-cloud-storage)
- [Sentry](#sentry-optional)

---

## Application

| Variable | Default | Required | Description |
|---|---|---|---|
| `APP_ENV` | `development` | No | Environment name: `development`, `staging`, `production` |
| `APP_NAME` | `FastAPI Boilerplate` | No | Application name shown in OpenAPI docs |
| `APP_VERSION` | `0.1.0` | No | Application version |
| `DEBUG` | `false` | No | Enable SQLAlchemy query logging. Blocked in production. |
| `LOG_LEVEL` | `INFO` | No | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `API_PREFIX` | `/api/v1` | No | URL prefix for all API routes |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | No | JSON array of CORS allowed origins |

> **`ALLOWED_ORIGINS` must be a JSON array string:**
> ```env
> # ✅ Correct
> ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
>
> # ❌ Wrong — fails to parse
> ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
> ```

---

## Database

| Variable | Default | Required | Description |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | **Yes** | Full async PostgreSQL connection string |
| `DATABASE_POOL_SIZE` | `10` | No | SQLAlchemy connection pool size |
| `DATABASE_MAX_OVERFLOW` | `20` | No | Max extra connections above pool size |
| `DATABASE_POOL_TIMEOUT` | `30` | No | Seconds to wait for a connection |

---

## Redis

| Variable | Default | Required | Description |
|---|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | **Yes** | Redis connection URL |
| `REDIS_MAX_CONNECTIONS` | `10` | No | Max connections in the pool |

---

## JWT Authentication

| Variable | Default | Required | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | — | **Yes** | Signing secret. Minimum 32 characters. Use a random hex string. |
| `JWT_ALGORITHM` | `HS256` | No | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | No | Access token TTL in minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | No | Refresh token TTL in days |

Generate a secure secret:

```bash
openssl rand -hex 32
# or:
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Rate Limiting

| Variable | Default | Required | Description |
|---|---|---|---|
| `RATE_LIMIT_DEFAULT` | `200/minute` | No | Global per-IP rate limit across all routes |
| `RATE_LIMIT_AUTH` | `10/minute` | No | Per-IP rate limit on `POST /auth/token` |

---

## Google Cloud Storage

| Variable | Default | Required | Description |
|---|---|---|---|
| `GCS_PROJECT_ID` | — | Yes (for GCS) | Your GCP project ID |
| `GCS_BUCKET_NAME` | — | Yes (for GCS) | GCS bucket name |
| `GCS_CREDENTIALS_PATH` | — | No | Path to service account JSON file |
| `GCS_CREDENTIALS_JSON` | — | No | Inline service account JSON string (alternative to path) |

**GCS authentication priority:**
1. `GCS_CREDENTIALS_JSON` (inline JSON string) — highest priority
2. `GCS_CREDENTIALS_PATH` (path to JSON file)
3. Application Default Credentials (ADC) — used automatically on GCP (GKE, Cloud Run, etc.)

```env
# Option 1: path to service account file
GCS_CREDENTIALS_PATH=/path/to/your/service-account.json

# Option 2: inline JSON (useful for CI/CD secrets)
GCS_CREDENTIALS_JSON={"type": "service_account", ...}
```

For initial GCS setup (creating the bucket and service account), see [Getting Started — GCS setup](getting-started.md#gcs-setup--create-a-service-account-and-bucket).

---

## Sentry (optional)

| Variable | Default | Required | Description |
|---|---|---|---|
| `SENTRY_DSN` | — | No | Sentry DSN. When set, Sentry is initialised automatically at startup. |

---

## Related Guides

- [Getting Started](getting-started.md) — step-by-step initial setup
- [Troubleshooting](troubleshooting.md) — common configuration errors
- [Back to README](../../README.md)
