"""Project manifest (agents-marketplace.yaml) — declarative installs for team sync.

A project commits this file to declare which artifacts every teammate should have;
`agents-marketplace sync` installs them non-interactively after a fresh clone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from marketplace.catalog import CatalogItem
from marketplace.consts.kinds import KIND_DIRS, KIND_PLUGIN, KIND_RULE, KIND_SKILL
from marketplace.consts.manifest import (
    MANIFEST_ALL,
    MANIFEST_HEADER,
    MANIFEST_KIND_KEYS,
    MANIFEST_NAME,
    MANIFEST_TARGETS_KEY,
)
from marketplace.installer import RULE_TARGETS, TARGETS


class ManifestError(ValueError):
    """Raised when the manifest file is malformed or references unknown targets."""


@dataclass
class Manifest:
    """Parsed contents of agents-marketplace.yaml.

    skills/plugins/rules of None means 'all items of that kind' (the YAML 'all' keyword).
    """

    skills: list[str] | None = field(default_factory=list)
    plugins: list[str] | None = field(default_factory=list)
    rules: list[str] | None = field(default_factory=list)
    skill_targets: list[str] = field(default_factory=list)
    rule_targets: list[str] = field(default_factory=list)


def manifest_path(project_dir: Path) -> Path:
    return project_dir / MANIFEST_NAME


def _parse_kind(data: dict, key: str) -> list[str] | None:
    if (value := data.get(key) or []) == MANIFEST_ALL:
        return None
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        raise ManifestError(f"'{key}' must be a list of artifact ids or the string 'all'")
    return value


def _validate_targets(manifest: Manifest) -> None:
    if unknown_skills := set(manifest.skill_targets) - set(TARGETS):
        raise ManifestError(
            f"Unknown skill targets {sorted(unknown_skills)} — valid: {sorted(TARGETS)}"
        )
    if unknown_rules := set(manifest.rule_targets) - set(RULE_TARGETS):
        raise ManifestError(
            f"Unknown rule targets {sorted(unknown_rules)} — valid: {sorted(RULE_TARGETS)}"
        )


def load_manifest(project_dir: Path) -> Manifest | None:
    """Parse the project manifest; None when the file doesn't exist."""
    path = manifest_path(project_dir)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{MANIFEST_NAME} must contain a YAML mapping")
    targets = data.get(MANIFEST_TARGETS_KEY) or {}
    manifest = Manifest(
        skills=_parse_kind(data, KIND_DIRS[KIND_SKILL]),
        plugins=_parse_kind(data, KIND_DIRS[KIND_PLUGIN]),
        rules=_parse_kind(data, KIND_DIRS[KIND_RULE]),
        skill_targets=list(targets.get(KIND_DIRS[KIND_SKILL]) or []),
        rule_targets=list(targets.get(KIND_DIRS[KIND_RULE]) or []),
    )
    _validate_targets(manifest)
    return manifest


def resolve_items(
    manifest: Manifest, catalog: list[CatalogItem]
) -> tuple[list[CatalogItem], list[str]]:
    """Match manifest entries against the catalog → (items to install, missing refs)."""
    selected: list[CatalogItem] = []
    missing: list[str] = []
    for kind, key in MANIFEST_KIND_KEYS:
        wanted = getattr(manifest, key)
        kind_items = {item.id: item for item in catalog if item.kind == kind}
        if wanted is None:
            selected.extend(kind_items.values())
            continue
        for item_id in wanted:
            if item_id in kind_items:
                selected.append(kind_items[item_id])
            else:
                missing.append(f"{kind}:{item_id}")
    return selected, missing


def save_manifest(
    project_dir: Path,
    items: list[CatalogItem],
    skill_targets: list[str],
    rule_targets: list[str],
) -> Path:
    """Write the manifest describing `items` and the chosen targets."""
    data: dict = {
        key: sorted(item.id for item in items if item.kind == kind)
        for kind, key in MANIFEST_KIND_KEYS
    }
    targets: dict = {}
    if skill_targets:
        targets[KIND_DIRS[KIND_SKILL]] = skill_targets
    if rule_targets:
        targets[KIND_DIRS[KIND_RULE]] = rule_targets
    if targets:
        data[MANIFEST_TARGETS_KEY] = targets
    path = manifest_path(project_dir)
    path.write_text(MANIFEST_HEADER + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
