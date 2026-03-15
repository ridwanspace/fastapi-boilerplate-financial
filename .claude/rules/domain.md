---
paths:
  - "src/contexts/*/domain/**/*.py"
  - "src/shared/domain/**/*.py"
---

# Domain Layer Rules

- Domain classes have **zero framework imports** — no FastAPI, SQLAlchemy, Pydantic, or Redis
- Entities extend `AggregateRoot` or `Entity` from `src/shared/domain/`
- Value objects extend `ValueObject` (frozen dataclass) — immutable, equality by value
- All state transitions go through explicit methods (e.g., `settle()`, `cancel()`) — never mutate fields directly from outside
- Every state transition must: validate preconditions → mutate state → increment `_version` → call `_touch()` → `_record_event()`
- Domain exceptions must extend the context's base exception class (e.g., `TransactionError`)
- `collect_events()` clears and returns pending events — call once per handler, after commit
- `Money` arithmetic: use `.add()`, `.subtract()`, `.multiply()` — never operate on `.amount` directly
- Currency codes must be ISO 4217 uppercase (e.g., `"USD"`, `"EUR"`) — validated at construction
