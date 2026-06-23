"""Core data model for marketplace artifacts — no IO, safe to import anywhere.

`CatalogItem` holds the fields every artifact shares; each kind is a subclass that
fixes its own `kind` and adds only the fields it actually needs. Build instances
from parsed metadata via `from_metadata` (or `KIND_CLASSES[kind].from_metadata`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Self

from marketplace.consts.authoring import DEFAULT_AUTHOR, DEFAULT_VERSION
from marketplace.consts.kinds import (
    DEFAULT_ICON,
    KIND_ICONS,
    KIND_PLUGIN,
    KIND_RULE,
    KIND_SKILL,
)

# typing.Literal only accepts inline string literals (constants are a syntax error
# here) — keep in sync with KIND_SKILL / KIND_PLUGIN / KIND_RULE in kinds.py.
Kind = Literal["skill", "plugin", "rule"]


@dataclass
class CatalogItem:
    """Fields shared by every authored artifact.

    Not instantiated directly — use a concrete subclass (`Skill`, `Plugin`, `Rule`),
    each of which fixes `kind` and adds its own kind-specific fields.
    """

    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    author: str = DEFAULT_AUTHOR
    version: str = DEFAULT_VERSION
    content: str = ""
    path: Path = field(default_factory=Path)

    kind: ClassVar[Kind]

    @property
    def label(self) -> str:
        return f"{KIND_ICONS.get(self.kind, DEFAULT_ICON)} {self.name}"

    @classmethod
    def _common_fields(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> dict[str, Any]:
        """Parse the fields shared by every kind out of raw metadata."""
        return {
            "id": item_id,
            "name": str(metadata.get("name", item_id)),
            "description": str(metadata.get("description", "")),
            "tags": list(metadata.get("tags") or []),
            "author": str(metadata.get("author", DEFAULT_AUTHOR)),
            "version": str(metadata.get("version", DEFAULT_VERSION)),
            "content": content,
            "path": path,
        }

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        """Build an instance of this kind from parsed metadata and body content."""
        return cls(**cls._common_fields(item_id, metadata, content, path))


@dataclass
class Skill(CatalogItem):
    """A reusable agent skill (skills/)."""

    kind: ClassVar[Kind] = KIND_SKILL


@dataclass
class Plugin(CatalogItem):
    """A plugin bundle (plugins/) — same shape as a skill, different home."""

    kind: ClassVar[Kind] = KIND_PLUGIN


@dataclass
class Rule(CatalogItem):
    """A coding rule (rules/) — adds glob scoping and an always-apply flag."""

    kind: ClassVar[Kind] = KIND_RULE
    globs: list[str] = field(default_factory=list)
    always_apply: bool = False

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        return cls(
            **cls._common_fields(item_id, metadata, content, path),
            globs=list(metadata.get("globs") or []),
            always_apply=bool(metadata.get("alwaysApply", False)),
        )


KIND_CLASSES: dict[Kind, type[CatalogItem]] = {
    KIND_SKILL: Skill,
    KIND_PLUGIN: Plugin,
    KIND_RULE: Rule,
}
