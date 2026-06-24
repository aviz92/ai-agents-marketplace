from __future__ import annotations

from marketplace.consts.kinds import KindCategory
from marketplace.consts.manifest import ManifestMode
from marketplace.consts.render import (
    PLUGIN_OUTPUT_FILE,
    PLUGIN_TEMPLATE,
    SKILL_OUTPUT_FILE,
    SKILL_TEMPLATE,
)
from marketplace.kind_catalog.config import KindConfig

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
