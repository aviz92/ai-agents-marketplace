"""Artifact kind identifiers and per-kind metadata."""

from __future__ import annotations

KIND_SKILL = "skill"
KIND_PLUGIN = "plugin"
KIND_RULE = "rule"
SKILL_LIKE_KINDS = frozenset({KIND_SKILL, KIND_PLUGIN})

KIND_DIRS: dict[str, str] = {KIND_SKILL: "skills", KIND_PLUGIN: "plugins", KIND_RULE: "rules"}
BODY_FILES: dict[str, str] = {
    KIND_SKILL: "skill.md",
    KIND_PLUGIN: "plugin.md",
    KIND_RULE: "rule.md",
}
KIND_ICONS: dict[str, str] = {KIND_SKILL: "🧠", KIND_PLUGIN: "🔌", KIND_RULE: "📏"}
DEFAULT_ICON = "📄"

KIND_SECTIONS: list[tuple[str, str]] = [
    (KIND_SKILL, f"{KIND_ICONS[KIND_SKILL]} Skills"),
    (KIND_PLUGIN, f"{KIND_ICONS[KIND_PLUGIN]} Plugins"),
    (KIND_RULE, f"{KIND_ICONS[KIND_RULE]} Rules"),
]
