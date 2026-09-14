# VibeHub contributor / Agent guide

## Product boundary
VibeHub is a curated tool collection, not an AI generator or a user-facing hosting manager.
Only ship homepage -> open tool -> use tool -> return home. Do not reintroduce build prompts,
import/scan dialogs, admin controls, editable registries, or arbitrary shell execution APIs.

## One source of truth
- `tools.json` + `ToolSpec`: metadata for homepage, runtime and packaging.
- `ToolHost.jsx`: all shared navigation, startup/retry UI and per-session iframe retention.
- `Application` / `ToolService`: identical runtime on web and desktop.
- `desktop.py`: window and browser-specific configuration only. Never duplicate tool logic here.
- `build.py`: same frontend build and catalog for both outputs. `build.bat` is the Windows entry.

## Safe changes
Preserve existing tool code and assets unless explicitly changing that tool. Adding a tool means
adding its directory, its uv script lock, one catalog entry and its tests. Follow docs/TOOL_SPEC.md.
Never write persistent state into the bundle or PyInstaller _MEI. Never kill by process name or
occupied port. No arbitrary tool paths from HTTP; resolve every tool through the catalog.

## Validation
Use Python 3.12, Node 22 and uv. Commit uv.lock and frontend/package-lock.json.
`uv run --locked --group test python -m unittest discover -s tests -v`
`cd frontend && npm ci && npm run build`
`uv run --locked --group build --group test python build.py --target web` (Linux)
`build.bat` (Windows: web + onefile exe)
`uv run --locked --group test python -m scripts.integration_check`
Windows: test `VibeHub.exe --smoke-test --report <path>` and `--gui-smoke-test` separately.
Do not claim Windows validation based solely on a Linux build or mocked subprocess tests.
Do not commit generated release files, caches or user logs.

Dependency maintenance is explicit: change constraints, run `uv lock`, regenerate affected
`uv lock --script projects/<id>/main.py`, and commit the results. Normal builds use --locked.
