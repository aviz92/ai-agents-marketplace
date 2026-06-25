from __future__ import annotations

from marketplace.consts.agents import AGENT_CODEX, AGENTS_MD, CODEX_DIR
from marketplace.detect.base import AgentConfig

CODEX_CONFIG = AgentConfig(
    id=AGENT_CODEX,
    signals=[AGENTS_MD, CODEX_DIR],
    instructions_candidates=[AGENTS_MD, f".{AGENT_CODEX}/{AGENTS_MD}"],
    instructions_fallback_header="# Agent Instructions",
)
