"""Write rendered output to disk: render files, copy assets, inject references."""

from __future__ import annotations

import shutil
from pathlib import Path

from marketplace.consts.agents import AGENT_CLAUDE, CLAUDE_MD_PATH
from marketplace.consts.authoring import AUTHORING_FILES, METADATA_FILE
from marketplace.consts.render import CLAUDE_MD_FALLBACK, RULE_REFERENCE_NOTE_FMT
from marketplace.kind_catalog.models import CatalogItem

from .models import ReferenceSpec


def _ensure_claude_md(target_id: str, project_dir: Path, files_written: list[str]) -> None:
    if target_id == AGENT_CLAUDE:
        claude_md = project_dir / CLAUDE_MD_PATH
        if not claude_md.exists():
            _write_rendered(claude_md, CLAUDE_MD_FALLBACK, project_dir, files_written)


def _write_rendered(out_file: Path, content: str, project_dir: Path, written: list[str]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(content, encoding="utf-8")
    written.append(str(out_file.relative_to(project_dir)))


def _copy_assets(item: CatalogItem, out_dir: Path, project_dir: Path, written: list[str]) -> None:
    """Copy extra authored files (e.g. assets/) next to the rendered output file.

    Only authoring sources count as a real item dir; constructed items with a
    None path are skipped so we never scan the working directory.
    """
    if item.path is None or not (item.path / METADATA_FILE).is_file():
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

    Skips to append when the file already mentions `rules_dir`, so re-running
    an installation never duplicates the reference.
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
