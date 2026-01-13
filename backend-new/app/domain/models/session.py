from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class Session(BaseModel):
    id: str
    user_id: str
    title: str = "New Session"
    status: str = "idle"
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    events: List[dict] = []
    unread_message_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
