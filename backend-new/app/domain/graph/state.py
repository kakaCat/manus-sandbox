from typing import List, Any, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    current_step: int
    plan: List[str]
    results: List[Any]
    is_complete: bool
    final_message: str | None
