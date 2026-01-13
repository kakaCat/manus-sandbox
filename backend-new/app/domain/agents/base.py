from typing import List, Dict, Any, AsyncGenerator
from langchain_core.tools import BaseTool as LangChainTool
from langchain_core.messages import BaseMessage


class ToolResult:
    success: bool
    message: str
    data: Dict[str, Any] | None = None

    def __init__(self, success: bool, message: str, data: Dict[str, Any] | None = None):
        self.success = success
        self.message = message
        self.data = data

    def model_dump_json(self) -> str:
        import json
        return json.dumps({
            "success": self.success,
            "message": self.message,
            "data": self.data
        })


class BaseAgent:
    name: str = ""
    system_prompt: str = ""
    tools: List[LangChainTool] = []

    def __init__(self, tools: List[LangChainTool] = []):
        self.tools = tools

    async def execute(self, request: str) -> AsyncGenerator[Dict[str, Any], None]:
        pass
