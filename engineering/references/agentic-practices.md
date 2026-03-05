# Agentic Engineering Practices

SOTA practices for AI-assisted software development (2025/2026).

## Tests First

Write the test before writing implementation code.

```
1. Write test that describes the desired behaviour
2. Run test — confirm it FAILS (proves the test is real)
3. Implement the minimum code to make it pass
4. Run test — confirm it PASSES
5. Refactor if needed; tests must still pass
```

Why it matters for agents: without tests written first, it's easy to write implementation that _looks_ correct but has subtle bugs. Tests-first forces you to define "done" before you start.

**For new features:** write tests → run pnpm test (red) → implement → run pnpm test (green) → commit.  
**For bug fixes:** write a test that reproduces the bug → confirm red → fix → confirm green.

## Branch Workflow

```
main        ← always green; tagged releases only
  └── feat/shooting-phase    ← feature work
  └── fix/drag-movement      ← bug fixes
  └── chore/git-cliff        ← non-feature work
```

Rules:
- **Never commit directly to `main`** unless it's a trivial doc-only change
- Branch names: `feat/<name>`, `fix/<name>`, `chore/<name>`, `docs/<name>`
- Merge to main only when: tests pass, build passes, acceptance criteria met
- Delete feature branch after merge

For solo projects (no PR review): use branches + squash-merge or rebase-merge to keep main history clean.

## Conventional Commits

Format: `type(scope): short description`

```
feat(engine): add ADVANCE_UNIT action with D6 roll
fix(ui): drag-based movement replaces click-to-destination
chore(deps): upgrade pixi.js to 8.x
docs(architecture): document blob-unit upgrade path
test(shooting): add wound roll table exhaustive tests
refactor(content): extract weaponToEngine mapper
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `ci`

Why it matters: git-cliff reads these to auto-generate CHANGELOG. Consistent commits = zero-effort release notes.

## Acceptance Criteria Before Implementation

Every feature plan needs measurable "done" criteria before starting:

```markdown
## Acceptance criteria
- [ ] pnpm test passes (target: N tests)
- [ ] pnpm build passes with no TS errors
- [ ] [specific behaviour]: [how to verify it]
- [ ] CHANGELOG.md updated
```

Never call something "done" without checking all criteria. If a criterion can't be verified, it's not a criterion — it's a hope.

## CI Gates

For every project with CI:
- **Tests must pass** on every PR/push to main
- **Build must pass** (no TS errors, no lint errors)
- **Coverage should not decrease** (optional but useful)

For agentic workflows specifically: CI is the guard against the agent being confidently wrong. Never disable or skip CI checks.

## When to Commit

Commit when:
- A logical unit of work is complete and tests pass
- You're about to try something risky (commit first = easy rollback)
- At the end of a working session

Don't commit:
- Broken/failing tests
- WIP that doesn't build
- Temporary debugging code

## Keeping main Clean

- `main` should always build and pass tests
- If you accidentally break main: fix it immediately, don't leave it broken
- Use `git revert` rather than force-pushing to main
- Tag releases: `git tag v1.2.3 && git push origin --tags`

## Plan.md Template Usage

See `assets/plan.md.template`. Fill it in at the start of any task with 3+ steps. Delete it when the task merges.

Key sections:
- **Goal** — one sentence
- **Steps** — 3–7 checkable items with acceptance criteria baked in
- **Key risks/unknowns** — what could go wrong
- **Files to touch** — prevents scope creep

## AGENTS.md Quality Bar

A good `AGENTS.md` answers these questions cold:
1. What is this project?
2. How do I run it? (install → build → test commands)
3. What are the key architectural decisions I must not violate?
4. What are the most important files/directories?
5. Are there any gotchas or known issues?

Keep it under 200 lines. Link to `docs/architecture.md` for deeper context.
