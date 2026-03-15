# Database Migrations

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Adding a Bounded Context](adding-a-bounded-context.md) · [Architecture](architecture.md)

Migrations are managed by Alembic. The `alembic/env.py` is configured for async SQLAlchemy.

---

## Table of Contents

- [Apply Migrations](#apply-migrations)
- [Create a New Migration](#create-a-new-migration)
- [Other Useful Commands](#other-useful-commands)
- [Registering New Models](#registering-new-models)
- [Financial Model Conventions](#financial-model-conventions)

---

## Apply Migrations

```bash
make migrate
# or:
python -m alembic upgrade head
```

---

## Create a New Migration

After modifying or adding a SQLAlchemy model, generate the migration automatically:

```bash
make migrate-create msg="add payment_method to transactions"
# or:
python -m alembic revision --autogenerate -m "add payment_method to transactions"
```

> **Important:** Always review the generated file in `alembic/versions/` before applying. Autogenerate may miss some changes (e.g. check constraints defined only at the Python level, custom PostgreSQL types).

---

## Other Useful Commands

```bash
python -m alembic current          # Show current applied revision
python -m alembic history          # Show migration history
python -m alembic downgrade -1     # Rollback one migration
python -m alembic downgrade base   # Rollback all migrations (⚠️ destructive)
```

---

## Registering New Models

When you add a new SQLAlchemy model, register it in `src/infrastructure/database/base.py` so Alembic can detect it:

```python
def import_all_models() -> None:
    from src.contexts.transactions.infrastructure.models import transaction_model  # noqa: F401
    # Add your new model import here ↓
    from src.contexts.payments.infrastructure.models import payment_model  # noqa: F401
```

> **Note:** Only import models for contexts that have been implemented. Importing a non-existent module will cause a mypy error at startup.

---

## Financial Model Conventions

Every financial ORM model must include these columns by default. See the [Architecture — Financial Safety Guarantees](architecture.md#financial-safety-guarantees) for the rationale behind each.

```python
from decimal import Decimal
import uuid
from datetime import datetime
from sqlalchemy import Numeric, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as Uuid

# Monetary amount — never float
amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)

# Audit trail
created_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
updated_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

# Soft-delete — never hard-delete financial records
deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# Optimistic locking
version: Mapped[int] = mapped_column(nullable=False, default=0)

# Required CHECK constraints
__table_args__ = (
    CheckConstraint("amount > 0", name="ck_<table>_amount_positive"),
    CheckConstraint("currency ~ '^[A-Z]{3}$'", name="ck_<table>_currency_iso4217"),
)
```

**Column rename strategy:** Never drop and re-add — use `op.alter_column()` to preserve data. Always add a `batch_alter_table` block for SQLite compatibility in tests.

---

## Related Guides

- [Adding a Bounded Context](adding-a-bounded-context.md) — step-by-step model and migration workflow
- [Architecture](architecture.md) — financial safety design decisions
- [Getting Started](getting-started.md) — initial migration setup
- [Troubleshooting](troubleshooting.md) — common Alembic errors
- [Back to README](../../README.md)
