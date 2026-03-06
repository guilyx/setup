from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Dict

import yaml
from flask import Flask, jsonify, render_template, request

from tooling.setup_cli import build_ansible_command


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_CONFIG_PATH = REPO_ROOT / "config" / "web-generated.yaml"

app = Flask(__name__, template_folder="templates")


def to_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def build_config_from_form(form: Dict[str, str]) -> Dict[str, Any]:
    return {
        "common": {
            "timezone": form.get("timezone", "UTC"),
            "locale": form.get("locale", "en_US.UTF-8"),
            "base_packages": [x.strip() for x in form.get("base_packages", "").split(",") if x.strip()],
        },
        "dotfiles": {
            "enabled": to_bool(form.get("dotfiles_enabled", "true")),
            "repo_url": form.get("dotfiles_repo_url", ""),
            "destination": form.get("dotfiles_destination", "~/.dotfiles"),
            "stow_folders": [x.strip() for x in form.get("stow_folders", "").split(",") if x.strip()],
        },
        "dev": {
            "enabled": True,
            "packages": [x.strip() for x in form.get("dev_packages", "").split(",") if x.strip()],
            "python": {
                "enabled": to_bool(form.get("dev_python_enabled", "true")),
                "packages": [x.strip() for x in form.get("dev_python_packages", "").split(",") if x.strip()],
            },
            "node": {
                "enabled": to_bool(form.get("dev_node_enabled", "true")),
                "packages": [x.strip() for x in form.get("dev_node_packages", "").split(",") if x.strip()],
            },
        },
        "vps": {
            "enabled": True,
            "create_deploy_user": to_bool(form.get("vps_create_deploy_user", "true")),
            "deploy_user": form.get("vps_deploy_user", "deploy"),
            "disable_password_auth": to_bool(form.get("vps_disable_password_auth", "true")),
            "ssh_port": int(form.get("vps_ssh_port", "22")),
            "ufw": {
                "enabled": to_bool(form.get("vps_ufw_enabled", "true")),
                "allow": [x.strip() for x in form.get("vps_ufw_allow", "OpenSSH,80,443").split(",") if x.strip()],
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

    dev_cmd = build_ansible_command(target="dev", config_path=GENERATED_CONFIG_PATH)
    vps_cmd = build_ansible_command(
        target="vps",
        config_path=GENERATED_CONFIG_PATH,
        inventory=REPO_ROOT / "inventory" / "vps.example.ini",
    )

    return jsonify(
        {
            "config_path": str(GENERATED_CONFIG_PATH),
            "dev_command": dev_cmd.as_shell(),
            "vps_command": vps_cmd.as_shell(),
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
