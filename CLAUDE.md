# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibeHub is an AI-driven web tool automation platform. Users describe a tool in natural language, and the system generates Python web tool code via Claude CLI, tests it, deploys it as a subprocess, and routes traffic to it through Caddy reverse proxy — fully automated.

Primary language is Chinese (comments, logs, UI text, docs).

## Running the Project

```bash
# Start everything (Caddy + VibeHub) — Windows only
start.bat
```

The startup script checks for required external dependencies (Node.js, npm, Claude CLI, Git Bash, uv.exe, caddy.exe), builds the React frontend if needed (`npm install && npm run build`), initializes directories, opens firewall port 9529, starts Caddy, then launches the FastAPI app via `uv run main.py`.

There is no test suite or linter configured for the hub itself. Testing only exists as auto-generated scripts for individual tools during the build/deploy cycle.

## Architecture

**Request flow:** Browser → Caddy (0.0.0.0:9529) → FastAPI Hub (127.0.0.1:8080) or Tool subprocess (127.0.0.1:{dynamic port})

**Frontend:** React 18 + Vite + Tailwind CSS 4, built to `frontend/dist/`, served as static files by FastAPI with SPA fallback.

**Backend API layer (`api_adapter.py`):**
- `GET /api/tools` — tool list with live status
- `POST /api/tools/{slug}/start|stop|restart` — process control
- `DELETE /api/tools/{slug}` — delete tool
- `POST /api/build` — start build task, returns `task_id`
- `WebSocket /ws/build/{task_id}` — real-time build progress

**Tool creation pipeline (Builder page):**
1. Guard Agent (`guard_agent.py`) classifies user request via Claude CLI → `PASS|slug|display_name` or `REJECT|reason`
2. Claude Agent (`claude_agent.py`) generates a single-file FastAPI tool with PEP 723 inline metadata
3. Auto-generated test script validates the tool; failures trigger self-healing loop (up to `MAX_HEAL_RETRIES=3`)
4. Process Manager (`process_manager.py`) starts the tool via `uv run`, passing port as `PORT` env var
5. Caddy Gateway (`caddy_gateway.py`) registers route `/tools/{slug}/*` via Caddy Admin API (localhost:2019)
6. Registry (`registry.py`) persists tool metadata to `data/registry.json`

**Key ports:**
- 9529 — Caddy gateway (public-facing)
- 8080 — FastAPI hub (internal)
- 2019 — Caddy Admin API

## Key Conventions

- **Generated tools are single-file Python scripts** in `projects/{slug}/main.py` using PEP 723 inline dependency metadata, FastAPI + Uvicorn, binding to `127.0.0.1` on the port from `PORT` env var, with relative URLs for reverse proxy compatibility.
- **All Claude CLI calls use stdin piping** for prompt delivery to avoid Windows CMD quoting issues.
- **Async throughout** — httpx for HTTP, asyncio for coordination.
- **Process management uses psutil** for process-tree-level cleanup (killing child processes recursively).
- **Logging** uses `vibehub.*` logger namespace, outputs to both console and `data/logs/hub.log`. Tool logs go to `data/logs/tools/`.
- **Frontend** is React + Vite + Tailwind CSS with dual theme (light/dark), design tokens as CSS variables in `frontend/src/index.css`.
- **API adapter** (`hub_core/api_adapter.py`) wraps all backend modules as REST/WebSocket endpoints.
- **Build manager** (`hub_core/build_manager.py`) runs build tasks asynchronously with WebSocket progress push, per-slug locking, and heartbeat keepalive.

## External Dependencies (not pip-managed)

These binaries must be present for the system to work:
- `bin/uv.exe` — Python script runner (resolves PEP 723 deps)
- `bin/caddy.exe` — Reverse proxy with Admin API
- Claude CLI (`claude` on PATH) — requires Node.js, npm, Git Bash on Windows
