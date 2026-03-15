---
paths:
  - "src/contexts/*/api/**/*.py"
  - "src/api/**/*.py"
---

# API Layer Rules

## Request / Response Schemas

- All request schemas: `model_config = ConfigDict(strict=True)`
- Monetary amounts in **responses**: `amount: str` — serialise as `str(dto.amount)`, never `Decimal` or `float`
- Monetary amounts in **requests**: `amount: Decimal` — validated with `Annotated[Decimal, Field(gt=0)]`
- Include `version: int` in every financial resource response (client needs it for optimistic locking)
- Include `idempotency_key: str | None` in every financial resource response

## Router Conventions

- `POST` endpoints that create resources: accept `Idempotency-Key` header
  ```python
  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
  ```
- Map domain exceptions to HTTP status codes in the router (not in the handler):
  - `NotFoundError` → 404
  - `ConflictError` / `DuplicateTransactionError` → 409
  - `TransactionImmutableError` → 409
  - `TransactionConcurrentUpdateError` → 409
- Result unwrapping pattern:
  ```python
  result = await handler.handle(command)
  if isinstance(result, Err):
      raise_http_exception(result.error)
  return result.value
  ```
- Always inject `current_user: CurrentUser = Depends(get_current_user)` on protected routes
- Pass `current_user.user_id` as `created_by_id` / `settled_by_id` to commands

## Rate Limiting

- Auth endpoints must be decorated with `@_limiter.limit("10/minute")`
- Token refresh: `@_limiter.limit("20/minute")`
- New sensitive endpoints (password reset, etc.): apply explicit per-route limits
