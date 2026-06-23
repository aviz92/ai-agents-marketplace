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
    """

    per_agent: dict[str, dict[str, list[str]]] = field(default_factory=dict)

