# 文档目录

本目录包含项目的所有技术文档。

## 📐 架构文档

架构设计和技术实现相关文档。

### 远程桌面架构

- [Xvfb 与 x11vnc 指南](architecture/xvfb-x11vnc-guide.md) - 虚拟显示服务器和 VNC 服务器配置
- [NoVNC 组件详细说明](architecture/novnc-component-guide.md) - NoVNC 远程桌面解决方案的完整技术文档

## 📚 文档结构

```
docs/
├── README.md                           # 本文件 - 文档总索引
└── architecture/                       # 架构设计文档
    ├── README.md                       # 架构文档索引
    ├── xvfb-x11vnc-guide.md           # Xvfb 与 x11vnc 指南
    └── novnc-component-guide.md        # NoVNC 组件详解
```

## 🔍 快速导航

### 远程桌面解决方案

完整的远程桌面技术栈：

```
浏览器 (NoVNC 客户端)
    ↓ WebSocket/WSS
WebSocket 代理 (websockify)
    ↓ VNC 协议
VNC 服务器 (x11vnc)
    ↓ X11 协议
虚拟显示器 (Xvfb)
    ↓
运行的应用程序
```

#### 1. 基础设施层

**[Xvfb 与 x11vnc 指南](architecture/xvfb-x11vnc-guide.md)**
- Xvfb 虚拟显示服务器配置
- x11vnc VNC 服务器部署
- 窗口管理器集成
- 自动化测试应用

#### 2. Web 访问层

**[NoVNC 组件详细说明](architecture/novnc-component-guide.md)**
- NoVNC 定义与特点
- 技术架构与工作原理
- 部署方式（Docker、systemd、Docker Compose）
- 安全配置与性能优化
- 常见问题排查

---

**更新日期**: 2026-01-09
