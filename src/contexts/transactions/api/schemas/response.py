import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.contexts.transactions.application.dtos.transaction_dto import TransactionDTO
from src.shared.domain.value_objects.pagination import PagedResult


class TransactionResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    # Amount serialised as string to guarantee precision is preserved for API clients
    amount: str = Field(description="Decimal amount as string — use for all calculations")
    currency: str
    transaction_type: str
    status: str
    reference: str
    idempotency_key: str | None
    failure_reason: str | None
    settled_at: datetime | None
    version: int = Field(description="Optimistic locking version")
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: TransactionDTO) -> "TransactionResponse":
        return cls(
            id=dto.id,
            account_id=dto.account_id,
            amount=str(dto.amount),
            currency=dto.currency,
            transaction_type=dto.transaction_type,
            status=dto.status,
            reference=dto.reference,
            idempotency_key=dto.idempotency_key,
            failure_reason=dto.failure_reason,
            settled_at=dto.settled_at,
            version=dto.version,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def from_paged_result(
        cls, result: PagedResult[TransactionDTO]
    ) -> "TransactionListResponse":
        return cls(
            items=[TransactionResponse.from_dto(dto) for dto in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
            has_next=result.has_next,
            has_previous=result.has_previous,
        )
