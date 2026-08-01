from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import yaml
from flask import Flask, jsonify, render_template, request

REPO_ROOT = Path(__file__).resolve().parents[1]
# Support both `uv run -m webapp.app` and `uv run webapp/app.py`.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tooling.setup_cli import build_ansible_command


GENERATED_CONFIG_PATH = REPO_ROOT / "config" / "web-generated.yaml"

DEFAULT_DEV_PACKAGES = (
    "build-essential,make,cmake,pkg-config,jq,yq,ripgrep,fd-find,tmux,fzf,zoxide,"
    "bat,eza,htop,btop,tree,ncdu,duf,httpie,net-tools,dnsutils,rsync,tldr,"
    "neofetch,direnv,xclip,unzip"
)
DEFAULT_ZSH_PLUGINS = "git,docker,docker-compose,npm,python,ubuntu,direnv,fzf,zoxide"
CUSTOM_ZSH_PLUGINS = [
    {"name": "zsh-autosuggestions", "repo_url": "https://github.com/zsh-users/zsh-autosuggestions.git"},
    {"name": "zsh-syntax-highlighting", "repo_url": "https://github.com/zsh-users/zsh-syntax-highlighting.git"},
    {"name": "zsh-completions", "repo_url": "https://github.com/zsh-users/zsh-completions.git"},
]

app = Flask(__name__, template_folder="templates")


