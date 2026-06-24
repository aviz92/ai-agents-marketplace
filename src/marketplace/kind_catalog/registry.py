from __future__ import annotations

from functools import cache

from marketplace.consts.manifest import ManifestMode
from marketplace.kind_catalog.config import KindConfig


@cache
def _all_kinds() -> tuple[KindConfig, ...]:
    from marketplace.kind_catalog.kinds import EXTERNAL_PLUGIN, PLUGIN, RULE, SKILL
    return (SKILL, PLUGIN, RULE, EXTERNAL_PLUGIN)


@cache
def _per_agent_kinds() -> tuple[KindConfig, ...]:
    return tuple(cfg for cfg in _all_kinds() if cfg.manifest_mode == ManifestMode.PER_AGENT)


@cache
def _flat_kinds() -> tuple[KindConfig, ...]:
    return tuple(cfg for cfg in _all_kinds() if cfg.manifest_mode == ManifestMode.FLAT)


@cache
def _registry() -> dict[str, KindConfig]:
    return {cfg.kind_name: cfg for cfg in _all_kinds()}


def __getattr__(name: str) -> object:
    if name == "ALL_KINDS":
        return _all_kinds()
    if name == "PER_AGENT_KINDS":
        return _per_agent_kinds()
    if name == "FLAT_KINDS":
        return _flat_kinds()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_kind(kind: str) -> KindConfig:
    try:
        return _registry()[kind]
    except KeyError:
        raise ValueError(f"Unknown artifact kind: {kind!r}") from None
