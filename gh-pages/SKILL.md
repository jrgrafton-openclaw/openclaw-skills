---
name: gh-pages
description: "CI-first GitHub Pages deployment workflow for static sites and web app previews. Use when setting up or fixing GitHub Pages publishing so main deploys automatically via CI, pull requests get preview deploys, and `gh-pages` is treated as build output rather than a manual working branch. NOT for manual branch-only Pages workflows."
---

# CI-first GitHub Pages

Use this skill to set up GitHub Pages the way we want it to work now:

1. **Always deploy via CI**
2. **Every PR gets a preview deploy**
3. **Production Pages deploy comes from `main` via workflow**
4. **`gh-pages` is build output, not a manual editing branch**

The reference implementation is the WH40K repo:
`jrgrafton-openclaw/warhammer-40k-simulator`

## Default pattern

### Main branch
- run tests/build in CI
- if CI passes on `main`, publish the built output to `gh-pages`
- never hand-edit `gh-pages`

### Pull requests
- build the PR in CI
- publish preview output under `preview/pr-<number>/`
- comment the preview URL back on the PR

### Cleanup
- when the PR closes, delete its preview directory from `gh-pages`

## Rules

- **Do not commit directly to `gh-pages`.**
- **Do not ask the agent to sync files manually between `main` and `gh-pages`.**
- **Use the WH40K workflows as the starting template** unless the repo has a strong reason to differ.
- **Preserve other previews** when deploying a single PR preview (`keep_files: true`).
- **Verify the live Pages URL after deploy.**

## What to copy from WH40K

See `references/wh40k-pattern.md` for the exact workflow shape.

At minimum, mirror these three workflows:
- main CI + production deploy
- PR preview deploy
- preview cleanup on PR close

## Required deliverables when applying this skill

1. A production Pages workflow that deploys from `main`
2. A PR preview workflow that comments the preview URL
3. A cleanup workflow that removes stale preview directories
4. A short note in the repo docs/AGENTS.md explaining the Pages URLs and preview pattern

## Verification

After wiring the workflows:
- confirm PR preview URL is posted and loads
- confirm `main` deploy lands at the production URL
- confirm closing a PR removes its preview directory