def to_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def split_csv(value: str) -> List[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def split_lines(value: str) -> List[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def build_config_from_form(form: Dict[str, str]) -> Dict[str, Any]:
    return {
        "common": {
            "timezone": form.get("timezone", "Asia/Dubai"),
            "locale": form.get("locale", "en_US.UTF-8"),
            "base_packages": split_csv(form.get("base_packages", "curl,git,unzip,ca-certificates")),
        },
        "dotfiles": {
            "enabled": to_bool(form.get("dotfiles_enabled", "true")),
            "manager": form.get("dotfiles_manager", "chezmoi"),
            "local_path": form.get("dotfiles_local_path", ""),
            "repo_url": form.get("dotfiles_repo_url", "https://github.com/guilyx/dotfiles.git"),
            "destination": form.get("dotfiles_destination", "~/.dotfiles"),
            "auto_discover_stow_folders": to_bool(form.get("dotfiles_auto_discover_stow_folders", "true")),
            "exclude_stow_folders": split_csv(form.get("dotfiles_exclude_stow_folders", ".git,ansible")),
            "stow_folders": split_csv(form.get("stow_folders", "")),
        },
        "chezmoi": {
            "enabled": to_bool(form.get("chezmoi_enabled", "true")),
            "user": form.get("chezmoi_user", ""),
            "repo_url": form.get("chezmoi_repo_url", "https://github.com/guilyx/chezmoi.git"),
            "install_dir": form.get("chezmoi_install_dir", "/usr/local/bin"),
            "apply": to_bool(form.get("chezmoi_apply", "true")),
            "update": to_bool(form.get("chezmoi_update", "true")),
            "data": {
                "name": form.get("chezmoi_data_name", ""),
                "email": form.get("chezmoi_data_email", ""),
                "editor": form.get("chezmoi_data_editor", "nvim"),
                "signing_key": form.get("chezmoi_data_signing_key", ""),
                "work_machine": to_bool(form.get("chezmoi_data_work_machine", "false")),
            },
        },
        "dev": {
            "enabled": True,
            "packages": split_csv(form.get("dev_packages", DEFAULT_DEV_PACKAGES)),
            "python": {
                "enabled": to_bool(form.get("dev_python_enabled", "true")),
                "packages": split_csv(form.get("dev_python_packages", "python3,python3-pip,python3-venv,pipx,virtualenv,pre-commit")),
            },
            "node": {
                "enabled": to_bool(form.get("dev_node_enabled", "true")),
                "version_major": int(form.get("dev_node_version_major", "22")),
                "enable_corepack": to_bool(form.get("dev_node_enable_corepack", "true")),
                "global_packages": split_csv(form.get("dev_node_global_packages", "")),
            },
            "ai_tools": {
                "enabled": to_bool(form.get("dev_ai_tools_enabled", "true")),
                "claude_code": {
                    "enabled": to_bool(form.get("dev_claude_code_enabled", "true")),
                },
                "cursor": {
                    "enabled": to_bool(form.get("dev_cursor_enabled", "true")),
                    "download_url": form.get(
                        "dev_cursor_download_url", "https://downloader.cursor.sh/linux/appImage/x64"
                    ),
                    "install_dir": form.get("dev_cursor_install_dir", "/opt/cursor"),
                    "desktop_entry": to_bool(form.get("dev_cursor_desktop_entry", "true")),
                },
            },
            "rust": {
                "enabled": to_bool(form.get("dev_rust_enabled", "true")),
                "channel": form.get("dev_rust_channel", "stable"),
                "components": split_csv(form.get("dev_rust_components", "rustfmt,clippy")),
            },
            "go": {
                "enabled": to_bool(form.get("dev_go_enabled", "false")),
                "packages": split_csv(form.get("dev_go_packages", "golang-go")),
            },
            "shell": {
                "enabled": to_bool(form.get("dev_shell_enabled", "true")),
                "user": form.get("dev_shell_user", ""),
                "packages": split_csv(form.get("dev_shell_packages", "zsh,fonts-powerline")),
                "oh_my_zsh": {
                    "enabled": to_bool(form.get("dev_shell_oh_my_zsh_enabled", "true")),
                    "repo_url": "https://github.com/ohmyzsh/ohmyzsh.git",
                    "branch": "master",
                    "plugins": split_csv(form.get("dev_shell_plugins", DEFAULT_ZSH_PLUGINS)),
                    "theme": form.get("dev_shell_theme", "robbyrussell"),
                    "custom_plugins": CUSTOM_ZSH_PLUGINS,
                },
                "starship": {"enabled": to_bool(form.get("dev_shell_starship_enabled", "true"))},
            },
            "git": {
                "enabled": to_bool(form.get("dev_git_enabled", "true")),
                "packages": split_csv(form.get("dev_git_packages", "git-lfs,gh,tig")),
                "configure_global": to_bool(form.get("dev_git_configure_global", "true")),
                "user_name": form.get("dev_git_user_name", ""),
                "user_email": form.get("dev_git_user_email", ""),
                "default_branch": form.get("dev_git_default_branch", "main"),
                "pull_rebase": to_bool(form.get("dev_git_pull_rebase", "true")),
                "editor": form.get("dev_git_editor", "nvim"),
            },
            "editor": {
                "enabled": to_bool(form.get("dev_editor_enabled", "true")),
                "packages": split_csv(form.get("dev_editor_packages", "neovim")),
                "default": form.get("dev_editor_default", "nvim"),
            },
            "quality": {
                "enabled": to_bool(form.get("dev_quality_enabled", "true")),
                "packages": split_csv(form.get("dev_quality_packages", "shellcheck,shfmt,yamllint")),
            },
            "containers": {
                "enabled": to_bool(form.get("dev_containers_enabled", "true")),
                "packages": split_csv(form.get("dev_containers_packages", "docker.io,docker-compose-v2")),
                "add_user_to_docker_group": to_bool(form.get("dev_containers_add_user_to_docker_group", "true")),
            },
            "desktop": {
                "enabled": to_bool(form.get("dev_desktop_enabled", "false")),
                "packages": split_csv(form.get("dev_desktop_packages", "polybar,rofi,picom,feh,dunst,waybar")),
            },
            "docs_and_reviews": {"enabled": True},
        },
        "apps": {
            "enabled": to_bool(form.get("apps_enabled", "false")),
            "repo_url": form.get("apps_repo_url", "https://github.com/guilyx/chezmoi.git"),
            "destination": form.get("apps_destination", "~/apps/chezmoi"),
            "version": form.get("apps_version", "main"),
            "update": to_bool(form.get("apps_update", "true")),
            "run_bootstrap": to_bool(form.get("apps_run_bootstrap", "false")),
            "start_stacks": to_bool(form.get("apps_start_stacks", "false")),
        },
        "vps": {
            "enabled": True,
            "create_deploy_user": to_bool(form.get("vps_create_deploy_user", "true")),
            "deploy_user": form.get("vps_deploy_user", "deploy"),
            "disable_password_auth": to_bool(form.get("vps_disable_password_auth", "true")),
            "ssh_port": int(form.get("vps_ssh_port", "22")),
            "ssh_authorized_keys": split_lines(form.get("vps_ssh_authorized_keys", "")),
            "ufw": {
                "enabled": to_bool(form.get("vps_ufw_enabled", "true")),
                "allow": split_csv(form.get("vps_ufw_allow", "OpenSSH,80,443")),
            },
            "reverse_proxy": {
                "engine": "caddy",
                "domains": [
                    {
                        "domain": form.get("vps_domain", "example.com"),
                        "upstream": form.get("vps_upstream", "127.0.0.1:3000"),
                    }
                ],
            },
        },
    }


@app.get("/")
def index() -> str:
    defaults_file = REPO_ROOT / "config" / "defaults.yaml"
    return render_template("index.html", defaults_path=str(defaults_file))


@app.post("/generate")
def generate() -> Any:
    cfg = build_config_from_form(request.form.to_dict())
    GENERATED_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    inventory_value = request.form.get("vps_inventory", "inventory/vps.example.ini")
    inventory_path = Path(inventory_value)
    if not inventory_path.is_absolute():
        inventory_path = REPO_ROOT / inventory_path

    dev_cmd = build_ansible_command(target="dev", config_path=GENERATED_CONFIG_PATH)
    vps_cmd = build_ansible_command(
        target="vps",
        config_path=GENERATED_CONFIG_PATH,
        inventory=inventory_path,
    )

    return jsonify(
        {
            "config_path": str(GENERATED_CONFIG_PATH),
            "inventory_path": str(inventory_path),
            "dev_command": dev_cmd.as_shell(),
            "vps_command": vps_cmd.as_shell(),
            "vps_check_command": f"{vps_cmd.as_shell()} --check",
        }
    )


@app.post("/run-dev")
def run_dev() -> Any:
    if not GENERATED_CONFIG_PATH.exists():
        return jsonify({"error": "No generated config. Use /generate first."}), 400

    command = build_ansible_command(target="dev", config_path=GENERATED_CONFIG_PATH)
    proc = subprocess.run(
        command.args,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-6000:],
            "stderr": proc.stderr[-6000:],
        }
    )


def main() -> None:
    app.run(host="127.0.0.1", port=8080, debug=False)


if __name__ == "__main__":
    main()
