---
name: engineering
description: "Agentic engineering conventions for every project: project file structure (AGENTS.md, CHANGELOG.md, architecture.md), workspace-root plan.md workflow, mandatory git worktrees for feature work, conventional commits, explicit PR writeups (features implemented + bugs fixed + verification), Codex review wait/evaluate/fix loop, and branch/test/merge/deploy/cleanup discipline. Use when: (1) starting a new project, (2) onboarding onto an existing one, (3) implementing any non-trivial feature (3+ steps, multiple interacting subsystems, or transform/state pipeline work), (4) asked about engineering process, planning workflow, PR workflow, or changelog setup. NOT for platform-specific build/deploy steps (use ios-devops, gh-issues, etc.)."
---

# Engineering Conventions

## 1. Project Setup

### Required Files

| File | Purpose | Auto-generated? |
|------|---------|----------------|
| `AGENTS.md` | AI context (what it is, how to build, key commands) | No — write once |
| `CHANGELOG.md` | What shipped and when | Yes — via git-cliff |
| `docs/architecture.md` | Why it's designed the way it is | No — maintain as decisions are made |

**Naming: use `AGENTS.md`** — the cross-tool standard (OpenAI Codex, Cursor, Claude Code all read it).

See `assets/AGENTS.md.template` for the required sections.

### plan.md — Ephemeral Feature Plans

`plan.md` lives at the **workspace root** (not in the project repo), not committed.

Lifecycle:
1. **Create** at feature start — copy `assets/plan.md.template`, fill in goal/steps/AC
2. **Work** — check off steps, update with discoveries
3. **Delete** when the feature merges to main

### Plans Must Include Tests

Every plan presented to the user — whether a plan.md file, a Slack message, or a sub-agent task — must include a **Tests** section listing what tests will be written. Tests are not an implementation detail; they define acceptance criteria.

Bad: "Step 1: add color helper. Step 2: wire it up. Step 3: add slider."
Good: "Step 1: add color helper. Step 2: wire it up. Step 3: add slider. **Tests:** color helper edge cases, serialize round-trip, backwards compat, visual verification with non-default color."

If you present a plan without tests, you haven't finished planning.

---

## 2. Git Discipline

### Worktree Policy

For any non-trivial feature, fix, or PR-driven task:

1. **Create a dedicated git worktree first**
2. **Create/use the feature branch inside that worktree**
3. **Do not implement non-trivial work in the main checkout**

Default sequence:
worktree → branch → implement/verify → PR → review → fix → re-verify → merge → verify deploy/CI → cleanup

### Conventional Commits

Format: `type(scope): short description`
Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `ci`

### Commit Sizing

Each commit = one logical change that builds and tests green.
For complex visual/interactive bugs: **one change per push** — make ONE change, verify, commit, then the next.

---

## 3. Refactoring Discipline

**This section exists because of a real failure:** an entity system refactor introduced 8 bifurcated code paths because creation was unified but consumption was not audited.

### The Consumer-First Rule

When unifying N implementations behind a shared interface:

1. **Find ALL consumers first** — grep for every function/property that accesses the old type-specific code (`_findSprite`, `C.allSprites.find`, `sp.rootEl`, etc.)
2. **List every call site** — not just the ones you think are relevant
3. **Update consumers BEFORE adding new producers** — if `addToGroup()` still calls `_findSprite()`, adding a new entity type that passes through `addToGroup()` will silently fail
4. **Test each consumer with each type** — if groups should work for sprites + FX + lights, test all three in groups

### The Grep Audit

Before marking a refactor complete, run:
```bash
# Find all references to the old type-specific code
grep -rn 'oldFunction\|oldProperty\|OldType' src/
```
Every hit is either: (a) intentionally type-specific (guard with comment why), or (b) a bug you need to fix.

### Test With the Full Fixture

When the user provides a test fixture (JSON scene, config file, etc.):
- **Always load it** for integration testing — don't test with empty/minimal state
- Save it as a test fixture file in the project
- Real scenes have groups, nested entities, edge cases that empty scenes miss

