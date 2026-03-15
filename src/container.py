"""
Dependency injection container.
Plain Python module — no DI framework magic.
All singletons are instantiated here and exposed as module-level attributes.
FastAPI Depends() calls factory functions that reference these singletons.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.cache.redis_client import RedisClient
from src.infrastructure.database.engine import create_engine, create_session_factory
from src.infrastructure.storage.gcs_storage import GCSStorage
from src.settings import settings


class Container:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._redis: RedisClient | None = None
        self._gcs: GCSStorage | None = None
        self._jwt: JWTService | None = None

    def setup(self) -> None:
        """Initialize all singletons. Called once at application startup."""
        self._engine = create_engine()
        self._session_factory = create_session_factory(self._engine)
        self._redis = RedisClient(settings)
        self._gcs = GCSStorage(settings)
        self._jwt = JWTService(settings)

    async def teardown(self) -> None:
        """Clean up resources. Called at application shutdown."""
        if self._engine:
            await self._engine.dispose()
        if self._redis:
            await self._redis.close()

    @property
    def engine(self) -> AsyncEngine:
        assert self._engine is not None, "Container not initialized. Call setup() first."
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        assert self._session_factory is not None, "Container not initialized."
        return self._session_factory

    @property
    def redis(self) -> RedisClient:
        assert self._redis is not None, "Container not initialized."
        return self._redis

    @property
    def gcs_storage(self) -> GCSStorage:
        assert self._gcs is not None, "Container not initialized."
        return self._gcs

    @property
    def jwt_service(self) -> JWTService:
        assert self._jwt is not None, "Container not initialized."
        return self._jwt


container = Container()
