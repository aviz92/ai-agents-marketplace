---
mode: 'agent'
description: "Run a senior code review on the current changes"
version: 1.0.0
---

Run a thorough code review on all staged or recently changed files.

## What to review

1. Find changed files: `git diff --name-only HEAD` (or `--cached` for staged)
2. Read the full diff for each changed file
3. Apply the project's review checklist:
   - Correctness and logic errors
   - Type safety and missing type hints
   - Error handling — no bare `except:`, no silent failures
   - Security — no hardcoded secrets, validate external inputs
   - Performance — no N+1 queries, no unnecessary loops
   - Code quality — single-responsibility functions, clear naming
   - Tests — new logic should have tests

## Output format

```
## Code Review — <branch or short SHA>

### Critical Issues
> Must fix before merge.

### Major Issues
> Should fix — structural or quality problems.

### Minor Issues
> Nice to have.

### What Was Done Well
- [specific praise]

### Summary
X critical / Y major / Z minor
Verdict: APPROVE ✅ / REQUEST CHANGES ❌
```

Be direct and concise. Every critical/major issue needs a concrete fix.
