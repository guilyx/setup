# Setup Orchestrator

Highly configurable provisioning for:
- `dev`: local development machine bootstrap (packages, dotfiles, utilities)
- `vps`: end-to-end VPS bootstrap from your machine (users, SSH hardening, firewall, reverse proxy, app runtime)

This project uses Ansible for idempotent provisioning, with:
- a typed Python CLI wrapper for safer command generation
- environment-specific YAML config
- a small web app to quickly compose setup configs and launch commands

## Developer tooling included

- Shell: `zsh` + `oh-my-zsh` (no Vim setup included)
- Productivity: `tmux`, `fzf`, `zoxide`, `bat`, `direnv`
- Git/Collaboration: `gh`, `git-lfs`, PR template, CODEOWNERS
- Quality: `pre-commit`, `shellcheck`, `yamllint`
- Containers: `docker.io`, `docker-compose-v2`
- Desktop bars/launchers: `polybar`, `rofi`, `picom`, `feh`, `dunst`, `waybar` (best-effort)

See `docs/dev-tooling-catalog.md` and `docs/review-policy.md`.

Dotfiles support auto-discovery of stow folders from the source repo root (with configurable excludes).

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

## Quick start

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

- `playbooks/dev.yml` - local machine setup
- `playbooks/vps.yml` - VPS setup
- `roles/*` - granular provisioning logic
- `config/defaults.yaml` - baseline configuration knobs
- `tooling/setup_cli.py` - typed command builder for playbooks
- `webapp/app.py` - quick browser UI for generating/running setup commands

## Web app

Run:

```bash
python -m webapp.app
```

Then open `http://127.0.0.1:8080`.

The UI:
- generates `config/web-generated.yaml`
- displays the exact command that will be run
- allows running `dev` setup locally
- provides `vps` command preview for safe copy/paste execution

## Testing

```bash
pytest
```

## Security notes

- Never commit real secrets or private keys.
- Keep host-specific secrets in `secrets/` (ignored by git).
- Use dedicated deployment SSH keys and locked-down SSH config.
