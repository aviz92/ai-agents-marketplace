"""Render everything the sync flow prints — results panel and external plugin panel."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from marketplace.consts import display
from marketplace.installer import ExternalInstallResult, InstallResult
from marketplace.kind_catalog.kinds import EXTERNAL_PLUGIN


def print_results(console: Console, results: list[InstallResult]) -> None:
    lines: list[str] = []
    for result in results:
        lines.append(f"[bold]{result.output_dir}[/bold] ({result.installed} installed)")
        lines.extend(f"  ✓ {file}" for file in result.files_written)
    console.print(Panel("\n".join(lines), title=display.TITLE_FILES_WRITTEN, style="green"))


def print_external_results(console: Console, results: list[ExternalInstallResult]) -> None:
    lines: list[str] = []
    all_ok = all(r.success for r in results)
    for result in results:
        icon = "[green]✓[/green]" if result.success else "[red]✗[/red]"
        lines.append(f"{icon} [bold]{result.name}[/bold]  [dim]{result.command}[/dim]")
    style = "green" if all_ok else "red"
    title = f"{EXTERNAL_PLUGIN.icon} {EXTERNAL_PLUGIN.display_name}"
    console.print(Panel("\n".join(lines), title=title, style=style))
