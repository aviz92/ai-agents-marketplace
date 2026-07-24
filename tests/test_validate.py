"""Tests for marketplace.kind_catalog.validate — surfacing what the loader silently skips."""

from pathlib import Path

import pytest
from rich.console import Console

import marketplace.cli.validate as cli_validate
from marketplace.kind_catalog.validate import validate_catalog
from utils import get_marketplace_root


def _write_item(root: Path, kind_dir: str, item_id: str, metadata: str, body_file: str) -> None:
    item_dir = root / kind_dir / item_id
    item_dir.mkdir(parents=True)
    (item_dir / "metadata.yaml").write_text(metadata, encoding="utf-8")
    (item_dir / body_file).write_text("# Body\n", encoding="utf-8")


class TestValidateCatalog:
    def test_validate_catalog_empty_root_returns_no_issues(self, tmp_path: Path) -> None:
        assert not validate_catalog(tmp_path), "Empty root must produce no issues"

    def test_validate_catalog_real_repo_has_no_errors(self) -> None:
        issues = validate_catalog(get_marketplace_root())
        errors = [issue for issue in issues if issue.severity == "error"]
        assert errors == [], f"Repo's own catalog must be error-free: {errors}"

    def test_validate_catalog_valid_item_produces_no_issues(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path,
            "rules",
            "my-rule",
            "name: My Rule\ndescription: desc\nauthor: avi\nversion: 1.0.0\n"
            'globs: ["**/*.py"]\nalwaysApply: false\n',
            "rule.md",
        )
        assert not validate_catalog(tmp_path), "Fully specified item must have no issues"

    def test_validate_catalog_missing_metadata_file_reports_error(self, tmp_path: Path) -> None:
        item_dir = tmp_path / "skills" / "no-metadata"
        item_dir.mkdir(parents=True)
        (item_dir / "skill.md").write_text("# Body\n", encoding="utf-8")
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "error", f"Wrong severity: {issues[0]}"
        assert "metadata.yaml" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_missing_body_file_reports_error(self, tmp_path: Path) -> None:
        item_dir = tmp_path / "skills" / "no-body"
        item_dir.mkdir(parents=True)
        (item_dir / "metadata.yaml").write_text("name: X\ndescription: d\n", encoding="utf-8")
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "error", f"Wrong severity: {issues[0]}"
        assert "skill.md" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_malformed_yaml_reports_error(self, tmp_path: Path) -> None:
        _write_item(tmp_path, "skills", "bad-yaml", "name: [unclosed\n", "skill.md")
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "error", f"Wrong severity: {issues[0]}"
        assert "invalid metadata.yaml" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_invalid_model_strength_reports_error(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path, "subagents", "bad", "name: Bad\nmodel_strength: nope\n", "subagent.md"
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "error", f"Wrong severity: {issues[0]}"
        assert "model_strength" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_external_plugin_missing_source_reports_error(
        self, tmp_path: Path
    ) -> None:
        item_dir = tmp_path / "external-plugins" / "no-source"
        item_dir.mkdir(parents=True)
        (item_dir / "metadata.yaml").write_text(
            "name: X\ndescription: d\ninstall: 'curl foo'\n", encoding="utf-8"
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "error", f"Wrong severity: {issues[0]}"

    def test_validate_catalog_missing_description_reports_warning_only(
        self, tmp_path: Path
    ) -> None:
        _write_item(
            tmp_path, "skills", "no-desc", "name: X\nauthor: avi\nversion: 1.0.0\n", "skill.md"
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "warning", f"Wrong severity: {issues[0]}"
        assert "description" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_missing_name_reports_warning_only(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path,
            "skills",
            "no-name",
            "description: d\nauthor: avi\nversion: 1.0.0\n",
            "skill.md",
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "warning", f"Wrong severity: {issues[0]}"
        assert "name" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_missing_author_reports_warning_only(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path,
            "skills",
            "no-author",
            "name: X\ndescription: d\nversion: 1.0.0\n",
            "skill.md",
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "warning", f"Wrong severity: {issues[0]}"
        assert "author" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_missing_version_reports_warning_only(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path, "skills", "no-version", "name: X\ndescription: d\nauthor: avi\n", "skill.md"
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "warning", f"Wrong severity: {issues[0]}"
        assert "version" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_rule_no_globs_no_always_apply_reports_warning(
        self, tmp_path: Path
    ) -> None:
        _write_item(
            tmp_path,
            "rules",
            "dead-rule",
            "name: X\ndescription: d\nauthor: avi\nversion: 1.0.0\n",
            "rule.md",
        )
        issues = validate_catalog(tmp_path)
        assert len(issues) == 1, f"Expected exactly one issue, got {issues}"
        assert issues[0].severity == "warning", f"Wrong severity: {issues[0]}"
        assert "globs" in issues[0].message, f"Wrong message: {issues[0].message}"

    def test_validate_catalog_rule_always_apply_without_globs_produces_no_issues(
        self, tmp_path: Path
    ) -> None:
        _write_item(
            tmp_path,
            "rules",
            "always-rule",
            "name: X\ndescription: d\nauthor: avi\nversion: 1.0.0\nalwaysApply: true\n",
            "rule.md",
        )
        assert not validate_catalog(tmp_path), "alwaysApply=true rule needs no globs"

    def test_validate_catalog_rule_globs_without_always_apply_produces_no_issues(
        self, tmp_path: Path
    ) -> None:
        _write_item(
            tmp_path,
            "rules",
            "glob-rule",
            'name: X\ndescription: d\nauthor: avi\nversion: 1.0.0\nglobs: ["**/*.py"]\n',
            "rule.md",
        )
        assert not validate_catalog(tmp_path), "Rule with globs needs no alwaysApply"

    def test_validate_catalog_non_rule_kind_ignores_globs_check(self, tmp_path: Path) -> None:
        _write_item(
            tmp_path,
            "skills",
            "min",
            "name: X\ndescription: d\nauthor: avi\nversion: 1.0.0\n",
            "skill.md",
        )
        assert not validate_catalog(tmp_path), "Skills must not be checked for globs/alwaysApply"


class TestRunValidate:
    def test_run_validate_clean_catalog_returns_zero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(cli_validate, "get_marketplace_root", lambda: tmp_path)
        assert cli_validate.run_validate(Console(quiet=True)) == 0, "Clean catalog must exit 0"

    def test_run_validate_warning_only_returns_zero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _write_item(tmp_path, "skills", "no-desc", "name: X\n", "skill.md")
        monkeypatch.setattr(cli_validate, "get_marketplace_root", lambda: tmp_path)
        assert cli_validate.run_validate(Console(quiet=True)) == 0, "Warnings alone must exit 0"

    def test_run_validate_error_returns_one(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        item_dir = tmp_path / "skills" / "no-metadata"
        item_dir.mkdir(parents=True)
        (item_dir / "skill.md").write_text("# Body\n", encoding="utf-8")
        monkeypatch.setattr(cli_validate, "get_marketplace_root", lambda: tmp_path)
        assert cli_validate.run_validate(Console(quiet=True)) == 1, "Any error must exit 1"
