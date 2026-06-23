"""Tests for marketplace.cli — installed-version detection, status logic, picker choices."""

from dataclasses import asdict
from pathlib import Path

from InquirerPy.base.control import Choice

from marketplace.catalog import CatalogItem
from marketplace.cli import (
    build_item_choices,
    collect_installed_state,
    get_installed_plugin_versions,
    get_installed_rule_versions,
    get_installed_versions,
    get_status_and_versions,
)
from marketplace.consts.display import STATUS_INSTALLED, STATUS_NOT_INSTALLED, STATUS_UPDATE
from marketplace.installer import install_rules_to_target, install_to_target


class TestVersionDetection:
    def test_get_installed_versions_nothing_installed_returns_empty_set(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        versions = get_installed_versions(sample_skill.id, project_dir)
        assert versions == set(), f"Expected no versions, got {versions}"

    def test_get_installed_versions_after_install_returns_catalog_version(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_to_target("agents", [sample_skill], project_dir)
        versions = get_installed_versions(sample_skill.id, project_dir)
        assert versions == {"1.0.0"}, f"Expected {{'1.0.0'}}, got {versions}"

    def test_get_installed_rule_versions_reads_all_native_formats(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("cursor", [sample_rule], project_dir)
        install_rules_to_target("copilot", [sample_rule], project_dir)
        versions = get_installed_rule_versions(sample_rule.id, project_dir)
        assert versions == {"1.0.0"}, f"Expected {{'1.0.0'}}, got {versions}"

    def test_get_installed_plugin_versions_nothing_installed_returns_empty_set(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        versions = get_installed_plugin_versions(sample_plugin.id, project_dir)
        assert versions == set(), f"Expected no versions, got {versions}"

    def test_get_installed_plugin_versions_after_install_returns_catalog_version(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_to_target("agents", [sample_plugin], project_dir)
        versions = get_installed_plugin_versions(sample_plugin.id, project_dir)
        assert versions == {"1.0.0"}, f"Expected {{'1.0.0'}}, got {versions}"


class TestBuildItemChoices:
    def test_build_item_choices_values_survive_inquirerpy_asdict(
        self, project_dir: Path, sample_skill: CatalogItem, sample_rule: CatalogItem
    ) -> None:
        """Regression: InquirerPy deep-converts Choice values via dataclasses.asdict().

        Passing CatalogItem as the value turned selections into plain dicts at
        runtime (AttributeError: 'dict' object has no attribute 'kind').
        """
        catalog = [sample_skill, sample_rule]
        choices = [c for c in build_item_choices(catalog, project_dir) if isinstance(c, Choice)]
        assert len(choices) == 2, f"Expected one choice per item, got {len(choices)}"
        for choice in choices:
            survived = asdict(choice)["value"]
            assert isinstance(
                survived, int
            ), f"Choice value must survive asdict() as a plain index, got {type(survived)}"
        indexes = [asdict(choice)["value"] for choice in choices]
        assert [catalog[index].id for index in indexes] == [
            "sample-skill",
            "sample-rule",
        ], f"Indexes must map back to catalog items: {indexes}"


class TestCollectInstalledState:
    def test_collect_installed_state_reflects_disk_per_target(
        self, project_dir: Path, sample_skill: CatalogItem, sample_rule: CatalogItem
    ) -> None:
        install_to_target("agents", [sample_skill], project_dir)
        install_rules_to_target("cursor", [sample_rule], project_dir)
        install_rules_to_target("claude", [sample_rule], project_dir)
        catalog = [sample_skill, sample_rule]
        per_target = collect_installed_state(catalog, project_dir)
        assert [item.id for item in per_target.get("agents", [])] == [
            "sample-skill"
        ], f"agents: {[i.id for i in per_target.get('agents', [])]}"
        assert [item.id for item in per_target.get("cursor", [])] == [
            "sample-rule"
        ], f"cursor: {[i.id for i in per_target.get('cursor', [])]}"
        assert [item.id for item in per_target.get("claude", [])] == [
            "sample-rule"
        ], f"claude: {[i.id for i in per_target.get('claude', [])]}"

    def test_collect_installed_state_empty_project_returns_empty(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        per_target = collect_installed_state([sample_skill], project_dir)
        assert not per_target, f"Nothing installed, got {per_target}"


class TestStatus:
    def test_get_status_not_installed_item_reports_not_installed(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        status, versions = get_status_and_versions(sample_skill, project_dir)
        assert status == STATUS_NOT_INSTALLED, f"Wrong status: {status}"
        assert versions == set(), f"Expected no versions, got {versions}"

    def test_get_status_installed_matching_version_reports_installed(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_to_target("claude", [sample_skill], project_dir)
        status, _ = get_status_and_versions(sample_skill, project_dir)
        assert status == STATUS_INSTALLED, f"Wrong status: {status}"

    def test_get_status_catalog_version_bumped_reports_update(
        self, project_dir: Path, sample_rule: CatalogItem
    ) -> None:
        install_rules_to_target("claude", [sample_rule], project_dir)
        sample_rule.version = "2.0.0"
        status, versions = get_status_and_versions(sample_rule, project_dir)
        assert status == STATUS_UPDATE, f"Wrong status: {status}"
        assert versions == {"1.0.0"}, f"Installed versions wrong: {versions}"

    def test_get_status_mixed_versions_across_targets_reports_update(
        self, project_dir: Path, sample_skill: CatalogItem
    ) -> None:
        install_to_target("claude", [sample_skill], project_dir)
        sample_skill.version = "1.1.0"
        install_to_target("agents", [sample_skill], project_dir)
        status, versions = get_status_and_versions(sample_skill, project_dir)
        assert status == STATUS_UPDATE, f"Wrong status: {status}"
        assert versions == {"1.0.0", "1.1.0"}, f"Versions wrong: {versions}"

    def test_get_status_plugin_not_installed_reports_not_installed(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        status, versions = get_status_and_versions(sample_plugin, project_dir)
        assert status == STATUS_NOT_INSTALLED, f"Wrong status: {status}"
        assert versions == set()

    def test_get_status_plugin_installed_matching_version_reports_installed(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_to_target("agents", [sample_plugin], project_dir)
        status, _ = get_status_and_versions(sample_plugin, project_dir)
        assert status == STATUS_INSTALLED, f"Wrong status: {status}"

    def test_get_status_plugin_version_bumped_reports_update(
        self, project_dir: Path, sample_plugin: CatalogItem
    ) -> None:
        install_to_target("agents", [sample_plugin], project_dir)
        sample_plugin.version = "2.0.0"
        status, versions = get_status_and_versions(sample_plugin, project_dir)
        assert status == STATUS_UPDATE, f"Wrong status: {status}"
        assert versions == {"1.0.0"}, f"Installed versions wrong: {versions}"
