import socket


def find_free_port() -> int:
    """向操作系统申请一个空闲的随机端口（绑定 localhost，对外隐形）"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
