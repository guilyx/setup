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
chezmoi:
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
| `enabled` | bool | `true` | toggle dotfiles handling |
| `manager` | string | `chezmoi` | `chezmoi` or `stow`; selects which role owns `$HOME` |
| `repo_url` | string | `https://github.com/me/dotfiles.git` | stow source repository |
| `destination` | string | `~/.dotfiles` | stow checkout directory |
| `local_path` | string | `""` | use an existing local stow tree instead of cloning |
| `stow_folders` | list[string] | `["shell","git"]` | packages to stow |

The `chezmoi` and `stow` roles are mutually exclusive. Whichever `manager`
names is the one that runs; the other ends itself immediately.

## `chezmoi`

| Key | Type | Example | Purpose |
|---|---|---|---|
| `enabled` | bool | `true` | toggle chezmoi role |
| `user` | string | `""` | target user; blank uses the playbook-resolved user |
| `repo_url` | string | `https://github.com/guilyx/chezmoi.git` | dotfiles source |
| `install_dir` | string | `/usr/local/bin` | where the binary lands |
| `apply` | bool | `true` | apply immediately on first init |
| `update` | bool | `true` | pull and apply on subsequent runs |
| `data` | map | see below | template values written to `~/.config/chezmoi/chezmoi.toml` |

```yaml
chezmoi:
  data:
    name: "Ada Lovelace"
    email: "ada@example.com"
    editor: "nvim"
    signing_key: ""
    work_machine: false
```

Keys under `data` become chezmoi template variables (`{{ .name }}`). Every
prompt in the dotfiles repo's `.chezmoi.toml.tmpl` needs a matching key here,
or provisioning stops to ask. See [Dotfiles with chezmoi](./chezmoi-guide.md).

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
| `rust.enabled` | bool | `true` | install Rust via rustup as the target user |
| `rust.channel` | string | `stable` | rustup default toolchain |
| `rust.components` | list[string] | `["rustfmt","clippy"]` | rustup components |
| `go.enabled` | bool | `false` | toggle Go toolchain |
| `shell.starship.enabled` | bool | `true` | install the starship prompt |
| `shell.oh_my_zsh.custom_plugins` | list[object] | see defaults | extra plugins cloned into `custom/plugins` |
| `git.configure_global` | bool | `true` | write global git settings for the target user |
| `git.user_name` / `git.user_email` | string | `""` | identity; skipped when blank |
| `editor.enabled` | bool | `true` | install the editor |
| `editor.default` | string | `nvim` | exported as `$EDITOR` |
| `containers.add_user_to_docker_group` | bool | `true` | docker without sudo |
| `desktop.enabled` | bool | `false` | bars and launchers; off for headless boxes |

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
