from __future__ import annotations

from marketplace.consts.agents import AGENT_GEMINI, GEMINI_DIR, GEMINI_MD
from marketplace.detect.base import AgentConfig

GEMINI_CONFIG = AgentConfig(
    id=AGENT_GEMINI,
    signals=[GEMINI_MD, GEMINI_DIR],
    instructions_candidates=[GEMINI_MD, f".{AGENT_GEMINI}/{GEMINI_MD}"],
    instructions_fallback_header="# Gemini Instructions",
)
