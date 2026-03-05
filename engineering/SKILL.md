---
name: engineering
description: "Agentic engineering conventions for every project: project file structure (AGENTS.md, CHANGELOG.md, architecture.md), ephemeral plan.md workflow, conventional commits, git-cliff CHANGELOG automation, and branch/test/merge discipline. Use when starting a new project, onboarding onto an existing one, or when asked about engineering process, planning workflow, or changelog setup. NOT for platform-specific build/deploy steps (use ios-devops, gh-issues, etc.)."
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

## CHANGELOG via git-cliff

```bash
# Setup (once per project)
cp skills/engineering/assets/cliff.toml.template <project>/cliff.toml
# Add to package.json scripts:
#   "changelog": "git cliff -o CHANGELOG.md"

# Update after each release/tag
git cliff -o CHANGELOG.md
```

Requires **conventional commits** — see references/agentic-practices.md for the format.

## Agentic Engineering Practices

See `references/agentic-practices.md` for the full guide. Quick rules:

1. **Tests before implementation** — write the test, watch it fail, then implement
2. **Feature branch** — never commit directly to `main`
3. **Conventional commits** — `type(scope): description` on every commit
4. **CI must pass** before merging — never merge red
5. **Verify before "done"** — run tests, check build, confirm acceptance criteria met
6. **Commit small** — each commit = one logical change, buildable
7. **Update CHANGELOG** — run `pnpm changelog` (or equivalent) before tagging a release
