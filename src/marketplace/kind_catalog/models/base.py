from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Self

from marketplace.consts.authoring import DEFAULT_AUTHOR, DEFAULT_VERSION
from marketplace.kind_catalog.kinds import KindConfig
from marketplace.kind_catalog.registry import get_kind

Kind = Literal["skill", "plugin", "rule", "external-plugin"]


@dataclass
class CatalogItem(ABC):
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
        return get_kind(self.kind)

    @property
    def label(self) -> str:
        return f"{self.config.icon} {self.name}"

    @classmethod
    def _common_fields(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> dict[str, Any]:
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
