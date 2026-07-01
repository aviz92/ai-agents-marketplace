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

![agents-marketplace demo](assets/agents-marketplace-readme.gif)


## 📖 How to Use

### Prerequisites

- Python ≥ 3.12
- [`uv`](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A project directory where you write code with AI tools (Claude Code, Cursor, Copilot, etc.)

---

### Step 1 — Fork the repository on GitHub

Go to `https://github.com/aviz92/ai-agents-marketplace` and click **Fork**.

> You now have your own copy at `https://github.com/<your-username>/ai-agents-marketplace`. This is your personal catalog — add your own skills, rules, and plugins here.

---

### Step 2 — Clone your fork locally

```bash
git clone https://github.com/<your-username>/ai-agents-marketplace
cd ai-agents-marketplace
```

---

### Step 3 — Browse available artifacts

```bash
ls skills/
ls rules/
ls plugins/
```

---

### Step 4 — Inspect an artifact

```bash
cat skills/create-skill/metadata.yaml
cat skills/create-skill/skill.md
```

> `metadata.yaml` shows `name`, `description`, `version`, and `tags`. `skill.md` contains the markdown instructions installed into your AI tool.

---

### Step 5 — Navigate to the project you want to enhance

```bash
cd /path/to/your-project
```

---

### Step 6 — Run the interactive installer

```bash
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace generate
```

Or run from a local checkout while building your catalog:

```bash
uvx --from /path/to/ai-agents-marketplace agents-marketplace generate
```

> A terminal TUI launches showing all available artifacts with checkboxes. Already-installed items are marked. Items with newer versions show an "update available" badge.

---

### Step 7 — Select artifacts

Use arrow keys + `Space` to check/uncheck, `Enter` to confirm.

---

### Step 8 — Choose install targets

Review pre-checked targets (based on auto-detection) and adjust if needed.

---

### Step 9 — Confirm installation

> Files are written, for example:
> ```
> .claude/skills/create-skill/SKILL.md
> .claude/rules/no-debug-code.md
> .cursor/rules/no-debug-code.mdc
> .github/instructions/no-debug-code.instructions.md
> ```

---

### Step 10 — Save selection

When prompted "Save installed state to `agents-marketplace.yaml`?", answer **yes** and commit the file so teammates get the same setup with one command.

---

### Step 11 — Team sync

Commit `agents-marketplace.yaml` to your project root and every teammate gets the same setup after cloning:

```bash
# Install only agents you choose (prompted)
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync

# Install all agents in the manifest without prompting (CI-friendly)
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --all

# Overwrite already-installed artifacts with the latest version
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --force

# CI-friendly: install all agents and overwrite existing artifacts, no prompting
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --all --force
```

```yaml
# agents-marketplace.yaml
claude:
  skills: [python-code-review, pre-push-checklist]
  rules: [no-debug-code]
agents:
  skills: [python-code-review]
cursor:
  rules: [no-debug-code]
copilot:
  rules: [no-debug-code]
```

- Valid skill/plugin targets: `claude`, `agents`
- Valid rule targets: `claude`, `cursor`, `copilot`, `codex`, `gemini`
- Every list must be explicit artifact IDs — no wildcards.
- Unknown IDs are reported and skipped; sync exits non-zero so CI can catch drift.

To keep every clone's artifacts current automatically, wire `sync --all --force` into `.pre-commit-config.yaml` as a local hook:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: agents-marketplace-sync
        name: Sync agents-marketplace artifacts
        entry: uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --all --force
        language: system
        pass_filenames: false
        files: ^agents-marketplace\.yaml$
```

`--all` skips the interactive prompt and `--force` overwrites artifacts already on disk, so the hook always installs exactly what `agents-marketplace.yaml` declares whenever that file changes.

The easiest way to create this file: run `generate` once and answer **yes** to "Save installed state?" — the manifest snapshots everything currently installed (all targets), so re-saving never drops previously installed artifacts.

---

### Step 12 — Add your own artifact

**Skill**

```bash
cd /path/to/ai-agents-marketplace
mkdir -p skills/my-new-skill
```

```yaml
# skills/my-new-skill/metadata.yaml
name: My New Skill
description: One-line description shown in the picker
tags: [custom]
author: your-name
version: 1.0.0
```

```markdown
<!-- skills/my-new-skill/skill.md -->
# My New Skill

Instructions for the AI agent go here...
```

Installed as `<target>/<skill-id>/SKILL.md` in every selected skill target. A skill may also bundle extra files (e.g. `assets/template.md`) next to `skill.md`; they are copied as-is, preserving relative paths.

**Rule**

```bash
mkdir -p rules/my-new-rule
```

```yaml
# rules/my-new-rule/metadata.yaml
name: Human Readable Name
description: One-line description
tags: [optional]
author: your-name
version: 1.0.0
globs: ["src/**/*.py"]   # Cursor `globs` / Copilot `applyTo`
alwaysApply: true        # Cursor: rule is always active
```

One authored rule produces per-target files: `.cursor/rules/<id>.mdc`, `.github/instructions/<id>.instructions.md`, `.claude/rules/<id>.md`, `.codex/rules/<id>.md`, `.gemini/rules/<id>.md`.

**Plugin**

Identical to a skill, but under `plugins/<plugin-id>/` with the body in `plugin.md`.

Push to your fork, then run `generate` in any target project — the new artifact appears in the picker:

```bash
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace generate
```

---

## Available Commands

```bash
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace --help
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace generate
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace generate --help
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace generate --version
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --all
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --help
uvx --from git+https://github.com/<your-username>/ai-agents-marketplace agents-marketplace sync --version
```


## What gets installed

| Artifact type | Target dir | Written file | Agents covered |
|---|---|---|---|
| Skill / Plugin | `.claude/skills/` | `<id>/SKILL.md` | Claude Code, GitHub Copilot |
| Skill / Plugin | `.agents/skills/` | `<id>/SKILL.md` | Cursor, GitHub Copilot, Codex CLI, Gemini CLI |
| Rule | `.claude/rules/` | `<id>.md` | Claude Code |
| Rule | `.cursor/rules/` | `<id>.mdc` | Cursor |
| Rule | `.github/instructions/` | `<id>.instructions.md` | GitHub Copilot |
| Rule | `.codex/rules/` | `<id>.md` | Codex CLI |
| Rule | `.gemini/rules/` | `<id>.md` | Gemini CLI |
