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

## PR Preview for Static HTML / GitHub Pages Projects

When a project deploys static HTML to GitHub Pages (via `peaceiris/actions-gh-pages` or similar), add a **PR preview workflow** so every PR gets its own live URL for side-by-side comparison.

Add `.github/workflows/pr-preview.yml`:

```yaml
name: PR Preview
on:
  pull_request:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Add your project's build steps here (pnpm install, build, etc.)
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist          # adjust to your build output
          publish_branch: gh-pages
          destination_dir: preview/pr-${{ github.event.pull_request.number }}
          keep_files: true
      - uses: peter-evans/create-or-update-comment@v4
        with:
          issue-number: ${{ github.event.pull_request.number }}
          body: |
            🔍 **Preview deployed:** https://<owner>.github.io/<repo>/preview/pr-${{ github.event.pull_request.number }}/
```

**Key points:**
- `destination_dir` isolates each PR's build under `preview/pr-N/` so it doesn't clobber production
- `keep_files: true` preserves the main site + other PR previews
- The comment auto-posts the preview link on the PR
- Consider adding a cleanup workflow that removes `preview/pr-N/` when the PR is closed/merged
- Only use this for projects with static HTML output — not for projects that deploy via other mechanisms

## Visual / UI Change Verification

For any change that affects visual appearance or interactive behavior (transforms, layout, drag/resize, animations, CSS):

### Mandatory: Screenshot Gate
1. **Before** — screenshot or evaluate the current visual state in the browser
2. **Change** — make the code change
3. **After** — screenshot or evaluate the new visual state
4. **Compare** — confirm the visual difference matches what was intended
5. **Only then** — commit and push

Never commit visual/UI changes based solely on "the math looks right." Math verification is necessary but NOT sufficient — you must see the actual pixels.

### Mandatory: Interactive Verification
For interactive features (drag, resize, rotate, click handlers):
1. **Reproduce the bug** interactively before writing any fix
2. **Test the fix** interactively (simulate the user interaction, not just compute expected values)
3. **Test at multiple states** — e.g. for rotation-dependent code, test at 0°, 45°, 90°, and an odd angle like 24°
4. **Test edge cases** — flipped sprites, zero-size, negative values

### Coordinate Space Discipline
When working with transforms (rotation, scale, flip, translation):
1. **Label every variable** with its coordinate space: `// global (screen) coords` or `// local (pre-rotation) coords`
2. **Verify with concrete numbers** at rot=0 (trivial case) AND rot=90 (axis-swap case) before coding
3. **Never mix coordinate spaces** — if a compensation vector is computed in global space, rotate it back to local before applying to x/y
4. **Anchor point rule** — when resize changes the rotation center, compute the visual drift of the anchor point and compensate. Derive the closed-form formula; don't iterate or guess.

### One Change Per Push
For complex visual/interactive bugs:
1. Make ONE change
2. Verify it visually
3. Commit
4. Then make the next change

Never batch multiple fixes (e.g. preserveAspectRatio + migration + probe fix) — if one is wrong, you can't tell which.

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
