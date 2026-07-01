from __future__ import annotations

from pathlib import Path

from marketplace.installer.models import InstallResult, targets
from marketplace.installer.rendering.templates import _get_template_env
from marketplace.installer.rendering.writer import _copy_assets, _ensure_claude_md, _write_rendered
from marketplace.kind_catalog.models import CatalogItem


def install_plugin(
    target_id: str, items: list[CatalogItem], project_dir: Path, force: bool = True
) -> InstallResult:
    target = targets()[target_id]
    env = _get_template_env()
    files_written: list[str] = []
    files_skipped: list[str] = []
    installed = 0
    for item in items:
        cfg = item.config
        if cfg.output_file is None or cfg.template is None:
            raise ValueError(f"Plugin kind '{item.kind}' missing output_file or template")
        out_dir = project_dir / target.dir / item.id
        out_file = out_dir / cfg.output_file
        if not force and out_file.exists():
            files_skipped.append(str(out_file.relative_to(project_dir)))
            continue
        _write_rendered(out_file, env.get_template(cfg.template).render(item=item), project_dir, files_written)
        _copy_assets(item, out_dir, project_dir, files_written)
        installed += 1
    _ensure_claude_md(target_id, project_dir, files_written)
    return InstallResult(
        target=target_id,
        installed=installed,
        files_written=files_written,
        files_skipped=files_skipped,
        output_dir=target.dir,
        covers=target.covers,
    )
