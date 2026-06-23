"""Prompts for the interactive install flow — pick items, pick targets, confirm, save."""

from __future__ import annotations

from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console

from marketplace.cli.render import _description_width, _item_row, _picker_header
from marketplace.cli.status import collect_installed_state
from marketplace.consts import display
from marketplace.consts.agents import AGENT_CLAUDE, TARGET_AGENTS
from marketplace.consts.kinds import KIND_RULE, KIND_SECTIONS, SKILL_LIKE_KINDS
from marketplace.installer import RULE_TARGETS, TARGETS
from marketplace.manifest import MANIFEST_NAME, save_manifest
from marketplace.models import CatalogItem


def build_item_choices(catalog: list[CatalogItem], project_dir: Path) -> list[Choice | Separator]:
    """Build picker rows with catalog *indexes* as values.

    InquirerPy runs `dataclasses.asdict()` on every Choice, which deep-converts
    dataclass values into plain dicts — so values must never be CatalogItem itself.
    """
    description_width = _description_width()
    choices: list[Choice | Separator] = [Separator(f"  {_picker_header()}")]
    indexed_catalog = list(enumerate(catalog))
    for kind, section in KIND_SECTIONS:
        if not (kind_indexed := [(i, item) for i, item in indexed_catalog if item.kind == kind]):
            continue
        choices.append(Separator(display.SECTION_SEPARATOR_FMT.format(section=section)))
        choices.extend(
            Choice(value=index, name=_item_row(item, project_dir, description_width))
            for index, item in kind_indexed
        )
    return choices


def prompt_items(catalog: list[CatalogItem], project_dir: Path) -> list[CatalogItem]:
    selected_indexes = inquirer.checkbox(
        message=display.PROMPT_SELECT_ITEMS,
        choices=build_item_choices(catalog, project_dir),
        cycle=True,
        transformer=lambda result: display.SELECTED_COUNT_FMT.format(count=len(result)),
    ).execute()
    return [catalog[index] for index in selected_indexes]


def _target_choice_name(target_id: str) -> str:
    target = TARGETS[target_id]
    return display.TARGET_CHOICE_FMT.format(label=target.label, covers=", ".join(target.covers))


def _prompt_targets(detected: set[str]) -> list[str]:
    agents_detected = bool(detected - {AGENT_CLAUDE})
    choices = [
        Choice(
            value=AGENT_CLAUDE,
            name=_target_choice_name(AGENT_CLAUDE),
            enabled=AGENT_CLAUDE in detected or not detected,
        ),
        Choice(
            value=TARGET_AGENTS,
            name=_target_choice_name(TARGET_AGENTS),
            enabled=agents_detected or not detected,
        ),
    ]
    return inquirer.checkbox(
        message=display.PROMPT_SKILL_TARGETS, choices=choices, cycle=True
    ).execute()


def _prompt_rule_targets(detected: set[str]) -> list[str]:
    any_detected = bool(detected & set(RULE_TARGETS))
    choices = [
        Choice(
            value=target_id,
            name=display.TARGET_CHOICE_FMT.format(
                label=target.label, covers=", ".join(target.covers)
            ),
            enabled=target_id in detected or not any_detected,
        )
        for target_id, target in RULE_TARGETS.items()
    ]
    return inquirer.checkbox(
        message=display.PROMPT_RULE_TARGETS, choices=choices, cycle=True
    ).execute()


def prompt_all_targets(
    console: Console, selected: list[CatalogItem], detected: set[str]
) -> tuple[list[str], list[str]]:
    has_skills = any(item.kind in SKILL_LIKE_KINDS for item in selected)
    has_rules = any(item.kind == KIND_RULE for item in selected)
    skill_targets = _prompt_targets(detected) if has_skills else []
    rule_targets = _prompt_rule_targets(detected) if has_rules else []
    if has_skills and not skill_targets:
        console.print(display.MSG_NO_SKILL_TARGETS)
    if has_rules and not rule_targets:
        console.print(display.MSG_NO_RULE_TARGETS)
    return skill_targets, rule_targets


def confirm_install() -> bool:
    return inquirer.confirm(message=display.PROMPT_CONFIRM_INSTALL, default=True).execute()


def offer_manifest_save(console: Console, project_dir: Path, catalog: list[CatalogItem]) -> None:
    try:
        save = inquirer.confirm(
            message=display.PROMPT_SAVE_MANIFEST_FMT.format(manifest=MANIFEST_NAME),
            default=True,
        ).execute()
    except (KeyboardInterrupt, EOFError):
        return
    if not save:
        return
    per_target = collect_installed_state(catalog, project_dir)
    path = save_manifest(project_dir, per_target)
    console.print(display.MSG_MANIFEST_SAVED_FMT.format(name=path.name))
