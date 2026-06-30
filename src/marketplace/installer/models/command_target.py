from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
    AGENT_NAMES,
    COPILOT_PROMPTS_DIR,
    CURSOR_COMMANDS_DIR,
)
from marketplace.consts.render import COMMAND_FILENAME_FMT, COMMAND_TEMPLATE_FMT, COMMANDS_DIR_FMT

COPILOT_COMMAND_FILENAME_FMT = "{id}.prompt.md"


@dataclass
class CommandTargetInfo:
    dir: str
    filename_pattern: str
    template: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"

    @classmethod
    def for_agent(cls, agent_id: str) -> CommandTargetInfo:
        return cls(
            dir=COMMANDS_DIR_FMT.format(agent=agent_id),
            filename_pattern=COMMAND_FILENAME_FMT,
            template=COMMAND_TEMPLATE_FMT.format(agent=agent_id),
            covers=[AGENT_NAMES[agent_id]],
        )


@cache
def command_targets() -> dict[str, CommandTargetInfo]:
    return {
        AGENT_CLAUDE: CommandTargetInfo.for_agent(AGENT_CLAUDE),
        AGENT_GEMINI: CommandTargetInfo.for_agent(AGENT_GEMINI),
        AGENT_CURSOR: CommandTargetInfo(
            dir=CURSOR_COMMANDS_DIR,
            filename_pattern=COMMAND_FILENAME_FMT,
            template=COMMAND_TEMPLATE_FMT.format(agent=AGENT_CURSOR),
            covers=[AGENT_NAMES[AGENT_CURSOR]],
        ),
        AGENT_COPILOT: CommandTargetInfo(
            dir=COPILOT_PROMPTS_DIR,
            filename_pattern=COPILOT_COMMAND_FILENAME_FMT,
            template=COMMAND_TEMPLATE_FMT.format(agent=AGENT_COPILOT),
            covers=[AGENT_NAMES[AGENT_COPILOT]],
        ),
    }
