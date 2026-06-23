"""Interactive install flow: pick artifacts and targets, render, write, offer to save."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from marketplace.catalog import load_catalog
from marketplace.cli import render
from marketplace.cli.install import prompts
from marketplace.consts import display
from marketplace.detect import detect_platforms
from marketplace.installer import (
    InstallResult,
    install_rules_to_target,
    install_to_target,
    split_install_kinds,
)
from marketplace.models import CatalogItem


def _run_install(
    selected: list[CatalogItem],
    project_dir: Path,
    skill_targets: list[str],
    rule_targets: list[str],
) -> list[InstallResult]:
    skills, rules = split_install_kinds(selected)
    results = [install_to_target(target_id, skills, project_dir) for target_id in skill_targets]
    results += [
        install_rules_to_target(target_id, rules, project_dir) for target_id in rule_targets
    ]
    return results


def run_interactive(console: Console, project_dir: Path) -> None:
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

        platforms = detect_platforms(project_dir)
        render.print_platforms(console, platforms)
        render.print_targets_panel(console)

        detected = {platform.id for platform in platforms if platform.detected}
        skill_targets, rule_targets = prompts.prompt_all_targets(console, selected, detected)
        if not skill_targets and not rule_targets:
            console.print(display.MSG_NO_TARGETS)
            return

        render.print_summary(console, selected, project_dir, skill_targets, rule_targets)
        if not prompts.confirm_install():
            console.print(display.MSG_ABORTED)
            return
    except (KeyboardInterrupt, EOFError):
        console.print(display.MSG_CANCELLED)
        return

    results = _run_install(selected, project_dir, skill_targets, rule_targets)
    render.print_results(console, results)
    prompts.offer_manifest_save(console, project_dir, catalog)
