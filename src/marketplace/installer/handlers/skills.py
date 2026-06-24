from __future__ import annotations

from pathlib import Path

from marketplace.kind_catalog.models import CatalogItem

from marketplace.installer.models import InstallResult, targets
from marketplace.installer.rendering.templates import _get_template_env
from marketplace.installer.rendering.writer import _copy_assets, _ensure_claude_md, _write_rendered


def install_skill(target_id: str, items: list[CatalogItem], project_dir: Path) -> InstallResult:
    target = targets()[target_id]
    env = _get_template_env()
    files_written: list[str] = []
    for item in items:
        cfg = item.config
        if cfg.output_file is None or cfg.template is None:
            raise ValueError(f"Skill kind '{item.kind}' missing output_file or template")
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
