# A2A Protocol Example
## Agent-to-Agent Communication Framework

基于JSON-RPC 2.0的代理间通信协议实现

## 功能特性

- **A2A协议核心**: 完整的消息传递、任务分发、事件处理机制
- **多种代理类型**: 研究代理、编码代理、写作代理
- **代理通信**: 支持同步/异步消息传递
- **工作流编排**: 复杂任务的分解和协调执行
- **并行执行**: 支持任务并行处理
- **依赖管理**: 支持任务间的依赖关系

## 目录结构

```
a2a-example/
├── protocols/           # A2A协议核心
│   └── a2a_protocol.py  # 消息、任务、事件定义
├── agents/              # 代理实现
│   ├── base_agent.py    # 代理基类
│   └── agent_implementations.py  # 具体代理实现
├── services/            # 服务组件
│   ├── agent_communicator.py  # 代理通信器
│   └── agent_coordinator.py   # 任务协调器
├── examples/            # 示例程序
│   └── a2a_example.py   # 完整演示
└── README.md            # 本文件
```

## 快速开始

```bash
# 运行示例
python examples/a2a_example.py
```

## 示例演示

1. **基本消息传递**: 代理间的消息发送和接收
2. **单代理任务执行**: 创建和执行任务
3. **多代理协作**: 多个代理协同完成复杂任务
4. **并行任务执行**: 同时执行多个任务
5. **复杂工作流**: 研究 → 开发 → 文档的完整流程

## 核心组件

### A2AMessage
```python
message = A2AMessage(
    message_type=MessageType.REQUEST,
    sender_agent="agent_1",
    receiver_agent="agent_2",
    payload={"method": "web_search", "params": {...}}
)
```

### A2ATask
```python
task = A2ATask(
    task_type="web_search",
    input_data={"query": "AI trends", "max_results": 10},
    priority=5
)
```

### 代理通信
```python
communicator = AgentCommunicator("my_agent")
await communicator.send_message(
    receiver_agent="research_agent",
    method="web_search",
    params={"query": "test"}
)
```

### 工作流执行
```python
coordinator = AgentCoordinator()
coordinator.register_agent("researcher", research_agent)

result = await coordinator.execute_workflow(
    workflow_id="my_workflow",
    workflow_config={
        "steps": [
            {"agent": "researcher", "task_type": "web_search", "params": {...}}
        ]
    }
)
```

## 依赖

- Python 3.7+
- asyncio
- 无外部依赖

## 许可证

MIT
