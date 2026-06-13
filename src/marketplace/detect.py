"""Detect which AI coding agents are present in the project or on the system.

Detection is data-driven: every agent's display name, project signals, and CLI
command come from the registries in `agents` — one generic detector serves all.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from marketplace.consts.agents import (
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_NAMES,
    AGENT_PROJECT_SIGNALS,
    CURSOR_APP_PATHS,
    GH_COPILOT_INDICATOR,
    GH_EXTENSION_LIST_CMD,
    GH_TIMEOUT_SECONDS,
    PATH_INDICATOR_FMT,
    SOURCE_PROJECT,
    SOURCE_SYSTEM,
    VSCODE_COPILOT_EXTENSION_GLOB,
    VSCODE_COPILOT_INDICATOR,
    VSCODE_EXTENSIONS_DIR,
)


@dataclass
class Platform:
    """One AI coding agent and whether/where it was detected."""

    id: str
    name: str
    detected: bool
    indicator: str | None
    detection_source: str | None = None


def _project_signal(project_dir: Path, signals: list[str]) -> str | None:
    for signal in signals:
        if (project_dir / signal).exists():
            return signal
    return None


def _command_in_path(command: str) -> bool:
    return shutil.which(command) is not None


def _vscode_copilot_extension() -> bool:
    extensions_dir = Path(VSCODE_EXTENSIONS_DIR).expanduser()
    if not extensions_dir.is_dir():
        return False
    return any(extensions_dir.glob(VSCODE_COPILOT_EXTENSION_GLOB))


def _gh_copilot_extension() -> bool:
    if not _command_in_path(GH_EXTENSION_LIST_CMD[0]):
        return False
    result = subprocess.run(
        GH_EXTENSION_LIST_CMD,
        capture_output=True,
        text=True,
        timeout=GH_TIMEOUT_SECONDS,
        check=False,
    )
    return AGENT_COPILOT in result.stdout.lower()


def _cursor_app_installed() -> str | None:
    for app_path in CURSOR_APP_PATHS:
        if Path(app_path).expanduser().exists():
            return app_path
    return None


def _copilot_extension_indicator() -> str | None:
    if _vscode_copilot_extension():
        return VSCODE_COPILOT_INDICATOR
    if _gh_copilot_extension():
        return GH_COPILOT_INDICATOR
    return None


def _system_indicator(agent_id: str) -> str | None:
    """Every agent's CLI command is its id; cursor and copilot have extra signals."""
    if _command_in_path(agent_id):
        return PATH_INDICATOR_FMT.format(command=agent_id)
    if agent_id == AGENT_CURSOR:
        return _cursor_app_installed()
    if agent_id == AGENT_COPILOT:
        return _copilot_extension_indicator()
    return None


def _detect_agent(agent_id: str, project_dir: Path) -> Platform:
    name = AGENT_NAMES[agent_id]
    if signal := _project_signal(project_dir, AGENT_PROJECT_SIGNALS[agent_id]):
        return Platform(agent_id, name, True, signal, SOURCE_PROJECT)
    if indicator := _system_indicator(agent_id):
        return Platform(agent_id, name, True, indicator, SOURCE_SYSTEM)
    return Platform(agent_id, name, False, None)


def detect_platforms(project_dir: Path) -> list[Platform]:
    """Detect every registered agent; detection must never crash the CLI."""
    platforms: list[Platform] = []
    for agent_id, name in AGENT_NAMES.items():
        try:
            platforms.append(_detect_agent(agent_id, project_dir))
        except (OSError, subprocess.SubprocessError, ValueError):
            platforms.append(Platform(agent_id, name, False, None))
    return platforms
