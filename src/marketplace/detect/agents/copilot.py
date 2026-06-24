from __future__ import annotations

from marketplace.consts.agents import (
    AGENT_COPILOT,
    AGENTS_MD,
    AGENTS_SKILLS_DIR,
    COPILOT_INSTRUCTIONS_DIR,
    COPILOT_INSTRUCTIONS_MD,
    COPILOT_SKILLS_DIR,
)
from marketplace.detect.base import Platform, PlatformDetector


class CopilotDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_COPILOT

    def detect(self) -> Platform:
        signals = [
            COPILOT_SKILLS_DIR,
            AGENTS_SKILLS_DIR,
            COPILOT_INSTRUCTIONS_DIR,
            COPILOT_INSTRUCTIONS_MD,
            AGENTS_MD,
        ]
        if signal := self._signal(signals):
            return self.found(signal)
        return self.not_found()
