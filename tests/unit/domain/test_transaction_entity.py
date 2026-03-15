import uuid

import pytest

from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.exceptions import (
    InvalidTransactionError,
    TransactionAlreadySettledError,
)
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.shared.domain.value_objects.money import Money


def make_transaction(**kwargs) -> Transaction:
    defaults = {
        "account_id": uuid.uuid4(),
        "amount": Money.of(500, "USD"),
        "transaction_type": TransactionType.CREDIT,
        "reference": "TXN-001",
    }
    return Transaction.create(**{**defaults, **kwargs})


@pytest.mark.unit
class TestTransactionCreation:
    def test_creates_in_pending_status(self):
        txn = make_transaction()
        assert txn.status == TransactionStatus.PENDING

    def test_version_starts_at_zero(self):
        txn = make_transaction()
        assert txn.version == 0

    def test_records_created_by_id(self):
        user_id = uuid.uuid4()
        txn = make_transaction(created_by_id=user_id)
        assert txn.created_by_id == user_id
        assert txn.updated_by_id == user_id

    def test_stores_idempotency_key(self):
        txn = make_transaction(idempotency_key="order-123")
        assert txn.idempotency_key == "order-123"

    def test_records_transaction_created_event(self):
        txn = make_transaction()
        events = txn.collect_events()
        assert len(events) == 1
        assert events[0].event_type == "TransactionCreated"

    def test_rejects_zero_amount(self):
        with pytest.raises(InvalidTransactionError):
            make_transaction(amount=Money.zero("USD"))

    def test_rejects_empty_reference(self):
        with pytest.raises(InvalidTransactionError):
            make_transaction(reference="   ")

    def test_not_soft_deleted_on_creation(self):
        txn = make_transaction()
        assert txn.deleted_at is None


@pytest.mark.unit
class TestTransactionSettlement:
    def test_settle_transitions_to_settled(self):
        txn = make_transaction()
        txn.collect_events()
        txn.settle()
        assert txn.status == TransactionStatus.SETTLED
        assert txn.settled_at is not None

    def test_settle_increments_version(self):
        txn = make_transaction()
        txn.settle()
        assert txn.version == 1

    def test_settle_records_settled_by(self):
        user_id = uuid.uuid4()
        txn = make_transaction()
        txn.settle(settled_by_id=user_id)
        assert txn.updated_by_id == user_id

    def test_settle_records_settled_event(self):
        txn = make_transaction()
        txn.collect_events()
        txn.settle()
        events = txn.collect_events()
        assert any(e.event_type == "TransactionSettled" for e in events)

    def test_cannot_settle_already_settled(self):
        txn = make_transaction()
        txn.settle()
        with pytest.raises(TransactionAlreadySettledError):
            txn.settle()

    def test_cannot_settle_failed_transaction(self):
        txn = make_transaction()
        txn.fail("Insufficient funds")
        with pytest.raises(InvalidTransactionError):
            txn.settle()

    def test_fail_sets_reason_and_increments_version(self):
        txn = make_transaction()
        txn.fail("Network timeout")
        assert txn.status == TransactionStatus.FAILED
        assert txn.failure_reason == "Network timeout"
        assert txn.version == 1

    def test_cancel_transitions_and_increments_version(self):
        txn = make_transaction()
        txn.cancel()
        assert txn.status == TransactionStatus.CANCELLED
        assert txn.version == 1

    def test_soft_delete_sets_deleted_at(self):
        txn = make_transaction()
        txn.soft_delete()
        assert txn.deleted_at is not None
        assert txn.version == 1
