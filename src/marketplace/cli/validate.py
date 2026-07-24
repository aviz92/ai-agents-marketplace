"""`validate` flow: check every authored artifact, no installs, no manifest."""

from __future__ import annotations

from rich.console import Console

from marketplace.consts import display
from marketplace.kind_catalog.validate import ValidationIssue, validate_catalog
from utils import get_marketplace_root

_SEVERITY_COLOR: dict[str, str] = {"error": "red", "warning": "yellow"}


def _print_issue(console: Console, issue: ValidationIssue) -> None:
    color = _SEVERITY_COLOR[issue.severity]
    console.print(
        f"[{color}]{issue.severity.upper()}[/{color}] {issue.kind}/{issue.item_id}: "
        f"{issue.message} [dim]({issue.path})[/dim]"
    )


def run_validate(console: Console) -> int:
    """Validate the marketplace catalog and print a report.

    Returns the process exit code: 0 when clean or warnings-only, 1 if any error found.
    """
    if not (issues := validate_catalog(get_marketplace_root())):
        console.print(display.MSG_VALIDATE_CLEAN)
        return 0

    for issue in issues:
        _print_issue(console, issue)

    errors = sum(1 for issue in issues if issue.severity == "error")
    warnings = len(issues) - errors
    console.print(display.MSG_VALIDATE_SUMMARY_FMT.format(errors=errors, warnings=warnings))
    return 1 if errors else 0
