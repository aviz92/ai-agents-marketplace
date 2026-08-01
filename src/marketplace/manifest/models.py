"""Manifest data models."""

from __future__ import annotations

from dataclasses import dataclass, field


class ManifestError(ValueError):
    """Raised when the manifest file is malformed or references unknown targets."""


@dataclass
class Manifest:
    """Parsed contents of agents-marketplace.yaml.

    per_agent maps each target_id to a dict of kind_key -> explicit artifact IDs.
    Example: {"claude": {"skills": ["a"], "rules": ["b"]}, "cursor": {"rules": ["b"]}}

    flat maps dir_name -> [ids] for ManifestMode.FLAT kinds (e.g. external-plugins).

    forked_from is the org/repo slug this fork was forked from, when this
    manifest lives in a fork of ai-agents-marketplace itself.
    """

    per_agent: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    flat: dict[str, list[str]] = field(default_factory=dict)
    forked_from: str | None = None
