import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from src.contexts.transactions.api.schemas.request import CreateTransactionRequest
from src.contexts.transactions.api.schemas.response import (
    TransactionListResponse,
    TransactionResponse,
)
from src.contexts.transactions.application.commands.create_transaction import (
    CreateTransactionCommand,
)
from src.contexts.transactions.application.commands.settle_transaction import (
    SettleTransactionCommand,
)
from src.contexts.transactions.application.handlers.create_transaction_handler import (
    CreateTransactionHandler,
)
from src.contexts.transactions.application.handlers.settle_transaction_handler import (
    SettleTransactionHandler,
)
from src.contexts.transactions.application.queries.list_transactions import (
    ListTransactionsHandler,
    ListTransactionsQuery,
)
from src.contexts.transactions.domain.exceptions import (
    TransactionConcurrentUpdateError,
    TransactionImmutableError,
    TransactionNotFoundError,
)
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.infrastructure.auth.dependencies import get_current_user
from src.infrastructure.auth.schemas import CurrentUser
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.shared.application.result import Ok
from src.shared.domain.value_objects.pagination import Pagination


router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_uow() -> SqlAlchemyUnitOfWork:
    from src.container import container

    return SqlAlchemyUnitOfWork(container.session_factory)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new financial transaction",
    description=(
        "Idempotent: supply `Idempotency-Key` header to safely retry on network failure. "
        "A repeated request with the same key returns the original response without creating a "
        "duplicate."
    ),
)
async def create_transaction(
    body: CreateTransactionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        description="Client-generated unique key to prevent duplicate transactions on retry.",
    ),
) -> TransactionResponse:
    handler = CreateTransactionHandler(uow)
    result = await handler.handle(
        CreateTransactionCommand(
            account_id=body.account_id,
            amount=body.amount,
            currency=body.currency,
            transaction_type=str(body.transaction_type),
            reference=body.reference,
            created_by_id=current_user.user_id,
            idempotency_key=idempotency_key,
        )
    )
    if result.is_err():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.unwrap()))
    assert isinstance(result, Ok)
    return TransactionResponse.from_dto(result.unwrap())


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions for an account",
)
async def list_transactions(
    account_id: uuid.UUID = Query(..., description="Filter by account ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: TransactionStatus | None = Query(default=None, alias="status"),
    current_user: CurrentUser = Depends(get_current_user),  # noqa: ARG001
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TransactionListResponse:
    handler = ListTransactionsHandler(uow)
    result = await handler.handle(
        ListTransactionsQuery(
            account_id=account_id,
            pagination=Pagination(page=page, page_size=page_size),
            status_filter=status_filter,
        )
    )
    return TransactionListResponse.from_paged_result(result)


@router.post(
    "/{transaction_id}/settle",
    response_model=TransactionResponse,
    summary="Settle a pending transaction",
)
async def settle_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TransactionResponse:
    handler = SettleTransactionHandler(uow)
    result = await handler.handle(
        SettleTransactionCommand(
            transaction_id=transaction_id,
            settled_by_id=current_user.user_id,
        )
    )
    if result.is_err():
        error = result.unwrap()
        if isinstance(error, TransactionNotFoundError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
        if isinstance(error, TransactionImmutableError):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        if isinstance(error, TransactionConcurrentUpdateError):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    assert isinstance(result, Ok)
    return TransactionResponse.from_dto(result.unwrap())
