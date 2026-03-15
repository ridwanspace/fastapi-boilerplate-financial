import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class TransactionDTO:
    id: uuid.UUID
    account_id: uuid.UUID
    amount: Decimal
    currency: str
    transaction_type: str
    status: str
    reference: str
    idempotency_key: str | None
    failure_reason: str | None
    settled_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None
    deleted_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
