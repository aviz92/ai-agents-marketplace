from __future__ import annotations

from pathlib import Path

from marketplace.detect.orchestrator import DETECTORS
from marketplace.installer.models import InstallResult, rule_targets
from marketplace.installer.models.reference import ReferenceSpec
from marketplace.installer.rendering.templates import _get_template_env
from marketplace.installer.rendering.writer import _ensure_reference, _write_rendered
from marketplace.kind_catalog.models import CatalogItem


def install_rule(
    target_id: str, items: list[CatalogItem], project_dir: Path, force: bool = True
) -> InstallResult:
    target = rule_targets()[target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    files_skipped: list[str] = []
    installed = 0
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        if not force and out_file.exists():
            files_skipped.append(str(out_file.relative_to(project_dir)))
            continue
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
        installed += 1
    agent_cfg = DETECTORS.get(target_id)
    if agent_cfg is not None and agent_cfg.instructions_candidates:
        reference = ReferenceSpec(
            candidates=agent_cfg.instructions_candidates,
            fallback=agent_cfg.instructions_candidates[0],
            fallback_header=agent_cfg.instructions_fallback_header,
        )
        _ensure_reference(project_dir, files_written, reference, rules_dir=target.dir)
    return InstallResult(
        target=target_id,
        installed=installed,
        files_written=files_written,
        files_skipped=files_skipped,
        output_dir=target.dir,
        covers=target.covers,
    )
