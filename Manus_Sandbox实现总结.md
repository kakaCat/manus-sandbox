# Manus Sandbox 实现总结

基于知乎文章：《我也复刻了一个 Manus，带高仿 WebUI 和沙盒》

项目地址：https://github.com/Simpleyyt/ai-manus

---

## 一、整体架构设计

### 系统组成

Manus 系统由三个核心模块组成：

1. **Web（前端）** - 用户交互界面
2. **Server（后端）** - 核心业务逻辑和 Agent 调度
3. **Sandbox（沙盒）** - 隔离的执行环境

### 工作流程

```
用户发起对话
    ↓
Web → Server: 创建 Agent 请求
    ↓
Server → Docker: 通过 /var/run/docker.sock 创建 Sandbox 容器
    ↓
返回会话 ID 给 Web
    ↓
Web → Server: 发送用户消息（带会话 ID）
    ↓
Server → PlanAct Agent: 处理消息
    ↓
Agent → Sandbox Tools: 调用工具（Browser/Shell/File/Python等）
    ↓
Server → Web: 通过 SSE 实时返回事件流
```

---

## 二、Sandbox 沙盒实现方案

### 2.1 核心技术栈

- **容器技术**: Docker
- **基础镜像**: Ubuntu
- **浏览器**: Chrome（Chromium）
- **虚拟显示**: Xvfb（X Virtual Framebuffer）
- **远程访问**:
  - **CDP**: Chrome DevTools Protocol（端口 9222）
  - **VNC**: x11vnc（图形界面访问）

### 2.2 Sandbox 容器特性

每个 Sandbox 是一个独立的 Docker 容器，包含：

1. **Ubuntu 环境** - 完整的 Linux 系统
2. **Chrome 浏览器** - 用于网页操作
3. **工具 API 服务**:
   - File API - 文件操作
   - Shell API - 命令行执行
   - Python API - Python 代码执行
   - Node API - Node.js 代码执行
4. **网络隔离** - 独立的 Docker 网络
5. **生命周期管理** - TTL 自动回收

---

## 三、Docker Compose 配置

### 3.1 完整配置示例

```yaml
services:
  # 前端服务
  frontend:
    image: simpleyyt/manus-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - manus-network
    environment:
      - BACKEND_URL=http://backend:8000

  # 后端服务
  backend:
    image: simpleyyt/manus-backend
    depends_on:
      - sandbox
    restart: unless-stopped
    volumes:
      # 关键：挂载 Docker socket，用于创建和管理 Sandbox 容器
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - manus-network
    environment:
      # OpenAI API 配置
      - API_KEY=your_api_key
      - API_BASE=https://api.openai.com/v1
      - MODEL_NAME=gpt-4
      - TEMPERATURE=0.7
      - MAX_TOKENS=2000

      # Sandbox 配置
      - SANDBOX_IMAGE=simpleyyt/manus-sandbox
      - SANDBOX_NAME_PREFIX=sandbox
      - SANDBOX_TTL_MINUTES=30
      - SANDBOX_NETWORK=manus-network
      - SANDBOX_CHROME_ARGS=
      - SANDBOX_HTTPS_PROXY=
      - SANDBOX_HTTP_PROXY=
      - SANDBOX_NO_PROXY=

      # 可选：Google 搜索
      - GOOGLE_SEARCH_API_KEY=
      - GOOGLE_SEARCH_ENGINE_ID=

      # 日志级别
      - LOG_LEVEL=INFO

  # Sandbox 镜像预拉取（不直接运行）
  sandbox:
    image: simpleyyt/manus-sandbox
    command: /bin/sh -c "exit 0"  # 防止启动，仅用于预拉取镜像
    restart: "no"
    networks:
      - manus-network

networks:
  manus-network:
    name: manus-network
```

### 3.2 关键配置说明

#### Backend 挂载 Docker Socket
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```
- 允许 Backend 容器与宿主机 Docker 通信
- `:ro` 表示只读权限，提升安全性
- 用于动态创建和销毁 Sandbox 容器

#### Sandbox 环境变量

| 变量 | 作用 | 默认值 |
|------|------|--------|
| `SANDBOX_IMAGE` | 沙盒 Docker 镜像 | simpleyyt/manus-sandbox |
| `SANDBOX_NAME_PREFIX` | 容器名称前缀 | sandbox |
| `SANDBOX_TTL_MINUTES` | 容器存活时间（分钟） | 30 |
| `SANDBOX_NETWORK` | Docker 网络 | manus-network |
| `SANDBOX_CHROME_ARGS` | Chrome 启动参数 | - |
| `SANDBOX_*_PROXY` | 代理配置 | - |

---

## 四、Sandbox 内部实现

### 4.1 Chrome 浏览器 CDP 访问

**Chrome DevTools Protocol (CDP)** 是 Chrome 提供的调试协议。

#### 启动 Chrome 并开启 CDP

```bash
# 在 Sandbox 容器内启动 Chrome
google-chrome \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --remote-debugging-port=8222 \
  --remote-debugging-address=127.0.0.1
