"""Tests for marketplace.manifest and the non-interactive sync flow."""

import io
from pathlib import Path

import pytest
from rich.console import Console

from marketplace.cli import run_sync
from marketplace.kind_catalog.models import CatalogItem
from marketplace.manifest import (
    MANIFEST_HEADER,
    MANIFEST_NAME,
    ManifestError,
    load_manifest,
    resolve_per_agent,
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

    def test_load_manifest_parses_per_agent_entries(self, project_dir: Path) -> None:
        _write_manifest(
            project_dir,
            "claude:\n  skills: [a, b]\n  rules: [c]\nagents:\n  skills: [a]\n",
        )
        manifest = load_manifest(project_dir)
        assert manifest is not None
        assert manifest.per_agent == {
            "claude": {"skills": ["a", "b"], "rules": ["c"]},
            "agents": {"skills": ["a"]},
        }, f"Wrong per_agent: {manifest.per_agent}"

    def test_load_manifest_all_keyword_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "gemini:\n  rules: all\n")
        with pytest.raises(ManifestError, match="list of strings"):
            load_manifest(project_dir)

    def test_load_manifest_unknown_target_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "vim:\n  rules: [x]\n")
        with pytest.raises(ManifestError, match="Unknown target"):
            load_manifest(project_dir)

    def test_load_manifest_skill_on_rule_only_target_raises_manifest_error(
        self, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "cursor:\n  skills: [x]\n")
        with pytest.raises(ManifestError, match="does not support skills"):
            load_manifest(project_dir)

    def test_load_manifest_rule_on_skill_only_target_raises_manifest_error(
        self, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "agents:\n  rules: [x]\n")
        with pytest.raises(ManifestError, match="does not support rules"):
            load_manifest(project_dir)

    def test_load_manifest_non_list_kind_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "claude:\n  skills: 42\n")
        with pytest.raises(ManifestError, match="list of strings"):
            load_manifest(project_dir)

    def test_load_manifest_non_mapping_raises_manifest_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "- just\n- a\n- list\n")
        with pytest.raises(ManifestError, match="YAML mapping"):
            load_manifest(project_dir)

    def test_load_manifest_non_mapping_agent_entry_raises_manifest_error(
        self, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "claude: [skills]\n")
        with pytest.raises(ManifestError, match="must be a mapping"):
            load_manifest(project_dir)


class TestResolvePerAgent:
    def test_resolve_per_agent_matches_items_per_target(
        self, sample_skill: CatalogItem, sample_rule: CatalogItem, project_dir: Path
    ) -> None:
        _write_manifest(
            project_dir,
            "claude:\n  skills: [sample-skill]\n  rules: [sample-rule]\n"
            "cursor:\n  rules: [sample-rule]\n",
        )
        manifest = load_manifest(project_dir)
        assert manifest is not None
        per_target, missing = resolve_per_agent(manifest, [sample_skill, sample_rule])
        assert not missing, f"Unexpected missing: {missing}"
        assert [item.id for item in per_target["claude"]] == [
            "sample-skill",
            "sample-rule",
        ], f"claude items wrong: {[i.id for i in per_target['claude']]}"
        assert [item.id for item in per_target["cursor"]] == [
            "sample-rule"
        ], f"cursor items wrong: {[i.id for i in per_target['cursor']]}"

    def test_resolve_per_agent_missing_id_reported(
        self, sample_skill: CatalogItem, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "claude:\n  skills: [sample-skill, ghost]\n")
        manifest = load_manifest(project_dir)
        assert manifest is not None
        per_target, missing = resolve_per_agent(manifest, [sample_skill])
        assert missing == ["skill:ghost"], f"Wrong missing refs: {missing}"
        assert [item.id for item in per_target["claude"]] == [
            "sample-skill"
        ], f"Known item must still be resolved: {[i.id for i in per_target['claude']]}"

    def test_resolve_per_agent_target_not_in_manifest_not_in_result(
        self, sample_skill: CatalogItem, project_dir: Path
    ) -> None:
        _write_manifest(project_dir, "claude:\n  skills: [sample-skill]\n")
        manifest = load_manifest(project_dir)
        assert manifest is not None
        per_target, _ = resolve_per_agent(manifest, [sample_skill])
        assert "cursor" not in per_target, "cursor not in manifest must not appear in result"


