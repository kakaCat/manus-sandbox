# Manus AI Agent - LangChain + LangGraph 重构版

基于 **LangChain + LangGraph + DeepAgent** 架构重新实现的 AI Manus 后端服务。

## 架构设计

### 核心技术栈

- **LangChain**: LLM 调用和工具集成框架
- **LangGraph**: 状态图工作流引擎 (Plan → Execute → Reflect)
- **DeepAgent**: 智能体框架，管理工具和沙盒
- **FastAPI**: 异步 Web 框架
- **MongoDB**: 会话持久化
- **Redis**: 缓存和会话管理
- **Docker**: 沙盒容器管理

### 架构图

```
┌─────────────┐
│   User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  FastAPI (Routes)     │
│  ──────────────────   │
│  Session Management    │
│  SSE Events           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────┐
│  AgentService         │
│  ──────────────────   │
│  LangGraph Workflow   │
│  ──────────────────   │
│  ├─ Planner Node     │
│  ├─ Executor Node    │
│  └─ Reflector Node  │
└──────┬──────────────┘
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ Browser  │      │  Shell   │      │   File   │
│  Tool    │      │  Tool    │      │   Tool   │
└──────────┘      └──────────┘      └──────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Docker Sandbox │
                  │  (8080 API)  │
                  └───────────────┘
```

### LangGraph 工作流

```python
用户输入
    ↓
[Planner Node]
  - 分析任务
  - 生成执行计划
    ↓
[Executor Node]
  - LangChain Agent 执行
  - 调用工具
  - 返回结果
    ↓
[Reflector Node]
  - 评估结果
  - 决定继续或结束
    ↓
   循环直到完成
```

## 项目结构

```
backend-new/
├── app/
│   ├── core/                      # 核心配置
│   │   └── config.py
│   │
│   ├── domain/                    # 领域层
│   │   ├── agents/               # DeepAgent 实现
│   │   │   ├── base.py
│   │   │   └── deep_agent.py
│   │   ├── tools/                # LangChain 工具
│   │   │   ├── base.py
│   │   │   ├── browser.py
│   │   │   ├── shell.py
│   │   │   ├── file.py
│   │   │   └── search.py
│   │   ├── graph/                # LangGraph 工作流
│   │   │   ├── state.py
│   │   │   ├── nodes.py
│   │   │   └── edges.py
│   │   └── models/               # 领域模型
│   │       ├── session.py
│   │       └── memory.py
│   │
│   ├── infrastructure/            # 基础设施
│   │   ├── sandbox/              # Docker 沙盒
│   │   │   └── docker_sandbox.py
│   │   ├── storage/              # MongoDB/Redis
│   │   │   ├── mongodb.py
│   │   │   └── redis.py
│   │   └── llm/                 # LangChain LLM
│   │       └── langchain_llm.py
│   │
│   ├── application/               # 应用服务
│   │   ├── session_service.py
│   │   └── agent_service.py
│   │
│   ├── interfaces/                # 接口层
│   │   ├── api/
│   │   │   └── routes.py
│   │   └── schemas/
│   │       └── session.py
│   │
│   └── main.py                   # FastAPI 入口
│
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## 快速开始

### 1. 环境配置

```bash
cd backend-new
cp .env.example .env
vim .env  # 修改配置
```

### 2. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Docker 部署

```bash
# 构建镜像
docker build -t manus-backend-new .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  -v /var/run/docker.sock:/var/run/docker.sock \
  manus-backend-new
```

### 4. Docker Compose 部署

```yaml
services:
  backend:
    build: ./backend-new
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE=${OPENAI_API_BASE}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7.0

  sandbox:
    image: simpleyyt/manus-sandbox
    command: /bin/sh -c "exit 0"
    network_mode: bridge

volumes:
  mongodb_data:

networks:
  default:
    name: manus-network
```

## API 接口

### 创建会话

```http
PUT /api/v1/sessions
```

响应:
```json
{
  "session_id": "uuid",
  "sandbox_id": "sandbox-container-id"
}
```

### 对话 (SSE 流)

```http
POST /api/v1/sessions/{session_id}/chat
Content-Type: application/json

{
  "message": "帮我搜索最新的 AI 论文"
}
```

响应事件流:
```
data: {"event_type":"step","step":"planner","message":"..."}
data: {"event_type":"step","step":"executor","message":"..."}
data: {"event_type":"done","message":"任务完成"}
```

### 获取会话列表

```http
GET /api/v1/sessions
```

### 停止会话

```http
POST /api/v1/sessions/{session_id}/stop
```

## 核心实现

### 1. LangGraph 工作流

```python
# domain/graph/nodes.py

