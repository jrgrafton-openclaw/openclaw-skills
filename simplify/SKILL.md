---
name: simplify
description: "Mandatory pre-merge simplification pass for pull requests and branches. Use when: (1) the user asks to merge, approve, land, ship, or do a final pass on a PR/branch, (2) a PR is green and you are considering merge readiness, (3) review feedback was just addressed and you are doing the last cleanup before merge, or (4) someone asks whether a branch is ready to merge. Review the changed code for unnecessary complexity, fix worthwhile issues directly, keep scope tight, re-run verification, and summarize what was simplified. Strong default: if the conversation is about merging or pre-merge readiness, activate this skill before merge action."
---

# Simplify

Run a final simplification pass before merge.

Goal: reduce unnecessary complexity **without** changing product behavior.

## What to review

Check the changed files for three classes of problems:

1. **Reuse**
   - duplicated helpers
   - inline logic that should use existing utilities
   - repeated patterns that want one abstraction

2. **Quality**
   - redundant state
   - parameter sprawl
   - copy-paste variants
   - leaky abstractions
   - stringly-typed logic
   - unnecessary wrapper layers/comments

3. **Efficiency**
   - duplicated work
   - sequential independent work that can be concurrent
   - hot-path bloat
   - no-op state updates
   - overly broad reads/loads
   - missing cleanup

## Workflow

1. Inspect the actual diff.
2. Review for reuse, quality, and efficiency.
3. Fix only worthwhile issues.
4. Re-run relevant verification.
5. Summarize what was simplified and what was intentionally left alone.

Do **not** merge as part of this skill unless explicitly asked.
