from __future__ import annotations

import argparse
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SetupCommand:
    args: List[str]

    def as_shell(self) -> str:
        return " ".join(shlex.quote(token) for token in self.args)


def build_ansible_command(
    target: str,
    config_path: Path,
    inventory: Optional[Path] = None,
    check: bool = False,
    limit: Optional[str] = None,
) -> SetupCommand:
    if target not in {"dev", "vps"}:
        raise ValueError(f"Unsupported target: {target}")

    playbook = REPO_ROOT / "playbooks" / f"{target}.yml"
    command: List[str] = [
        "ansible-playbook",
        str(playbook),
        "-e",
        f"@{config_path}",
    ]

    if target == "vps":
        if inventory is None:
            raise ValueError("inventory is required for vps target")
        command.extend(["-i", str(inventory)])

    if limit:
        command.extend(["--limit", limit])

    if check:
        command.append("--check")

    return SetupCommand(args=command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run setup provisioning targets.")
    parser.add_argument("target", choices=["dev", "vps"], help="Provisioning target")
    parser.add_argument(
        "--config",
        default="config/defaults.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--inventory",
        default=None,
        help="Inventory file (required for vps target)",
    )
    parser.add_argument("--check", action="store_true", help="Ansible check mode")
    parser.add_argument("--limit", default=None, help="Optional Ansible --limit")
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print resolved command without executing it",
    )
    return parser.parse_args()


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def run_command(command: SetupCommand) -> int:
    completed = subprocess.run(command.args, cwd=REPO_ROOT, check=False)
    return completed.returncode


def main() -> int:
    args = parse_args()

    config_path = resolve_path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")

    inventory_path = resolve_path(args.inventory) if args.inventory else None
    if args.target == "vps" and inventory_path is not None and not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file does not exist: {inventory_path}")

    command = build_ansible_command(
        target=args.target,
        config_path=config_path,
        inventory=inventory_path,
        check=args.check,
        limit=args.limit,
    )

    print(command.as_shell())
    if args.print_only:
        return 0

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
