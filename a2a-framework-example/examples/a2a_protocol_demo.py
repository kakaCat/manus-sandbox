"""
真正的 Google A2A Protocol 实现

遵循官方 A2A 协议规范:
- AgentCard: 代理能力描述
- Task: 任务生命周期 (submitted → working → completed/failed)
- Message: 消息格式 (role, content, type)
- Streaming: SSE 流式传输

A2A Protocol 官方文档: https://a2a-protocol.org
GitHub: https://github.com/google-a2a/a2a-python

安装官方SDK:
    pip install a2a-sdk

本实现是A2A协议的简化版，遵循同样的协议规范。
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional
from abc import ABC, abstractmethod


class TaskStatus(str, Enum):
    """A2A协议定义的任务状态"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class MessageRole(str, Enum):
    """A2A协议定义的消息角色"""
    AGENT = "agent"
    USER = "user"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"


class MessageType(str, Enum):
    """A2A协议定义的消息类型"""
    TEXT = "text"
    IMAGE = "image"
    DATA = "data"
    AUDIO = "audio"


# ============ A2A协议核心数据结构 ============

@dataclass
class AgentSkill:
    """代理技能描述"""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentCard:
    """
    A2A协议核心 - AgentCard
    
    描述代理的能力、URL、认证方式等信息。
    代理发现时，其他代理通过AgentCard了解其能力。
    
    Example:
        agent_card = AgentCard(
            agent_id="research_agent",
            name="Research Agent",
            url="http://localhost:8000",
            version="1.0.0",
            skills=[
                AgentSkill(id="web_search", name="Web Search", description="Search the web")
            ],
            capabilities=["streaming", "pushNotifications"]
        )
    """
    agent_id: str
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    skills: List[AgentSkill] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    authentication: Optional[Dict] = None
    default_input_modes: List[str] = field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text"])
    
    def to_dict(self) -> Dict:
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "skills": [s.to_dict() for s in self.skills],
            "capabilities": self.capabilities,
            "authentication": self.authentication,
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentCard':
        return cls(
            agent_id=data["agentId"],
            name=data["name"],
            description=data["description"],
            url=data["url"],
            version=data.get("version", "1.0.0"),
            skills=[AgentSkill(**s) for s in data.get("skills", [])],
            capabilities=data.get("capabilities", []),
            authentication=data.get("authentication"),
            default_input_modes=data.get("defaultInputModes", ["text"]),
            default_output_modes=data.get("defaultOutputModes", ["text"])
        )


@dataclass
class TextContent:
    """文本消息内容"""
    type: str = "text"
    text: str = ""
    
    def to_dict(self) -> Dict:
        return {"type": self.type, "text": self.text}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TextContent':
        return cls(type=data.get("type", "text"), text=data.get("text", ""))


@dataclass
class Message:
    """
    A2A协议核心 - Message
    
    代理间传递的消息，包含角色、内容和类型。
    
    Example:
        message = Message(
            role=MessageRole.AGENT,
            content=TextContent(text="Here are the search results..."),
            type=MessageType.TEXT
        )
    """
    role: MessageRole
    content: Dict  # 可以是TextContent或其他结构
    type: MessageType = MessageType.TEXT
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role.value,
            "content": self.content if isinstance(self.content, dict) else self.content.to_dict(),
            "type": self.type.value,
            "messageId": self.message_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            type=MessageType(data.get("type", "text")),
            message_id=data.get("messageId", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )


