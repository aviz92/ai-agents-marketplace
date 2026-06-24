from __future__ import annotations

from pathlib import Path

from marketplace.detect.agents.claude import ClaudeDetector
from marketplace.detect.agents.codex import CodexDetector
from marketplace.detect.agents.copilot import CopilotDetector
from marketplace.detect.agents.cursor import CursorDetector
from marketplace.detect.agents.gemini import GeminiDetector
from marketplace.detect.base import Platform, PlatformDetector

_DETECTORS: tuple[type[PlatformDetector], ...] = (
    ClaudeDetector,
    CursorDetector,
    CopilotDetector,
    CodexDetector,
    GeminiDetector,
)


def detect_platforms(project_dir: Path) -> list[Platform]:
    platforms: list[Platform] = []
    for detector_cls in _DETECTORS:
        detector = detector_cls(project_dir)
        try:
            platforms.append(detector.detect())
        except (OSError, ValueError):
            platforms.append(detector.not_found())
    return platforms
