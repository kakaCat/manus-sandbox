from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings


class MongoDB:
    _instance: AsyncIOMotorClient = None

    @classmethod
    async def get_client(cls) -> AsyncIOMotorClient:
        if cls._instance is None:
            settings = get_settings()

            client_kwargs = {
                "host": settings.mongodb_uri
            }

            if settings.mongodb_username and settings.mongodb_password:
                client_kwargs.update({
                    "username": settings.mongodb_username,
                    "password": settings.mongodb_password
                })

            cls._instance = AsyncIOMotorClient(**client_kwargs)

        return cls._instance

    @classmethod
    async def get_database(cls):
        client = await cls.get_client()
        settings = get_settings()
        return client[settings.mongodb_database]

    @classmethod
    async def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None
