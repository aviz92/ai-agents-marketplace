from __future__ import annotations

from enum import Enum

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
)


class ModelStrength(str, Enum):
    STRONG = "strong"
    REGULAR = "regular"
    WEAK = "weak"


class ModelStrengthError(ValueError):
    pass


AGENT_MODEL_STRENGTHS: dict[str, dict[ModelStrength, str]] = {
    AGENT_CLAUDE: {
        ModelStrength.STRONG: "opus",
        ModelStrength.REGULAR: "sonnet",
        ModelStrength.WEAK: "haiku",
    },
    AGENT_CURSOR: {
        ModelStrength.STRONG: "claude-opus-4.5",
        ModelStrength.REGULAR: "claude-sonnet-4.5",
        ModelStrength.WEAK: "claude-haiku-4.5",
    },
    AGENT_COPILOT: {
        ModelStrength.STRONG: "gpt-5",
        ModelStrength.REGULAR: "gpt-4.1",
        ModelStrength.WEAK: "o4-mini",
    },
    AGENT_GEMINI: {
        ModelStrength.STRONG: "gemini-3-pro",
        ModelStrength.REGULAR: "gemini-3-flash",
        ModelStrength.WEAK: "gemini-3-flash-lite",
    },
    AGENT_CODEX: {
        ModelStrength.STRONG: "gpt-5.1-codex-max",
        ModelStrength.REGULAR: "gpt-5.1-codex",
        ModelStrength.WEAK: "gpt-5.1-codex-mini",
    },
}


def resolve_model(agent_id: str, strength: ModelStrength) -> str:
    if agent_id not in AGENT_MODEL_STRENGTHS:
        raise ModelStrengthError(
            f"No model-strength mapping for agent '{agent_id}'"
            f" — known agents: {sorted(AGENT_MODEL_STRENGTHS)}"
        )
    strengths = AGENT_MODEL_STRENGTHS[agent_id]
    if strength not in strengths:
        raise ModelStrengthError(
            f"Agent '{agent_id}' has no model mapped for strength '{strength}'"
            f" — known strengths: {sorted(s.value for s in strengths)}"
        )
    return strengths[strength]
