# Agents Marketplace

An interactive CLI (`agents-marketplace`) that distributes reusable AI-agent context —
**skills** 🧠, **plugins** 🔌, and **rules** 📏 — into any project, rendering each artifact
into the **native format** every supported AI coding agent expects.

- **Skills & plugins** are universal: authored once, installed into shared open-standard
  directories (`.claude/skills/`, `.agents/skills/`) that many agents already read.
- **Rules** are agent-specific: each agent has its own rules format, frontmatter, and
  location — so one authored rule is rendered into up to **5 native formats** at install
  time. *Author once, render many.*


## 🎬 Demo

![agents-marketplace demo](assets/agents-marketplace-presentation.gif)


## Quick start

### 1. Fork this repo

Your fork is your catalog. Click **Fork** on GitHub, then clone it:

```bash
git clone https://github.com/<you>/ai-agents-marketplace
cd ai-agents-marketplace
```

### 2. Add your skills, rules, and plugins

Drop your content into the catalog directories — see [Adding a skill](#adding-a-skill),
[Adding a rule](#adding-a-rule), and [Adding a plugin](#adding-a-plugin) below for the
exact file layout. Push when ready.

### 3. Install into any project

Run the interactive picker from the root of any project, pointing at your fork:

```bash
uvx --from git+https://github.com/<you>/ai-agents-marketplace agents-marketplace install
```

The `install` TUI walks you through:

1. Pick artifacts from the catalog (shows installed status and available updates).
2. Review which AI tools were detected in your project / on your system.
3. Pick install targets (pre-checked based on detection).
4. Confirm — files are rendered and written into your project.
5. Optionally save your selection to `agents-marketplace.yaml` for team sync (see below).

Or run from a local checkout while you're building your catalog:

```bash
uvx --from /path/to/ai-agents-marketplace agents-marketplace install
```

Available commands:

```
agents-marketplace --help              # list commands
agents-marketplace install             # interactive TUI
agents-marketplace install --help      # install command options
agents-marketplace install --version   # print version
agents-marketplace sync                # non-interactive team sync
agents-marketplace sync --help         # sync command options
```


## Team sync

Commit an `agents-marketplace.yaml` to your project root (like VS Code's
`.vscode/extensions.json`) and every teammate gets the same setup after cloning —
no install required:

```bash
uvx --from git+https://github.com/<you>/ai-agents-marketplace agents-marketplace sync
```

(If the tool is already installed via `uv tool install`, plain `agents-marketplace sync` works too.)

Run `agents-marketplace sync --help` to see all options.

```yaml
# agents-marketplace.yaml
skills:
  - python-code-review
  - pre-push-checklist
rules: all                # 'all' installs every rule in the catalog
plugins: []
targets:                  # optional — defaults to detected agents
  skills: [claude, agents]
  rules: [cursor, claude]
```

- `skills` / `rules` / `plugins` — list of artifact ids, or the string `all`.
- `targets` — optional; when omitted, sync installs to the agents it detects
  (and falls back to `.agents/skills` + all rule formats when nothing is detected).
- Unknown ids are reported and skipped; sync still installs the rest but exits non-zero
  so CI can catch drift.

The easiest way to create the file: run `agents-marketplace install` once and answer **yes**
to "Save installed state to agents-marketplace.yaml?" at the end. The saved manifest
is a **snapshot of everything currently installed in the project** (all targets, not
just the latest selection), so re-saving never drops previously installed artifacts.


## What gets installed

| Target dir | Format | Written file | Agents covered |
|---|---|---|---|
| `.claude/skills/` | Universal skill | `<id>/SKILL.md` | Claude Code, GitHub Copilot |
| `.agents/skills/` | Universal skill | `<id>/SKILL.md` | Cursor, GitHub Copilot, Codex CLI, Gemini CLI, Windsurf, Cline, OpenCode, OpenClaw, Amp, Letta Code, Antigravity IDE |
| `.cursor/rules/` | Cursor MDC (`globs`, `alwaysApply`) | `<id>.mdc` | Cursor |
| `.github/instructions/` | Copilot instructions (`applyTo`) | `<id>.instructions.md` | GitHub Copilot |
| `.claude/rules/` | Markdown + frontmatter | `<id>.md` | Claude Code |
| `.codex/rules/` | Markdown + frontmatter | `<id>.md` | Codex CLI |
| `.gemini/rules/` | Markdown + frontmatter | `<id>.md` | Gemini CLI |


## Adding a skill

Create `skills/<skill-id>/` with two files:

```yaml
# skills/<skill-id>/metadata.yaml
name: Human Readable Name
description: One-line description shown in the picker
tags: [optional, tags]
author: your-name
version: 1.0.0
```

```markdown
<!-- skills/<skill-id>/skill.md -->
# What this skill does
Platform-agnostic markdown instructions...
```

Installed as `<target>/<skill-id>/SKILL.md` in every selected skill target.

A skill may also bundle extra files (e.g. `assets/template.md`) next to its
`skill.md`; they are copied as-is alongside the rendered `SKILL.md`, preserving
relative paths — so links like `[template.md](assets/template.md)` keep working
after install.


## Adding a rule

Create `rules/<rule-id>/` with `metadata.yaml` + `rule.md`. Rules support two extra
metadata keys used by the per-agent renderers:

```yaml
# rules/<rule-id>/metadata.yaml
name: Human Readable Name
description: One-line description
tags: [optional]
author: your-name
version: 1.0.0
globs: ["src/**/*.py"]   # Cursor `globs` / Copilot `applyTo`
alwaysApply: true        # Cursor: rule is always active
```

One authored rule produces these files (per selected target):

- `.cursor/rules/<rule-id>.mdc`
- `.github/instructions/<rule-id>.instructions.md`
- `.claude/rules/<rule-id>.md`
- `.codex/rules/<rule-id>.md`
- `.gemini/rules/<rule-id>.md`


## Adding a plugin

Identical to a skill, but under `plugins/<plugin-id>/` with the body in `plugin.md`.
