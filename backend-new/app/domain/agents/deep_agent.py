from typing import List, Dict, Any, AsyncGenerator
from langchain_core.tools import BaseTool as LangChainTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from .base import BaseAgent
from ..graph.state import AgentState
from ..graph.nodes import create_planner_node, create_executor_node, create_reflector_node


class DeepAgent(BaseAgent):
    def __init__(self, tools: List[LangChainTool] = [], max_iterations: int = 10):
        super().__init__(tools)
        self.max_iterations = max_iterations

    def _build_graph(self, llm, sandbox):
        graph = StateGraph(AgentState)

        # 创建节点
        planner = create_planner_node(llm, sandbox)
        executor = create_executor_node(llm, sandbox, self.tools)
        reflector = create_reflector_node(llm, sandbox)

        # 添加节点
        graph.add_node("planner", planner)
        graph.add_node("executor", executor)
        graph.add_node("reflector", reflector)

        # 添加边
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "reflector")

        # 添加条件边 - 修复：直接返回节点名
        def should_continue(state):
            """决定是否继续执行"""
            if state.get("is_complete", False) or state.get("current_step", 0) >= self.max_iterations:
                return END
            return "executor"

        graph.add_conditional_edges(
            "reflector",
            should_continue,
            {END: END, "executor": "executor"}
        )

        # 设置入口点
        graph.set_entry_point("planner")

        return graph.compile()

    async def execute(self, llm, sandbox, request: str) -> AsyncGenerator[Dict[str, Any], None]:
        graph = self._build_graph(llm, sandbox)

        initial_state = {
            "messages": [HumanMessage(content=request)],
            "current_step": 0,
            "plan": [],
            "results": [],
            "is_complete": False,
            "final_message": None
        }

        try:
            async for event in graph.astream(initial_state, stream_mode="updates"):
                if not event:
                    continue

                node_name = list(event.keys())[0]
                node_output = event.get(node_name, {})

                # 发送步骤事件
                yield {
                    "type": "step",
                    "step": node_name,
                    "message": self._format_step_message(node_name, node_output)
                }

                # 检查是否完成
                if node_output.get("is_complete", False):
                    yield {
                        "type": "done",
                        "message": node_output.get("final_message", "Task completed")
                    }
                    break

        except Exception as e:
            yield {
                "type": "error",
                "message": f"Agent execution failed: {str(e)}"
            }

    def _format_step_message(self, node_name: str, node_output: Dict[str, Any]) -> str:
        """格式化步骤消息"""
        if node_name == "planner":
            plan = node_output.get("plan", [])
            return f"Planning: {len(plan)} steps generated"
        elif node_name == "executor":
            results = node_output.get("results", [])
            return f"Executing: {len(results)} actions completed"
        elif node_name == "reflector":
            is_complete = node_output.get("is_complete", False)
            return f"Reflecting: {'Task complete' if is_complete else 'Continuing execution'}"
        return f"{node_name}: Processing..."
