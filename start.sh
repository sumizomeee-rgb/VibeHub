#!/usr/bin/env bash
set -euo pipefail

VIBEHUB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$VIBEHUB_ROOT/bin:$PATH"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$VIBEHUB_ROOT/runtime}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$VIBEHUB_ROOT/caddy_data}"

resolve_cmd() {
  local env_value="$1"
  local local_path="$2"
  local command_name="$3"

  if [ -n "$env_value" ]; then
    printf '%s\n' "$env_value"
  elif [ -x "$local_path" ]; then
    printf '%s\n' "$local_path"
  else
    command -v "$command_name" || true
  fi
}

UV_CMD="$(resolve_cmd "${VIBEHUB_UV:-}" "$VIBEHUB_ROOT/bin/uv" "uv")"
CADDY_CMD="$(resolve_cmd "${VIBEHUB_CADDY:-}" "$VIBEHUB_ROOT/bin/caddy" "caddy")"

echo
echo "========================================"
echo "        VibeHub v2.0 Starting"
echo "========================================"
echo

ENV_OK=1
check_cmd() {
  local label="$1"
  local cmd="$2"
  if [ -z "$cmd" ]; then
    echo "  [X] $label not found"
    ENV_OK=0
  else
    echo "  [OK] $label found: $cmd"
  fi
}

warn_cmd() {
  local label="$1"
  local cmd="$2"
  local hint="$3"
  if [ -z "$cmd" ]; then
    echo "  [WARN] $label not found - $hint"
  else
    echo "  [OK] $label found: $cmd"
  fi
}

echo "[1/5] Checking environment..."
check_cmd "Node.js" "$(command -v node || true)"
check_cmd "npm" "$(command -v npm || true)"
warn_cmd "Claude CLI" "$(command -v claude || true)" "tool generation will be unavailable until installed"
check_cmd "uv" "$UV_CMD"
check_cmd "Caddy" "$CADDY_CMD"

if [ "$ENV_OK" != "1" ]; then
  echo
  echo "Environment check FAILED."
  echo "Install missing dependencies or set VIBEHUB_UV / VIBEHUB_CADDY."
  exit 1
fi

mkdir -p "$VIBEHUB_ROOT/data/logs/tools" "$VIBEHUB_ROOT/projects" "$VIBEHUB_ROOT/runtime" "$VIBEHUB_ROOT/caddy_data"
if [ ! -f "$VIBEHUB_ROOT/data/registry.json" ]; then
  printf '{}\n' > "$VIBEHUB_ROOT/data/registry.json"
fi
echo

echo "[2/5] Checking frontend..."
if [ ! -f "$VIBEHUB_ROOT/frontend/dist/index.html" ]; then
  echo "  Frontend not built, building now..."
  (cd "$VIBEHUB_ROOT/frontend" && npm install && npm run build)
  echo "  Frontend built successfully"
else
  echo "  Frontend already built"
fi
echo

echo "[3/5] Cleaning previous local services..."
"$CADDY_CMD" stop >/dev/null 2>&1 || true
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill -9
elif command -v fuser >/dev/null 2>&1; then
  fuser -k 8080/tcp >/dev/null 2>&1 || true
else
  echo "  lsof/fuser not found; skipping port 8080 cleanup"
fi
echo "  Done"
echo

echo "[4/5] Starting Caddy gateway..."
"$CADDY_CMD" run 2>"$VIBEHUB_ROOT/data/logs/caddy.log" &
CADDY_PID=$!
trap 'kill "$CADDY_PID" >/dev/null 2>&1 || true' EXIT
sleep 2
echo "  Caddy Admin API ready (localhost:2019)"
echo

echo "[5/5] Starting VibeHub..."
echo
echo "  LAN access:  http://localhost:9529/"
echo "  Internal UI: http://127.0.0.1:8080/"
echo

while true; do
  "$UV_CMD" run "$VIBEHUB_ROOT/main.py"
  exit_code=$?

  if [ "$exit_code" = "42" ]; then
    echo
    echo "[VibeHub] Restart requested, restarting..."
    echo
    sleep 2
    continue
  fi

  exit "$exit_code"
done
