---
paths:
  - "src/contexts/*/application/**/*.py"
---

# Application Layer Rules

- Handlers receive a Command or Query dataclass — plain `@dataclass`, no Pydantic
- Handlers return `Result[DTO, Exception]` — `Ok(dto)` on success, `Err(exception)` on failure
- All database work happens inside `async with self._uow as uow:` — never commit outside the context manager
- Idempotency check: before any INSERT, call `repo.get_by_idempotency_key(key)` and return the existing DTO if found
- Structured audit log on every mutation — include `transaction_id`, `amount`, `user_id`, `action`
- DTOs are plain dataclasses — no domain objects leave the application layer
- Import domain entity types directly (e.g., `from ...domain.entities.transaction import Transaction`)
  rather than using forward references (`"Transaction"`) — forward refs cause F821 undefined name errors
- Queries use read-only repository methods — never load an aggregate just to read data
- Commands must include `created_by_id: uuid.UUID | None` for audit trail
