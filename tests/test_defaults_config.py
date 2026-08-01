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


def test_chezmoi_is_the_default_dotfiles_manager() -> None:
    cfg = load_defaults()

    assert cfg["dotfiles"]["manager"] == "chezmoi"
    assert cfg["chezmoi"]["enabled"] is True
    assert cfg["chezmoi"]["repo_url"].endswith(".git")
    assert cfg["chezmoi"]["apply"] is True


def test_chezmoi_template_data_covers_repo_prompts() -> None:
    """Every prompt in the dotfiles repo must have a non-interactive answer."""
    data = load_defaults()["chezmoi"]["data"]

    for key in ("name", "email", "editor", "signing_key", "work_machine"):
        assert key in data, f"chezmoi.data is missing {key}"


def test_stow_local_path_is_not_hardcoded_to_a_foreign_home() -> None:
    cfg = load_defaults()
    assert cfg["dotfiles"]["local_path"] == ""


def test_shell_is_oh_my_zsh_only() -> None:
    cfg = load_defaults()
    shell_cfg = cfg["dev"]["shell"]

    assert shell_cfg["enabled"] is True
    assert "zsh" in shell_cfg["packages"]
    assert shell_cfg["oh_my_zsh"]["enabled"] is True

    configured_packages = set(cfg["dev"]["packages"])
    assert "nvim" not in configured_packages
    assert "vim" not in configured_packages


def test_quality_of_life_tooling_is_present() -> None:
    cfg = load_defaults()
    packages = set(cfg["dev"]["packages"])

    for expected in ("ripgrep", "fzf", "zoxide", "bat", "htop", "tmux", "direnv"):
        assert expected in packages, f"{expected} missing from dev.packages"

    assert cfg["dev"]["shell"]["starship"]["enabled"] is True
    assert cfg["dev"]["containers"]["add_user_to_docker_group"] is True
    assert cfg["dev"]["git"]["configure_global"] is True


def test_vps_defaults_include_ssh_authorized_keys_list() -> None:
    cfg = load_defaults()
    assert "ssh_authorized_keys" in cfg["vps"]
    assert isinstance(cfg["vps"]["ssh_authorized_keys"], list)
