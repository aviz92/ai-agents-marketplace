"""Interactive TUI: pick artifacts, pick targets, render, install."""

from __future__ import annotations

import shutil
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from python_base_command import BaseCommand, CommandRegistry
from python_base_command.base import CommandParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from marketplace.consts import display
from marketplace.consts.agents import AGENT_CLAUDE, TARGET_AGENTS
from marketplace.catalog import CatalogItem, load_catalog
from marketplace.detect import Platform, detect_platforms
from marketplace.installer import (
    RULE_TARGETS,
    TARGETS,
    InstallResult,
    RuleTargetInfo,
    TargetInfo,
    install_rules_to_target,
    install_to_target,
)
from marketplace.consts.kinds import KIND_PLUGIN, KIND_RULE, KIND_SECTIONS, KIND_SKILL, SKILL_LIKE_KINDS
from marketplace.manifest import (
    MANIFEST_NAME,
    ManifestError,
    load_manifest,
    resolve_items,
    save_manifest,
)
from marketplace.consts.render import SKILL_OUTPUT_FILE, VERSION_RE


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


def _get_status_and_versions(item: CatalogItem, project_dir: Path) -> tuple[str, set[str]]:
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


def _clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + display.ELLIPSIS


def _description_width() -> int:
    """Fit the description to the terminal so rows never wrap (wrapping breaks the list)."""
    available = shutil.get_terminal_size().columns - display.FIXED_ROW_COLUMNS
    return max(display.DESCRIPTION_MIN_WIDTH, min(display.DESCRIPTION_MAX_WIDTH, available))


def _item_row(item: CatalogItem, project_dir: Path, description_width: int) -> str:
    nw, sw, vw = display.NAME_COL_WIDTH, display.STATUS_COL_WIDTH, display.VERSION_COL_WIDTH
    status, versions = _get_status_and_versions(item, project_dir)
    installed = ",".join(sorted(versions)) if versions else display.EMPTY_VALUE
    return (
        f"{_clip(item.name, nw):<{nw}} │ {status:<{sw}} │ "
        f"{_clip(installed, vw):<{vw}} "
        f"│ {item.version:<{vw}} │ {_clip(item.description, description_width)}"
    )


def _picker_header() -> str:
    nw, sw, vw = display.NAME_COL_WIDTH, display.STATUS_COL_WIDTH, display.VERSION_COL_WIDTH
    return (
        f"{display.COL_NAME:<{nw}} │ {display.COL_STATUS:<{sw}} │ "
        f"{display.COL_INSTALLED:<{vw}} │ {display.COL_AVAILABLE:<{vw}} "
        f"│ {display.COL_DESCRIPTION}"
    )


def _build_item_choices(catalog: list[CatalogItem], project_dir: Path) -> list[Choice | Separator]:
    """Build picker rows with catalog *indexes* as values.

    InquirerPy runs `dataclasses.asdict()` on every Choice, which deep-converts
    dataclass values into plain dicts — so values must never be CatalogItem itself.
    """
    description_width = _description_width()
    choices: list[Choice | Separator] = [Separator(f"  {_picker_header()}")]
    indexed_catalog = list(enumerate(catalog))
    for kind, section in KIND_SECTIONS:
        if not (kind_indexed := [(i, item) for i, item in indexed_catalog if item.kind == kind]):
            continue
        choices.append(Separator(display.SECTION_SEPARATOR_FMT.format(section=section)))
        choices.extend(
            Choice(value=index, name=_item_row(item, project_dir, description_width))
            for index, item in kind_indexed
        )
    return choices


def _prompt_items(catalog: list[CatalogItem], project_dir: Path) -> list[CatalogItem]:
    selected_indexes = inquirer.checkbox(
        message=display.PROMPT_SELECT_ITEMS,
        choices=_build_item_choices(catalog, project_dir),
        cycle=True,
        transformer=lambda result: display.SELECTED_COUNT_FMT.format(count=len(result)),
    ).execute()
    return [catalog[index] for index in selected_indexes]


