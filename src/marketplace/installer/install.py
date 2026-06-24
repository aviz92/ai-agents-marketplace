"""Orchestration: render catalog items and write them into agent directories."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from marketplace.consts.agents import AGENT_CLAUDE, CLAUDE_MD_PATH
from marketplace.consts.kinds import KindCategory
from marketplace.consts.render import CLAUDE_MD_FALLBACK
from marketplace.kind_catalog.models import CatalogItem

from .models import _RULE_REFERENCES, RULE_TARGETS, TARGETS, InstallResult
from .templates import _get_template_env
from .writer import _copy_assets, _ensure_reference, _write_rendered

_InstallFn = Callable[[str, list[CatalogItem], Path], InstallResult]


def _install_skill(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    return _install_into_targets_dir(target_id, items, project_dir)


def _install_plugin(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    return _install_into_targets_dir(target_id, items, project_dir)


def _install_rule(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = RULE_TARGETS[target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    if (reference := _RULE_REFERENCES.get(target_id)) is not None:
        _ensure_reference(project_dir, files_written, reference, rules_dir=target.dir)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )


def _install_into_targets_dir(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    target = TARGETS[target_id]
    env = _get_template_env()
    files_written: list[str] = []
    for item in items:
        cfg = item.config
        template = env.get_template(cfg.template)
        out_dir = project_dir / target.dir / item.id
        output_file = out_dir / cfg.output_file
        _write_rendered(output_file, template.render(item=item), project_dir, files_written)
        _copy_assets(item, out_dir, project_dir, files_written)
    if target_id == AGENT_CLAUDE:
        claude_md = project_dir / CLAUDE_MD_PATH
        if not claude_md.exists():
            _write_rendered(claude_md, CLAUDE_MD_FALLBACK, project_dir, files_written)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )

# Handlers per registry — defines which kinds each registry installs.
# Derive group sets and dispatch from these; don't define groups elsewhere.
_TARGETS_HANDLERS: list[tuple[KindCategory, _InstallFn]] = [
    (KindCategory.SKILL, _install_skill),
    (KindCategory.PLUGIN, _install_plugin),
]
_RULE_TARGETS_HANDLERS: list[tuple[KindCategory, _InstallFn]] = [
    (KindCategory.RULES, _install_rule),
]

SKILLS_TARGET_GROUPS: frozenset[KindCategory] = frozenset(g for g, _ in _TARGETS_HANDLERS)
RULE_TARGET_GROUPS: frozenset[KindCategory] = frozenset(g for g, _ in _RULE_TARGETS_HANDLERS)

# Per-target dispatch: target_id → [(KindCategory, install_fn), ...]
_TARGET_DISPATCH: dict[str, list[tuple[KindCategory, _InstallFn]]] = {}
for _tid in TARGETS:
    _TARGET_DISPATCH.setdefault(_tid, []).extend(_TARGETS_HANDLERS)
for _tid in RULE_TARGETS:
    _TARGET_DISPATCH.setdefault(_tid, []).extend(_RULE_TARGETS_HANDLERS)


def install_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> list[InstallResult]:
    """Install items into target_id, dispatching each kind to its registered function."""
    by_group: dict[KindCategory, list[CatalogItem]] = {}
    for item in items:
        by_group.setdefault(item.config.kind_category, []).append(item)

    results: list[InstallResult] = []
    for group, install_fn in _TARGET_DISPATCH.get(target_id, []):
        if group_items := by_group.get(group):
            results.append(install_fn(target_id, group_items, project_dir))
    return results
