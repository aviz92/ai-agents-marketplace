from __future__ import annotations

from marketplace.consts.agents import AGENT_CODEX, AGENTS_MD, CODEX_DIR
from marketplace.detect.base import AgentConfig, ReferenceSpec

CODEX_CONFIG = AgentConfig(
    id=AGENT_CODEX,
    signals=[AGENTS_MD, CODEX_DIR],
    rule_reference=ReferenceSpec(
        candidates=[AGENTS_MD, f".{AGENT_CODEX}/{AGENTS_MD}"],
        fallback=AGENTS_MD,
        fallback_header="# Agent Instructions",
    ),
)
