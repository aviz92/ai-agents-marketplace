from __future__ import annotations

from marketplace.consts.agents import AGENT_CLAUDE, AGENTS_MD, CLAUDE_DIR, CLAUDE_MD, CLAUDE_MD_PATH
from marketplace.detect.base import AgentConfig, ReferenceSpec

CLAUDE_CONFIG = AgentConfig(
    id=AGENT_CLAUDE,
    signals=[CLAUDE_MD, CLAUDE_DIR],
    rule_reference=ReferenceSpec(
        candidates=[CLAUDE_MD_PATH, AGENTS_MD],
        fallback=CLAUDE_MD_PATH,
    ),
)
