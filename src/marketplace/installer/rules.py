from __future__ import annotations

from pathlib import Path

from marketplace.kind_catalog.models import CatalogItem

from marketplace.installer.models import InstallResult, _rule_references, rule_targets
from marketplace.installer.templates import _get_template_env
from marketplace.installer.writer import _ensure_reference, _write_rendered


def install_rule(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = rule_targets()[target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    if (reference := _rule_references().get(target_id)) is not None:
        _ensure_reference(project_dir, files_written, reference, rules_dir=target.dir)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
