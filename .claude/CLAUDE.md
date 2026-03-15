# FastAPI Boilerplate — Claude Code Project Instructions

## Architecture

DDD + Clean Architecture. Strict inward dependency: `api → application → domain ← infrastructure`.
Bounded contexts live under `src/contexts/<context>/` with four internal layers: `domain/`, `application/`, `infrastructure/`, `api/`.
Shared kernel in `src/shared/` — no context may import from another context directly.

## Key Commands

```bash
make dev          # start postgres + redis via docker-compose
make run          # start the app (uvicorn)
make test-unit    # pytest -m unit
make test-int     # pytest -m integration (requires TEST_DATABASE_URL)
make test-e2e     # pytest -m e2e
make lint         # ruff check + mypy
make format       # ruff format
make migrate      # alembic upgrade head
make migrate-create  # alembic revision --autogenerate -m "..."
```

## Code Style

- Python 3.12+, async-first throughout
- Type hints required on all functions and methods
- `Decimal` for all monetary values — never `float`
- Domain exceptions only; never raise `HTTPException` inside domain or application layers
- Result type for handler returns: `Ok(value) | Err(exception)` — no exceptions crossing layer boundaries
- Pydantic v2 for all request/response schemas; `model_config = ConfigDict(strict=True)` by default

## Testing

- Three markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- Unit tests: pure domain logic, no I/O, no DB, no mocks of internals
- Integration tests: real DB via `db_session` fixture (per-test transaction rollback)
- Never mock the database in integration tests
- Run a single test: `pytest tests/unit/domain/test_transaction_entity.py -v`

## Financial Safety — Non-Negotiable Rules

1. **Money**: always `Decimal`, `ROUND_HALF_EVEN`, stored as `Numeric(19,4)` in PostgreSQL
2. **Immutability**: `SETTLED` and `REVERSED` transactions must never be mutated
3. **Optimistic locking**: every aggregate has a `version` column; repository validates `model.version == transaction.version - 1` before any UPDATE
4. **Soft-delete**: no hard deletes; all queries filter `WHERE deleted_at IS NULL`
5. **Idempotency**: check `idempotency_key` before every INSERT; DB UNIQUE constraint is the final guard
6. **Audit trail**: every mutation must populate `created_by_id` / `updated_by_id` from `CurrentUser.user_id`
7. **API amounts**: serialise as `str` in responses — never `float` or `Decimal` directly

## Adding a New Bounded Context

1. Create `src/contexts/<name>/domain/` — entities, value objects, exceptions, domain events, repository protocol
2. Create `src/contexts/<name>/application/` — commands, queries, handlers, DTOs
3. Create `src/contexts/<name>/infrastructure/` — SQLAlchemy model, repository implementation
4. Create `src/contexts/<name>/api/` — router, request/response schemas
5. Register model in `src/infrastructure/database/base.py → import_all_models()`
6. Wire dependencies in `src/container.py`
7. Include router in `src/api/router.py`
8. Write unit tests for domain, integration tests for repository

## Environment

Copy `.env.example` → `.env` before first run. `JWT_SECRET_KEY` must be ≥ 32 chars.
Test env: `.env.test` (auto-loaded by `tests/conftest.py`).
Production: `APP_ENV=production` triggers startup validation — `DEBUG` must be `false`, GCS must be configured.

See @README.md for full architecture diagrams and API reference.

## Detailed Rule Files

The following rule files contain specialized guidelines that are automatically loaded based on the files you're working on:

| Rule File | When Loaded | Covers | Quick Reference |
|-----------|-------------|--------|----------------|
| `.claude/rules/api.md` | Working on `src/contexts/*/api/**/*.py`, `src/api/**/*.py` | Request/response schemas, router conventions, rate limiting, result unwrapping, idempotency headers | `schema`, `dto`, `request/response`, `router`, `rate limit`, `idempotency`, `http exception`, `current_user` |
| `.claude/rules/application.md` | Working on `src/contexts/*/application/**/*.py` | Command/query handlers, Result type, UoW, idempotency check, audit log, DTOs | `handler`, `command`, `query`, `Result`, `Ok`, `Err`, `UoW`, `idempotency`, `audit log`, `dto` |
| `.claude/rules/domain.md` | Working on `src/contexts/*/domain/**/*.py`, `src/shared/domain/**/*.py` | Entities, value objects, state transitions, domain exceptions, Money arithmetic, events | `entity`, `value object`, `AggregateRoot`, `state transition`, `domain exception`, `Money`, `collect_events` |
| `.claude/rules/infrastructure.md` | Working on `src/contexts/*/infrastructure/**/*.py`, `src/infrastructure/**/*.py` | SQLAlchemy models, repositories, optimistic locking, soft-delete, GCS storage | `model`, `repository`, `optimistic locking`, `soft-delete`, `Numeric`, `version`, `GCS`, `asyncio.to_thread` |
| `.claude/rules/migrations.md` | Working on `alembic/**/*.py`, `alembic/versions/*.py` | Autogenerate workflow, required financial columns, column rename strategy, review checklist | `migration`, `alembic`, `autogenerate`, `version column`, `rename column`, `drop column`, `CheckConstraint` |
| `.claude/rules/security.md` | **ALL code generation** | Credentials, JWT, CORS, rate limiting, SQL injection, GCS signed URLs, production validation, logging | `secret`, `JWT`, `CORS`, `rate limit`, `SQL injection`, `signed URL`, `production`, `credentials`, `log` |
| `.claude/rules/testing.md` | Working on `tests/**/*.py` | Test markers, unit/integration/e2e structure, no DB mocks, naming conventions, coverage targets | `test`, `pytest`, `mock`, `fixture`, `unit`, `integration`, `e2e`, `db_session`, `coverage` |
