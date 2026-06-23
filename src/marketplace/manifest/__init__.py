"""Project manifest (agents-marketplace.yaml) — declarative installs for team sync.

A project commits this file to declare which artifacts each agent target should have;
`agents-marketplace sync` installs them non-interactively after a fresh clone.
"""

from __future__ import annotations

from marketplace.consts.manifest import MANIFEST_HEADER, MANIFEST_NAME
from marketplace.manifest.loader import load_manifest, manifest_path
from marketplace.manifest.models import Manifest, ManifestError
from marketplace.manifest.resolver import resolve_per_agent
from marketplace.manifest.writer import save_manifest

__all__ = [
    "MANIFEST_HEADER",
    "MANIFEST_NAME",
    "Manifest",
    "ManifestError",
    "load_manifest",
    "manifest_path",
    "resolve_per_agent",
    "save_manifest",
]