@dataclass
class Task:
    """
    A2A协议核心 - Task
    
    任务对象，代理间通信的基本单元。
    状态生命周期: submitted → working → completed/failed
    
    Example:
        task = Task(
            id="task_123",
            session_id="session_456",
            status=TaskStatus.SUBMITTED,
            messages=[Message(...)],
            input={"query": "AI trends"}
        )
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    status: TaskStatus = TaskStatus.SUBMITTED
    status_message: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    input: Optional[Dict] = None
    output: Optional[Dict] = None
    metadata: Optional[Dict] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "status": self.status.value,
            "statusMessage": self.status_message,
            "messages": [m.to_dict() for m in self.messages],
            "input": self.input,
            "output": self.output,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            session_id=data.get("sessionId"),
            status=TaskStatus(data.get("status", "submitted")),
            status_message=data.get("statusMessage"),
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            input=data.get("input"),
            output=data.get("output"),
            metadata=data.get("metadata"),
            created_at=data.get("createdAt", datetime.now().isoformat()),
            updated_at=data.get("updatedAt", datetime.now().isoformat())
        )
    
    def update_status(self, status: TaskStatus, message: Optional[str] = None):
        """更新任务状态"""
        self.status = status
        self.status_message = message
        self.updated_at = datetime.now().isoformat()


# ============ A2A协议接口定义 ============

class A2AProtocolHandler(ABC):
    """A2A协议处理器抽象基类"""
    
    @abstractmethod
    async def on_task(self, task: Task) -> AsyncGenerator[Dict, None]:
        """
        处理任务 - 遵循A2A协议
        
        当收到任务请求时调用，返回流式更新
        """
        pass
    
    @abstractmethod
    async def get_agent_card(self) -> AgentCard:
        """获取AgentCard"""
        pass


class A2AClient:
    """
    A2A协议客户端
    
    用于向其他A2A代理发送任务和接收结果。
    
    Example:
        client = A2AClient("http://research-agent:8000")
        async for update in client.send_task(Task(input={"query": "AI"})):
            print(update)
    """
    
    def __init__(self, agent_url: str, api_key: Optional[str] = None):
        self.agent_url = agent_url.rstrip('/')
        self.api_key = api_key
    
    async def send_task(self, task: Task) -> Task:
        """
        发送任务到A2A代理（同步方式）
        
        Args:
            task: 任务对象
            
        Returns:
            完成的Task对象
        """
        # 模拟发送到代理并接收响应
        # 实际实现中这里会是 HTTP POST 请求
        task.update_status(TaskStatus.WORKING, "Task is being processed")
        
        # 模拟任务处理
        await asyncio.sleep(0.5)
        
        # 添加系统消息
        task.messages.append(Message(
            role=MessageRole.AGENT,
            content={"type": "text", "text": f"Task {task.id} received and processing..."},
            type=MessageType.TEXT
        ))
        
        task.update_status(TaskStatus.COMPLETED, "Task completed successfully")
        task.output = {"result": f"Processed task {task.id}"}
        
        return task
    
    async def send_task_streaming(self, task: Task) -> AsyncGenerator[Dict, None]:
        """
        发送任务并接收流式更新（遵循A2A协议）
        
        Yields:
            任务状态和消息更新
        """
        # 发送任务
        yield {"type": "status", "status": TaskStatus.WORKING.value, "taskId": task.id}
        
        # 模拟流式处理
        for i in range(3):
            await asyncio.sleep(0.3)
            yield {
                "type": "message",
                "message": {
                    "role": "agent",
                    "content": {"type": "text", "text": f"Processing step {i+1}..."}
                },
                "taskId": task.id
            }
        
        # 完成
        yield {"type": "status", "status": TaskStatus.COMPLETED.value, "taskId": task.id}
        yield {"type": "output", "output": {"result": f"Task {task.id} completed"}, "taskId": task.id}


class A2AServer:
    """
    A2A协议服务器
    
    实现A2A协议的服务器端，处理来自其他代理的任务请求。
    
    Example:
        server = A2AServer(agent_card=my_agent_card)
        server.register_handler(my_handler)
        await server.start(port=8000)
    """
    
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self.handlers: Dict[str, A2AProtocolHandler] = {}
        self.tasks: Dict[str, Task] = {}
    
    def register_handler(self, handler: A2AProtocolHandler):
        """注册任务处理器"""
        self.handlers[handler.__class__.__name__] = handler
    
    async def get_agent_card(self) -> Dict:
        """返回AgentCard（代理发现）"""
        return self.agent_card.to_dict()
    
    async def create_task(self, task_input: Dict, session_id: Optional[str] = None) -> Task:
        """创建新任务"""
        task = Task(
            session_id=session_id,
            status=TaskStatus.SUBMITTED,
            input=task_input
        )
        self.tasks[task.id] = task
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)


# ============ A2A协议示例实现 ============

class ResearchAgentHandler(A2AProtocolHandler):
    """研究代理处理器 - 遵循A2A协议"""
    
    def __init__(self):
        self.agent_card = AgentCard(
            agent_id="research_agent",
            name="Research Agent",
            description="专业研究助手，负责信息收集和分析",
            url="http://localhost:8001",
            version="1.0.0",
            skills=[
                AgentSkill(id="web_search", name="Web Search", description="搜索网络信息"),
                AgentSkill(id="data_analysis", name="Data Analysis", description="数据分析"),
                AgentSkill(id="report_generation", name="Report Generation", description="生成研究报告")
            ],
            capabilities=["streaming"]
        )
    
    async def get_agent_card(self) -> AgentCard:
        return self.agent_card
    
    async def on_task(self, task: Task) -> AsyncGenerator[Dict, None]:
        """处理研究任务"""
        query = task.input.get("query", "")
        
        yield {"type": "status", "status": "working", "taskId": task.id}
        
        # 模拟搜索
        await asyncio.sleep(0.3)
        yield {
            "type": "message",
            "message": {
                "role": "agent",
                "content": {"type": "text", "text": f"Searching for: {query}"}
            },
            "taskId": task.id
        }
        
        # 分析
        await asyncio.sleep(0.3)
        yield {
            "type": "message", 
            "message": {
                "role": "agent",
                "content": {"type": "text", "text": "Analyzing results..."}
            },
            "taskId": task.id
        }
        
        # 完成
        yield {
            "type": "output",
            "output": {
                "results": [
                    {"title": "Result 1", "url": "https://example.com/1"},
                    {"title": "Result 2", "url": "https://example.com/2"}
                ],
                "summary": f"Found 10 results for: {query}"
            },
            "taskId": task.id
        }
        yield {"type": "status", "status": "completed", "taskId": task.id}


class CodingAgentHandler(A2AProtocolHandler):
    """编码代理处理器 - 遵循A2A协议"""
    
    def __init__(self):
        self.agent_card = AgentCard(
            agent_id="coding_agent",
            name="Coding Agent",
            description="专业编程助手，负责代码生成和审查",
            url="http://localhost:8002",
            version="1.0.0",
            skills=[
                AgentSkill(id="code_generation", name="Code Generation", description="生成代码"),
                AgentSkill(id="code_review", name="Code Review", description="代码审查")
            ],
            capabilities=["streaming"]
        )
    
    async def get_agent_card(self) -> AgentCard:
        return self.agent_card
    
    async def on_task(self, task: Task) -> AsyncGenerator[Dict, None]:
        """处理编码任务"""
        language = task.input.get("language", "python")
        requirements = task.input.get("requirements", "")
        
        yield {"type": "status", "status": "working", "taskId": task.id}
        
        await asyncio.sleep(0.4)
        yield {
            "type": "message",
            "message": {
                "role": "agent",
                "content": {"type": "text", "text": f"Generating {language} code..."}
            },
            "taskId": task.id
        }
        
        code = f'''"""
{requirements}
"""

def main():
    print("Hello, World!")
    return True
'''
        
        yield {
            "type": "output",
            "output": {
                "language": language,
                "code": code,
                "lines": len(code.split('\n'))
            },
            "taskId": task.id
        }
        yield {"type": "status", "status": "completed", "taskId": task.id}


# ============ A2A协议演示 ============

async def demo_agent_discovery():
    """演示A2A代理发现"""
    print("\n" + "="*60)
    print("A2A Demo 1: Agent Discovery (AgentCard)")
    print("="*60)
    
    # 创建研究代理
    research_handler = ResearchAgentHandler()
    agent_card = await research_handler.get_agent_card()
    
    print(f"\nAgent Card (代理能力描述):")
    print(f"  Agent ID: {agent_card.agent_id}")
    print(f"  Name: {agent_card.name}")
    print(f"  Description: {agent_card.description}")
    print(f"  URL: {agent_card.url}")
    print(f"\nSkills (代理技能):")
    for skill in agent_card.skills:
        print(f"  - {skill.name}: {skill.description}")
    print(f"\nCapabilities: {agent_card.capabilities}")
    
    print("\n✓ Agent Discovery 演示完成\n")


async def demo_task_lifecycle():
    """演示A2A任务生命周期"""
    print("\n" + "="*60)
    print("A2A Demo 2: Task Lifecycle")
    print("="*60)
    
    # 创建任务
    task = Task(
        input={"query": "A2A Protocol latest developments"},
        session_id="session_001"
    )
    
    print(f"\nTask Created:")
    print(f"  Task ID: {task.id}")
    print(f"  Status: {task.status.value}")
    print(f"  Created At: {task.created_at}")
    
    # 模拟任务状态变化
    task.update_status(TaskStatus.WORKING, "Processing...")
    print(f"\nStatus Updated: {task.status.value}")
    
    # 添加消息
    task.messages.append(Message(
        role=MessageRole.AGENT,
        content={"type": "text", "text": "Task started"},
        type=MessageType.TEXT
    ))
    print(f"\nMessages: {len(task.messages)}")
    
    # 完成
    task.update_status(TaskStatus.COMPLETED, "Done")
    task.output = {"result": "Analysis complete"}
    print(f"\nStatus Updated: {task.status.value}")
    print(f"Output: {task.output}")
    
    print("\n✓ Task Lifecycle 演示完成\n")


async def demo_a2a_communication():
    """演示A2A代理间通信"""
    print("\n" + "="*60)
    print("A2A Demo 3: Agent-to-Agent Communication")
    print("="*60)
    
    # 创建服务器和客户端
    research_server = A2AServer(AgentCard(
        agent_id="research_agent",
        name="Research Agent",
        description="Research service",
        url="http://localhost:8001"
    ))
    research_handler = ResearchAgentHandler()
    research_server.register_handler(research_handler)
    
    coding_server = A2AServer(AgentCard(
        agent_id="coding_agent",
        name="Coding Agent", 
        description="Coding service",
        url="http://localhost:8002"
    ))
    coding_handler = CodingAgentHandler()
    coding_server.register_handler(coding_handler)
    
    # 创建客户端
    client = A2AClient("http://localhost:8001")
    
    # 发送任务给研究代理
    print("\n1. Client → Research Agent: Send Task")
    task = await client.send_task(Task(
        input={"query": "AI agent frameworks comparison"}
    ))
    
    print(f"   Task ID: {task.id}")
    print(f"   Status: {task.status.value}")
    print(f"   Messages: {len(task.messages)}")
    print(f"   Output: {task.output}")
    
    # 发送任务给编码代理
    print("\n2. Client → Coding Agent: Send Task")
    client2 = A2AClient("http://localhost:8002")
    task2 = await client2.send_task(Task(
        input={"language": "python", "requirements": "REST API"}
    ))
    
    print(f"   Task ID: {task2.id}")
    print(f"   Status: {task2.status.value}")
    print(f"   Output: {task2.output}")
    
    print("\n✓ A2A Communication 演示完成\n")


async def demo_streaming():
    """演示A2A流式传输"""
    print("\n" + "="*60)
    print("A2A Demo 4: Streaming Updates (SSE)")
    print("="*60)
    
    client = A2AClient("http://localhost:8001")
    task = Task(id="stream_task_001", input={"query": "test"})
    
    print("\nStreaming Updates:")
    async for update in client.send_task_streaming(task):
        print(f"  [{update['type']}] {update}")
    
    print("\n✓ Streaming 演示完成\n")


async def demo_workflow():
    """演示A2A工作流"""
    print("\n" + "="*60)
    print("A2A Demo 5: Multi-Agent Workflow")
    print("="*60)
    
    # 创建协调器
    coordinator = A2ACoordinatorA2A()
    
    # 创建代理
    research = A2AServer(AgentCard(
        agent_id="researcher",
        name="Researcher",
        description="Research agent",
        url="http://research:8000"
    ))
    coder = A2AServer(AgentCard(
        agent_id="coder",
        name="Coder",
        description="Coding agent",
        url="http://coder:8000"
    ))
    
    coordinator.register_agent(research)
    coordinator.register_agent(coder)
    
    # 执行工作流
    print("\nExecuting workflow:")
    print("  Step 1: Research → Analyze topic")
    print("  Step 2: Coder → Generate code")
    
    result = await coordinator.execute_workflow([
        {"agent": "researcher", "input": {"query": "web framework trends"}},
        {"agent": "coder", "input": {"language": "python", "requirements": "web framework"}}
    ])
    
    print(f"\nWorkflow Result:")
    print(f"  Status: {result['status']}")
    print(f"  Steps: {result['completed']}/{result['total']}")
    
    print("\n✓ Workflow 演示完成\n")


class A2ACoordinatorA2A:
    """A2A协议协调器"""
    
    def __init__(self):
        self.agents: Dict[str, A2AServer] = {}
    
    def register_agent(self, server: A2AServer):
        self.agents[server.agent_card.agent_id] = server
    
    async def execute_workflow(self, steps: List[Dict]) -> Dict:
        """执行A2A工作流"""
        completed = 0
        
        for i, step in enumerate(steps):
            agent_id = step["agent"]
            print(f"  Step {i+1}: {agent_id} → {step.get('input', {})}")
            
            if agent_id in self.agents:
                client = A2AClient(self.agents[agent_id].agent_card.url)
                task = await client.send_task(Task(input=step.get("input")))
                if task.status == TaskStatus.COMPLETED:
                    completed += 1
        
        return {
            "status": "completed" if completed == len(steps) else "partial",
            "total": len(steps),
            "completed": completed
        }


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("A2A Protocol Implementation Demo")
    print("Google Agent-to-Agent Protocol")
    print("="*60)
    
    await demo_agent_discovery()
    await demo_task_lifecycle()
    await demo_a2a_communication()
    await demo_streaming()
    await demo_workflow()
    
    print("="*60)
    print("All A2A Protocol Demos Completed!")
    print("="*60)
    print("\nA2A Protocol Components Demonstrated:")
    print("  ✓ AgentCard (代理能力描述)")
    print("  ✓ Task (任务生命周期: submitted→working→completed)")
    print("  ✓ Message (消息格式)")
    print("  ✓ Streaming (SSE流式传输)")
    print("  ✓ Agent Discovery (代理发现)")
    print("  ✓ Multi-Agent Workflow (工作流)")
    print()


if __name__ == "__main__":
    asyncio.run(main())
