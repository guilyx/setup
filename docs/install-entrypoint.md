# Install Entrypoint

`install.sh` is the front door for a fresh Ubuntu machine. It is designed to be
piped from `curl`, so the machine does not need git, python, or this repository
beforehand.

```bash
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash
```

## What it does

1. Refuses to run as root — it wants your unprivileged account, and calls
   `sudo` only where elevation is genuinely needed.
2. Installs `git`, `curl`, `ca-certificates`, and Python via apt.
3. Installs `uv` if missing (into `~/.local/bin`).
4. Clones this repository to `$SETUP_DIR` (default `~/.local/share/setup`), or
   fast-forwards it if already present.
5. `uv sync --extra dev` and `ansible-galaxy collection install`.
6. Runs the `dev` playbook through `tooling/setup_cli.py`.

## Options

| Flag | Environment variable | Default | Purpose |
|---|---|---|---|
| `--config PATH` | `SETUP_CONFIG` | `config/defaults.yaml` | Config to provision from |
| `--ref REF` | `SETUP_REF` | `main` | Branch or tag to install from |
| `--dir PATH` | `SETUP_DIR` | `~/.local/share/setup` | Clone location |
| `--check` | — | off | Ansible dry run |
| `--print-only` | — | off | Print the command and exit |

When piping into `bash`, flags need `-s --`:

```bash
curl -fsSL .../install.sh | bash -s -- --check --config config/local.yaml
```

Environment variables are often easier in that position:

```bash
curl -fsSL .../install.sh | SETUP_REF=my-branch SETUP_CONFIG=config/local.yaml bash
```

## Privilege and user resolution

The playbook needs to know which unprivileged account to configure, but it runs
as root. `install.sh` invokes it via `sudo env`, and sudo populates `SUDO_USER`
with the invoking account; the `dev` playbook reads that in a pre-task and
resolves `setup_target_user` plus that user's real home directory from
`getent`. Every role that touches a home directory uses those two facts rather
than `~` or `ansible_env.HOME`, both of which point at `/root` under `become`.

`sudo env` is used rather than plain `sudo` because Debian's `secure_path`
overrides `PATH`, which would hide both the project virtualenv's Python and
`ansible-playbook`.

Ansible collections install into `./.ansible/collections` (set in
`ansible.cfg`), so they resolve identically whether the playbook is run as your
user or under sudo.

## Re-running

The script is idempotent and safe to re-run: it fast-forwards the clone and
re-converges the machine. That is also the upgrade path — re-running picks up
new roles and new dotfiles.

## Verifying before running

Piping a script from the internet into a shell deserves a look first:

```bash
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | less
```

`--check` is the other safety net: it runs the full playbook in Ansible's dry
run mode and reports what would change without changing it.
