# 🚀 VibeHub

**AI 驱动的 Web 工具工坊** —— 用自然语言描述你想要的工具，AI 自动生成代码、测试、部署并上线，全程无需手写一行代码。

---

## ✨ 项目简介

VibeHub 是一个本地部署的 **AI Web 工具自动化平台**。它将 Claude CLI 作为代码生成引擎，让用户通过自然语言描述需求，即可自动完成：

1. **需求审核** — Guard Agent 对用户请求进行分类和过滤
2. **代码生成** — Claude CLI 根据详细的 Prompt 规范生成完整的 Python Web 工具
3. **自动测试** — 自动生成并运行测试脚本，未通过则进入自愈修复循环（最多 3 次）
4. **一键部署** — 通过 `uv` 启动工具进程，Caddy 反向代理自动注册路由
5. **统一管理** — NiceGUI 构建的现代化 Dashboard，支持启动/停止/重启/删除/重命名

整个流程从需求到上线，完全自动化。

---

## 🏗️ 系统架构

```
用户浏览器
    │
    ▼
┌─────────────────────────────────────────┐
│  Caddy 反向代理网关 (0.0.0.0:9529)      │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ /* → Hub UI  │  │ /tools/{slug}/*  │ │
│  │  (port 8080) │  │  → 各工具进程     │ │
│  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────┘
    │                         │
    ▼                         ▼
┌──────────┐         ┌──────────────┐
│ NiceGUI  │         │ 工具子进程    │
│ Hub Core │         │ (FastAPI +   │
│ port 8080│         │  Uvicorn)    │
└──────────┘         └──────────────┘
    │
    ├── Dashboard (看板页)
    ├── Builder (构建台)
    ├── Claude Agent (代码生成)
    └── Guard Agent (需求审核)
```

---

## 📁 项目结构

```
VibeHub/
├── main.py                    # 应用入口，NiceGUI 页面路由
├── pyproject.toml             # 项目元数据和依赖声明
├── start.bat                  # Windows 一键启动脚本
│
├── hub_core/                  # 核心模块
│   ├── config.py              # 全局配置（路径、端口、CLI 检测）
│   ├── registry.py            # 工具注册表（JSON 持久化）
│   ├── process_manager.py     # 子进程管理（启动/停止/健康检查）
│   ├── caddy_gateway.py       # Caddy Admin API 网关管理
│   ├── claude_agent.py        # Claude CLI 代码生成 & 自愈修复
│   ├── guard_agent.py         # 需求审核 Agent（请求分类过滤）
│   ├── port_manager.py        # 空闲端口分配
│   │
│   └── ui/                    # 前端界面（NiceGUI）
│       ├── theme.py           # 设计系统（CSS/JS/动画/Toast）
│       ├── dashboard.py       # 看板页：卡片式工具管理
│       └── builder.py         # 构建台：需求 → 生成 → 测试 → 部署
│
├── projects/                  # AI 生成的工具目录
│   ├── pdf_to_images_converter/   # 示例：PDF 转图片工具
│   └── images_to_pdf_converter/   # 示例：图片转 PDF 工具
│
├── bin/                       # 外部二进制（不纳入版本控制）
│   ├── uv.exe                 # Python 脚本运行器
│   └── caddy.exe              # HTTP 反向代理服务器
│
├── data/                      # 运行时数据（不纳入版本控制）
│   ├── registry.json          # 工具注册信息
│   └── logs/                  # 日志目录
│
└── runtime/                   # uv 缓存目录（不纳入版本控制）
```

---

## 🔧 核心模块说明

### `claude_agent.py` — AI 代码生成引擎

- 调用 Claude CLI 生成符合严格规范的 Python Web 工具代码
- 代码规范包括：PEP 723 内联元数据、动态端口绑定、相对路径 URL、单文件架构
- 支持自动生成测试脚本并执行，未通过时自动修复（自愈循环）
- 通过 stdin 管道传递 Prompt，完美规避 Windows CMD 引号解析问题

### `guard_agent.py` — 需求审核 Agent

- 使用 Claude CLI 对用户请求进行分类
- 合法请求返回 `PASS|slug|display_name`
- 非法请求（闲聊、攻击等）返回 `REJECT|原因`

### `caddy_gateway.py` — Caddy 网关管理

- 通过 Caddy Admin API 动态管理路由规则
- 每个工具注册为 `/tools/{slug}/*` 路径，反向代理到对应端口
- Hub 主面板作为 fallback 路由，匹配 `/*`

### `process_manager.py` — 子进程管理

- 使用 `uv run` 启动工具脚本（自动解析 PEP 723 依赖）
- 进程树级别的停止和清理（基于 psutil）
- 健康检查：等待端口可连接后才注册路由

### `registry.py` — 工具注册表

- JSON 文件持久化，记录每个工具的名称、路径、状态、创建时间
- 支持状态管理：`active` / `stopped` / `error`

---

## 🚀 快速开始

### 前置要求

| 依赖 | 说明 |
|------|------|
| **Node.js + npm** | Claude CLI 运行依赖 |
| **Claude CLI** | `npm install -g @anthropic-ai/claude-code` |
| **Git Bash** | Claude CLI 在 Windows 上需要 bash 环境 |
| **uv.exe** | Python 脚本运行器，放入 `bin/` 目录，[下载地址](https://github.com/astral-sh/uv/releases) |
| **caddy.exe** | HTTP 反向代理，放入 `bin/` 目录，[下载地址](https://github.com/caddyserver/caddy/releases) |

### 启动

```bash
# 双击 start.bat 或在命令行执行
start.bat
```

启动脚本会自动完成：
1. 检查环境依赖（Node.js, npm, Claude CLI, Git Bash, uv, caddy）
2. 初始化数据目录
3. 配置防火墙规则（端口 9529）
4. 启动 Caddy 网关
5. 启动 VibeHub 主服务

### 访问

- **LAN 访问**：`http://localhost:9529/`
- **内部 UI**：`http://127.0.0.1:8080/`

---

## 🎨 界面特性

- **现代 SaaS 风格** — Inter 字体、圆角卡片、渐变配色
- **实时状态指示** — 运行中(绿色脉冲)、异常(红色)、已停止(灰色)
- **部署进度条** — 6 步进度可视化（审核 → 生成 → 测试 → 启动 → 路由 → 完成）
- **终端风格日志** — JetBrains Mono 字体，实时展示部署过程
- **成功庆祝动画** — 彩纸粒子特效 + Toast 通知 + 浏览器通知
- **暗色终端 + 亮色卡片** — 混合主题设计

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | [NiceGUI](https://nicegui.io/) (基于 FastAPI) |
| AI 引擎 | Claude CLI (`@anthropic-ai/claude-code`) |
| 工具运行时 | [uv](https://github.com/astral-sh/uv) + PEP 723 |
| 反向代理 | [Caddy](https://caddyserver.com/) (Admin API 动态配置) |
| 进程管理 | psutil |
| HTTP 客户端 | httpx (异步) |
| 生成工具框架 | FastAPI + Uvicorn (单文件架构) |

---

## 📝 License

私有项目，仅供个人使用。
