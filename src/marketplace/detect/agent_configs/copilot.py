from __future__ import annotations

from marketplace.consts.agents import (
    AGENT_COPILOT,
    AGENTS_MD,
    AGENTS_SKILLS_DIR,
    COPILOT_INSTRUCTIONS_DIR,
    COPILOT_INSTRUCTIONS_MD,
    COPILOT_SKILLS_DIR,
)
from marketplace.detect.base import AgentConfig

COPILOT_CONFIG = AgentConfig(
    id=AGENT_COPILOT,
    signals=[
        COPILOT_SKILLS_DIR,
        AGENTS_SKILLS_DIR,
        COPILOT_INSTRUCTIONS_DIR,
        COPILOT_INSTRUCTIONS_MD,
        AGENTS_MD,
    ],
)
