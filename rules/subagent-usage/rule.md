# Subagent Usage

## When to delegate
- Delegate to a subagent when a task is narrow, well-scoped, and matches an
  existing subagent's purpose (e.g. running tests, locating code, reviewing a diff).
- Do NOT spawn a subagent just because a task has multiple steps — only when its
  intermediate output is not worth keeping in your own context, or its purpose
  clearly matches a specialized agent.

## Picking an agent
- Prefer the most specific available subagent over a general-purpose one
  (e.g. a test-runner agent for running tests, not a general coder).
- If no subagent fits the task, do the work directly instead of forcing a delegation.
- Never invent or assume an agent exists — check the available agent list first.

## Briefing a subagent
- A fresh subagent has zero context — explain the goal, relevant files, and any
  constraints already established; do not assume it read the conversation.
- Give a self-contained prompt: what to do, what's in scope, what's out of scope.
- State the expected output format and level of detail (e.g. "report failures with
  file:line detail" rather than "let me know how it goes").

## Autonomy boundaries
- Subagents must not modify code, commit, or push unless explicitly instructed to.
- A read-only or reporting subagent (e.g. test-runner, reviewer) must only run,
  read, and report — never fix or refactor unless the task says so.
- Treat a subagent's summary as a claim, not a fact — verify results before
  reporting them as done, especially for code changes.

## Reporting
- After a subagent completes, tell the user which agent ran the task and
  summarize the result — do not silently absorb its output as your own work.