class TestSaveManifest:
    def test_save_manifest_roundtrips_through_load(
        self, sample_skill: CatalogItem, sample_rule: CatalogItem, project_dir: Path
    ) -> None:
        project_dir.mkdir(parents=True)
        per_target = {
            "claude": [sample_skill, sample_rule],
            "cursor": [sample_rule],
        }
        save_manifest(project_dir, per_target)
        manifest = load_manifest(project_dir)
        assert manifest is not None
        assert manifest.per_agent == {
            "claude": {"skills": ["sample-skill"], "rules": ["sample-rule"]},
            "cursor": {"rules": ["sample-rule"]},
        }, f"Wrong per_agent after roundtrip: {manifest.per_agent}"

    def test_save_manifest_starts_with_sync_command_header(
        self, sample_skill: CatalogItem, project_dir: Path
    ) -> None:
        project_dir.mkdir(parents=True)
        path = save_manifest(project_dir, {"agents": [sample_skill]})
        text = path.read_text(encoding="utf-8")
        assert text.startswith(MANIFEST_HEADER), f"Header missing:\n{text[:200]}"
        assert "agents-marketplace sync" in text, "Header must show the sync command"

    def test_save_manifest_omits_empty_targets(self, project_dir: Path) -> None:
        project_dir.mkdir(parents=True)
        save_manifest(project_dir, {"claude": [], "agents": []})
        manifest = load_manifest(project_dir)
        assert manifest is not None
        assert "claude" not in manifest.per_agent, "Empty claude target must be omitted"
        assert "agents" not in manifest.per_agent, "Empty agents target must be omitted"


class TestRunSync:
    def test_run_sync_installs_per_target_as_declared(self, project_dir: Path) -> None:
        _write_manifest(
            project_dir,
            "claude:\n  skills: [create-skill]\n  rules: [no-debug-code]\n"
            "cursor:\n  rules: [no-debug-code]\n",
        )
        run_sync(_quiet_console(), project_dir, install_all=True)
        assert (project_dir / ".claude/skills/create-skill/SKILL.md").is_file()
        assert (project_dir / ".claude/rules/no-debug-code.md").is_file()
        assert (project_dir / ".cursor/rules/no-debug-code.mdc").is_file()
        assert not (project_dir / ".agents").exists(), "agents not in manifest must not be written"

    def test_run_sync_agents_target_installs_to_agents_dir(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "agents:\n  skills: [create-skill]\n")
        run_sync(_quiet_console(), project_dir, install_all=True)
        assert (project_dir / ".agents/skills/create-skill/SKILL.md").is_file()
        assert not (project_dir / ".claude").exists(), "claude not in manifest must not be written"

    def test_run_sync_missing_manifest_exits_with_error(self, project_dir: Path) -> None:
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir, install_all=True)

    def test_run_sync_unknown_id_installs_rest_but_exits_nonzero(self, project_dir: Path) -> None:
        _write_manifest(
            project_dir,
            "agents:\n  skills: [ghost-skill, create-skill]\n",
        )
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir, install_all=True)
        assert (
            project_dir / ".agents/skills/create-skill/SKILL.md"
        ).is_file(), "known items must still install when others are missing"

    def test_run_sync_invalid_manifest_exits_with_error(self, project_dir: Path) -> None:
        _write_manifest(project_dir, "claude:\n  skills: 42\n")
        with pytest.raises(SystemExit, match="1"):
            run_sync(_quiet_console(), project_dir, install_all=True)
