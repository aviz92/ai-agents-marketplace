from __future__ import annotations

from pathlib import Path

from marketplace.detect.orchestrator import DETECTORS
from marketplace.installer.models import InstallResult, rule_targets
from marketplace.installer.rendering.templates import _get_template_env
from marketplace.installer.rendering.writer import _ensure_reference, _write_rendered
from marketplace.kind_catalog.models import CatalogItem


def install_rule(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = rule_targets()[target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    agent_cfg = DETECTORS.get(target_id)
    if agent_cfg is not None and agent_cfg.rule_reference is not None:
        _ensure_reference(
            project_dir, files_written, agent_cfg.rule_reference, rules_dir=target.dir
        )
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