def _target_choice_name(target_id: str) -> str:
    target = TARGETS[target_id]
    return display.TARGET_CHOICE_FMT.format(label=target.label, covers=", ".join(target.covers))


def _prompt_targets(detected: set[str]) -> list[str]:
    agents_detected = bool(detected - {AGENT_CLAUDE})
    choices = [
        Choice(
            value=AGENT_CLAUDE,
            name=_target_choice_name(AGENT_CLAUDE),
            enabled=AGENT_CLAUDE in detected or not detected,
        ),
        Choice(
            value=TARGET_AGENTS,
            name=_target_choice_name(TARGET_AGENTS),
            enabled=agents_detected or not detected,
        ),
    ]
    return inquirer.checkbox(
        message=display.PROMPT_SKILL_TARGETS, choices=choices, cycle=True
    ).execute()


def _prompt_rule_targets(detected: set[str]) -> list[str]:
    any_detected = bool(detected & set(RULE_TARGETS))
    choices = [
        Choice(
            value=target_id,
            name=display.TARGET_CHOICE_FMT.format(
                label=target.label, covers=", ".join(target.covers)
            ),
            enabled=target_id in detected or not any_detected,
        )
        for target_id, target in RULE_TARGETS.items()
    ]
    return inquirer.checkbox(
        message=display.PROMPT_RULE_TARGETS, choices=choices, cycle=True
    ).execute()


def _print_banner(console: Console, project_dir: Path) -> None:
    console.print(f"[bold cyan]{display.BANNER}[/bold cyan]")
    msg = display.MSG_INSTALLING_INTO_FMT.format(project_dir=project_dir)
    console.print(Panel(msg, style="cyan"))


def _print_catalog_counts(console: Console, catalog: list[CatalogItem]) -> None:
    counts = {kind: sum(1 for item in catalog if item.kind == kind) for kind, _ in KIND_SECTIONS}
    console.print(
        display.MSG_CATALOG_COUNTS_FMT.format(
            skills=counts[KIND_SKILL], rules=counts[KIND_RULE], plugins=counts[KIND_PLUGIN]
        )
    )


def _print_platforms(console: Console, platforms: list[Platform]) -> None:
    table = Table(title=display.TITLE_DETECTED_TOOLS, title_justify=display.TABLE_TITLE_JUSTIFY)
    for column in display.PLATFORM_TABLE_COLUMNS:
        table.add_column(column)
    for platform in platforms:
        mark = display.DETECTED_MARK if platform.detected else display.NOT_DETECTED_MARK
        source = platform.detection_source or display.EMPTY_VALUE
        table.add_row(platform.name, mark, platform.indicator or display.EMPTY_VALUE, source)
    console.print(table)


def _print_targets_panel(console: Console) -> None:
    all_targets = list(TARGETS.values()) + list(RULE_TARGETS.values())
    lines = [
        display.TARGET_PANEL_LINE_FMT.format(label=target.label, covers=", ".join(target.covers))
        for target in all_targets
    ]
    console.print(Panel("\n".join(lines), title=display.TITLE_INSTALL_TARGETS, title_align="left"))


def _print_summary(
    console: Console,
    items: list[CatalogItem],
    project_dir: Path,
    skill_targets: list[str],
    rule_targets: list[str],
) -> None:
    table = Table(title=display.TITLE_SUMMARY, title_justify=display.TABLE_TITLE_JUSTIFY)
    for column in display.SUMMARY_TABLE_COLUMNS:
        table.add_column(column)
    for item in items:
        status, _ = _get_status_and_versions(item, project_dir)
        table.add_row(item.label, item.kind, item.version, display.ACTION_BY_STATUS[status])
    console.print(table)
    dirs = [TARGETS[target_id].dir for target_id in skill_targets]
    dirs += [RULE_TARGETS[target_id].dir for target_id in rule_targets]
    console.print(Panel("\n".join(dirs), title=display.TITLE_TARGET_DIRS, title_align="left"))


