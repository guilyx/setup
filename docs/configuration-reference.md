# Configuration Reference

The system reads YAML from `config/defaults.yaml` (and optional overrides such as `config/local.yaml`).

## Merge Strategy

Current CLI passes a single YAML file to Ansible (`-e @file`).  
Recommended approach:

- Keep `defaults.yaml` as baseline.
- Create environment-specific file with complete values (copy + edit).
- In future, introduce explicit multi-file merge if needed.

## Root Schema

```yaml
common:
dotfiles:
dev:
vps:
```

## `common`

| Key | Type | Example | Purpose |
|---|---|---|---|
| `timezone` | string | `UTC` | host timezone |
| `locale` | string | `en_US.UTF-8` | generated/active locale |
| `base_packages` | list[string] | `["curl","git"]` | baseline package set |

## `dotfiles`

| Key | Type | Example | Purpose |
|---|---|---|---|
| `enabled` | bool | `true` | toggle dotfiles role |
| `repo_url` | string | `https://github.com/me/dotfiles.git` | source repository |
| `destination` | string | `~/.dotfiles` | checkout directory |
| `stow_folders` | list[string] | `["shell","git"]` | packages to stow |

## `dev`

| Key | Type | Example | Purpose |
|---|---|---|---|
| `enabled` | bool | `true` | toggle dev role |
| `package_manager` | string | `apt` | metadata for future multi-OS logic |
| `packages` | list[string] | `["ripgrep","jq"]` | core dev utilities |
| `python.enabled` | bool | `true` | toggle Python toolchain |
| `python.packages` | list[string] | `["pipx","virtualenv"]` | Python packages |
| `node.enabled` | bool | `true` | toggle Node toolchain |
| `node.packages` | list[string] | `["nodejs","npm"]` | Node packages |

## `vps`

| Key | Type | Example | Purpose |
|---|---|---|---|
| `enabled` | bool | `true` | toggle VPS role |
| `create_deploy_user` | bool | `true` | manage deploy account |
| `deploy_user` | string | `deploy` | deploy account name |
| `disable_password_auth` | bool | `true` | SSH hardening toggle |
| `ssh_port` | int | `22` | SSH daemon port |
| `ufw.enabled` | bool | `true` | firewall management toggle |
| `ufw.allow` | list[string] | `["OpenSSH","80","443"]` | allowed UFW rules |
| `reverse_proxy.engine` | string | `caddy` | proxy engine selector |
| `reverse_proxy.domains` | list[object] | see below | domain->upstream routing |

### `vps.reverse_proxy.domains` object

```yaml
- domain: "example.com"
  upstream: "127.0.0.1:3000"
```

## Configuration Example (Production-Oriented)

```yaml
common:
  timezone: "Europe/Amsterdam"
  locale: "en_US.UTF-8"
  base_packages: ["curl", "git", "unzip", "ca-certificates", "fail2ban"]

dotfiles:
  enabled: true
  repo_url: "https://github.com/your-org/dotfiles.git"
  destination: "~/.dotfiles"
  stow_folders: ["shell", "git", "tmux", "nvim"]

dev:
  enabled: true
  package_manager: "apt"
  packages: ["build-essential", "jq", "ripgrep", "fd-find", "fzf"]
  python:
    enabled: true
    packages: ["pipx", "virtualenv"]
  node:
    enabled: true
    packages: ["nodejs", "npm"]

vps:
  enabled: true
  create_deploy_user: true
  deploy_user: "deploy"
  disable_password_auth: true
  ssh_port: 22
  ufw:
    enabled: true
    allow: ["OpenSSH", "80", "443"]
  reverse_proxy:
    engine: "caddy"
    domains:
      - domain: "api.example.com"
        upstream: "127.0.0.1:4000"
      - domain: "app.example.com"
        upstream: "127.0.0.1:3000"
```

## Validation and Safety Tips

- Prefer `--print-only` before first run.
- Use `--check` for impact preview.
- Keep host-specific values in dedicated config files by environment.
- Never place private keys in tracked config.
