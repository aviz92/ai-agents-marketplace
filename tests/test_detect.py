"""Tests for marketplace.detect — AI coding agent detection."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
    AGENT_NAMES,
)
from marketplace.detect import DETECTORS, Platform, detect_platforms


class TestDetectPlatforms:
    def test_detect_platforms_returns_one_entry_per_registered_agent(self, tmp_path: Path) -> None:
        platforms = detect_platforms(tmp_path)
        detected_ids = {p.id for p in platforms}
        assert detected_ids == set(
            AGENT_NAMES
        ), f"Expected all registered agents, got {detected_ids}"

    def test_detect_platforms_empty_dir_marks_all_as_not_detected(self, tmp_path: Path) -> None:
        platforms = detect_platforms(tmp_path)
        undetected = [p for p in platforms if p.detected]
        assert not undetected, f"No agents should be detected in an empty dir: {undetected}"

    @pytest.mark.parametrize(
        "agent_id", [AGENT_CLAUDE, AGENT_CURSOR, AGENT_COPILOT, AGENT_CODEX, AGENT_GEMINI]
    )
    def test_detect_platforms_first_signal_triggers_detection(
        self, tmp_path: Path, agent_id: str
    ) -> None:
        signal = DETECTORS[agent_id].signals[0]
        signal_path = tmp_path / signal
        # Create as a file or directory based on whether it has an extension
        if "." in signal_path.name:
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            signal_path.write_text("", encoding="utf-8")
        else:
            signal_path.mkdir(parents=True, exist_ok=True)

        platforms = detect_platforms(tmp_path)
        match = next(p for p in platforms if p.id == agent_id)
        assert match.detected, f"{agent_id}: expected detected=True for signal '{signal}'"
        assert match.indicator == signal, f"{agent_id}: wrong indicator, got {match.indicator}"

    def test_detect_platforms_non_present_agent_has_none_indicator(self, tmp_path: Path) -> None:
        platforms = detect_platforms(tmp_path)
        for p in platforms:
            assert (
                p.indicator is None
            ), f"{p.id}: indicator should be None when not detected, got {p.indicator}"

    def test_detect_platforms_oserror_during_detection_is_swallowed(self, tmp_path: Path) -> None:
        """An OSError in _detect_agent must never crash detect_platforms."""
        with patch("marketplace.detect._detect_agent", side_effect=OSError("disk error")):
            platforms = detect_platforms(tmp_path)
        assert len(platforms) == len(
            AGENT_NAMES
        ), "All agents must still appear even after an OSError"
        for p in platforms:
            assert not p.detected, f"{p.id}: should fall back to detected=False on error"

    def test_detect_platforms_detection_source_is_set_on_detected_agent(
        self, tmp_path: Path
    ) -> None:
        signal = DETECTORS[AGENT_CURSOR].signals[0]
        (tmp_path / signal).mkdir(parents=True, exist_ok=True)
        platforms = detect_platforms(tmp_path)
        cursor = next(p for p in platforms if p.id == AGENT_CURSOR)
        assert (
            cursor.detection_source == "project"
        ), f"Expected 'project', got {cursor.detection_source}"


class TestPlatformDataclass:
    def test_platform_fields_accessible(self) -> None:
        p = Platform(id="x", name="X", detected=True, indicator=".x", detection_source="project")
        assert p.id == "x"
        assert p.name == "X"
        assert p.detected is True
        assert p.indicator == ".x"
        assert p.detection_source == "project"

    def test_platform_detection_source_defaults_to_none(self) -> None:
        p = Platform(id="x", name="X", detected=False, indicator=None)
        assert p.detection_source is None
