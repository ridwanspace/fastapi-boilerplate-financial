import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class SettleTransactionCommand:
    transaction_id: uuid.UUID
    settled_by_id: uuid.UUID | None = None
