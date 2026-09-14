"""Fetch pinned upstream binaries, validate checksums, and cache them locally."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request
import zipfile

UV_VERSION = "0.8.22"
CADDY_VERSION = "2.10.2"
SUPPORTED = ("windows-x64", "linux-x64")


def host_platform() -> str:
    machine = platform.machine().lower()
    if machine not in {"amd64", "x86_64"}:
        raise RuntimeError(f"Unsupported architecture: {machine}; currently x64 only")
    system = platform.system()
    if system not in {"Windows", "Linux"}:
        raise RuntimeError(f"Unsupported build platform: {system}")
    return "windows-x64" if system == "Windows" else "linux-x64"


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VibeHub-build"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def extract_file(archive: bytes, filename: str, zipped: bool) -> bytes:
    if zipped:
        with zipfile.ZipFile(io.BytesIO(archive)) as file:
            names = [name for name in file.namelist() if Path(name).name == filename]
            if len(names) != 1:
                raise ValueError(f"Expected exactly one {filename} in archive")
            return file.read(names[0])
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as file:
        members = [member for member in file.getmembers() if member.isfile() and Path(member.name).name == filename]
        if len(members) != 1:
            raise ValueError(f"Expected exactly one {filename} in archive")
        return file.extractfile(members[0]).read()


def fetch_runtime(root: Path, target: str) -> Path:
    if target not in SUPPORTED:
        raise ValueError(target)
    windows = target == "windows-x64"
    destination = root / "bin" / target
    destination.mkdir(parents=True, exist_ok=True)
    uv_archive = "uv-x86_64-pc-windows-msvc.zip" if windows else "uv-x86_64-unknown-linux-gnu.tar.gz"
    caddy_archive = f"caddy_{CADDY_VERSION}_{'windows' if windows else 'linux'}_amd64.{ 'zip' if windows else 'tar.gz'}"
    packages = [
        ("uv", UV_VERSION, f"https://github.com/astral-sh/uv/releases/download/{UV_VERSION}/{uv_archive}", uv_archive + ".sha256"),
        ("caddy", CADDY_VERSION, f"https://github.com/caddyserver/caddy/releases/download/v{CADDY_VERSION}/{caddy_archive}", f"caddy_{CADDY_VERSION}_checksums.txt"),
    ]
    for name, version, url, checksum_file in packages:
        path = destination / (name + (".exe" if windows else ""))
        stamp = path.with_suffix(path.suffix + ".json")
        try:
            old = json.loads(stamp.read_text())
            if old["version"] == version and hashlib.sha256(path.read_bytes()).hexdigest() == old["binary_sha256"]:
                continue
        except (OSError, KeyError, ValueError):
            pass
        print(f"Fetching {name} {version} ({target})", flush=True)
        checksum_url = url.rsplit("/", 1)[0] + "/" + checksum_file
        checksums = download(checksum_url).decode("utf-8")
        archive_name = url.rsplit("/", 1)[1]
        expected = None
        for line in checksums.splitlines():
            fields = line.split()
            if fields and (len(fields) == 1 or fields[-1].lstrip("*") == archive_name):
                expected = fields[0].lower()
                break
        if not expected or len(expected) not in {64, 128}:
            raise ValueError(f"No checksum for {archive_name}")
        archive = download(url)
        hasher = hashlib.sha256 if len(expected) == 64 else hashlib.sha512
        if hasher(archive).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {archive_name}")
        data = extract_file(archive, path.name, zipped=windows)
        # Preserve upstream redistribution notices alongside the bundled programs.
        notices = destination / "licenses" / name
        notices.mkdir(parents=True, exist_ok=True)
        if windows:
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                for item in bundle.namelist():
                    if Path(item).name.upper().startswith(("LICENSE", "NOTICE")) and not item.endswith("/"):
                        (notices / Path(item).name).write_bytes(bundle.read(item))
        else:
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
                for item in bundle.getmembers():
                    if item.isfile() and Path(item.name).name.upper().startswith(("LICENSE", "NOTICE")):
                        (notices / Path(item.name).name).write_bytes(bundle.extractfile(item).read())
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.chmod(0o755)
        temporary.replace(path)
        stamp.write_text(json.dumps({"version": version, "url": url, "archive_checksum": expected,
                                    "binary_sha256": hashlib.sha256(data).hexdigest()}, indent=2), encoding="utf-8")
    return destination


if __name__ == "__main__":
    fetch_runtime(Path(__file__).resolve().parent.parent, host_platform())
