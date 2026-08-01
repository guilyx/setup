#!/usr/bin/env bash
#
# One-command bootstrap for an Ubuntu development machine.
#
#   curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash
#
# Everything this needs (git, python, ansible, uv) is installed on the fly, so
# the only prerequisite is curl and a sudo-capable user.
set -euo pipefail

SETUP_REPO="${SETUP_REPO:-https://github.com/guilyx/setup.git}"
SETUP_REF="${SETUP_REF:-main}"
SETUP_DIR="${SETUP_DIR:-$HOME/.local/share/setup}"
SETUP_CONFIG="${SETUP_CONFIG:-config/defaults.yaml}"

log() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m==>\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m==>\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: install.sh [options]

Options:
  --config PATH   Config file to provision from, relative to the repo root
                  or absolute (default: config/defaults.yaml)
  --ref REF       Branch or tag of the setup repo to use (default: main)
  --dir PATH      Where to clone the setup repo
                  (default: ~/.local/share/setup)
  --check         Ansible dry run: report what would change, change nothing
  --print-only    Print the resolved ansible-playbook command and exit
  -h, --help      Show this help

Every option also has an environment variable: SETUP_CONFIG, SETUP_REF,
SETUP_DIR.

Examples:
  curl -fsSL .../install.sh | bash
  curl -fsSL .../install.sh | bash -s -- --check
  curl -fsSL .../install.sh | SETUP_REF=my-branch bash
EOF
}

PASSTHROUGH=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) SETUP_CONFIG="${2:?--config needs a value}"; shift 2 ;;
    --ref) SETUP_REF="${2:?--ref needs a value}"; shift 2 ;;
    --dir) SETUP_DIR="${2:?--dir needs a value}"; shift 2 ;;
    --check | --print-only) PASSTHROUGH+=("$1"); shift ;;
    -h | --help) usage; exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done

[[ $(id -u) -ne 0 ]] || die "Run this as your normal user, not root. It will call sudo when it needs to."

command -v apt-get >/dev/null 2>&1 || die "This bootstrap targets Debian/Ubuntu (no apt-get found)."

if ! sudo -n true 2>/dev/null; then
  log "Elevated access is needed to install packages; you may be prompted for your password."
fi
sudo -v || die "sudo access is required."

log "Installing bootstrap prerequisites"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
# python3-apt is what Ansible's apt module imports; it only exists for the
# system interpreter, which is why the dev playbook pins itself to it.
sudo apt-get install -y -qq git curl ca-certificates python3 python3-pip python3-venv python3-apt

# uv manages the project's Python environment; the official installer drops it
# in ~/.local/bin, which is not necessarily on PATH in a non-interactive shell.
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  log "Installing uv"
  curl -fsSL https://astral.sh/uv/install.sh | sh
fi
command -v uv >/dev/null 2>&1 || die "uv installation failed; see https://docs.astral.sh/uv/"

if [[ -d "$SETUP_DIR/.git" ]]; then
  log "Updating $SETUP_DIR"
  git -C "$SETUP_DIR" fetch --depth 1 origin "$SETUP_REF"
  git -C "$SETUP_DIR" checkout -q FETCH_HEAD
else
  log "Cloning $SETUP_REPO into $SETUP_DIR"
  mkdir -p "$(dirname "$SETUP_DIR")"
  git clone --depth 1 --branch "$SETUP_REF" "$SETUP_REPO" "$SETUP_DIR"
fi

cd "$SETUP_DIR"

log "Installing project dependencies"
uv sync --extra dev
uv run ansible-galaxy collection install -r requirements.yml

# Run the playbook as root, but through `sudo env` with the project venv on
# PATH: sudo's secure_path would otherwise hide both python and
# ansible-playbook. sudo sets SUDO_USER itself, which is how the playbook
# learns which unprivileged account to configure.
log "Provisioning (config: $SETUP_CONFIG)"
sudo env "PATH=$SETUP_DIR/.venv/bin:$PATH" "$SETUP_DIR/.venv/bin/python" \
  -m tooling.setup_cli dev \
  --config "$SETUP_CONFIG" "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"

log "Done. Open a new terminal (or run 'exec zsh') to pick up the new shell."
if id -nG "$(id -un)" | tr ' ' '\n' | grep -qx docker; then
  warn "Log out and back in for docker group membership to take effect."
fi
