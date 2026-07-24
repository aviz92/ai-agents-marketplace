"""Validate authored artifacts on disk without silently skipping broken ones.

`loader.load_catalog()` intentionally skips malformed items so a broken artifact
never crashes install flows. This module re-walks the same directories and
reports every issue it finds instead, for use by the `validate` CLI command.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from marketplace.consts.authoring import METADATA_FILE
from marketplace.kind_catalog.kinds import RULE, KindConfig
from marketplace.kind_catalog.models import KIND_CLASSES
from marketplace.kind_catalog.registry import all_kinds

Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class ValidationIssue:
    kind: str
    item_id: str
    path: Path
    severity: Severity
    message: str


def _issue(cfg: KindConfig, item_dir: Path, severity: Severity, message: str) -> ValidationIssue:
    return ValidationIssue(
        kind=cfg.kind_name, item_id=item_dir.name, path=item_dir, severity=severity, message=message
    )


def _read_metadata(item_dir: Path, cfg: KindConfig) -> tuple[dict, ValidationIssue | None]:
    metadata_file = item_dir / METADATA_FILE
    if not metadata_file.is_file():
        return {}, _issue(cfg, item_dir, "error", f"missing {METADATA_FILE}")
    try:
        metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as exc:
        return {}, _issue(cfg, item_dir, "error", f"invalid {METADATA_FILE}: {exc}")
    if not isinstance(metadata, dict):
        return {}, _issue(cfg, item_dir, "error", f"{METADATA_FILE} must be a mapping")
    return metadata, None


def _read_body(item_dir: Path, cfg: KindConfig) -> tuple[str, ValidationIssue | None]:
    if not cfg.body_filename:
        return "", None
    body_file = item_dir / cfg.body_filename
    if not body_file.is_file():
        return "", _issue(cfg, item_dir, "error", f"missing {cfg.body_filename}")
    try:
        return body_file.read_text(encoding="utf-8").strip() + "\n", None
    except OSError as exc:
        return "", _issue(cfg, item_dir, "error", f"cannot read {cfg.body_filename}: {exc}")


def _check_field_warnings(metadata: dict, cfg: KindConfig, item_dir: Path) -> list[ValidationIssue]:
    warnings: list[ValidationIssue] = []
    if not str(metadata.get("name", "")).strip():
        warnings.append(
            _issue(cfg, item_dir, "warning", "missing 'name' — falls back to directory name")
        )
    if not str(metadata.get("description", "")).strip():
        warnings.append(_issue(cfg, item_dir, "warning", "missing or empty 'description'"))
    if not str(metadata.get("author", "")).strip():
        warnings.append(
            _issue(cfg, item_dir, "warning", "missing 'author' — falls back to 'unknown'")
        )
    if not str(metadata.get("version", "")).strip():
        warnings.append(
            _issue(cfg, item_dir, "warning", "missing 'version' — falls back to '1.0.0'")
        )
    if (
        cfg.kind_name == RULE.kind_name
        and not metadata.get("globs")
        and not metadata.get("alwaysApply")
    ):
        warnings.append(
            _issue(
                cfg,
                item_dir,
                "warning",
                "no 'globs' and alwaysApply is false — rule will never activate on Cursor",
            )
        )
    return warnings


def _validate_item(item_dir: Path, cfg: KindConfig) -> list[ValidationIssue]:
    metadata, metadata_issue = _read_metadata(item_dir, cfg)
    if metadata_issue is not None:
        return [metadata_issue]

    content, body_issue = _read_body(item_dir, cfg)
    if body_issue is not None:
        return [body_issue]

    try:
        KIND_CLASSES[cfg.kind_name].from_metadata(item_dir.name, metadata, content, item_dir)
    except (ValueError, TypeError) as exc:
        return [_issue(cfg, item_dir, "error", str(exc))]

    return _check_field_warnings(metadata, cfg, item_dir)


def _validate_kind(root: Path, cfg: KindConfig) -> list[ValidationIssue]:
    kind_dir = root / cfg.dir_name
    if not kind_dir.is_dir():
        return []
    issues: list[ValidationIssue] = []
    for item_dir in sorted(kind_dir.iterdir()):
        if item_dir.is_dir():
            issues.extend(_validate_item(item_dir, cfg))
    return issues


def validate_catalog(root: Path) -> list[ValidationIssue]:
    """Check every authored artifact under `root`, surfacing issues the loader would skip."""
    issues: list[ValidationIssue] = []
    for cfg in all_kinds():
        issues.extend(_validate_kind(root, cfg))
    return issues
