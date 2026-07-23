"""Tests for marketplace.consts.models — model-strength resolution per agent."""

import pytest

from marketplace.consts.models import ModelStrength, ModelStrengthError, resolve_model


class TestResolveModel:
    @pytest.mark.parametrize(
        ("agent_id", "strength", "expected"),
        [
            ("claude", ModelStrength.STRONG, "opus"),
            ("claude", ModelStrength.REGULAR, "sonnet"),
            ("claude", ModelStrength.WEAK, "haiku"),
            ("cursor", ModelStrength.STRONG, "claude-opus-4.5"),
            ("copilot", ModelStrength.REGULAR, "gpt-4.1"),
            ("gemini", ModelStrength.WEAK, "gemini-3-flash-lite"),
            ("codex", ModelStrength.STRONG, "gpt-5.1-codex-max"),
        ],
        ids=[
            "claude-strong",
            "claude-regular",
            "claude-weak",
            "cursor-strong",
            "copilot-regular",
            "gemini-weak",
            "codex-strong",
        ],
    )
    def test_resolve_model_returns_expected_model_id(
        self, agent_id: str, strength: ModelStrength, expected: str
    ) -> None:
        assert (
            resolve_model(agent_id, strength) == expected
        ), f"{agent_id}/{strength}: expected {expected}"

    def test_resolve_model_unknown_agent_raises_model_strength_error(self) -> None:
        with pytest.raises(ModelStrengthError, match="No model-strength mapping"):
            resolve_model("vim", ModelStrength.STRONG)
