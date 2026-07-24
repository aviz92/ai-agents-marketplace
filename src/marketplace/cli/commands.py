"""Command definitions and the `agents-marketplace` entry point."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path

from python_base_command import BaseCommand, CommandRegistry
from python_base_command.base import CommandParser
from rich.console import Console

from marketplace.cli.generate import run_generate
from marketplace.cli.sync import run_sync
from marketplace.cli.validate import run_validate

try:
    _VERSION = _pkg_version("agents-marketplace")
except PackageNotFoundError:
    _VERSION = "dev"


class _GenerateCommand(BaseCommand):
    help = "Interactively select artifacts and generate agents-marketplace.yaml."
    version = _VERSION

    def handle(self, **kwargs: object) -> None:
        verbosity = int(str(kwargs.get("verbosity", 1)))
        run_generate(Console(quiet=verbosity == 0), Path.cwd())


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
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            help="Overwrite already-installed artifacts with the latest version.",
        )

    def handle(self, **kwargs: object) -> None:
        verbosity = int(str(kwargs.get("verbosity", 1)))
        install_all = bool(kwargs.get("install_all", False))
        force = bool(kwargs.get("force", False))
        run_sync(Console(quiet=verbosity == 0), Path.cwd(), install_all, force)


class _ValidateCommand(BaseCommand):
    help = (
        "Validate every authored artifact in the catalog (metadata.yaml, body file, "
        "required fields) without installing anything. Exits non-zero on any error."
    )
    version = _VERSION

    def handle(self, **kwargs: object) -> None:
        verbosity = int(str(kwargs.get("verbosity", 1)))
        if exit_code := run_validate(Console(quiet=verbosity == 0)):
            raise SystemExit(exit_code)


_registry = CommandRegistry()
_registry.add("generate", _GenerateCommand)
_registry.add("sync", _SyncCommand)
_registry.add("validate", _ValidateCommand)


def main() -> None:
    """Entry point for the `agents-marketplace` command."""
    _registry.run()


if __name__ == "__main__":
    main()
