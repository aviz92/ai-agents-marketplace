"""Manifest file writer."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.manifest import MANIFEST_HEADER, MANIFEST_KIND_KEYS
from marketplace.manifest.loader import manifest_path
from marketplace.models import CatalogItem


def save_manifest(
    project_dir: Path,
    per_target: dict[str, list[CatalogItem]],
) -> Path:
    """Write the manifest describing what is installed per target."""
    data: dict = {}
    for target_id, items in per_target.items():
        entry: dict = {
            key: sorted(item.id for item in items if item.kind == kind)
            for kind, key in MANIFEST_KIND_KEYS
            if any(item.kind == kind for item in items)
        }
        if entry:
            data[target_id] = entry
    path = manifest_path(project_dir)
    path.write_text(MANIFEST_HEADER + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
