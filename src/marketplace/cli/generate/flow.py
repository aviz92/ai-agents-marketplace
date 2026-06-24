"""Interactive generate flow: pick artifacts and targets, generate agents-marketplace.yaml."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from marketplace.kind_catalog.loader import load_catalog
from marketplace.cli import render
from marketplace.cli.generate import prompts
from marketplace.consts import display
from marketplace.consts.kinds import KindCategory
from marketplace.detect import detect_platforms
from marketplace.installer import RULE_TARGET_GROUPS, SKILLS_TARGET_GROUPS
from marketplace.manifest import save_manifest
from marketplace.kind_catalog.models import CatalogItem


def _build_per_target(
    selected: list[CatalogItem],
    skill_targets: list[str],
    rule_targets: list[str],
) -> dict[str, list[CatalogItem]]:
    per_target: dict[str, list[CatalogItem]] = {}
    for target_id in skill_targets:
        per_target.setdefault(target_id, []).extend(
            item for item in selected if item.config.kind_category in SKILLS_TARGET_GROUPS
        )
    for target_id in rule_targets:
        per_target.setdefault(target_id, []).extend(
            item for item in selected if item.config.kind_category in RULE_TARGET_GROUPS
        )
    return per_target


def run_generate(console: Console, project_dir: Path) -> None:
    render.print_banner(console, project_dir)

    with console.status(display.LOADING_CATALOG):
        catalog = load_catalog()
    if not catalog:
        console.print(display.MSG_EMPTY_CATALOG)
        return
    render.print_catalog_counts(console, catalog)

    try:
        if not (selected := prompts.prompt_items(catalog, project_dir)):
            console.print(display.MSG_NOTHING_SELECTED)
            return

        external_selected = [
            item for item in selected if item.config.kind_category == KindCategory.EXTERNAL_PLUGIN
        ]
        regular_selected = [
            item for item in selected if item.config.kind_category != KindCategory.EXTERNAL_PLUGIN
        ]

        skill_targets: list[str] = []
        rule_targets: list[str] = []
        if regular_selected:
            platforms = detect_platforms(project_dir)
            render.print_platforms(console, platforms)
            render.print_targets_panel(console)
            detected = {platform.id for platform in platforms if platform.detected}
            skill_targets, rule_targets = prompts.prompt_all_targets(
                console, regular_selected, detected
            )
            if not skill_targets and not rule_targets and not external_selected:
                console.print(display.MSG_NO_TARGETS)
                return

        render.print_summary(console, selected, project_dir, skill_targets, rule_targets)
        if not prompts.confirm_generate():
            console.print(display.MSG_ABORTED)
            return
    except (KeyboardInterrupt, EOFError):
        console.print(display.MSG_CANCELLED)
        return

    per_target = _build_per_target(regular_selected, skill_targets, rule_targets)
    path = save_manifest(project_dir, per_target, external_items=external_selected)
    console.print(display.MSG_MANIFEST_SAVED_FMT.format(name=path.name))
