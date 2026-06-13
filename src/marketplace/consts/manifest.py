"""Manifest file constants."""

from __future__ import annotations

from marketplace.consts.kinds import KIND_DIRS

MANIFEST_NAME = "agents-marketplace.yaml"
MANIFEST_ALL = "all"
MANIFEST_KIND_KEYS: list[tuple[str, str]] = list(KIND_DIRS.items())
MANIFEST_TARGETS_KEY = "targets"
MANIFEST_HEADER = """\
# agents-marketplace team-sync manifest — commit this file.
# Install everything declared below by running this from the project root:
#   uvx --from git+https://github.com/aviz92/ai-marketplace agents-marketplace sync
# (once on PyPI: `uvx agents-marketplace sync`)
"""
