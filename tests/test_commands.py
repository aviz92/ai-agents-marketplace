"""Tests for marketplace.cli.commands — CLI argument wiring for `sync --filename`."""

import sys

import pytest

from marketplace.cli import commands
from marketplace.consts.manifest import MANIFEST_NAME


def _stub_run_sync(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    captured: dict[str, object] = {}

    def _fake_run_sync(
        console: object, project_dir: object, install_all: bool, force: bool, filename: str
    ) -> None:
        captured.update(install_all=install_all, force=force, filename=filename)

    monkeypatch.setattr(commands, "run_sync", _fake_run_sync)
    return captured


class TestSyncCliFilenameWiring:
    def test_sync_cli_without_filename_flag_uses_manifest_name_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured = _stub_run_sync(monkeypatch)
        monkeypatch.setattr(sys, "argv", ["agents-marketplace", "sync"])
        commands.main()
        assert (
            captured["filename"] == MANIFEST_NAME
        ), f"Wrong default filename: {captured['filename']}"

    def test_sync_cli_with_filename_flag_forwards_custom_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured = _stub_run_sync(monkeypatch)
        monkeypatch.setattr(
            sys, "argv", ["agents-marketplace", "sync", "--filename", "custom.yaml"]
        )
        commands.main()
        assert (
            captured["filename"] == "custom.yaml"
        ), f"Custom filename not forwarded: {captured['filename']}"

    def test_sync_cli_filename_flag_combined_with_all_and_force(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured = _stub_run_sync(monkeypatch)
        monkeypatch.setattr(
            sys,
            "argv",
            ["agents-marketplace", "sync", "--all", "--force", "--filename", "custom.yaml"],
        )
        commands.main()
        assert captured == {
            "install_all": True,
            "force": True,
            "filename": "custom.yaml",
        }, f"Flags not all forwarded correctly: {captured}"