def _print_results(console: Console, results: list[InstallResult]) -> None:
    lines: list[str] = []
    for result in results:
        lines.append(f"[bold]{result.output_dir}[/bold] ({result.installed} installed)")
        lines.extend(f"  ✓ {file}" for file in result.files_written)
    console.print(Panel("\n".join(lines), title=display.TITLE_FILES_WRITTEN, style="green"))


def _run_install(
    selected: list[CatalogItem],
    project_dir: Path,
    skill_targets: list[str],
    rule_targets: list[str],
) -> list[InstallResult]:
    skills = [item for item in selected if item.kind in SKILL_LIKE_KINDS]
    rules = [item for item in selected if item.kind == KIND_RULE]
    results = [install_to_target(target_id, skills, project_dir) for target_id in skill_targets]
    results += [
        install_rules_to_target(target_id, rules, project_dir) for target_id in rule_targets
    ]
    return results


def _prompt_all_targets(
    console: Console, selected: list[CatalogItem], detected: set[str]
) -> tuple[list[str], list[str]]:
    has_skills = any(item.kind in SKILL_LIKE_KINDS for item in selected)
    has_rules = any(item.kind == KIND_RULE for item in selected)
    skill_targets = _prompt_targets(detected) if has_skills else []
    rule_targets = _prompt_rule_targets(detected) if has_rules else []
    if has_skills and not skill_targets:
        console.print(display.MSG_NO_SKILL_TARGETS)
    if has_rules and not rule_targets:
        console.print(display.MSG_NO_RULE_TARGETS)
    return skill_targets, rule_targets


def _default_skill_targets(detected: set[str]) -> list[str]:
    """Mirror the interactive pre-checks: claude when detected, agents as the broad default."""
    targets: list[str] = []
    if AGENT_CLAUDE in detected:
        targets.append(AGENT_CLAUDE)
    if detected - {AGENT_CLAUDE} or not detected:
        targets.append(TARGET_AGENTS)
    return targets


def _default_rule_targets(detected: set[str]) -> list[str]:
    detected_targets = [target_id for target_id in RULE_TARGETS if target_id in detected]
    return detected_targets or list(RULE_TARGETS)


def _sync_targets(
    manifest_skill_targets: list[str],
    manifest_rule_targets: list[str],
    selected: list[CatalogItem],
    detected: set[str],
) -> tuple[list[str], list[str]]:
    has_skills = any(item.kind in SKILL_LIKE_KINDS for item in selected)
    has_rules = any(item.kind == KIND_RULE for item in selected)
    skill_targets = (
        (manifest_skill_targets or _default_skill_targets(detected)) if has_skills else []
    )
    rule_targets = (manifest_rule_targets or _default_rule_targets(detected)) if has_rules else []
    return skill_targets, rule_targets


def run_sync(console: Console, project_dir: Path) -> None:
    """Install everything agents-marketplace.yaml declares — no prompts."""
    err = Console(stderr=True)
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

    with console.status(display.LOADING_CATALOG):
        catalog = load_catalog()
    selected, missing = resolve_items(manifest, catalog)
    for reference in missing:
        err.print(display.MSG_MISSING_REF_FMT.format(reference=reference))
    if not selected:
        err.print(display.MSG_MANIFEST_EMPTY_FMT.format(manifest=MANIFEST_NAME))
        raise SystemExit(1)

    detected = {platform.id for platform in detect_platforms(project_dir) if platform.detected}
    skill_targets, rule_targets = _sync_targets(
        manifest.skill_targets, manifest.rule_targets, selected, detected
    )
    results = _run_install(selected, project_dir, skill_targets, rule_targets)
    _print_results(console, results)
    if missing:
        raise SystemExit(1)


