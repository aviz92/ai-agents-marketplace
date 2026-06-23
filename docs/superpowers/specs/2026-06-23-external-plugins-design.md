# External Plugins — Design Spec

Date: 2026-06-23

## Context

The marketplace today serves three internal catalog kinds — `skill`, `plugin`,
`rule` — each stored as a folder with `metadata.yaml` plus a body Markdown file,
rendered through Jinja templates and written into a project's agent directories.

There is no way to list a **third-party tool that lives in its own repo and ships
its own installer**. Example: Caveman Mode, installed via
`curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash`.

This spec adds an **external-plugins** catalog: a new, fourth kind whose entries
are pure pointers (source URL + install command + metadata), not rendered
content. The marketplace **displays** an external plugin's install command and
source; it **never executes** the command.

### Why show-only, never execute

Auto-running an external `install` command means executing arbitrary remote shell
(`curl … | bash`) from third-party repos on the user's machine on every sync — a
supply-chain / RCE risk where one compromised entry runs code on every user. The
design therefore stores and renders the command for the user to run deliberately.
No code path in this feature executes it.

## Decisions

| Topic | Decision |
|-------|----------|
| Execution | Show install command + source; never run. Zero auto-execution. |
| Storage | New catalog dir `external-plugins/<id>/metadata.yaml`, metadata-only (no body file). |
| Kind | `KIND_EXTERNAL_PLUGIN = "external-plugin"`. Not in `SKILL_LIKE_KINDS`. |
| Manifest | Flat top-level `external-plugins: [<id>, ...]` list, not nested per-agent (external plugins are agent-agnostic). |
| Install side effects | None. External plugins never write into `.claude/`, `.agents/`, etc. Display-only. |

## Metadata schema

`external-plugins/<id>/metadata.yaml`:

```yaml
name: Caveman Mode
description: Ultra-compressed communication mode for AI agents. Cuts ~75% of tokens while keeping full technical accuracy by speaking like a caveman. Supports intensity levels — lite, full (default), ultra, and wenyan variants.
source: https://github.com/JuliusBrussee/caveman
install: "curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash"
author: JuliusBrussee
version: 1.0.1
tags: [productivity, token-efficiency, communication]
```

Fields: existing `name`, `description`, `author`, `version`, `tags` (shared with
other kinds) plus two new required fields **`source`** (repo/landing URL) and
**`install`** (shell command string, stored verbatim, never executed).

## Components

### 1. Kind constants — `src/marketplace/consts/kinds.py`
- Add `KIND_EXTERNAL_PLUGIN = "external-plugin"`.
- `KIND_DIRS[KIND_EXTERNAL_PLUGIN] = "external-plugins"`.
- `KIND_ICONS[KIND_EXTERNAL_PLUGIN] = "🌐"`.
- **No** `BODY_FILES` entry → marks this kind as metadata-only.
- Leave `SKILL_LIKE_KINDS` unchanged (external plugins are not skill-like).

### 2. Model — `src/marketplace/models.py`
- New `ExternalPlugin(CatalogItem)` with extra fields `source: str` and
  `install: str`; `content` defaults to `""` (unused).
- Override `from_metadata` to map `source` and `install` from the YAML mapping
  (mirrors how `Rule` maps `globs`/`alwaysApply`).
- Register `KIND_CLASSES[KIND_EXTERNAL_PLUGIN] = ExternalPlugin`.

### 3. Catalog loader — `src/marketplace/catalog.py`
- `_load_item` currently requires the kind's body file to exist. Change: when a
  kind has **no** entry in `BODY_FILES`, load it metadata-only — read
  `metadata.yaml`, pass `content=""`, skip the body read/existence check.
- Kinds with a body file keep the existing required-body behavior unchanged.

### 4. Manifest — flat global list
- `src/marketplace/manifest/models.py`: add `external: list[str] = field(default_factory=list)`
  to `Manifest`.
- `src/marketplace/manifest/loader.py`: parse a top-level `external-plugins:` key
  (sibling of agent blocks) as a `list[str]` of ids; validate ids resolve in the
  catalog; reject non-list values with the existing `ManifestError` pattern.
- `src/marketplace/manifest/resolver.py`: resolve the `external` ids to
  `ExternalPlugin` catalog items; report unknown ids the same way other missing
  refs are reported.
- `src/marketplace/manifest/writer.py`: emit the flat `external-plugins:` list;
  omit when empty (consistent with empty-target omission).
- `src/marketplace/consts/manifest.py`: add the `external-plugins` top-level key
  constant.

### 5. Sync display — show, never run
- `src/marketplace/cli/render.py`: new `print_external_plugins(console, items)` —
  one panel per external plugin showing name, version, `source` URL, and the
  `install` command in a copyable code block.
- `src/marketplace/cli/sync/flow.py` (`run_sync`): after `print_results`, if the
  manifest declared external plugins, resolve them and call
  `print_external_plugins`. No install/write/execute path.

### 6. Seed entry
- `external-plugins/caveman/metadata.yaml` populated from the example above.

## Data flow

```
agents-marketplace.yaml
  external-plugins: [caveman]        (flat, top-level)
        │  load_manifest → Manifest.external = ["caveman"]
        ▼
  resolve_per_agent / external resolver → [ExternalPlugin(caveman)]
        │  (loaded from external-plugins/caveman/metadata.yaml, content="")
        ▼
  render.print_external_plugins → panel: name, version, source, install cmd
        (display only — no disk write, no shell execution)
```

## Error handling
- Missing `source`/`install` in metadata → handled by `from_metadata`; surfaced as
  a load warning (existing `catalog.py` warn-and-skip path) — entry skipped, sync
  continues.
- Unknown id in `external-plugins:` manifest list → reported as a missing
  reference, sync exits non-zero like other missing refs.
- Non-list `external-plugins:` value → `ManifestError`, consistent with existing
  manifest validation.

## Testing
- **Model:** `ExternalPlugin.from_metadata` parses `source` + `install`; `content`
  is `""`; kind is `external-plugin`.
- **Loader:** a metadata-only `external-plugins/<id>/` dir loads without a body
  file; a body-file kind still fails when its body is missing (no regression).
- **Manifest:** flat `external-plugins:` list round-trips through load → write →
  load; unknown id reported missing; non-list raises `ManifestError`; empty list
  omitted on write.
- **Render:** `print_external_plugins` output contains the install command and
  source; assert no code path invokes a shell (display-only).

## Out of scope (YAGNI)
- Running, sandboxing, or verifying install commands.
- Per-agent targeting of external plugins.
- Versioning/update detection of the external tool itself.
- Interactive selection UI beyond listing (can come later if needed).
