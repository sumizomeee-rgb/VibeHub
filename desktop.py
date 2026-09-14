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


def unique_download_path(output_dir: Path, suggested_path: str) -> Path:
    """Choose a visible output path without replacing an earlier result."""
    output_dir.mkdir(parents=True, exist_ok=True)
    name = Path(suggested_path).name or "download"
    target = output_dir / name
    stem, suffix = target.stem, target.suffix
    counter = 2
    while target.exists():
        target = output_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return target


def save_downloads_to(output_dir: Path):
    """Send tool results straight to the output folder instead of prompting.

    pywebview's EdgeChromium backend opens a native Save-As dialog for every
    download. Tools stream their results as attachments, so the browser version
    simply saves the file; the desktop must not add a step the web build lacks.
    """
    from webview.platforms import edgechromium

    def on_download_starting(self, sender, args):
        if not edgechromium.webview_settings["ALLOW_DOWNLOADS"]:
            args.Cancel = True
            return
        args.ResultFilePath = str(unique_download_path(output_dir, args.ResultFilePath))

    edgechromium.EdgeChrome.on_download_starting = on_download_starting


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true", help="Test the frozen server and all bundled tool entrypoints without a GUI")
    parser.add_argument("--gui-smoke-test", action="store_true", help="Open WebView2, verify the homepage, and close automatically")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    settings = Settings.from_env(desktop=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
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
            if os.name == "nt":
                save_downloads_to(settings.output_dir)
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