def create_planner_node(llm, sandbox):
    async def planner(state):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Break down user's task into steps"),
            ("user", "{input}")
        ])

        response = await llm.ainvoke(prompt.format_messages(...))

        return {"plan": response.content.split('\n')}
    return planner


def create_executor_node(llm, sandbox, tools):
    async def executor(state):
        agent = create_tool_calling_agent(llm, tools)
        agent_executor = AgentExecutor(agent=agent, tools=tools)

        result = await agent_executor.ainvoke({"input": state["messages"][-1].content})

        return {"results": [result]}
    return executor


def create_reflector_node(llm, sandbox):
    async def reflector(state):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Evaluate if task is complete"),
            ("user", "Results: {results}")
        ])

        response = await llm.ainvoke(...)

        is_complete = "complete" in response.content.lower()

        return {"is_complete": is_complete, "current_step": state["current_step"] + 1}
    return reflector
```

### 2. DeepAgent 执行

```python
# domain/agents/deep_agent.py

class DeepAgent:
    def _build_graph(self, llm, sandbox):
        graph = StateGraph(AgentState)

        graph.add_node("planner", planner)
        graph.add_node("executor", executor)
        graph.add_node("reflector", reflector)

        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "reflector")

        graph.add_conditional_edges(
            "reflector",
            reflect_to_end,
            {"continue": "executor", "end": END}
        )

        return graph.compile()

    async def execute(self, llm, sandbox, request):
        graph = self._build_graph(llm, sandbox)

        initial_state = {
            "messages": [HumanMessage(content=request)],
            "current_step": 0,
            "plan": [],
            "results": [],
            "is_complete": False
        }

        async for event in graph.astream(initial_state):
            node_name = list(event.keys())[0]
            yield {"type": "step", "step": node_name, "output": event[node_name]}

            if "is_complete" in event[node_name] and event[node_name]["is_complete"]:
                yield {"type": "done"}
                break
```

### 3. LangChain 工具

```python
# domain/tools/browser.py

class BrowserTool(BaseTool):
    name = "browser_navigate"
    description = "Navigate browser to a specific URL"

    def __init__(self, sandbox):
        super().__init__(name=self.name, description=self.description, args_schema=NavigateInput)
        self.sandbox = sandbox

    async def _arun(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.sandbox.base_url}/browser/navigate",
                json={"url": url},
                timeout=30.0
            )

            result = response.json()
            return result.get('data', {}).get('content', '')
```

## 工具系统

### 可用工具

- **browser_navigate**: 导航浏览器到指定 URL
- **browser_view**: 查看当前浏览器页面内容
- **shell_execute**: 在沙盒中执行 Shell 命令
- **file_read**: 读取沙盒中的文件
- **file_write**: 写入文件到沙盒
- **web_search**: Web 搜索 (Bing/Google/Baidu)

### 添加新工具

```python
# domain/tools/my_tool.py

class MyTool(BaseTool):
    name = "my_tool"
    description = "My custom tool description"

    def __init__(self, sandbox):
        super().__init__(name=self.name, description=self.description, args_schema=MyInput)
        self.sandbox = sandbox

    async def _arun(self, **kwargs) -> str:
        # 实现工具逻辑
        return "Tool result"

# 在 agent_service.py 中注册
tools = [
    # ... 其他工具
    MyTool(sandbox)
]
```

## 与原版对比

| 特性 | 原版 ai-manus | 重构版 (LangChain + LangGraph) |
|------|----------------|------------------------------|
| LLM 集成 | 原生 OpenAI SDK | LangChain ChatOpenAI |
| 工作流引擎 | 自定义 PlanAct Agent | LangGraph 状态图 |
| 工具系统 | 自定义 BaseTool | LangChain BaseTool |
| 沙盒管理 | DockerSandbox | 保持一致 |
| 状态管理 | Memory 类 | LangGraph State |
| 工作流 | 单一循环 | Planner → Executor → Reflector |
| 可扩展性 | 中等 | 高 (LangGraph 生态) |

## 优势

1. **标准化**: 使用业界标准的 LangChain 生态
2. **可视化**: LangGraph 提供工作流可视化
3. **可扩展**: 轻松集成 LangChain 生态的 100+ 工具
4. **可调试**: LangGraph 支持检查点和状态回溯
5. **模块化**: Planner/Executor/Reflector 清晰分离

## 开发计划

- [x] 基础架构设计
- [x] LangGraph 工作流实现
- [x] 工具系统集成
- [ ] 浏览器工具完善 (Playwright)
- [ ] Shell 工具完善 (会话管理)
- [ ] 文件工具完善 (支持二进制)
- [ ] 测试覆盖
- [ ] 性能优化
- [ ] 监控和日志

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT License
