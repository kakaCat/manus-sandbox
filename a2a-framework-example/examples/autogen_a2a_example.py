"""
A2A Multi-Agent Example using Microsoft AutoGen

A2A (Agent-to-Agent) 多代理协作示例
使用 Microsoft AutoGen 框架实现

安装依赖:
    pip install autogen-agentchat autogen-ext openai

运行示例:
    python examples/autogen_a2a_example.py
"""

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

# AutoGen imports (ensure package is installed)
try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat, MagenticOneGroupChat
    from autogen_agentchat.tasks import ChatTask
    from autogen_agentchat import STATE_UPDATE, TEXT
    from autogen_agentchat.messages import AgentMessage
    from autogen_core.components import FunctionCall
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("Warning: AutoGen not installed. Run: pip install autogen-agentchat autogen-ext")


class AgentRole(str, Enum):
    """代理角色枚举"""
    RESEARCHER = "researcher"
    CODER = "coder"
    WRITER = "writer"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


@dataclass
class AgentInfo:
    """代理信息"""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[str]
    system_prompt: str
    model: str = "gpt-4"


class A2AMessage:
    """A2A协议消息"""
    
    def __init__(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict] = None
    ):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class BaseA2AAgent:
    """A2A代理基类"""
    
    def __init__(self, agent_info: AgentInfo):
        self.agent_id = agent_info.agent_id
        self.name = agent_info.name
        self.role = agent_info.role
        self.capabilities = agent_info.capabilities
        self.system_prompt = agent_info.system_prompt
        self.model = agent_info.model
        self.message_history: List[A2AMessage] = []
        self.status = "idle"
    
    async def send_message(self, receiver: str, content: str, 
                          message_type: str = "text") -> A2AMessage:
        """发送消息到其他代理"""
        message = A2AMessage(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type
        )
        self.message_history.append(message)
        self.status = "sending"
        return message
    
    async def receive_message(self, message: A2AMessage):
        """接收来自其他代理的消息"""
        self.message_history.append(message)
        self.status = "receiving"
    
    async def process_message(self, message: A2AMessage) -> str:
        """处理接收到的消息（子类实现）"""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """获取代理信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "status": self.status,
            "messages": len(self.message_history)
        }


class ResearchAgent(BaseA2AAgent):
    """研究代理 - 负责信息收集和分析"""
    
    def __init__(self, agent_id: str = "research_agent"):
        agent_info = AgentInfo(
            agent_id=agent_id,
            name="ResearchAgent",
            role=AgentRole.RESEARCHER,
            capabilities=["web_search", "data_analysis", "trend_analysis", "report_generation"],
            system_prompt="""你是一个专业的研究助手。你的职责是:
1. 收集和整理信息
2. 分析数据趋势
3. 生成研究报告
4. 提供客观的分析结果

请始终保持专业、严谨的态度。"""
        )
        super().__init__(agent_info)
    
    async def process_message(self, message: A2AMessage) -> str:
        """处理研究相关消息"""
        if "search" in message.content.lower():
            return await self._handle_search(message)
        elif "analyze" in message.content.lower():
            return await self._handle_analysis(message)
        elif "report" in message.content.lower():
            return await self._handle_report(message)
        else:
            return f"研究代理收到: {message.content[:100]}..."
    
    async def _handle_search(self, message: A2AMessage) -> str:
        """处理搜索请求"""
        # 模拟搜索结果
        return f"""搜索结果:
1. 主题: {message.content}
- 结果1: 相关文献A (相关性: 0.95)
- 结果2: 相关文献B (相关性: 0.87)
- 结果3: 相关文献C (相关性: 0.82)

共找到约50个相关结果。"""
    
    async def _handle_analysis(self, message: A2AMessage) -> str:
        """处理分析请求"""
        return f"""分析结果:
- 数据点: 100个样本
- 平均值: 75.5
- 标准差: 12.3
- 趋势: 上升 (+15%)

