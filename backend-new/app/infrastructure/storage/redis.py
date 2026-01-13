import redis.asyncio as redis
from app.core.config import get_settings


class RedisCache:
    _instance: redis.Redis = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            settings = get_settings()

            cls._instance = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )

        return cls._instance

    @classmethod
    async def set(cls, key: str, value: str, expire: int = 3600):
        client = await cls.get_client()
        await client.setex(key, expire, value)

    @classmethod
    async def get(cls, key: str) -> str | None:
        client = await cls.get_client()
        return await client.get(key)

    @classmethod
    async def delete(cls, key: str):
        client = await cls.get_client()
        await client.delete(key)

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
