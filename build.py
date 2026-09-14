"""Single build entrypoint: identical frontend/catalog for web and Windows.

On Windows: build.bat
On Linux:   uv run --locked --group build --group test python build.py --target web
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from hub_core.catalog import Catalog, project_files
from hub_core.config import ROOT, Settings
from scripts.runtime_binaries import fetch_runtime, host_platform


def run(command: list[str], cwd: Path = ROOT):
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def build_frontend(*, install: bool = True):
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("Build requires Node.js 22 and npm (not needed by end users)")
    if install:
        run([npm, "ci"], ROOT / "frontend")
    run([npm, "run", "build"], ROOT / "frontend")


def copy_projects(catalog: Catalog, destination: Path):
    for tool in catalog.tools:
        directory = tool.project_dir(catalog.root)
        for path in project_files(directory):
            target = destination / "projects" / tool.id / path.relative_to(directory)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def archive_web(root: Path):
    # A Windows-generated web ZIP must keep Linux runtime files executable.
    with zipfile.ZipFile(ROOT / "release/VibeHub-web.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            executable = relative == "start.sh" or relative in {"bin/linux-x64/uv", "bin/linux-x64/caddy"}
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if executable else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with path.open("rb") as source, archive.open(info, "w") as target:
                shutil.copyfileobj(source, target)


def build_web(catalog: Catalog) -> Path:
    root = ROOT / "release/web"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for filename in ("main.py", "pyproject.toml", "uv.lock", "tools.json", "start.bat", "start.sh", "README.md", ".python-version"):
        shutil.copy2(ROOT / filename, root / filename)
    shutil.copytree(ROOT / "hub_core", root / "hub_core", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "frontend/dist", root / "frontend/dist")
    copy_projects(catalog, root)
    for target in ("windows-x64", "linux-x64"):
        binaries = fetch_runtime(ROOT, target)
        shutil.copytree(binaries, root / "bin" / target)
    (root / "start.sh").chmod(0o755)
    archive_web(root)
    return root


def write_manifest(executable: Path, version: str) -> dict:
    with executable.open("rb") as file:
        checksum = hashlib.file_digest(file, "sha256").hexdigest()
    result = {"version": version, "platform": "windows-x64", "filename": executable.name,
              "bytes": executable.stat().st_size, "sha256": checksum}
    temporary = executable.parent / "latest.json.tmp"
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(executable.parent / "latest.json")
    return result


def build_windows(catalog: Catalog) -> Path:
    if host_platform() != "windows-x64":
        raise RuntimeError("Windows exe must be built on Windows; use --target web here")
    stage = ROOT / "build/desktop-resources"
    if stage.exists(): shutil.rmtree(stage)
    stage.mkdir(parents=True)
    copy_projects(catalog, stage)
    binaries = fetch_runtime(ROOT, "windows-x64")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
               "--name", "VibeHub", "--distpath", str(ROOT / "release/windows"),
               "--workpath", str(ROOT / "build/pyinstaller"), "--specpath", str(ROOT / "build"),
               "--paths", str(ROOT), "--collect-all", "webview", "--collect-all", "pythonnet",
               "--hidden-import", "uvicorn.logging", "--hidden-import", "uvicorn.loops.auto",
               "--hidden-import", "uvicorn.protocols.http.auto", "--hidden-import", "uvicorn.protocols.websockets.auto",
               "--hidden-import", "uvicorn.lifespan.on"]
    for source, target in [(ROOT / "frontend/dist", "frontend/dist"), (ROOT / "tools.json", "."),
                           (ROOT / "pyproject.toml", "."), (stage / "projects", "projects")]:
        command += ["--add-data", f"{source}{os.pathsep}{target}"]
    for name in ("uv.exe", "caddy.exe"):
        command += ["--add-binary", f"{binaries / name}{os.pathsep}bin/windows-x64"]
    if (binaries / "licenses").exists():
        command += ["--add-data", f"{binaries / 'licenses'}{os.pathsep}licenses/runtime"]
    command.append(str(ROOT / "desktop.py"))
    run(command)
    executable = ROOT / "release/windows/VibeHub.exe"
    write_manifest(executable, Settings().version)
    return executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["all", "web", "windows"], default="all" if os.name == "nt" else "web")
    parser.add_argument("--skip-install", action="store_true", help="Reuse existing frontend node_modules for local iteration")
    args = parser.parse_args()
    if args.target in {"all", "windows"} and os.name != "nt":
        parser.error("Windows packaging requires Windows; use --target web")
    catalog = Catalog(ROOT)
    catalog.validate()
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    build_frontend(install=not args.skip_install)
    web = build_web(catalog) if args.target in {"all", "web"} else None
    if args.target in {"all", "windows"}:
        executable = build_windows(catalog)
        if web:
            shutil.copytree(executable.parent, web / "release/windows", dirs_exist_ok=True)
            archive_web(web)
    print(f"Build complete: {ROOT / 'release'}")


if __name__ == "__main__":
    main()
