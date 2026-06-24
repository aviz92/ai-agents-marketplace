"""Manifest file writer."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.manifest import MANIFEST_HEADER
from marketplace.kind_catalog.models import CatalogItem
from marketplace.kind_catalog.registry import flat_kinds, per_agent_kinds
from marketplace.manifest.loader import manifest_path


def save_manifest(
    project_dir: Path,
    per_target: dict[str, list[CatalogItem]],
    external_items: list[CatalogItem] | None = None,
) -> Path:
    """Write the manifest describing what is installed per target."""
    data: dict = {}

    for target_id, items in per_target.items():
        entry: dict = {
            cfg.dir_name: sorted(item.id for item in items if item.kind == cfg.kind_name)
            for cfg in per_agent_kinds()
            if any(item.kind == cfg.kind_name for item in items)
        }
        if entry:
            data[target_id] = entry

    if external_items:
        for cfg in flat_kinds():
            if ids := sorted(item.id for item in external_items if item.kind == cfg.kind_name):
                data[cfg.dir_name] = ids

    path = manifest_path(project_dir)
    path.write_text(MANIFEST_HEADER + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
