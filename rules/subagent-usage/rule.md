# Subagent Orchestration

## Purpose

Use subagents deliberately, not reflexively. Delegation should buy parallelism, clean context, or specialized capability — never used just because a task has several steps. Every subagent's output is a claim to verify, not a fact to relay.

## Core Principle

**Fresh subagent per well-scoped task → task-level review (spec compliance + code quality) → one broad review at the end.** This combination keeps quality high without slowing iteration down.

## 1. When to Delegate

- Delegate when a task is narrow, well-scoped, and matches an existing subagent's purpose (running tests, locating code, reviewing a diff, implementing one item from a plan).
- Do not spawn a subagent merely because a task has multiple steps. Delegate when either: (a) the intermediate output isn't worth keeping in your own context (long logs, broad searches), or (b) the task clearly matches a specialized agent's purpose.
- If no subagent fits, do the work directly rather than forcing a delegation.
- Never invent or assume an agent exists — check the available agent list first.

## 2. Picking an Agent

- Prefer the most specific available subagent over a general-purpose one (a test-runner for tests, not a general coder).
- Match tool access to the task — a read-only investigation goes to a read-only agent, not one with write access.
- When several agents could work, pick the one whose description most tightly matches the task's verb (review vs. implement vs. locate).

## 3. Briefing a Subagent

A fresh subagent has zero context from this conversation — brief it like a new hire who just walked in.

- State the goal and why it matters, not just the instruction.
- Name relevant files, line numbers, and constraints already established. Don't make the subagent rediscover what you already know.
- Define scope explicitly: what's in bounds, what's out of bounds.
- Specify the expected output format and depth ("report failures with file:line detail," not "let me know how it goes").
- If you need a short response, say so — open-ended prompts produce open-ended reports.

## 4. Autonomy Boundaries

- Subagents must not modify code, commit, or push unless explicitly instructed to.
- A read-only or reporting subagent (test-runner, reviewer, locator) only runs, reads, and reports — never fixes or refactors unless the task says so.
- An implementer subagent stays inside the task it was given. It does not expand scope to "fix while I'm here" without flagging it back to you first.

## 5. Verification

- Treat every subagent summary as a claim, not a fact — it describes what the agent intended to do, not necessarily what it did.
- For code changes: read the actual diff before reporting the work as done.
- For high-stakes or final-stage work: route verification through a dedicated review subagent rather than trusting the implementer's self-report.

## 6. Subagent-Driven Development Workflow

For executing a multi-task plan:

1. Dispatch one fresh implementer subagent per task. Never reuse an implementer across tasks, and never let one subagent implement multiple tasks in a single dispatch.
2. After each task, dispatch a task-level review (spec compliance + code quality) before moving to the next task.
3. After all tasks are complete, run one broad, whole-branch review covering integration and consistency — the things task-level reviews can't see.

## 7. Continuous Execution

- Execute all tasks in the plan without pausing to check in between them.
- Narrate at most one short line between tool calls — the task ledger and tool results already carry the record; don't restate them.
- Valid reasons to stop mid-plan: a BLOCKED status you cannot resolve yourself, ambiguity that genuinely prevents progress (not just uncertainty you could resolve by reading more code), or all tasks complete.
- Don't ask "should I continue?" and don't produce interim progress summaries. If the user asked for the plan to be executed, execute it.

## 8. Handling Blockers

- If a subagent reports BLOCKED, try to resolve it yourself first (read the referenced files, check the ambiguity against the plan) before stopping.
- Only surface a blocker to the user when it requires a decision only they can make — a genuine product/design choice, missing credentials, conflicting requirements.
- When surfacing a blocker, state what's blocked, why, and the smallest decision needed to unblock it. Skip the full status recap.

## 9. Reporting

- After a subagent completes, name which agent ran the task and summarize the result. Never silently absorb its output as your own work.
- Keep the summary proportional to what changed: one line for a clean pass, more detail when something needed correction.