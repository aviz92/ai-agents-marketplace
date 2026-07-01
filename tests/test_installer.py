"""Tests for marketplace.installer — rendering and writing artifacts into a project."""

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from marketplace.cli.sync.render import print_results
from marketplace.installer import (
    InstallResult,
    install_rules_to_target,
    install_skills_to_target,
    install_to_target,
    rule_targets,
    targets,
)
from marketplace.kind_catalog.models import CatalogItem, Command, Rule, Skill

TARGETS = targets()
RULE_TARGETS = rule_targets()


class TestInstallSkillsToTarget:
    def test_install_skills_to_target_claude_writes_skill_md_and_creates_claude_md(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        result = install_skills_to_target("claude", [sample_skill], project_dir)
        skill_file = project_dir / ".claude/skills/sample-skill/SKILL.md"
        claude_md = project_dir / ".claude/CLAUDE.md"
        assert skill_file.is_file(), "SKILL.md was not written"
        assert claude_md.read_text() == "Refer to ../AGENTS.md\n", "CLAUDE.md fallback wrong"
        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert (
            ".claude/skills/sample-skill/SKILL.md" in result.files_written
        ), f"files_written missing skill file: {result.files_written}"

    def test_install_skills_to_target_claude_existing_claude_md_is_not_overwritten(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        claude_md = project_dir / ".claude/CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("custom content\n", encoding="utf-8")
        install_skills_to_target("claude", [sample_skill], project_dir)
        assert claude_md.read_text() == "custom content\n", "Existing CLAUDE.md was overwritten"

    def test_install_skills_to_target_agents_writes_skill_md_without_claude_md(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_skill], project_dir)
        assert (
            project_dir / ".agents/skills/sample-skill/SKILL.md"
        ).is_file(), "SKILL.md missing under .agents/skills"
        assert not (
            project_dir / ".claude/CLAUDE.md"
        ).exists(), "agents target must not create CLAUDE.md"

    def test_install_skills_to_target_rendered_skill_has_version_frontmatter(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_skill], project_dir)
        text = (project_dir / ".agents/skills/sample-skill/SKILL.md").read_text()
        assert "version: 1.0.0" in text, f"version frontmatter missing:\n{text}"
        assert "# Sample skill body" in text, f"body missing:\n{text}"

    def test_install_skills_to_target_skill_with_assets_copies_them_alongside_skill_md(
        self, project_dir: Path, tmp_path: Path
    ) -> None:
        authored = tmp_path / "authored" / "with-assets"
        (authored / "assets").mkdir(parents=True)
        (authored / "metadata.yaml").write_text("name: With Assets\n", encoding="utf-8")
        (authored / "skill.md").write_text("# Body\n", encoding="utf-8")
        (authored / "assets" / "template.md").write_text("# Template\n", encoding="utf-8")
        item = Skill(
            id="with-assets",
            name="With Assets",
            description="",
            content="# Body\n",
            path=authored,
        )
        result = install_skills_to_target("agents", [item], project_dir)
        asset = project_dir / ".agents/skills/with-assets/assets/template.md"
        assert asset.read_text() == "# Template\n", "asset not copied next to SKILL.md"
        assert (
            ".agents/skills/with-assets/assets/template.md" in result.files_written
        ), f"asset missing from files_written: {result.files_written}"

    def test_install_skills_to_target_item_without_authored_path_copies_no_assets(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        result = install_skills_to_target("agents", [sample_skill], project_dir)
        assert result.files_written == [
            ".agents/skills/sample-skill/SKILL.md"
        ], f"constructed item must write only SKILL.md, got {result.files_written}"

    def test_install_skills_to_target_unknown_target_raises_key_error(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        with pytest.raises(KeyError, match="nope"):
            install_skills_to_target("nope", [sample_skill], project_dir)

    def test_install_skills_to_target_no_items_writes_nothing_but_succeeds(
        self, project_dir: Path
    ) -> None:
        result = install_skills_to_target("agents", [], project_dir)
        assert result.installed == 0, "Expected zero installs for empty selection"
        assert not result.files_written, f"Unexpected files: {result.files_written}"


class TestInstallPluginToTarget:
    def test_install_plugin_writes_plugin_md_not_skill_md(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        result = install_skills_to_target("agents", [sample_plugin], project_dir)
        plugin_file = project_dir / ".agents/skills/sample-plugin/PLUGIN.md"
        skill_file = project_dir / ".agents/skills/sample-plugin/SKILL.md"
        assert plugin_file.is_file(), "PLUGIN.md was not written"
        assert not skill_file.exists(), "SKILL.md must not be written for a plugin"
        assert ".agents/skills/sample-plugin/PLUGIN.md" in result.files_written

    def test_install_plugin_rendered_output_has_version_frontmatter(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_plugin], project_dir)
        text = (project_dir / ".agents/skills/sample-plugin/PLUGIN.md").read_text()
        assert "version: 1.0.0" in text, f"version frontmatter missing:\n{text}"
        assert "# Sample plugin body" in text, f"body missing:\n{text}"

    def test_install_plugin_to_claude_target_writes_plugin_md_and_claude_md(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_skills_to_target("claude", [sample_plugin], project_dir)
        assert (project_dir / ".claude/skills/sample-plugin/PLUGIN.md").is_file()
        assert (project_dir / ".claude/CLAUDE.md").is_file(), "CLAUDE.md fallback not created"


class TestInstallRulesToTarget:
    @pytest.mark.parametrize("target_id", sorted(RULE_TARGETS))
    def test_install_rules_to_target_writes_native_file_with_version(
        self, project_dir: Path, sample_rule: CatalogItem, target_id: str
    ) -> None:
        target = RULE_TARGETS[target_id]
        install_rules_to_target(target_id, [sample_rule], project_dir)
        out = project_dir / target.dir / target.filename_pattern.format(id=sample_rule.id)
        assert out.is_file(), f"{target_id}: native rule file not written at {out}"
        text = out.read_text()
        assert "version: 1.0.0" in text, f"{target_id}: version frontmatter missing:\n{text}"
        assert "# Sample rule body" in text, f"{target_id}: body missing:\n{text}"

    def test_install_rules_to_target_cursor_frontmatter_has_globs_and_always_apply(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("cursor", [sample_rule], project_dir)
        text = (project_dir / ".cursor/rules/sample-rule.mdc").read_text()
        assert 'globs: ["src/**/*.py"]' in text, f"globs missing:\n{text}"
        assert "alwaysApply: true" in text, f"alwaysApply missing:\n{text}"

    def test_install_rules_to_target_cursor_without_globs_omits_globs_line(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        sample_rule.globs = []
        sample_rule.always_apply = False
        install_rules_to_target("cursor", [sample_rule], project_dir)
        text = (project_dir / ".cursor/rules/sample-rule.mdc").read_text()
        assert "globs:" not in text, f"globs line must be omitted when empty:\n{text}"
        assert "alwaysApply: false" in text, f"alwaysApply false missing:\n{text}"

    def test_install_rules_to_target_copilot_apply_to_joins_globs(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        sample_rule.globs = ["src/**/*.py", "tests/**/*.py"]
        install_rules_to_target("copilot", [sample_rule], project_dir)
        text = (project_dir / ".github/instructions/sample-rule.instructions.md").read_text()
        assert 'applyTo: "src/**/*.py,tests/**/*.py"' in text, f"applyTo wrong:\n{text}"

    def test_install_rules_to_target_copilot_without_globs_applies_to_everything(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        sample_rule.globs = []
        install_rules_to_target("copilot", [sample_rule], project_dir)
        text = (project_dir / ".github/instructions/sample-rule.instructions.md").read_text()
        assert 'applyTo: "**"' in text, f"applyTo fallback wrong:\n{text}"


class TestReferenceInjection:
    def test_install_rules_codex_no_agents_md_creates_fallback(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("codex", [sample_rule], project_dir)
        agents_md = project_dir / "AGENTS.md"
        assert agents_md.is_file(), "AGENTS.md fallback was not created"
        assert ".codex/rules" in agents_md.read_text(), "fallback must mention .codex/rules"

    def test_install_rules_codex_existing_agents_md_gets_note_appended(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        project_dir.mkdir(parents=True)
        agents_md = project_dir / "AGENTS.md"
        agents_md.write_text("# Existing\n", encoding="utf-8")
        install_rules_to_target("codex", [sample_rule], project_dir)
        text = agents_md.read_text()
        assert text.startswith("# Existing\n"), f"Existing content lost:\n{text}"
        assert ".codex/rules" in text, f"Reference note not appended:\n{text}"

    def test_install_rules_rerun_does_not_duplicate_reference(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("gemini", [sample_rule], project_dir)
        first = (project_dir / "GEMINI.md").read_text()
        install_rules_to_target("gemini", [sample_rule], project_dir)
        second = (project_dir / "GEMINI.md").read_text()
        assert first == second, "Re-running the install duplicated the reference note"

    def test_install_rules_claude_appends_to_existing_claude_md(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        claude_md = project_dir / ".claude/CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("Refer to ../AGENTS.md\n", encoding="utf-8")
        install_rules_to_target("claude", [sample_rule], project_dir)
        text = claude_md.read_text()
        assert ".claude/rules" in text, f"Reference note not appended:\n{text}"

    @pytest.mark.parametrize("target_id", ["cursor", "copilot"])
    def test_install_rules_auto_discovering_targets_write_no_reference_file(
        self, project_dir: Path, sample_rule: CatalogItem, target_id: str
    ) -> None:
        result = install_rules_to_target(target_id, [sample_rule], project_dir)
        assert (
            len(result.files_written) == 1
        ), f"{target_id} must write only the rule file, got {result.files_written}"


class TestTargetRegistries:
    def test_targets_registry_covers_expected_skill_dirs(self) -> None:
        dirs = {target.dir for target in TARGETS.values()}
        assert dirs == {".claude/skills", ".agents/skills"}, f"Unexpected dirs: {dirs}"

    def test_rule_targets_registry_has_all_five_agents(self) -> None:
        expected = {"cursor", "copilot", "claude", "codex", "gemini"}
        assert set(RULE_TARGETS) == expected, f"Unexpected rule targets: {set(RULE_TARGETS)}"


class TestForceFlag:
    def test_install_skill_without_force_skips_existing_file(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_skill], project_dir)
        skill_file = project_dir / ".agents/skills/sample-skill/SKILL.md"
        skill_file.write_text("custom content\n", encoding="utf-8")

        result = install_skills_to_target("agents", [sample_skill], project_dir, False)

        assert skill_file.read_text() == "custom content\n", "File overwritten despite force=False"
        assert result.installed == 0, f"Expected 0 installed, got {result.installed}"
        assert not result.files_written, f"Expected no files written, got {result.files_written}"
        assert (
            ".agents/skills/sample-skill/SKILL.md" in result.files_skipped
        ), f"Expected skipped file in files_skipped: {result.files_skipped}"

    def test_install_skill_with_force_overwrites_existing_file(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_skill], project_dir)
        skill_file = project_dir / ".agents/skills/sample-skill/SKILL.md"
        skill_file.write_text("custom content\n", encoding="utf-8")

        result = install_skills_to_target("agents", [sample_skill], project_dir, True)

        assert (
            "custom content" not in skill_file.read_text()
        ), "File not overwritten with force=True"
        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert not result.files_skipped, f"Expected no skipped files, got {result.files_skipped}"

    def test_install_skill_without_force_installs_when_file_missing(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        result = install_skills_to_target("agents", [sample_skill], project_dir, False)

        skill_file = project_dir / ".agents/skills/sample-skill/SKILL.md"
        assert skill_file.is_file(), "SKILL.md not written when file was missing"
        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert not result.files_skipped, f"Expected no skipped files, got {result.files_skipped}"

    def test_install_skill_without_force_partial_skip_mixed_items(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        new_skill = Skill(
            id="new-skill",
            name="New Skill",
            description="",
            version="1.0.0",
            content="# New skill\n",
        )
        install_skills_to_target("agents", [sample_skill], project_dir)
        (project_dir / ".agents/skills/sample-skill/SKILL.md").write_text(
            "custom content\n", encoding="utf-8"
        )

        result = install_skills_to_target("agents", [sample_skill, new_skill], project_dir, False)

        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert len(result.files_skipped) == 1, f"Expected 1 skipped, got {result.files_skipped}"
        assert ".agents/skills/sample-skill/SKILL.md" in result.files_skipped
        assert ".agents/skills/new-skill/SKILL.md" in result.files_written

    def test_install_rule_without_force_skips_existing_file(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("gemini", [sample_rule], project_dir)
        rule_file = project_dir / ".gemini/rules/sample-rule.md"
        rule_file.write_text("custom content\n", encoding="utf-8")

        result = install_rules_to_target("gemini", [sample_rule], project_dir, False)

        assert rule_file.read_text() == "custom content\n", "Rule overwritten despite force=False"
        assert result.installed == 0, f"Expected 0 installed, got {result.installed}"
        assert (
            ".gemini/rules/sample-rule.md" in result.files_skipped
        ), f"Expected skipped rule in files_skipped: {result.files_skipped}"

    def test_install_rule_with_force_overwrites_existing_file(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("gemini", [sample_rule], project_dir)
        rule_file = project_dir / ".gemini/rules/sample-rule.md"
        rule_file.write_text("custom content\n", encoding="utf-8")

        result = install_rules_to_target("gemini", [sample_rule], project_dir, True)

        assert "custom content" not in rule_file.read_text(), "Rule not overwritten with force=True"
        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert not result.files_skipped, f"Expected no skipped files, got {result.files_skipped}"

    def test_install_command_without_force_skips_existing_file(
        self, project_dir: Path, sample_command: Command
    ) -> None:
        install_to_target("claude", [sample_command], project_dir)
        command_file = project_dir / ".claude/commands/sample-command.md"
        command_file.write_text("custom content\n", encoding="utf-8")

        result = install_to_target("claude", [sample_command], project_dir, False)

        assert (
            command_file.read_text() == "custom content\n"
        ), "Command overwritten despite force=False"
        assert len(result) == 1, f"Expected 1 result, got {len(result)}"
        assert result[0].installed == 0, f"Expected 0 installed, got {result[0].installed}"
        assert (
            ".claude/commands/sample-command.md" in result[0].files_skipped
        ), f"Expected skipped command: {result[0].files_skipped}"

    def test_install_command_with_force_overwrites_existing_file(
        self, project_dir: Path, sample_command: Command
    ) -> None:
        install_to_target("claude", [sample_command], project_dir)
        command_file = project_dir / ".claude/commands/sample-command.md"
        command_file.write_text("custom content\n", encoding="utf-8")

        result = install_to_target("claude", [sample_command], project_dir, True)

        assert (
            "custom content" not in command_file.read_text()
        ), "Command not overwritten with force=True"
        assert result[0].installed == 1, f"Expected 1 installed, got {result[0].installed}"
        assert not result[0].files_skipped, f"Expected no skipped, got {result[0].files_skipped}"

    def test_install_plugin_without_force_skips_existing_file(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_plugin], project_dir)
        plugin_file = project_dir / ".agents/skills/sample-plugin/PLUGIN.md"
        plugin_file.write_text("custom content\n", encoding="utf-8")

        result = install_skills_to_target("agents", [sample_plugin], project_dir, False)

        assert (
            plugin_file.read_text() == "custom content\n"
        ), "Plugin overwritten despite force=False"
        assert result.installed == 0, f"Expected 0 installed, got {result.installed}"
        assert (
            ".agents/skills/sample-plugin/PLUGIN.md" in result.files_skipped
        ), f"Expected skipped plugin in files_skipped: {result.files_skipped}"

    def test_install_plugin_with_force_overwrites_existing_file(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_skills_to_target("agents", [sample_plugin], project_dir)
        plugin_file = project_dir / ".agents/skills/sample-plugin/PLUGIN.md"
        plugin_file.write_text("custom content\n", encoding="utf-8")

        result = install_skills_to_target("agents", [sample_plugin], project_dir, True)

        assert (
            "custom content" not in plugin_file.read_text()
        ), "Plugin not overwritten with force=True"
        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert not result.files_skipped, f"Expected no skipped, got {result.files_skipped}"

    def test_install_skill_without_force_skips_assets_when_main_file_exists(
        self, project_dir: Path, tmp_path: Path
    ) -> None:
        authored = tmp_path / "authored" / "with-assets"
        (authored / "assets").mkdir(parents=True)
        (authored / "metadata.yaml").write_text("name: With Assets\n", encoding="utf-8")
        (authored / "skill.md").write_text("# Body\n", encoding="utf-8")
        (authored / "assets" / "template.md").write_text("# Original\n", encoding="utf-8")
        item = Skill(
            id="with-assets", name="With Assets", description="", content="# Body\n", path=authored
        )

        install_skills_to_target("agents", [item], project_dir)
        skill_file = project_dir / ".agents/skills/with-assets/SKILL.md"
        asset_file = project_dir / ".agents/skills/with-assets/assets/template.md"
        skill_file.write_text("custom content\n", encoding="utf-8")
        (authored / "assets" / "template.md").write_text("# Updated\n", encoding="utf-8")

        result = install_skills_to_target("agents", [item], project_dir, False)

        assert (
            asset_file.read_text() == "# Original\n"
        ), "Asset updated despite force=False — _copy_assets must be skipped with main file"
        assert result.installed == 0, f"Expected 0 installed, got {result.installed}"
        assert not result.files_written, f"Expected no files written, got {result.files_written}"

    def test_install_rule_without_force_partial_skip_mixed_rules(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        new_rule = Rule(
            id="new-rule",
            name="New Rule",
            description="",
            version="1.0.0",
            globs=[],
            always_apply=False,
            content="# New rule\n",
        )
        install_rules_to_target("gemini", [sample_rule], project_dir)
        (project_dir / ".gemini/rules/sample-rule.md").write_text("custom\n", encoding="utf-8")

        result = install_rules_to_target("gemini", [sample_rule, new_rule], project_dir, False)

        assert result.installed == 1, f"Expected 1 installed, got {result.installed}"
        assert len(result.files_skipped) == 1, f"Expected 1 skipped: {result.files_skipped}"
        assert ".gemini/rules/sample-rule.md" in result.files_skipped
        assert ".gemini/rules/new-rule.md" in result.files_written

    def test_install_rule_without_force_creates_reference_even_when_rule_skipped(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        # Simulate: rule file exists (e.g. manually placed) but reference does not.
        rule_file = project_dir / ".gemini/rules/sample-rule.md"
        rule_file.parent.mkdir(parents=True)
        rule_file.write_text("manually placed\n", encoding="utf-8")

        result = install_rules_to_target("gemini", [sample_rule], project_dir, False)

        reference = project_dir / "GEMINI.md"
        assert (
            reference.is_file()
        ), "Reference file must be created even when all rule files were skipped"
        assert ".gemini/rules" in reference.read_text(), "Reference must point at rules dir"
        assert result.installed == 0, f"Expected 0 installed, got {result.installed}"
        assert ".gemini/rules/sample-rule.md" in result.files_skipped

    def test_install_to_target_without_force_skips_across_multiple_kinds(
        self, project_dir: Path, sample_skill: CatalogItem, sample_command: Command
    ) -> None:
        install_to_target("claude", [sample_skill, sample_command], project_dir)
        (project_dir / ".claude/skills/sample-skill/SKILL.md").write_text(
            "custom skill\n", encoding="utf-8"
        )
        (project_dir / ".claude/commands/sample-command.md").write_text(
            "custom command\n", encoding="utf-8"
        )

        results = install_to_target("claude", [sample_skill, sample_command], project_dir, False)

        skill_result = next(r for r in results if r.output_dir == ".claude/skills")
        command_result = next(r for r in results if r.output_dir == ".claude/commands")
        assert skill_result.installed == 0, f"Skill must be skipped, got {skill_result.installed}"
        assert (
            command_result.installed == 0
        ), f"Command must be skipped, got {command_result.installed}"
        assert ".claude/skills/sample-skill/SKILL.md" in skill_result.files_skipped
        assert ".claude/commands/sample-command.md" in command_result.files_skipped


class TestForceFlagRender:
    def _render(self, results: list[InstallResult]) -> str:
        buf = StringIO()
        print_results(Console(file=buf, width=120), results)
        return buf.getvalue()

    def test_print_results_no_skipped_shows_installed_only(self) -> None:
        result = InstallResult(
            target="claude",
            installed=2,
            files_written=["a/SKILL.md", "b/SKILL.md"],
            output_dir=".claude/skills",
        )
        output = self._render([result])
        assert "2 installed" in output, f"Expected '2 installed' in output:\n{output}"
        assert "skipped" not in output, f"'skipped' must not appear when none skipped:\n{output}"

    def test_print_results_with_skipped_shows_count_in_summary(self) -> None:
        result = InstallResult(
            target="claude",
            installed=1,
            files_written=["a/SKILL.md"],
            files_skipped=["b/SKILL.md", "c/SKILL.md"],
            output_dir=".claude/skills",
        )
        output = self._render([result])
        assert "1 installed" in output, f"Installed count missing:\n{output}"
        assert "2 skipped" in output, f"Skipped count missing:\n{output}"

    def test_print_results_with_skipped_lists_dim_already_installed_label(self) -> None:
        result = InstallResult(
            target="claude",
            installed=0,
            files_written=[],
            files_skipped=["x/SKILL.md"],
            output_dir=".claude/skills",
        )
        output = self._render([result])
        assert "x/SKILL.md" in output, f"Skipped file path missing:\n{output}"
        assert "already installed" in output, f"'already installed' label missing:\n{output}"

    def test_print_results_all_skipped_shows_zero_installed(self) -> None:
        result = InstallResult(
            target="agents",
            installed=0,
            files_written=[],
            files_skipped=["a/SKILL.md", "b/SKILL.md"],
            output_dir=".agents/skills",
        )
        output = self._render([result])
        assert "0 installed" in output, f"Expected '0 installed':\n{output}"
        assert "2 skipped" in output, f"Expected '2 skipped':\n{output}"
