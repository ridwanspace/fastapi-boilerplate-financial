---
paths:
  - "tests/**/*.py"
---

# Testing Rules

## Test Markers

- `@pytest.mark.unit` — pure logic, no I/O, no DB, no external calls
- `@pytest.mark.integration` — real PostgreSQL via `db_session` fixture
- `@pytest.mark.e2e` — full HTTP stack via `async_client` fixture

## Unit Tests

- No mocks of internal domain/application logic
- No database, no file system, no network
- Test one behaviour per test function
- Use `make_transaction(**overrides)` helper pattern — never repeat construction boilerplate
- `pytest.raises()` must always specify a **concrete exception class**, never bare `Exception`:
  - Frozen dataclass mutation → `FrozenInstanceError` (from `dataclasses`)
  - Invalid domain transition → the specific domain exception (e.g., `InvalidTransactionError`)
  - Use `match=` parameter if the same exception type can be raised for different reasons

## Integration Tests

- Use `db_session: AsyncSession` fixture from `tests/conftest.py`
- Each test runs inside a transaction that is rolled back on teardown — tests are isolated automatically
- **Never mock the database** — we were burned by mock/prod divergence before
- Test the full repo method, including DB constraints (e.g., test that immutable status raises)

## Test Naming

- `test_<what>_<expected_outcome>` — e.g., `test_settle_increments_version`, `test_returns_none_for_unknown_id`
- Class per behaviour group: `TestTransactionCreation`, `TestTransactionSettlement`

## Coverage

- Minimum 80% overall
- Domain entities: 100% target — they are pure logic with no external dependencies
- Run: `pytest --cov=src --cov-report=term-missing`
