from typing import AsyncGenerator, Optional, Dict, Any, List, Annotated
import logging
import httpx
import tempfile
import os
from typing_extensions import TypedDict

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from ..infrastructure.llm.langchain_llm import create_llm
from ..infrastructure.sandbox.docker_sandbox import DockerSandbox
from .session_service import SessionService
from app.core.config import get_settings

logger = logging.getLogger(__name__)


# 定义DeepAgent状态
class DeepAgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    current_step: int
    plan: List[str]
    results: List[Any]
    is_complete: bool
    final_message: Optional[str]
    workspace_dir: str  # 文件系统工作目录


# 创建沙盒工具
def create_sandbox_tools(sandbox: DockerSandbox):
    """创建与沙盒集成的工具"""

    @tool
    async def browser_navigate(url: str) -> str:
        """Navigate browser to a specific URL and return page content."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{sandbox.base_url}/browser/navigate",
                    json={"url": url}
                )
                result = response.json()
                return result.get('data', {}).get('content', f'Successfully navigated to {url}')
        except Exception as e:
            logger.error(f"Browser navigation failed: {e}")
            return f"Failed to navigate to {url}: {str(e)}"

    @tool
    async def browser_view() -> str:
        """Get current browser page content."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{sandbox.base_url}/browser/view")
                result = response.json()
                return result.get('data', {}).get('content', 'No content available')
        except Exception as e:
            logger.error(f"Browser view failed: {e}")
            return f"Failed to view page: {str(e)}"

    @tool
    async def shell_execute(command: str) -> str:
        """Execute shell command in sandbox environment."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{sandbox.base_url}/shell/execute",
                    json={"command": command}
                )
                result = response.json()
                return result.get('data', {}).get('output', 'Command executed')
        except Exception as e:
            logger.error(f"Shell execution failed: {e}")
            return f"Failed to execute command: {str(e)}"

    @tool
    async def file_read(path: str) -> str:
        """Read content from a file in sandbox."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{sandbox.base_url}/file/read?path={path}")
                result = response.json()
                return result.get('data', {}).get('content', 'File not found')
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return f"Failed to read file {path}: {str(e)}"

    @tool
    async def file_write(path: str, content: str) -> str:
        """Write content to a file in sandbox."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{sandbox.base_url}/file/write",
                    json={"path": path, "content": content}
                )
                result = response.json()
                return result.get('data', {}).get('message', 'File written successfully')
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return f"Failed to write file {path}: {str(e)}"

    return [browser_navigate, browser_view, shell_execute, file_read, file_write]


# DeepAgent节点函数
def create_planner_node(llm):
    """创建规划节点"""
    async def planner(state: DeepAgentState) -> Dict[str, Any]:
        messages = state["messages"]
        current_step = state.get("current_step", 0)

        prompt = f"""You are a planning agent for a powerful AI assistant. Break down the user's task into a clear, actionable step-by-step plan.

Task: {messages[-1].content if messages else "No task provided"}

Create a numbered list of specific, executable steps. Each step should be:
- Clear and actionable
- Focused on a single objective
- Consider using available tools: browser navigation, file operations, shell commands

Return only the numbered list, no additional text."""

        try:
            response = await llm.ainvoke(prompt)
            plan_text = response.content.strip()

            # 解析计划步骤
            plan = []
            for line in plan_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # 移除编号和符号
                    step = line.lstrip('0123456789.- ').strip()
                    if step:
                        plan.append(step)

            if not plan:
                plan = ["Analyze the task and determine next steps"]

            return {
                "plan": plan,
                "current_step": current_step
            }
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "plan": ["Execute the user's request directly"],
                "current_step": current_step
            }

    return planner


def create_executor_node(llm, tools):
    """创建执行节点"""
    async def executor(state: DeepAgentState) -> Dict[str, Any]:
        from langchain.agents import create_tool_calling_agent, AgentExecutor

        messages = state["messages"]
        current_step = state.get("current_step", 0)

        # 创建工具调用代理
        prompt = f"""You are an execution agent. Use the available tools to complete the current task step.

Available tools: {', '.join([tool.name for tool in tools])}

Current task context: {messages[-1].content if messages else 'No context'}

Be precise and efficient. Use only the necessary tools."""

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=3
        )

        try:
            result = await agent_executor.ainvoke({
                "input": messages[-1].content if messages else "",
                "chat_history": messages[:-1] if len(messages) > 1 else []
            })

            output = result.get("output", "Task completed")

            return {
                "results": [result],
                "messages": messages + [AIMessage(content=output)],
                "current_step": current_step + 1
            }
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            return {
                "results": [{"error": error_msg}],
                "messages": messages + [AIMessage(content=error_msg)],
                "current_step": current_step + 1
            }

    return executor


def create_reflector_node(llm):
    """创建反思节点"""
    async def reflector(state: DeepAgentState) -> Dict[str, Any]:
        current_step = state.get("current_step", 0)
        results = state.get("results", [])
        messages = state.get("messages", [])

        # 检查最大迭代次数
        if current_step >= 10:
            return {
                "is_complete": True,
                "final_message": "Maximum iterations reached. Task may be incomplete.",
                "current_step": current_step
            }

        # 获取最后的结果
        last_result = results[-1] if results else {}
        last_message = messages[-1].content if messages else ""

        prompt = f"""Evaluate if the task has been completed successfully.

