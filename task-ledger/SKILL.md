---
name: task-ledger
description: Deterministic long-task ledger workflow with callback deadlines. Use when a task is expected to run longer than 10 minutes, involves multiple phases, detached work, or requires visible progress checkpoints.
---

# Task Ledger

Use this skill for long-running work so progress cannot silently disappear.

## Required workflow
1. Create or confirm an active ledger in `memory/in-progress/`
2. Record a deterministic callback deadline
   - default: 10 minutes
   - if the user specifies a time window like `in 5 minutes` or `every 20 minutes`, use that instead
3. Update the ledger at every phase boundary:
   - after triage
   - after each push/commit
   - after each verification pass
   - before yielding, handing off, or stopping
4. Send a user-visible progress update before the callback deadline elapses
5. Mark the ledger `review`, `done`, `blocked`, `failed`, or `cancelled` when appropriate

## Helper script
Use the helper for deterministic mutations:

```bash
node /Users/familybot/.openclaw/workspace/plugins/task-ledger/skills/task-ledger/scripts/ledger-helper.mjs create \
  --session-key "$SESSION_KEY" \
  --title "PR #70 deploy parity" \
  --goal "Bring the preview into parity with the source mockup" \
  --timeout-minutes 10
```

```bash
node /Users/familybot/.openclaw/workspace/plugins/task-ledger/skills/task-ledger/scripts/ledger-helper.mjs check
```

## Deterministic callback rule
A long-running task may not go past `next_callback_at` without one of:
- a user-visible checkpoint
- an explicit blocked status
- a completed/done transition
