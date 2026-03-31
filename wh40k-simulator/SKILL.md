---
name: wh40k-simulator
description: "WH40K Simulator repository conventions: file placement, architecture boundaries, verification workflow, deploy rules, and task handoff guidance. Use when working on any task in the warhammer-40k-simulator repo across game, editor, mockups, shared modules, or CI."
---

# WH40K Simulator conventions

## Staleness check — run first

Before using this skill, verify the documented structure still matches the repo.
If the structure drifted, update the skill before relying on it.

## Use this skill for repo-specific rules

This skill defines:
- where files belong
- which rendering / state boundaries matter
- how to verify changes in the browser
- deploy constraints for this repo
- what context sub-agents need

## Core rules

1. Do not create files in ad hoc locations; use the file placement map.
2. Keep shared code import-only: `shared/` must not depend on `game/` or `editor/`.
3. Use repo-specific verification, not generic “looks good”.
4. Never commit directly to `gh-pages` for this repo.
5. If a regression existed in a known-good version, restore the original pipeline before inventing a fallback.

## References

- `references/file-placement.md`
- `references/architecture.md`
- `references/verification.md`
- `references/deploy.md`
