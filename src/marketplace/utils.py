"""General-purpose utilities for the marketplace package."""

from __future__ import annotations

from pathlib import Path

from marketplace.consts.kinds import KIND_DIRS, KIND_PLUGIN, KIND_SKILL


def get_marketplace_root() -> Path:
    """Resolve the directory holding skills/, plugins/, rules/ and templates/.

    Dual-mode: prefer the source repo layout (content dirs next to src/);
    otherwise assume an installed wheel where content was force-included
    next to the package itself.
    """
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent.parent
    skills_dir = repo_root / KIND_DIRS[KIND_SKILL]
    plugins_dir = repo_root / KIND_DIRS[KIND_PLUGIN]
    if skills_dir.is_dir() or plugins_dir.is_dir():
        return repo_root
    return package_dir
