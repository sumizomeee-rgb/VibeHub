"""Developer-maintained catalog: the only source for UI, runtime and packaging."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tomllib

from pydantic import BaseModel, ConfigDict, Field, field_validator

from hub_core.config import Settings

IGNORED_DIRS = {"__pycache__", ".venv", ".git", ".claude", "node_modules", ".pytest_cache"}
IGNORED_FILES = {"CLAUDE.md", "_mission.md", "main.py.backup"}


class ToolSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(pattern=r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$", max_length=64)
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=240)
    icon: str = Field(default="tool", pattern=r"^[a-z0-9-]+$")

    @field_validator("id")
    @classmethod
    def portable_id(cls, value: str) -> str:
        if value in {"con", "prn", "aux", "nul", *[f"com{i}" for i in range(10)], *[f"lpt{i}" for i in range(10)]}:
            raise ValueError("Tool id is a reserved Windows filename")
        return value

    def project_dir(self, root: Path) -> Path:
        base = (root / "projects").resolve()
        path = base / self.id
        if path.is_symlink() or not path.resolve().is_relative_to(base):
            raise ValueError(f"Unsafe project path: {self.id}")
        return path

    def public(self) -> dict:
        return {**self.model_dump(), "url": f"/tools/{self.id}/"}


def project_files(directory: Path) -> list[Path]:
    """Include assets/subfolders, but never machine state or agent work files."""
    result = []
    for path in sorted(directory.rglob("*")):
        rel = path.relative_to(directory)
        if any(part in IGNORED_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if path.name in IGNORED_FILES or path.suffix in {".pyc", ".log"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported in tool bundles: {path}")
        if path.is_file():
            result.append(path)
    return result


def script_metadata(script: Path) -> dict:
    source = script.read_text(encoding="utf-8-sig")
    ast.parse(source, filename=str(script))  # Parse only; never import/execute for discovery.
    blocks = re.findall(r"(?m)^# /// script\r?\n((?:#(?: .*)?\r?\n)*)# ///\s*$", source)
    if len(blocks) != 1:
        raise ValueError(f"{script}: expected exactly one PEP 723 script block")
    text = "\n".join(line[2:] if line.startswith("# ") else "" for line in blocks[0].splitlines())
    metadata = tomllib.loads(text)
    deps = metadata.get("dependencies")
    if not isinstance(deps, list) or not all(isinstance(d, str) and d.strip() for d in deps):
        raise ValueError(f"{script}: dependencies must be a list of requirement strings")
    if "requires-python" in metadata and not isinstance(metadata["requires-python"], str):
        raise ValueError(f"{script}: requires-python must be a string")
    return metadata


class Catalog:
    def __init__(self, root: Path):
        self.root = root.resolve()
        data = json.loads((root / "tools.json").read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("Unsupported tools.json schema_version")
        self.tools = [ToolSpec.model_validate(item) for item in data["tools"]]
        self.by_id = {tool.id: tool for tool in self.tools}
        if len(self.by_id) != len(self.tools):
            raise ValueError("Duplicate tool id in tools.json")

    def get(self, tool_id: str) -> ToolSpec:
        try:
            return self.by_id[tool_id]
        except KeyError:
            raise KeyError("工具不存在") from None

    def validate(self) -> None:
        for tool in self.tools:
            directory = tool.project_dir(self.root)
            if not directory.is_dir():
                raise ValueError(f"Missing project directory: {tool.id}")
            project_files(directory)
            script_metadata(directory / "main.py")

    def prepare(self, tool: ToolSpec, settings: Settings) -> Path:
        directory = tool.project_dir(self.root)
        if not getattr(sys, "frozen", False):
            return directory
        # A content-addressed copy avoids writing under PyInstaller's temporary _MEI.
        # It also makes updating a bundle safe without overwriting old tool data.
        files = project_files(directory)
        digest = hashlib.sha256()
        for path in files:
            digest.update(path.relative_to(directory).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
        target = settings.data_dir / "apps" / tool.id / digest.hexdigest()[:20]
        marker = target / ".ready"
        if not marker.exists():
            if target.exists():
                shutil.rmtree(target)  # Incomplete, application-owned installation only.
            for path in files:
                destination = target / path.relative_to(directory)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
            marker.write_text("ready", encoding="utf-8")
        return target