def _collect_installed_state(
    catalog: list[CatalogItem], project_dir: Path
) -> tuple[list[CatalogItem], list[str], list[str]]:
    """Snapshot what is actually installed on disk — the manifest mirrors reality,
    not the current selection or the previous file contents."""
    items: list[CatalogItem] = []
    skill_targets: set[str] = set()
    rule_targets: set[str] = set()
    for item in catalog:
        if item.kind == KIND_RULE:
            by_target = get_installed_rule_versions_by_target(item.id, RULE_TARGETS, project_dir)
            rule_targets.update(by_target)
        else:
            by_target = get_installed_versions_by_target(item.id, TARGETS, project_dir)
            skill_targets.update(by_target)
        if by_target:
            items.append(item)
    ordered_skill_targets = [target for target in TARGETS if target in skill_targets]
    ordered_rule_targets = [target for target in RULE_TARGETS if target in rule_targets]
    return items, ordered_skill_targets, ordered_rule_targets


def _offer_manifest_save(console: Console, project_dir: Path, catalog: list[CatalogItem]) -> None:
    try:
        save = inquirer.confirm(
            message=display.PROMPT_SAVE_MANIFEST_FMT.format(manifest=MANIFEST_NAME),
            default=True,
        ).execute()
    except (KeyboardInterrupt, EOFError):
        return
    if not save:
        return
    items, skill_targets, rule_targets = _collect_installed_state(catalog, project_dir)
    path = save_manifest(project_dir, items, skill_targets, rule_targets)
    console.print(display.MSG_MANIFEST_SAVED_FMT.format(name=path.name))


def _run_interactive(console: Console, project_dir: Path) -> None:
    _print_banner(console, project_dir)

    with console.status(display.LOADING_CATALOG):
        catalog = load_catalog()
    if not catalog:
        console.print(display.MSG_EMPTY_CATALOG)
        return
    _print_catalog_counts(console, catalog)

    try:
        if not (selected := _prompt_items(catalog, project_dir)):
            console.print(display.MSG_NOTHING_SELECTED)
            return

        platforms = detect_platforms(project_dir)
        _print_platforms(console, platforms)
        _print_targets_panel(console)

        detected = {platform.id for platform in platforms if platform.detected}
        skill_targets, rule_targets = _prompt_all_targets(console, selected, detected)
        if not skill_targets and not rule_targets:
            console.print(display.MSG_NO_TARGETS)
            return

        _print_summary(console, selected, project_dir, skill_targets, rule_targets)
        if not inquirer.confirm(message=display.PROMPT_CONFIRM_INSTALL, default=True).execute():
            console.print(display.MSG_ABORTED)
            return
    except (KeyboardInterrupt, EOFError):
        console.print(display.MSG_CANCELLED)
        return

    results = _run_install(selected, project_dir, skill_targets, rule_targets)
    _print_results(console, results)
    _offer_manifest_save(console, project_dir, catalog)


try:
    _VERSION = _pkg_version("agents-marketplace")
except PackageNotFoundError:
    _VERSION = "dev"


class _InstallCommand(BaseCommand):
    help = "Interactively browse and install skills, rules, and plugins."
    version = _VERSION

    def create_parser(self, prog_name: str, _subcommand: str, **kwargs: object) -> CommandParser:
        return super().create_parser(prog_name, "install", **kwargs)

    def handle(self, **kwargs: object) -> None:
        verbosity = int(kwargs.get("verbosity", 1))
        _run_interactive(Console(quiet=verbosity == 0), Path.cwd())


class _SyncCommand(BaseCommand):
    help = "Install everything agents-marketplace.yaml declares — no prompts."
    version = _VERSION

    def create_parser(self, prog_name: str, _subcommand: str, **kwargs: object) -> CommandParser:
        return super().create_parser(prog_name, "sync", **kwargs)

    def handle(self, **kwargs: object) -> None:
        verbosity = int(kwargs.get("verbosity", 1))
        run_sync(Console(quiet=verbosity == 0), Path.cwd())


_registry = CommandRegistry()
_registry.add("install", _InstallCommand)
_registry.add("sync", _SyncCommand)


def main() -> None:
    """Entry point for the `agents-marketplace` command."""
    _registry.run()


if __name__ == "__main__":
    main()
