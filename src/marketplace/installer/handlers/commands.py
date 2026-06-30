from __future__ import annotations

from pathlib import Path

from marketplace.installer.models import InstallResult, command_targets
from marketplace.installer.rendering.templates import _get_template_env
from marketplace.installer.rendering.writer import _write_rendered
from marketplace.kind_catalog.models import CatalogItem


def install_command(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = command_targets()[target_id]
    template = _get_template_env().get_template(target.template)
    files_written: list[str] = []
    for item in items:
        out_file = project_dir / target.dir / target.filename_pattern.format(id=item.id)
        _write_rendered(out_file, template.render(item=item), project_dir, files_written)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
