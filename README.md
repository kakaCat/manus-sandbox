# Manus Sandbox 研究文档

> 深入研究 Manus AI Agent 沙盒环境的实现原理和技术细节

本仓库包含对 Manus Sandbox 技术实现的全面研究和文档整理。

---

## 📚 文档列表

### 1. [Manus Sandbox 实现总结](./Manus_Sandbox实现总结.md)

**来源**: 知乎文章《我也复刻了一个 Manus，带高仿 WebUI 和沙盒》

**内容概要**:
- 整体架构设计（Web + Server + Sandbox）
- Sandbox 沙盒实现方案
- Docker Compose 配置详解
- Chrome CDP 和 VNC 访问实现
- AI Agent 设计模式
- 与 E2B/Modal/Dagger 的对比

**适合人群**: 想要快速了解 Manus Sandbox 核心概念的读者

---

### 2. [Manus 参考实现文档](./Manus_参考实现文档.md)

**来源**: ai-manus 项目源码分析

**内容概要**:
- 完整的项目结构分析
- 核心源码实现详解
  - `DockerSandbox` 类的完整实现
  - Supervisor 配置文件解析
  - API 接口设计规范
- Dockerfile 逐行分析
- 部署方案（生产 + 开发）
- 调试技巧和工具

**适合人群**: 需要实际实现 Manus Sandbox 的开发者

---

## 🎯 核心技术栈

### 容器化
- **Docker**: 容器运行时
- **Docker SDK**: Python 容器管理
- **Docker Compose**: 多容器编排

### 沙盒环境
- **Ubuntu 22.04**: 基础镜像
- **Xvfb**: X Virtual Framebuffer（虚拟显示）
- **Chromium**: 无头浏览器
- **Supervisor**: 进程管理器

### 远程访问
- **CDP**: Chrome DevTools Protocol
- **x11vnc**: VNC Server
- **websockify**: VNC 转 WebSocket
- **socat**: 端口转发

### 后端服务
- **FastAPI**: Python Web 框架
- **Uvicorn**: ASGI 服务器
- **httpx**: 异步 HTTP 客户端

### 前端
- **Vue 3**: 前端框架
- **NoVNC**: Web VNC 客户端

---

## 🏗️ 架构概览

```
┌─────────────┐
│   Frontend  │  Vue 3 Web UI
│  (Port 5173)│
└──────┬──────┘
       │ HTTP/WebSocket
       │
┌──────▼──────┐
│   Backend   │  FastAPI + Python
│  (Port 8000)│
│             │
│ ┌─────────┐ │
│ │ Docker  │ │  通过 /var/run/docker.sock
│ │ Manager │ │  动态创建和销毁容器
│ └─────────┘ │
└──────┬──────┘
       │ Docker API + HTTP
       │
┌──────▼──────────────────────────────────┐
│  Sandbox Container (Ubuntu 22.04)       │
│                                          │
│  ┌─────────┬─────────┬─────────────┐   │
│  │  Xvfb   │ Chrome  │   Socat     │   │
│  │  (虚拟  │ (浏览器)│  (端口转发) │   │
│  │   显示) │         │             │   │
│  └─────────┴─────────┴─────────────┘   │
│                                          │
│  ┌─────────┬──────────┬────────────┐   │
│  │ x11vnc  │websockify│  FastAPI   │   │
│  │ (VNC)   │  (WS转换)│  (工具API) │   │
│  └─────────┴──────────┴────────────┘   │
│                                          │
│  端口: 8080, 9222, 5900, 5901           │
└──────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 查看理论总结

```bash
# 阅读知乎文章总结
cat Manus_Sandbox实现总结.md
```

### 查看实现细节

```bash
# 阅读源码分析
cat Manus_参考实现文档.md
```

### 运行原项目

```bash
# 克隆 ai-manus 项目
git clone https://github.com/Simpleyyt/ai-manus.git
cd ai-manus

# 配置环境变量
cp .env.example .env
vim .env  # 修改 API_KEY

# 启动服务
docker compose up -d

# 访问 Web UI
open http://localhost:5173
```

---

## 📖 学习路径

### 初学者

1. 阅读 [Manus_Sandbox实现总结.md](./Manus_Sandbox实现总结.md)
   - 了解整体架构
   - 理解核心概念

2. 运行 ai-manus 项目
   - 体验实际功能
   - 观察日志输出

### 进阶开发者

1. 阅读 [Manus_参考实现文档.md](./Manus_参考实现文档.md)
   - 理解源码实现
   - 学习 API 设计

2. 修改和调试
   - 启动开发模式
   - 修改 Sandbox 配置
   - 添加新工具

### 高级开发者

1. 扩展功能
   - 集成 MCP 工具
   - 支持多语言运行时
   - 优化性能

2. 生产部署
   - K8s 部署
   - 多节点扩展
   - 监控告警

---

## 🔑 关键实现要点

### 1. 动态沙盒创建

```python
# Backend 通过 Docker SDK 创建容器
docker_client = docker.from_env()
container = docker_client.containers.run(
    image="simpleyyt/manus-sandbox",
    name=f"sandbox-{uuid}",
    detach=True,
    remove=True,  # 自动删除
    network="manus-network",
    environment={"SERVICE_TIMEOUT_MINUTES": 30}
)
```

### 2. Supervisor 服务编排

```ini
# 启动顺序（通过 priority 控制）
[program:xvfb]       # priority=10 (最先)
[program:chrome]     # priority=20
[program:socat]      # priority=30
[program:x11vnc]     # priority=40
[program:websockify] # priority=45
[program:app]        # priority=50 (最后)
```

### 3. 无头浏览器方案

```
Xvfb :1 → Chrome --display=:1 → CDP 9222
    ↓
x11vnc 5900 → websockify 5901 → NoVNC (Web)
```

### 4. TTL 自动回收

```python
# 容器环境变量
SERVICE_TIMEOUT_MINUTES=30  # 30分钟后自动退出

# Sandbox 内部监控超时
if elapsed_time > ttl:
    sys.exit(0)
```

---

## 🔗 相关资源

### 项目链接
- **ai-manus**: https://github.com/Simpleyyt/ai-manus
- **QQ 交流群**: 100547581

### 技术文档
- **Supervisor**: http://supervisord.org/
- **Docker SDK**: https://docker-py.readthedocs.io/
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/
- **Xvfb**: https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml
- **x11vnc**: https://github.com/LibVNC/x11vnc
- **websockify**: https://github.com/novnc/websockify
- **NoVNC**: https://github.com/novnc/noVNC

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果您有任何问题或建议，请：
1. 提交 Issue 讨论
2. Fork 本仓库
3. 创建 Feature 分支
4. 提交 Pull Request

---

## 📝 License

MIT License

---

## 🙏 致谢

- 感谢 [ai-manus](https://github.com/Simpleyyt/ai-manus) 项目提供的优秀开源实现
- 感谢知乎作者"摇一摇"分享的实现经验

---

**最后更新**: 2025-01-09
