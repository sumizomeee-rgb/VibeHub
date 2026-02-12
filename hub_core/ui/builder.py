import asyncio
import logging
import traceback
from datetime import datetime

from nicegui import ui

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.claude_agent import generate_tool_code, fix_tool_code, generate_test_code, run_test
from hub_core.guard_agent import guard_check
from hub_core.ui.theme import apply_theme

log = logging.getLogger("vibehub.builder")

# 生成代码快照目录，方便事后排查
_SNAPSHOT_DIR = config.DATA_DIR / "logs" / "snapshots"


def _save_snapshot(slug: str, label: str, content: str):
    """Save a code snapshot for post-mortem debugging."""
    _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    path = _SNAPSHOT_DIR / f"{slug}_{ts}_{label}.py"
    path.write_text(content, encoding="utf-8")
    log.info(f"[{slug}] Snapshot saved: {path.name}")


# ---- JS helpers ----

_JS_REQUEST_NOTIFICATION = """
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
"""

_JS_SET_TITLE = """document.title = '%TITLE%';"""

_JS_DEPLOY_SUCCESS = """
(function(name) {
    // Browser notification (background tab)
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('VibeHub', { body: name + ' 部署成功!' });
    }
    // Title flash
    var orig = document.title;
    var on = true;
    var iv = setInterval(function() {
        document.title = on ? '✅ 部署成功! - VibeHub' : orig;
        on = !on;
    }, 800);
    setTimeout(function() { clearInterval(iv); document.title = orig; }, 10000);
    // In-page toast
    vhToast('success', '部署成功', name + ' 已上线，可以使用了', 8000);
})('%NAME%');
"""

_JS_DEPLOY_FAIL = """
(function(msg) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('VibeHub', { body: '部署失败' });
    }
    document.title = '❌ 部署失败 - VibeHub';
    setTimeout(function() { document.title = 'VibeHub'; }, 8000);
    vhToast('error', '部署失败', msg || '请查看日志了解详情', 10000);
})('%MSG%');
"""


# ---- Step definitions for progress stepper ----
STEPS = [
    ("审核需求", "policy"),
    ("生成代码", "code"),
    ("单元测试", "science"),
    ("启动服务", "dns"),
    ("注册路由", "route"),
    ("完成", "check_circle"),
]


