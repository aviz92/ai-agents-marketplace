from __future__ import annotations

from marketplace.consts.agents import AGENT_CLAUDE, CLAUDE_MD
from marketplace.detect.base import Platform, PlatformDetector


class ClaudeDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_CLAUDE

    def detect(self) -> Platform:
        if signal := self._signal([CLAUDE_MD, ".claude"]):
            return self.found(signal)
        return self.not_found()
