from __future__ import annotations

from functools import cache

from marketplace.consts.manifest import ManifestMode
from marketplace.kind_catalog.kinds import COMMAND, EXTERNAL_PLUGIN, PLUGIN, RULE, SKILL, KindConfig


@cache
def all_kinds() -> tuple[KindConfig, ...]:
    return SKILL, PLUGIN, RULE, EXTERNAL_PLUGIN, COMMAND


@cache
def per_agent_kinds() -> tuple[KindConfig, ...]:
    return tuple(cfg for cfg in all_kinds() if cfg.manifest_mode == ManifestMode.PER_AGENT)


@cache
def flat_kinds() -> tuple[KindConfig, ...]:
    return tuple(cfg for cfg in all_kinds() if cfg.manifest_mode == ManifestMode.FLAT)


@cache
def _registry() -> dict[str, KindConfig]:
    return {cfg.kind_name: cfg for cfg in all_kinds()}


def get_kind(kind: str) -> KindConfig:
    try:
        return _registry()[kind]
    except KeyError:
        raise ValueError(f"Unknown artifact kind: {kind!r}") from None
