"""Read what is installed on disk and derive each item's status (no UI here)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from marketplace.consts import display
from marketplace.consts.kinds import KindCategory
from marketplace.consts.render import PLUGIN_OUTPUT_FILE, SKILL_OUTPUT_FILE, VERSION_RE
from marketplace.installer import RuleTargetInfo, TargetInfo, rule_targets, targets
from marketplace.kind_catalog.models import CatalogItem

_StatusFn = Callable[["CatalogItem", Path], dict[str, str]]


def _read_installed_version(file_path: Path) -> str | None:
    try:
        match = VERSION_RE.search(file_path.read_text(encoding="utf-8"))
    except OSError:
        return None
    return match.group(1) if match else None


_T = TypeVar("_T", TargetInfo, RuleTargetInfo)


def _get_versions_by_target(
    item_id: str,
    target_map: dict[str, _T],
    path_resolver: Callable[[str, _T], Path],
    project_dir: Path,
) -> dict[str, str]:
    versions: dict[str, str] = {}
    for target_id, target in target_map.items():
        file_path = project_dir / path_resolver(item_id, target)
        if version := _read_installed_version(file_path):
            versions[target_id] = version
    return versions


def get_installed_versions_by_target(
    item_id: str, target_map: dict[str, TargetInfo], project_dir: Path
) -> dict[str, str]:
    """Map skill target id → installed version found in its SKILL.md."""
    return _get_versions_by_target(
        item_id,
        target_map,
        lambda iid, t: Path(t.dir) / iid / SKILL_OUTPUT_FILE,
        project_dir,
    )


def get_installed_plugin_versions_by_target(
    item_id: str, target_map: dict[str, TargetInfo], project_dir: Path
) -> dict[str, str]:
    """Map plugin target id → installed version found in its PLUGIN.md."""
    return _get_versions_by_target(
        item_id,
        target_map,
        lambda iid, t: Path(t.dir) / iid / PLUGIN_OUTPUT_FILE,
        project_dir,
    )


def get_installed_rule_versions_by_target(
    item_id: str, rule_target_map: dict[str, RuleTargetInfo], project_dir: Path
) -> dict[str, str]:
    """Map rule target id → installed version found in its rendered rule file."""
    return _get_versions_by_target(
        item_id,
        rule_target_map,
        lambda iid, t: Path(t.dir) / t.filename_pattern.format(id=iid),
        project_dir,
    )


def _status_skill(item: CatalogItem, project_dir: Path) -> dict[str, str]:
    output_file = item.config.output_file or SKILL_OUTPUT_FILE
    return _get_versions_by_target(
        item.id, targets(), lambda iid, t: Path(t.dir) / iid / output_file, project_dir
    )


def _status_plugin(item: CatalogItem, project_dir: Path) -> dict[str, str]:
    output_file = item.config.output_file or PLUGIN_OUTPUT_FILE
    return _get_versions_by_target(
        item.id, targets(), lambda iid, t: Path(t.dir) / iid / output_file, project_dir
    )


def _status_rule(item: CatalogItem, project_dir: Path) -> dict[str, str]:
    return get_installed_rule_versions_by_target(item.id, rule_targets(), project_dir)


_STATUS_DISPATCH: dict[KindCategory, _StatusFn] = {
    KindCategory.SKILL: _status_skill,
    KindCategory.PLUGIN: _status_plugin,
    KindCategory.RULES: _status_rule,
}


def _resolve_versions_by_target(item: CatalogItem, project_dir: Path) -> dict[str, str]:
    fn = _STATUS_DISPATCH.get(item.config.kind_category)
    return fn(item, project_dir) if fn else {}


def get_installed_versions(item_id: str, project_dir: Path) -> set[str]:
    return set(get_installed_versions_by_target(item_id, targets(), project_dir).values())


def get_installed_plugin_versions(item_id: str, project_dir: Path) -> set[str]:
    return set(get_installed_plugin_versions_by_target(item_id, targets(), project_dir).values())


def get_installed_rule_versions(item_id: str, project_dir: Path) -> set[str]:
    return set(get_installed_rule_versions_by_target(item_id, rule_targets(), project_dir).values())


def get_status_and_versions(item: CatalogItem, project_dir: Path) -> tuple[str, set[str]]:
    if not (versions := set(_resolve_versions_by_target(item, project_dir).values())):
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
        for target_id in _resolve_versions_by_target(item, project_dir):
            per_target.setdefault(target_id, []).append(item)
    return per_target