### Common Refactoring Traps

| Trap | Example | Prevention |
|------|---------|------------|
| **Unified creation, bifurcated consumption** | Entity created with shared interface but `_findSprite()` still used in undo commands | Grep for all old accessors before marking done |
| **Copied rendering, missed interaction** | FX row renders in layers panel but has no drag handlers | For every "create row" call, check: does the old type also set up event handlers? |
| **String-based type dispatch** | `if (id.startsWith('fx'))` instead of `entity.type === 'fire'` | Use the Entity interface, not string heuristics |
| **Partial handler coverage** | mousedown handler calls `select()` but forgets `preventDefault()` that the old code had | Diff the old handler against the new one line by line |

---

## 4. Implementation Workflow

### Read Before Writing

Before implementing code that touches transforms, state pipelines, undo systems, or any multi-layered subsystem: **read ALL interacting code first.** Trace one concrete example through the full pipeline with real values before designing.

### Tests First

1. Write test that describes the desired behavior
2. Run test — confirm it **fails** (proves the test is real)
3. Implement the minimum code to make it pass
4. Run test — confirm it **passes**

**For bug fixes:** write a test that reproduces the bug → confirm red → fix → confirm green.

### Reproduce Before Fixing

Before writing ANY fix, reproduce the exact bug:
- For visual bugs: in the browser
- For logic bugs: with a failing test
- If you can't reproduce it, you don't understand it yet

### Stop After a Failed Fix

If a fix doesn't work, do NOT immediately try another approach. First: explain WHY the previous fix failed. Write it down. Two failed fixes in a row = step back, read all interacting code, restate the problem from scratch.

---

## 5. Visual & Interactive Verification

### Screenshot Gate (Mandatory for UI Changes)

1. **Before** — screenshot the current visual state
2. **Change** — make the code change
3. **After** — screenshot the new visual state
4. **Compare** — confirm the difference matches intent
5. **Only then** — commit

Never commit visual changes based solely on "the math looks right."

### Interactive Verification (Mandatory for Interactions)

For drag, resize, rotate, click handlers:
1. Reproduce the bug interactively before writing any fix
2. Test the fix interactively (simulate user interaction, not just compute values)
3. Test at multiple states (e.g. 0°, 45°, 90°, odd angles)
4. Test edge cases (flipped, zero-size, nested in groups)

### Coordinate Space Discipline

When working with transforms (rotation, scale, flip, translation):
1. **Label every variable** with its coordinate space: `// global (screen)` or `// local (pre-rotation)`
2. **Verify with concrete numbers** at rot=0 AND rot=90 before coding
3. **Never mix coordinate spaces**
4. **Anchor point rule** — when resize changes rotation center, compute visual drift and compensate

---

## 6. Pull Request Workflow

### PR Loop

1. Implement in worktree
2. Verify locally
3. Open PR
4. Wait for review / automated feedback
5. Evaluate comments (correct? relevant? worth the complexity?)
6. Fix real issues; ignore noise
7. Re-verify after changes
8. Merge when CI is green
9. Verify merge + deploy
10. Inform the user

### PR Description (Required)

Every PR body must explicitly list:

```md
## Features implemented
- ...

## Bugs fixed
- ...

## Verification
- `pnpm test` — N tests pass
- browser QA for [specific interactions]

## Follow-ups / risks
- ...
```

### PR Preview for GitHub Pages

Add `.github/workflows/pr-preview.yml` for static HTML projects:
- `destination_dir: preview/pr-${{ github.event.pull_request.number }}`
- `keep_files: true` to preserve other previews
- Auto-comment with preview URL

---

## 7. CHANGELOG

```bash
# Setup (once per project)
bash skills/engineering/assets/setup-cliff.sh <project-dir>

# Update after each release/tag
git cliff -o CHANGELOG.md
```

Requires conventional commits.

---

## 8. Quick Reference

See `references/agentic-practices.md` for expanded rationale on tests-first, branch workflow, commit discipline, and AGENTS.md quality bar.
