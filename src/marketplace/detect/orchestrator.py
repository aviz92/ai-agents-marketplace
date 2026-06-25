from __future__ import annotations

from pathlib import Path

from marketplace.detect.agent_configs import ALL_CONFIGS
from marketplace.detect.base import AgentConfig, AgentDetector, Platform

DETECTORS: dict[str, AgentConfig] = {cfg.id: cfg for cfg in ALL_CONFIGS}


def _detect_agent(detector: AgentDetector) -> Platform:
    return detector.detect()


def detect_platforms(project_dir: Path) -> list[Platform]:
    platforms: list[Platform] = []
    for config in ALL_CONFIGS:
        detector = AgentDetector(config, project_dir)
        try:
            platforms.append(_detect_agent(detector))
        except (OSError, ValueError):
            platforms.append(detector.not_found())
    return platforms
