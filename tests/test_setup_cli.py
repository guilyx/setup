from pathlib import Path

import pytest

from tooling.setup_cli import build_ansible_command


def test_build_dev_command() -> None:
    config = Path("/tmp/local.yaml")
    cmd = build_ansible_command(target="dev", config_path=config)
    shell = cmd.as_shell()
    assert "ansible-playbook" in shell
    assert "playbooks/dev.yml" in shell
    assert "@/tmp/local.yaml" in shell


def test_build_vps_requires_inventory() -> None:
    with pytest.raises(ValueError):
        build_ansible_command(target="vps", config_path=Path("/tmp/local.yaml"))


def test_build_vps_command() -> None:
    cmd = build_ansible_command(
        target="vps",
        config_path=Path("/tmp/local.yaml"),
        inventory=Path("/tmp/inventory.ini"),
        check=True,
        limit="vps[0]",
    )
    shell = cmd.as_shell()
    assert "playbooks/vps.yml" in shell
    assert "-i /tmp/inventory.ini" in shell
    assert "--check" in shell
    assert "--limit 'vps[0]'" in shell
