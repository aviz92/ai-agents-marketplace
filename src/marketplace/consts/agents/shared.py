from __future__ import annotations

from marketplace.consts.agents.agents import AGENTS_MD, AGENTS_SKILLS_DIR, TARGET_AGENTS
from marketplace.consts.agents.claude import AGENT_CLAUDE, CLAUDE_DIR, CLAUDE_MD
from marketplace.consts.agents.codex import AGENT_CODEX, CODEX_DIR
from marketplace.consts.agents.copilot import (
    AGENT_COPILOT,
    COPILOT_INSTRUCTIONS_DIR,
    COPILOT_INSTRUCTIONS_MD,
    COPILOT_SKILLS_DIR,
)
from marketplace.consts.agents.cursor import AGENT_CURSOR, CURSOR_DIR, CURSOR_RULES_FILE
from marketplace.consts.agents.gemini import AGENT_GEMINI, GEMINI_DIR, GEMINI_MD

VALID_RULE_TARGET_IDS: frozenset[str] = frozenset(
    {AGENT_CURSOR, AGENT_COPILOT, AGENT_CLAUDE, AGENT_CODEX, AGENT_GEMINI}
)
VALID_SKILL_TARGET_IDS: frozenset[str] = frozenset({AGENT_CLAUDE, TARGET_AGENTS})

AGENT_NAMES: dict[str, str] = {
    AGENT_CLAUDE: "Claude Code",
    AGENT_CURSOR: "Cursor",
    AGENT_COPILOT: "GitHub Copilot",
    AGENT_CODEX: "Codex CLI",
    AGENT_GEMINI: "Gemini CLI",
}

AGENTS_TARGET_COVERS: list[str] = [
    AGENT_NAMES[AGENT_CURSOR],
    AGENT_NAMES[AGENT_COPILOT],
    AGENT_NAMES[AGENT_CODEX],
    AGENT_NAMES[AGENT_GEMINI],
]

AGENT_PROJECT_SIGNALS: dict[str, list[str]] = {
    AGENT_CLAUDE: [CLAUDE_MD, CLAUDE_DIR],
    AGENT_CURSOR: [CURSOR_DIR, CURSOR_RULES_FILE],
    AGENT_COPILOT: [
        COPILOT_SKILLS_DIR,
        AGENTS_SKILLS_DIR,
        COPILOT_INSTRUCTIONS_DIR,
        COPILOT_INSTRUCTIONS_MD,
        AGENTS_MD,
    ],
    AGENT_CODEX: [AGENTS_MD, CODEX_DIR],
    AGENT_GEMINI: [GEMINI_MD, GEMINI_DIR],
}

SOURCE_PROJECT = "project"
