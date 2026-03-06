# Dev Tooling Catalog

This catalog describes the additional developer tooling now configurable in `config/defaults.yaml`.

## Shell

- `zsh` as default shell for the selected local user.
- `oh-my-zsh` as the only shell framework (no Vim dependency).
- Generated `.zshrc` with selected plugins and theme.

## Terminal and CLI Productivity

- `tmux`
- `fzf`
- `zoxide`
- `bat`
- `direnv`
- existing baseline: `ripgrep`, `fd-find`, `jq`

## Git and Collaboration

- `gh` (GitHub CLI)
- `git-lfs`
- Repository guardrails:
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.github/CODEOWNERS`

## Quality and Validation

- `pre-commit`
- `shellcheck`
- `yamllint`

## Containers

- `docker.io`
- `docker-compose-v2`

## Desktop/Bar and Launcher Tooling

- `polybar`
- `rofi`
- `picom`
- `feh`
- `dunst`
- `waybar`

Desktop package installation is best-effort to keep provisioning resilient across distro differences.

## Configuration Surface

All toggles and package lists live under `dev` in `config/defaults.yaml`:

- `dev.shell`
- `dev.git`
- `dev.quality`
- `dev.containers`
- `dev.desktop`
- `dev.docs_and_reviews`
