from __future__ import annotations

from dataclasses import dataclass

from marketplace.consts.kinds import KindCategory
from marketplace.consts.manifest import ManifestMode
from marketplace.consts.render import (
    PLUGIN_OUTPUT_FILE,
    PLUGIN_TEMPLATE,
    SKILL_OUTPUT_FILE,
    SKILL_TEMPLATE,
)


@dataclass(frozen=True)
class KindConfig:
    """Complete specification for one artifact kind."""

    kind_name: str
    dir_name: str
    icon: str
    display_name: str
    table_style: str           # Rich markup color for summary table ("" = default)
    body_filename: str | None  # None = metadata-only (no body file on disk)
    manifest_mode: ManifestMode
    kind_category: KindCategory
    template: str | None = None     # Jinja2 template filename (None for display-only)
    output_file: str | None = None  # rendered output filename (None for display-only)


SKILL = KindConfig(
    kind_name="skill",
    dir_name="skills",
    icon="🧠",
    display_name="Skills",
    table_style="green",
    body_filename="skill.md",
    manifest_mode=ManifestMode.PER_AGENT,
    kind_category=KindCategory.SKILL,
    template=SKILL_TEMPLATE,
    output_file=SKILL_OUTPUT_FILE,
)
PLUGIN = KindConfig(
    kind_name="plugin",
    dir_name="plugins",
    icon="🔌",
    display_name="Plugins",
    table_style="blue",
    body_filename="plugin.md",
    manifest_mode=ManifestMode.PER_AGENT,
    kind_category=KindCategory.PLUGIN,
    template=PLUGIN_TEMPLATE,
    output_file=PLUGIN_OUTPUT_FILE,
)
RULE = KindConfig(
    kind_name="rule",
    dir_name="rules",
    icon="📏",
    display_name="Rules",
    table_style="yellow",
    body_filename="rule.md",
    manifest_mode=ManifestMode.PER_AGENT,
    kind_category=KindCategory.RULES,
)
EXTERNAL_PLUGIN = KindConfig(
    kind_name="external-plugin",
    dir_name="external-plugins",
    icon="🌐",
    display_name="External",
    table_style="",
    body_filename=None,
    manifest_mode=ManifestMode.FLAT,
    kind_category=KindCategory.EXTERNAL_PLUGIN,
)

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