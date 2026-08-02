"""Tests for marketplace.cli.generate — manifest filename normalization and validation."""

import io
from pathlib import Path

import pytest
from rich.console import Console

from marketplace.cli.generate import flow, prompts
from marketplace.consts.manifest import MANIFEST_NAME
from marketplace.kind_catalog.models import CatalogItem


class _FakeTextPrompt:
    def __init__(self, answer: str) -> None:
        self._answer = answer

    def execute(self) -> str:
        return self._answer


def _stub_answer(monkeypatch: pytest.MonkeyPatch, answer: str) -> None:
    monkeypatch.setattr(prompts.inquirer, "text", lambda **_: _FakeTextPrompt(answer))


class TestPromptManifestFilename:
    @pytest.mark.parametrize("answer", ["", "   "], ids=["empty", "whitespace_only"])
    def test_prompt_manifest_filename_blank_answer_returns_default(
        self, monkeypatch: pytest.MonkeyPatch, answer: str
    ) -> None:
        _stub_answer(monkeypatch, answer)
        assert (
            prompts.prompt_manifest_filename() == MANIFEST_NAME
        ), f"Blank answer must fall back to {MANIFEST_NAME}"

    def test_prompt_manifest_filename_no_extension_appends_yaml(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _stub_answer(monkeypatch, "custom")
        assert (
            prompts.prompt_manifest_filename() == "custom.yaml"
        ), "Filename without an extension must get .yaml appended"

    @pytest.mark.parametrize(
        "answer", ["custom.yaml", "custom.yml"], ids=["yaml_extension", "yml_extension"]
    )
    def test_prompt_manifest_filename_existing_extension_left_unchanged(
        self, monkeypatch: pytest.MonkeyPatch, answer: str
    ) -> None:
        _stub_answer(monkeypatch, answer)
        assert (
            prompts.prompt_manifest_filename() == answer
        ), f"Filename already ending in .yaml/.yml must not be altered, got different from {answer}"

    def test_prompt_manifest_filename_strips_surrounding_whitespace(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _stub_answer(monkeypatch, "  custom.yaml  ")
        assert (
            prompts.prompt_manifest_filename() == "custom.yaml"
        ), "Surrounding whitespace must be stripped before use"


def _quiet_console() -> Console:
    return Console(file=io.StringIO(), force_terminal=False)


class TestRunGeneratePathTraversal:
    def test_run_generate_path_traversal_filename_reports_error_without_writing(
        self, monkeypatch: pytest.MonkeyPatch, sample_skill: CatalogItem, project_dir: Path
    ) -> None:
        project_dir.mkdir(parents=True)
        monkeypatch.setattr(flow, "load_catalog", lambda: [sample_skill])
        monkeypatch.setattr(
            flow.prompts, "prompt_items", lambda catalog, project_dir: [sample_skill]
        )
        monkeypatch.setattr(
            flow.prompts,
            "prompt_all_targets",
            lambda console, selected, detected: (["claude"], [], [], []),
        )
        monkeypatch.setattr(flow.prompts, "prompt_manifest_filename", lambda: "../escaped.yaml")

        console = _quiet_console()
        flow.run_generate(console, project_dir)

        assert (
            "Invalid" in console.file.getvalue()
        ), f"Expected an invalid-filename message, got: {console.file.getvalue()!r}"
        assert not (
            project_dir.parent / "escaped.yaml"
        ).exists(), "Nothing must be written outside project_dir"
