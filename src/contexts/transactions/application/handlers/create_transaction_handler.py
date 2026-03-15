import structlog

from src.contexts.transactions.application.commands.create_transaction import (
    CreateTransactionCommand,
)
from src.contexts.transactions.application.dtos.transaction_dto import TransactionDTO
from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.contexts.transactions.infrastructure.repositories.sql_transaction_repository import (
    SqlTransactionRepository,
)
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.shared.application.result import Ok, Result
from src.shared.domain.value_objects.money import Money


logger = structlog.get_logger(__name__)


class CreateTransactionHandler:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateTransactionCommand) -> Result[TransactionDTO]:
        async with self._uow as uow:
            repo = SqlTransactionRepository(uow.session)

            # Idempotency check: return existing transaction if key already used
            if command.idempotency_key:
                existing = await repo.get_by_idempotency_key(command.idempotency_key)
                if existing is not None:
                    logger.info(
                        "transaction_idempotent_replay",
                        idempotency_key=command.idempotency_key,
                        transaction_id=str(existing.id),
                    )
                    return Ok(self._to_dto(existing))

            transaction = Transaction.create(
                account_id=command.account_id,
                amount=Money.of(command.amount, command.currency),
                transaction_type=TransactionType(command.transaction_type),
                reference=command.reference,
                created_by_id=command.created_by_id,
                idempotency_key=command.idempotency_key,
            )
            await repo.save(transaction)
            await uow.commit()

            logger.info(
                "transaction_created",
                transaction_id=str(transaction.id),
                account_id=str(transaction.account_id),
                amount=str(transaction.amount.amount),
                currency=transaction.amount.currency,
                transaction_type=str(transaction.transaction_type),
                created_by_id=str(command.created_by_id) if command.created_by_id else None,
            )

            return Ok(self._to_dto(transaction))

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
