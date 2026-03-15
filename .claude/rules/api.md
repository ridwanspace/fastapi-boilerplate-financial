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
- Result unwrapping pattern — always `assert isinstance(result, Ok)` after the error guard so mypy
  can narrow the type:
  ```python
  from src.shared.application.result import Ok
  result = await handler.handle(command)
  if result.is_err():
      raise HTTPException(status_code=400, detail=str(result.unwrap()))
  assert isinstance(result, Ok)
  return SomeResponse.from_dto(result.unwrap())
  ```
- Always inject `current_user: CurrentUser = Depends(get_current_user)` on protected routes
- Pass `current_user.user_id` as `created_by_id` / `settled_by_id` to commands
- FastAPI and slowapi require certain parameters in handler signatures even when unused in the body
  (`request: Request` for rate-limited routes, `app: FastAPI` in lifespan, `exc` in exception handlers).
  Suppress the lint warning with `# noqa: ARG001` — do **not** remove the parameter

## Rate Limiting

- Auth endpoints must be decorated with `@_limiter.limit("10/minute")`
- Token refresh: `@_limiter.limit("20/minute")`
- New sensitive endpoints (password reset, etc.): apply explicit per-route limits
