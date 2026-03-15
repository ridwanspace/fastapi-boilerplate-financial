# Docker

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Configuration](configuration.md)

---

## Table of Contents

- [Local Development](#local-development)
- [Production Build](#production-build)

---

## Local Development

The `docker-compose.yml` starts **PostgreSQL** and **Redis** with health checks, plus the **app** with hot-reload:

```bash
# Start everything
make docker-up

# Stop everything
make docker-down

# View logs
docker compose -f docker/docker-compose.yml logs -f app

# View only postgres logs
docker compose -f docker/docker-compose.yml logs -f postgres
```

**Services and ports:**

| Service | Port | Credentials |
|---|---|---|
| FastAPI app | `8000` | — |
| PostgreSQL | `5432` | `postgres` / `postgres` |
| Redis | `6379` | no password |

---

## Production Build

The production Dockerfile uses a **multi-stage build** to produce a minimal, secure image:

```
Stage 1 (builder)             Stage 2 (runtime)
─────────────────             ─────────────────
python:3.12-slim              python:3.12-slim
+ gcc, libpq-dev              + libpq5 only (runtime lib)
+ pip install wheels    ───►  + compiled wheels (no pip, no build tools)
                              + non-root user: appuser
                              + health check every 30s
                              + CMD: start.sh (migrate then serve)
```

Build and run the production image:

```bash
# Build the image
docker build -f docker/Dockerfile -t <your-repo-name>:latest .

# Run it (pass your env values)
docker run -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL=postgresql+asyncpg://... \
  <your-repo-name>:latest
```

**Security properties of the production image:**
- Runs as non-root user (`appuser`)
- No `pip`, no compiler, no build tools in the runtime layer
- Source code limited to `src/`, `alembic/`, `scripts/`
- No secrets baked in — all injected via environment variables at runtime
- Health check polls `/api/v1/health` every 30 seconds

---

## Related Guides

- [Getting Started](getting-started.md) — starting infrastructure for development
- [Configuration](configuration.md) — environment variables for production
- [API Reference — Health Check](api-reference.md#get-apiv1health--deep-health-check)
- [Back to README](../../README.md)
