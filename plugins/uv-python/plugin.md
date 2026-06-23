# UV Python Package Manager

Use `uv` exclusively for all Python dependency and environment management.
Never use `pip`, `pip-tools`, `poetry`, `pdm`, or `conda` directly.

## Package management

```bash
# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Remove a dependency
uv remove <package>

# Sync the environment from lockfile
uv sync

# Run a command inside the managed environment
uv run <command>
```

## Project setup

```bash
# Create a new project
uv init <project-name>

# Install all dependencies (including dev)
uv sync --all-extras
```

## Running tools and scripts

```bash
# Always prefix commands with `uv run` — never activate the venv manually
uv run pytest
uv run pre-commit run --all-files
uv run python -m <module>
```

## Rules

- Never write `pip install` in instructions, scripts, CI steps, or READMEs.
- Never create or activate a virtualenv manually — `uv` manages it.
- Lock file (`uv.lock`) must be committed; do not `.gitignore` it.
- Python version is pinned in `pyproject.toml` under `[project] requires-python`.
- When adding a new dependency, always run `uv sync` afterward to verify the lockfile is consistent.
