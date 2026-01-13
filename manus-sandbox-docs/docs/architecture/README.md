# 架构文档

本目录包含系统架构设计相关文档。

## 📋 文档列表

### 远程桌面架构

完整的远程桌面解决方案由两部分组成：

#### 1. 基础设施层 - Xvfb 与 x11vnc

**[Xvfb 与 x11vnc 指南](xvfb-x11vnc-guide.md)** - 虚拟显示服务器和 VNC 服务器配置
  - Xvfb 是什么：虚拟 X11 显示服务器
  - x11vnc 是什么：VNC 服务器
  - 安装与配置：Docker、systemd 部署方式
  - 窗口管理器：fluxbox、openbox 集成
  - 应用场景：无头服务器、自动化测试、CI/CD
  - 故障排查：常见问题与解决方案

#### 2. Web 访问层 - NoVNC

**[NoVNC 组件详细说明](novnc-component-guide.md)** - NoVNC 远程桌面解决方案
  - NoVNC 是什么：HTML5/JavaScript 的 VNC 客户端
  - 技术架构：浏览器 → WebSocket 代理 → VNC 服务器 → 虚拟显示
  - 核心组件：NoVNC JavaScript 库、WebSocket 代理服务器、浏览器集成
  - 部署方式：Docker 容器、systemd 服务、Docker Compose
  - 安全配置：开发环境 vs 生产环境、SSL/TLS、防火墙
  - 性能优化：客户端与服务器端优化参数
  - 故障排查：常见问题与解决方案
  - 应用场景：远程测试、云端开发、技术支持

## 📐 架构概览

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

---

**更新日期**: 2026-01-09
