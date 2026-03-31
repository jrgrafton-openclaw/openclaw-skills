---
name: engineering
description: "Project-level engineering workflow and quality standards for non-trivial software work. Use when: (1) starting or onboarding to a project, (2) planning or implementing a feature with 3+ steps, multiple subsystems, or state/transform pipelines, (3) fixing bugs that need reproduction, tests, and verification, (4) preparing a PR, release, or deploy, or (5) asked about process, planning, changelogs, or review workflow. NOT for platform-specific build/deploy procedures that already have a dedicated skill."
---

# Engineering Conventions

Use this skill as the default process wrapper for substantial software work.

## Core rules

1. **Plan first** for any task with 3+ steps, architecture choices, migrations, deploys, or unclear requirements.
2. **Prefer the smallest design that works**. Minimal surface area beats cleverness.
3. **Reproduce before fixing**. If you cannot reproduce the bug, you do not understand it yet.
4. **Verify before claiming done**. Run the relevant tests/builds and report proof.
5. **Do not trust delegated coding work blindly**. Independently verify important UI, deploy, and integration changes.

## Required project files

Every maintained project should have:

- `AGENTS.md` — project context and key commands
- `docs/architecture.md` — architectural decisions and boundaries
- `CHANGELOG.md` — generated from conventional commits where possible

See `assets/AGENTS.md.template`, `assets/plan.md.template`, and `references/project-setup.md`.

## Standard workflow

1. **Plan**
   - Write 3–7 checkable steps.
   - Include explicit acceptance criteria.
   - Include a **Tests** section in any plan shown to the user or another agent.
2. **Isolate work**
   - For non-trivial work, use a dedicated branch/worktree.
3. **Read before writing**
   - Trace the interacting codepaths before changing transforms, state, undo, rendering, or orchestration logic.
4. **Implement**
   - Prefer test-first when practical.
   - Keep commits small and conventional.
5. **Verify**
   - Re-run targeted tests/build/checks.
   - For UI work, run the interactive verification checklist.
6. **Ship**
   - Summarize features implemented, bugs fixed, verification run, and follow-ups/risks.

## Non-negotiable quality bars

### Tests-first discipline

For new behavior or bug fixes:
1. Write the test.
2. Run it and confirm it fails.
3. Implement the minimum fix.
4. Re-run and confirm it passes.

See `references/testing-and-refactoring.md`.

### Refactoring discipline

When unifying or refactoring a subsystem:
- find **all** consumers first
- update consumers before adding new producers
- grep for old access patterns before calling the refactor complete
- if >10 tests break, stop and identify the shared root cause instead of fixing failures one by one

See `references/testing-and-refactoring.md`.

### UI verification gate

After UI changes, test the actual interaction surface:
- click/tap every changed control
- type into every changed input
- test full lifecycle flows where relevant
- reload and confirm state persistence when applicable
- use screenshots for before/after confirmation

See `references/ui-verification.md`.

## Pull request / merge workflow

Before merge:
1. verify locally
2. simplify obvious unnecessary complexity
3. wait for review / CI
4. address only worthwhile feedback
5. re-verify after changes
6. confirm deploy / release result when applicable

PR descriptions must include:
- features implemented
- bugs fixed
- verification run
- follow-ups / risks

See `references/release-and-review.md`.

## Coding agent guidance

If you delegate implementation to another agent:
- give explicit file paths, constraints, and acceptance criteria
- require concrete verification output
- do not report success to the user until you have checked the result yourself

See `references/coding-agents.md`.
