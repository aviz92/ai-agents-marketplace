from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from marketplace.consts.agents import AGENT_NAMES, SOURCE_PROJECT
from marketplace.consts.reference import ReferenceSpec


@dataclass(frozen=True)
class AgentConfig:
    """Static identity and detection metadata for one AI coding agent."""

    id: str
    signals: list[str]
    rule_reference: ReferenceSpec | None = None


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


class AgentDetector:
    def __init__(self, config: AgentConfig, project_dir: Path) -> None:
        self._config = config
        self._project_dir = project_dir

    def detect(self) -> Platform:
        if signal := self._signal(self._config.signals):
            return self.found(signal)
        return self.not_found()

    def found(self, indicator: str) -> Platform:
        return Platform(
            id=self._config.id,
            name=AGENT_NAMES[self._config.id],
            detected=True,
            indicator=indicator,
            detection_source=SOURCE_PROJECT,
        )

    def not_found(self, indicator: str | None = None) -> Platform:
        return Platform(
            id=self._config.id,
            name=AGENT_NAMES[self._config.id],
            detected=False,
            indicator=indicator,
            detection_source=SOURCE_PROJECT,
        )

    def _signal(self, signals: list[str]) -> str | None:
        for signal in signals:
            if (self._project_dir / signal).exists():
                return signal
        return None
