"""Tests for marketplace.manifest and the non-interactive sync flow."""

import io
from pathlib import Path

import pytest
from rich.console import Console

from marketplace.catalog import CatalogItem
from marketplace.cli import run_sync
from marketplace.manifest import (
    MANIFEST_HEADER,
    MANIFEST_NAME,
    ManifestError,
    load_manifest,
    resolve_items,
    save_manifest,
)


def _write_manifest(project_dir: Path, content: str) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / MANIFEST_NAME).write_text(content, encoding="utf-8")


def _quiet_console() -> Console:
    return Console(file=io.StringIO(), force_terminal=False)


class TestLoadManifest:
    def test_load_manifest_missing_file_returns_none(self, project_dir: Path) -> None:
        assert load_manifest(project_dir) is None, "Missing manifest must return None"

    def test_load_manifest_parses_ids_and_targets(self, project_dir: Path) -> None:
        _write_manifest(
            project_dir,
            "skills: [a, b]\nrules: [c]\ntargets:\n  skills: [agents]\n  rules: [cursor, claude]\n",
        )
        manifest = load_manifest(project_dir)
        assert manifest is not None, "Manifest file exists but was not parsed"
        assert manifest.skills == ["a", "b"], f"Wrong skills: {manifest.skills}"
        assert manifest.rules == ["c"], f"Wrong rules: {manifest.rules}"
        assert manifest.skill_targets == ["agents"], f"Wrong targets: {manifest.skill_targets}"
        assert manifest.rule_targets == [
            "cursor",
            "claude",
        ], f"Wrong rule targets: {manifest.rule_targets}"

    def test_load_manifest_all_keyword_parses_to_none(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "rules: all\n")
        manifest = load_manifest(project_dir)
        assert manifest is not None and manifest.rules is None, "'all' keyword must parse to None"

    def test_load_manifest_non_list_kind_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "skills: 42\n")
        with pytest.raises(ManifestError, match="list of artifact ids"):
            load_manifest(project_dir)

    def test_load_manifest_unknown_rule_target_raises_manifest_error(
        self, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "rules: [x]\ntargets:\n  rules: [vim]\n")
        with pytest.raises(ManifestError, match="Unknown rule targets"):
            load_manifest(project_dir)

    def test_load_manifest_non_mapping_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "- just\n- a\n- list\n")
        with pytest.raises(ManifestError, match="YAML mapping"):
            load_manifest(project_dir)


class TestResolveItems:
    def test_resolve_items_matches_ids_and_reports_missing(
        self, sample_skill: CatalogItem, sample_rule: CatalogItem, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "skills: [sample-skill, ghost]\nrules: [sample-rule]\n")
        manifest = load_manifest(project_dir)
        assert manifest is not None
        selected, missing = resolve_items(manifest, [sample_skill, sample_rule])
        assert [item.id for item in selected] == [
            "sample-skill",
            "sample-rule",
        ], f"Wrong selection: {[item.id for item in selected]}"
        assert missing == ["skill:ghost"], f"Wrong missing refs: {missing}"

    def test_resolve_items_all_selects_every_item_of_kind(
        self, sample_skill: CatalogItem, sample_rule: CatalogItem, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "rules: all\n")
        manifest = load_manifest(project_dir)
        assert manifest is not None
        selected, missing = resolve_items(manifest, [sample_skill, sample_rule])
        assert [item.id for item in selected] == [
            "sample-rule"
        ], f"'all' must select rules only: {[item.id for item in selected]}"
        assert not missing, f"Unexpected missing refs: {missing}"


class TestSaveManifest:
    def test_save_manifest_roundtrips_through_load(
        self, sample_skill: CatalogItem, sample_rule: CatalogItem, project_dir: Path
    ) -> None:
        project_dir.mkdir(parents=True)
        save_manifest(project_dir, [sample_skill, sample_rule], ["agents"], ["cursor"])
        manifest = load_manifest(project_dir)
        assert manifest is not None, "Saved manifest could not be loaded back"
        assert manifest.skills == ["sample-skill"], f"Wrong skills: {manifest.skills}"
        assert manifest.rules == ["sample-rule"], f"Wrong rules: {manifest.rules}"
        assert manifest.skill_targets == ["agents"], f"Wrong targets: {manifest.skill_targets}"
        assert manifest.rule_targets == ["cursor"], f"Wrong rule targets: {manifest.rule_targets}"

    def test_save_manifest_starts_with_sync_command_header(
        self, sample_skill: CatalogItem, project_dir: Path
    ) -> None:
        project_dir.mkdir(parents=True)
        path = save_manifest(project_dir, [sample_skill], ["agents"], [])
        text = path.read_text(encoding="utf-8")
        assert text.startswith(MANIFEST_HEADER), f"Header comment missing:\n{text[:200]}"
        assert "agents-marketplace sync" in text, "Header must show the sync command"


class TestRunSync:
    def test_run_sync_installs_manifest_selection_to_declared_targets(
        self, project_dir: Path
    ) -> None:
        _write_manifest(
            project_dir,
            "skills: [python-code-review]\nrules: [no-debug-code]\n"
            "targets:\n  skills: [agents]\n  rules: [claude]\n",
        )
        run_sync(_quiet_console(), project_dir)
        skill_file = project_dir / ".agents/skills/python-code-review/SKILL.md"
        rule_file = project_dir / ".claude/rules/no-debug-code.md"
        assert skill_file.is_file(), "sync did not install the declared skill"
        assert rule_file.is_file(), "sync did not install the declared rule"
        assert not (project_dir / ".cursor").exists(), "sync wrote to an undeclared target"

    def test_run_sync_missing_manifest_exits_with_error(self, project_dir: Path) -> None:
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir)

    def test_run_sync_unknown_id_installs_rest_but_exits_nonzero(self, project_dir: Path) -> None:
        _write_manifest(
            project_dir,
            "skills: [ghost-skill, python-code-review]\ntargets:\n  skills: [agents]\n",
        )
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir)
        assert (
            project_dir / ".agents/skills/python-code-review/SKILL.md"
        ).is_file(), "known items must still install when others are missing"

    def test_run_sync_invalid_manifest_exits_with_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "skills: 42\n")
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir)
