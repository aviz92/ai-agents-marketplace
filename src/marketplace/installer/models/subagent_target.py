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
    COPILOT_AGENTS_DIR,
)
from marketplace.consts.render import (
    SUBAGENT_FILENAME_FMT,
    SUBAGENT_TEMPLATE_FMT,
    SUBAGENTS_DIR_FMT,
)


@dataclass
class SubagentTargetInfo:
    dir: str
    filename_pattern: str
    template: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"

    @classmethod
    def for_agent(cls, agent_id: str) -> SubagentTargetInfo:
        return cls(
            dir=SUBAGENTS_DIR_FMT.format(agent=agent_id),
            filename_pattern=SUBAGENT_FILENAME_FMT,
            template=SUBAGENT_TEMPLATE_FMT.format(agent=agent_id),
            covers=[AGENT_NAMES[agent_id]],
        )


@cache
def subagent_targets() -> dict[str, SubagentTargetInfo]:
    return {
        AGENT_CLAUDE: SubagentTargetInfo.for_agent(AGENT_CLAUDE),
        AGENT_CURSOR: SubagentTargetInfo.for_agent(AGENT_CURSOR),
        AGENT_GEMINI: SubagentTargetInfo.for_agent(AGENT_GEMINI),
        AGENT_CODEX: SubagentTargetInfo.for_agent(AGENT_CODEX),
        AGENT_COPILOT: SubagentTargetInfo(
            dir=COPILOT_AGENTS_DIR,
            filename_pattern=SUBAGENT_FILENAME_FMT,
            template=SUBAGENT_TEMPLATE_FMT.format(agent=AGENT_COPILOT),
            covers=[AGENT_NAMES[AGENT_COPILOT]],
        ),
    }
