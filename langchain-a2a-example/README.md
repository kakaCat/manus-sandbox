# LangChain + Google A2A SDK A2A 通信示例

基于 Google A2A SDK 和 LangChain 实现的 Agent-to-Agent (A2A) 通信示例。

## 特性

- **A2A 协议兼容**: 使用 Google 官方 A2A SDK 实现标准协议
- **LangChain 集成**: 利用 LangChain 的工具和代理生态系统
- **多代理协作**: 支持多个 LangChain 代理间的通信
- **异步架构**: 基于 FastAPI 的异步 HTTP 服务
- **可扩展设计**: 易于添加新的代理类型和工具

## 架构概述

```
┌─────────────────┐    A2A Protocol    ┌─────────────────┐
│   LangChain     │◄─────────────────►│   LangChain     │
│   Agent A       │   (JSON-RPC over   │   Agent B       │
│                 │    HTTP/WebSocket) │                 │
│ - LLM           │                    │ - LLM           │
│ - Tools         │                    │ - Tools         │
│ - Memory        │                    │ - Memory        │
└─────────────────┘                    └─────────────────┘
        ▲                                     ▲
        │                                     │
        └───────────── A2A Server ────────────┘
                      (FastAPI + A2A SDK)
```

## 安装依赖

```bash
cd langchain-a2a-example
pip install -r requirements.txt
```

## 项目结构

```
langchain-a2a-example/
├── examples/
│   └── langchain_a2a_demo.py    # 完整示例
├── README.md                    # 本文档
└── requirements.txt             # 依赖列表
```

## 快速开始

1. 设置环境变量：

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

2. 运行示例：

```bash
cd langchain-a2a-example
python examples/langchain_a2a_demo.py
```

## 核心组件

### A2ALangChainAgent

基于 LangChain 代理的 A2A 代理包装器：

```python
class A2ALangChainAgent:
    def __init__(self, agent_name: str, langchain_agent):
        self.agent_name = agent_name
        self.langchain_agent = langchain_agent
        self.a2a_client = A2AClient()

    async def send_message(self, target_agent: str, message: str):
        # 通过 A2A 协议发送消息
        return await self.a2a_client.send_message(target_agent, message)

    async def handle_a2a_message(self, message: A2AMessage):
        # 处理接收到的 A2A 消息
        response = await self.langchain_agent.ainvoke(message.content)
        return response
```

### A2ACommunicationLayer

A2A 通信层，处理协议细节：

```python
class A2ACommunicationLayer:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.a2a_server = A2AServer()

    async def start_server(self):
        # 启动 A2A 服务器
        await self.a2a_server.start()

    async def register_agent(self, agent: A2ALangChainAgent):
        # 注册代理到 A2A 网络
        await self.a2a_server.register_agent(agent)
```

### LangChainA2ABridge

LangChain 和 A2A 的桥梁：

```python
class LangChainA2ABridge:
    def __init__(self):
        self.agents = {}
        self.communication_layer = A2ACommunicationLayer()

    def add_langchain_agent(self, name: str, agent):
        # 添加 LangChain 代理
        a2a_agent = A2ALangChainAgent(name, agent)
        self.agents[name] = a2a_agent

    async def start_communication(self):
        # 启动 A2A 通信
        await self.communication_layer.start_server()
        for agent in self.agents.values():
            await self.communication_layer.register_agent(agent)
```

## 示例输出

```
============================================================
LangChain A2A Communication Demo
============================================================
✓ 已注册代理: research_agent (LangChain)
✓ 已注册代理: coding_agent (LangChain)
✓ A2A 服务器启动: http://localhost:8000

执行工作流: AI系统开发工作流
============================================================
[Step 1/3] research_agent → coding_agent
  Message: "设计一个用户管理系统"
  Response: "我来帮你设计用户管理系统..."

[Step 2/3] coding_agent → research_agent
  Message: "需要添加哪些安全功能？"
  Response: "建议添加JWT认证、密码加密..."

[Step 3/3] research_agent → coding_agent
  Message: "实现JWT认证"
  Response: "开始实现JWT认证功能..."

工作流完成: AI系统开发工作流
耗时: 2.45秒
消息数: 6
```

## 扩展使用

### 添加新的 LangChain 代理

```python
from langchain.agents import create_react_agent
from langchain.tools import Tool

# 创建工具
def search_web(query: str) -> str:
    return f"搜索结果: {query}"

tools = [
    Tool(name="web_search", func=search_web, description="网络搜索工具")
]

# 创建 LangChain 代理
llm = ChatOpenAI(temperature=0.7)
agent = create_react_agent(llm, tools, prompt)

# 添加到 A2A 网络
bridge = LangChainA2ABridge()
bridge.add_langchain_agent("web_agent", agent)
```

### 自定义消息处理

```python
class CustomA2ALangChainAgent(A2ALangChainAgent):
    async def handle_a2a_message(self, message: A2AMessage):
        # 自定义消息预处理
        enhanced_message = self.preprocess_message(message)

        # 调用 LangChain 代理
        response = await self.langchain_agent.ainvoke(enhanced_message)

        # 自定义响应后处理
        final_response = self.postprocess_response(response)

        return final_response
```

## 优势对比

| 特性 | 本示例 | Microsoft AutoGen | 纯 LangChain |
|------|--------|------------------|-------------|
| A2A 协议 | ✅ 官方 Google SDK | ❌ 不支持 | ❌ 不支持 |
| 多代理通信 | ✅ 标准协议 | ✅ 自定义协议 | ❌ 有限支持 |
| 生态集成 | ✅ LangChain + A2A | ❌ 单框架 | ✅ 丰富工具 |
| 生产就绪 | ✅ 企业级 | ⚠️ 实验性 | ✅ 成熟 |
| 可扩展性 | ✅ 模块化 | ✅ 插件化 | ✅ 组件化 |

## 许可证

MIT