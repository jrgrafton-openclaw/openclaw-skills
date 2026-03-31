---
name: sub-agents
description: "Orchestrate sub-agent sessions via sessions_spawn for long-running, parallel, or isolated tasks. Use when a task has 5+ well-defined steps that can run independently, you need parallel workstreams, or inline work would pollute context. NOT for quick tasks, tasks needing clarification, or situations where result reporting back to the user is not yet planned."
---

# Sub-agent orchestration

## When to spawn

Spawn only when all of these are true:
- the task is well-scoped
- acceptance criteria are explicit
- the sub-agent can start cold from the written task description
- you already know how the result will be reported back to the user

Do inline when the task is short, ambiguous, or tightly coupled to the next conversational turn.

## User communication is mandatory

Long-running work must never become invisible.

### Immediately after spawning
Tell the user:
- what was delegated
- approximate ETA
- whether you will poll manually or expect a completion event

### If the work runs longer than ~5 minutes
Send a brief progress update.

### When the sub-agent finishes or fails
Reply manually to the user with the result. On Slack, do **not** rely on thread-routing hooks alone.

## Slack-specific rule

Slack routing hooks are not reliable enough to be the only completion path.

If you spawn on Slack:
- prefer a clear manual follow-up plan
- check status on demand
- post the outcome yourself in-thread when the work completes

## Pre-flight

Before spawning, ensure:
- the task description includes current state, file paths, acceptance criteria, constraints, and required verification
- the timeout is sized for the work
- the user-facing follow-up path is clear

If sub-agent permissions or gateway scopes are missing, **report the failure and stop**. Do not edit pairing files or restart the gateway from inside an active agent session.

## Task description checklist

Include:
- what is already done
- exact files / interfaces to change
- acceptance criteria
- tests / verification commands
- constraints
- required report format when done

## Verification checklist for returned results

Never trust self-reported completion blindly. Verify the result directly:
- inspect changed files or commits
- check CI/deploy state if relevant
- verify live URLs or built artifacts if relevant
- run the claimed verification where appropriate

## Task sizing

- prefer incremental tasks over giant rewrites
- split unrelated workstreams into separate agents
- avoid asking one sub-agent to generate multiple large outputs in one run

## Steer / kill

Use steer when requirements change. Use kill when the task is clearly wrong or no longer needed.
