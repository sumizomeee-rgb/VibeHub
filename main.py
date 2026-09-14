"""Web entrypoint. Use desktop.py for the same application in a WebView2 window."""
import argparse
from dataclasses import replace
import signal
import threading

from hub_core.application import Application
from hub_core.config import Settings


def main():
    parser = argparse.ArgumentParser(description="VibeHub 工具合集")
    parser.add_argument("--host", default=None, help="默认仅本机；局域网部署使用 0.0.0.0")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    settings = Settings.from_env()
    if args.host:
        settings = replace(settings, host=args.host)
    if args.port is not None:
        settings = replace(settings, port=args.port)
    finished = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: finished.set())
    signal.signal(signal.SIGTERM, lambda *_: finished.set())
    with Application(settings) as app:
        print(f"VibeHub: {app.url}", flush=True)
        while not finished.wait(0.3):
            if not app.thread.is_alive():
                raise RuntimeError("VibeHub server stopped unexpectedly")


if __name__ == "__main__":
    main()
