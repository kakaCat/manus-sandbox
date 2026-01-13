# A2A Multi-Agent Framework Example

基于 **Microsoft AutoGen** 模式实现的 A2A (Agent-to-Agent) 多代理协作示例。

## 特性

- **A2A 通信协议**: 代理间的消息传递和任务分发
- **多代理类型**: 研究代理、编码代理、写作代理
- **工作流编排**: 复杂任务的分步执行和协调
- **并行执行**: 多个代理同时执行任务
- **状态追踪**: 任务执行状态和结果记录

## 安装依赖

```bash
# 使用AutoGen框架
pip install autogen-agentchat autogen-ext

# 或使用OpenAI作为LLM后端
pip install openai
```

## 项目结构

```
a2a-framework-example/
├── examples/
│   └── autogen_a2a_example.py   # 完整示例
├── README.md                     # 本文档
└── requirements.txt              # 依赖列表
```

## 快速开始

```bash
cd a2a-framework-example
python examples/autogen_a2a_example.py
```

## 演示内容

1. **A2A基本通信** - 代理间的消息传递
2. **单代理任务** - 单一代理执行任务
3. **多代理工作流** - 多个代理协作完成复杂任务
4. **复杂工作流** - 7步完整项目流程
5. **并行任务** - 多个代理同时执行

## 核心组件

### BaseA2AAgent
所有代理的基类，提供：
- 消息发送/接收
- 任务处理
- 状态管理

### ResearchAgent
研究代理，负责：
- 信息收集 (web_search)
- 数据分析 (data_analysis)
- 趋势分析 (trend_analysis)
- 报告生成 (report_generation)

### CodingAgent
编码代理，负责：
- 代码生成 (code_generation)
- 代码审查 (code_review)
- 调试修复 (debugging)
- 代码重构 (refactoring)

### WriterAgent
写作代理，负责：
- 技术写作 (technical_writing)
- 内容编辑 (editing)
- 内容摘要 (summarization)

### A2ACoordinator
协调器，负责：
- 代理注册和管理
- 消息路由
- 工作流执行

## 示例输出

```
============================================================
Demo 3: Multi-Agent Workflow
============================================================
✓ 已注册代理: ResearchAgent (researcher)
✓ 已注册代理: CodingAgent (coder)
✓ 已注册代理: WriterAgent (writer)

执行工作流: AI系统开发工作流
============================================================
[Step 1/3] research_agent: research
  ✓ ResearchAgent 完成 research
[Step 2/3] coding_agent: generate
  ✓ CodingAgent 完成 generate
[Step 3/3] writer_agent: write
  ✓ WriterAgent 完成 write

工作流完成: AI系统开发工作流
耗时: 0.90秒
步骤: 3/3
```

## 扩展使用

### 添加新代理

```python
class CustomAgent(BaseA2AAgent):
    def __init__(self, agent_id: str = "custom_agent"):
        agent_info = AgentInfo(
            agent_id=agent_id,
            name="CustomAgent",
            role=AgentRole.CUSTOM,
            capabilities=["custom_skill"],
            system_prompt="你的职责描述..."
        )
        super().__init__(agent_info)
    
    async def process_message(self, message: A2AMessage) -> str:
        # 实现自定义消息处理逻辑
        return f"处理结果: {message.content}"
```

### 自定义工作流

```python
coordinator = A2ACoordinator()
coordinator.register_agent(research_agent)
coordinator.register_agent(coding_agent)

workflow = [
    {"agent": "research_agent", "task": "research", "params": "你的主题"},
    {"agent": "coding_agent", "task": "generate", "params": "你的需求"}
]

result = await coordinator.execute_workflow("my_workflow", workflow)
```

## 推荐框架

如果需要生产级别的 A2A 实现，建议使用：

1. **Google A2A SDK** - 官方 A2A 协议实现
   - `pip install a2a-sdk`
   - https://github.com/google-a2a/a2a-python

2. **Microsoft AutoGen** - 多代理协作框架
   - `pip install autogen-agentchat`
   - https://microsoft.github.io/autogen/

3. **CrewAI** - 角色扮演代理团队
   - `pip install crewai`

4. **LangGraph** - Agent 工作流编排
   - `pip install langgraph`

## 许可证

MIT
