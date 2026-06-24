# Agent Instructions

## Versioning
Every time an artifact's content or metadata changes (anything under `skills/`,
`plugins/`, or `rules/`), bump the `version` field in its `metadata.yaml`.
This is how the CLI detects that an update is available.

## Git
Never commit or push without explicit human approval.

---

# Avi Zaguri — Workspace Rules

Senior Python developer. Be direct, concise, no fluff.

## Rule Precedence
*NEVER* print the changes made to a file in the response. Always summarize the changes instead.
Project-local `CLAUDE.md` or `AGENTS.md` in the repo overrides this file. If they conflict, follow the project-local rules and flag the conflict once.

## Plan Mode Response Format
- In plan mode, respond in **100 words or less**
- Use **numbered steps only**
- No explanations, no commentary, no context

## Libraries (check first)
I maintain an open-source Python ecosystem under `github.com/aviz92/`. **Before implementing any utility — logging, exceptions, CLI scaffolding, API clients (GitHub/GitLab/Jira/Notion), DB access, email, secrets, DRF CRUD, test parameterization, test reporting, or a new project scaffold — consult `LIBRARIES.md` first.** Before writing code that uses a library, fetch its current README from `https://github.com/aviz92/<library_name>`. Do not rely on memory for API shape.

## Behavior
- Act autonomously on small-to-medium tasks: bug fixes, single-file changes, adding tests, refactoring within one module, dependency bumps, doc edits.
- Ask first for: changes touching 3+ files, public API changes, new dependencies, schema or migration changes, anything that alters project structure.
- Proactively flag tech debt, performance, and security issues.

## Environment
- Package manager: `uv` exclusively — never pip
- Python: >=3.12

## Security
- Never read/write .env, secrets/, credentials, token files
- Never commit API keys or passwords
- Always use parameterized queries

## Git
- Conventional Commits (feat:, fix:, refactor:, test:, chore:, docs:)
- Branches: feature/, fix/, chore/ prefixes
- Pre-commit must pass before committing

## Code Quality Rules
- After writing or modifying any file, ALWAYS run `pre-commit run --all-files` and fix all issues before considering the task complete.
- Never ignore pre-commit warnings or errors.
- Never use `# noqa` or `# pylint: disable` comments without asking for explicit permission from the user.

## Definition of Done
1. Code written and tested
2. There is no `# noqa` or `# pylint: disable` in the codebase without explicit permission
3. `pre-commit run --all-files` passes cleanly
4. All existing tests still pass (`pytest`)

Project rules live in `.codex/rules/` — read and follow every file there.
