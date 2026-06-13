"""Authoring-format constants — on-disk layout for catalog items."""

from __future__ import annotations

from marketplace.consts.kinds import BODY_FILES

METADATA_FILE = "metadata.yaml"
AUTHORING_FILES = frozenset({METADATA_FILE, *BODY_FILES.values()})
DEFAULT_AUTHOR = "unknown"
DEFAULT_VERSION = "1.0.0"
