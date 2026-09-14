"""Shared startup/shutdown. Desktop adds a window, not a second server implementation."""
from dataclasses import replace
import logging
from logging.handlers import RotatingFileHandler
import socket
import sys
import threading
import time

import uvicorn

from hub_core.api_adapter import create_app
from hub_core.child_process import InstanceLock
from hub_core.config import Settings
from hub_core.caddy_gateway import free_port


class Application:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lock = InstanceLock(settings.data_dir / "instance.lock")
        self.socket = None
        self.server = None
        self.thread = None
        self.error = None
        self.handler = None

    @property
    def url(self) -> str:
        host = "127.0.0.1" if self.settings.host == "0.0.0.0" else self.settings.host
        return f"http://{host}:{self.settings.port}/"

    def start(self):
        self.lock.acquire()
        try:
            logs = self.settings.data_dir / "logs"
            logs.mkdir(parents=True, exist_ok=True)
            self.handler = RotatingFileHandler(logs / "hub.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
            self.handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
            logging.getLogger("vibehub").setLevel(logging.INFO)
            logging.getLogger("vibehub").addHandler(self.handler)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(("127.0.0.1", 0))  # Keep this reservation until Uvicorn owns it.
            self.socket.listen(128)
            self.settings = replace(self.settings, hub_port=self.socket.getsockname()[1], port=self.settings.port or free_port())
            self.app = create_app(self.settings)
            config = uvicorn.Config(self.app, log_config=None, access_log=False, timeout_graceful_shutdown=15)
            self.server = uvicorn.Server(config)

            def run():
                try:
                    self.server.run(sockets=[self.socket])
                except BaseException as error:
                    self.error = error

            self.thread = threading.Thread(target=run, name="vibehub-http", daemon=True)
            self.thread.start()
            deadline = time.monotonic() + 25
            while not self.server.started:
                if self.error or not self.thread.is_alive():
                    raise RuntimeError("VibeHub 服务启动失败，请查看本机 logs 目录") from self.error
                if time.monotonic() > deadline:
                    raise TimeoutError("VibeHub 服务启动超时")
                time.sleep(0.05)
            return self
        except BaseException:
            self.stop()
            raise

    def stop(self):
        try:
            if self.server:
                self.server.should_exit = True
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=25)
            if self.thread and self.thread.is_alive():
                self.server.force_exit = True
                self.app.state.tools.runner.emergency_stop()
                child = self.app.state.gateway.child
                if child:
                    child.stop()
                self.thread.join(timeout=5)
            if self.socket:
                self.socket.close()
                self.socket = None
        finally:
            if self.handler:
                logging.getLogger("vibehub").removeHandler(self.handler)
                self.handler.close()
                self.handler = None
            self.lock.release()

    def __enter__(self):
        return self.start()

    def __exit__(self, *_):
        self.stop()
