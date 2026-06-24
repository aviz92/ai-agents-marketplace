"""Jinja2 template environment used to render catalog items."""

from __future__ import annotations

import functools

from jinja2 import Environment, FileSystemLoader

from marketplace.consts.render import TEMPLATES_DIR_NAME
from utils import get_marketplace_root


@functools.lru_cache(maxsize=1)
def _get_template_env() -> Environment:
    """Return the shared Jinja2 Environment, built once and cached for the process lifetime."""
    templates_dir = get_marketplace_root() / TEMPLATES_DIR_NAME
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def clear_template_env_cache() -> None:
    """Invalidate the cached Jinja2 Environment.

    Call this in tests that monkeypatch ``get_marketplace_root`` so the installer
    picks up the new root rather than reusing a stale Environment.
    """
    _get_template_env.cache_clear()
