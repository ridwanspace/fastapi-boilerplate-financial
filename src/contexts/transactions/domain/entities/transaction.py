import uuid
from datetime import UTC, datetime

from src.contexts.transactions.domain.events.transaction_events import (
    TransactionCancelled,
    TransactionCreated,
    TransactionFailed,
    TransactionSettled,
)
from src.contexts.transactions.domain.exceptions import (
    InvalidTransactionError,
    TransactionAlreadySettledError,
)
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.shared.domain.base_aggregate import AggregateRoot
from src.shared.domain.value_objects.money import Money


class Transaction(AggregateRoot):
    """
    Transaction aggregate root.
    Enforces business invariants and records domain events.
    All state transitions go through methods — never set attributes directly.

    Financial integrity guarantees:
    - Amount is always a Money value object (Decimal, never float)
    - Status transitions are strictly controlled
    - version field enables optimistic locking (prevents lost updates)
    - Soft-delete only — financial records are never hard-deleted
    - Audit trail: created_by_id / updated_by_id carried on every write
    - idempotency_key prevents double-spend on client retries
    """

    def __init__(
        self,
        account_id: uuid.UUID,
        amount: Money,
        transaction_type: TransactionType,
        reference: str,
        created_by_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
        id: uuid.UUID | None = None,
    ) -> None:
        super().__init__(id=id)
        if amount.is_zero():
            raise InvalidTransactionError("Transaction amount must be greater than zero")
        if not reference.strip():
            raise InvalidTransactionError("Transaction reference cannot be empty")

        self._account_id = account_id
        self._amount = amount
        self._transaction_type = transaction_type
        self._reference = reference.strip()
        self._idempotency_key = idempotency_key
        self._status = TransactionStatus.PENDING
        self._settled_at: datetime | None = None
        self._failure_reason: str | None = None
        self._deleted_at: datetime | None = None

        # Audit trail
        self._created_by_id: uuid.UUID | None = created_by_id
        self._updated_by_id: uuid.UUID | None = created_by_id

        # Optimistic locking — starts at 0, incremented on every state transition
        self._version: int = 0

        self._record_event(
            TransactionCreated(
                transaction_id=self._id,
                account_id=self._account_id,
                amount=self._amount.amount,
                currency=self._amount.currency,
                transaction_type=str(self._transaction_type),
            )
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def account_id(self) -> uuid.UUID:
        return self._account_id

    @property
    def amount(self) -> Money:
        return self._amount

    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def idempotency_key(self) -> str | None:
        return self._idempotency_key

    @property
    def status(self) -> TransactionStatus:
        return self._status

    @property
    def settled_at(self) -> datetime | None:
        return self._settled_at

    @property
    def failure_reason(self) -> str | None:
        return self._failure_reason

    @property
    def created_by_id(self) -> uuid.UUID | None:
        return self._created_by_id

    @property
    def updated_by_id(self) -> uuid.UUID | None:
        return self._updated_by_id

    @property
    def deleted_at(self) -> datetime | None:
        return self._deleted_at

    @property
    def version(self) -> int:
        return self._version

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def settle(self, settled_by_id: uuid.UUID | None = None) -> None:
        if self._status == TransactionStatus.SETTLED:
            raise TransactionAlreadySettledError(
                f"Cannot settle transaction in status: {self._status}"
            )
        if self._status != TransactionStatus.PENDING:
            raise InvalidTransactionError(
                f"Cannot settle transaction in status: {self._status}"
            )
        self._status = TransactionStatus.SETTLED
        self._settled_at = datetime.now(UTC)
        self._updated_by_id = settled_by_id
        self._version += 1
        self._touch()
        self._record_event(TransactionSettled(transaction_id=self._id))

    def fail(self, reason: str, failed_by_id: uuid.UUID | None = None) -> None:
        if self._status != TransactionStatus.PENDING:
            raise InvalidTransactionError(f"Cannot fail transaction in status: {self._status}")
        self._status = TransactionStatus.FAILED
        self._failure_reason = reason
        self._updated_by_id = failed_by_id
        self._version += 1
        self._touch()
        self._record_event(TransactionFailed(transaction_id=self._id, reason=reason))

    def cancel(self, cancelled_by_id: uuid.UUID | None = None) -> None:
        if self._status != TransactionStatus.PENDING:
            raise InvalidTransactionError(f"Cannot cancel transaction in status: {self._status}")
        self._status = TransactionStatus.CANCELLED
        self._updated_by_id = cancelled_by_id
        self._version += 1
        self._touch()
        self._record_event(TransactionCancelled(transaction_id=self._id))

    def soft_delete(self, deleted_by_id: uuid.UUID | None = None) -> None:
        """Soft-delete: marks record as deleted without removing from DB. Never hard-delete financials."""
        self._deleted_at = datetime.now(UTC)
        self._updated_by_id = deleted_by_id
        self._version += 1
        self._touch()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        account_id: uuid.UUID,
        amount: Money,
        transaction_type: TransactionType,
        reference: str,
        created_by_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
    ) -> "Transaction":
        return cls(
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            reference=reference,
            created_by_id=created_by_id,
            idempotency_key=idempotency_key,
        )
