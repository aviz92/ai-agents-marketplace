from __future__ import annotations

from marketplace.consts.manifest import ManifestMode
from marketplace.kind_catalog.config import KindConfig
from marketplace.kind_catalog.kinds import EXTERNAL_PLUGIN, PLUGIN, RULE, SKILL

ALL_KINDS: tuple[KindConfig, ...] = (SKILL, PLUGIN, RULE, EXTERNAL_PLUGIN)

PER_AGENT_KINDS: tuple[KindConfig, ...] = tuple(
    cfg for cfg in ALL_KINDS if cfg.manifest_mode == ManifestMode.PER_AGENT
)
FLAT_KINDS: tuple[KindConfig, ...] = tuple(
    cfg for cfg in ALL_KINDS if cfg.manifest_mode == ManifestMode.FLAT
)

_REGISTRY: dict[str, KindConfig] = {cfg.kind_name: cfg for cfg in ALL_KINDS}


def get_kind(kind: str) -> KindConfig:
    try:
        return _REGISTRY[kind]
    except KeyError:
        raise ValueError(f"Unknown artifact kind: {kind!r}") from None
