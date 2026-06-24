from __future__ import annotations

from dataclasses import dataclass

from marketplace.consts.kinds import KindCategory
from marketplace.consts.manifest import ManifestMode


@dataclass(frozen=True)
class KindConfig:
    """Complete specification for one artifact kind."""

    kind_name: str
    dir_name: str
    icon: str
    display_name: str
    table_style: str  # Rich markup color for summary table ("" = default)
    body_filename: str | None  # None = metadata-only (no body file on disk)
    manifest_mode: ManifestMode
    kind_category: KindCategory
    template: str | None = None  # Jinja2 template filename (None for display-only)
    output_file: str | None = None  # rendered output filename (None for display-only)
