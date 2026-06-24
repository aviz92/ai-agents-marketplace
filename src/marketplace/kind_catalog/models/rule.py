from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Self

from marketplace.kind_catalog.kinds import RULE as RULE_KIND
from marketplace.kind_catalog.models.base import CatalogItem, Kind


@dataclass
class Rule(CatalogItem):
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
