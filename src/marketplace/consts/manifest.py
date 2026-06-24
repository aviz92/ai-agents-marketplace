"""Manifest file constants."""

from __future__ import annotations

from marketplace.consts.kinds import KIND_DIRS

MANIFEST_NAME = "agents-marketplace.yaml"
MANIFEST_EXTERNAL_KEY = "external-plugins"
MANIFEST_KIND_KEYS: list[tuple[str, str]] = [
    (kind, key) for kind, key in KIND_DIRS.items() if kind != "external-plugin"
]
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
