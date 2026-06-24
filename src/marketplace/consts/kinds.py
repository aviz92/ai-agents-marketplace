"""Artifact kind type definitions — enums and the KindConfig dataclass."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class KindConfig:
    """Complete specification for one artifact kind."""

    kind_name: str
    dir_name: str
    icon: str
    display_name: str
    table_style: str           # Rich markup color for summary table ("" = default)
    body_filename: str | None  # None = metadata-only (no body file on disk)
    manifest_mode: ManifestMode
    install_group: InstallGroup
    template: str | None = None     # Jinja2 template filename (None for display-only)
    output_file: str | None = None  # rendered output filename (None for display-only)
