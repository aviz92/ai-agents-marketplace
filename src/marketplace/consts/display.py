from __future__ import annotations

BANNER = r"""
     _    ____ _____ _   _ _____ ____
    / \  / ___| ____| \ | |_   _/ ___|
   / _ \| |  _|  _| |  \| | | | \___ \
  / ___ \ |_| | |___| |\  | | |  ___) |
 /_/   \_\____|_____|_| \_| |_| |____/
        M A R K E T P L A C E
"""

# ── Status / action labels ────────────────────────────────────────────────────
STATUS_NOT_INSTALLED = "◯ Not Installed"
STATUS_INSTALLED = "✓ Installed"
STATUS_UPDATE = "↻ Update"

ACTION_INSTALL = "Install"
ACTION_REINSTALL = "Reinstall"
ACTION_UPDATE = "Update"
ACTION_BY_STATUS: dict[str, str] = {
    STATUS_NOT_INSTALLED: ACTION_INSTALL,
    STATUS_INSTALLED: ACTION_REINSTALL,
    STATUS_UPDATE: ACTION_UPDATE,
}

# ── Picker layout ─────────────────────────────────────────────────────────────
NAME_COL_WIDTH = 28
STATUS_COL_WIDTH = 15
VERSION_COL_WIDTH = 9
FIXED_ROW_COLUMNS = 80  # prompt prefix + fixed columns + separators
DESCRIPTION_MIN_WIDTH = 20
DESCRIPTION_MAX_WIDTH = 150
ELLIPSIS = "…"
EMPTY_VALUE = "—"
SECTION_SEPARATOR_FMT = f"{'─' * 4} {{section}} {'─' * 60}"
TABLE_TITLE_JUSTIFY = "left"

COL_NAME = "Name"
COL_STATUS = "Status"
COL_INSTALLED = "Installed"
COL_AVAILABLE = "Available"
COL_DESCRIPTION = "Description"
PLATFORM_TABLE_COLUMNS = ("Tool", "Detected", "Indicator", "Source")
SUMMARY_TABLE_COLUMNS = ("Artifact", "Kind", "Version", "Action")

TITLE_DETECTED_TOOLS = "Detected AI Tools"
TITLE_INSTALL_TARGETS = "Install Targets"
TITLE_SUMMARY = "Manifest Preview"
TITLE_TARGET_DIRS = "Target directories"
TITLE_FILES_WRITTEN = "Files written"
TITLE_EXTERNAL_PLUGINS = "🌐 External Plugins"

DETECTED_MARK = "[green]✓[/green]"
NOT_DETECTED_MARK = "[dim]✗[/dim]"
TARGET_CHOICE_FMT = "{label} → {covers}"
TARGET_PANEL_LINE_FMT = "[bold]{label}[/bold] → {covers}"

# ── Prompts ───────────────────────────────────────────────────────────────────
LOADING_CATALOG = "Loading catalog..."
PROMPT_SELECT_ITEMS = "Select artifacts to add (space toggles, enter confirms):"
PROMPT_SKILL_TARGETS = "Add skills/plugins for:"
PROMPT_RULE_TARGETS = "Add rules for (one native format per agent):"
PROMPT_CONFIRM_GENERATE = "Generate agents-marketplace.yaml?"
SELECTED_COUNT_FMT = "{count} selected"

# ── Messages ──────────────────────────────────────────────────────────────────
MSG_INSTALLING_INTO_FMT = "Generating manifest in: [bold]{project_dir}[/bold]"
MSG_CATALOG_COUNTS_FMT = (
    "Catalog: [bold]{skills}[/bold] skills · "
    "[bold]{rules}[/bold] rules · [bold]{plugins}[/bold] plugins · "
    "[bold]{external}[/bold] external\n"
)
MSG_EMPTY_CATALOG = "[red]No artifacts found in the marketplace catalog.[/red]"
MSG_NOTHING_SELECTED = "[yellow]Nothing selected — exiting.[/yellow]"
MSG_NO_TARGETS = "[yellow]No targets selected — exiting.[/yellow]"
MSG_NO_SKILL_TARGETS = "[yellow]No skill/plugin target selected — skipping those items.[/yellow]"
MSG_NO_RULE_TARGETS = "[yellow]No rule target selected — skipping rules.[/yellow]"
MSG_ABORTED = "[yellow]Aborted.[/yellow]"
MSG_CANCELLED = "\n[yellow]Cancelled.[/yellow]"
MSG_INVALID_MANIFEST_FMT = "[red]Invalid {manifest}: {error}[/red]"
MSG_MANIFEST_MISSING_FMT = "[red]No {manifest} found in {project_dir}.[/red]"
MSG_MANIFEST_EMPTY_FMT = "[red]{manifest} selected nothing to install.[/red]"
MSG_MISSING_REF_FMT = "[yellow]⚠ not in catalog: {reference}[/yellow]"
MSG_MANIFEST_SAVED_FMT = "[green]Wrote {name} — commit it to sync your team.[/green]"
PROMPT_SYNC_AGENTS = "Install for which agents? (space toggles, enter confirms):"
MSG_NO_SYNC_AGENTS = "[yellow]No agents selected — exiting.[/yellow]"

_SEP_LEAD = "─" * 4
_SEP_TOTAL = 65


def _section_header(label: str) -> str:
    """Build a fixed-total-width section separator string."""
    fill = max(0, _SEP_TOTAL - len(_SEP_LEAD) - 1 - len(label) - 1)
    return f"{_SEP_LEAD} {label} {'─' * fill}"


SYNC_SECTION_SKILLS = _section_header("Skills")
SYNC_SECTION_PLUGINS = _section_header("External Plugins")
SYNC_SECTION_RULES = _section_header("Rules")
