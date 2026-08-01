from webapp.app import build_config_from_form


def test_build_config_from_form_parses_vps_ssh_keys() -> None:
    form = {
        "vps_ssh_authorized_keys": "ssh-ed25519 AAAA first@host\n\nssh-rsa BBBB second@host\n",
        "vps_ufw_allow": "OpenSSH,80,443",
    }
    cfg = build_config_from_form(form)
    assert cfg["vps"]["ssh_authorized_keys"] == [
        "ssh-ed25519 AAAA first@host",
        "ssh-rsa BBBB second@host",
    ]


def test_build_config_from_form_defaults_timezone_and_dotfiles() -> None:
    cfg = build_config_from_form({})
    assert cfg["common"]["timezone"] == "Asia/Dubai"
    assert cfg["dotfiles"]["auto_discover_stow_folders"] is True


def test_build_config_from_form_defaults_to_chezmoi() -> None:
    cfg = build_config_from_form({})

    assert cfg["dotfiles"]["manager"] == "chezmoi"
    assert cfg["chezmoi"]["enabled"] is True
    assert cfg["chezmoi"]["data"]["editor"] == "nvim"
    assert cfg["chezmoi"]["data"]["work_machine"] is False


def test_build_config_from_form_carries_chezmoi_template_data() -> None:
    cfg = build_config_from_form(
        {
            "chezmoi_data_name": "Ada Lovelace",
            "chezmoi_data_email": "ada@example.com",
            "chezmoi_data_work_machine": "on",
        }
    )

    assert cfg["chezmoi"]["data"]["name"] == "Ada Lovelace"
    assert cfg["chezmoi"]["data"]["email"] == "ada@example.com"
    assert cfg["chezmoi"]["data"]["work_machine"] is True


def test_generated_dev_section_matches_the_keys_roles_read() -> None:
    """A partial `dev` block would silently disable roles, since Ansible
    replaces the whole key rather than merging it."""
    cfg = build_config_from_form({})

    expected = {
        "enabled",
        "packages",
        "python",
        "node",
        "rust",
        "go",
        "shell",
        "git",
        "editor",
        "quality",
        "containers",
        "desktop",
        "docs_and_reviews",
    }
    assert expected.issubset(cfg["dev"].keys())
