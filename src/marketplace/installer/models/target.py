from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_COPILOT,
    AGENT_NAMES,
    AGENTS_SKILLS_DIR,
    AGENTS_TARGET_COVERS,
    CLAUDE_SKILLS_DIR,
    TARGET_AGENTS,
)


@dataclass
class TargetInfo:
    dir: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"


@cache
def targets() -> dict[str, TargetInfo]:
    return {
        AGENT_CLAUDE: TargetInfo(
            dir=CLAUDE_SKILLS_DIR, covers=[AGENT_NAMES[AGENT_CLAUDE], AGENT_NAMES[AGENT_COPILOT]]
        ),
        TARGET_AGENTS: TargetInfo(dir=AGENTS_SKILLS_DIR, covers=AGENTS_TARGET_COVERS),
    }
