---
name: pr-bug-fix-web
description: "Triage, fix, and verify bugs reported on web project PRs. Use when: (1) user reports visual or functional bugs with screenshots on an open PR, (2) PR review comments describe broken behavior in a web mockup/app, (3) you need to systematically fix multiple bugs on a feature branch with independent verification. Covers the full cycle: triage → structured bug report → fix agent → independent verify agent → cleanup. Web-focused: uses browser tool, DOM queries, computed styles, SVG geometry for measurable verification. NOT for: test-only changes, non-web platforms (use platform-specific skills), or greenfield feature work."
---

# PR Bug Fix — Web

Structured workflow for fixing bugs reported on web project PRs. Each bug goes through: **Triage → Report → Fix → Verify → Cleanup**.

## When This Triggers

- User sends screenshots of broken behavior on a PR
- GH review comments describe visual/functional regressions
- Multiple bugs need systematic fixing on a feature branch

## Step 1: Triage

Read the user's bug reports (Slack messages, screenshots, GH comments). For each reported issue:

1. **Assess clarity.** If the bug report is ambiguous, uncertain, or missing critical info — **ask the user before proceeding.** Specifically ask when:
   - The screenshot doesn't clearly show what's wrong vs what's expected
   - The bug could be in multiple places and you can't tell which from the description
   - You need to know the exact reproduction steps (which page, which state, which interaction)
   - The expected behavior isn't obvious from context
   - Multiple bugs are tangled together and you need the user to prioritize

   Don't guess. A 30-second clarification question saves a 30-minute wrong fix.

2. **Investigate each clear bug.** For each one:
   - Grep for relevant selectors/functions in the codebase
   - Read the suspect files, trace the code path
   - Identify the root cause at the **code-symbol level** (exact file, line, mechanism)
   - Define a **measurable acceptance check** (not "looks right" — a DOM query, computed style, geometry comparison, or element count that proves the fix)

3. **Write the structured bug report.** Create `bug-reports/<pr-number>/bugs.md`:

```markdown
# Bug Report — PR #<number>

## BUG-1: <short description>

**What's wrong:** <concrete, measurable description>
**Screenshot:** `screenshots/<filename>.png`
**Root cause:** <exact file, line, mechanism>
**Acceptance check:** <measurable condition that proves it's fixed>
**Fix approach:** <specific code change>
```

4. **Save user screenshots** to `bug-reports/<pr-number>/screenshots/`.
5. **Commit + push** the bug report to the feature branch.
6. **Comment on the PR** with a summary via `gh pr comment`.

## Step 2: Fix

Spawn a sub-agent:

```
task: "Read bug-reports/<pr>/bugs.md. Fix each bug per the
acceptance checks. One conventional commit per bug:
fix(scope): description (BUG-N). Push to <branch>."
model: opus
```

The fix agent, for each bug:
1. Reads the bug entry from `bugs.md`
2. Implements the fix approach
3. Verifies locally against the acceptance check (measurable)
4. Commits and pushes

## Step 3: Verify

Spawn a **separate** sub-agent — not the same one that fixed:

```
task: "Read bug-reports/<pr>/bugs.md. For each bug, verify
the fix using the EXACT acceptance check. Serve the app
locally. Use browser tool for visual bugs. Report PASS or
FAIL with measurable evidence per bug."
model: opus
```

The verify agent, for each bug:
1. Serves the web app locally (`python3 -m http.server` or project dev server)
2. Opens in browser, navigates to the bug's context
3. Runs the measurable check:
   - DOM queries (`document.querySelectorAll('.class').length`)
   - Computed styles (`getComputedStyle(el).opacity`)
   - SVG geometry (`el.getBBox()`, `el.getScreenCTM()`)
   - Layout measurements (`el.getBoundingClientRect()`)
   - Element counts, class presence, attribute values
4. For subtle visual issues: temporarily exaggerate the suspect feature (red outlines, high opacity, center guides) to confirm, then remove
5. Reports `PASS` with evidence or `FAIL` with what's still wrong

**Why a separate agent:** The fixer has confirmation bias. An independent verifier catches failures the fixer missed. This caught a real bug today (clipPath applied to wrong SVG element due to runtime reparenting).

## Step 4: Handle Failures

For any `FAIL` from the verify agent:

1. Read the failure evidence — the verify agent describes what's still wrong
2. Diagnose the real root cause (often different from the original hypothesis)
3. Update `bugs.md` with the revised root cause
4. Either fix directly (if small) or re-spawn a fix agent for just the failed bugs
5. Re-spawn a verify agent for just the re-fixed bugs
6. Repeat until all `PASS`

## Step 5: Cleanup

After ALL bugs are verified as `PASS`:

1. Mark each bug as `✅ VERIFIED` in `bugs.md`
2. Remove the entire `bug-reports/<pr-number>/` directory
3. Commit: `chore: remove resolved bug report artifacts`
4. Push to the feature branch
5. Update the PR description with final summary:

```markdown
## Bugs fixed
- BUG-1: <description> — <commit hash>
- BUG-2: <description> — <commit hash>

## Verification
- All bugs independently verified via browser automation
- <specific evidence summary>

## Risks
- <any side effects or edge cases noted>
```

6. Post result to user (Slack/thread)

## Measurable Verification Patterns (Web)

Common checks by bug type:

| Bug type | Measurable check |
|----------|-----------------|
| Element not centered | `el.getBoundingClientRect().left + width/2 === window.innerWidth/2` |
| Missing overlay/fade | `getComputedStyle(el).opacity > 0` on both sides |
| Stale elements visible | `document.querySelectorAll('.stale-class').length === 0` |
| SVG overflow | `el.getBBox().y >= 0 && el.getBBox().height <= 528` |
| Wrong phase state | `document.body.classList.contains('phase-X')` |
| Layout shift | Capture `gridTemplateColumns` over time during animation |
| Zone shading missing | `getComputedStyle(zoneEl).opacity !== '0'` in active phase |
| Font overflow | `text.getBBox().width <= container.getBBox().width` |

When in doubt: **if you can't express the check as a JS expression that returns true/false, you haven't defined it precisely enough.**

## Key Principles

- **Don't guess when the bug report is unclear** — ask the user
- **One bug per commit** — easy to revert, clean PR history
- **Fix and verify are always separate agents** — eliminates confirmation bias
- **Measurable checks, not visual impression** — "looks fine" is not a check
- **Exaggerate to detect** — temporarily make subtle features loud during QA
- **Artifacts are ephemeral** — bug reports live on the branch during the fix cycle, get removed after all bugs are verified
