# VibeHub · 工具合集

同一套首页和工具，在浏览器与 Windows 客户端中使用。

用户只需：**首页点击工具 → 自动启动 → 使用 → 左上角返回首页**。
没有 AI、新建、导入、编辑、删除、重命名、手动启停或公开管理 API。
现有五个工具的业务代码与图片资源保持不变。

## 开发与构建

构建机准备 **Windows x64、Node.js 22、uv**。Python 3.12 由 uv 管理。

```bat
build.bat
```

脚本执行测试、校验 `tools.json` 与 PEP 723、`npm ci`、前端生产构建，下载并校验固定版本的 uv/Caddy，收集完整工具目录，然后产出：

- `release/windows/VibeHub.exe`：PyInstaller 单文件 Windows 客户端。
- `release/windows/latest.json`：version / platform / filename / bytes / sha256。
- `release/web/` 和 `release/VibeHub-web.zip`：相同前端、清单及工具的 Web 发布包。
- Windows 上 `--target all` 会把 Windows 下载文件一并放入 Web 包的 `release/windows/`。

Linux 只构建 Web 发布包：

```sh
uv run --python 3.12 --locked --group build --group test python build.py --target web
```

Windows exe 必须在 Windows 上编译。仓库的 GitHub Actions 在 Linux/Windows 上分别执行测试、真实进程/代理检查和构建；Windows 还验证冻结 exe 与 WebView2 首页启动。

开发期命令：

```sh
uv sync --python 3.12 --locked --group test
uv run --locked python -m scripts.runtime_binaries
cd frontend && npm ci && npm run build
# 返回仓库根目录
uv run --locked python main.py
# Windows 桌面开发模式
uv run --locked --group desktop python desktop.py
```

前端热更新：启动后端后，在 `frontend/` 运行 `npm run dev`。Vite 把 `/api` 和 `/tools` 都代理到网关 9529。

## 运行发布包

Windows 用户双击 `VibeHub.exe`，无需 Node.js、Claude、Git Bash 或 Anthropic 配置。需要 **Microsoft Edge WebView2 Runtime**。

Web 发布包运行 `start.bat` 或 `./start.sh`。默认仅监听 `127.0.0.1:9529`；明确需要局域网访问时使用 `start.bat --host 0.0.0.0` / `./start.sh --host 0.0.0.0`。不会自动改防火墙，也不会按进程名称或占用端口杀其他应用。

**单 exe 不等于完全离线。** Hub Python 已打包，但工具使用 uv 管理的独立 Python 和依赖；首次运行可能联网下载。现有工具中的第三方 CDN 资源仍可能需要联网。此版本不承诺离线首次启动。

## 新增工具：只改工具与清单

1. 复制 `templates/basic-tool/` 到 `projects/<id>/`，实现功能。
2. 在 `tools.json` 添加一项：

```json
{"id":"my_tool","name":"我的工具","description":"工具用途","icon":"tool"}
```

3. 生成并提交依赖锁：`uv lock --script projects/my_tool/main.py`。
4. 执行同一个 `build.bat`。不需要改前端路由、桌面入口或打包文件清单。

`ToolSpec` 是共享清单模型；`ToolHost` 是共享页面容器。返回首页、启动等待、失败重试只实现一次。返回首页后，已打开的 iframe 保持挂载，重新进入不主动清空页面状态。刷新页面或退出应用会结束当前页面会话。

**公开工具入口是 `/tool/<id>`**。`/tools/<id>/` 是 iframe 内部运行地址，不用于绕过外层导航。

完整约定见 [docs/TOOL_SPEC.md](docs/TOOL_SPEC.md)。

## 结构

```text
hub_core/
  catalog.py          ToolSpec、目录/PEP 723 校验、资源收集
  tool_service.py     唯一启动协调器：去重、就绪、失败与重试
  process_manager.py  uv 工具子进程与 HTTP 健康检查
  child_process.py    进程归属、Windows Job Object、实例锁
  caddy_gateway.py    当前实例专用的 Caddy 与动态路由
  api_adapter.py      只读清单、自动打开、发行下载 API
  application.py      两端共用的启动/退出生命周期
frontend/             唯一一份 React 页面和 ToolHost
projects/             工具代码、main.py.lock 与资源
main.py               Web 入口
desktop.py            WebView2 窗口与退出清理
build.py              唯一构建入口
```

两端都使用真实本地 HTTP 和相同子路径代理，不维护 TestClient 生产桥接分支。Caddy 由当前进程拥有，Admin API 使用随机回环端口，不使用全局 2019；Hub 内部端口也动态分配。桌面网关仅绑定回环地址。

## 数据与日志

源码开发：`.runtime/`。桌面：`%LOCALAPPDATA%\VibeHub`。通过 `VIBEHUB_DATA_DIR` 可覆盖。

- `logs/`：平台和工具日志；不对用户公开代码/日志管理页面。
- `runtime/uv`、`runtime/python`：依赖缓存与工具 Python。
- `apps/<id>/<content-hash>/`：冻结版工具代码及资源的持久副本。
- `tools/<id>/`：新工具可通过 `VIBEHUB_TOOL_DATA_DIR` 存放用户数据。
- `webview/`：窗口浏览器存储。

PyInstaller 临时解压目录只读使用，不能用于持久化。一个数据目录只允许一个活动实例；不会覆盖正在运行实例的状态。退出应用停止所有属于本实例的工具及 Caddy；Windows 用 Job Object 在异常退出时清理后代进程。

旧的 `data/registry.json` / `registry_state.json` 不再参与启动，也不会被自动删除或覆盖。V3 使用随版本发布的 `tools.json`，不迁移旧自动启动配置。

## 下载服务与发布

服务端读取 `release/windows/latest.json` 与其指向的 exe：

- `GET /api/desktop/latest`
- `GET /api/desktop/download`（支持文件响应与 Range）

没有有效 Windows 发行文件时返回 404，首页不显示下载按钮。可通过 `VIBEHUB_RELEASE_DIR` 指向外部发布目录。部署时先上传新 exe，再替换对应清单；不要把尚未完整传输的文件作为 latest 发布。

构建只是生成产物，不会自动部署服务器、上传 GitHub Release 或静默更新已安装的客户端。

## 维护边界

工具代码是受信任的本地 Python，并非沙箱。不要把来自未知来源的脚本加入清单。不要向公网直接开放未认证的工具服务；生产公网部署应在外层加认证和 TLS。

维护 Agent 请先阅读 [AGENTS.md](AGENTS.md)。项目原有许可声明保持：个人项目，仅供个人使用；运行时依赖使用各自上游许可证。
