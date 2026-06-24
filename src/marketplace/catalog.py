"""Load authored artifacts (skills, plugins, rules) from disk into a catalog."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from marketplace.consts.authoring import METADATA_FILE
from marketplace.consts.kinds import BODY_FILES, KIND_DIRS
from marketplace.models import KIND_CLASSES, CatalogItem, Kind
from marketplace.utils import get_marketplace_root

_log = logging.getLogger(__name__)


def _load_item(item_dir: Path, kind: Kind) -> CatalogItem | None:
    metadata_file = item_dir / METADATA_FILE
    if not metadata_file.is_file():
        return None
    metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
    if kind in BODY_FILES:
        body_file = item_dir / BODY_FILES[kind]
        if not body_file.is_file():
            return None
        content = body_file.read_text(encoding="utf-8").strip() + "\n"
    else:
        content = ""
    return KIND_CLASSES[kind].from_metadata(item_dir.name, metadata, content, item_dir)


def _load_kind(root: Path, kind: Kind) -> list[CatalogItem]:
    kind_dir = root / KIND_DIRS[kind]
    if not kind_dir.is_dir():
        return []
    items: list[CatalogItem] = []
    for item_dir in sorted(kind_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        try:
            item = _load_item(item_dir, kind)
        except (yaml.YAMLError, OSError, ValueError, TypeError) as exc:
            _log.warning("Skipping malformed %s item %s: %s", kind, item_dir.name, exc)
            continue
        if item is not None:
            items.append(item)
    return items


def load_catalog() -> list[CatalogItem]:
    """Load every artifact from the marketplace root, sorted by (kind, name)."""
    root = get_marketplace_root()
    items: list[CatalogItem] = []
    for kind in KIND_DIRS:
        items.extend(_load_kind(root, kind))
    return sorted(items, key=lambda item: (item.kind, item.name.lower()))
