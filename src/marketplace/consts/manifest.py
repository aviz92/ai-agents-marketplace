from __future__ import annotations

from enum import Enum


class ManifestMode(str, Enum):
    """How a kind appears in agents-marketplace.yaml."""

    PER_AGENT = "per_agent"
    FLAT = "flat"


MANIFEST_NAME = "agents-marketplace.yaml"
MANIFEST_EXTERNAL_KEY = "external-plugins"
MANIFEST_FORKED_FROM_KEY = "forked_from"

MANIFEST_HEADER = """\
# agents-marketplace team-sync manifest — commit this file.
# Install everything declared below by running this from the project root:
#   uvx --from git+https://github.com/aviz92/ai-agents-marketplace agents-marketplace sync
# (once on PyPI: `uvx agents-marketplace sync`)
#
# Format: each top-level key is an agent target (claude, agents, cursor, copilot, codex, gemini).
# Under each target, declare which skills/plugins/rules to install for that agent only.
# external-plugins: flat list of third-party plugin IDs to display install commands for.
# forked_from: optional, only set this in a fork of ai-agents-marketplace itself — the
#   org/repo slug of the repo this fork was forked from, e.g. team-a/ai-agents-marketplace.
"""
