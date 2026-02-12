import asyncio

from nicegui import ui

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.ui.theme import apply_theme


def create_dashboard():
    """总看板页面：卡片式展示所有已部署工具"""

    apply_theme()

    async def refresh_cards():
        cards_container.clear()
        tools = registry.list_tools()

        with cards_container:
            if not tools:
                # ---- Empty State ----
                with ui.column().classes("w-full items-center justify-center py-20 vh-fade-in"):
                    with ui.element("div").classes("vh-empty-icon"):
                        ui.icon("auto_awesome", size="52px").classes("text-indigo-400")
                    ui.label("还没有部署任何工具").classes(
                        "text-xl font-semibold text-slate-700 mt-8"
                    )
                    ui.label("描述你想要的工具，AI 帮你生成并一键上线").classes(
                        "text-sm text-slate-400 mt-2"
                    )
                    ui.button(
                        "创建第一个工具",
                        icon="add",
                        on_click=lambda: ui.navigate.to("/builder"),
                    ).classes("mt-6 vh-btn-primary").props("unelevated size=lg no-caps")
                return

            with ui.grid(columns=3).classes("w-full gap-6"):
                for tool in tools:
                    slug = tool["slug"]
                    name = tool.get("display_name", slug)
                    status = tool.get("status", "stopped")
                    alive = process_manager.is_tool_alive(slug)

                    # 状态判定
                    if status == "active" and alive:
                        dot_class = "vh-status-dot vh-status-running"
                        badge_class = "vh-badge vh-badge-green"
                        status_text = "运行中"
                    elif status == "error":
                        dot_class = "vh-status-dot vh-status-error"
                        badge_class = "vh-badge vh-badge-red"
                        status_text = "异常"
                    else:
                        dot_class = "vh-status-dot vh-status-stopped"
                        badge_class = "vh-badge vh-badge-grey"
                        status_text = "已停止"

                    with ui.card().classes("w-full vh-card").props("flat"):
                        with ui.card_section():
                            # 头部：名称 + 改名 + 状态
                            with ui.row().classes("items-center justify-between w-full"):
                                with ui.row().classes("items-center gap-3"):
                                    ui.html(f'<span class="{dot_class}"></span>')
                                    name_label = ui.label(name).classes(
                                        "text-base font-semibold text-slate-800"
                                    )

                                    async def do_rename(
                                        s=slug, n=name, lbl=None
                                    ):
                                        # lbl captured below
                                        rename_input = ui.input(
                                            value=n
                                        ).classes("vh-input").props(
                                            "outlined dense"
                                        )
                                        with ui.dialog() as dlg, ui.card().style(
                                            "min-width: 340px; border-radius: 16px;"
                                        ):
                                            ui.label("重命名工具").classes(
                                                "text-lg font-semibold text-slate-800"
                                            )
                                            rename_input = ui.input(
                                                label="显示名称", value=n
                                            ).classes("w-full vh-input mt-2").props(
                                                "outlined dense"
                                            )
                                            with ui.row().classes(
                                                "w-full justify-end gap-2 mt-4"
                                            ):
                                                ui.button(
                                                    "取消",
                                                    on_click=dlg.close,
                                                ).props(
                                                    "flat no-caps color=grey-7"
                                                )

                                                async def confirm_rename(
                                                    s=s, inp=rename_input
                                                ):
                                                    new = inp.value.strip()
                                                    if not new:
                                                        return
                                                    registry.rename_tool(s, new)
                                                    dlg.close()
                                                    ui.run_javascript(
                                                        f"vhToast('success','已重命名','{new}', 3000)"
                                                    )
                                                    await refresh_cards()

                                                ui.button(
                                                    "确定",
                                                    on_click=confirm_rename,
                                                ).classes("vh-btn-primary").props(
                                                    "unelevated no-caps"
                                                )
                                        dlg.open()

                                    ui.button(
                                        icon="edit",
                                        on_click=lambda s=slug, n=name: do_rename(s, n),
                                    ).props(
                                        "flat dense round size=xs color=grey-5"
                                    ).tooltip("重命名")

                                ui.html(f'<span class="{badge_class}">{status_text}</span>')

                            # 元信息
                            with ui.row().classes("items-center gap-2 mt-3"):
                                ui.icon("link", size="14px").classes("text-slate-300")
                                ui.label(f"/tools/{slug}/").classes(
                                    "text-xs text-slate-400 font-mono"
                                )
                            with ui.row().classes("items-center gap-2 mt-1"):
                                ui.icon("schedule", size="14px").classes("text-slate-300")
                                ui.label(f"{tool.get('created_at', '未知')}").classes(
                                    "text-xs text-slate-400"
                                )

                        # 操作按钮
                        with ui.card_actions().classes("px-4 pb-3"):
                            with ui.row().classes("gap-2 w-full"):
                                if status == "active" and alive:
                                    ui.button(
                                        "打开",
                                        icon="open_in_new",
                                        on_click=lambda s=slug: ui.navigate.to(
                                            f"/tools/{s}/", new_tab=True
                                        ),
                                    ).classes("vh-btn-ghost").props(
                                        "flat dense color=primary size=sm no-caps"
                                    )

                                ui.button(
                                    "编辑",
                                    icon="edit",
                                    on_click=lambda s=slug: ui.navigate.to(f"/builder/{s}"),
                                ).classes("vh-btn-ghost").props(
                                    "flat dense color=secondary size=sm no-caps"
                                )

                                async def do_restart(s=slug):
                                    ui.run_javascript(
                                        f"vhToast('info', '重启中', '{s} 正在重启...', 4000)"
                                    )
                                    try:
                                        process_manager.stop_tool(s)
                                        await caddy_gateway.remove_route(s)
                                        pid, port = process_manager.start_tool(s)
                                        ready = await process_manager.wait_for_tool_ready(s)
                                        if ready:
                                            await caddy_gateway.add_route(s, port)
                                            registry.set_status(s, "active")
                                            ui.run_javascript(
                                                f"vhToast('success', '重启成功', '{s} 已恢复运行')"
                                            )
                                        else:
                                            registry.set_status(s, "error")
                                            ui.run_javascript(
                                                f"vhToast('error', '重启失败', '{s} 启动后未就绪')"
                                            )
                                    except Exception as e:
                                        ui.run_javascript(
                                            f"vhToast('error', '重启失败', '{str(e)[:80]}')"
                                        )
                                    await refresh_cards()

                                ui.button(
                                    "重启",
                                    icon="refresh",
                                    on_click=lambda s=slug: do_restart(s),
                                ).classes("vh-btn-ghost").props(
                                    "flat dense color=warning size=sm no-caps"
                                )

                                # 删除按钮推到右侧
                                ui.space()

                                async def do_delete(s=slug):
                                    process_manager.stop_tool(s)
                                    await caddy_gateway.remove_route(s)
                                    registry.unregister_tool(s)
                                    ui.run_javascript(
                                        f"vhToast('info', '已删除', '{s} 已从看板移除')"
                                    )
                                    await refresh_cards()

                                ui.button(
                                    icon="delete_outline",
                                    on_click=lambda s=slug: do_delete(s),
                                ).classes("vh-btn-ghost").props(
                                    "flat dense round color=negative size=sm"
                                )

    # ---- 页面布局 ----
    with ui.header().classes("items-center justify-between px-6 vh-header"):
        with ui.row().classes("items-center gap-4"):
            # Logo
            with ui.row().classes("items-center gap-2"):
                ui.icon("hub", size="30px").classes("text-white")
                ui.label("VibeHub").classes(
                    "text-2xl font-bold text-white tracking-tight"
                )
            # Divider
            ui.element("div").style(
                "width:1px; height:24px; background:rgba(255,255,255,0.2);"
            )
            ui.label("AI 工具工坊").classes("text-sm text-white/70 font-medium")

        with ui.row().classes("gap-3"):
            ui.button(
                icon="refresh", on_click=refresh_cards
            ).classes("vh-btn-ghost").props(
                "flat round text-color=white size=sm"
            ).tooltip("刷新")
            ui.button(
                "新建工具", icon="add", on_click=lambda: ui.navigate.to("/builder")
            ).props("no-caps unelevated rounded").style(
                "background: rgba(255,255,255,0.15); color: white; "
                "backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.2); "
                "font-weight: 600; border-radius: 10px;"
            )

    cards_container = ui.column().classes("w-full max-w-5xl mx-auto p-8")

    # 首次加载
    asyncio.ensure_future(refresh_cards())
