"""General-purpose utilities for the marketplace package."""

from __future__ import annotations

from pathlib import Path

from marketplace.kind_catalog.kinds import PLUGIN, SKILL


def get_marketplace_root() -> Path:
    """Resolve the directory holding skills/, plugins/, rules/ and templates/.

    Walks up from the package directory looking for a directory that contains
    the skills/ or plugins/ content tree. This handles both the source-repo
    layout (content dirs next to src/) and an installed wheel (content dirs
    placed next to the package by hatchling's force-include).
    """
    package_dir = Path(__file__).resolve().parent
    for candidate in (package_dir, *package_dir.parents):
        has_skills = (candidate / SKILL.dir_name).is_dir()
        has_plugins = (candidate / PLUGIN.dir_name).is_dir()
        if has_skills or has_plugins:
            return candidate
    # No content tree found — fall back to the package directory itself.
    return package_dir
