# Create a marketplace skill

Author a new reusable skill for the AI marketplace. Skills are platform-agnostic
markdown instructions distributed to every supported AI coding agent.

## Structure

Every skill is a directory under `skills/`:

```
skills/<skill-id>/
├── metadata.yaml
├── skill.md
└── assets/          # optional — extra files the skill references
```

The directory name is the skill's id — kebab-case, short, descriptive.

Extra files under the skill directory (e.g. `assets/template.md`) are copied
as-is next to the rendered `SKILL.md` at install time, preserving relative
paths — so links like `[template.md](assets/template.md)` keep working.

## metadata.yaml

```yaml
name: Human Readable Name
description: One-line description shown in the marketplace picker
tags: [optional, tags]
author: your-name
version: 1.0.0
```

- `description` must be a single line — it appears in the interactive picker.
- `version` is semver. **Bump it on any change** to the skill's content or
  metadata — version changes are how installed copies detect updates.

## skill.md

Plain markdown, platform-agnostic:

- Do not reference a specific AI tool (Claude, Cursor, Copilot) — the same body
  is rendered for all of them.
- Start with a `#` heading naming the task the skill performs.
- Prefer imperative, checklist-style instructions over prose.
- Include concrete commands and code snippets where they remove ambiguity.
- Keep it focused: one skill = one job. Split unrelated workflows into
  separate skills.

## Checklist before publishing

- [ ] Directory name is kebab-case and matches the skill's purpose
- [ ] `metadata.yaml` has name, description, author, version
- [ ] `skill.md` is platform-agnostic markdown
- [ ] `version` bumped if this is a change to an existing skill
