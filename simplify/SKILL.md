---
name: simplify
description: Mandatory pre-merge simplification pass for pull requests and branches. Use when: (1) the user asks to merge, approve, land, ship, or "do a final pass" on a PR/branch, (2) a PR is green and you are considering merge readiness, (3) review feedback was just addressed and you are doing the last cleanup before merge, (4) someone asks "is this ready to merge?", "can you merge this?", "deal with review feedback", or "anything else before we land this?". Review the changed code for unnecessary complexity before merge: missed reuse of existing helpers/utilities, redundant state, parameter sprawl, copy-paste variants, leaky abstractions, stringly-typed code, unnecessary comments/wrappers, wasted work, missed concurrency, hot-path bloat, recurring no-op updates, and overly broad reads/operations. Fix worthwhile issues directly, keep scope tight, re-run verification, then summarize what was simplified. Strong default: if the conversation is about merging or pre-merge readiness, activate this skill before any merge action.
---

# Simplify

Do a **final simplification / cleanup pass before merge**.

Goal: reduce complexity without changing product behavior.

## When this skill triggers

Treat this as the default **pre-merge gate**.
If the user asks to merge, land, approve, ship, or do a final pass on a PR, run this skill **before** merging.

## What to review

Review the changed files and look for three classes of problems:

### 1) Reuse
- New helpers that duplicate existing utilities
- Inline logic that should call an existing shared helper/module
- Repeated patterns across nearby files that should use one abstraction

### 2) Quality
- Redundant or cached state that should be derived
- Parameter sprawl instead of a cleaner shape/abstraction
- Copy-paste with slight variation
- Leaky abstractions or boundary violations
- Stringly-typed logic where existing constants/types/identifiers already exist
- Unnecessary comments that explain *what* instead of *why*
- Unnecessary wrapper elements/components/indirection

### 3) Efficiency
- Redundant computations or duplicate work
- Independent operations done sequentially when they can be concurrent
- New work added to hot paths without need
- Recurring no-op state/store updates
- Overly broad reads or loads when a narrower operation is enough
- Missing cleanup / listener leaks / unbounded accumulation

## Workflow

1. **Inspect the actual changes**
   - Prefer `git diff` / `git diff --stat`.
   - For a PR, compare against the target branch if needed.
   - Focus on changed files first, not the whole repo.

2. **Run 3 review passes**
   - Reuse pass
   - Quality pass
   - Efficiency pass

3. **For bigger diffs, parallelize**
   - If the diff spans multiple files/subsystems, spawn sub-agents in parallel with one focus each: reuse, quality, efficiency.
   - Give each sub-agent the full diff or exact file list plus acceptance criteria.
   - Aggregate findings, then implement only the worthwhile fixes.

4. **Fix directly**
   - Prefer the smallest change that simplifies the code.
   - Do not perform speculative rewrites.
   - Skip low-value churn.
   - If a finding is a false positive, note it briefly and move on.

5. **Verify**
   - Re-run relevant tests/build/checks.
   - If this is a UI PR, do the interactive/screenshot verification required by the project conventions.

6. **Only then consider merge**
   - Report what was simplified.
   - Call out anything intentionally left alone.
   - Do **not** merge as part of this skill unless explicitly asked.

## Heuristics

Good simplification usually:
- removes code
- removes branching/state/parameters
- replaces custom logic with existing primitives
- narrows scope
- makes future review easier

Bad simplification usually:
- rewrites stable code without payoff
- changes behavior during a cleanup pass
- mixes refactors with unrelated feature work
- introduces a new abstraction for a one-off case

## Output

Keep the final report short:
- what was simplified
- what you intentionally left alone
- what verification ran
- whether the PR is cleaner / safer to merge now
