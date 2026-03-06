from pathlib import Path

import yaml


def load_defaults() -> dict:
    defaults_path = Path(__file__).resolve().parents[1] / "config" / "defaults.yaml"
    return yaml.safe_load(defaults_path.read_text(encoding="utf-8"))


def test_dotfiles_autodiscovery_defaults() -> None:
    cfg = load_defaults()
    dotfiles = cfg["dotfiles"]

    assert dotfiles["auto_discover_stow_folders"] is True
    assert ".git" in dotfiles["exclude_stow_folders"]
    assert "ansible" in dotfiles["exclude_stow_folders"]


def test_shell_is_oh_my_zsh_only() -> None:
    cfg = load_defaults()
    shell_cfg = cfg["dev"]["shell"]

    assert shell_cfg["enabled"] is True
    assert "zsh" in shell_cfg["packages"]
    assert shell_cfg["oh_my_zsh"]["enabled"] is True

    configured_packages = set(cfg["dev"]["packages"])
    assert "nvim" not in configured_packages
    assert "vim" not in configured_packages


def test_vps_defaults_include_ssh_authorized_keys_list() -> None:
    cfg = load_defaults()
    assert "ssh_authorized_keys" in cfg["vps"]
    assert isinstance(cfg["vps"]["ssh_authorized_keys"], list)
