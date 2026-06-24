"""Shared cross-agent constants built from per-agent modules."""

from __future__ import annotations

from .agent_claude import AGENT_CLAUDE, CLAUDE_MD, CLAUDE_MD_PATH
from .agent_codex import AGENT_CODEX
from .agent_copilot import AGENT_COPILOT
from .agent_cursor import AGENT_CURSOR
from .agent_gemini import AGENT_GEMINI, GEMINI_MD

AGENT_NAMES: dict[str, str] = {
    AGENT_CLAUDE: "Claude Code",
    AGENT_CURSOR: "Cursor",
    AGENT_COPILOT: "GitHub Copilot",
    AGENT_CODEX: "Codex CLI",
    AGENT_GEMINI: "Gemini CLI",
}

TARGET_AGENTS = "agents"
AGENTS_MD = "AGENTS.md"
AGENTS_SKILLS_DIR = ".agents/skills"
RULES_DIR_FMT = ".{agent}/rules"

# Display names of all agents covered by the shared .agents/ target.
# Keep updated as new open-standard agents adopt the .agents/ layout.
AGENTS_TARGET_COVERS: list[str] = [
    AGENT_NAMES[AGENT_CURSOR],
    AGENT_NAMES[AGENT_COPILOT],
    AGENT_NAMES[AGENT_CODEX],
    AGENT_NAMES[AGENT_GEMINI],
]

# Valid target IDs for manifest validation — single source of truth consumed by
# manifest/loader.py so it doesn't need to import from the installer layer.
# Keep in sync with the TARGETS dict keys in installer.py.
VALID_SKILL_TARGET_IDS: frozenset[str] = frozenset({AGENT_CLAUDE, TARGET_AGENTS})
# Keep in sync with the RULE_TARGETS dict keys in installer.py.
VALID_RULE_TARGET_IDS: frozenset[str] = frozenset(
    {AGENT_CURSOR, AGENT_COPILOT, AGENT_CLAUDE, AGENT_CODEX, AGENT_GEMINI}
)

AGENT_PROJECT_SIGNALS: dict[str, list[str]] = {
    AGENT_CLAUDE: [CLAUDE_MD, ".claude"],
    AGENT_CURSOR: [".cursor", ".cursorrules"],
    AGENT_COPILOT: [
        ".github/skills",
        ".agents/skills",
        ".github/instructions",
        ".github/copilot-instructions.md",
        AGENTS_MD,
    ],
    AGENT_CODEX: [AGENTS_MD, ".codex"],
    AGENT_GEMINI: [GEMINI_MD, ".gemini"],
}

SOURCE_PROJECT = "project"
