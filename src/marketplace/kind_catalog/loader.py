from __future__ import annotations

import logging
from pathlib import Path

import yaml

from marketplace.consts.authoring import METADATA_FILE
from marketplace.kind_catalog.config import KindConfig
from marketplace.kind_catalog.registry import ALL_KINDS
from marketplace.kind_catalog.models import KIND_CLASSES, CatalogItem
from utils import get_marketplace_root

_log = logging.getLogger(__name__)


def _load_item(item_dir: Path, cfg: KindConfig) -> CatalogItem | None:
    metadata_file = item_dir / METADATA_FILE
    if not metadata_file.is_file():
        return None
    metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
    if cfg.body_filename:
        body_file = item_dir / cfg.body_filename
        if not body_file.is_file():
            return None
        content = body_file.read_text(encoding="utf-8").strip() + "\n"
    else:
        content = ""
    return KIND_CLASSES[cfg.kind_name].from_metadata(item_dir.name, metadata, content, item_dir)


def _load_kind(root: Path, cfg: KindConfig) -> list[CatalogItem]:
    kind_dir = root / cfg.dir_name
    if not kind_dir.is_dir():
        return []
    items: list[CatalogItem] = []
    for item_dir in sorted(kind_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        try:
            item = _load_item(item_dir, cfg)
        except (yaml.YAMLError, OSError, ValueError, TypeError) as exc:
            _log.warning("Skipping malformed %s item %s: %s", cfg.kind_name, item_dir.name, exc)
            continue
        if item is not None:
            items.append(item)
    return items


def load_catalog() -> list[CatalogItem]:
    """Load every artifact from the marketplace root, sorted by (kind, name)."""
    root = get_marketplace_root()
    items: list[CatalogItem] = []
    for cfg in ALL_KINDS:
        items.extend(_load_kind(root, cfg))
    return sorted(items, key=lambda item: (item.kind, item.name.lower()))
