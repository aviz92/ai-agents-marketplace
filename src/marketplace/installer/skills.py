from __future__ import annotations

from pathlib import Path

from marketplace.kind_catalog.models import CatalogItem

from .models import InstallResult, targets
from .templates import _get_template_env
from .writer import _copy_assets, _ensure_claude_md, _write_rendered


def install_skill(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = targets()[target_id]
    env = _get_template_env()
    files_written: list[str] = []
    for item in items:
        cfg = item.config
        out_dir = project_dir / target.dir / item.id
        _write_rendered(
            out_dir / cfg.output_file,
            env.get_template(cfg.template).render(item=item),
            project_dir,
            files_written,
        )
        _copy_assets(item, out_dir, project_dir, files_written)
    _ensure_claude_md(target_id, project_dir, files_written)
    return InstallResult(
        target=target_id,
        installed=len(items),
        files_written=files_written,
        output_dir=target.dir,
        covers=target.covers,
    )
