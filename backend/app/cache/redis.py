import hashlib
import json

from redis.asyncio import Redis

from app.config import Settings


class RedisCache:
    def __init__(self, settings: Settings) -> None:
        self.client = Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.cache_ttl_seconds
        self.enabled = settings.cache_enabled

    async def get(self, namespace: str, params: dict) -> str | None:
        if not self.enabled:
            return None

        try:
            version = await self.get_version(namespace)
            return await self.client.get(self.make_key(namespace, version, params))
        except Exception:
            return None

    async def set(self, namespace: str, params: dict, value: str) -> None:
        if not self.enabled:
            return

        try:
            version = await self.get_version(namespace)
            await self.client.set(
                self.make_key(namespace, version, params),
                value,
                ex=self.ttl,
            )
        except Exception:
            pass

    async def invalidate(self, namespace: str) -> None:
        if not self.enabled:
            return

        try:
            await self.client.incr(f"{namespace}:cache_version")
        except Exception:
            pass

    async def get_version(self, namespace: str) -> int:
        key = f"{namespace}:cache_version"
        version = await self.client.get(key)
        if version is None:
            await self.client.set(key, 1)
            return 1
        return int(version)

    @staticmethod
    def make_key(namespace: str, version: int, params: dict) -> str:
        serialized = json.dumps(params, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(serialized.encode()).hexdigest()
        return f"{namespace}:list:v{version}:{digest}"

    async def ping(self) -> bool:
        return await self.client.ping()

    async def close(self) -> None:
        await self.client.aclose()
