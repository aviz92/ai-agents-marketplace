"""Manifest loading and parsing logic."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.agents import (
    VALID_COMMAND_TARGET_IDS,
    VALID_RULE_TARGET_IDS,
    VALID_SKILL_TARGET_IDS,
)
from marketplace.consts.manifest import MANIFEST_NAME
from marketplace.kind_catalog.kinds import COMMAND, PLUGIN, RULE, SKILL
from marketplace.kind_catalog.registry import flat_kinds, per_agent_kinds
from marketplace.manifest.models import Manifest, ManifestError


def manifest_path(project_dir: Path) -> Path:
    return project_dir / MANIFEST_NAME


def _parse_kind(data: dict, key: str) -> list[str]:
    value = data.get(key) or []
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        raise ManifestError(f"'{key}' must be a list of strings")
    return value


def _validate_per_agent(per_agent: dict[str, dict[str, list[str]]]) -> None:
    skill_keys = {SKILL.dir_name, PLUGIN.dir_name}
    rule_key = RULE.dir_name
    command_key = COMMAND.dir_name
    for target_id, entry in per_agent.items():
        if skill_keys & set(entry) and target_id not in VALID_SKILL_TARGET_IDS:
            raise ManifestError(
                f"Target '{target_id}' does not support skills/plugins"
                f" — valid skill targets: {sorted(VALID_SKILL_TARGET_IDS)}"
            )
        if rule_key in entry and target_id not in VALID_RULE_TARGET_IDS:
            raise ManifestError(
                f"Target '{target_id}' does not support rules"
                f" — valid rule targets: {sorted(VALID_RULE_TARGET_IDS)}"
            )
        if command_key in entry and target_id not in VALID_COMMAND_TARGET_IDS:
            raise ManifestError(
                f"Target '{target_id}' does not support commands"
                f" — valid command targets: {sorted(VALID_COMMAND_TARGET_IDS)}"
            )


def _read_manifest_data(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{MANIFEST_NAME} must contain a YAML mapping")
    return data


def _parse_flat(data: dict) -> tuple[dict[str, list[str]], set[str]]:
    flat_keys = {cfg.dir_name for cfg in flat_kinds()}
    flat = {
        cfg.dir_name: _parse_kind(data, cfg.dir_name)
        for cfg in flat_kinds()
        if cfg.dir_name in data
    }
    return flat, flat_keys


def _parse_per_agent(data: dict, flat_keys: set[str]) -> dict[str, dict[str, list[str]]]:
    valid_targets = VALID_SKILL_TARGET_IDS | VALID_RULE_TARGET_IDS | VALID_COMMAND_TARGET_IDS
    per_agent: dict[str, dict[str, list[str]]] = {}
    for target_id, entry in data.items():
        if target_id in flat_keys:
            continue
        if target_id not in valid_targets:
            raise ManifestError(f"Unknown target '{target_id}' — valid: {sorted(valid_targets)}")
        if not isinstance(entry, dict):
            raise ManifestError(f"Entry for '{target_id}' must be a mapping")
        per_agent[target_id] = {
            cfg.dir_name: _parse_kind(entry, cfg.dir_name)
            for cfg in per_agent_kinds()
            if cfg.dir_name in entry
        }
    return per_agent


def load_manifest(project_dir: Path) -> Manifest | None:
    """Parse the project manifest; None when the file doesn't exist."""
    path = manifest_path(project_dir)
    if not path.is_file():
        return None
    data = _read_manifest_data(path)
    flat, flat_keys = _parse_flat(data)
    per_agent = _parse_per_agent(data, flat_keys)
    _validate_per_agent(per_agent)
    return Manifest(per_agent=per_agent, flat=flat)
