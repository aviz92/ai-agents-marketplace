from __future__ import annotations

from marketplace.consts.agents import AGENT_GEMINI, GEMINI_MD
from marketplace.detect.base import Platform, PlatformDetector


class GeminiDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_GEMINI

    def detect(self) -> Platform:
        if signal := self._signal([GEMINI_MD, ".gemini"]):
            return self.found(signal)
        return self.not_found()
