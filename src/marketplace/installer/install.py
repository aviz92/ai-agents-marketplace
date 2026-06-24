"""Orchestration: dispatch catalog items to per-kind installers."""

from __future__ import annotations

from pathlib import Path

from marketplace.consts.kinds import KindCategory
from marketplace.kind_catalog.models import CatalogItem

from .models import RULE_TARGETS, TARGETS, InstallResult
from .plugins import install_plugin
from .rules import install_rule
from .skills import install_skill


def install_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> list[InstallResult]:
    by_kind: dict[KindCategory, list[CatalogItem]] = {}
    for item in items:
        by_kind.setdefault(item.config.kind_category, []).append(item)

    results: list[InstallResult] = []
    if target_id in TARGETS:
        if group := by_kind.get(KindCategory.SKILL):
            results.append(install_skill(target_id, group, project_dir))
        if group := by_kind.get(KindCategory.PLUGIN):
            results.append(install_plugin(target_id, group, project_dir))
    if target_id in RULE_TARGETS:
        if group := by_kind.get(KindCategory.RULES):
            results.append(install_rule(target_id, group, project_dir))
    return results
