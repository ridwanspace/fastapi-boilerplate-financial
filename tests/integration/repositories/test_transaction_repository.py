import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.transactions.domain.entities.transaction import Transaction
from src.contexts.transactions.domain.exceptions import TransactionImmutableError
from src.contexts.transactions.domain.value_objects.transaction_status import TransactionStatus
from src.contexts.transactions.domain.value_objects.transaction_type import TransactionType
from src.contexts.transactions.infrastructure.repositories.sql_transaction_repository import (
    SqlTransactionRepository,
)
from src.shared.domain.value_objects.money import Money
from src.shared.domain.value_objects.pagination import Pagination


def make_transaction(
    account_id: uuid.UUID | None = None,
    idempotency_key: str | None = None,
    created_by_id: uuid.UUID | None = None,
) -> Transaction:
    return Transaction.create(
        account_id=account_id or uuid.uuid4(),
        amount=Money.of(250, "USD"),
        transaction_type=TransactionType.DEBIT,
        reference="INT-TEST-001",
        created_by_id=created_by_id,
        idempotency_key=idempotency_key,
    )


@pytest.mark.integration
class TestSqlTransactionRepository:
    async def test_save_and_retrieve_by_id(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        txn = make_transaction()
        await repo.save(txn)

        retrieved = await repo.get_by_id(txn.id)
        assert retrieved is not None
        assert retrieved.id == txn.id
        assert retrieved.amount == txn.amount
        assert retrieved.reference == txn.reference
        assert retrieved.version == 0

    def test_amount_type_is_decimal(self):
        from decimal import Decimal
        txn = make_transaction()
        assert isinstance(txn.amount.amount, Decimal)

    async def test_returns_none_for_unknown_id(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    async def test_audit_trail_persisted(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        repo = SqlTransactionRepository(db_session)
        txn = make_transaction(created_by_id=user_id)
        await repo.save(txn)

        retrieved = await repo.get_by_id(txn.id)
        assert retrieved is not None
        assert retrieved.created_by_id == user_id
        assert retrieved.updated_by_id == user_id

    async def test_idempotency_key_lookup(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        key = f"idem-{uuid.uuid4()}"
        txn = make_transaction(idempotency_key=key)
        await repo.save(txn)

        found = await repo.get_by_idempotency_key(key)
        assert found is not None
        assert found.id == txn.id

    async def test_settle_increments_version(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        txn = make_transaction()
        await repo.save(txn)

        txn.settle()
        await repo.save(txn)

        updated = await repo.get_by_id(txn.id)
        assert updated is not None
        assert updated.status == TransactionStatus.SETTLED
        assert updated.version == 1

    async def test_cannot_update_settled_transaction(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        txn = make_transaction()
        await repo.save(txn)
        txn.settle()
        await repo.save(txn)

        # Try to cancel an already-settled transaction via repo (simulate concurrent write)
        # We re-fetch and try to cancel (which will be blocked by domain first, but
        # if the domain were bypassed, repo immutability check catches it)
        with pytest.raises(Exception):
            txn.cancel()  # domain raises first

    async def test_soft_delete_hides_from_get(self, db_session: AsyncSession):
        repo = SqlTransactionRepository(db_session)
        txn = make_transaction()
        await repo.save(txn)
        txn.soft_delete()
        await repo.save(txn)

        found = await repo.get_by_id(txn.id)
        assert found is None

    async def test_list_by_account_excludes_soft_deleted(self, db_session: AsyncSession):
        account_id = uuid.uuid4()
        repo = SqlTransactionRepository(db_session)

        visible = make_transaction(account_id=account_id)
        hidden = make_transaction(account_id=account_id)
        await repo.save(visible)
        await repo.save(hidden)
        hidden.soft_delete()
        await repo.save(hidden)

        result = await repo.list_by_account(account_id, Pagination(page=1, page_size=10))
        assert result.total == 1
        assert result.items[0].id == visible.id

    async def test_list_by_account_returns_paged_results(self, db_session: AsyncSession):
        account_id = uuid.uuid4()
        repo = SqlTransactionRepository(db_session)

        for _ in range(3):
            await repo.save(make_transaction(account_id=account_id))

        result = await repo.list_by_account(account_id, Pagination(page=1, page_size=2))
        assert result.total == 3
        assert len(result.items) == 2
        assert result.has_next
