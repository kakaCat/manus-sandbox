from langchain_core.tools import BaseTool as LangChainTool
from pydantic import BaseModel, Field


class BaseTool(LangChainTool):
    name: str
    description: str

    def __init__(self, sandbox):
        super().__init__(name=self.name, description=self.description, func=self._run)
        self.sandbox = sandbox

    def _run(self, **kwargs) -> str:
        pass
