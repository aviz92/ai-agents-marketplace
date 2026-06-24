"""Manifest loading and parsing logic."""

from __future__ import annotations

from pathlib import Path

import yaml

from marketplace.consts.agents import VALID_RULE_TARGET_IDS, VALID_SKILL_TARGET_IDS
from marketplace.consts.kinds import KIND_DIRS, KIND_PLUGIN, KIND_RULE, KIND_SKILL
from marketplace.consts.manifest import MANIFEST_EXTERNAL_KEY, MANIFEST_KIND_KEYS, MANIFEST_NAME
from marketplace.manifest.models import Manifest, ManifestError


def manifest_path(project_dir: Path) -> Path:
    return project_dir / MANIFEST_NAME


def _parse_kind(data: dict, key: str) -> list[str]:
    value = data.get(key) or []
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        raise ManifestError(f"'{key}' must be a list of strings")
    return value


def _validate_per_agent(per_agent: dict[str, dict[str, list[str]]]) -> None:
    skill_keys = {KIND_DIRS[KIND_SKILL], KIND_DIRS[KIND_PLUGIN]}
    rule_key = KIND_DIRS[KIND_RULE]
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


def load_manifest(project_dir: Path) -> Manifest | None:
    """Parse the project manifest; None when the file doesn't exist."""
    path = manifest_path(project_dir)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{MANIFEST_NAME} must contain a YAML mapping")
    external = _parse_kind(data, MANIFEST_EXTERNAL_KEY) if MANIFEST_EXTERNAL_KEY in data else []
    valid_targets = VALID_SKILL_TARGET_IDS | VALID_RULE_TARGET_IDS
    per_agent: dict[str, dict[str, list[str]]] = {}
    for target_id, entry in data.items():
        if target_id == MANIFEST_EXTERNAL_KEY:
            continue
        if target_id not in valid_targets:
            raise ManifestError(f"Unknown target '{target_id}' — valid: {sorted(valid_targets)}")
        if not isinstance(entry, dict):
            raise ManifestError(f"Entry for '{target_id}' must be a mapping")
        per_agent[target_id] = {
            key: _parse_kind(entry, key) for _, key in MANIFEST_KIND_KEYS if key in entry
        }
    _validate_per_agent(per_agent)
    return Manifest(per_agent=per_agent, external=external)
