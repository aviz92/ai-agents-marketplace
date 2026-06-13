"""Load authored artifacts (skills, plugins, rules) from disk into a catalog."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

from marketplace.consts.authoring import DEFAULT_AUTHOR, DEFAULT_VERSION, METADATA_FILE
from marketplace.consts.kinds import (
    BODY_FILES,
    DEFAULT_ICON,
    KIND_DIRS,
    KIND_ICONS,
    KIND_PLUGIN,
    KIND_SKILL,
)

# typing.Literal only accepts inline string literals (constants are a syntax error
# here) — keep in sync with KIND_SKILL / KIND_PLUGIN / KIND_RULE in kinds.py.
Kind = Literal["skill", "plugin", "rule"]

_log = logging.getLogger(__name__)


@dataclass
class CatalogItem:
    """A single authored artifact loaded from the marketplace."""

    id: str
    name: str
    description: str
    kind: Kind
    tags: list[str] = field(default_factory=list)
    author: str = DEFAULT_AUTHOR
    version: str = DEFAULT_VERSION
    globs: list[str] = field(default_factory=list)
    always_apply: bool = False
    content: str = ""
    path: Path = field(default_factory=Path)

    @property
    def label(self) -> str:
        icon = KIND_ICONS.get(self.kind, DEFAULT_ICON)
        return f"{icon} {self.name}"


def get_marketplace_root() -> Path:
    """Resolve the directory holding skills/, plugins/, rules/ and templates/.

    Dual-mode: prefer the source repo layout (content dirs next to src/);
    otherwise assume an installed wheel where content was force-included
    next to the package itself.
    """
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent.parent
    skills_dir = repo_root / KIND_DIRS[KIND_SKILL]
    plugins_dir = repo_root / KIND_DIRS[KIND_PLUGIN]
    if skills_dir.is_dir() or plugins_dir.is_dir():
        return repo_root
    return package_dir


def _load_item(item_dir: Path, kind: Kind) -> CatalogItem | None:
    metadata_file = item_dir / METADATA_FILE
    body_file = item_dir / BODY_FILES[kind]
    if not metadata_file.is_file() or not body_file.is_file():
        return None
    metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
    return CatalogItem(
        id=item_dir.name,
        name=str(metadata.get("name", item_dir.name)),
        description=str(metadata.get("description", "")),
        kind=kind,
        tags=list(metadata.get("tags") or []),
        author=str(metadata.get("author", DEFAULT_AUTHOR)),
        version=str(metadata.get("version", DEFAULT_VERSION)),
        globs=list(metadata.get("globs") or []),
        always_apply=bool(metadata.get("alwaysApply", False)),
        content=body_file.read_text(encoding="utf-8").strip() + "\n",
        path=item_dir,
    )


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
