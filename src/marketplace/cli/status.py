"""Read what is installed on disk and derive each item's status (no UI here)."""

from __future__ import annotations

from pathlib import Path

from marketplace.consts import display
from marketplace.consts.kinds import KIND_RULE
from marketplace.consts.render import SKILL_OUTPUT_FILE, VERSION_RE
from marketplace.installer import RULE_TARGETS, TARGETS, RuleTargetInfo, TargetInfo
from marketplace.models import CatalogItem


def _read_installed_version(file_path: Path) -> str | None:
    try:
        match = VERSION_RE.search(file_path.read_text(encoding="utf-8"))
    except OSError:
        return None
    return match.group(1) if match else None


def get_installed_versions_by_target(
    item_id: str, targets: dict[str, TargetInfo], project_dir: Path
) -> dict[str, str]:
    """Map skill/plugin target id → installed version found in its SKILL.md."""
    versions: dict[str, str] = {}
    for target_id, target in targets.items():
        skill_file = project_dir / target.dir / item_id / SKILL_OUTPUT_FILE
        if version := _read_installed_version(skill_file):
            versions[target_id] = version
    return versions


def get_installed_rule_versions_by_target(
    item_id: str, rule_targets: dict[str, RuleTargetInfo], project_dir: Path
) -> dict[str, str]:
    """Map rule target id → installed version found in its rendered rule file."""
    versions: dict[str, str] = {}
    for target_id, target in rule_targets.items():
        rule_file = project_dir / target.dir / target.filename_pattern.format(id=item_id)
        if version := _read_installed_version(rule_file):
            versions[target_id] = version
    return versions


def get_installed_versions(item_id: str, project_dir: Path) -> set[str]:
    return set(get_installed_versions_by_target(item_id, TARGETS, project_dir).values())


def get_installed_rule_versions(item_id: str, project_dir: Path) -> set[str]:
    return set(get_installed_rule_versions_by_target(item_id, RULE_TARGETS, project_dir).values())


def get_status_and_versions(item: CatalogItem, project_dir: Path) -> tuple[str, set[str]]:
    versions = (
        get_installed_rule_versions(item.id, project_dir)
        if item.kind == KIND_RULE
        else get_installed_versions(item.id, project_dir)
    )
    if not versions:
        return display.STATUS_NOT_INSTALLED, versions
    if versions == {item.version}:
        return display.STATUS_INSTALLED, versions
    return display.STATUS_UPDATE, versions


def collect_installed_state(
    catalog: list[CatalogItem], project_dir: Path
) -> dict[str, list[CatalogItem]]:
    """Snapshot what is installed on disk, grouped by target."""
    per_target: dict[str, list[CatalogItem]] = {}
    for item in catalog:
        by_target = (
            get_installed_rule_versions_by_target(item.id, RULE_TARGETS, project_dir)
            if item.kind == KIND_RULE
            else get_installed_versions_by_target(item.id, TARGETS, project_dir)
        )
        for target_id in by_target:
            per_target.setdefault(target_id, []).append(item)
    return per_target
