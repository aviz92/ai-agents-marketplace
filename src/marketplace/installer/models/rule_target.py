from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
    AGENT_NAMES,
    COPILOT_INSTRUCTIONS_DIR,
    EXT_INSTRUCTIONS_MD,
    EXT_MDC,
)
from marketplace.consts.render import (
    RULE_FILENAME_FMT,
    RULE_TEMPLATE_FMT,
    RULES_DIR_FMT,
)


@dataclass
class RuleTargetInfo:
    dir: str
    filename_pattern: str
    template: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"

    @classmethod
    def for_agent(
        cls, agent_id: str, extension: str, rules_dir: str | None = None
    ) -> RuleTargetInfo:
        """Derive the target from minimal inputs — dir, filename, template, and covers
        all follow the same per-agent conventions; only exceptions are passed in."""
        target_dir = RULES_DIR_FMT.format(agent=agent_id) if rules_dir is None else rules_dir
        return cls(
            dir=target_dir,
            filename_pattern=RULE_FILENAME_FMT.format(extension=extension),
            template=RULE_TEMPLATE_FMT.format(agent=agent_id, extension=extension),
            covers=[AGENT_NAMES[agent_id]],
        )


@cache
def rule_targets() -> dict[str, RuleTargetInfo]:
    return {
        AGENT_CURSOR: RuleTargetInfo.for_agent(AGENT_CURSOR, EXT_MDC),
        AGENT_COPILOT: RuleTargetInfo.for_agent(
            AGENT_COPILOT, EXT_INSTRUCTIONS_MD, rules_dir=COPILOT_INSTRUCTIONS_DIR
        ),
        AGENT_CLAUDE: RuleTargetInfo.for_agent(AGENT_CLAUDE, "md"),
        AGENT_CODEX: RuleTargetInfo.for_agent(AGENT_CODEX, "md"),
        AGENT_GEMINI: RuleTargetInfo.for_agent(AGENT_GEMINI, "md"),
    }
