# Adding a New Bounded Context

> **Navigation:** [README](../../README.md) · [Architecture](architecture.md) · [Database Migrations](database-migrations.md) · [Testing](testing.md)

Follow these steps to add a new domain context (e.g. `payments`). The `accounts/` context is already scaffolded as a reference. The `transactions/` context is the full working example to copy patterns from.

---

## Table of Contents

- [Step 1 — Create the directory structure](#step-1--create-the-directory-structure)
- [Step 2 — Define the domain](#step-2--define-the-domain)
- [Step 3 — Define the abstract repository](#step-3--define-the-abstract-repository)
- [Step 4 — Create the SQLAlchemy model](#step-4--create-the-sqlalchemy-model)
- [Step 5 — Create and apply a migration](#step-5--create-and-apply-a-migration)
- [Step 6 — Implement the repository and handlers](#step-6--implement-the-repository-and-handlers)
- [Step 7 — Create the API router](#step-7--create-the-api-router)
- [Step 8 — Write tests](#step-8--write-tests)

---

## Step 1 — Create the directory structure

```bash
mkdir -p src/contexts/payments/{domain/{entities,value_objects,events,repositories},application/{commands,queries,handlers,dtos},infrastructure/{models,repositories},api/schemas}

# Create __init__.py in every directory
find src/contexts/payments -type d | xargs -I{} touch {}/__init__.py
```

This follows the [Dependency Rule](architecture.md#dependency-rule): each layer knows only about layers below it.

---

## Step 2 — Define the domain

Create your aggregate root in `src/contexts/payments/domain/entities/payment.py`. Always include audit fields and version in the domain entity:

```python
from src.shared.domain.base_aggregate import AggregateRoot
from src.shared.domain.value_objects.money import Money

class Payment(AggregateRoot):
    def __init__(self, amount: Money, created_by_id: uuid.UUID | None = None, ...) -> None:
        super().__init__()
        self._created_by_id = created_by_id
        self._updated_by_id = created_by_id
        self._deleted_at = None
        self._version = 0
        # enforce your invariants here
```

---

## Step 3 — Define the abstract repository

In `src/contexts/payments/domain/repositories/payment_repository.py`:

```python
from typing import Protocol
import uuid
from src.contexts.payments.domain.entities.payment import Payment

class PaymentRepository(Protocol):
    async def save(self, payment: Payment) -> None: ...
    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None: ...
```

---

## Step 4 — Create the SQLAlchemy model

In `src/contexts/payments/infrastructure/models/payment_model.py`. Always include the [financial model conventions](database-migrations.md#financial-model-conventions) (audit, soft-delete, version, check constraints):

```python
from decimal import Decimal
from src.infrastructure.database.base import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )
```

Register the model in `src/infrastructure/database/base.py`:

```python
def import_all_models() -> None:
    ...
    from src.contexts.payments.infrastructure.models import payment_model  # noqa: F401
```

---

## Step 5 — Create and apply a migration

See [Database Migrations](database-migrations.md) for the full Alembic workflow.

```bash
make migrate-create msg="add payments table"
# Review the generated file in alembic/versions/
alembic upgrade head
```

---

## Step 6 — Implement the repository and handlers

Copy the patterns from:
- `src/contexts/transactions/infrastructure/repositories/sql_transaction_repository.py` — immutability guard, soft-delete filter, version check
- `src/contexts/transactions/application/handlers/create_transaction_handler.py` — idempotency, audit logging

See [API Reference — Security Behaviour](api-reference.md#security-behaviour) for idempotency conventions.

---

## Step 7 — Create the API router

In `src/contexts/payments/api/router.py`, create your `APIRouter`. Pass `current_user.user_id` as `created_by_id` on every mutation. Then register in `src/api/router.py`:

```python
from src.contexts.payments.api.router import router as payments_router
api_router.include_router(payments_router)
```

---

## Step 8 — Write tests

Follow the [Testing](testing.md) guide for marker and fixture conventions.

| Test file | What to cover |
|---|---|
| `tests/unit/domain/test_payment_entity.py` | State transitions, version increments, invariant enforcement, soft-delete |
| `tests/integration/repositories/test_payment_repository.py` | Idempotency, immutability, soft-delete filtering, audit fields |
| `tests/e2e/test_payment_endpoints.py` | Auth required, correct HTTP status codes |

---

## Related Guides

- [Architecture](architecture.md) — layer responsibilities and dependency rule
- [Database Migrations](database-migrations.md) — financial model conventions
- [API Reference](api-reference.md) — API conventions
- [Testing](testing.md) — test tier guidance
- [Claude Code](claude-code.md) — `/plan` and `/run-plan` workflow for implementing this
- [Back to README](../../README.md)
