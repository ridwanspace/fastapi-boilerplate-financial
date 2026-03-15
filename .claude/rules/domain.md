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
- State transition guards must use the **most specific** exception:
  - Raise `<Entity>AlreadySettledError` only when the entity is already in the settled state
  - Raise `InvalidTransactionError` for all other invalid transitions (e.g., settling a failed/cancelled tx)
  - Never use a single broad guard (`if status != PENDING: raise AlreadySettledError`) for multiple invalid states
- `DomainEvent` subclasses: base class uses `KW_ONLY` for defaulted fields (`event_id`, `occurred_at`).
  Subclass fields must come **before** any inherited defaults — they are positional args:
  ```python
  @dataclass(frozen=True)
  class TransactionCreated(DomainEvent):
      transaction_id: uuid.UUID   # positional — defined before KW_ONLY defaults
      amount: Decimal
  ```
- `collect_events()` clears and returns pending events — call once per handler, after commit
- `Money` arithmetic: use `.add()`, `.subtract()`, `.multiply()` — never operate on `.amount` directly
- Currency codes must be ISO 4217 uppercase (e.g., `"USD"`, `"EUR"`) — validated at construction