Task: {last_message}
Last Result: {str(last_result)}

Respond with only: 'COMPLETE' if done, or 'CONTINUE: [brief reason]' if more work needed."""

        try:
            response = await llm.ainvoke(prompt)
            response_text = response.content.strip()

            is_complete = response_text.upper().startswith("COMPLETE")

            return {
                "is_complete": is_complete,
                "final_message": response_text if is_complete else f"Continuing: {response_text}",
                "current_step": current_step
            }
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return {
                "is_complete": False,
                "final_message": f"Evaluation failed: {str(e)}. Continuing execution.",
                "current_step": current_step
            }

    return reflector


class AgentService:
    def __init__(self):
        self.session_service = SessionService()
        self.settings = get_settings()
        self._agents = {}  # 缓存已创建的agents

    def _create_deep_agent(self, sandbox: DockerSandbox, workspace_dir: str):
        """创建DeepAgent实例"""
        llm = create_llm()
        tools = create_sandbox_tools(sandbox)

        # 创建状态图
        graph = StateGraph(DeepAgentState)

        # 添加节点
        graph.add_node("planner", create_planner_node(llm))
        graph.add_node("executor", create_executor_node(llm, tools))
        graph.add_node("reflector", create_reflector_node(llm))

        # 添加边
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "reflector")

        # 条件边：根据反思结果决定是否继续
        def should_continue(state):
            if state.get("is_complete", False) or state.get("current_step", 0) >= 10:
                return END
            return "executor"

        graph.add_conditional_edges("reflector", should_continue)

        # 设置入口点
        graph.set_entry_point("planner")

        return graph.compile()

    async def create_session(self, user_id: str):
        """创建新的会话和沙盒"""
        # 创建沙盒
        sandbox = DockerSandbox.create()

        # 创建工作目录
        workspace_dir = tempfile.mkdtemp(prefix="manus_workspace_")

        # 创建DeepAgent
        agent = self._create_deep_agent(sandbox, workspace_dir)

        # 创建会话
        session = await self.session_service.create(user_id, sandbox)

        # 缓存agent和workspace
        self._agents[session.id] = {
            "agent": agent,
            "sandbox": sandbox,
            "workspace_dir": workspace_dir
        }

        return {
            "session_id": session.id,
            "sandbox_id": sandbox.id
        }

    async def chat(self, session_id: str, user_id: str, message: str) -> AsyncGenerator[dict, None]:
        """处理聊天消息"""
        session = await self.session_service.get(session_id, user_id)

        if not session:
            raise ValueError("Session not found")

        # 获取agent
        agent_data = self._agents.get(session_id)
        if not agent_data:
            raise ValueError("Agent not found for session")

        agent = agent_data["agent"]

        try:
            # 初始化状态
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_step": 0,
                "plan": [],
                "results": [],
                "is_complete": False,
                "final_message": None,
                "workspace_dir": agent_data["workspace_dir"]
            }

            # 执行agent
            async for event in agent.astream(initial_state):
                node_name = list(event.keys())[0]
                node_output = event.get(node_name, {})

                # 发送步骤事件
                if node_name == "planner":
                    plan = node_output.get("plan", [])
                    yield {
                        "event_type": "step",
                        "step": "planning",
                        "message": f"Created plan with {len(plan)} steps"
                    }
                elif node_name == "executor":
                    yield {
                        "event_type": "step",
                        "step": "executing",
                        "message": "Executing tools..."
                    }
                elif node_name == "reflector":
                    is_complete = node_output.get("is_complete", False)
                    yield {
                        "event_type": "step",
                        "step": "reflecting",
                        "message": "Evaluating progress..."
                    }

                    # 检查是否完成
                    if is_complete:
                        yield {
                            "event_type": "done",
                            "message": node_output.get("final_message", "Task completed")
                        }
                        break

                # 记录事件
                await self.session_service.add_event(session_id, {
                    "type": "step",
                    "step": node_name,
                    "message": str(node_output)
                })

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            yield {
                "event_type": "error",
                "message": f"Agent execution failed: {str(e)}"
            }

    async def stop_session(self, session_id: str, user_id: str):
        """停止会话"""
        session = await self.session_service.get(session_id, user_id)

        if not session:
            raise ValueError("Session not found")

        # 获取agent数据
        agent_data = self._agents.get(session_id)
        if agent_data:
            sandbox = agent_data["sandbox"]
            workspace_dir = agent_data["workspace_dir"]

            # 停止沙盒
            await sandbox.shutdown()

            # 清理工作目录
            try:
                import shutil
                shutil.rmtree(workspace_dir, ignore_errors=True)
            except:
                pass

            # 清理缓存
            del self._agents[session_id]

        await self.session_service.update_status(session_id, "stopped")

    async def close(self):
        """关闭服务"""
        # 停止所有agent和沙盒
        for session_id, agent_data in self._agents.items():
            try:
                sandbox = agent_data["sandbox"]
                workspace_dir = agent_data["workspace_dir"]

                await sandbox.shutdown()

                import shutil
                shutil.rmtree(workspace_dir, ignore_errors=True)
            except:
                pass

        self._agents.clear()
        await self.session_service.close()