结论: 数据呈现明显上升趋势。"""
    
    async def _handle_report(self, message: A2AMessage) -> str:
        """处理报告生成请求"""
        return f"""研究报告: {message.content}

执行摘要:
本报告分析了{message.content}相关主题...

主要发现:
1. 发现了3个关键趋势
2. 识别了5个重要因素
3. 提供了4条建议

建议下一步行动:
- 深入研究趋势1
- 验证因素2的影响
- 实施建议3和4"""


class CodingAgent(BaseA2AAgent):
    """编码代理 - 负责代码编写和审查"""
    
    def __init__(self, agent_id: str = "coding_agent"):
        agent_info = AgentInfo(
            agent_id=agent_id,
            name="CodingAgent",
            role=AgentRole.CODER,
            capabilities=["code_generation", "code_review", "debugging", "refactoring"],
            system_prompt="""你是一个专业的编程助手。你的职责是:
1. 编写高质量代码
2. 代码审查和优化
3. 调试和修复问题
4. 重构遗留代码

请遵循最佳实践，编写清晰、可维护的代码。"""
        )
        super().__init__(agent_info)
    
    async def process_message(self, message: A2AMessage) -> str:
        """处理编码相关消息"""
        if "generate" in message.content.lower() or "write" in message.content.lower():
            return await self._handle_code_generation(message)
        elif "review" in message.content.lower():
            return await self._handle_code_review(message)
        elif "debug" in message.content.lower() or "fix" in message.content.lower():
            return await self._handle_debugging(message)
        else:
            return f"编码代理收到: {message.content[:100]}..."
    
    async def _handle_code_generation(self, message: A2AMessage) -> str:
        """处理代码生成请求"""
        return f"""```python
# {message.content}

def main():
    \"\"\"Main function\"\"\"
    print("Hello, World!")
    
    # TODO: 实现需求
    # {message.content}
    
    return True

if __name__ == "__main__":
    main()
```
代码已生成! 共15行。"""
    
    async def _handle_code_review(self, message: A2AMessage) -> str:
        """处理代码审查请求"""
        return """代码审查结果:
- 质量评分: 85/100
- 发现问题: 2个
  1. 缺少类型注解 (建议修复)
  2. 可以添加单元测试 (建议)
  
改进建议:
- 添加函数签名类型注解
- 扩展异常处理逻辑"""
    
    async def _handle_debugging(self, message: A2AMessage) -> str:
        """处理调试请求"""
        return f"""调试分析:
问题描述: {message.content}

诊断结果:
- 错误类型: RuntimeError
- 错误位置: 第23行
- 可能原因: 空值未检查

修复方案:
```python
if value is not None:
    # 处理逻辑
```
建议添加空值检查。"""


class WriterAgent(BaseA2AAgent):
    """写作代理 - 负责文档撰写"""
    
    def __init__(self, agent_id: str = "writer_agent"):
        agent_info = AgentInfo(
            agent_id=agent_id,
            name="WriterAgent",
            role=AgentRole.WRITER,
            capabilities=["technical_writing", "creative_writing", "editing", "summarization"],
            system_prompt="""你是一个专业的技术写手。你的职责是:
1. 撰写清晰的技术文档
2. 编辑和润色内容
3. 创作创意内容
4. 总结和提炼要点

请使用简洁、专业的语言。"""
        )
        super().__init__(agent_info)
    
    async def process_message(self, message: A2AMessage) -> str:
        """处理写作相关消息"""
        if "write" in message.content.lower() or "document" in message.content.lower():
            return await self._handle_writing(message)
        elif "edit" in message.content.lower():
            return await self._handle_editing(message)
        elif "summarize" in message.content.lower():
            return await self._handle_summarization(message)
        else:
            return f"写作代理收到: {message.content[:100]}..."
    
    async def _handle_writing(self, message: A2AMessage) -> str:
        """处理写作请求"""
        return f"""# {message.content}

