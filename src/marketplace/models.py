"""Core data model for marketplace artifacts — no IO, safe to import anywhere.

`CatalogItem` is an ABC; every artifact kind is a concrete subclass that declares
its own `kind` and implements `from_metadata`. Build instances via
`KIND_CLASSES[kind].from_metadata(...)`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Self

from marketplace.consts.authoring import DEFAULT_AUTHOR, DEFAULT_VERSION
from marketplace.kinds import KindConfig
from marketplace.kinds import (
    EXTERNAL_PLUGIN as EXTERNAL_PLUGIN_KIND,
    PLUGIN as PLUGIN_KIND,
    RULE as RULE_KIND,
    SKILL as SKILL_KIND,
    get_kind,
)

# typing.Literal only accepts inline string literals (constants are a syntax error
# here) — keep in sync with the kind strings in consts/kinds.py.
Kind = Literal["skill", "plugin", "rule", "external-plugin"]


@dataclass
class CatalogItem(ABC):
    """Abstract base for every marketplace artifact.

    Not instantiated directly — use a concrete subclass (Skill, Plugin, Rule, ExternalPlugin).
    """

    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    author: str = DEFAULT_AUTHOR
    version: str = DEFAULT_VERSION
    content: str = ""
    path: Path | None = None

    kind: ClassVar[Kind]

    @property
    def config(self) -> KindConfig:
        """This kind's full configuration — use instead of scattered constant lookups."""
        return get_kind(self.kind)

    @property
    def label(self) -> str:
        return f"{self.config.icon} {self.name}"

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
    @abstractmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        """Build an instance of this kind from parsed metadata and body content."""


@dataclass
class Rule(CatalogItem):
    """A coding rule (rules/) — adds glob scoping and an always-apply flag."""

    kind: ClassVar[Kind] = RULE_KIND.kind_name
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


@dataclass
class Skill(CatalogItem):
    """A reusable agent skill (skills/)."""

    kind: ClassVar[Kind] = SKILL_KIND.kind_name

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        return cls(**cls._common_fields(item_id, metadata, content, path))


@dataclass
class Plugin(CatalogItem):
    """A plugin bundle (plugins/) — same shape as a skill, different home."""

    kind: ClassVar[Kind] = PLUGIN_KIND.kind_name

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        return cls(**cls._common_fields(item_id, metadata, content, path))


@dataclass
class ExternalPlugin(CatalogItem):
    """A third-party plugin (external-plugins/) — pointer to an external repo + install command.

    The install command is stored and displayed; it is never executed by the marketplace.
    """

    kind: ClassVar[Kind] = EXTERNAL_PLUGIN_KIND.kind_name
    source: str = ""
    install: str = ""

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        source = metadata.get("source")
        install = metadata.get("install")
        if not source or not install:
            raise ValueError(
                f"External plugin '{item_id}' missing required 'source' or 'install' field"
            )
        return cls(
            **cls._common_fields(item_id, metadata, content, path),
            source=str(source),
            install=str(install),
        )


KIND_CLASSES: dict[str, type[CatalogItem]] = {
    RULE_KIND.kind_name: Rule,
    SKILL_KIND.kind_name: Skill,
    PLUGIN_KIND.kind_name: Plugin,
    EXTERNAL_PLUGIN_KIND.kind_name: ExternalPlugin,
}
