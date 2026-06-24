"""Render everything the generate flow prints — banners, tables, panels, and picker rows."""

from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from marketplace.cli.status import get_status_and_versions
from marketplace.consts import display
from marketplace.detect import Platform
from marketplace.installer import rule_targets, targets
from marketplace.kind_catalog.kinds import EXTERNAL_PLUGIN, PLUGIN, RULE, SKILL
from marketplace.kind_catalog.models import CatalogItem
from marketplace.kind_catalog.registry import all_kinds


def _clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + display.ELLIPSIS


def description_width() -> int:
    """Fit the description to the terminal so rows never wrap (wrapping breaks the list)."""
    available = shutil.get_terminal_size().columns - display.FIXED_ROW_COLUMNS
    return max(display.DESCRIPTION_MIN_WIDTH, min(display.DESCRIPTION_MAX_WIDTH, available))


def item_row(item: CatalogItem, project_dir: Path, desc_width: int) -> str:
    nw, sw, vw = display.NAME_COL_WIDTH, display.STATUS_COL_WIDTH, display.VERSION_COL_WIDTH
    status, versions = get_status_and_versions(item, project_dir)
    installed = ",".join(sorted(versions)) if versions else display.EMPTY_VALUE
    return (
        f"{_clip(item.name, nw):<{nw}} │ {status:<{sw}} │ "
        f"{_clip(installed, vw):<{vw}} "
        f"│ {item.version:<{vw}} │ {_clip(item.description, desc_width)}"
    )


def picker_header() -> str:
    nw, sw, vw = display.NAME_COL_WIDTH, display.STATUS_COL_WIDTH, display.VERSION_COL_WIDTH
    return (
        f"{display.COL_NAME:<{nw}} │ {display.COL_STATUS:<{sw}} │ "
        f"{display.COL_INSTALLED:<{vw}} │ {display.COL_AVAILABLE:<{vw}} "
        f"│ {display.COL_DESCRIPTION}"
    )


def print_banner(console: Console, project_dir: Path) -> None:
    console.print(f"[bold cyan]{display.BANNER}[/bold cyan]")
    msg = display.MSG_INSTALLING_INTO_FMT.format(project_dir=project_dir)
    console.print(Panel(msg, style="cyan"))


def print_catalog_counts(console: Console, catalog: list[CatalogItem]) -> None:
    counts = {
        cfg.kind_name: sum(1 for item in catalog if item.kind == cfg.kind_name)
        for cfg in all_kinds()
    }
    console.print(
        display.MSG_CATALOG_COUNTS_FMT.format(
            skills=counts[SKILL.kind_name],
            rules=counts[RULE.kind_name],
            plugins=counts[PLUGIN.kind_name],
            external=counts[EXTERNAL_PLUGIN.kind_name],
        )
    )


def print_platforms(console: Console, platforms: list[Platform]) -> None:
    table = Table(title=display.TITLE_DETECTED_TOOLS, title_justify=display.TABLE_TITLE_JUSTIFY)
    for column in display.PLATFORM_TABLE_COLUMNS:
        table.add_column(column)
    for platform in platforms:
        mark = display.DETECTED_MARK if platform.detected else display.NOT_DETECTED_MARK
        source = platform.detection_source or display.EMPTY_VALUE
        table.add_row(platform.name, mark, platform.indicator or display.EMPTY_VALUE, source)
    console.print(table)


def print_targets_panel(console: Console) -> None:
    all_targets = list(targets().values()) + list(rule_targets().values())
    lines = [
        display.TARGET_PANEL_LINE_FMT.format(label=target.label, covers=", ".join(target.covers))
        for target in all_targets
    ]
    console.print(Panel("\n".join(lines), title=display.TITLE_INSTALL_TARGETS, title_align="left"))


def print_summary(
    console: Console,
    items: list[CatalogItem],
    project_dir: Path,
    skill_targets: list[str],
    rule_target_ids: list[str],
) -> None:
    table = Table(title=display.TITLE_SUMMARY, title_justify=display.TABLE_TITLE_JUSTIFY)
    for column in display.SUMMARY_TABLE_COLUMNS:
        table.add_column(column)
    for item in items:
        status, _ = get_status_and_versions(item, project_dir)
        style = item.config.table_style
        kind_cell = f"[{style}]{item.kind}[/]" if style else item.kind
        table.add_row(item.name, kind_cell, item.version, display.ACTION_BY_STATUS[status])
    console.print(table)
    dirs = [targets()[target_id].dir for target_id in skill_targets]
    dirs += [rule_targets()[target_id].dir for target_id in rule_target_ids]
    if dirs:
        console.print(Panel("\n".join(dirs), title=display.TITLE_TARGET_DIRS, title_align="left"))
