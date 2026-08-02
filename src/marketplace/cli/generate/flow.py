"""Interactive generate flow: pick artifacts and targets, generate agents-marketplace.yaml."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from marketplace.cli.generate import prompts, render
from marketplace.consts import display
from marketplace.consts.kinds import (
    COMMAND_TARGET_GROUPS,
    RULE_TARGET_GROUPS,
    SKILLS_TARGET_GROUPS,
    SUBAGENT_TARGET_GROUPS,
    KindCategory,
)
from marketplace.detect import detect_platforms
from marketplace.installer import command_targets, rule_targets, subagent_targets
from marketplace.kind_catalog.loader import load_catalog
from marketplace.kind_catalog.models import CatalogItem
from marketplace.manifest import ManifestError, save_manifest


def _build_per_target(
    selected: list[CatalogItem],
    skill_target_ids: list[str],
    rule_target_ids: list[str],
    command_target_ids: list[str],
    subagent_target_ids: list[str],
) -> dict[str, list[CatalogItem]]:
    per_target: dict[str, list[CatalogItem]] = {}
    for target_ids, kind_groups in (
        (skill_target_ids, SKILLS_TARGET_GROUPS),
        (rule_target_ids, RULE_TARGET_GROUPS),
        (command_target_ids, COMMAND_TARGET_GROUPS),
        (subagent_target_ids, SUBAGENT_TARGET_GROUPS),
    ):
        for target_id in target_ids:
            per_target.setdefault(target_id, []).extend(
                item for item in selected if item.config.kind_category in kind_groups
            )
    return per_target


def _prompt_targets(
    console: Console,
    project_dir: Path,
    regular_selected: list[CatalogItem],
    external_selected: list[CatalogItem],
) -> tuple[list[str], list[str], list[str], list[str]] | None:
    skill_targets: list[str] = []
    rule_target_ids: list[str] = []
    command_target_ids: list[str] = []
    subagent_target_ids: list[str] = []
    if regular_selected:
        platforms = detect_platforms(project_dir)
        render.print_platforms(console, platforms)
        render.print_targets_panel(console)
        detected = {platform.id for platform in platforms if platform.detected}
        (
            skill_targets,
            rule_target_ids,
            command_target_ids,
            subagent_target_ids,
        ) = prompts.prompt_all_targets(console, regular_selected, detected)
        if (
            not skill_targets
            and not rule_target_ids
            and not command_target_ids
            and not subagent_target_ids
            and not external_selected
        ):
            return None
    return skill_targets, rule_target_ids, command_target_ids, subagent_target_ids


def _save_manifest_or_report(
    console: Console,
    project_dir: Path,
    per_target: dict[str, list[CatalogItem]],
    external_selected: list[CatalogItem],
    filename: str,
) -> Path | None:
    try:
        return save_manifest(
            project_dir, per_target, external_items=external_selected, filename=filename
        )
    except ManifestError as error:
        console.print(display.MSG_INVALID_MANIFEST_FMT.format(manifest=filename, error=error))
        return None


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

        if (
            targets := _prompt_targets(console, project_dir, regular_selected, external_selected)
        ) is None:
            console.print(display.MSG_NO_TARGETS)
            return
        skill_targets, rule_target_ids, command_target_ids, subagent_target_ids = targets

        extra_dirs = (
            [rule_targets()[t].dir for t in rule_target_ids]
            + [command_targets()[t].dir for t in command_target_ids]
            + [subagent_targets()[t].dir for t in subagent_target_ids]
        )
        render.print_summary(console, selected, project_dir, skill_targets, extra_dirs)
        filename = prompts.prompt_manifest_filename()
    except (KeyboardInterrupt, EOFError):
        console.print(display.MSG_CANCELLED)
        return

    per_target = _build_per_target(
        regular_selected, skill_targets, rule_target_ids, command_target_ids, subagent_target_ids
    )
    if (
        path := _save_manifest_or_report(
            console, project_dir, per_target, external_selected, filename
        )
    ) is None:
        return
    console.print(display.MSG_MANIFEST_SAVED_FMT.format(name=path.name))
