from typing import List, Optional, AsyncGenerator
from datetime import datetime
import uuid

from ..domain.models.session import Session
from ..infrastructure.storage.mongodb import MongoDB
from ..infrastructure.storage.redis import RedisCache
from ..infrastructure.sandbox.docker_sandbox import DockerSandbox


class SessionService:
    def __init__(self):
        self.db = MongoDB()
        self.cache = RedisCache()

    async def create(self, user_id: str, sandbox: DockerSandbox) -> Session:
        session_id = str(uuid.uuid4())

        session = Session(
            id=session_id,
            user_id=user_id,
            status="active"
        )

        await self._save(session)
        await self.cache.set(f"sandbox:{session_id}", sandbox.id, expire=1800)

        return session

    async def get(self, session_id: str, user_id: Optional[str] = None) -> Optional[Session]:
        data = await self._find_one(session_id, user_id)

        if not data:
            return None

        return Session(**data)

    async def get_all(self, user_id: str) -> List[Session]:
        db = await self.db.get_database()
        cursor = db.sessions.find({"user_id": user_id}).sort("created_at", -1)
        sessions = []
        async for doc in cursor:
            sessions.append(Session(**doc))
        return sessions

    async def update_status(self, session_id: str, status: str):
        db = await self.db.get_database()
        await db.sessions.update_one(
            {"id": session_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )

    async def add_event(self, session_id: str, event: dict):
        db = await self.db.get_database()
        await db.sessions.update_one(
            {"id": session_id},
            {
                "$push": {"events": event},
                "$set": {"updated_at": datetime.utcnow()}}
        )

    async def delete(self, session_id: str):
        db = await self.db.get_database()
        await db.sessions.delete_one({"id": session_id})

    async def _save(self, session: Session):
        db = await self.db.get_database()
        await db.sessions.insert_one(session.model_dump())

    async def _find_one(self, session_id: str, user_id: Optional[str] = None):
        db = await self.db.get_database()
        query = {"id": session_id}

        if user_id:
            query["user_id"] = user_id

        return await db.sessions.find_one(query)

    async def close(self):
        await self.db.close()
        await self.cache.close()
