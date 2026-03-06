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
            "local_path": form.get("dotfiles_local_path", "/home/wardn/dev/made_after_dark/dotfiles"),
            "repo_url": form.get("dotfiles_repo_url", "https://github.com/guilyx/dotfiles.git"),
            "destination": form.get("dotfiles_destination", "~/.dotfiles"),
            "auto_discover_stow_folders": to_bool(form.get("dotfiles_auto_discover_stow_folders", "true")),
            "exclude_stow_folders": split_csv(form.get("dotfiles_exclude_stow_folders", ".git,ansible")),
            "stow_folders": split_csv(form.get("stow_folders", "")),
        },
        "dev": {
            "enabled": True,
            "packages": split_csv(form.get("dev_packages", "build-essential,make,jq,ripgrep,fd-find,tmux,fzf,zoxide,bat,direnv")),
            "python": {
                "enabled": to_bool(form.get("dev_python_enabled", "true")),
                "packages": split_csv(form.get("dev_python_packages", "pipx,virtualenv,pre-commit")),
            },
            "node": {
                "enabled": to_bool(form.get("dev_node_enabled", "true")),
                "packages": split_csv(form.get("dev_node_packages", "nodejs,npm")),
            },
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
