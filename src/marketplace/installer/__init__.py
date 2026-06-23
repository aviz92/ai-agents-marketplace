"""Render catalog items and write them into a project's agent directories.

Public API is re-exported here so callers keep using `marketplace.installer`
unchanged; the package is split into layers internally (models, templates,
writer, install).
"""

from __future__ import annotations

from .install import install_rules_to_target, install_skills_to_target, split_install_kinds
from .models import (
    RULE_TARGETS,
    TARGETS,
    InstallResult,
    ReferenceSpec,
    RuleTargetInfo,
    TargetInfo,
)
from .templates import clear_template_env_cache

__all__ = [
    "RULE_TARGETS",
    "TARGETS",
    "InstallResult",
    "ReferenceSpec",
    "RuleTargetInfo",
    "TargetInfo",
    "clear_template_env_cache",
    "install_rules_to_target",
    "install_skills_to_target",
    "split_install_kinds",
]
