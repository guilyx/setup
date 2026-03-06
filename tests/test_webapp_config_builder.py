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
