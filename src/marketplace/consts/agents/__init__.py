from __future__ import annotations

from marketplace.consts.agents.agents import AGENTS_MD, AGENTS_SKILLS_DIR, TARGET_AGENTS
from marketplace.consts.agents.claude import (
    AGENT_CLAUDE,
    CLAUDE_COMMANDS_DIR,
    CLAUDE_DIR,
    CLAUDE_MD,
    CLAUDE_MD_PATH,
    CLAUDE_SKILLS_DIR,
)
from marketplace.consts.agents.codex import AGENT_CODEX, CODEX_DIR
from marketplace.consts.agents.copilot import (
    AGENT_COPILOT,
    COPILOT_INSTRUCTIONS_DIR,
    COPILOT_INSTRUCTIONS_MD,
    COPILOT_PROMPTS_DIR,
    COPILOT_SKILLS_DIR,
    EXT_INSTRUCTIONS_MD,
)
from marketplace.consts.agents.cursor import (
    AGENT_CURSOR,
    CURSOR_COMMANDS_DIR,
    CURSOR_DIR,
    CURSOR_RULES_FILE,
    EXT_MDC,
)
from marketplace.consts.agents.gemini import (
    AGENT_GEMINI,
    GEMINI_COMMANDS_DIR,
    GEMINI_DIR,
    GEMINI_MD,
)
from marketplace.consts.agents.shared import (
    AGENT_NAMES,
    AGENTS_TARGET_COVERS,
    SOURCE_PROJECT,
    VALID_COMMAND_TARGET_IDS,
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
    "AGENTS_MD",
    "AGENTS_SKILLS_DIR",
    "AGENTS_TARGET_COVERS",
    "CLAUDE_COMMANDS_DIR",
    "CLAUDE_DIR",
    "CLAUDE_MD",
    "CLAUDE_MD_PATH",
    "CLAUDE_SKILLS_DIR",
    "CODEX_DIR",
    "COPILOT_INSTRUCTIONS_DIR",
    "COPILOT_INSTRUCTIONS_MD",
    "COPILOT_PROMPTS_DIR",
    "COPILOT_SKILLS_DIR",
    "CURSOR_COMMANDS_DIR",
    "CURSOR_DIR",
    "CURSOR_RULES_FILE",
    "EXT_INSTRUCTIONS_MD",
    "EXT_MDC",
    "GEMINI_COMMANDS_DIR",
    "GEMINI_DIR",
    "GEMINI_MD",
    "SOURCE_PROJECT",
    "TARGET_AGENTS",
    "VALID_COMMAND_TARGET_IDS",
    "VALID_RULE_TARGET_IDS",
    "VALID_SKILL_TARGET_IDS",
]
