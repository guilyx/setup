"""Structural checks on the Ansible layout and the curl entrypoint.

These are cheap guards against the failure mode where config grows a knob that
no role reads, or a role is added but never wired into a playbook.
"""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str):
    return yaml.safe_load((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_dev_playbook_runs_the_chezmoi_role() -> None:
    play = load_yaml("playbooks/dev.yml")[0]
    roles = [entry["role"] for entry in play["roles"]]

    assert roles == ["common", "dev_shell", "dev", "chezmoi", "dotfiles", "apps"]


def test_dev_playbook_resolves_a_target_user_before_roles_run() -> None:
    play = load_yaml("playbooks/dev.yml")[0]
    pre_task_names = [task["name"] for task in play["pre_tasks"]]

    assert any("target user" in name for name in pre_task_names)


def test_every_role_directory_has_tasks() -> None:
    for role_dir in sorted((REPO_ROOT / "roles").iterdir()):
        if not role_dir.is_dir():
            continue
        assert (role_dir / "tasks" / "main.yml").is_file(), f"{role_dir.name} has no tasks"


def test_no_config_key_is_read_through_a_dict_method_name() -> None:
    """`foo.update` in Jinja resolves to dict.update, the bound method, not the
    config key — and it fails silently: truthy as an object, False through
    `| bool`. Keys that collide with dict methods must use bracket syntax."""
    collisions = ("update", "items", "keys", "values", "copy", "pop", "clear", "get")
    offenders = []

    for path in sorted((REPO_ROOT / "roles").rglob("*.yml")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "{{" not in line and not line.lstrip().startswith("-"):
                continue
            for method in collisions:
                # A config variable read as `something.update`, excluding
                # module parameters like `update_cache:` and FQCNs.
                if re.search(rf"\b(?!ansible|community|posix)\w+\.{method}\b(?!_)", line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")

    assert not offenders, "use bracket syntax for these:\n" + "\n".join(offenders)


def test_install_script_is_executable_and_self_contained() -> None:
    install = REPO_ROOT / "install.sh"

    assert install.is_file()
    assert install.stat().st_mode & 0o111, "install.sh must be executable"

    body = install.read_text(encoding="utf-8")
    assert body.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in body
    # The whole point of the entrypoint: it clones the repo itself.
    assert "git clone" in body
    assert "tooling.setup_cli dev" in body


def test_readme_documents_the_curl_entrypoint() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "curl -fsSL" in readme
    assert "install.sh" in readme
