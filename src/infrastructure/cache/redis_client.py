from typing import Any

import redis.asyncio as aioredis

from src.settings import Settings


class RedisClient:
    def __init__(self, settings: Settings) -> None:
        self._pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)  # type: ignore[return-value]

    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: int | None = None,
    ) -> None:
        await self._client.set(key, value, ex=expire_seconds)

    async def delete(self, *keys: str) -> None:
        await self._client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def increment(self, key: str, amount: int = 1) -> int:
        return await self._client.incrby(key, amount)  # type: ignore[return-value]

    async def expire(self, key: str, seconds: int) -> None:
        await self._client.expire(key, seconds)

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        await self._pool.disconnect()

    async def get_json(self, key: str) -> Any | None:
        import json

        raw = await self.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: Any, expire_seconds: int | None = None) -> None:
        import json

        await self.set(key, json.dumps(value), expire_seconds=expire_seconds)
