# Webapp Usage

The webapp helps operators generate config and commands for both local laptop setup and VPS setup.

## Start

```bash
uv run webapp/app.py
```

Open `http://127.0.0.1:8080`.

## Local Laptop Setup

1. Fill Common, Dotfiles, and Dev sections.
2. Click **Generate Commands**.
3. Click **Run Local Dev Setup**.

This writes `config/web-generated.yaml` and runs the generated `dev` playbook command.

## VPS Setup

1. Fill **VPS Bootstrap** fields:
   - inventory path (`inventory/vps.ini` or absolute path)
   - deploy user
   - SSH port
   - one SSH public key per line
   - firewall allows and reverse proxy mapping
2. Click **Generate Commands**.
3. Run `vps_check_command` first (dry run).
4. Run `vps_command` when output looks correct.

## SSH Keys Behavior

Keys entered in the UI are written to:

```yaml
vps:
  ssh_authorized_keys:
    - ssh-ed25519 AAAA... user@host
```

During VPS provisioning, these keys are installed for the deploy user.
