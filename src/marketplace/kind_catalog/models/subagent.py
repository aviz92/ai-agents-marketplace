from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Self

from marketplace.consts.models import ModelStrength
from marketplace.kind_catalog.kinds import SUBAGENT as SUBAGENT_KIND
from marketplace.kind_catalog.models.base import CatalogItem, Kind

_DEFAULT_MODEL_STRENGTH = ModelStrength.REGULAR.value


@dataclass
class Subagent(CatalogItem):
    kind: ClassVar[Kind] = SUBAGENT_KIND.kind_name
    model_strength: str = _DEFAULT_MODEL_STRENGTH

    @classmethod
    def from_metadata(
        cls, item_id: str, metadata: dict[str, Any], content: str, path: Path
    ) -> Self:
        strength = str(metadata.get("model_strength") or _DEFAULT_MODEL_STRENGTH)
        if strength not in {s.value for s in ModelStrength}:
            raise ValueError(
                f"Invalid model_strength {strength!r} for subagent '{item_id}'"
                f" — expected one of {[s.value for s in ModelStrength]}"
            )
        return cls(
            **cls._common_fields(item_id, metadata, content, path),
            model_strength=strength,
        )
