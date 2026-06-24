"""Manifest file writer."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.kinds import KIND_EXTERNAL_PLUGIN
from marketplace.consts.manifest import MANIFEST_EXTERNAL_KEY, MANIFEST_HEADER, MANIFEST_KIND_KEYS
from marketplace.manifest.loader import manifest_path
from marketplace.models import CatalogItem


def save_manifest(
    project_dir: Path,
    per_target: dict[str, list[CatalogItem]],
    external_items: list[CatalogItem] | None = None,
) -> Path:
    """Write the manifest describing what is installed per target."""
    data: dict = {}
    if external_items:
        data[MANIFEST_EXTERNAL_KEY] = sorted(
            item.id for item in external_items if item.kind == KIND_EXTERNAL_PLUGIN
        )
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