```

#### 使用 socat 转发端口

由于 Chrome 只监听 `127.0.0.1:8222`，需要转发到 `0.0.0.0:9222` 以便外部访问：

```bash
socat TCP-LISTEN:9222,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:8222
```

- `TCP-LISTEN:9222` - 监听 9222 端口
- `bind=0.0.0.0` - 绑定所有网卡
- `fork` - 为每个连接创建子进程
- `reuseaddr` - 允许端口复用
- `TCP:127.0.0.1:8222` - 转发到本地 8222

### 4.2 VNC 图形界面访问

由于 Docker 镜像内**没有 X Server** 等图形环境，通过以下方案提供 VNC 访问：

#### 启动虚拟 X11 显示服务器

```bash
# 启动 Xvfb 在 Display :1
Xvfb :1 -screen 0 1280x1029x24
```

- `Xvfb` - X Virtual Framebuffer，虚拟显示服务器
- `:1` - Display 编号
- `-screen 0 1280x1029x24` - 屏幕分辨率和色深

#### Chrome 指定 Display

```bash
# Chrome 浏览器指定 Display :1
google-chrome \
  --display=:1 \
  --headless \
  --remote-debugging-port=8222
```

#### 启动 VNC Server

```bash
# 使用 x11vnc 提供 VNC Server
x11vnc -display :1 -forever -shared
```

- `-display :1` - 连接到 Xvfb 的 Display
- `-forever` - 持续运行
- `-shared` - 允许多个客户端连接

---

## 五、AI Agent 设计模式

### 5.1 AI Agent 公式

```
AI Agent = LLM + Planning + Memory + Tools
```

### 5.2 Tool Use 方案选择

项目采用 **FunctionCall** 方式：

| 方案 | 优点 | 缺点 | 是否采用 |
|------|------|------|---------|
| LangChain | 高度封装，简单易用 | 黑盒，不利于学习 | ❌ |
| ReAct Prompt | 通用性强 | 设计繁琐 | ❌（后续研究） |
| FunctionCall | 强大且直接 | 需要高阶模型 | ✅ |

### 5.3 LLM 要求

- 兼容 OpenAI 接口
- 支持 FunctionCall
- 支持 JSON Format 输出
- **推荐模型**: Deepseek、ChatGPT

---

## 六、开发和部署

### 6.1 环境要求

- **Docker**: 20.10+
- **Docker Compose**
- **模型能力**:
  - 兼容 OpenAI 接口
  - 支持 FunctionCall
  - 支持 JSON Format 输出

### 6.2 快速部署

#### 生产环境部署

```bash
# 1. 克隆项目
git clone https://github.com/Simpleyyt/ai-manus.git
cd ai-manus

# 2. 复制配置文件
cp .env.example .env

# 3. 修改 .env 配置
# 填写 API_KEY、API_BASE 等

# 4. 启动服务
docker compose up -d
```

#### 开发环境运行

```bash
# 相当于 docker compose -f docker-compose-development.yaml up
./dev.sh

# 停止服务
./dev.sh down -v

# 重新构建镜像
./run build

# 推送镜像到仓库
./run push
```

> **注意**: 开发模式下只会全局启动一个沙盒

---

## 七、核心技术要点总结

### 7.1 Sandbox 隔离机制

| 隔离维度 | 实现方式 | 目的 |
|---------|---------|------|
| 进程隔离 | Docker 容器 | 防止任务互相干扰 |
| 网络隔离 | Docker Network | 独立的网络命名空间 |
| 文件隔离 | Docker Volume | 独立的文件系统 |
| 资源限制 | Docker Limits | CPU/内存/磁盘限制 |
| 生命周期 | TTL 自动回收 | 30 分钟后自动销毁 |

### 7.2 Browser Use 实现路径

```
Agent 工具调用
    ↓
Backend API 请求
    ↓
Sandbox 容器内的 Browser Service
    ↓
通过 CDP (Chrome DevTools Protocol)
    ↓
控制 Chrome 浏览器
    ↓
执行网页操作（点击、输入、截图等）
    ↓
返回结果给 Agent
```

### 7.3 关键设计亮点

1. **动态沙盒创建**
   - Backend 通过 Docker API 动态创建容器
   - 每个任务独立沙盒，完全隔离

2. **实时事件流**
   - 使用 SSE (Server-Sent Events)
   - 实时推送 Agent 执行过程

3. **多工具集成**
   - File API - 文件读写
   - Shell API - 命令执行
   - Browser API - 网页操作
   - Python/Node API - 代码执行

4. **资源管理**
   - TTL 自动回收
   - 容器命名规范
   - 网络统一管理

---

## 八、与其他方案对比

### 8.1 vs E2B

- **E2B**: 商业化沙盒服务，功能强大但需付费
- **Manus Sandbox**: 开源自建，完全可控
- **优势**: 无使用限制，可定制化
- **劣势**: 需要自行维护

### 8.2 vs Modal/Dagger

- **Modal/Dagger**: 云端容器编排服务
- **Manus Sandbox**: 本地 Docker
- **优势**: 可本地部署，数据私密
- **劣势**: 需要自己管理基础设施

---

## 九、参考资源

- **项目地址**: https://github.com/Simpleyyt/ai-manus
- **QQ 交流群**: 100547581
- **ReAct 框架**: [Prompt Engineering Guide - ReAct](https://www.promptingguide.ai/techniques/react)
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/

---

## 十、总结

Manus Sandbox 的实现核心思路：

1. **容器化隔离**: 使用 Docker 提供独立的执行环境
2. **动态管理**: Backend 通过 Docker API 按需创建/销毁容器
3. **工具封装**: 在容器内提供统一的 API 服务（Browser/Shell/File/Python）
4. **无头浏览器**: 使用 Xvfb + Chrome + CDP 实现浏览器自动化
5. **远程访问**: 通过 VNC 和 CDP 提供图形和调试能力
6. **生命周期**: TTL 机制自动回收闲置容器

这种设计简单高效，适合学习和快速原型开发。
