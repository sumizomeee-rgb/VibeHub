"""Windows shell. All tool behavior remains in the shared web application."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import sys
import time
import traceback

from hub_core.application import Application
from hub_core.config import Settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true", help="Test the frozen server and all bundled tool entrypoints without a GUI")
    parser.add_argument("--gui-smoke-test", action="store_true", help="Open WebView2, verify the homepage, and close automatically")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    settings = Settings.from_env(desktop=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    # A --windowed PyInstaller process has no stdout/stderr. Libraries still use them.
    if sys.stdout is None:
        sys.stdout = (settings.data_dir / "logs-desktop.txt").open("a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = sys.stdout
    try:
        with Application(settings) as application:
            if args.smoke_test:
                from hub_core.smoke import exercise_server
                report = exercise_server(application.url)
                if args.report:
                    args.report.parent.mkdir(parents=True, exist_ok=True)
                    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
                return
            import webview
            webview.settings["ALLOW_DOWNLOADS"] = True
            window = webview.create_window("VibeHub", application.url, width=1280, height=860, min_size=(760, 560))
            errors = []

            def verify_window():
                try:
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        if window.evaluate_js("document.querySelectorAll('[data-tool-card]').length") == len(application.app.state.tools.catalog.tools):
                            return
                        time.sleep(0.2)
                    raise RuntimeError("WebView2 homepage did not become ready")
                except Exception as error:
                    errors.append(str(error))
                finally:
                    window.destroy()

            webview.start(verify_window if args.gui_smoke_test else None,
                          gui="edgechromium" if os.name == "nt" else None,
                          private_mode=False, storage_path=str(settings.data_dir / "webview"))
            if errors:
                raise RuntimeError("; ".join(errors))
            if args.gui_smoke_test and args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps({"webview2_homepage": "passed"}), encoding="utf-8")
    except Exception as error:
        log = settings.data_dir / "desktop-error.log"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        if os.name == "nt" and not (args.smoke_test or args.gui_smoke_test):
            ctypes.windll.user32.MessageBoxW(None, f"启动失败：{error}\n\n日志：{log}\n请确认已安装 Microsoft Edge WebView2 Runtime。", "VibeHub", 0x10)
        traceback.print_exc()
        raise SystemExit(1) from error


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
