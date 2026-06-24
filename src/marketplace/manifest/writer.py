"""Manifest file writer."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.manifest import (
    MANIFEST_FLAT_KINDS,
    MANIFEST_HEADER,
    MANIFEST_PER_AGENT_KINDS,
)
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
        for cfg in MANIFEST_FLAT_KINDS:
            ids = sorted(item.id for item in external_items if item.kind == cfg.kind_name)
            if ids:
                data[cfg.dir_name] = ids

    for target_id, items in per_target.items():
        entry: dict = {
            cfg.dir_name: sorted(item.id for item in items if item.kind == cfg.kind_name)
            for cfg in MANIFEST_PER_AGENT_KINDS
            if any(item.kind == cfg.kind_name for item in items)
        }
        if entry:
            data[target_id] = entry

    path = manifest_path(project_dir)
    path.write_text(MANIFEST_HEADER + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
