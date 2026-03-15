import structlog

from src.contexts.transactions.application.commands.settle_transaction import (
    SettleTransactionCommand,
)
from src.contexts.transactions.application.dtos.transaction_dto import TransactionDTO
from src.contexts.transactions.domain.exceptions import TransactionNotFoundError
from src.contexts.transactions.infrastructure.repositories.sql_transaction_repository import (
    SqlTransactionRepository,
)
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.shared.application.result import Err, Ok, Result


logger = structlog.get_logger(__name__)


class SettleTransactionHandler:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: SettleTransactionCommand) -> Result[TransactionDTO]:
        async with self._uow as uow:
            repo = SqlTransactionRepository(uow.session)
            transaction = await repo.get_by_id(command.transaction_id)
            if transaction is None:
                return Err(
                    TransactionNotFoundError(f"Transaction {command.transaction_id} not found")
                )

            transaction.settle(settled_by_id=command.settled_by_id)
            await repo.save(transaction)
            await uow.commit()

            logger.info(
                "transaction_settled",
                transaction_id=str(transaction.id),
                account_id=str(transaction.account_id),
                amount=str(transaction.amount.amount),
                currency=transaction.amount.currency,
                settled_by_id=str(command.settled_by_id) if command.settled_by_id else None,
            )

            return Ok(self._to_dto(transaction))

    def _to_dto(self, transaction: "Transaction") -> TransactionDTO:  # type: ignore[name-defined]
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
