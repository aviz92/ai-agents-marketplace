"""Catalog resolution for manifest entries."""

from __future__ import annotations

from marketplace.consts.kinds import ManifestMode
from marketplace.consts.manifest import MANIFEST_FLAT_KINDS, MANIFEST_PER_AGENT_KINDS
from marketplace.manifest.models import Manifest
from marketplace.kind_catalog.models import CatalogItem


def resolve_per_agent(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[dict[str, list[CatalogItem]], list[str]]:
    """Resolve per-target artifact IDs against the catalog.

    Returns (per_target_items, missing_refs).
    """
    kind_index: dict[str, dict[str, CatalogItem]] = {
        cfg.kind_name: {item.id: item for item in catalog if item.kind == cfg.kind_name}
        for cfg in MANIFEST_PER_AGENT_KINDS
    }
    per_target: dict[str, list[CatalogItem]] = {}
    missing: list[str] = []
    for target_id, entry in manifest.per_agent.items():
        items: list[CatalogItem] = []
        for cfg in MANIFEST_PER_AGENT_KINDS:
            if cfg.dir_name not in entry:
                continue
            kind_items = kind_index[cfg.kind_name]
            for item_id in entry[cfg.dir_name]:
                if item_id in kind_items:
                    items.append(kind_items[item_id])
                else:
                    missing.append(f"{cfg.kind_name}:{item_id}")
        per_target[target_id] = items
    return per_target, missing


def resolve_flat(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[list[CatalogItem], list[str]]:
    """Resolve flat-mode artifact IDs from the manifest against the catalog.

    Works for any ManifestMode.FLAT kind (e.g. external-plugins).
    Returns (items, missing_refs).
    """
    flat_dir_to_cfg = {cfg.dir_name: cfg for cfg in MANIFEST_FLAT_KINDS}
    index = {
        item.id: item
        for item in catalog
        if item.config.manifest_mode == ManifestMode.FLAT
    }
    items: list[CatalogItem] = []
    missing: list[str] = []
    for key, ids in manifest.flat.items():
        cfg = flat_dir_to_cfg.get(key)
        kind_label = cfg.kind_name if cfg else key
        for item_id in ids:
            if item_id in index:
                items.append(index[item_id])
            else:
                missing.append(f"{kind_label}:{item_id}")
    return items, missing
