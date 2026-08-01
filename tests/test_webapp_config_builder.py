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
        "ai_tools",
        "shell",
        "git",
        "editor",
        "quality",
        "containers",
        "desktop",
        "docs_and_reviews",
    }
    assert expected.issubset(cfg["dev"].keys())


def test_generated_node_config_matches_the_nodesource_role() -> None:
    node_cfg = build_config_from_form({})["dev"]["node"]

    assert node_cfg["version_major"] == 22
    assert "packages" not in node_cfg


def test_generated_apps_handoff_is_off_unless_asked_for() -> None:
    cfg = build_config_from_form({})
    assert cfg["apps"]["enabled"] is False
    assert cfg["apps"]["start_stacks"] is False

    opted_in = build_config_from_form({"apps_enabled": "on", "apps_run_bootstrap": "on"})
    assert opted_in["apps"]["enabled"] is True
    assert opted_in["apps"]["run_bootstrap"] is True
