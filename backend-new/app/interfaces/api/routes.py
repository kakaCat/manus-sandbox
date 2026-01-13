from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator, Optional

from app.application.agent_service import AgentService
from app.interfaces.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    ChatRequest,
    SessionResponse,
    ListSessionsResponse,
    ChatEvent
)


router = APIRouter(prefix="/api/v1")

agent_service = AgentService()


@router.put("/sessions", response_model=CreateSessionResponse)
async def create_session(user_id: str = "anonymous"):
    try:
        result = await agent_service.create_session(user_id)
        return CreateSessionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user_id: str = "anonymous"):
    session = await agent_service.session_service.get(session_id, user_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.id,
        title=session.title,
        status=session.status,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        events=session.events,
        unread_message_count=session.unread_message_count
    )


@router.get("/sessions", response_model=ListSessionsResponse)
async def list_sessions(user_id: str = "anonymous"):
    sessions = await agent_service.session_service.get_all(user_id)

    session_responses = [
        SessionResponse(
            session_id=s.id,
            title=s.title,
            status=s.status,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
            events=s.events,
            unread_message_count=s.unread_message_count
        )
        for s in sessions
    ]

    return ListSessionsResponse(sessions=session_responses)


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str = "anonymous"):
    await agent_service.session_service.delete(session_id)
    return {"message": "Session deleted"}


@router.post("/sessions/{session_id}/stop")
async def stop_session(session_id: str, user_id: str = "anonymous"):
    try:
        await agent_service.stop_session(session_id, user_id)
        return {"message": "Session stopped"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/chat")
async def chat_session(session_id: str, request: ChatRequest, user_id: str = "anonymous"):
    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            async for event in agent_service.chat(session_id, user_id, request.message):
                yield event
        except Exception as e:
            yield {
                "event_type": "error",
                "message": str(e)
            }

    return EventSourceResponse(event_generator())
