"""Manifest-driven sync flow: read agents-marketplace.yaml and install per agent."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from marketplace.catalog import load_catalog
from marketplace.cli import render
from marketplace.cli.sync.prompts import prompt_sync_agents
from marketplace.consts import display
from marketplace.installer import (
    RULE_TARGETS,
    TARGETS,
    InstallResult,
    install_rules_to_target,
    install_to_target,
    split_install_kinds,
)
from marketplace.manifest import (
    MANIFEST_NAME,
    Manifest,
    ManifestError,
    load_manifest,
    resolve_per_agent,
)
from marketplace.models import CatalogItem


def _install_per_target(
    per_target: dict[str, list[CatalogItem]], project_dir: Path
) -> list[InstallResult]:
    results: list[InstallResult] = []
    for target_id, items in per_target.items():
        skills, rules = split_install_kinds(items)
        if target_id in TARGETS and skills:
            results.append(install_to_target(target_id, skills, project_dir))
        if target_id in RULE_TARGETS and rules:
            results.append(install_rules_to_target(target_id, rules, project_dir))
    return results


def _load_manifest_or_exit(err: Console, project_dir: Path) -> Manifest:
    """Load the manifest, exiting with a message on a parse error or a missing file."""
    try:
        manifest = load_manifest(project_dir)
    except ManifestError as error:
        err.print(display.MSG_INVALID_MANIFEST_FMT.format(manifest=MANIFEST_NAME, error=error))
        raise SystemExit(1) from error
    if manifest is None:
        err.print(
            display.MSG_MANIFEST_MISSING_FMT.format(manifest=MANIFEST_NAME, project_dir=project_dir)
        )
        raise SystemExit(1)
    return manifest


def _select_sync_targets(
    console: Console, installable: dict[str, list[CatalogItem]]
) -> dict[str, list[CatalogItem]]:
    """Prompt for which agents to sync, exiting on cancel or an empty selection."""
    try:
        selected = prompt_sync_agents(installable)
    except (KeyboardInterrupt, EOFError) as exc:
        console.print(display.MSG_CANCELLED)
        raise SystemExit(0) from exc
    if not selected:
        console.print(display.MSG_NO_SYNC_AGENTS)
        raise SystemExit(0)
    return {k: v for k, v in installable.items() if k in selected}


def run_sync(console: Console, project_dir: Path, *, install_all: bool = False) -> None:
    """Install artifacts declared in agents-marketplace.yaml.

    Prompts the user to choose which agents to install for unless install_all is True.
    """
    err = Console(stderr=True)
    manifest = _load_manifest_or_exit(err, project_dir)

    with console.status(display.LOADING_CATALOG):
        catalog = load_catalog()
    per_target, missing = resolve_per_agent(manifest, catalog)
    for reference in missing:
        err.print(display.MSG_MISSING_REF_FMT.format(reference=reference))

    if not (installable := {k: v for k, v in per_target.items() if v}):
        err.print(display.MSG_MANIFEST_EMPTY_FMT.format(manifest=MANIFEST_NAME))
        raise SystemExit(1)

    if not install_all:
        installable = _select_sync_targets(console, installable)

    render.print_results(console, _install_per_target(installable, project_dir))
    if missing:
        raise SystemExit(1)
