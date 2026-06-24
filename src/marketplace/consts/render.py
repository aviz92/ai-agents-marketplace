"""Rendering and installation path constants."""

from __future__ import annotations

import re

TEMPLATES_DIR_NAME = "templates"
SKILL_TEMPLATE = "skill.md.j2"
SKILL_OUTPUT_FILE = "SKILL.md"
PLUGIN_TEMPLATE = "plugin.md.j2"
PLUGIN_OUTPUT_FILE = "PLUGIN.md"
CLAUDE_MD_FALLBACK = "Refer to ../AGENTS.md\n"

RULE_FILENAME_FMT = "{{id}}.{extension}"
RULE_TEMPLATE_FMT = "rule.{agent}.{extension}.j2"
RULE_REFERENCE_NOTE_FMT = "Project rules live in `{rules_dir}/` — read and follow every file there."

VERSION_RE = re.compile(r"^version:\s*(\S+)", re.MULTILINE)
