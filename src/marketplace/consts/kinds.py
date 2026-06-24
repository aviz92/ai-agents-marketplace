"""Artifact kind type definitions — enums and the KindConfig dataclass."""

from __future__ import annotations

from enum import Enum


class InstallGroup(str, Enum):
    """How an artifact kind is installed into a project."""

    SKILL = "skill"
    PLUGIN = "plugin"
    RULES = "rules"
    EXTERNAL_PLUGIN = "external_plugin"


class ManifestMode(str, Enum):
    """How a kind appears in agents-marketplace.yaml."""

    PER_AGENT = "per_agent"
    FLAT = "flat"
