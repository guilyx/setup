# Dotfiles with chezmoi

[chezmoi](https://www.chezmoi.io) is the default dotfiles manager. It keeps a
source directory (`~/.local/share/chezmoi`, a clone of the dotfiles repository)
and applies it to `$HOME`, templating machine-specific values on the way.

## Why chezmoi rather than stow

Stow symlinks directories into `$HOME`. That works until a file needs to differ
per machine — a work email in `.gitconfig`, a signing key that only exists on
one laptop, a plugin list that depends on what is installed. chezmoi templates
those values instead of forcing a second branch or a second repo.

The stow role is still present and supported; set `dotfiles.manager: stow` to
use it. Exactly one manager runs: the other role ends itself immediately, so
the two never fight over the same file.

## What the role does

`roles/chezmoi` runs, in order:

1. Installs the `chezmoi` binary into `chezmoi.install_dir` (skipped if present).
2. Writes `~/.config/chezmoi/chezmoi.toml` from `chezmoi.data`.
3. On first run, `chezmoi init --apply <repo_url>`.
4. On later runs, `chezmoi update` (git pull + apply).

Step 2 is what keeps provisioning non-interactive. The dotfiles repository's
`.chezmoi.toml.tmpl` uses `promptStringOnce`, which only prompts when the value
is not already in the config file — so writing the config first means
`chezmoi init` finds every answer it needs and never blocks on a TTY.

## Configuration

```yaml
dotfiles:
  manager: "chezmoi"        # or "stow"

chezmoi:
  enabled: true
  user: ""                  # blank: the user resolved by the dev playbook
  repo_url: "https://github.com/guilyx/chezmoi.git"
  install_dir: "/usr/local/bin"
  apply: true               # apply immediately on init
  update: true              # pull and apply on subsequent runs
  data:                     # becomes [data] in ~/.config/chezmoi/chezmoi.toml
    name: "Erwin Lejeune"
    email: "erwin.lejeune15@gmail.com"
    editor: "nvim"
    signing_key: ""
    work_machine: false
```

Anything you add under `chezmoi.data` is available in templates as
`{{ .your_key }}`. Booleans and numbers are emitted unquoted so TOML types stay
correct.

## Adding a new templated value

1. Add it under `chezmoi.data` in `config/defaults.yaml`.
2. Add a matching `promptStringOnce` / `promptBoolOnce` line to
   `.chezmoi.toml.tmpl` in the dotfiles repo, so machines set up by hand are
   still asked for it.
3. Reference it from any `.tmpl` file in the dotfiles repo.

Step 2 matters: without it, a hand-run `chezmoi init` has no way to supply the
value and templates referencing it fail.

## Daily commands

| Command | Effect |
|---|---|
| `chezmoi edit ~/.zshrc` | Edit the source file, not the applied one |
| `chezmoi diff` | Show what `apply` would change |
| `chezmoi apply -v` | Apply the source to `$HOME` |
| `chezmoi update -v` | `git pull` in the source directory, then apply |
| `chezmoi cd` | Open a shell in the source directory |
| `chezmoi add ~/.foorc` | Start tracking an existing file |
| `chezmoi re-add` | Pull local edits back into the source |

## Troubleshooting

**`chezmoi init` hangs or fails asking for input.** The config file was not
written, or a prompt in `.chezmoi.toml.tmpl` has no matching key under
`chezmoi.data`. Check `~/.config/chezmoi/chezmoi.toml`.

**Local edits are reverted by `apply`.** That is the design — `$HOME` is a
render target. Use `chezmoi re-add <file>` to promote a local edit into the
source, or put machine-local overrides in `~/.config/shell/local.sh`, which is
sourced last and never tracked.

**A file needs to exist on only some machines.** Guard it in
`.chezmoiignore`, which is itself a template:
`{{ if .work_machine }}.config/personal-thing{{ end }}`.
