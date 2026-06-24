"""Orchestration: dispatch catalog items to per-kind installers."""

from __future__ import annotations

from pathlib import Path

from marketplace.consts.kinds import KindCategory
from marketplace.kind_catalog.models import CatalogItem

from marketplace.installer.models import InstallResult, rule_targets, targets
from marketplace.installer.plugins import install_plugin
from marketplace.installer.rules import install_rule
from marketplace.installer.skills import install_skill


def install_skills_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    plugins = [i for i in items if i.config.kind_category == KindCategory.PLUGIN]
    skills = [i for i in items if i.config.kind_category == KindCategory.SKILL]
    if plugins:
        return install_plugin(target_id, plugins, project_dir)
    return install_skill(target_id, skills, project_dir)


def install_rules_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    return install_rule(target_id, items, project_dir)


def install_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> list[InstallResult]:
    by_kind: dict[KindCategory, list[CatalogItem]] = {}
    for item in items:
        by_kind.setdefault(item.config.kind_category, []).append(item)

    results: list[InstallResult] = []
    if target_id in targets():
        if group := by_kind.get(KindCategory.SKILL):
            results.append(install_skill(target_id, group, project_dir))
        if group := by_kind.get(KindCategory.PLUGIN):
            results.append(install_plugin(target_id, group, project_dir))
    if target_id in rule_targets():
        if group := by_kind.get(KindCategory.RULES):
            results.append(install_rule(target_id, group, project_dir))
    return results
