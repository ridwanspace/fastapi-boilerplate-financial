import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.infrastructure.database.base import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Financial precision: Decimal — never float
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    transaction_type: Mapped[str] = mapped_column(
        Enum(TransactionType, name="transaction_type_enum"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(TransactionStatus, name="transaction_status_enum"),
        nullable=False,
        default=TransactionStatus.PENDING,
        index=True,
    )
    reference: Mapped[str] = mapped_column(String(255), nullable=False)

    # Idempotency: unique per client-supplied key to prevent double-spend on retries
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit trail
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    # Soft-delete — financial records are never hard-deleted
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optimistic locking — prevents lost updates on concurrent modifications
    version: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        # Database-level enforcement of financial invariants (defence-in-depth beyond domain layer)
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "currency ~ '^[A-Z]{3}$'",
            name="ck_transactions_currency_iso4217",
        ),
        # Composite index for the most common query: account transactions by status
        Index("ix_transactions_account_status", "account_id", "status"),
        # Partial index: fast lookup of all pending transactions (operational monitoring)
        Index(
            "ix_transactions_pending",
            "account_id",
            postgresql_where="status = 'PENDING'",
        ),
    )
