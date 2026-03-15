# API Reference

> **Navigation:** [README](../../README.md) · [Getting Started](getting-started.md) · [Architecture](architecture.md) · [Troubleshooting](troubleshooting.md)

All endpoints are prefixed with `/api/v1`.

---

## Table of Contents

- [Auth Endpoints](#auth-endpoints)
- [Transaction Endpoints](#transaction-endpoints)
- [System Endpoints](#system-endpoints)
- [Security Behaviour](#security-behaviour)

---

## Auth Endpoints

> **Rate limited:** `POST /auth/token` — 10 requests/minute per IP. `POST /auth/refresh` — 20 requests/minute per IP.

### `POST /api/v1/auth/token` — Issue token pair

Request:
```json
{
  "username": "demo",
  "password": "demo"
}
```

Response `200 OK`:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

> **Important — Production behaviour:** In `APP_ENV=production` this endpoint returns `501 Not Implemented` until you wire a real user repository. Replace the stub in `src/infrastructure/auth/router.py`. The demo credentials (`demo/demo`) work only in `development` and `staging`.

See the [Auth Flow diagram](architecture.md#auth-flow) for the full token lifecycle.

---

### `POST /api/v1/auth/refresh` — Refresh token pair

Request:
```json
{
  "refresh_token": "eyJ..."
}
```

Response `200 OK`: same structure as token issuance.

---

## Transaction Endpoints

All transaction endpoints require a valid Bearer token:

```
Authorization: Bearer <access_token>
```

### `POST /api/v1/transactions` — Create a transaction

Supports idempotent retries via `Idempotency-Key` header. Safe to retry on network failure — a repeated request with the same key returns the original response without creating a duplicate.

**Headers:**

| Header | Required | Description |
|---|---|---|
| `Authorization` | **Yes** | `Bearer <access_token>` |
| `Idempotency-Key` | Recommended | Client-generated unique key (e.g. UUID). Prevents double-spend on retry. |

**Request:**
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "1500.00",
  "currency": "USD",
  "transaction_type": "credit",
  "reference": "SALARY-2026-03"
}
```

**Response `201 Created`:**
```json
{
  "id": "a1b2c3d4-...",
  "account_id": "550e8400-...",
  "amount": "1500.0000",
  "currency": "USD",
  "transaction_type": "credit",
  "status": "pending",
  "reference": "SALARY-2026-03",
  "idempotency_key": "my-client-key-001",
  "failure_reason": null,
  "settled_at": null,
  "version": 0,
  "created_at": "2026-03-15T10:00:00Z",
  "updated_at": "2026-03-15T10:00:00Z"
}
```

> **Note:** `amount` is always returned as a **decimal string** (e.g. `"1500.0000"`), not a JSON number, to guarantee precision is preserved for all clients.

**Transaction types:** `credit` | `debit` | `transfer`

---

### `GET /api/v1/transactions` — List transactions

**Query parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `account_id` | **Yes** | — | Filter by account ID (UUID) |
| `page` | No | `1` | Page number (1-indexed) |
| `page_size` | No | `20` | Results per page (max 100) |
| `status` | No | — | Filter by status: `pending`, `settled`, `failed`, `cancelled` |

**Response `200 OK`:**
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "has_next": true,
  "has_previous": false
}
```

---

### `POST /api/v1/transactions/{transaction_id}/settle` — Settle a transaction

Records `settled_by_id` from the authenticated user automatically.

**Response `200 OK`:** same structure as create, with `status: "settled"`, `settled_at` populated, and `version` incremented to `1`.

**Error responses:**

| Status | When |
|---|---|
| `401 Unauthorized` | Missing or invalid Bearer token |
| `404 Not Found` | Transaction ID does not exist or is soft-deleted |
| `409 Conflict` | Transaction is already settled/cancelled/failed (immutable) |
| `409 Conflict` | Concurrent update detected (optimistic lock) — client should retry |
| `400 Bad Request` | Other domain validation failure |

---

## System Endpoints

### `GET /api/v1/health` — Deep health check

Probes all three downstream services. Does not require authentication.

Response `200 OK`:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development",
  "services": {
    "database": "ok",
    "redis": "ok",
    "storage": "ok"
  }
}
```

`status` is `"ok"` when all services are healthy, `"degraded"` when one or more are unavailable (individual service statuses show which).

---

## Security Behaviour

### Auth stub in production

`POST /auth/token` is intentionally blocked in production (`APP_ENV=production`) until a real user repository is wired:

```python
# src/infrastructure/auth/router.py
if settings.is_production:
    raise HTTPException(status_code=501, detail="Authentication backend not configured.")
```

To implement real auth: replace the stub in `src/infrastructure/auth/router.py` with a lookup against your users table, validate the password with `passlib`, and return the token pair.

### Rate limiting

| Endpoint | Limit | Scope |
|---|---|---|
| `POST /auth/token` | 10 requests/minute | Per IP |
| `POST /auth/refresh` | 20 requests/minute | Per IP |
| All other routes | 200 requests/minute | Per IP (global default) |

Exceeded limits return `429 Too Many Requests`.

### Idempotency

All mutation endpoints that could cause financial harm support idempotency via the `Idempotency-Key` request header. Send a unique client-generated key (e.g. a UUID) with each request. If you retry with the same key, the original response is returned without re-executing the operation.

```bash
curl -X POST /api/v1/transactions \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Authorization: Bearer ..." \
  -d '{"amount": "500.00", ...}'
```

See the [Idempotency Flow diagram](architecture.md#idempotency-flow) for the internal implementation.

### Production startup validation

On startup, `_validate_production_config()` checks:
- `DEBUG` must be `False`
- `GCS_PROJECT_ID` must be set
- `GCS_BUCKET_NAME` must be set

The application refuses to start if any check fails.

### CORS

CORS is configured with explicit allowed methods and headers — no wildcards:

```python
allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
allow_headers=["Authorization", "Content-Type", "X-Correlation-ID", "Idempotency-Key"]
```

---

## Related Guides

- [Architecture](architecture.md) — request lifecycle, auth flow, idempotency design
- [Getting Started](getting-started.md) — running the server
- [Troubleshooting](troubleshooting.md) — common API errors
- [Back to README](../../README.md)
