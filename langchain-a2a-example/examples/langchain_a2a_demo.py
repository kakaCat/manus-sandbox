"""
LangChain + Google A2A SDK A2A 通信示例

使用 Google A2A SDK 和 LangChain 实现的多代理协作示例。
演示了如何让多个 LangChain 代理通过 A2A 协议进行通信。

安装依赖:
    pip install -r requirements.txt

运行示例:
    python examples/langchain_a2a_demo.py
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# A2A SDK imports
from a2a import A2AClient, A2AServer
from a2a.types import (
    AgentCard, AgentSkill, Message, MessageSendParams,
    AgentCapabilities, DataPart, A2AMessage
)

# LangChain imports
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# FastAPI for server
from fastapi import FastAPI
import uvicorn


@dataclass
class A2AConfig:
    """A2A 配置"""
    server_url: str = "http://localhost:8000"
    agent_timeout: int = 30
    max_message_length: int = 10000


class A2ALangChainAgent:
    """
    基于 LangChain 的 A2A 代理包装器

    将 LangChain 代理包装为 A2A 协议兼容的代理
    """

    def __init__(
        self,
        agent_name: str,
        langchain_agent: AgentExecutor,
        a2a_config: A2AConfig = None
    ):
        self.agent_name = agent_name
        self.langchain_agent = langchain_agent
        self.a2a_config = a2a_config or A2AConfig()
        self.a2a_client = A2AClient()
        self.message_history: List[Dict] = []
        self.connected_agents: List[str] = []

    async def initialize_a2a_card(self) -> AgentCard:
        """初始化 A2A 代理卡片"""
        return AgentCard(
            name=self.agent_name,
            description=f"LangChain-powered A2A agent: {self.agent_name}",
            url=f"{self.a2a_config.server_url}/agents/{self.agent_name}",
            capabilities=AgentCapabilities(
                streaming=True,
                push_notifications=False
            ),
            skills=[
                AgentSkill(
                    id=f"{self.agent_name}_research",
                    name="Research & Analysis",
                    description="Conduct research, analyze information, and provide insights using web search and data analysis tools",
                    input_modes=["text"],
                    output_modes=["text"],
                    examples=[
                        "Research the latest trends in AI",
                        "Analyze market data for investment opportunities"
                    ]
                ),
                AgentSkill(
                    id=f"{self.agent_name}_code_generation",
                    name="Code Generation & Review",
                    description="Generate code, review implementations, and provide technical solutions",
                    input_modes=["text"],
                    output_modes=["text"],
                    examples=[
                        "Implement a user authentication system",
                        "Review code for security vulnerabilities"
                    ]
                ),
                AgentSkill(
                    id=f"{self.agent_name}_writing",
                    name="Technical Writing",
                    description="Create documentation, write technical content, and generate reports",
                    input_modes=["text"],
                    output_modes=["text"],
                    examples=[
                        "Write API documentation",
                        "Create technical specifications"
                    ]
                )
            ]
        )

    async def send_message(
        self,
        target_agent: str,
        content: str,
        message_type: str = "chat"
    ) -> Dict[str, Any]:
        """
        通过 A2A 协议发送消息

        Args:
            target_agent: 目标代理名称
            content: 消息内容
            message_type: 消息类型 (chat/task)

        Returns:
            发送结果
        """
        try:
            # 创建消息
            message = Message(
                message_id=f"msg_{datetime.now().timestamp()}",
                task_id=f"task_{datetime.now().timestamp()}",
                role="user",
                parts=[
                    DataPart(
                        kind="text",
                        data=content
                    )
                ]
            )

            # 发送参数
            params = MessageSendParams(
                message=message,
                configuration={
                    "blocking": True,
                    "accepted_output_modes": ["text"]
                }
            )

            # 记录发送历史
            self.message_history.append({
                "timestamp": datetime.now(),
                "direction": "outgoing",
                "target": target_agent,
                "content": content,
                "type": message_type
            })

            # 发送消息 (这里是模拟，实际需要连接到 A2A 网络)
            print(f"📤 [{self.agent_name}] → [{target_agent}]: {content[:50]}...")

            # 模拟响应
            response = await self._simulate_a2a_response(target_agent, content)

            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now()
            }

        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }

    async def handle_incoming_message(self, message: A2AMessage) -> str:
        """
        处理接收到的 A2A 消息

        Args:
            message: A2A 消息对象

        Returns:
            响应内容
        """
        try:
            # 提取消息内容
            content = ""
            if message.parts:
                for part in message.parts:
                    if hasattr(part, 'data') and part.kind == "text":
                        content += part.data

            # 记录接收历史
            self.message_history.append({
                "timestamp": datetime.now(),
                "direction": "incoming",
                "sender": getattr(message, 'sender', 'unknown'),
                "content": content,
                "type": "message"
            })

            print(f"📥 [{self.agent_name}] 收到消息: {content[:50]}...")

            # 使用 LangChain 代理处理消息
            response = await self.langchain_agent.ainvoke({"input": content})

            # 提取响应内容
            response_text = response.get("output", str(response))

            # 记录响应历史
            self.message_history.append({
                "timestamp": datetime.now(),
                "direction": "outgoing",
                "target": getattr(message, 'sender', 'unknown'),
                "content": response_text,
                "type": "response"
            })

            return response_text

        except Exception as e:
            error_msg = f"处理消息时出错: {e}"
            print(f"❌ {error_msg}")
            return error_msg

    async def _simulate_a2a_response(self, target_agent: str, content: str) -> str:
        """
        模拟 A2A 响应 (在实际实现中会连接到真正的 A2A 网络)
        """
        # 这里是模拟实现，实际应该通过 A2A 协议调用目标代理
        await asyncio.sleep(0.5)  # 模拟网络延迟

        return f"来自 {target_agent} 的响应: 已收到消息 '{content[:30]}...'"

    def get_message_history(self) -> List[Dict]:
        """获取消息历史"""
        return self.message_history.copy()

    def get_connected_agents(self) -> List[str]:
        """获取已连接的代理列表"""
        return self.connected_agents.copy()


class A2ACommunicationLayer:
    """
    A2A 通信层

    处理 A2A 协议的底层通信细节
    """

    def __init__(self, config: A2AConfig = None):
        self.config = config or A2AConfig()
        self.a2a_server = A2AServer()
        self.registered_agents: Dict[str, A2ALangChainAgent] = {}
        self.app = FastAPI(title="LangChain A2A Server")

        # 设置路由
        self._setup_routes()

    def _setup_routes(self):
        """设置 API 路由"""

        @self.app.get("/")
        async def root():
            return {"message": "LangChain A2A Server", "agents": list(self.registered_agents.keys())}

        @self.app.get("/agents")
        async def list_agents():
            return {
                "agents": [
                    {
                        "name": name,
                        "status": "active",
                        "message_count": len(agent.get_message_history())
                    }
                    for name, agent in self.registered_agents.items()
                ]
            }

        @self.app.get("/agents/{agent_name}/history")
        async def get_agent_history(agent_name: str):
            if agent_name not in self.registered_agents:
                return {"error": "Agent not found"}, 404

            return {
                "agent": agent_name,
                "history": self.registered_agents[agent_name].get_message_history()
            }

    async def register_agent(self, agent: A2ALangChainAgent):
        """
        注册代理到 A2A 网络

        Args:
            agent: 要注册的 A2A LangChain 代理
        """
        try:
            # 初始化代理卡片
            agent_card = await agent.initialize_a2a_card()

            # 注册到服务器
            self.registered_agents[agent.agent_name] = agent

            print(f"✅ 已注册代理: {agent.agent_name}")

        except Exception as e:
            print(f"❌ 注册代理失败 {agent.agent_name}: {e}")
            raise

    async def start_server(self, host: str = "localhost", port: int = 8000):
        """
        启动 A2A 服务器

        Args:
            host: 服务器主机
            port: 服务器端口
        """
        print(f"🚀 启动 A2A 服务器: http://{host}:{port}")
        print(f"📋 已注册代理: {list(self.registered_agents.keys())}")

        # 在后台启动服务器
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)

        # 启动服务器 (非阻塞)
        import threading
        def run_server():
            asyncio.run(server.serve())

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # 等待服务器启动
        await asyncio.sleep(1)

    async def stop_server(self):
        """停止 A2A 服务器"""
        print("🛑 停止 A2A 服务器")
        # 这里可以添加清理逻辑


class LangChainA2ABridge:
    """
    LangChain 和 A2A 的桥梁

    提供高层 API 来管理 LangChain 代理和 A2A 通信
    """

    def __init__(self, config: A2AConfig = None):
        self.config = config or A2AConfig()
        self.agents: Dict[str, A2ALangChainAgent] = {}
        self.communication_layer = A2ACommunicationLayer(self.config)
        self.workflows: Dict[str, Dict] = {}

    def add_langchain_agent(
        self,
        name: str,
        langchain_agent: AgentExecutor,
        description: str = ""
    ):
        """
        添加 LangChain 代理到 A2A 网络

        Args:
            name: 代理名称
            langchain_agent: LangChain AgentExecutor 实例
            description: 代理描述
        """
        if name in self.agents:
            raise ValueError(f"代理 '{name}' 已存在")

        a2a_agent = A2ALangChainAgent(name, langchain_agent, self.config)
        self.agents[name] = a2a_agent

        print(f"➕ 添加代理: {name}")

    def create_workflow(self, name: str, steps: List[Dict[str, Any]]):
        """
        创建多代理工作流

        Args:
            name: 工作流名称
            steps: 工作流步骤列表
                  [{"from": "agent1", "to": "agent2", "message": "任务内容"}]
        """
        self.workflows[name] = {
            "name": name,
            "steps": steps,
            "created_at": datetime.now()
        }
        print(f"📋 创建工作流: {name} ({len(steps)} 步骤)")

    async def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        执行多代理工作流

        Args:
            workflow_name: 工作流名称

        Returns:
            执行结果
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"工作流 '{workflow_name}' 不存在")

        workflow = self.workflows[workflow_name]
        print(f"\n{'='*60}")
        print(f"执行工作流: {workflow_name}")
        print(f"{'='*60}")

        start_time = datetime.now()
        results = []
        message_count = 0

        for i, step in enumerate(workflow["steps"], 1):
            from_agent = step["from"]
            to_agent = step["to"]
            message = step["message"]

            if from_agent not in self.agents or to_agent not in self.agents:
                raise ValueError(f"代理不存在: {from_agent} 或 {to_agent}")

            print(f"[Step {i}/{len(workflow['steps'])}] {from_agent} → {to_agent}")

            # 发送消息
            result = await self.agents[from_agent].send_message(to_agent, message)
            results.append({
                "step": i,
                "from": from_agent,
                "to": to_agent,
                "message": message,
                "result": result
            })

            message_count += 1

            if result["success"]:
                print(f"  ✓ {from_agent} 完成发送")
            else:
                print(f"  ❌ {from_agent} 发送失败: {result.get('error', 'Unknown error')}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "workflow": workflow_name,
            "duration": duration,
            "steps_completed": len(results),
            "messages_sent": message_count,
            "success_rate": sum(1 for r in results if r["result"]["success"]) / len(results),
            "results": results
        }

        print(f"\n工作流完成: {workflow_name}")
        print(f"耗时: {duration:.2f}秒")
        print(f"步骤: {len(results)}/{len(workflow['steps'])}")
        print(f"消息数: {message_count}")

        return summary

    async def start_a2a_network(self):
        """启动 A2A 网络"""
        print(f"🌐 启动 A2A 网络...")

        # 注册所有代理
        for agent in self.agents.values():
            await self.communication_layer.register_agent(agent)

        # 启动通信层
        await self.communication_layer.start_server()

        print(f"✅ A2A 网络启动完成")
        print(f"📡 代理数量: {len(self.agents)}")
        print(f"🔗 服务器地址: {self.config.server_url}")

    async def get_network_status(self) -> Dict[str, Any]:
        """获取网络状态"""
        return {
            "server_url": self.config.server_url,
            "agent_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "workflows": list(self.workflows.keys()),
            "total_messages": sum(
                len(agent.get_message_history())
                for agent in self.agents.values()
            )
        }


# 示例工具函数
def web_search(query: str) -> str:
    """模拟网络搜索工具"""
    return f"搜索结果 for '{query}': 找到相关信息..."

def code_analysis(code: str) -> str:
    """模拟代码分析工具"""
    return f"代码分析结果: {code[:50]}... 代码质量良好。"

def documentation_writer(topic: str) -> str:
    """模拟文档编写工具"""
    return f"为 '{topic}' 生成的技术文档内容..."


def create_research_agent() -> AgentExecutor:
    """创建研究代理"""
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    tools = [
        Tool(
            name="web_search",
            func=web_search,
            description="用于搜索网络信息和最新研究成果"
        )
    ]

    prompt = PromptTemplate.from_template("""
    你是一个专业的研究代理，擅长信息收集和分析。

    你的任务是:
    1. 使用 web_search 工具收集相关信息
    2. 分析和总结发现
    3. 提供有价值的见解

    当前任务: {input}

    思考过程:
    {agent_scratchpad}

    最终回答:
    """)

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=ConversationBufferMemory(),
        verbose=True
    )


def create_coding_agent() -> AgentExecutor:
    """创建编码代理"""
    llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

    tools = [
        Tool(
            name="code_analysis",
            func=code_analysis,
            description="用于分析代码质量和提供改进建议"
        )
    ]

    prompt = PromptTemplate.from_template("""
    你是一个专业的编码代理，擅长软件开发和代码实现。

    你的任务是:
    1. 理解需求并设计解决方案
    2. 使用 code_analysis 工具检查代码质量
    3. 提供高质量的代码实现

    当前任务: {input}

    思考过程:
    {agent_scratchpad}

    最终回答:
    """)

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=ConversationBufferMemory(),
        verbose=True
    )


def create_writer_agent() -> AgentExecutor:
    """创建写作代理"""
    llm = ChatOpenAI(temperature=0.8, model="gpt-3.5-turbo")

    tools = [
        Tool(
            name="documentation_writer",
            func=documentation_writer,
            description="用于生成技术文档和说明"
        )
    ]

    prompt = PromptTemplate.from_template("""
    你是一个专业的写作代理，擅长技术文档编写和内容创作。

    你的任务是:
    1. 理解主题并组织内容结构
    2. 使用 documentation_writer 工具生成文档
    3. 确保内容清晰、专业、有用

    当前任务: {input}

    思考过程:
    {agent_scratchpad}

    最终回答:
    """)

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=ConversationBufferMemory(),
        verbose=True
    )


async def main():
    """主函数 - 演示 LangChain A2A 通信"""
    print("=" * 60)
    print("LangChain A2A Communication Demo")
    print("=" * 60)

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return

    try:
        # 创建 A2A 桥梁
        bridge = LangChainA2ABridge()

        # 创建并添加 LangChain 代理
        print("\n🤖 创建代理...")

        research_agent = create_research_agent()
        bridge.add_langchain_agent("research_agent", research_agent)

        coding_agent = create_coding_agent()
        bridge.add_langchain_agent("coding_agent", coding_agent)

        writer_agent = create_writer_agent()
        bridge.add_langchain_agent("writer_agent", writer_agent)

        # 创建示例工作流
        workflow_steps = [
            {
                "from": "research_agent",
                "to": "coding_agent",
                "message": "研究并设计一个现代化的用户管理系统，包括用户注册、登录、权限管理等功能"
            },
            {
                "from": "coding_agent",
                "to": "research_agent",
                "message": "我已经完成了用户管理系统的初步设计，请帮我分析一下安全性和性能方面的考虑"
            },
            {
                "from": "research_agent",
                "to": "writer_agent",
                "message": "基于刚才的设计，为用户管理系统编写详细的技术文档，包括API接口、数据库设计和部署指南"
            }
        ]

        bridge.create_workflow("user_management_workflow", workflow_steps)

        # 启动 A2A 网络
        print("\n🌐 启动 A2A 网络...")
        await bridge.start_a2a_network()

        # 等待一下让服务器完全启动
        await asyncio.sleep(2)

        # 执行工作流
        print("\n⚡ 执行多代理协作工作流...")
        result = await bridge.execute_workflow("user_management_workflow")

        # 显示最终状态
        print(f"\n{'='*60}")
        print("演示完成")
        print(f"{'='*60}")

        status = await bridge.get_network_status()
        print(f"📊 网络状态:")
        print(f"   代理数量: {status['agent_count']}")
        print(f"   总消息数: {status['total_messages']}")
        print(f"   成功率: {result['success_rate']:.1%}")
        print(f"   执行时间: {result['duration']:.2f}秒")

        # 保持服务器运行一段时间用于测试
        print(f"\n🔄 服务器运行中，可通过以下地址访问:")
        print(f"   http://localhost:8000/agents - 查看代理列表")
        print(f"   http://localhost:8000/agents/research_agent/history - 查看消息历史")

        # 运行 30 秒后自动停止
        await asyncio.sleep(30)

    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🛑 清理资源...")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())