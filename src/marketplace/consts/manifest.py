"""Manifest file constants."""

from __future__ import annotations

from marketplace.kind_catalog.config import ALL_KINDS, KindConfig, ManifestMode

MANIFEST_NAME = "agents-marketplace.yaml"
MANIFEST_EXTERNAL_KEY = "external-plugins"

MANIFEST_PER_AGENT_KINDS: tuple[KindConfig, ...] = tuple(
    cfg for cfg in ALL_KINDS if cfg.manifest_mode == ManifestMode.PER_AGENT
)
MANIFEST_FLAT_KINDS: tuple[KindConfig, ...] = tuple(
    cfg for cfg in ALL_KINDS if cfg.manifest_mode == ManifestMode.FLAT
)

MANIFEST_HEADER = """\
# agents-marketplace team-sync manifest — commit this file.
# Install everything declared below by running this from the project root:
#   uvx --from git+https://github.com/aviz92/ai-agents-marketplace agents-marketplace sync
# (once on PyPI: `uvx agents-marketplace sync`)
#
# Format: each top-level key is an agent target (claude, agents, cursor, copilot, codex, gemini).
# Under each target, declare which skills/plugins/rules to install for that agent only.
# external-plugins: flat list of third-party plugin IDs to display install commands for.
"""
