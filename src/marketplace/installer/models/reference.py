from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_GEMINI,
    AGENTS_MD,
    CLAUDE_MD_PATH,
    GEMINI_MD,
)


@dataclass
class ReferenceSpec:
    """How to point an agent's top-level instructions file at an installed rules dir.

    The note text itself is derived from the rules dir (RULE_REFERENCE_NOTE_FMT);
    only the file locations and an optional fallback heading vary per agent.
    """

    candidates: list[str]
    fallback: str
    fallback_header: str = ""


@cache
def _rule_references() -> dict[str, ReferenceSpec]:
    return {
        AGENT_CLAUDE: ReferenceSpec(
            candidates=[CLAUDE_MD_PATH, AGENTS_MD],
            fallback=CLAUDE_MD_PATH,
        ),
        AGENT_CODEX: ReferenceSpec(
            candidates=[AGENTS_MD, f".{AGENT_CODEX}/{AGENTS_MD}"],
            fallback=AGENTS_MD,
            fallback_header="# Agent Instructions",
        ),
        AGENT_GEMINI: ReferenceSpec(
            candidates=[GEMINI_MD, f".{AGENT_GEMINI}/{GEMINI_MD}"],
            fallback=GEMINI_MD,
            fallback_header="# Gemini Instructions",
        ),
    }
