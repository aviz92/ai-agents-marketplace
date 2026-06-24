from __future__ import annotations

from enum import Enum


class KindCategory(str, Enum):
    SKILL = "skill"
    PLUGIN = "plugin"
    RULES = "rules"
    EXTERNAL_PLUGIN = "external_plugin"


SKILLS_TARGET_GROUPS: frozenset[KindCategory] = frozenset({KindCategory.SKILL, KindCategory.PLUGIN})
RULE_TARGET_GROUPS: frozenset[KindCategory] = frozenset({KindCategory.RULES})