## 概述

本文档提供了关于{message.content}的详细说明。

## 背景

随着技术的发展，{message.content}变得越来越重要。

## 详细说明

### 主要功能

1. 功能A - 描述
2. 功能B - 描述
3. 功能C - 描述

### 使用方法

```python
# 示例代码
result = do_something()
```

## 总结

本文档涵盖了{message.content}的核心内容。

---
文档已生成，共约500字。"""
    
    async def _handle_editing(self, message: A2AMessage) -> str:
        """处理编辑请求"""
        return """编辑结果:
- 改进: 3处
  1. 修正拼写错误
  2. 优化句子结构
  3. 添加标点符号
  
- 格式: 已调整
- 可读性: 已提升

建议: 文档质量良好，可以发布。"""
    
    async def _handle_summarization(self, message: A2AMessage) -> str:
        """处理摘要请求"""
        return f"""摘要:

原文: {message.content[:200]}...

要点提取:
1. 核心主题: 重要概念
2. 关键发现: 3个要点
3. 建议: 2条建议

字数压缩: 80% -> 20%

结论: 内容已提炼为核心要点。"""


class A2ACoordinator:
    """A2A协调器 - 负责协调多个代理"""
    
    def __init__(self):
        self.agents: Dict[str, BaseA2AAgent] = {}
        self.message_bus: List[A2AMessage] = []
        self.workflow_history: List[Dict] = []
    
    def register_agent(self, agent: BaseA2AAgent):
        """注册代理"""
        self.agents[agent.agent_id] = agent
        print(f"✓ 已注册代理: {agent.name} ({agent.role.value})")
    
    def get_registered_agents(self) -> List[Dict]:
        """获取所有已注册的代理"""
        return [agent.get_info() for agent in self.agents.values()]
    
    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        content: str,
        message_type: str = "text"
    ) -> A2AMessage:
        """发送消息（代理间通信）"""
        if receiver_id not in self.agents:
            raise ValueError(f"未知接收者: {receiver_id}")
        
        message = A2AMessage(
            sender=sender_id,
            receiver=receiver_id,
            content=content,
            message_type=message_type
        )
        
        # 发送消息
        await self.agents[receiver_id].receive_message(message)
        
        # 处理消息
        response = await self.agents[receiver_id].process_message(message)
        
        # 记录消息
        self.message_bus.append(message)
        
        return message
    
    async def broadcast_message(
        self,
        sender_id: str,
        content: str,
        exclude: Optional[List[str]] = None
    ) -> List[A2AMessage]:
        """广播消息到所有代理"""
        exclude = exclude or []
        messages = []
        
        for agent_id in self.agents:
            if agent_id not in exclude and agent_id != sender_id:
                msg = await self.send_message(sender_id, agent_id, content)
                messages.append(msg)
        
        return messages
    
    async def execute_workflow(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """执行工作流"""
        print(f"\n{'='*60}")
        print(f"执行工作流: {workflow_name}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        results = []
        
        for i, step in enumerate(steps):
            step_num = i + 1
            agent_id = step["agent"]
            task = step["task"]
            params = step.get("params", "")
            
            print(f"\n[Step {step_num}/{len(steps)}] {agent_id}: {task}")
            
            if agent_id not in self.agents:
                error_result = {
                    "step": step_num,
                    "agent": agent_id,
                    "status": "failed",
                    "error": f"Unknown agent: {agent_id}"
                }
                results.append(error_result)
                continue
            
            agent = self.agents[agent_id]
            
            # 构建消息内容
            content = f"{task}: {params}" if params else task
            
            # 发送任务消息
            await self.send_message("coordinator", agent_id, content)
            
            # 模拟处理时间
            import asyncio
            await asyncio.sleep(0.3)
            
            # 获取最新消息的处理结果
            if agent.message_history:
                last_msg = agent.message_history[-1]
                response = await agent.process_message(last_msg)
                
                result = {
                    "step": step_num,
                    "agent": agent_id,
                    "agent_name": agent.name,
                    "task": task,
                    "status": "completed",
                    "response": response[:200] + "..." if len(response) > 200 else response,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "step": step_num,
                    "agent": agent_id,
                    "agent_name": agent.name,
                    "task": task,
                    "status": "completed",
                    "response": "任务完成",
                    "timestamp": datetime.now().isoformat()
                }
            
            results.append(result)
            print(f"  ✓ {agent.name} 完成 {task}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        all_completed = all(r.get("status") == "completed" for r in results)
        summary = {
            "workflow_name": workflow_name,
            "status": "completed" if all_completed else "partial",
            "total_steps": len(steps),
            "completed_steps": sum(1 for r in results if r.get("status") == "completed"),
            "failed_steps": sum(1 for r in results if r.get("status") == "failed"),
            "duration_seconds": duration,
            "results": results,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        self.workflow_history.append(summary)
        
        print(f"\n{'='*60}")
        print(f"工作流完成: {workflow_name}")
        print(f"耗时: {duration:.2f}秒")
        print(f"步骤: {summary['completed_steps']}/{summary['total_steps']}")
        print(f"{'='*60}\n")
        
        return summary


# ============ 示例演示 ============

async def demo_basic_a2a_communication():
    """演示A2A基本通信"""
    print("\n" + "="*60)
    print("Demo 1: A2A Basic Communication")
    print("="*60)
    
    coordinator = A2ACoordinator()
    
    # 创建代理
    research_agent = ResearchAgent()
    coding_agent = CodingAgent()
    
    # 注册代理
    coordinator.register_agent(research_agent)
    coordinator.register_agent(coding_agent)
    
    # 代理间通信
    await coordinator.send_message(
        sender_id="research_agent",
        receiver_id="coding_agent",
        content="请根据以下研究结果生成代码: 用户登录系统需要支持OAuth2认证"
    )
    
    print("\n✓ A2A通信演示完成\n")


async def demo_single_agent_task():
    """演示单个代理任务执行"""
    print("\n" + "="*60)
    print("Demo 2: Single Agent Task")
    print("="*60)
    
    research_agent = ResearchAgent()
    
    # 执行研究任务
    result = await research_agent.process_message(
        A2AMessage(
            sender="user",
            receiver="research_agent",
            content="分析AI发展趋势，生成报告"
        )
    )
    
    print(f"研究结果:\n{result[:300]}...")
    print("\n✓ 单代理任务演示完成\n")


async def demo_multi_agent_workflow():
    """演示多代理协作工作流"""
    print("\n" + "="*60)
    print("Demo 3: Multi-Agent Workflow")
    print("="*60)
    
    coordinator = A2ACoordinator()
    
    # 创建和注册代理
    research_agent = ResearchAgent()
    coding_agent = CodingAgent()
    writer_agent = WriterAgent()
    
    coordinator.register_agent(research_agent)
    coordinator.register_agent(coding_agent)
    coordinator.register_agent(writer_agent)
    
    print(f"\n已注册 {len(coordinator.agents)} 个代理")
    
    # 定义工作流
    workflow = [
        {
            "agent": "research_agent",
            "task": "research",
            "params": "AI Agent框架的最新发展趋势"
        },
        {
            "agent": "coding_agent",
            "task": "generate",
            "params": "创建一个简单的AI Agent管理系统"
        },
        {
            "agent": "writer_agent",
            "task": "write",
            "params": "AI Agent管理系统 - 技术文档"
        }
    ]
    
    # 执行工作流
    result = await coordinator.execute_workflow(
        workflow_name="AI系统开发工作流",
        steps=workflow
    )
    
    print(f"工作流结果:")
    print(f"  状态: {result['status']}")
    print(f"  完成: {result['completed_steps']}/{result['total_steps']}")
    print(f"  耗时: {result['duration_seconds']:.2f}秒")
    
    print("\n✓ 多代理工作流演示完成\n")


async def demo_complex_workflow():
    """演示复杂工作流"""
    print("\n" + "="*60)
    print("Demo 4: Complex Workflow with All Agents")
    print("="*60)
    
    coordinator = A2ACoordinator()
    
    # 注册所有代理
    research_agent = ResearchAgent("senior_researcher")
    coding_agent = CodingAgent("senior_coder")
    writer_agent = WriterAgent("tech_writer")
    reviewer = ResearchAgent("peer_reviewer")
    reviewer.role = AgentRole.REVIEWER
    
    coordinator.register_agent(research_agent)
    coordinator.register_agent(coding_agent)
    coordinator.register_agent(writer_agent)
    coordinator.register_agent(reviewer)
    
    # 复杂工作流
    workflow = [
        {
            "agent": "senior_researcher",
            "task": "research",
            "params": "微服务架构的最佳实践"
        },
        {
            "agent": "senior_researcher",
            "task": "analyze",
            "params": "收集的性能数据"
        },
        {
            "agent": "senior_coder",
            "task": "generate",
            "params": "微服务API网关服务"
        },
        {
            "agent": "senior_coder",
            "task": "review",
            "params": "用户认证服务的代码"
        },
        {
            "agent": "peer_reviewer",
            "task": "analyze",
            "params": "代码审查结果"
        },
        {
            "agent": "tech_writer",
            "task": "write",
            "params": "微服务架构设计文档"
        },
        {
            "agent": "tech_writer",
            "task": "summarize",
            "params": "整个项目文档"
        }
    ]
    
    result = await coordinator.execute_workflow(
        workflow_name="微服务项目完整流程",
        steps=workflow
    )
    
    print(f"\n工作流统计:")
    print(f"  总步骤: {result['total_steps']}")
    print(f"  完成: {result['completed_steps']}")
    print(f"  失败: {result['failed_steps']}")
    print(f"  耗时: {result['duration_seconds']:.2f}秒")
    
    print("\n✓ 复杂工作流演示完成\n")


async def demo_parallel_agents():
    """演示并行代理任务"""
    print("\n" + "="*60)
    print("Demo 5: Parallel Agent Tasks")
    print("="*60)
    
    coordinator = A2ACoordinator()
    
    # 创建多个相同类型的代理
    research_agents = [
        ResearchAgent(f"researcher_{i}") for i in range(3)
    ]
    
    for agent in research_agents:
        coordinator.register_agent(agent)
    
    print(f"\n已注册 {len(coordinator.agents)} 个研究代理")
    
    # 并行任务
    import asyncio
    
    tasks = [
        coordinator.send_message(
            sender_id="coordinator",
            receiver_id=agent.agent_id,
            content="分析市场趋势"
        )
        for agent in research_agents
    ]
    
    print("\n并行执行3个研究任务...")
    await asyncio.gather(*tasks)
    
    print(f"所有代理收到消息")
    
    for agent in research_agents:
        print(f"  - {agent.name}: {len(agent.message_history)} 条消息")
    
    print("\n✓ 并行任务演示完成\n")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("A2A Multi-Agent Framework Demo")
    print("Using Microsoft AutoGen Pattern")
    print("="*60)
    
    # 运行演示
    await demo_basic_a2a_communication()
    await demo_single_agent_task()
    await demo_multi_agent_workflow()
    await demo_complex_workflow()
    await demo_parallel_agents()
    
    print("="*60)
    print("All Demos Completed!")
    print("="*60)
    print("\nFeatures Demonstrated:")
    print("  ✓ A2A Message Passing")
    print("  ✓ Agent Registration & Discovery")
    print("  ✓ Single Agent Task Execution")
    print("  ✓ Multi-Agent Collaboration")
    print("  ✓ Complex Workflow Orchestration")
    print("  ✓ Parallel Task Execution")
    print()


if __name__ == "__main__":
    asyncio.run(main())
