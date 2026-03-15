import uuid
from dataclasses import dataclass

from src.contexts.transactions.application.dtos.transaction_dto import TransactionDTO
from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.infrastructure.repositories.sql_transaction_repository import (
    SqlTransactionRepository,
)
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.shared.domain.value_objects.pagination import PagedResult, Pagination


@dataclass(frozen=True)
class ListTransactionsQuery:
    account_id: uuid.UUID
    pagination: Pagination
    status_filter: TransactionStatus | None = None


class ListTransactionsHandler:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: ListTransactionsQuery) -> PagedResult[TransactionDTO]:
        async with self._uow as uow:
            repo = SqlTransactionRepository(uow.session)
            paged = await repo.list_by_account(
                account_id=query.account_id,
                pagination=query.pagination,
                status_filter=query.status_filter,
            )
            return PagedResult(
                items=[self._to_dto(t) for t in paged.items],
                total=paged.total,
                page=paged.page,
                page_size=paged.page_size,
            )

    def _to_dto(self, transaction: Transaction) -> TransactionDTO:
        return TransactionDTO(
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
