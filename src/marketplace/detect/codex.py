from __future__ import annotations

from marketplace.consts.agents import AGENT_CODEX, AGENTS_MD
from marketplace.detect.base import Platform, PlatformDetector


class CodexDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_CODEX

    def detect(self) -> Platform:
        if signal := self._signal([AGENTS_MD, ".codex"]):
            return self.found(signal)
        return self.not_found()
