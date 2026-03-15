import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.exceptions import TransactionImmutableError
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.contexts.transactions.infrastructure.models.transaction_model import TransactionModel
from src.shared.domain.value_objects.money import Money
from src.shared.domain.value_objects.pagination import PagedResult, Pagination


_IMMUTABLE_STATUSES = {TransactionStatus.SETTLED, TransactionStatus.REVERSED}


class SqlTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, transaction: Transaction) -> None:
        model = await self._session.get(TransactionModel, transaction.id)
        if model is None:
            self._session.add(self._to_model(transaction))
        else:
            if TransactionStatus(model.status) in _IMMUTABLE_STATUSES:
                raise TransactionImmutableError(
                    f"Transaction {transaction.id} is in terminal status "
                    f"'{model.status}' and cannot be modified."
                )
            self._update_model(model, transaction)

    async def get_by_id(self, transaction_id: uuid.UUID) -> Transaction | None:
        stmt = select(TransactionModel).where(
            TransactionModel.id == transaction_id,
            TransactionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_idempotency_key(self, key: str) -> Transaction | None:
        stmt = select(TransactionModel).where(
            TransactionModel.idempotency_key == key,
            TransactionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_account(
        self,
        account_id: uuid.UUID,
        pagination: Pagination,
        status_filter: TransactionStatus | None = None,
    ) -> PagedResult[Transaction]:
        base = select(TransactionModel).where(
            TransactionModel.account_id == account_id,
            TransactionModel.deleted_at.is_(None),
        )
        if status_filter is not None:
            base = base.where(TransactionModel.status == status_filter)

        total = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()

        rows = (
            (
                await self._session.execute(
                    base.order_by(TransactionModel.created_at.desc())
                    .offset(pagination.offset)
                    .limit(pagination.limit)
                )
            )
            .scalars()
            .all()
        )

        return PagedResult(
            items=[self._to_entity(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    # ------------------------------------------------------------------
    # Private mapping helpers
    # ------------------------------------------------------------------

    def _to_model(self, transaction: Transaction) -> TransactionModel:
        return TransactionModel(
            id=transaction.id,
            account_id=transaction.account_id,
            amount=transaction.amount.amount,
            currency=transaction.amount.currency,
            transaction_type=str(transaction.transaction_type),
            status=str(transaction.status),
            reference=transaction.reference,
            idempotency_key=transaction.idempotency_key,
            failure_reason=transaction.failure_reason,
            settled_at=transaction.settled_at,
            created_by_id=transaction.created_by_id,
            updated_by_id=transaction.updated_by_id,
            deleted_at=transaction.deleted_at,
            version=transaction.version,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )

    def _update_model(self, model: TransactionModel, transaction: Transaction) -> None:
        # Guard: version must match to prevent lost updates (optimistic locking)
        if model.version != transaction.version - 1:
            from src.contexts.transactions.domain.exceptions import TransactionConcurrentUpdateError

            raise TransactionConcurrentUpdateError(
                f"Transaction {transaction.id} was modified concurrently. Please retry."
            )
        model.status = str(transaction.status)
        model.failure_reason = transaction.failure_reason
        model.settled_at = transaction.settled_at
        model.updated_by_id = transaction.updated_by_id
        model.deleted_at = transaction.deleted_at
        model.version = transaction.version
        model.updated_at = transaction.updated_at

    def _to_entity(self, model: TransactionModel) -> Transaction:
        transaction = Transaction.__new__(Transaction)
        transaction._id = model.id
        transaction._account_id = model.account_id
        transaction._amount = Money(amount=Decimal(str(model.amount)), currency=model.currency)
        transaction._transaction_type = TransactionType(model.transaction_type)
        transaction._status = TransactionStatus(model.status)
        transaction._reference = model.reference
        transaction._idempotency_key = model.idempotency_key
        transaction._failure_reason = model.failure_reason
        transaction._settled_at = model.settled_at
        transaction._created_by_id = model.created_by_id
        transaction._updated_by_id = model.updated_by_id
        transaction._deleted_at = model.deleted_at
        transaction._version = model.version
        transaction._created_at = model.created_at
        transaction._updated_at = model.updated_at
        transaction._domain_events = []
        return transaction
