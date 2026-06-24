"""The sync-agent picker: group manifest targets by kind and render their choice rows.

This is the one elaborate prompt — a multi-column, terminal-width-aware label per
agent — kept apart from the simpler questions in the install flow's prompts.
"""

from __future__ import annotations

import shutil

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from marketplace.consts import display
from marketplace.consts.agents import AGENT_NAMES, TARGET_AGENTS
from marketplace.installer import RuleTargetInfo, TargetInfo, rule_targets, targets
from marketplace.kind_catalog.kinds import PLUGIN, RULE, SKILL, KindConfig
from marketplace.kind_catalog.models import CatalogItem, ExternalPlugin

_NAME_W = 26
_KIND_W = 11
_GUTTER = 4  # "  ◉ " prefix InquirerPy adds to every choice row
_ARROW = "  →  "


def _target_info() -> dict[str, TargetInfo | RuleTargetInfo]:
    return {**targets(), **rule_targets()}


_DISPLAY_NAMES = {**AGENT_NAMES, TARGET_AGENTS: "agents/ (multi-agent)"}

# Each kind's section title and the singular/plural noun for its count column, in display order.
_SECTIONS: tuple[tuple[KindConfig, str, tuple[str, str]], ...] = (
    (SKILL, display.SYNC_SECTION_SKILLS, ("skill", "skills")),
    (PLUGIN, display.SYNC_SECTION_PLUGINS, ("plugin", "plugins")),
    (RULE, display.SYNC_SECTION_RULES, ("rule", "rules")),
)
_NOUNS: dict[KindConfig, tuple[str, str]] = {cfg: nouns for cfg, _, nouns in _SECTIONS}


def _has_kind(items: list[CatalogItem], cfg: KindConfig) -> bool:
    return any(item.config == cfg for item in items)


def _kind_column(items: list[CatalogItem], cfg: KindConfig) -> tuple[int, str, str]:
    count = sum(1 for item in items if item.config == cfg)
    return (count, *_NOUNS[cfg])


def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}" if count else display.EMPTY_VALUE


def _primary_kind(items: list[CatalogItem]) -> KindConfig:
    """The section a target belongs to: skills outrank plugins outrank rules.

    Every populated target carries at least one kind, so a match is always found.
    """
    for cfg, _, _ in _SECTIONS:
        if _has_kind(items, cfg):
            return cfg
    return RULE  # unreachable: a populated target always has a kind


def _covers(target_id: str, prefix_len: int) -> str:
    if not (target := _target_info().get(target_id)):
        return ""
    joined = ", ".join(target.covers)
    available = max(
        20,
        shutil.get_terminal_size().columns - prefix_len - _GUTTER - len(_ARROW),
    )
    return (joined[: available - 1] + "…") if len(joined) > available else joined


def _choice(target_id: str, columns: list[tuple[int, str, str]]) -> Choice:
    """One agent row: name, one count column per kind, then an arrow and its coverage."""
    prefix = f"{_DISPLAY_NAMES.get(target_id, target_id):<{_NAME_W}}"
    for count, singular, plural in columns:
        prefix += f"  {_count_label(count, singular, plural):<{_KIND_W}}"
    label = prefix + _ARROW + _covers(target_id, len(prefix))
    return Choice(value=target_id, name=label, enabled=True)


def prompt_confirm_external_plugin(plugin: ExternalPlugin) -> bool:
    """Ask user to confirm before running a third-party install command."""
    return inquirer.confirm(
        message=f"Run install command for {plugin.name}?\n  [dim]{plugin.install}[/dim]",
        default=True,
    ).execute()


def prompt_sync_agents(per_target: dict[str, list[CatalogItem]]) -> list[str]:
    grouped: dict[KindConfig, dict[str, list[CatalogItem]]] = {cfg: {} for cfg, _, _ in _SECTIONS}
    for target_id, items in per_target.items():
        if items:
            grouped[_primary_kind(items)][target_id] = items

    # Skill rows show a plugin column too, but only when a skill target also carries plugins.
    skills_show_plugins = any(_has_kind(i, PLUGIN) for i in grouped[SKILL].values())

    def columns_for(cfg: KindConfig, items: list[CatalogItem]) -> list[tuple[int, str, str]]:
        if cfg == SKILL and skills_show_plugins:
            return [_kind_column(items, SKILL), _kind_column(items, PLUGIN)]
        return [_kind_column(items, cfg)]

    choices: list[Choice | Separator] = []
    for cfg, title, _ in _SECTIONS:
        if not (group := grouped[cfg]):
            continue
        choices.append(Separator(""))
        choices.append(Separator(title))
        choices.extend(_choice(tid, columns_for(cfg, items)) for tid, items in group.items())
    choices.append(Separator(""))

    return inquirer.checkbox(
        message=display.PROMPT_SYNC_AGENTS, choices=choices, cycle=True
    ).execute()
