---
name: engineering
description: "Agentic engineering conventions for every project: project file structure (AGENTS.md, CHANGELOG.md, architecture.md), workspace-root plan.md workflow, mandatory git worktrees for feature work, conventional commits, explicit PR writeups (features implemented + bugs fixed + verification), Codex review wait/evaluate/fix loop, and branch/test/merge/deploy/cleanup discipline. Use when: (1) starting a new project, (2) onboarding onto an existing one, (3) implementing any non-trivial feature (3+ steps, multiple interacting subsystems, or transform/state pipeline work), (4) asked about engineering process, planning workflow, PR workflow, or changelog setup. NOT for platform-specific build/deploy steps (use ios-devops, gh-issues, etc.)."
---

# Engineering Conventions

## Project File Checklist

Every project repo must have:

| File | Purpose | Auto-generated? |
|------|---------|----------------|
| `AGENTS.md` | AI context (what it is, how to build, key commands) | No — write once |
| `CHANGELOG.md` | What shipped and when | Yes — via git-cliff |
| `docs/architecture.md` | Why it's designed the way it is | No — maintain as decisions are made |

**Naming: use `AGENTS.md`** — the cross-tool standard (OpenAI Codex, Cursor, Claude Code all read it). CLAUDE.md is Claude-specific; AGENTS.md works everywhere.

See `assets/AGENTS.md.template` for the required sections.

## plan.md — Ephemeral Feature Plans

`plan.md` lives at the **workspace root** (not in the project repo), not committed.

Lifecycle:
1. **Create** at feature start — copy `assets/plan.md.template`, fill in goal/steps/AC
2. **Work** — check off steps, update with discoveries
3. **Delete** when the feature merges to main

Why not commit it? Plans go stale. What matters is the _result_ — tests, code, CHANGELOG, architecture.md update if design changed.

## Worktree Policy

For any non-trivial feature, fix, or PR-driven task:

1. **Create a dedicated git worktree first**
2. **Create/use the feature branch inside that worktree**
3. **Do not implement non-trivial work in the main checkout**

Default sequence:
- worktree → branch → implement/verify → PR → wait for review → address comments if worthwhile → re-verify → merge → verify deploy/CI → cleanup

After merge:
- remove the feature worktree
- delete the local feature branch if appropriate
- delete the remote feature branch if appropriate
- report completion only after cleanup or after explicitly stating why cleanup was deferred

If work is paused or waiting on feedback, preserve the worktree and report its path + branch.

## Pull Request Workflow

For GitHub-based delivery, use this default loop unless the user explicitly asks to bypass it:

1. **Implement in worktree**
2. **Verify locally**
3. **Open PR**
4. **Wait for Codex review / automated review feedback**
5. **Evaluate review comments one by one**
6. **Fix real issues; ignore low-value noise**
7. **Re-run verification after changes**
8. **Merge only when CI is green and the PR is in good shape**
9. **Verify merge + deploy status if applicable**
10. **Inform the user**

Treat automated review comments as advisory, not mandatory. Validate whether each comment is:
- correct
- relevant
- worth the added complexity

If adopting a comment, mention that in the final report. If declining one, be able to explain why briefly.

## PR Description Requirements

Do not open vague PRs. Every PR body should explicitly list:

- **Features implemented**
- **Bugs fixed**
- **Verification performed**
- **Follow-ups / risks** (if any)

Prefer concrete bullets over generic summaries.

Good pattern:

```md
## Features implemented
- add projectile FX when hit roll starts
- add persistent wound state for damaged multi-wound units

## Bugs fixed
- fix overlay drift during zoom
- fix projectile origin/target misalignment under zoom

## Verification
- `pnpm test`
- `pnpm --filter @wh40k/ui build`
- browser QA for zoom, overlays, wound persistence
```

If a PR is pure bugfix work, still separate fixes from verification. If a PR mixes new features and bugfixes, list both explicitly.

## CHANGELOG via git-cliff

```bash
# Setup (once per project) — copies cliff.toml + patches package.json if present
bash skills/engineering/assets/setup-cliff.sh <project-dir>

# Update after each release/tag
git cliff -o CHANGELOG.md
```

Requires **conventional commits** — see `references/agentic-practices.md` for the format.

## Agentic Engineering Practices

See `references/agentic-practices.md` for the full guide. Quick rules:

1. **Read before writing** — before implementing code that touches transforms, state pipelines, undo systems, or any multi-layered subsystem, **read ALL interacting code first**. Trace one concrete example through the full pipeline with real values before designing. Don't reason about composed transforms abstractly — they combine in non-obvious ways (e.g. flip-aware crop + rotation + clip paths).
2. **Tests before implementation** — write the test, watch it fail, then implement
3. **Worktree + feature branch** — never do non-trivial work directly on `main`
4. **Conventional commits** — `type(scope): description` on every commit
5. **CI must pass** before merging — never merge red
6. **Verify before "done"** — run tests, check build, confirm acceptance criteria met
7. **Commit small** — each commit = one logical change, buildable
8. **Update CHANGELOG** — run `pnpm changelog` (or equivalent) before tagging a release
9. **Wait for review by default** — do not merge immediately after opening a PR unless the user explicitly asks
10. **Verify after merge** — confirm merge landed and confirm deploy/artifact status when relevant
11. **Clean up branches/worktrees** — keep the repo tidy after merge
