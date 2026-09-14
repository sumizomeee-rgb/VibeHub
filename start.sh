#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
UV="${VIBEHUB_UV:-uv}"
if [[ -x bin/linux-x64/uv ]]; then UV="$PWD/bin/linux-x64/uv"; fi
if [[ -x bin/uv ]]; then UV="$PWD/bin/uv"; fi
exec "$UV" run --locked python main.py "$@"
