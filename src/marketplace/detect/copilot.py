from __future__ import annotations

from marketplace.consts.agents import AGENT_COPILOT, AGENTS_MD
from marketplace.detect.base import Platform, PlatformDetector


class CopilotDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_COPILOT

    def detect(self) -> Platform:
        signals = [
            ".github/skills",
            ".agents/skills",
            ".github/instructions",
            ".github/copilot-instructions.md",
            AGENTS_MD,
        ]
        if signal := self._signal(signals):
            return self.found(signal)
        return self.not_found()
