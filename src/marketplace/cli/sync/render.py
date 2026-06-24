"""Render everything the sync flow prints — results panel and external plugin panel."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from marketplace.consts import display
from marketplace.installer import InstallResult
from marketplace.kind_catalog.models import CatalogItem, ExternalPlugin


def print_results(console: Console, results: list[InstallResult]) -> None:
    lines: list[str] = []
    for result in results:
        lines.append(f"[bold]{result.output_dir}[/bold] ({result.installed} installed)")
        lines.extend(f"  ✓ {file}" for file in result.files_written)
    console.print(Panel("\n".join(lines), title=display.TITLE_FILES_WRITTEN, style="green"))


def print_external_plugins(console: Console, items: list[CatalogItem]) -> None:
    """Display each external plugin's source and install command. Never executes the command."""
    lines: list[str] = []
    for item in items:
        if not isinstance(item, ExternalPlugin):
            continue
        lines.append(f"[bold]{item.label}[/bold]  v{item.version}")
        lines.append(f"  {item.description}")
        lines.append(f"  Source:  [cyan]{item.source}[/cyan]")
        lines.append(f"  Install: [dim]{item.install}[/dim]")
        lines.append("")
    if lines:
        console.print(
            Panel("\n".join(lines).rstrip(), title=display.TITLE_EXTERNAL_PLUGINS, style="blue")
        )
