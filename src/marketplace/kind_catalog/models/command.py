from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Self

from marketplace.kind_catalog.kinds import COMMAND as COMMAND_KIND
from marketplace.kind_catalog.models.base import CatalogItem, Kind


@dataclass
class Command(CatalogItem):
    kind: ClassVar[Kind] = COMMAND_KIND.kind_name

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        return cls(**cls._common_fields(item_id, metadata, content, path))
