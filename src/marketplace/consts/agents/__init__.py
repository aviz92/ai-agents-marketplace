"""Agent constants — re-exported from per-agent modules."""

from __future__ import annotations

from .agent_claude import AGENT_CLAUDE, CLAUDE_MD, CLAUDE_MD_PATH, CLAUDE_SKILLS_DIR
from .agent_codex import AGENT_CODEX
from .agent_copilot import AGENT_COPILOT, COPILOT_INSTRUCTIONS_DIR, EXT_INSTRUCTIONS_MD
from .agent_cursor import AGENT_CURSOR, EXT_MDC
from .agent_gemini import AGENT_GEMINI, GEMINI_MD
from .shared import (
    AGENT_NAMES,
    AGENT_PROJECT_SIGNALS,
    AGENTS_MD,
    AGENTS_SKILLS_DIR,
    AGENTS_TARGET_COVERS,
    RULES_DIR_FMT,
    SOURCE_PROJECT,
    TARGET_AGENTS,
    VALID_RULE_TARGET_IDS,
    VALID_SKILL_TARGET_IDS,
)

__all__ = [
    "AGENT_CLAUDE",
    "AGENT_CODEX",
    "AGENT_COPILOT",
    "AGENT_CURSOR",
    "AGENT_GEMINI",
    "AGENT_NAMES",
    "AGENT_PROJECT_SIGNALS",
    "AGENTS_MD",
    "AGENTS_SKILLS_DIR",
    "AGENTS_TARGET_COVERS",
    "CLAUDE_MD",
    "CLAUDE_MD_PATH",
    "CLAUDE_SKILLS_DIR",
    "COPILOT_INSTRUCTIONS_DIR",
    "EXT_INSTRUCTIONS_MD",
    "EXT_MDC",
    "GEMINI_MD",
    "RULES_DIR_FMT",
    "SOURCE_PROJECT",
    "TARGET_AGENTS",
    "VALID_RULE_TARGET_IDS",
    "VALID_SKILL_TARGET_IDS",
]
