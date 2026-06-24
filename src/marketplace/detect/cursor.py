from __future__ import annotations

from marketplace.consts.agents import AGENT_CURSOR
from marketplace.detect.base import Platform, PlatformDetector


class CursorDetector(PlatformDetector):
    @property
    def platform_id(self) -> str:
        return AGENT_CURSOR

    def detect(self) -> Platform:
        if signal := self._signal([".cursor", ".cursorrules"]):
            return self.found(signal)
        return self.not_found()
