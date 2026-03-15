---
paths:
  - "src/contexts/*/infrastructure/**/*.py"
  - "src/infrastructure/**/*.py"
---

# Infrastructure Layer Rules

## SQLAlchemy Models

- Monetary columns: `Mapped[Decimal]` with `Numeric(precision=19, scale=4)` — never `Float`
- All models include: `version`, `created_by_id`, `updated_by_id`, `deleted_at`
- `__table_args__` must include:
  - `CheckConstraint("amount > 0", ...)` for any amount column
  - `CheckConstraint("currency ~ '^[A-Z]{3}$'", ...)` for any currency column
  - Composite index on `(account_id, status)` for list queries
  - Partial index on `status = 'pending'` for pending-only queries
- Register every new model in `src/infrastructure/database/base.py → import_all_models()`

## Repositories

- `save()` must check immutable statuses before any UPDATE:
  ```python
  if TransactionStatus(model.status) in _IMMUTABLE_STATUSES:
      raise TransactionImmutableError(...)
  ```
- `save()` must validate optimistic lock before UPDATE:
  ```python
  if model.version != transaction.version - 1:
      raise TransactionConcurrentUpdateError(...)
  ```
- All `SELECT` queries filter `WHERE deleted_at IS NULL`
- `get_by_id()` returns `None` for soft-deleted records (same as not found)
- Read back from DB after INSERT to get server-generated defaults

## GCS Storage

- All GCS SDK calls wrapped with `asyncio.to_thread()` — SDK is synchronous
- Never call GCS SDK directly from async context without `to_thread()`
- GCS SDK and redis client have no type stubs — suppress mypy errors with targeted comments:
  - `# type: ignore[no-any-return]` on return statements that hand back untyped SDK values
  - `# type: ignore[no-untyped-call]` on `service_account.Credentials.from_service_account_*` calls
- Token-type string literals (`"bearer"`, `"access"`, `"refresh"`) in Pydantic schemas trigger S105
  (false positive — they are not passwords). Suppress with `# noqa: S105`
- New bounded context model imports in `base.py → import_all_models()` must only be added once the
  context's infrastructure module actually exists — comment them out with `# noqa: ERA001` until then
