from __future__ import annotations

from marketplace.kind_catalog.registry import ALL_KINDS

METADATA_FILE = "metadata.yaml"
AUTHORING_FILES = frozenset({METADATA_FILE, *(cfg.body_filename for cfg in ALL_KINDS if cfg.body_filename)})
DEFAULT_AUTHOR = "unknown"
DEFAULT_VERSION = "1.0.0"
