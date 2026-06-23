"""Agent identifiers, display names, and detection signals."""

from __future__ import annotations

# ── Agent identifiers ────────────────────────────────────────────────────────
AGENT_CLAUDE = "claude"
AGENT_CURSOR = "cursor"
AGENT_COPILOT = "copilot"
AGENT_CODEX = "codex"
AGENT_GEMINI = "gemini"

AGENT_NAMES: dict[str, str] = {
    AGENT_CLAUDE: "Claude Code",
    AGENT_CURSOR: "Cursor",
    AGENT_COPILOT: "GitHub Copilot",
    AGENT_CODEX: "Codex CLI",
    AGENT_GEMINI: "Gemini CLI",
}

# The shared .agents/ skill dir serves many agents — not itself an agent id.
TARGET_AGENTS = "agents"

# Display names of all agents covered by the shared .agents/ target.
# Keep this list updated as new open-standard agents adopt the .agents/ layout.
AGENTS_TARGET_COVERS: list[str] = [
    AGENT_NAMES[AGENT_CURSOR],
    AGENT_NAMES[AGENT_COPILOT],
    AGENT_NAMES[AGENT_CODEX],
    AGENT_NAMES[AGENT_GEMINI],
]

# Valid target IDs for manifest validation — single source of truth consumed by
# manifest/loader.py so it doesn't need to import from the installer layer.
VALID_SKILL_TARGET_IDS: frozenset[str] = frozenset({AGENT_CLAUDE, TARGET_AGENTS})
VALID_RULE_TARGET_IDS: frozenset[str] = frozenset(
    {AGENT_CURSOR, AGENT_COPILOT, AGENT_CLAUDE, AGENT_CODEX, AGENT_GEMINI}
)

# ── Well-known instruction files ─────────────────────────────────────────────
AGENTS_MD = "AGENTS.md"
CLAUDE_MD = "CLAUDE.md"
GEMINI_MD = "GEMINI.md"
CLAUDE_MD_PATH = ".claude/CLAUDE.md"

# ── Project-level detection signals ─────────────────────────────────────────
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
