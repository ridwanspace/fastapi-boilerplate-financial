import uuid
from typing import Protocol

from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.shared.domain.value_objects.pagination import PagedResult, Pagination


class TransactionRepository(Protocol):
    async def save(self, transaction: Transaction) -> None: ...

    async def get_by_id(self, transaction_id: uuid.UUID) -> Transaction | None: ...

    async def list_by_account(
        self,
        account_id: uuid.UUID,
        pagination: Pagination,
        status_filter: TransactionStatus | None = None,
    ) -> PagedResult[Transaction]: ...
