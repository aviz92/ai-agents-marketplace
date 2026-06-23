"""Interactive TUI package.

Shared layer: `status` (what's installed), `render` (everything printed),
`commands` (entry point). Each flow is its own subpackage with a `flow` module
and a `prompts` module: `generate/` and `sync/`. The names below are the
package's public surface, re-exported for stable imports.
"""

from __future__ import annotations

from marketplace.cli.commands import main
from marketplace.cli.generate import run_generate
from marketplace.cli.generate.prompts import build_item_choices
from marketplace.cli.status import (
    collect_installed_state,
    get_installed_rule_versions,
    get_installed_versions,
    get_status_and_versions,
)
from marketplace.cli.sync import run_sync
from marketplace.cli.sync.prompts import prompt_sync_agents

__all__ = [
    "build_item_choices",
    "collect_installed_state",
    "get_installed_rule_versions",
    "get_installed_versions",
    "get_status_and_versions",
    "main",
    "prompt_sync_agents",
    "run_generate",
    "run_sync",
]
