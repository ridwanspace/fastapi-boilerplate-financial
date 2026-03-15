import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType


class CreateTransactionRequest(BaseModel):
    account_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=4)
    currency: str = Field(min_length=3, max_length=3)
    transaction_type: TransactionType
    reference: str = Field(min_length=1, max_length=255)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()
