from marketplace.kind_catalog.kinds import (
    EXTERNAL_PLUGIN as EXTERNAL_PLUGIN_KIND,
    PLUGIN as PLUGIN_KIND,
    RULE as RULE_KIND,
    SKILL as SKILL_KIND,
)
from marketplace.kind_catalog.models.base import CatalogItem, Kind
from marketplace.kind_catalog.models.external_plugin import ExternalPlugin
from marketplace.kind_catalog.models.plugin import Plugin
from marketplace.kind_catalog.models.rule import Rule
from marketplace.kind_catalog.models.skill import Skill

KIND_CLASSES: dict[str, type[CatalogItem]] = {
    RULE_KIND.kind_name: Rule,
    SKILL_KIND.kind_name: Skill,
    PLUGIN_KIND.kind_name: Plugin,
    EXTERNAL_PLUGIN_KIND.kind_name: ExternalPlugin,
}

__all__ = [
    "CatalogItem",
    "ExternalPlugin",
    "Kind",
    "KIND_CLASSES",
    "Plugin",
    "Rule",
    "Skill",
]
