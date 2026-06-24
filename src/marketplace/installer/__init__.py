"""Render catalog items and write them into a project's agent directories."""

from __future__ import annotations

from .install import RULE_TARGET_GROUPS, SKILLS_TARGET_GROUPS, install_to_target
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
    "RULE_TARGET_GROUPS",
    "RULE_TARGETS",
    "SKILLS_TARGET_GROUPS",
    "TARGETS",
    "InstallResult",
    "ReferenceSpec",
    "RuleTargetInfo",
    "TargetInfo",
    "clear_template_env_cache",
    "install_to_target",
]
