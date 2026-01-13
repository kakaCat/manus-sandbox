from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.interfaces.api.routes import router
from app.application.agent_service import AgentService
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
agent_service = None  # Will be initialized in lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Manus AI Agent (LangChain + LangGraph)")

    global agent_service
    agent_service = AgentService()

    yield

    logger.info("Shutting down Manus AI Agent")
    await agent_service.close()


app = FastAPI(
    title="Manus AI Agent - LangChain + LangGraph",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/")
async def root():
    return {
        "name": "Manus AI Agent",
        "version": "2.0.0",
        "architecture": "LangChain + LangGraph + DeepAgent"
    }
