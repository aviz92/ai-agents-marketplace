from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from marketplace.detect.base import Platform, PlatformDetector


@cache
def _detectors() -> tuple[type[PlatformDetector], ...]:
    # pylint: disable=import-outside-toplevel
    from marketplace.detect.claude import ClaudeDetector
    from marketplace.detect.codex import CodexDetector
    from marketplace.detect.copilot import CopilotDetector
    from marketplace.detect.cursor import CursorDetector
    from marketplace.detect.gemini import GeminiDetector

    return ClaudeDetector, CursorDetector, CopilotDetector, CodexDetector, GeminiDetector


def detect_platforms(project_dir: Path) -> list[Platform]:
    platforms: list[Platform] = []
    for detector_cls in _detectors():
        detector = detector_cls(project_dir)
        try:
            platforms.append(detector.detect())
        except (OSError, ValueError):
            platforms.append(detector.not_found())
    return platforms
