from pydantic import BaseModel, Field
from typing import Optional


class CreateSessionRequest(BaseModel):
    pass


class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="Session ID")
    sandbox_id: str = Field(..., description="Sandbox container ID")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    timestamp: Optional[int] = None


class ChatEvent(BaseModel):
    event_type: str = Field(..., description="Event type: step, done, error")
    step: Optional[str] = Field(None, description="Current step")
    message: Optional[str] = Field(None, description="Event message")


class SessionResponse(BaseModel):
    session_id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    events: list = []
    unread_message_count: int = 0


class ListSessionsResponse(BaseModel):
    sessions: list[SessionResponse]
