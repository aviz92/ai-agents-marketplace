from __future__ import annotations

from marketplace.consts.agents.agents import TARGET_AGENTS
from marketplace.consts.agents.claude import AGENT_CLAUDE
from marketplace.consts.agents.codex import AGENT_CODEX
from marketplace.consts.agents.copilot import (
    AGENT_COPILOT,
)
from marketplace.consts.agents.cursor import AGENT_CURSOR
from marketplace.consts.agents.gemini import AGENT_GEMINI

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

SOURCE_PROJECT = "project"
