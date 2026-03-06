#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

cd "${ROOT_DIR}"
uv sync --extra dev

ansible-galaxy collection install -r "${ROOT_DIR}/requirements.yml"

echo "Bootstrap complete."
