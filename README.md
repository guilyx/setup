# Setup Orchestrator

Highly configurable provisioning for:
- `dev`: local development machine bootstrap (packages, dotfiles, utilities)
- `vps`: end-to-end VPS bootstrap from your machine (users, SSH hardening, firewall, reverse proxy, app runtime)

This project uses Ansible for idempotent provisioning, with:
- a typed Python CLI wrapper for safer command generation
- environment-specific YAML config
- a small web app to quickly compose setup configs and launch commands

## Install on a fresh Ubuntu machine

One command. No clone, no prerequisites beyond `curl` and a sudo-capable user:

```bash
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash
```

It installs git/python/uv, clones this repo to `~/.local/share/setup`, installs
the Ansible collections, and provisions the machine from `config/defaults.yaml`.

Preview without changing anything:

```bash
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash -s -- --check
```

Other flags: `--config PATH`, `--ref BRANCH`, `--dir PATH`, `--print-only`.
Each has an environment variable equivalent (`SETUP_CONFIG`, `SETUP_REF`,
`SETUP_DIR`), which is how you pass them when piping into `bash`:

```bash
curl -fsSL .../install.sh | SETUP_REF=my-branch bash
```

## Developer tooling included

- Shell: `zsh` + `oh-my-zsh` with autosuggestions, syntax highlighting and completions, plus the `starship` prompt
- Productivity: `tmux`, `fzf`, `zoxide`, `bat`, `eza`, `ripgrep`, `fd`, `jq`, `yq`, `htop`, `btop`, `tree`, `ncdu`, `duf`, `httpie`, `tldr`, `direnv`, `xclip`
- Languages: Python (`pipx`, `virtualenv`, `pre-commit`), Node 22 from NodeSource with corepack, Rust via `rustup` (opt-in Go)
- AI coding tools: Claude Code and Cursor
- Git/Collaboration: `gh`, `git-lfs`, `tig`, opinionated global git config, PR template, CODEOWNERS
- Quality: `pre-commit`, `shellcheck`, `shfmt`, `yamllint`
- Containers: `docker.io`, `docker-compose-v2`, with your user added to the `docker` group
- Desktop bars/launchers: `polybar`, `rofi`, `picom`, `feh`, `dunst`, `waybar` (opt-in)

Package installation is resilient: a group is installed in one transaction, and
if a name does not exist on your Ubuntu release the group is retried
package-by-package so the rest still lands.

See `docs/dev-tooling-catalog.md` and `docs/review-policy.md`.

## Dotfiles with chezmoi

Dotfiles are managed by [chezmoi](https://www.chezmoi.io) by default, from
[`guilyx/chezmoi`](https://github.com/guilyx/chezmoi). The `chezmoi` role:

- installs the `chezmoi` binary
- writes `~/.config/chezmoi/chezmoi.toml` from `chezmoi.data` in your config, so
  `chezmoi init` never stops to prompt during provisioning
- runs `chezmoi init --apply` on first run and `chezmoi update` on later runs

Day to day:

```bash
chezmoi edit ~/.zshrc   # edit the source
chezmoi diff            # preview
chezmoi apply -v        # apply
chezmoi update -v       # pull and apply
```

The older GNU stow workflow is still available: set `dotfiles.manager: stow`.
The two managers are mutually exclusive — whichever one is selected owns the
home directory, and the other role skips itself.

See `docs/chezmoi-guide.md`.

## The app ecosystem

This repo provisions the machine. The apps themselves — what runs, on which
port, started how — live in [`guilyx/chezmoi`](https://github.com/guilyx/chezmoi).
Provision first, then bring the apps up:

```bash
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash
exec zsh                     # docker group applies to new sessions only
cd ~/apps/chezmoi && make configure && make up
```

Setting `apps.enabled: true` makes this repo do the clone and configure step
for you during provisioning. Starting the stacks stays opt-in, since it needs
secrets. See `docs/ecosystem-handoff.md`.

## Local LLM serving (LeHarness)

Set `leharness.enabled: true` to also install
[`guilyx/LeHarness`](https://github.com/guilyx/LeHarness) — the harness that
detects the machine's hardware tier (DGX-class multi-GPU, single-GPU
workstation, Jetson AGX Orin, or CPU-only), serves local models through vLLM
or Ollama accordingly, and exposes one OpenAI-compatible endpoint
(`http://127.0.0.1:8000/v1`). The role clones the repo, verifies the GPU
container runtime (installing `nvidia-container-toolkit` when needed), and
reports the detected profile; actually starting the engine
(`leharness.start: true`) stays opt-in because it downloads model weights.

## Documentation

- Full docs index: `docs/README.md`
- Architecture and diagrams: `docs/architecture.md`
- Provisioning execution flows: `docs/provisioning-flows.md`
- Config schema and examples: `docs/configuration-reference.md`
- Operational procedures: `docs/operations-runbook.md`
- Web UI usage and extension: `docs/webapp-guide.md`
- Reusable diagram snippets: `docs/diagrams-snippets.md`

## Why this design

- **Idempotent**: rerunning playbooks converges to desired state.
- **Granular**: role variables map directly to setup capabilities.
- **Composable**: `dev`, `vps`, and dotfiles are independent roles.
- **Auditable**: declarative config + Ansible logs.
- **Safe defaults**: dry-run capable and explicit inventory.

## Quick start (working on this repo)

If you cloned the repository yourself rather than using the curl entrypoint:

1) Install dependencies:

```bash
./scripts/bootstrap.sh
```

2) Copy and customize config:

```bash
cp config/defaults.yaml config/local.yaml
```

3) Run local dev provisioning:

```bash
./scripts/run-dev.sh --config config/local.yaml
```

4) Run VPS provisioning:

```bash
cp inventory/vps.example.ini inventory/vps.ini
# edit inventory/vps.ini with your host(s)
./scripts/run-vps.sh --config config/local.yaml --inventory inventory/vps.ini
```

## Components

- `install.sh` - curl-able entrypoint for a fresh machine
- `playbooks/dev.yml` - local machine setup
- `playbooks/vps.yml` - VPS setup
- `roles/*` - granular provisioning logic
- `config/defaults.yaml` - baseline configuration knobs
- `tooling/setup_cli.py` - typed command builder for playbooks
- `webapp/app.py` - quick browser UI for generating/running setup commands

## Web app

Run:

```bash
uv run python -m webapp.app
```

Then open `http://127.0.0.1:8080`.

The UI:
- generates `config/web-generated.yaml`
- displays the exact command that will be run
- allows running `dev` setup locally
- provides `vps` command and `--check` preview for safe copy/paste execution
- supports deploy-user SSH key input (one public key per line) for VPS bootstrap

## Testing

```bash
uv run pytest
```

## Security notes

- Never commit real secrets or private keys.
- Keep host-specific secrets in `secrets/` (ignored by git).
- Use dedicated deployment SSH keys and locked-down SSH config.
