import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


logger = structlog.get_logger(__name__)


class DomainError(Exception):
    """Base class for domain-level errors surfaced to the API layer."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass


_DOMAIN_ERROR_STATUS_MAP: dict[type[DomainError], int] = {
    NotFoundError: HTTP_404_NOT_FOUND,
    ConflictError: HTTP_409_CONFLICT,
    ValidationError: HTTP_422_UNPROCESSABLE_ENTITY,
    DomainError: HTTP_400_BAD_REQUEST,
}


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = next(
        (code for exc_type, code in _DOMAIN_ERROR_STATUS_MAP.items() if isinstance(exc, exc_type)),
        HTTP_400_BAD_REQUEST,
    )
    logger.warning("domain_error", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    logger.exception("unhandled_error", path=request.url.path)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
