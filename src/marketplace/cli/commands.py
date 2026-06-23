"""Command definitions and the `agents-marketplace` entry point."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path

from python_base_command import BaseCommand, CommandRegistry
from python_base_command.base import CommandParser
from rich.console import Console

from marketplace.cli.install import run_interactive
from marketplace.cli.sync import run_sync

try:
    _VERSION = _pkg_version("agents-marketplace")
except PackageNotFoundError:
    _VERSION = "dev"


class _InstallCommand(BaseCommand):
    help = "Interactively browse and install skills, rules, and plugins."
    version = _VERSION

    def handle(self, **kwargs: object) -> None:
        verbosity = int(kwargs.get("verbosity", 1))
        run_interactive(Console(quiet=verbosity == 0), Path.cwd())


class _SyncCommand(BaseCommand):
    help = (
        "Install artifacts from agents-marketplace.yaml. "
        "Prompts to choose which agents unless --all is passed."
    )
    version = _VERSION

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--all",
            action="store_true",
            dest="install_all",
            help="Install for all agents in the manifest without prompting.",
        )

    def handle(self, **kwargs: object) -> None:
        verbosity = int(kwargs.get("verbosity", 1))
        install_all = bool(kwargs.get("install_all", False))
        run_sync(Console(quiet=verbosity == 0), Path.cwd(), install_all=install_all)


_registry = CommandRegistry()
_registry.add("install", _InstallCommand)
_registry.add("sync", _SyncCommand)


def main() -> None:
    """Entry point for the `agents-marketplace` command."""
    _registry.run()


if __name__ == "__main__":
    main()
