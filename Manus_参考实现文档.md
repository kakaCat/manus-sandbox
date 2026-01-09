# Manus Sandbox 参考实现文档

> 基于 ai-manus 项目的详细技术实现分析

**项目地址**: https://github.com/Simpleyyt/ai-manus

---

## 📋 目录

1. [项目结构](#项目结构)
2. [核心架构](#核心架构)
3. [Sandbox 容器实现](#sandbox-容器实现)
4. [Backend 沙盒管理](#backend-沙盒管理)
5. [服务编排 Supervisor](#服务编排-supervisor)
6. [API 接口设计](#api-接口设计)
7. [部署方案](#部署方案)
8. [开发调试](#开发调试)

---

## 项目结构

```
ai-manus/
├── frontend/               # Vue 3 前端
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 主应用入口
│   │   ├── application/   # 应用层
│   │   ├── domain/        # 领域层
│   │   └── infrastructure/
│   │       └── external/
│   │           └── sandbox/
│   │               └── docker_sandbox.py  # 核心实现 ⭐
│   ├── Dockerfile
│   └── requirements.txt
│
├── sandbox/                # Ubuntu 沙盒容器
│   ├── app/
│   │   ├── main.py        # Sandbox API 服务
│   │   ├── api/           # 工具 API 路由
│   │   │   ├── file.py    # 文件操作
│   │   │   ├── shell.py   # Shell 命令
│   │   │   └── supervisor.py
│   │   ├── services/      # 工具实现
│   │   └── core/
│   ├── Dockerfile         # Sandbox 镜像定义 ⭐
│   ├── supervisord.conf   # 服务编排配置 ⭐
│   └── requirements.txt
│
├── docker-compose.yml            # 生产部署配置
├── docker-compose-development.yml # 开发调试配置
├── .env.example                  # 环境变量模板
├── dev.sh                        # 开发启动脚本
└── run.sh                        # 镜像构建脚本
```

---

## 核心架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Web)                      │
│                     Vue 3 + TypeScript                   │
│              端口: 5173 (生产) / 5173 (开发)            │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/WebSocket
                  │
┌─────────────────▼───────────────────────────────────────┐
│                   Backend (Server)                       │
│                    FastAPI + Python                      │
│               端口: 8000                                 │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  DockerSandbox Manager                          │   │
│  │  - 通过 /var/run/docker.sock 管理容器          │   │
│  │  - 动态创建/销毁 Sandbox                       │   │
│  │  - 与 Sandbox API 通信                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │ Docker API + HTTP
                  │
┌─────────────────▼───────────────────────────────────────┐
│                 Sandbox (隔离环境)                       │
│                Ubuntu 22.04 + Docker                     │
│                                                           │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │   Xvfb       │   Chrome     │   Socat      │        │
│  │  虚拟显示    │   浏览器     │   端口转发   │        │
│  └──────────────┴──────────────┴──────────────┘        │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │  x11vnc      │  websockify  │   FastAPI    │        │
│  │  VNC服务     │  WS转换      │   工具API    │        │
│  └──────────────┴──────────────┴──────────────┘        │
│                                                           │
│  端口: 8080 (API), 9222 (CDP), 5900 (VNC), 5901 (WS)   │
└───────────────────────────────────────────────────────────┘
```

### 工作流程

#### 1. 创建 Sandbox

```python
# backend/app/infrastructure/external/sandbox/docker_sandbox.py

@staticmethod
def _create_task() -> 'DockerSandbox':
    """动态创建 Docker Sandbox"""
    settings = get_settings()

    # 生成唯一容器名
    container_name = f"{settings.sandbox_name_prefix}-{str(uuid.uuid4())[:8]}"

    # 创建 Docker 客户端
    docker_client = docker.from_env()

    # 容器配置
    container_config = {
        "image": settings.sandbox_image,  # simpleyyt/manus-sandbox
        "name": container_name,
        "detach": True,
        "remove": True,  # 容器停止后自动删除
        "environment": {
            "SERVICE_TIMEOUT_MINUTES": settings.sandbox_ttl_minutes,  # TTL
            "CHROME_ARGS": settings.sandbox_chrome_args,
            "HTTPS_PROXY": settings.sandbox_https_proxy,
            "HTTP_PROXY": settings.sandbox_http_proxy,
            "NO_PROXY": settings.sandbox_no_proxy
        }
    }

    # 加入指定网络
    if settings.sandbox_network:
        container_config["network"] = settings.sandbox_network

    # 创建并启动容器
    container = docker_client.containers.run(**container_config)

    # 获取容器 IP
    container.reload()
    ip_address = DockerSandbox._get_container_ip(container)

    return DockerSandbox(ip=ip_address, container_name=container_name)
```

#### 2. 等待 Sandbox 就绪

```python
async def ensure_sandbox(self) -> None:
    """等待所有服务启动"""
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            # 调用 Sandbox 的 supervisor status API
            response = await self.client.get(
                f"{self.base_url}/api/v1/supervisor/status"
            )

            services = response.json()["data"]

            # 检查所有服务是否 RUNNING
            all_running = all(
                service["statename"] == "RUNNING"
                for service in services
            )

            if all_running:
                logger.info("All services are RUNNING - sandbox ready")
                return

            await asyncio.sleep(retry_interval)

        except Exception as e:
            logger.warning(f"Check failed (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(retry_interval)
```

#### 3. 调用工具

```python
# 文件操作示例
async def file_write(self, file: str, content: str, **kwargs) -> ToolResult:
    response = await self.client.post(
        f"{self.base_url}/api/v1/file/write",
        json={
            "file": file,
            "content": content,
            "append": kwargs.get("append", False),
            "sudo": kwargs.get("sudo", False)
        }
    )
    return ToolResult(**response.json())

# Shell 命令示例
async def exec_command(self, session_id: str, exec_dir: str, command: str):
    response = await self.client.post(
        f"{self.base_url}/api/v1/shell/exec",
        json={
            "id": session_id,
            "exec_dir": exec_dir,
            "command": command
        }
    )
    return ToolResult(**response.json())

# 浏览器操作
async def get_browser(self) -> Browser:
    """返回连接到 Sandbox Chrome 的 Browser 实例"""
    return PlaywrightBrowser(self.cdp_url)
```

#### 4. 销毁 Sandbox

```python
async def destroy(self) -> bool:
    """销毁 Docker Sandbox"""
    try:
        # 关闭 HTTP 客户端
        if self.client:
            await self.client.aclose()

        # 强制删除容器
        if self.container_name:
            docker_client = docker.from_env()
            container = docker_client.containers.get(self.container_name)
            container.remove(force=True)

        return True
    except Exception as e:
        logger.error(f"Failed to destroy sandbox: {e}")
        return False
```

---

## Sandbox 容器实现

### Dockerfile 分析

```dockerfile
FROM ubuntu:22.04

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV HOSTNAME=sandbox

# 配置国内镜像源（加速）
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list

# 安装基础工具
RUN apt-get update && apt-get install -y \
    sudo bc curl wget gnupg software-properties-common \
    xvfb \          # X Virtual Framebuffer - 虚拟显示
    x11vnc \        # VNC Server - 远程桌面
    xterm \         # 终端模拟器
    socat \         # 端口转发工具
    supervisor \    # 进程管理器
    websockify \    # VNC 转 WebSocket
    && apt-get clean

# 创建用户并授予 sudo 权限
RUN useradd -m -d /home/ubuntu -s /bin/bash ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu

# 安装 Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3-pip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# 安装 Node.js 20
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | \
    gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | \
    tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y nodejs

# 安装 Chromium 浏览器
RUN add-apt-repository ppa:xtradeb/apps -y && \
    apt-get update && \
    apt-get install -y chromium --no-install-recommends

# 安装中文字体（支持中文网页）
RUN apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    language-pack-zh-hans

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 配置 supervisor
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

# 暴露端口
EXPOSE 8080 9222 5900 5901

# 启动 supervisor 管理所有服务
CMD ["supervisord", "-n", "-c", "/app/supervisord.conf"]
```

### 端口说明

| 端口 | 服务 | 用途 |
|------|------|------|
| 8080 | FastAPI | Sandbox 工具 API |
| 9222 | CDP | Chrome DevTools Protocol |
| 5900 | VNC | VNC 原始协议 |
| 5901 | WebSocket | VNC 转 WebSocket（供 Web 访问）|

---

## 服务编排 Supervisor

### supervisord.conf 完整配置

```ini
[supervisord]
logfile=/dev/stdout         # 日志输出到标准输出
logfile_maxbytes=0          # 不限制日志大小
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=true               # 前台运行（Docker 必需）
autoshutdown=true           # 所有服务停止后自动退出

# 1️⃣ Xvfb - 虚拟 X11 显示服务器
[program:xvfb]
command=bash -c "rm -f /tmp/.X1-lock && Xvfb :1 -screen 0 1280x1029x24"
autostart=true
autorestart=true
environment=DISPLAY=:1
priority=10                 # 优先级 10 - 最先启动

# 2️⃣ Chrome - 浏览器
[program:chrome]
command=chromium \
    --display=:1 \          # 使用 Xvfb 的 Display :1
    --window-size=1280,1029 \
    --no-sandbox \          # Docker 环境必需
    --disable-gpu \
    --disable-dev-shm-usage \
    --remote-debugging-address=0.0.0.0 \  # 监听所有网卡
    --remote-debugging-port=8222 \        # CDP 端口
    %(ENV_CHROME_ARGS)s                   # 额外参数
autostart=true
autorestart=true
environment=DISPLAY=:1
priority=20
startretries=3
startsecs=5

# 3️⃣ Socat - CDP 端口转发（8222 → 9222）
[program:socat]
command=socat TCP-LISTEN:9222,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:8222
autostart=true
autorestart=true
priority=30
startsecs=2

# 4️⃣ x11vnc - VNC Server
[program:x11vnc]
command=x11vnc -display :1 -nopw -shared -listen 0.0.0.0 -xkb -forever -rfbport 5900
autostart=true
autorestart=true
environment=DISPLAY=:1
priority=40
startsecs=3

# 5️⃣ Websockify - VNC 转 WebSocket
[program:websockify]
command=websockify 0.0.0.0:5901 localhost:5900
autostart=true
autorestart=true
priority=45
startsecs=3

# 6️⃣ FastAPI - Sandbox API 服务
[program:app]
command=uvicorn app.main:app --host 0.0.0.0 --port 8080 %(ENV_UVI_ARGS)s
directory=/app
user=ubuntu                 # 使用 ubuntu 用户运行
autostart=true
autorestart=true
environment=HOME=/home/ubuntu
priority=50
```

### 服务启动顺序

```
启动时间线:
    0s  →  Xvfb 启动 (priority=10)
    ↓
   2s  →  Chrome 启动 (priority=20, 需要 Display :1)
    ↓
   5s  →  Socat 启动 (priority=30, 转发 CDP 端口)
    ↓
   8s  →  x11vnc 启动 (priority=40, 需要 Display :1)
    ↓
  11s  →  Websockify 启动 (priority=45)
    ↓
  14s  →  FastAPI 启动 (priority=50)
    ↓
  ~20s → 所有服务就绪
```

### 关键技术点

#### 1. Xvfb 虚拟显示

```bash
# 清理旧锁文件，避免启动失败
rm -f /tmp/.X1-lock

# 启动虚拟 X11 Server
Xvfb :1 -screen 0 1280x1029x24
#     ↑          ↑    ↑
#     |          |    └─ 24位色深
#     |          └────── 屏幕编号和分辨率
#     └─────────────── Display 编号
```

#### 2. Chrome CDP 暴露

```bash
chromium \
    --display=:1 \                        # 连接到虚拟显示
    --remote-debugging-address=0.0.0.0 \  # 监听所有网卡（允许外部访问）
    --remote-debugging-port=8222          # CDP 端口
```

**问题**: Chrome 的 `--remote-debugging-address=0.0.0.0` 在某些版本不生效

**解决**: 使用 `socat` 转发端口

```bash
socat TCP-LISTEN:9222,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:8222
#     ↑                                           ↑
#     └─ 监听 0.0.0.0:9222                       └─ 转发到本地 8222
```

#### 3. VNC 图形访问

```bash
# 启动 VNC Server
x11vnc -display :1 \      # 连接到虚拟显示
       -nopw \            # 无密码
       -shared \          # 允许多客户端
       -listen 0.0.0.0 \  # 监听所有网卡
       -forever \         # 持续运行
       -rfbport 5900      # VNC 端口

# 转换为 WebSocket（供 Web 前端使用）
websockify 0.0.0.0:5901 localhost:5900
```

---

## API 接口设计

### Sandbox API 结构

```
sandbox/app/
├── api/
│   ├── router.py           # 路由汇总
│   ├── file.py             # 文件操作 API
│   ├── shell.py            # Shell 命令 API
│   └── supervisor.py       # Supervisor 状态 API
│
├── services/
│   ├── file_service.py     # 文件操作实现
│   ├── shell_service.py    # Shell 执行实现
│   └── supervisor_service.py
│
└── schemas/
    ├── file.py             # 请求/响应模型
    └── shell.py
```

### 核心 API 接口

#### 1. 文件操作

```python
# POST /api/v1/file/write
{
  "file": "/home/ubuntu/test.py",
  "content": "print('hello')",
  "append": false,
  "sudo": false
}

# POST /api/v1/file/read
{
  "file": "/home/ubuntu/test.py",
  "start_line": 1,
  "end_line": 10,
  "sudo": false
}

# POST /api/v1/file/list
{
  "path": "/home/ubuntu"
}

# POST /api/v1/file/find
{
  "path": "/home/ubuntu",
  "glob": "*.py"
}

# POST /api/v1/file/replace
{
  "file": "/home/ubuntu/test.py",
  "old_str": "hello",
  "new_str": "world"
}

# POST /api/v1/file/upload
# 使用 multipart/form-data
{
  "file": <binary>,
  "path": "/home/ubuntu/upload.txt"
}

# GET /api/v1/file/download?path=/home/ubuntu/test.py
# 返回二进制流
```

#### 2. Shell 命令

```python
# POST /api/v1/shell/exec
{
  "id": "session-001",        # 会话 ID（可复用）
  "exec_dir": "/home/ubuntu",  # 执行目录
  "command": "python test.py"  # 命令
}

# POST /api/v1/shell/view
{
  "id": "session-001",
  "console": true              # 是否显示历史输出
}

# POST /api/v1/shell/wait
{
  "id": "session-001",
  "seconds": 5                 # 等待时间（可选）
}

# POST /api/v1/shell/write
{
  "id": "session-001",
  "input": "y",                # 输入内容
  "press_enter": true          # 是否按回车
}

# POST /api/v1/shell/kill
{
  "id": "session-001"
}
```

#### 3. Supervisor 状态

```python
# GET /api/v1/supervisor/status
# 返回所有服务状态
{
  "success": true,
  "data": [
    {
      "name": "xvfb",
      "statename": "RUNNING",
      "description": "pid 123, uptime 0:01:23"
    },
    {
      "name": "chrome",
      "statename": "RUNNING",
      "description": "pid 456, uptime 0:01:18"
    }
    // ...其他服务
  ]
}
```

### 统一响应格式

```python
# models/tool_result.py
class ToolResult(BaseModel):
    success: bool           # 是否成功
    message: str            # 消息
    data: Any = None        # 数据（可选）
    error: str = None       # 错误详情（可选）

# 示例
{
  "success": true,
  "message": "File written successfully",
  "data": {
    "file": "/home/ubuntu/test.py",
    "size": 1024
  }
}
```

---

## 部署方案

### 生产环境部署

#### docker-compose.yml

```yaml
services:
  # 前端
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

  # 后端
  backend:
    image: simpleyyt/manus-backend
    depends_on:
      - sandbox
      - mongodb
      - redis
    restart: unless-stopped
    volumes:
      # ⭐ 挂载 Docker socket（用于创建 Sandbox）
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - manus-network
    environment:
      # LLM 配置
      - API_BASE=https://api.openai.com/v1
      - API_KEY=sk-xxxx
      - MODEL_NAME=gpt-4o
      - TEMPERATURE=0.7
      - MAX_TOKENS=2000

      # Sandbox 配置
      - SANDBOX_IMAGE=simpleyyt/manus-sandbox
      - SANDBOX_NAME_PREFIX=sandbox
      - SANDBOX_TTL_MINUTES=30              # 30分钟自动回收
      - SANDBOX_NETWORK=manus-network

      # MongoDB
      - MONGODB_URI=mongodb://mongodb:27017
      - MONGODB_DATABASE=manus

      # Redis
      - REDIS_HOST=redis
      - REDIS_PORT=6379

      # 搜索引擎
      - SEARCH_PROVIDER=bing

      # 认证
      - AUTH_PROVIDER=password
      - JWT_SECRET_KEY=your-secret-key-here

      # 日志
      - LOG_LEVEL=INFO

  # Sandbox 镜像预拉取（不运行）
  sandbox:
    image: simpleyyt/manus-sandbox
    command: /bin/sh -c "exit 0"  # 立即退出
    restart: "no"
    networks:
      - manus-network

  # MongoDB
  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped
    networks:
      - manus-network

  # Redis
  redis:
    image: redis:7.0
    restart: unless-stopped
    networks:
      - manus-network

volumes:
  mongodb_data:
    name: manus-mongodb-data

networks:
  manus-network:
    name: manus-network
    driver: bridge
```

#### 启动命令

```bash
# 1. 克隆项目
git clone https://github.com/Simpleyyt/ai-manus.git
cd ai-manus

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改 API_KEY 等配置

# 3. 启动服务
docker compose up -d

# 4. 查看日志
docker compose logs -f

# 5. 访问应用
open http://localhost:5173
```

### 关键配置项说明

#### Backend 环境变量

```bash
# === LLM 配置 ===
API_BASE=https://api.openai.com/v1    # API 端点
API_KEY=sk-xxxx                        # API 密钥
MODEL_NAME=gpt-4o                      # 模型名称
TEMPERATURE=0.7                        # 温度参数
MAX_TOKENS=2000                        # 最大 Token

# === Sandbox 配置 ===
# 可选：使用固定 Sandbox（不动态创建）
#SANDBOX_ADDRESS=192.168.1.100         # Sandbox IP 或域名

# 动态创建模式
SANDBOX_IMAGE=simpleyyt/manus-sandbox  # Sandbox 镜像
SANDBOX_NAME_PREFIX=sandbox            # 容器名前缀
SANDBOX_TTL_MINUTES=30                 # 存活时间（分钟）
SANDBOX_NETWORK=manus-network          # Docker 网络

# Chrome 额外参数（可选）
#SANDBOX_CHROME_ARGS=--proxy-server=http://proxy:8080

# 代理配置（可选）
#SANDBOX_HTTPS_PROXY=http://proxy:8080
#SANDBOX_HTTP_PROXY=http://proxy:8080
#SANDBOX_NO_PROXY=localhost,127.0.0.1

# === 数据库配置 ===
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=manus

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# === 搜索引擎 ===
SEARCH_PROVIDER=bing                   # 选项: baidu, google, bing

# Google 搜索（仅 SEARCH_PROVIDER=google 时需要）
#GOOGLE_SEARCH_API_KEY=
#GOOGLE_SEARCH_ENGINE_ID=

# === 认证配置 ===
AUTH_PROVIDER=password                 # 选项: password, none, local

# 密码认证
PASSWORD_SALT=random-salt-here
PASSWORD_HASH_ROUNDS=10

# 本地认证（开发用）
#LOCAL_AUTH_EMAIL=admin@example.com
#LOCAL_AUTH_PASSWORD=admin

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# === 邮件配置 ===
# 用于发送验证码（仅 AUTH_PROVIDER=password 时需要）
#EMAIL_HOST=smtp.gmail.com
#EMAIL_PORT=587
#EMAIL_USERNAME=your-email@gmail.com
#EMAIL_PASSWORD=your-password
#EMAIL_FROM=your-email@gmail.com

# === MCP 工具集成 ===
#MCP_CONFIG_PATH=/etc/mcp.json

# === 日志 ===
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
```

---

## 开发调试

### 开发环境配置

#### docker-compose-development.yml

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app        # 挂载源码（热重载）
      - /app/node_modules      # 排除 node_modules
    environment:
      - BACKEND_URL=http://localhost:8000

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app         # 挂载源码（热重载）
      - /var/run/docker.sock:/var/run/docker.sock:ro
    env_file:
      - .env
    environment:
      - UVI_ARGS=--reload      # Uvicorn 热重载
    depends_on:
      - sandbox

  # 开发模式：全局启动一个 Sandbox
  sandbox:
    build:
      context: ./sandbox
      dockerfile: Dockerfile
    ports:
      - "8080:8080"            # API
      - "9222:9222"            # CDP
      - "5900:5900"            # VNC
      - "5901:5901"            # WebSocket
    volumes:
      - ./sandbox:/app         # 挂载源码（热重载）
    environment:
      - UVI_ARGS=--reload      # Uvicorn 热重载
      - SERVICE_TIMEOUT_MINUTES=0  # 不自动退出
```

### 开发脚本

#### dev.sh

```bash
#!/bin/bash

# 启动开发环境
./dev.sh up

# 停止并清理
./dev.sh down -v

# 重新构建镜像
./dev.sh build

# 查看日志
./dev.sh logs -f
```

实际上是对 `docker compose -f docker-compose-development.yml` 的封装。

### 开发调试要点

#### 1. 热重载

```yaml
# Backend & Sandbox
volumes:
  - ./backend:/app           # 源码挂载
environment:
  - UVI_ARGS=--reload        # Uvicorn --reload

# Frontend
volumes:
  - ./frontend:/app
command: npm run dev -- --host 0.0.0.0  # Vite dev server
```

#### 2. 端口暴露

```yaml
# 开发模式暴露所有端口，方便调试
backend:
  ports:
    - "8000:8000"       # Backend API

sandbox:
  ports:
    - "8080:8080"       # Sandbox API
    - "9222:9222"       # Chrome CDP
    - "5900:5900"       # VNC
    - "5901:5901"       # WebSocket VNC
```

#### 3. 调试工具

```bash
# 1. 查看 Sandbox 浏览器（VNC）
# macOS
open vnc://localhost:5900

# Linux
vncviewer localhost:5900

# 2. 连接 Chrome DevTools
# 浏览器访问
open http://localhost:9222

# 3. 查看 Supervisor 状态
curl http://localhost:8080/api/v1/supervisor/status

# 4. 测试文件操作
curl -X POST http://localhost:8080/api/v1/file/write \
  -H "Content-Type: application/json" \
  -d '{
    "file": "/tmp/test.txt",
    "content": "Hello Sandbox"
  }'

# 5. 测试 Shell 命令
curl -X POST http://localhost:8080/api/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "exec_dir": "/tmp",
    "command": "ls -la"
  }'
```

### 开发注意事项

#### 全局 Sandbox vs 动态 Sandbox

| 模式 | 开发环境 | 生产环境 |
|------|---------|---------|
| Sandbox 数量 | 1个全局 | 每个任务一个 |
| 启动方式 | docker-compose | Backend 动态创建 |
| 地址配置 | 固定 IP | 动态获取 |
| 生命周期 | 手动管理 | TTL 自动回收 |

```python
# Backend 检测模式
settings = get_settings()

if settings.sandbox_address:
    # 开发模式：使用固定 Sandbox
    sandbox = DockerSandbox(ip=settings.sandbox_address)
else:
    # 生产模式：动态创建
    sandbox = await DockerSandbox.create()
```

#### 依赖更新

```bash
# Backend 依赖变化
cd backend
pip install -r requirements.txt

# 或重新构建镜像
./dev.sh down -v
./dev.sh build
./dev.sh up

# Frontend 依赖变化
cd frontend
npm install

# 或重新构建
./dev.sh down -v
./dev.sh build
./dev.sh up

# Sandbox 依赖变化
cd sandbox
pip install -r requirements.txt
# 重新构建
./dev.sh build sandbox
```

---

## 镜像构建与发布

### 构建脚本 run.sh

```bash
#!/bin/bash

# 设置镜像仓库和标签
export IMAGE_REGISTRY=${IMAGE_REGISTRY:-simpleyyt}
export IMAGE_TAG=${IMAGE_TAG:-latest}

# 构建所有镜像
./run.sh build

# 推送到镜像仓库
./run.sh push

# 构建指定镜像
./run.sh build backend
./run.sh build sandbox
./run.sh build frontend
```

### 多架构构建

```bash
# 使用 buildx 构建多架构镜像
docker buildx build --platform linux/amd64,linux/arm64 \
  -t simpleyyt/manus-backend:latest \
  --push \
  ./backend

docker buildx build --platform linux/amd64,linux/arm64 \
  -t simpleyyt/manus-sandbox:latest \
  --push \
  ./sandbox

docker buildx build --platform linux/amd64,linux/arm64 \
  -t simpleyyt/manus-frontend:latest \
  --push \
  ./frontend
```

---

## 核心技术要点总结

### 1. 动态沙盒管理

```python
# Backend 通过 Docker SDK 动态创建容器
docker_client = docker.from_env()
container = docker_client.containers.run(
    image="simpleyyt/manus-sandbox",
    name=f"sandbox-{uuid.uuid4()[:8]}",
    detach=True,
    remove=True,  # 容器停止后自动删除
    network="manus-network"
)
```

### 2. 服务编排 Supervisor

- 使用 **priority** 控制启动顺序
- **Xvfb** 最先启动（提供虚拟显示）
- **Chrome** 依赖 Xvfb
- **x11vnc** 依赖 Xvfb
- **FastAPI** 最后启动

### 3. 无头浏览器方案

```
Xvfb (:1) → Chrome (--display=:1) → CDP (9222)
     ↓
 x11vnc (5900) → websockify (5901) → Web NoVNC
```

### 4. 容器网络通信

```yaml
networks:
  manus-network:
    driver: bridge

# Backend 和 Sandbox 在同一网络
# Backend 通过容器 IP 访问 Sandbox API
# http://{container_ip}:8080/api/v1/...
```

### 5. TTL 自动回收

```python
# Sandbox 容器环境变量
SERVICE_TIMEOUT_MINUTES=30

# Sandbox 内部实现（伪代码）
start_time = time.time()
while True:
    if time.time() - start_time > TTL:
        sys.exit(0)  # 自动退出
    await asyncio.sleep(60)
```

### 6. 工具 API 抽象

```
Backend Agent
    ↓ (HTTP)
Sandbox API (/api/v1/file/write)
    ↓ (Python)
File Service (file_service.py)
    ↓ (System Call)
Linux Filesystem
```

---

## 与理论文档的对应关系

| 理论概念 | 实际实现 | 文件位置 |
|---------|---------|---------|
| Docker 动态创建 | `DockerSandbox._create_task()` | `backend/app/infrastructure/external/sandbox/docker_sandbox.py` |
| Xvfb 虚拟显示 | `supervisord.conf [program:xvfb]` | `sandbox/supervisord.conf` |
| Chrome CDP | `--remote-debugging-port=8222` | `sandbox/supervisord.conf` |
| Socat 端口转发 | `socat TCP-LISTEN:9222...` | `sandbox/supervisord.conf` |
| VNC 访问 | `x11vnc + websockify` | `sandbox/supervisord.conf` |
| 文件操作 | `file_write(), file_read()` | `sandbox/app/services/file_service.py` |
| Shell 执行 | `exec_command()` | `sandbox/app/services/shell_service.py` |
| 浏览器控制 | `PlaywrightBrowser(cdp_url)` | `backend/app/infrastructure/external/browser/` |

---

## 扩展阅读

- **Supervisor 文档**: http://supervisord.org/
- **Docker SDK for Python**: https://docker-py.readthedocs.io/
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/
- **Xvfb 使用指南**: https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml
- **x11vnc 文档**: https://github.com/LibVNC/x11vnc
- **websockify**: https://github.com/novnc/websockify

---

## 总结

ai-manus 的 Sandbox 实现是一个完整的生产级方案：

✅ **动态隔离**: 每个任务独立 Docker 容器
✅ **服务编排**: Supervisor 管理 6 个服务
✅ **无头浏览器**: Xvfb + Chrome + CDP
✅ **远程访问**: VNC + WebSocket
✅ **工具集成**: File/Shell/Browser API
✅ **自动回收**: TTL 机制防止资源泄漏
✅ **热重载**: 开发模式支持代码热更新
✅ **多架构**: 支持 amd64 和 arm64

这是一个值得学习和参考的优秀开源实现！
