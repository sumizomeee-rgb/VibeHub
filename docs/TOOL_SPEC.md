# VibeHub Tool Spec v1

## 工具清单

`tools.json` 是唯一入口。根对象 `schema_version=1`，`tools` 是有序数组。字段必须符合 `hub_core.catalog.ToolSpec`；未知字段、重复 id、非法路径、Windows 保留名会使校验失败。

id 使用小写字母、数字及单个 `_` / `-` 分段，最长 64 字符。id 是稳定标识，不跟随显示名称改变。每个工具目录为 `projects/<id>/`，入口为 `main.py`。图标可使用 avatar/crop/image/pdf/pages/tool，未知图标回退到 tool。

## 运行约定

- `main.py` 包含唯一合法的 PEP 723 `script` 元数据块；第三方依赖完整列在 dependencies。
- 提交 `main.py.lock`，由 `uv lock --script projects/<id>/main.py` 生成。运行器在存在锁时使用 `uv run --locked --no-project --script`。
- FastAPI 应用在文件末尾的 `if __name__ == '__main__'` 中由 Uvicorn 启动。
- 地址只绑定 `127.0.0.1`；端口从 `PORT` 环境变量读取。
- `GET /` 返回正常工具 HTML（HTTP 2xx/3xx）。平台用真实 HTTP 检查就绪，不只检查 TCP 端口。
- 读取 `DISPLAY_NAME` 作为工具标题。持久数据使用 `VIBEHUB_TOOL_DATA_DIR`。
- 不启动浏览器、不修改其他工具、不管理自身的外层窗口。
- 工具不是安全沙箱；只接入维护者审核过的源码和依赖。

## 路由与公共导航

用户入口 `/tool/<id>` 渲染 React ToolHost。外层始终显示“返回首页”；不要在每个 Python 工具复制返回按钮，也不要调用 `window.top.location` 抢走外层导航。

iframe 页面由 `/tools/<id>/` 反向代理加载，Caddy 去掉这个前缀。工具内 fetch、表单、图片、下载链接都使用相对路径，如 `api/upload`，不要用 `/api/upload`。需要子页面时，必须保持资源基路径正确，不依赖当前路径末段碰巧是根。

不要给页面设置禁止本平台 iframe 的 `X-Frame-Options: DENY` 或 frame-ancestors 策略。工具里的响应下载应使用合适的 Content-Type 与 Content-Disposition。中文文件名使用 ASCII filename + UTF-8 filename*，禁止直接把中文写进响应头。

返回首页只隐藏工具页面；同一会话再次进入保持 iframe 状态。关闭客户端会终止工具进程。不要把浏览器内存当作永久存储。

## 资源与打包

打包单位是整个工具目录，包含 assets、模板和额外 Python 模块。统一排除 .git、.venv、node_modules、__pycache__、隐藏目录、日志、CLAUDE.md、_mission.md、main.py.backup。工具源码目录不允许软链接；不要把上传结果或用户私密数据放进将被打包的源码目录。

新增工具不需要改 `desktop.py`、`main.py`、前端路由或 PyInstaller 参数。

## 验收

必须覆盖主页、子路径下的上传/拖拽/预览/下载、带中文文件名下载、返回后重新进入、重复点击只启动一次、首次依赖准备失败后的重试、退出后无遗留进程。WebView2 和浏览器共用页面，但下载、剪贴板等浏览器能力仍需实机验收。
