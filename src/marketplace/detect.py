"""Detect which AI coding agents are present in the project.

Detection is data-driven: every agent's display name and project signals come
from the registries in `agents` — one generic detector serves all.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from marketplace.consts.agents import (
    AGENT_NAMES,
    AGENT_PROJECT_SIGNALS,
    SOURCE_PROJECT,
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


def _detect_agent(agent_id: str, project_dir: Path) -> Platform:
    name = AGENT_NAMES[agent_id]
    if signal := _project_signal(project_dir, AGENT_PROJECT_SIGNALS[agent_id]):
        return Platform(agent_id, name, True, signal, SOURCE_PROJECT)
    return Platform(agent_id, name, False, None)


def detect_platforms(project_dir: Path) -> list[Platform]:
    """Detect every registered agent; detection must never crash the CLI."""
    platforms: list[Platform] = []
    for agent_id, name in AGENT_NAMES.items():
        try:
            platforms.append(_detect_agent(agent_id, project_dir))
        except (OSError, ValueError):
            platforms.append(Platform(agent_id, name, False, None))
    return platforms
