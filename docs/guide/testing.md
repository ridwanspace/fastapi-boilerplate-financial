# Testing

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Adding a Bounded Context](adding-a-bounded-context.md)

---

## Table of Contents

- [Running Tests](#running-tests)
- [Test Tiers](#test-tiers)
- [Integration Test Isolation](#integration-test-isolation)
- [Running a Specific Test](#running-a-specific-test)
- [Coverage Report](#coverage-report)

---

## Running Tests

```bash
# Run all tests with coverage report
make test

# Run only unit tests (no external dependencies — fastest)
make test-unit

# Run only integration tests (requires PostgreSQL)
make test-integration

# Run only e2e tests (requires running app + PostgreSQL)
make test-e2e
```

---

## Test Tiers

| Tier | Marker | Speed | Requires | What it tests |
|---|---|---|---|---|
| Unit | `@pytest.mark.unit` | ~100ms total | Nothing | Domain logic, Money arithmetic, transaction state machine, version increments, soft-delete |
| Integration | `@pytest.mark.integration` | ~2–10s | PostgreSQL | Repository: idempotency, immutability enforcement, soft-delete filtering, audit fields, optimistic locking |
| E2E | `@pytest.mark.e2e` | ~5–30s | PostgreSQL + Redis | Full HTTP stack from request to response, auth requirements |

**Test file locations:**

| Test file | What it covers |
|---|---|
| `tests/unit/domain/test_money_value_object.py` | Decimal arithmetic, rounding, immutability |
| `tests/unit/domain/test_transaction_entity.py` | State transitions, version, audit, soft-delete |
| `tests/integration/repositories/test_transaction_repository.py` | Idempotency, immutability, soft-delete filtering, audit fields |
| `tests/e2e/test_transaction_endpoints.py` | Full HTTP stack |

When adding a new bounded context, follow the same pattern. See [Adding a Bounded Context — Step 8](adding-a-bounded-context.md#step-8--write-tests).

---

## Integration Test Isolation

Integration tests do **not** recreate the database schema between tests. Instead, each test runs inside a transaction that is rolled back at teardown. This is 10–50× faster than truncating tables.

```
Session begins
  └─ BEGIN transaction (before each test)
       └─ test runs — inserts, updates, queries
  └─ ROLLBACK (after each test — changes discarded)
Session ends
```

**Key rules:**
- Never mock the database in integration tests — use the real `db_session` fixture
- The `db_session` fixture is defined in `tests/conftest.py`
- Each test is fully isolated despite sharing the schema

---

## Running a Specific Test

```bash
# All tests in a file
pytest tests/unit/domain/test_transaction_entity.py -v

# A specific test by name
pytest tests/unit/domain/test_transaction_entity.py -v -k "test_settle_increments_version"

# All tests matching a keyword
pytest -v -k "idempotency"
```

---

## Coverage Report

After `make test`, an HTML report is generated at `htmlcov/index.html`:

```bash
open htmlcov/index.html       # macOS
xdg-open htmlcov/index.html   # Linux
```

---

## Related Guides

- [Adding a Bounded Context](adding-a-bounded-context.md) — test expectations for new contexts
- [Getting Started](getting-started.md) — setting up the test database
- [Make Reference](make-reference.md) — all test commands
- [Back to README](../../README.md)
