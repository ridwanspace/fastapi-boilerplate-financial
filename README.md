# FastAPI Financial Boilerplate

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.14-6BA539?style=flat-square)
![Ruff](https://img.shields.io/badge/Ruff-linter-D7FF64?style=flat-square&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/Mypy-strict-2A6DB2?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

Production-grade FastAPI boilerplate for financial applications, built with **Domain-Driven Design (DDD)** and **Clean Architecture**. Designed for teams who need a solid, extensible foundation — not a toy scaffold.

---

## What's Included

| Capability | Implementation |
|---|---|
| REST API | FastAPI with Pydantic v2 validation |
| Database ORM | Async SQLAlchemy 2.0 + asyncpg driver |
| Migrations | Alembic with async-aware env |
| Auth | JWT access + refresh tokens (stateless) |
| Rate limiting | slowapi — 10 req/min on auth, 200 req/min global |
| Object Storage | Google Cloud Storage adapter |
| Caching | Redis (async, connection pooled) |
| Logging | Structured JSON logs via structlog |
| Request tracing | Correlation ID middleware |
| Error tracking | Sentry SDK integration (opt-in via env var) |
| Error handling | Global domain exception → HTTP mapping |
| Containerisation | Multi-stage Dockerfile + docker-compose |
| Linting | Ruff (linter + formatter) |
| Type checking | Mypy (strict mode) |
| Testing | pytest + asyncio + coverage (unit / integration / e2e) |

---

## Quick Start

1. Click **"Use this template"** → **"Create a new repository"** at the top of this page.
2. Clone your new repo and set up:

```bash
git clone git@github.com:<your-username>/<your-repo-name>.git && cd <your-repo-name>
python -m venv .venv && source .venv/bin/activate
make dev

# Configure
cp .env.example .env
# Edit .env — set JWT_SECRET_KEY (min 32 chars) and GCS credentials

# Start infrastructure
make docker-up

# Create test database and apply migrations
docker compose -f docker/docker-compose.yml exec postgres psql -U postgres -c "CREATE DATABASE boilerplate_test_db;"
make migrate

# Run
make run
```

API is available at `http://localhost:8000/docs`.

For GCS setup, conda environments, and detailed steps see [Getting Started](docs/guide/getting-started.md).

---

## Documentation

| Guide | Description |
|---|---|
| [Architecture](docs/guide/architecture.md) | DDD layers, dependency rule, request lifecycle, financial safety guarantees, key design decisions |
| [Getting Started](docs/guide/getting-started.md) | Prerequisites, full quick start, GCS setup |
| [Configuration](docs/guide/configuration.md) | All environment variables reference |
| [API Reference](docs/guide/api-reference.md) | Endpoints, request/response formats, security behaviour |
| [Testing](docs/guide/testing.md) | Unit, integration, e2e test strategy and isolation |
| [Database Migrations](docs/guide/database-migrations.md) | Alembic workflow, financial model conventions |
| [Docker](docs/guide/docker.md) | Local dev and production build |
| [Adding a Bounded Context](docs/guide/adding-a-bounded-context.md) | Step-by-step guide for new features |
| [Claude Code](docs/guide/claude-code.md) | Slash commands, rule files, AI-assisted workflow |
| [Troubleshooting](docs/guide/troubleshooting.md) | Common errors and fixes |
| [Make Reference](docs/guide/make-reference.md) | All make targets |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.12 |
| Framework | FastAPI | ≥ 0.115 |
| ASGI Server | Uvicorn + uvloop | ≥ 0.32 |
| ORM | SQLAlchemy (async) | ≥ 2.0 |
| DB Driver | asyncpg | ≥ 0.30 |
| Database | PostgreSQL | 16 |
| Migrations | Alembic | ≥ 1.14 |
| Cache | Redis | 7 |
| Auth | python-jose + passlib | ≥ 3.3 |
| Rate Limiting | slowapi | ≥ 0.1.9 |
| Object Storage | google-cloud-storage | ≥ 2.19 |
| Error Tracking | sentry-sdk | ≥ 2.19 |
| Settings | pydantic-settings | ≥ 2.6 |
| Logging | structlog | ≥ 24.4 |
| Linter | Ruff | ≥ 0.8 |
| Type Checker | Mypy | ≥ 1.13 |
| Test Runner | pytest + pytest-asyncio | ≥ 8.3 |

---

*Built with FastAPI · Python 3.12 · Clean Architecture · DDD*
