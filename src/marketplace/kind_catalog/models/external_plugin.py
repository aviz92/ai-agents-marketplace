from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Self

from marketplace.kind_catalog.kinds import EXTERNAL_PLUGIN as EXTERNAL_PLUGIN_KIND
from marketplace.kind_catalog.models.base import CatalogItem, Kind


@dataclass
class ExternalPlugin(CatalogItem):
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
