# Xvfb 与 x11vnc VNC 服务指南

## 概述

本文档介绍 Xvfb 和 x11vnc 两个工具的作用、工作原理以及如何配合使用来提供 VNC 远程桌面服务。

---

## 什么是 Xvfb？

### 定义

**Xvfb**（X Virtual Framebuffer）是一个虚拟的 X11 显示服务器，它在内存中执行所有图形操作，而不需要物理显示器。

### 主要特点

- **无头运行**（Headless）：不需要物理显示器、键盘或鼠标
- **内存渲染**：所有图形操作在内存中的虚拟帧缓冲区完成
- **完整 X11 协议支持**：支持所有标准 X11 图形操作
- **轻量级**：相比真实的 X Server，资源占用更少

### 使用场景

1. **自动化测试**：运行需要图形界面的测试用例（如 Selenium、Playwright）
2. **CI/CD 环境**：在没有显示器的服务器上运行图形应用
3. **批量渲染**：后台批量处理图形任务
4. **远程桌面**：配合 VNC 提供虚拟桌面环境

### 启动命令示例

```bash
# 基本启动
Xvfb :99 -screen 0 1920x1080x24

# 参数说明：
# :99              - 显示编号（Display number）
# -screen 0        - 屏幕编号
# 1920x1080x24     - 分辨率和色深（宽x高x色深）
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `:N` | 显示编号 | `:99` |
| `-screen N WxHxD` | 配置屏幕 | `-screen 0 1920x1080x24` |
| `-ac` | 禁用访问控制 | `-ac` |
| `-nolisten tcp` | 禁用 TCP 连接 | `-nolisten tcp` |
| `-fbdir` | 指定帧缓冲目录 | `-fbdir /var/tmp` |

---

## 什么是 x11vnc？

### 定义

**x11vnc** 是一个 VNC 服务器，它允许远程查看和控制真实或虚拟的 X11 显示器（如 Xvfb）。

### 主要特点

- **X11 集成**：直接连接到现有的 X Server（包括 Xvfb）
- **实时共享**：共享正在运行的 X 会话
- **性能优化**：支持多种压缩和优化选项
- **灵活配置**：支持密码保护、SSL 加密等安全特性

### 使用场景

1. **远程桌面访问**：通过 VNC 客户端访问远程 Linux 桌面
2. **技术支持**：远程协助用户解决问题
3. **开发调试**：远程查看无头服务器上运行的图形应用
4. **自动化测试**：实时监控测试执行过程

### 启动命令示例

```bash
# 连接到 Xvfb 显示器并启动 VNC 服务
x11vnc -display :99 -forever -nopw -shared -rfbport 5900

# 参数说明：
# -display :99   - 连接到显示编号 :99 的 X Server
# -forever       - 客户端断开后继续运行
# -nopw          - 不需要密码（仅用于开发环境）
# -shared        - 允许多个客户端同时连接
# -rfbport 5900  - VNC 服务端口
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-display :N` | 指定 X 显示器 | `-display :99` |
| `-forever` | 持续运行 | `-forever` |
| `-nopw` | 无密码（不安全） | `-nopw` |
| `-passwd` | 设置密码 | `-passwd mypassword` |
| `-shared` | 允许多客户端 | `-shared` |
| `-rfbport N` | VNC 端口 | `-rfbport 5900` |
| `-localhost` | 仅本地连接 | `-localhost` |
| `-noxdamage` | 禁用损坏跟踪 | `-noxdamage` |
| `-ncache` | 启用客户端缓存 | `-ncache 10` |

---

## Xvfb + x11vnc 组合使用

### 工作原理

```
┌─────────────────────────────────────────────┐
│                                             │
│  1. Xvfb 创建虚拟显示器 (:99)              │
│     ├─ 内存中的帧缓冲区                     │
│     └─ 监听 X11 协议                        │
│                                             │
│  2. 图形应用连接到 :99                      │
│     └─ export DISPLAY=:99                  │
│                                             │
│  3. x11vnc 连接到 :99                       │
│     ├─ 读取帧缓冲区内容                     │
│     └─ 通过 VNC 协议传输                    │
│                                             │
│  4. VNC 客户端连接                          │
│     ├─ 查看屏幕内容                         │
│     └─ 发送键盘鼠标事件                     │
│                                             │
└─────────────────────────────────────────────┘
```

### 完整启动脚本

```bash
#!/bin/bash

# 配置参数
DISPLAY_NUM=99
VNC_PORT=5900
SCREEN_RESOLUTION="1920x1080x24"

# 1. 启动 Xvfb（后台运行）
echo "启动 Xvfb 虚拟显示器 :${DISPLAY_NUM}..."
Xvfb :${DISPLAY_NUM} \
    -screen 0 ${SCREEN_RESOLUTION} \
    -ac \
    +extension GLX \
    +render \
    -noreset \
    > /var/log/xvfb.log 2>&1 &

