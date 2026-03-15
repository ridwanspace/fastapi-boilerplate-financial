import uuid
from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class TransactionCreated(DomainEvent):
    transaction_id: uuid.UUID
    account_id: uuid.UUID
    amount: Decimal
    currency: str
    transaction_type: str


@dataclass(frozen=True)
class TransactionSettled(DomainEvent):
    transaction_id: uuid.UUID


@dataclass(frozen=True)
class TransactionFailed(DomainEvent):
    transaction_id: uuid.UUID
    reason: str


@dataclass(frozen=True)
class TransactionCancelled(DomainEvent):
    transaction_id: uuid.UUID
