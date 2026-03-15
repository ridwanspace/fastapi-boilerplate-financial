import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateTransactionCommand:
    account_id: uuid.UUID
    amount: Decimal
    currency: str
    transaction_type: str
    reference: str
    created_by_id: uuid.UUID | None = None
    idempotency_key: str | None = None
