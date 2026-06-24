"""Artifact kind type definitions."""

from __future__ import annotations

from enum import Enum


class KindCategory(str, Enum):
    """Category of an artifact kind."""

    SKILL = "skill"
    PLUGIN = "plugin"
    RULES = "rules"
    EXTERNAL_PLUGIN = "external_plugin"
