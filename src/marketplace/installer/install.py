"""Orchestration: render catalog items and write them into agent directories."""

from __future__ import annotations

from pathlib import Path

from marketplace.consts.agents import AGENT_CLAUDE, CLAUDE_MD_PATH
from marketplace.consts.kinds import KIND_PLUGIN, KIND_RULE, SKILL_LIKE_KINDS
from marketplace.consts.render import (
    CLAUDE_MD_FALLBACK,
    PLUGIN_OUTPUT_FILE,
    PLUGIN_TEMPLATE,
    SKILL_OUTPUT_FILE,
    SKILL_TEMPLATE,
)
from marketplace.models import CatalogItem

from .models import _RULE_REFERENCES, RULE_TARGETS, TARGETS, InstallResult
from .templates import _get_template_env
from .writer import _copy_assets, _ensure_reference, _write_rendered


def split_install_kinds(
    items: list[CatalogItem],
) -> tuple[list[CatalogItem], list[CatalogItem]]:
    """Partition items into the two install paths: (skills-and-plugins, rules)."""
    skills = [item for item in items if item.kind in SKILL_LIKE_KINDS]
    rules = [item for item in items if item.kind == KIND_RULE]
    return skills, rules


def install_skills_to_target(
    target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    """Render skills/plugins via their respective templates into one shared target dir."""
    target = TARGETS[target_id]
    skill_template = _get_template_env().get_template(SKILL_TEMPLATE)
    plugin_template = _get_template_env().get_template(PLUGIN_TEMPLATE)
    files_written: list[str] = []
    for item in items:
        out_dir = project_dir / target.dir / item.id
        if item.kind == KIND_PLUGIN:
            output_file = out_dir / PLUGIN_OUTPUT_FILE
            content = plugin_template.render(item=item)
        else:
            output_file = out_dir / SKILL_OUTPUT_FILE
            content = skill_template.render(item=item)
        _write_rendered(output_file, content, project_dir, files_written)
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


def install_rules_to_target(
    rule_target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    """Render rules into one agent's native format, plus its reference file if needed."""
    target = RULE_TARGETS[rule_target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    if (reference := _RULE_REFERENCES.get(rule_target_id)) is not None:
        _ensure_reference(project_dir, files_written, reference, rules_dir=target.dir)
    return InstallResult(
        target=rule_target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