def create_builder(edit_slug: str | None = None):
    """构建台页面：需求输入 → AI 生成 → 测试 → 部署"""

    existing_tool = registry.get_tool(edit_slug) if edit_slug else None
    existing_code = ""
    if existing_tool:
        script_path = config.PROJECTS_DIR / edit_slug / "main.py"
        if script_path.exists():
            existing_code = script_path.read_text(encoding="utf-8")

    apply_theme()

    # ---- 请求浏览器通知权限 ----
    ui.run_javascript(_JS_REQUEST_NOTIFICATION)

    # ---- Header ----
    with ui.header().classes("items-center justify-between px-6 vh-header"):
        with ui.row().classes("items-center gap-4"):
            with ui.row().classes("items-center gap-2 cursor-pointer").on(
                "click", lambda: ui.navigate.to("/")
            ):
                ui.icon("hub", size="30px").classes("text-white")
                ui.label("VibeHub").classes(
                    "text-2xl font-bold text-white tracking-tight"
                )
        ui.button(
            "返回看板", icon="arrow_back", on_click=lambda: ui.navigate.to("/")
        ).props("flat text-color=white no-caps").style(
            "font-weight: 500; border-radius: 10px;"
        )

    # ---- Main Content ----
    with ui.column().classes("w-full max-w-3xl mx-auto p-8 gap-6"):

        # 标题区
        if edit_slug:
            with ui.row().classes("items-center gap-3 vh-fade-in"):
                with ui.element("div").style(
                    "width:44px; height:44px; border-radius:12px; "
                    "background: linear-gradient(135deg, #fef3c7, #fde68a); "
                    "display:flex; align-items:center; justify-content:center;"
                ):
                    ui.icon("edit", size="22px").classes("text-amber-600")
                with ui.column().classes("gap-0"):
                    ui.label(
                        f"编辑 {existing_tool.get('display_name', edit_slug) if existing_tool else edit_slug}"
                    ).classes("text-2xl font-bold text-slate-800")
                    ui.label("修改需求后重新部署").classes("text-sm text-slate-400")
        else:
            with ui.row().classes("items-center gap-3 vh-fade-in"):
                with ui.element("div").style(
                    "width:44px; height:44px; border-radius:12px; "
                    "background: linear-gradient(135deg, #e0e7ff, #c7d2fe); "
                    "display:flex; align-items:center; justify-content:center;"
                ):
                    ui.icon("auto_awesome", size="22px").classes("text-indigo-500")
                with ui.column().classes("gap-0"):
                    ui.label("创建新工具").classes("text-2xl font-bold text-slate-800")
                    ui.label("描述你想要的工具，AI 会自动生成、测试并部署").classes(
                        "text-sm text-slate-400"
                    )

        # ---- 需求输入卡片 ----
        with ui.card().classes("w-full vh-card").props("flat"):
            with ui.card_section().classes("gap-4"):
                if edit_slug:
                    prompt_placeholder = "描述需要修改或新增的功能..."
                else:
                    prompt_placeholder = "例如：做一个 JSON 格式化工具，支持压缩和美化..."

                user_input = ui.textarea(
                    label="需求描述", placeholder=prompt_placeholder
                ).classes("w-full vh-input").props("outlined autogrow rows=4")

                # 提示标签
                with ui.row().classes("gap-2 flex-wrap"):
                    for hint in ["数据处理", "文件转换", "文本工具", "可视化", "表单生成"]:
                        ui.button(
                            hint,
                            on_click=lambda h=hint: user_input.set_value(
                                user_input.value + (" " if user_input.value else "") + h
                            ),
                        ).props("flat dense size=sm no-caps color=grey-7").style(
                            "border: 1px solid #e2e8f0; border-radius: 8px; "
                            "font-size: 12px; padding: 2px 10px;"
                        )

        # 如果是编辑模式，显示当前代码
        if existing_code:
            with ui.expansion("查看当前代码", icon="code").classes("w-full").style(
                "border: 1px solid #e2e8f0; border-radius: 16px;"
            ):
                ui.code(existing_code, language="python").classes(
                    "w-full max-h-80 overflow-auto"
                )

        # ---- 步骤进度条 ----
        step_container = ui.row().classes(
            "w-full items-center vh-stepper hidden"
        )
        step_items: list = []  # [(icon_div, label, connector)]
        with step_container:
            for i, (label, icon_name) in enumerate(STEPS):
                if i > 0:
                    connector = ui.element("div").classes("vh-step-connector")
                else:
                    connector = None

                with ui.column().classes("items-center gap-1 vh-step-pending").style(
                    "min-width: 56px;"
                ) as step_col:
                    with ui.element("div").classes("vh-step-icon") as icon_div:
                        ui.icon(icon_name, size="20px")
                    ui.label(label).classes("text-xs font-medium text-slate-400")

                step_items.append((step_col, icon_div, connector))

        def _set_step(index: int):
            """Highlight the active step in the progress bar."""
            step_container.classes(remove="hidden")
            for i, (col, icon_div, connector) in enumerate(step_items):
                # Remove old state classes
                col.classes(remove="vh-step-pending vh-step-active vh-step-done")
                if connector:
                    connector.classes(
                        remove="vh-step-connector-done vh-step-connector-active"
                    )

                if i < index:
                    col.classes(add="vh-step-done")
                    if connector:
                        connector.classes(add="vh-step-connector-done")
                elif i == index:
                    col.classes(add="vh-step-active")
                    if connector:
                        connector.classes(add="vh-step-connector-active")
                else:
                    col.classes(add="vh-step-pending")

        def _complete_steps():
            for col, icon_div, connector in step_items:
                col.classes(remove="vh-step-pending vh-step-active")
                col.classes(add="vh-step-done")
                if connector:
                    connector.classes(add="vh-step-connector-done")

        # 进度日志区（终端风格）
        log_area = ui.log(max_lines=50).classes("w-full h-64 hidden vh-terminal")

        # 结果区
        result_container = ui.column().classes("w-full")

        # ---- 部署逻辑 ----
        async def do_deploy():
            text = user_input.value.strip()
            if not text:
                ui.run_javascript(
                    "vhToast('error', '请输入需求', '描述你想要的工具功能', 4000)"
                )
                return

            log_area.classes(remove="hidden")
            log_area.clear()
            result_container.clear()

            # 按钮变为 loading 状态
            deploy_btn.disable()
            deploy_btn.props(add="loading")
            deploy_btn.text = "部署中..."

            # 更新 title
            ui.run_javascript(
                _JS_SET_TITLE.replace("%TITLE%", "⏳ 部署中... - VibeHub")
            )

            try:
                # Step 1: Guard 过滤（编辑模式跳过）
                _set_step(0)
                if edit_slug:
                    slug = edit_slug
                    display_name = (
                        existing_tool.get("display_name", edit_slug)
                        if existing_tool
                        else edit_slug
                    )
                    log_area.push(f"✏️  编辑模式 → {display_name} ({slug})")
                else:
                    log_area.push("🔍  正在审核需求...")
                    is_valid, guard_msg = (
                        await asyncio.get_event_loop().run_in_executor(
                            None, guard_check, text
                        )
                    )

                    if not is_valid:
                        log_area.push(f"❌  需求被拒绝：{guard_msg}")
                        _safe_js_fail(f"需求被拒绝：{guard_msg[:60]}")
                        return

                    slug, display_name = guard_msg.split("|", 1)
                    log_area.push(f"✅  需求审核通过 → {display_name} ({slug})")

                # Step 2: 生成代码
                _set_step(1)
                log_area.push("🤖  正在调用 AI 生成代码...")
                code = await asyncio.get_event_loop().run_in_executor(
                    None, generate_tool_code, text, existing_code or None
                )
                log_area.push(f"✅  代码生成完成 ({len(code)} 字符)")
                _save_snapshot(slug, "gen", code)

                # Step 3: 单元测试
                _set_step(2)
                log_area.push("🧪  正在生成测试脚本...")
                test_code = await asyncio.get_event_loop().run_in_executor(
                    None, generate_test_code, code
                )
                _save_snapshot(slug, "test", test_code)
                log_area.push("🧪  正在执行测试...")

                # 先写入工具代码（测试需要读取）
                tool_dir = config.PROJECTS_DIR / slug
                tool_dir.mkdir(parents=True, exist_ok=True)
                script_path = tool_dir / "main.py"
                script_path.write_text(code, encoding="utf-8")

                passed, test_log = await asyncio.get_event_loop().run_in_executor(
                    None, run_test, slug, test_code
                )

                # 自愈循环
                retries = 0
                while not passed and retries < config.MAX_HEAL_RETRIES:
                    retries += 1
                    log_area.push(f"⚠️  测试未通过 (第{retries}次修复中...)")
                    log_area.push(f"    错误: {test_log[:200]}")

                    code = await asyncio.get_event_loop().run_in_executor(
                        None, fix_tool_code, code, test_log
                    )
                    _save_snapshot(slug, f"fix{retries}", code)
                    script_path.write_text(code, encoding="utf-8")

                    test_code = await asyncio.get_event_loop().run_in_executor(
                        None, generate_test_code, code
                    )
                    passed, test_log = await asyncio.get_event_loop().run_in_executor(
                        None, run_test, slug, test_code
                    )

                if passed:
                    log_area.push("✅  测试通过!")
                else:
                    log_area.push(
                        f"⚠️  测试仍未通过（已重试{config.MAX_HEAL_RETRIES}次），继续部署..."
                    )

                # Step 4: 启动工具
                _set_step(3)
                log_area.push("🚀  正在启动工具...")

                # 编辑模式先停旧进程
                if edit_slug:
                    process_manager.stop_tool(edit_slug)
                    await caddy_gateway.remove_route(edit_slug)

                pid, port = process_manager.start_tool(slug)
                ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)

                if not ready:
                    err_log = process_manager.get_tool_log(slug, tail=20)
                    log_area.push(f"❌  工具启动失败:\n{err_log}")
                    if edit_slug:
                        registry.set_status(slug, "error")
                    _safe_js_fail("工具启动失败，请检查日志")
                    return

                # Step 5: 注册路由
                _set_step(4)
                log_area.push("🔗  正在注册网关路由...")
                await caddy_gateway.add_route(slug, port)

                # Step 6: 完成
                _set_step(5)
                _complete_steps()
                registry.register_tool(
                    slug,
                    display_name,
                    str(config.PROJECTS_DIR / slug / "main.py"),
                )
                log_area.push("✅  部署完成!")

                # ---- 成功通知 (in-page toast + background notification) ----
                safe_name = display_name.replace("'", "\\'")
                ui.run_javascript(
                    _JS_DEPLOY_SUCCESS.replace("%NAME%", safe_name)
                )

                # ---- 成功结果卡片 ----
                tool_url = f"/tools/{slug}/"
                with result_container:
                    with ui.card().classes("w-full vh-celebrate").props("flat").style(
                        "background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%); "
                        "border: 1px solid #6ee7b7; border-radius: 20px; "
                        "overflow: visible; position: relative;"
                    ):
                        with ui.card_section().classes(
                            "items-center w-full py-8 gap-4"
                        ):
                            # 大图标
                            with ui.element("div").classes(
                                "vh-celebrate-icon"
                            ).style(
                                "width: 72px; height: 72px; border-radius: 20px; "
                                "background: linear-gradient(135deg, #10b981, #34d399); "
                                "display: flex; align-items: center; justify-content: center; "
                                "box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3); "
                                "margin: 0 auto;"
                            ):
                                ui.icon("check", size="36px").classes("text-white")

                            ui.label(display_name).classes(
                                "text-2xl font-bold text-emerald-800"
                            ).style("text-align: center;")
                            ui.label("部署成功，工具已上线").classes(
                                "text-emerald-600 font-medium"
                            )

                            with ui.row().classes("gap-3 mt-3 justify-center"):
                                ui.button(
                                    "打开工具",
                                    icon="open_in_new",
                                    on_click=lambda u=tool_url: ui.navigate.to(
                                        u, new_tab=True
                                    ),
                                ).classes("vh-btn-primary").props(
                                    "unelevated no-caps"
                                ).style(
                                    "background: linear-gradient(135deg, #10b981, #059669) !important; "
                                    "box-shadow: 0 4px 14px rgba(16,185,129,0.35) !important;"
                                )
                                ui.button(
                                    "返回看板",
                                    icon="dashboard",
                                    on_click=lambda: ui.navigate.to("/"),
                                ).classes("vh-btn-outline").props(
                                    "outline no-caps color=grey-8"
                                )
                                ui.button(
                                    "再建一个",
                                    icon="add",
                                    on_click=lambda: ui.navigate.to("/builder"),
                                ).classes("vh-btn-outline").props(
                                    "outline no-caps color=grey-8"
                                )

                # 触发 confetti
                ui.run_javascript(
                    "setTimeout(function(){ "
                    "var el = document.querySelector('.vh-celebrate-icon'); "
                    "if(el) vhConfetti(el); "
                    "}, 300);"
                )

                # 滚动到结果区
                await ui.run_javascript(
                    "window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})"
                )

                # 按钮变为完成状态
                deploy_btn.text = "部署完成"
                deploy_btn.props(remove="loading")
                return

            except Exception as e:
                log.error(f"Deploy error: {e}\n{traceback.format_exc()}")
                log_area.push(f"❌  部署异常: {e}")
                _safe_js_fail(str(e)[:80])
            finally:
                deploy_btn.props(remove="loading")
                deploy_btn.enable()
                if deploy_btn.text == "部署中...":
                    deploy_btn.text = "重新部署"

        def _safe_js_fail(msg: str):
            """Send failure toast, escaping quotes for JS."""
            safe = msg.replace("\\", "\\\\").replace("'", "\\'")
            ui.run_javascript(_JS_DEPLOY_FAIL.replace("%MSG%", safe))

        # ---- 部署按钮 ----
        deploy_btn = ui.button(
            "开始部署",
            icon="rocket_launch",
            on_click=do_deploy,
        ).classes("w-full mt-2 vh-btn-primary").props(
            "size=lg unelevated no-caps"
        ).style("height: 52px; font-size: 16px;")
