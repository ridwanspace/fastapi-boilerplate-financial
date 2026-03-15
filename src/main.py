from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.api.middleware.correlation_id import CorrelationIdMiddleware
from src.api.middleware.error_handler import (
    DomainError,
    domain_error_handler,
    unhandled_error_handler,
)
from src.api.middleware.request_logging import RequestLoggingMiddleware
from src.api.router import api_router
from src.container import container
from src.settings import settings


logger = structlog.get_logger(__name__)

# Rate limiter — shared instance, referenced by route decorators
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    _validate_production_config()
    logger.info("startup", environment=settings.app_env, version=settings.app_version)
    container.setup()

    if settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            traces_sample_rate=0.1,
        )
        logger.info("sentry_initialized")

    yield
    await container.teardown()
    logger.info("shutdown")


def _validate_production_config() -> None:
    """Fail fast if critical production settings are missing or unsafe."""
    if not settings.is_production:
        return
    errors = []
    if settings.debug:
        errors.append("DEBUG must be False in production")
    if not settings.gcs_project_id:
        errors.append("GCS_PROJECT_ID is required in production")
    if not settings.gcs_bucket_name:
        errors.append("GCS_BUCKET_NAME is required in production")
    if errors:
        raise RuntimeError(f"Invalid production configuration: {'; '.join(errors)}")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Rate limiting state
    app.state.limiter = limiter

    # Middleware (registered in reverse order — last added runs first)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Correlation-ID", "Idempotency-Key"],
        expose_headers=["X-Correlation-ID"],
    )

    # Exception handlers
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DomainError, domain_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)

    # Routers
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
