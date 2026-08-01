# Dev Tooling Catalog

Everything here is configurable in `config/defaults.yaml` under `dev`.

Package installation is best-effort per group: the group is installed in one
apt transaction, and only if that fails is it retried package-by-package, so a
name that does not exist on your Ubuntu release does not take the rest of the
group down with it. Skipped packages are reported at the end of the run.

## Shell

- `zsh` as the default shell for the target user.
- `oh-my-zsh` with custom plugins: `zsh-autosuggestions`,
  `zsh-syntax-highlighting`, `zsh-completions`.
- `starship` prompt (`dev.shell.starship.enabled`).

Who installs what depends on the dotfiles manager, and exactly one side does
each job:

| | chezmoi (default) | stow |
|---|---|---|
| `~/.zshrc` | dotfiles repo | generated from `zshrc.j2` |
| `~/.oh-my-zsh` and plugins | `.chezmoiexternal.toml` | cloned by the `dev_shell` role |
| zsh package, default shell, starship binary | `dev_shell` role | `dev_shell` role |

The split matters: chezmoi's externals are declared `exact`, so if the role
also cloned into `~/.oh-my-zsh` chezmoi would delete whatever it had not put
there itself.

## Terminal and CLI Productivity

| Tool | What it replaces or adds |
|---|---|
| `ripgrep` | `grep`, recursively and fast |
| `fd-find` | `find`, with sane defaults |
| `bat` | `cat` with syntax highlighting |
| `eza` | `ls` with git status and tree mode |
| `fzf` | Fuzzy finder, wired into shell key bindings |
| `zoxide` | `cd` that learns your directories |
| `tmux` | Terminal multiplexer |
| `direnv` | Per-directory environment loading |
| `htop`, `btop` | Process and system monitors |
| `ncdu`, `duf`, `tree` | Disk usage and layout |
| `jq`, `yq` | JSON and YAML on the command line |
| `httpie` | HTTP requests without curl flag archaeology |
| `tldr` | Practical examples instead of full man pages |
| `xclip` | Clipboard from the terminal |
| `net-tools`, `dnsutils`, `rsync` | Network and transfer basics |

Ubuntu ships `fd` and `bat` as `fdfind` and `batcat`; the `dev` role symlinks
both to their conventional names in `/usr/local/bin`.

## Languages

- Python: `python3`, `pip`, `venv`, `pipx`, `virtualenv`, `pre-commit`
- Node: installed from NodeSource at `dev.node.version_major` (default 22),
  with corepack enabled for pnpm and yarn. Not from apt — Ubuntu ships Node 18,
  and its separate `npm` package conflicts with NodeSource's bundled one, so
  the role removes it first. See [Machine Setup and the App Ecosystem](./ecosystem-handoff.md).
- Rust: installed through `rustup` under the target user's account, with
  `rustfmt` and `clippy`. Toolchains stay user-owned and updatable without root.
- Go: opt-in (`dev.go.enabled`)

## Git and Collaboration

- `gh` (GitHub CLI), `git-lfs`, `tig`
- Global git configuration applied to the target user when
  `dev.git.configure_global` is true: default branch, rebase-on-pull,
  `push.autoSetupRemote`, `rebase.autoStash`, `fetch.prune`, `diff.colorMoved`.
  Only keys with a value are written, so nothing you or chezmoi already set is
  clobbered.
- Repository guardrails: `.github/PULL_REQUEST_TEMPLATE.md`, `.github/CODEOWNERS`

## Editor

- `neovim`, with `dev.editor.default` exported as `$EDITOR`.

## AI Coding Tools

`dev.ai_tools`, on by default.

- **Claude Code** — installed via the official installer into the target user's
  `~/.local/bin/claude`, so it stays user-owned and self-updating. Authenticate
  once with `claude` on first run.
- **Cursor** — the Linux AppImage, placed in `dev.ai_tools.cursor.install_dir`
  (default `/opt/cursor`), symlinked to `/usr/local/bin/cursor`, with a desktop
  entry. `libfuse2` is installed alongside it, since AppImages need FUSE 2 and
  Ubuntu stopped shipping it by default at 22.04.

Cursor is a GUI application and is pointless on a headless box — set
`dev.ai_tools.cursor.enabled: false` there. Its download is best-effort: if the
URL changes upstream, provisioning reports it and carries on rather than
failing the run.

## Quality and Validation

- `pre-commit`, `shellcheck`, `shfmt`, `yamllint`

## Containers

- `docker.io`, `docker-compose-v2`
- The target user is added to the `docker` group
  (`dev.containers.add_user_to_docker_group`), so `docker` works without
  `sudo`. This takes effect on next login.
- The docker service is enabled and started.

## Desktop, Bars and Launchers

Opt-in (`dev.desktop.enabled`, default `false`, since these are meaningless on
a headless box): `polybar`, `rofi`, `picom`, `feh`, `dunst`, `waybar`.

## Configuration Surface

All toggles and package lists live under `dev` in `config/defaults.yaml`:

`dev.packages`, `dev.python`, `dev.node`, `dev.rust`, `dev.go`, `dev.shell`,
`dev.git`, `dev.editor`, `dev.quality`, `dev.containers`, `dev.desktop`,
`dev.docs_and_reviews`.

Dotfiles are configured separately — see [Dotfiles with chezmoi](./chezmoi-guide.md).
