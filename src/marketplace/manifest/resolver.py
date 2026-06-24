"""Catalog resolution for manifest entries."""

from __future__ import annotations

from marketplace.consts.kinds import KIND_EXTERNAL_PLUGIN
from marketplace.consts.manifest import MANIFEST_KIND_KEYS
from marketplace.manifest.models import Manifest
from marketplace.models import CatalogItem


def resolve_per_agent(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[dict[str, list[CatalogItem]], list[str]]:
    """Resolve per-target artifact IDs against the catalog.

    Returns (per_target_items, missing_refs).
    """
    kind_index: dict[str, dict[str, CatalogItem]] = {
        kind: {item.id: item for item in catalog if item.kind == kind}
        for kind, _ in MANIFEST_KIND_KEYS
    }
    per_target: dict[str, list[CatalogItem]] = {}
    missing: list[str] = []
    for target_id, entry in manifest.per_agent.items():
        items: list[CatalogItem] = []
        for kind, key in MANIFEST_KIND_KEYS:
            if key not in entry:
                continue
            kind_items = kind_index[kind]
            for item_id in entry[key]:
                if item_id in kind_items:
                    items.append(kind_items[item_id])
                else:
                    missing.append(f"{kind}:{item_id}")
        per_target[target_id] = items
    return per_target, missing


def resolve_external(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[list[CatalogItem], list[str]]:
    """Resolve external-plugin IDs from the manifest against the catalog.

    Returns (external_items, missing_refs).
    """
    ext_index = {item.id: item for item in catalog if item.kind == KIND_EXTERNAL_PLUGIN}
    items: list[CatalogItem] = []
    missing: list[str] = []
    for item_id in manifest.external:
        if item_id in ext_index:
            items.append(ext_index[item_id])
        else:
            missing.append(f"{KIND_EXTERNAL_PLUGIN}:{item_id}")
    return items, missing
