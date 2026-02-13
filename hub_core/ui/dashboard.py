import asyncio

from nicegui import ui

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.ui.theme import apply_theme

# 排序选项
SORT_OPTIONS = {
    "创建时间": "created_at",
    "名称": "display_name",
    "使用量": "click_count",
}


def create_dashboard():
    """总看板页面：卡片式展示所有已部署工具"""

    apply_theme()

    # ---- 搜索/排序状态 ----
    search_state = {"query": "", "sort": "创建时间"}

    async def refresh_cards():
        cards_container.clear()
        tools = registry.list_tools()

        # 搜索过滤
        query = search_state["query"].strip().lower()
        if query:
            tools = [
                t for t in tools
                if query in t.get("display_name", "").lower()
                or query in t.get("slug", "").lower()
            ]

        # 排序
        sort_key = SORT_OPTIONS.get(search_state["sort"], "created_at")
        if sort_key == "display_name":
            tools.sort(key=lambda t: t.get("display_name", "").lower())
        elif sort_key == "click_count":
            tools.sort(key=lambda t: t.get("click_count", 0), reverse=True)
        else:
            tools.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        with cards_container:
            if not tools and not query:
                # ---- Empty State ----
                with ui.column().classes("w-full items-center justify-center py-20 vh-fade-in"):
                    with ui.element("div").classes("vh-empty-icon"):
                        ui.icon("auto_awesome", size="52px").style(
                            "color: var(--vh-primary-light);"
                        )
                    ui.label("还没有部署任何工具").classes(
                        "text-xl font-semibold mt-8"
                    ).style("color: var(--vh-text);")
                    ui.label("描述你想要的工具，AI 帮你生成并一键上线").classes(
                        "text-sm mt-2"
                    ).style("color: var(--vh-text-muted);")
                    ui.button(
                        "创建第一个工具",
                        icon="add",
                        on_click=lambda: ui.navigate.to("/builder"),
                    ).classes("mt-6 vh-btn-primary").props("unelevated size=lg no-caps")
                return

            if not tools and query:
                with ui.column().classes("w-full items-center justify-center py-16 vh-fade-in"):
                    ui.icon("search_off", size="48px").style("color: var(--vh-text-muted);")
                    ui.label("没有找到匹配的工具").classes(
                        "text-lg font-medium mt-4"
                    ).style("color: var(--vh-text-secondary);")
                    ui.label(f"搜索 \"{search_state['query']}\" 无结果").classes(
                        "text-sm mt-1"
                    ).style("color: var(--vh-text-muted);")
                return

            # Bento Grid: running tools span 2 columns
            with ui.element("div").classes("w-full vh-responsive-grid").style(
                "display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;"
            ):
                for idx, tool in enumerate(tools):
                    slug = tool["slug"]
                    name = tool.get("display_name", slug)
                    status = tool.get("status", "stopped")
                    click_count = tool.get("click_count", 0)
                    alive = process_manager.is_tool_alive(slug)

                    # 状态判定
                    if status == "active" and alive:
                        dot_class = "vh-status-dot vh-status-running"
                        badge_class = "vh-badge vh-badge-green"
                        status_text = "运行中"
                        card_status_class = "vh-card-running"
                    elif status == "error":
                        dot_class = "vh-status-dot vh-status-error"
                        badge_class = "vh-badge vh-badge-red"
                        status_text = "异常"
                        card_status_class = "vh-card-error"
                    else:
                        dot_class = "vh-status-dot vh-status-stopped"
                        badge_class = "vh-badge vh-badge-grey"
                        status_text = "已停止"
                        card_status_class = "vh-card-stopped"

                    # Bento: running tools get featured (span 2)
                    bento_style = ""
                    if status == "active" and alive:
                        bento_style = "grid-column: span 2;"

                    with ui.card().classes(
                        f"w-full vh-card {card_status_class}"
                    ).props("flat").style(
                        f"animation: staggerIn 0.4s cubic-bezier(0.16,1,0.3,1) {idx * 0.06}s both; {bento_style}"
                    ):
                        with ui.card_section():
                            # 头部：名称 + 改名 + 状态
                            with ui.row().classes("items-center justify-between w-full"):
                                with ui.row().classes("items-center gap-3"):
                                    ui.html(f'<span class="{dot_class}"></span>')
                                    ui.label(name).classes(
                                        "text-base font-semibold"
                                    ).style("color: var(--vh-text);")

                                    async def do_rename(
                                        s=slug, n=name, lbl=None
                                    ):
                                        with ui.dialog() as dlg, ui.card().style(
                                            "min-width: 340px; border-radius: 16px; "
                                            "background: var(--vh-surface); "
                                            "box-shadow: inset 0 0 0 1px var(--vh-glass-border), var(--vh-shadow-xl);"
                                        ):
                                            ui.label("重命名工具").classes(
                                                "text-lg font-semibold"
                                            ).style("color: var(--vh-text);")
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
                                                    "flat no-caps"
                                                ).style("color: var(--vh-text-secondary);")

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
                                        "flat dense round size=xs"
                                    ).style(
                                        "color: var(--vh-text-muted);"
                                    ).tooltip("重命名")

                                ui.html(f'<span class="{badge_class}">{status_text}</span>')

                            # 元信息
                            with ui.row().classes("items-center gap-2 mt-3"):
                                ui.icon("link", size="14px").style("color: var(--vh-text-muted);")
                                ui.label(f"/tools/{slug}/").classes(
                                    "text-xs font-mono"
                                ).style("color: var(--vh-text-muted);")
                            with ui.row().classes("items-center gap-4 mt-1"):
                                with ui.row().classes("items-center gap-1"):
                                    ui.icon("schedule", size="14px").style("color: var(--vh-text-muted);")
                                    ui.label(f"{tool.get('created_at', '未知')}").classes(
                                        "text-xs"
                                    ).style("color: var(--vh-text-muted);")
                                if click_count > 0:
                                    with ui.row().classes("items-center gap-1"):
                                        ui.icon("touch_app", size="14px").style("color: var(--vh-text-muted);")
                                        ui.label(f"{click_count} 次使用").classes(
                                            "text-xs"
                                        ).style("color: var(--vh-text-muted);")

                        # 分隔线
                        ui.element("div").classes("vh-divider")

                        # 操作按钮
                        with ui.card_actions().classes("px-4 py-3"):
                            with ui.row().classes("gap-2 w-full"):
                                if status == "active" and alive:
                                    def _open_tool(s=slug):
                                        registry.increment_click(s)
                                        ui.navigate.to(f"/tools/{s}/", new_tab=True)

                                    ui.button(
                                        "打开",
                                        icon="open_in_new",
                                        on_click=_open_tool,
                                    ).classes("vh-btn-ghost").props(
                                        "flat dense size=sm no-caps"
                                    )

                                ui.button(
                                    "编辑",
                                    icon="edit",
                                    on_click=lambda s=slug: ui.navigate.to(f"/builder/{s}"),
                                ).classes("vh-btn-ghost").props(
                                    "flat dense size=sm no-caps"
                                )

                                async def do_restart(s=slug):
                                    ui.run_javascript(
                                        f"vhToast('info', '重启中', '{s} 正在重启...', 4000)"
                                    )
                                    try:
                                        process_manager.stop_tool(s)
                                        await caddy_gateway.remove_route(s)
                                        pid, port = process_manager.start_tool(s)
                                        ready = await process_manager.wait_for_tool_ready(s, timeout=30.0)
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
                                    "flat dense size=sm no-caps"
                                ).style("color: var(--vh-warning) !important;")

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
                                    "flat dense round size=sm"
                                ).style("color: var(--vh-error) !important;")

    # ---- 页面布局 ----
    with ui.header().classes("items-center justify-between px-6 vh-header"):
        with ui.row().classes("items-center gap-4"):
            # Logo
            with ui.row().classes("items-center gap-2"):
                ui.icon("hub", size="30px").classes("vh-header-logo")
                ui.label("VibeHub").classes(
                    "text-2xl font-bold tracking-tight vh-header-logo"
                )
            # Divider
            ui.element("div").classes("vh-header-divider").style(
                "width:1px; height:24px; background: var(--vh-border);"
            )
            ui.label("AI 工具工坊").classes("text-sm font-medium").style(
                "color: var(--vh-text-muted);"
            )

        with ui.row().classes("gap-3"):
            # Theme toggle button
            ui.button(
                icon="dark_mode",
                on_click=lambda: ui.run_javascript("vhToggleTheme()"),
            ).props("flat round size=sm").classes(
                "vh-theme-toggle"
            ).style("color: var(--vh-text-secondary);").tooltip("切换主题")

            ui.button(
                icon="refresh", on_click=refresh_cards
            ).props(
                "flat round size=sm"
            ).style("color: var(--vh-text-secondary);").tooltip("刷新")
            ui.button(
                "新建工具", icon="add", on_click=lambda: ui.navigate.to("/builder")
            ).classes("vh-btn-header").props("no-caps unelevated")

    # ---- 搜索/排序工具栏 ----
    with ui.row().classes("w-full max-w-5xl mx-auto px-8 pt-8 pb-0 items-center gap-4").style(
        "flex-wrap: nowrap;"
    ):
        async def on_search(e):
            search_state["query"] = search_input.value or ""
            await refresh_cards()

        search_input = ui.input(
            placeholder="搜索工具...",
            on_change=on_search,
        ).classes("vh-input").props(
            "outlined dense clearable"
        ).style("flex: 1; min-width: 200px;")

        # 搜索图标前缀
        with search_input.add_slot("prepend"):
            ui.icon("search").style("color: var(--vh-text-muted);")

        async def on_sort(e):
            search_state["sort"] = sort_select.value or "创建时间"
            await refresh_cards()

        sort_select = ui.select(
            list(SORT_OPTIONS.keys()),
            value="创建时间",
            label="排序",
            on_change=on_sort,
        ).classes("vh-select").props(
            "outlined dense"
        ).style("min-width: 140px;")

    cards_container = ui.column().classes("w-full max-w-5xl mx-auto px-8 pt-4 pb-8")

    # 首次加载
    asyncio.ensure_future(refresh_cards())
