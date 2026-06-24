"""Install-target data models and the registries that drive all rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache

from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
    AGENT_NAMES,
    AGENTS_MD,
    AGENTS_SKILLS_DIR,
    AGENTS_TARGET_COVERS,
    CLAUDE_MD_PATH,
    CLAUDE_SKILLS_DIR,
    COPILOT_INSTRUCTIONS_DIR,
    EXT_INSTRUCTIONS_MD,
    EXT_MDC,
    GEMINI_MD,
    TARGET_AGENTS,
)
from marketplace.consts.render import (
    RULE_FILENAME_FMT,
    RULE_TEMPLATE_FMT,
    RULES_DIR_FMT,
)


@dataclass
class TargetInfo:
    dir: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"


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


@dataclass
class InstallResult:
    target: str
    installed: int
    files_written: list[str] = field(default_factory=list)
    output_dir: str = ""
    covers: list[str] = field(default_factory=list)


@cache
def targets() -> dict[str, TargetInfo]:
    return {
        AGENT_CLAUDE: TargetInfo(
            dir=CLAUDE_SKILLS_DIR,
            covers=[AGENT_NAMES[AGENT_CLAUDE], AGENT_NAMES[AGENT_COPILOT]],
        ),
        TARGET_AGENTS: TargetInfo(
            dir=AGENTS_SKILLS_DIR,
            covers=AGENTS_TARGET_COVERS,
        ),
    }


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
