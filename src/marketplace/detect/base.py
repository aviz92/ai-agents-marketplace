from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from marketplace.consts.agents import AGENT_NAMES, SOURCE_PROJECT


@dataclass
class Platform:
    id: str
    name: str
    detected: bool
    indicator: str | None
    detection_source: str | None = None

    @property
    def label(self) -> str:
        status = "✅ detected" if self.detected else "❌ not detected"
        return f"{self.name} ({status})"


class PlatformDetector(ABC):
    def __init__(self, project_dir: Path) -> None:
        self._project_dir = project_dir

    @property
    @abstractmethod
    def platform_id(self) -> str:
        """Return the platform id."""

    @abstractmethod
    def detect(self) -> Platform:
        """Return the platform detected."""

    def found(self, indicator: str) -> Platform:
        return Platform(
            id=self.platform_id,
            name=AGENT_NAMES[self.platform_id],
            detected=True,
            indicator=indicator,
            detection_source=SOURCE_PROJECT,
        )

    def not_found(self, indicator: str | None = None) -> Platform:
        return Platform(
            id=self.platform_id,
            name=AGENT_NAMES[self.platform_id],
            detected=False,
            indicator=indicator,
            detection_source=SOURCE_PROJECT,
        )

    def _signal(self, signals: list[str]) -> str | None:
        for signal in signals:
            if (self._project_dir / signal).exists():
                return signal
        return None
