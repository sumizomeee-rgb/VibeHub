"""Own only our child processes; never kill by executable name or occupied port."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading


_spawn_lock = threading.Lock()


def clean_environment() -> dict[str, str]:
    env = dict(os.environ)
    for name in ("LD_LIBRARY_PATH", "LIBPATH"):
        if name + "_ORIG" in env:
            env[name] = env[name + "_ORIG"]
        elif getattr(sys, "frozen", False):
            env.pop(name, None)
    # uv must not reuse the Hub's virtualenv or PyInstaller's internal interpreter.
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONHOME", None)
    if getattr(sys, "frozen", False):
        mei = str(getattr(sys, "_MEIPASS", ""))
        env["PATH"] = os.pathsep.join(p for p in env.get("PATH", "").split(os.pathsep) if not (mei and p.startswith(mei)))
        env.pop("PYTHONPATH", None)
    return env


class WindowsJob:
    """Kill descendants even if the GUI crashes; handle is intentionally not inherited."""
    def __init__(self):
        self.handle = None
        if os.name != "nt":
            return
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel = kernel
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]
        self.handle = kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def attach(self, proc: subprocess.Popen):
        if self.handle and not self.kernel.AssignProcessToJobObject(self.handle, wintypes.HANDLE(int(proc._handle))):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


class ChildProcess:
    def __init__(self, command: list[str], *, cwd: Path, log_file: Path, env: dict | None = None):
        self.job = WindowsJob()
        self.process = None
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log = log_file.open("ab", buffering=0)
        try:
            # PyInstaller modifies the Windows DLL search directory globally. Restore
            # the system search path just while creating an external process.
            with _spawn_lock:
                frozen_windows = os.name == "nt" and getattr(sys, "frozen", False)
                if frozen_windows:
                    ctypes.windll.kernel32.SetDllDirectoryW(None)
                try:
                    self.process = subprocess.Popen(
                        command, cwd=str(cwd), env=env or clean_environment(),
                        stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                        start_new_session=os.name != "nt",
                    )
                    self.job.attach(self.process)
                finally:
                    if frozen_windows:
                        ctypes.windll.kernel32.SetDllDirectoryW(str(sys._MEIPASS))
        except BaseException:
            self.stop()
            raise

    @property
    def alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def stop(self):
        proc = self.process
        if proc is not None:
            if os.name == "nt":
                # Closing the job handles all descendants, even when uv exited first.
                self.job.close()
                if proc.poll() is None:
                    proc.kill()
            else:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    proc.kill()
                proc.wait(timeout=3)
            # A parent may exit before its descendants finish handling SIGTERM.
            if os.name != "nt":
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.job.close()
        if getattr(self, "log", None):
            self.log.close()


class InstanceLock:
    def __init__(self, path: Path):
        self.path = path
        self.file = None

    def acquire(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a+b")
        try:
            # Windows denies reads of a region locked by another process. Inspect
            # the file length instead, and include setup in the failure cleanup.
            if os.fstat(self.file.fileno()).st_size == 0:
                self.file.write(b"0")
                self.file.flush()
            self.file.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.file.close()
            self.file = None
            raise RuntimeError("此数据目录已有 VibeHub 实例运行，请先关闭它。") from error

    def release(self):
        if self.file:
            if os.name == "nt":
                import msvcrt
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()
            self.file = None
