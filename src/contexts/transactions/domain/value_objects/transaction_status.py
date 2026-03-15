from enum import StrEnum


class TransactionStatus(StrEnum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"
