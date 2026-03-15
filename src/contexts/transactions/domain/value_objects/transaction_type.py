from enum import StrEnum


class TransactionType(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"
