# Machine Setup and the App Ecosystem

Two repositories, one boundary between them:

| Repo | Owns |
|---|---|
| [`guilyx/setup`](https://github.com/guilyx/setup) (this one) | The machine: packages, docker, Node, Python, Rust, shell, dotfiles, AI coding tools |
| [`guilyx/chezmoi`](https://github.com/guilyx/chezmoi) | The apps: which exist, how they are cloned, configured, started and monitored — plus the dotfiles source under `home/` |

If a change installs a toolchain or configures the OS, it belongs here. If it
adds an app, a port, or a compose stack, it belongs there.

## The order

```bash
# 1. Provision the machine. Installs everything, including the dotfiles
#    (which live in the chezmoi repo and are applied by the chezmoi role).
curl -fsSL https://raw.githubusercontent.com/guilyx/setup/main/install.sh | bash

# 2. Open a new shell — zsh is now your login shell, and docker group
#    membership only applies to sessions started after it was granted.
exec zsh

# 3. Bring up the apps.
cd ~/apps/chezmoi
$EDITOR .env          # secrets
make configure && make up
make doctor
```

Step 2 is not optional cosmetics. Docker group membership is read at login, so
a shell that predates it cannot talk to the daemon — this is the single most
common "it worked but docker says permission denied" moment on a fresh box.
The ecosystem's `make preflight` detects it and says so.

## Doing step 3 from step 1

The `apps` role can clone and configure the ecosystem during provisioning:

```yaml
apps:
  enabled: true
  run_bootstrap: true    # clone the app repos and generate their .env files
  start_stacks: false    # leave this off until secrets are filled in
```

It does not reimplement anything — it clones the chezmoi repo and calls that
repo's own scripts, so the ecosystem stays defined in exactly one place.

`start_stacks` is deliberately separate and defaults to off. Starting the
stacks needs real secrets in `~/apps/chezmoi/.env`, which provisioning cannot
supply. The role seeds that file from `.env.example` and tells you what to
edit.

## Why Node comes from NodeSource

Ubuntu 24.04 ships Node 18; the ecosystem apps need 22 or newer. Ubuntu also
packages `npm` separately, while NodeSource's `nodejs` bundles its own — so
installing Ubuntu's `nodejs` and `npm` first, then NodeSource's on top, leaves
dpkg resolving a conflict.

This repo therefore installs Node from NodeSource at `dev.node.version_major`
(default 22) and removes the distro `npm` package first. The ecosystem's
preflight checks for `node >= 22` and finds it already satisfied, so the two
repos agree no matter which order you run them in.

## What moved when the split was drawn

The chezmoi repo used to install apt essentials, docker, Node and Python
itself. Those steps are gone; `scripts/00-preflight.sh` replaced them with a
check. Packages that only the apps needed — `ffmpeg` for clankergram's reel
processing, `sqlite3` for LeClanker's memory store, `openssl` — moved into
`dev.packages` here.
