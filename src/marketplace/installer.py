"""Render catalog items and write them into a project's agent directories."""

from __future__ import annotations

import functools
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from marketplace.catalog import CatalogItem, get_marketplace_root
from marketplace.consts.agents import (
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_COPILOT,
    AGENT_CURSOR,
    AGENT_GEMINI,
    AGENT_NAMES,
    AGENTS_MD,
    CLAUDE_MD_PATH,
    GEMINI_MD,
    TARGET_AGENTS,
)
from marketplace.consts.authoring import AUTHORING_FILES, METADATA_FILE
from marketplace.consts.render import (
    AGENTS_SKILLS_DIR,
    CLAUDE_MD_FALLBACK,
    CLAUDE_SKILLS_DIR,
    COPILOT_INSTRUCTIONS_DIR,
    EXT_INSTRUCTIONS_MD,
    EXT_MD,
    EXT_MDC,
    RULE_FILENAME_FMT,
    RULE_REFERENCE_NOTE_FMT,
    RULE_TEMPLATE_FMT,
    RULES_DIR_FMT,
    SKILL_OUTPUT_FILE,
    SKILL_TEMPLATE,
    TEMPLATES_DIR_NAME,
)


@dataclass
class TargetInfo:
    """A universal skill/plugin install target (shared open-standard directory)."""

    dir: str
    covers: list[str]

    @property
    def label(self) -> str:
        return f"{self.dir}/"


@dataclass
class RuleTargetInfo:
    """A per-agent rule install target with its native filename and template."""

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
    """Outcome of one install operation against one target."""

    target: str
    installed: int
    files_written: list[str] = field(default_factory=list)
    output_dir: str = ""
    covers: list[str] = field(default_factory=list)


TARGETS: dict[str, TargetInfo] = {
    AGENT_CLAUDE: TargetInfo(
        dir=CLAUDE_SKILLS_DIR,
        covers=[AGENT_NAMES[AGENT_CLAUDE], AGENT_NAMES[AGENT_COPILOT]],
    ),
    TARGET_AGENTS: TargetInfo(
        dir=AGENTS_SKILLS_DIR,
        covers=[
            AGENT_NAMES[AGENT_CURSOR],
            AGENT_NAMES[AGENT_COPILOT],
            AGENT_NAMES[AGENT_CODEX],
            AGENT_NAMES[AGENT_GEMINI],
            "Windsurf",
            "Cline",
            "OpenCode",
            "OpenClaw",
            "Amp",
            "Letta Code",
            "Antigravity IDE",
        ],
    ),
}

RULE_TARGETS: dict[str, RuleTargetInfo] = {
    AGENT_CURSOR: RuleTargetInfo.for_agent(AGENT_CURSOR, EXT_MDC),
    AGENT_COPILOT: RuleTargetInfo.for_agent(
        AGENT_COPILOT, EXT_INSTRUCTIONS_MD, rules_dir=COPILOT_INSTRUCTIONS_DIR
    ),
    AGENT_CLAUDE: RuleTargetInfo.for_agent(AGENT_CLAUDE, EXT_MD),
    AGENT_CODEX: RuleTargetInfo.for_agent(AGENT_CODEX, EXT_MD),
    AGENT_GEMINI: RuleTargetInfo.for_agent(AGENT_GEMINI, EXT_MD),
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


_RULE_REFERENCES: dict[str, ReferenceSpec] = {
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


@functools.lru_cache(maxsize=1)
def _get_template_env() -> Environment:
    templates_dir = get_marketplace_root() / TEMPLATES_DIR_NAME
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _write_rendered(out_file: Path, content: str, project_dir: Path, written: list[str]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(content, encoding="utf-8")
    written.append(str(out_file.relative_to(project_dir)))


def _copy_assets(item: CatalogItem, out_dir: Path, project_dir: Path, written: list[str]) -> None:
    """Copy extra authored files (e.g. assets/) next to the rendered SKILL.md.

    Only authoring sources count as a real item dir; constructed items with a
    default path are skipped so we never scan the working directory.
    """
    if not (item.path / METADATA_FILE).is_file():
        return
    for source in sorted(item.path.rglob("*")):
        if source.is_dir() or source.name in AUTHORING_FILES:
            continue
        dest = out_dir / source.relative_to(item.path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        written.append(str(dest.relative_to(project_dir)))


def _ensure_reference(
    project_dir: Path, files_written: list[str], reference: ReferenceSpec, rules_dir: str
) -> None:
    """Append the reference note to the first existing candidate file, or create the fallback.

    Skips the append when the file already mentions `rules_dir`, so re-running
    an install never duplicates the reference.
    """
    note = RULE_REFERENCE_NOTE_FMT.format(rules_dir=rules_dir)
    for candidate in reference.candidates:
        path = project_dir / candidate
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if rules_dir in text:
            return
        separator = "" if text.endswith("\n") else "\n"
        path.write_text(f"{text}{separator}\n{note}\n", encoding="utf-8")
        files_written.append(candidate)
        return
    header = f"{reference.fallback_header}\n\n" if reference.fallback_header else ""
    fallback_file = project_dir / reference.fallback
    _write_rendered(fallback_file, f"{header}{note}\n", project_dir, files_written)


def install_to_target(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    """Render skills/plugins via the universal template into one shared target dir."""
    target = TARGETS[target_id]
    template = _get_template_env().get_template(SKILL_TEMPLATE)
    files_written: list[str] = []
    for item in items:
        out_dir = project_dir / target.dir / item.id
        skill_md = out_dir / SKILL_OUTPUT_FILE
        _write_rendered(skill_md, template.render(item=item), project_dir, files_written)
        _copy_assets(item, out_dir, project_dir, files_written)
    if target_id == AGENT_CLAUDE:
        claude_md = project_dir / CLAUDE_MD_PATH
        if not claude_md.exists():
            _write_rendered(claude_md, CLAUDE_MD_FALLBACK, project_dir, files_written)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )


def install_rules_to_target(
    rule_target_id: str, items: list[CatalogItem], project_dir: Path
) -> InstallResult:
    """Render rules into one agent's native format, plus its reference file if needed."""
    target = RULE_TARGETS[rule_target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    if (reference := _RULE_REFERENCES.get(rule_target_id)) is not None:
        _ensure_reference(project_dir, files_written, reference, rules_dir=target.dir)
    return InstallResult(
        target=rule_target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
