from __future__ import annotations

from marketplace.consts.agents import AGENT_CURSOR, CURSOR_DIR, CURSOR_RULES_FILE
from marketplace.detect.base import AgentConfig

CURSOR_CONFIG = AgentConfig(
    id=AGENT_CURSOR,
    signals=[CURSOR_DIR, CURSOR_RULES_FILE],
)
