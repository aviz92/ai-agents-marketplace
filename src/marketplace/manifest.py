"""Project manifest (agents-marketplace.yaml) — declarative installs for team sync.

A project commits this file to declare which artifacts each agent target should have;
`agents-marketplace sync` installs them non-interactively after a fresh clone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from marketplace.consts.kinds import KIND_DIRS, KIND_PLUGIN, KIND_RULE, KIND_SKILL
from marketplace.consts.manifest import (
    MANIFEST_HEADER,
    MANIFEST_KIND_KEYS,
    MANIFEST_NAME,
)
from marketplace.installer import RULE_TARGETS, TARGETS
from marketplace.models import CatalogItem


class ManifestError(ValueError):
    """Raised when the manifest file is malformed or references unknown targets."""


@dataclass
class Manifest:
    """Parsed contents of agents-marketplace.yaml.

    per_agent maps each target_id to a dict of kind_key -> explicit artifact IDs.
    Example: {"claude": {"skills": ["a"], "rules": ["b"]}, "cursor": {"rules": ["b"]}}
    """

    per_agent: dict[str, dict[str, list[str]]] = field(default_factory=dict)


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
        if skill_keys & set(entry) and target_id not in TARGETS:
            raise ManifestError(
                f"Target '{target_id}' does not support skills/plugins"
                f" — valid skill targets: {sorted(TARGETS)}"
            )
        if rule_key in entry and target_id not in RULE_TARGETS:
            raise ManifestError(
                f"Target '{target_id}' does not support rules"
                f" — valid rule targets: {sorted(RULE_TARGETS)}"
            )


def load_manifest(project_dir: Path) -> Manifest | None:
    """Parse the project manifest; None when the file doesn't exist."""
    path = manifest_path(project_dir)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{MANIFEST_NAME} must contain a YAML mapping")
    valid_targets = set(TARGETS) | set(RULE_TARGETS)
    per_agent: dict[str, dict[str, list[str]]] = {}
    for target_id, entry in data.items():
        if target_id not in valid_targets:
            raise ManifestError(f"Unknown target '{target_id}' — valid: {sorted(valid_targets)}")
        if not isinstance(entry, dict):
            raise ManifestError(f"Entry for '{target_id}' must be a mapping")
        per_agent[target_id] = {
            key: _parse_kind(entry, key) for _, key in MANIFEST_KIND_KEYS if key in entry
        }
    _validate_per_agent(per_agent)
    return Manifest(per_agent=per_agent)


def resolve_per_agent(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[dict[str, list[CatalogItem]], list[str]]:
    """Resolve per-target artifact IDs against the catalog.

    Returns (per_target_items, missing_refs).
    """
    kind_index: dict[str, dict[str, CatalogItem]] = {
        kind: {item.id: item for item in catalog if item.kind == kind}
        for kind, _ in MANIFEST_KIND_KEYS
    }
    per_target: dict[str, list[CatalogItem]] = {}
    missing: list[str] = []
    for target_id, entry in manifest.per_agent.items():
        items: list[CatalogItem] = []
        for kind, key in MANIFEST_KIND_KEYS:
            if key not in entry:
                continue
            kind_items = kind_index[kind]
            for item_id in entry[key]:
                if item_id in kind_items:
                    items.append(kind_items[item_id])
                else:
                    missing.append(f"{kind}:{item_id}")
        per_target[target_id] = items
    return per_target, missing


def save_manifest(
    project_dir: Path,
    per_target: dict[str, list[CatalogItem]],
) -> Path:
    """Write the manifest describing what is installed per target."""
    data: dict = {}
    for target_id, items in per_target.items():
        entry: dict = {
            key: sorted(item.id for item in items if item.kind == kind)
            for kind, key in MANIFEST_KIND_KEYS
            if any(item.kind == kind for item in items)
        }
        if entry:
            data[target_id] = entry
    path = manifest_path(project_dir)
    path.write_text(MANIFEST_HEADER + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
