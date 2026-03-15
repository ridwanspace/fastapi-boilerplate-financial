import sqlalchemy
from fastapi import APIRouter

from src.api.schemas.health import HealthResponse, ServiceStatus
from src.container import container
from src.infrastructure.auth.router import router as auth_router
from src.settings import settings

from src.contexts.transactions.api.router import router as transactions_router
# from src.contexts.accounts.api.router import router as accounts_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(transactions_router)
# api_router.include_router(accounts_router)


@api_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["system"],
)
async def health_check() -> HealthResponse:
    db_ok = "ok"
    redis_ok = "ok"
    storage_ok = "ok"

    try:
        async with container.session_factory() as session:
            await session.execute(sqlalchemy.text("SELECT 1"))
    except Exception:
        db_ok = "unavailable"

    try:
        redis_ok = "ok" if await container.redis.ping() else "unavailable"
    except Exception:
        redis_ok = "unavailable"

    try:
        # Probe GCS with a lightweight exists() call on a sentinel path
        await container.gcs_storage.exists("health-check/.probe")
        storage_ok = "ok"
    except Exception:
        storage_ok = "unavailable"

    all_ok = all(s == "ok" for s in [db_ok, redis_ok, storage_ok])

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        version=settings.app_version,
        environment=settings.app_env,
        services=ServiceStatus(
            database=db_ok,
            redis=redis_ok,
            storage=storage_ok,
        ),
    )