XVFB_PID=$!
echo "Xvfb PID: $XVFB_PID"

# 等待 Xvfb 启动
sleep 2

# 2. 设置显示环境变量
export DISPLAY=:${DISPLAY_NUM}

# 3. 启动 x11vnc（后台运行）
echo "启动 x11vnc VNC 服务器..."
x11vnc \
    -display :${DISPLAY_NUM} \
    -forever \
    -shared \
    -rfbport ${VNC_PORT} \
    -nopw \
    -xkb \
    -noxrecord \
    -noxfixes \
    -noxdamage \
    -wait 10 \
    -defer 10 \
    > /var/log/x11vnc.log 2>&1 &

X11VNC_PID=$!
echo "x11vnc PID: $X11VNC_PID"

# 4. 显示连接信息
echo ""
echo "=========================================="
echo "✅ VNC 服务已启动"
echo "=========================================="
echo "VNC 地址: localhost:${VNC_PORT}"
echo "显示编号: :${DISPLAY_NUM}"
echo ""
echo "使用以下命令连接："
echo "  vncviewer localhost:${VNC_PORT}"
echo ""
echo "停止服务："
echo "  kill $XVFB_PID $X11VNC_PID"
echo ""
```

### 测试方法

```bash
# 1. 在虚拟显示器上启动一个应用
export DISPLAY=:99
xterm &

# 或者启动浏览器
google-chrome --no-sandbox --disable-dev-shm-usage &

# 2. 使用 VNC 客户端连接
# macOS: 使用内置 Screen Sharing
# open vnc://localhost:5900

# Linux: 使用 vncviewer
# vncviewer localhost:5900

# Windows: 使用 TigerVNC/RealVNC
```

---

## 实际应用场景

### 1. 自动化测试环境

```bash
# 启动虚拟显示
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# 启动 VNC 以便调试
x11vnc -display :99 -forever -shared &

# 运行测试
pytest tests/ui_tests.py
```

### 2. Docker 容器中的图形应用

```dockerfile
FROM ubuntu:22.04

# 安装 Xvfb 和 x11vnc
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

# 启动脚本
COPY start-vnc.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-vnc.sh

EXPOSE 5900

CMD ["/usr/local/bin/start-vnc.sh"]
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/ui-tests.yml
name: UI Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: 启动虚拟显示
        run: |
          Xvfb :99 -screen 0 1920x1080x24 &
          export DISPLAY=:99

      - name: 运行 UI 测试
        run: npm run test:ui
        env:
          DISPLAY: :99
```

---

## 安全注意事项

### 开发环境

```bash
# 可以使用 -nopw（无密码），仅监听本地
x11vnc -display :99 -localhost -nopw -forever
```

### 生产环境

```bash
# 必须设置密码和 SSL
x11vnc -display :99 \
    -passwd mySecurePassword \
    -ssl \
    -sslonly \
    -forever

# 或使用 SSH 隧道
ssh -L 5900:localhost:5900 user@server
```

---

## 常见问题

### Q1: VNC 连接显示黑屏？

```bash
# 确保 Xvfb 正在运行
ps aux | grep Xvfb

# 检查显示编号是否正确
echo $DISPLAY

# 在虚拟显示上启动窗口管理器
export DISPLAY=:99
fluxbox &
```

### Q2: 如何提高 VNC 性能？

```bash
# 使用性能优化参数
x11vnc -display :99 \
    -forever \
    -shared \
    -ncache 10 \          # 启用客户端缓存
    -ncache_cr \          # 缓存优化
    -speeds lan \         # LAN 速度优化
    -noxdamage \          # 禁用损坏跟踪
    -threads              # 多线程
```

### Q3: 如何查看日志？

```bash
# 启动时重定向日志
Xvfb :99 > /tmp/xvfb.log 2>&1 &
x11vnc -display :99 -o /tmp/x11vnc.log -forever &

# 查看日志
tail -f /tmp/xvfb.log
tail -f /tmp/x11vnc.log
```

---

## 资源链接

- **Xvfb**: [X.Org Documentation](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
- **x11vnc**: [LibVNC Project](https://github.com/LibVNC/x11vnc)
- **VNC 协议**: [RFC 6143](https://tools.ietf.org/html/rfc6143)

---

## 总结

| 工具 | 作用 | 端口 |
|------|------|------|
| **Xvfb** | 虚拟 X11 显示服务器 | X11 协议（通常 6099） |
| **x11vnc** | VNC 服务器（读取 X11 显示） | VNC 协议（默认 5900） |

**组合使用流程**:
1. Xvfb 创建虚拟显示器
2. 图形应用连接到 Xvfb
3. x11vnc 读取 Xvfb 内容
4. VNC 客户端连接查看

---

**文档版本**: v1.0
**更新日期**: 2026-01-09
**作者**: AI Development Team
