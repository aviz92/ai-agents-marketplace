"""Orchestration: dispatch catalog items to per-kind installers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from marketplace.consts.kinds import KindCategory
from marketplace.installer.handlers.commands import install_command
from marketplace.installer.handlers.plugins import install_plugin
from marketplace.installer.handlers.rules import install_rule
from marketplace.installer.handlers.skills import install_skill
from marketplace.installer.models import (
    ExternalInstallResult,
    InstallResult,
    command_targets,
    rule_targets,
    targets,
)
from marketplace.kind_catalog.models import CatalogItem, ExternalPlugin


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


def install_commands_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    return install_command(target_id, items, project_dir)


def install_external_plugin(item: ExternalPlugin) -> ExternalInstallResult:
    """Run item.install and stream output to the terminal.

    shell=True is required: install commands may contain pipes (e.g. curl | bash).
    item.install comes from repo-controlled catalog metadata.yaml — callers must
    confirm with the user before calling this function.
    """
    try:
        proc = subprocess.run(item.install, shell=True, check=False)  # noqa: S602
        success = proc.returncode == 0
    except Exception as exc:
        success = False
        return ExternalInstallResult(
            plugin_id=item.id, name=item.name, command=item.install, success=False, output=str(exc)
        )
    return ExternalInstallResult(
        plugin_id=item.id, name=item.name, command=item.install, success=success
    )


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
    if target_id in command_targets():
        if group := by_kind.get(KindCategory.COMMAND):
            results.append(install_command(target_id, group, project_dir))
    return results
