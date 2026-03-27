---
name: web-qa
description: "End-to-end QA pipeline for web projects using GitHub Issues as the bug tracker. Use when: (1) user reports visual or functional bugs with screenshots, (2) PR review comments describe broken behavior, (3) bugs found on main/Pages/any branch need systematic fixing, (4) you need structured triage, investigation, and independent verification of web issues. Covers the full cycle: triage → GitHub Issue → fix agent → independent verify agent → close with evidence. Web-focused: uses browser tool, DOM queries, computed styles, SVG geometry for measurable verification. NOT for: test-only changes, non-web platforms (use platform-specific skills), or greenfield feature work."
---

# Bug Fix — Web

Structured workflow for fixing web bugs using **GitHub Issues** as the single source of truth. Each bug goes through: **Triage → Issue → Fix → Verify → Close**.

## When This Triggers

- User sends screenshots of broken behavior (any branch, PR, or live Pages)
- GH review comments describe visual/functional regressions on a PR
- User reports a bug verbally (Slack, thread, DM) with or without screenshots
- Multiple bugs need systematic fixing on any branch

## Step 1: Triage

Read the user's bug reports (Slack messages, screenshots, GH comments, verbal descriptions). For each reported issue:

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

## Step 2: Create GitHub Issues

For each triaged bug, create a GitHub Issue with full context. **Attachments (screenshots, recordings) go directly on the issue** — never in the source tree or a side file.

### Issue Template

```
gh issue create \
  --repo <owner/repo> \
  --title "BUG: <short description>" \
  --label bug \
  --body "$(cat <<'EOF'
## Context

- **Source:** <where this was reported — PR #N / main branch / Pages / user report>
- **Branch:** <branch name, e.g. main, feature/charge-phase>
- **PR:** <#N if applicable, or "N/A">
- **Commit:** <SHA if known, or "HEAD">
- **URL:** <live URL if applicable, e.g. Pages link>
- **Reported by:** <name or "automated">

## Bug Description

<concrete, measurable description of what's wrong>

## Expected Behavior

<what should happen instead>

## Root Cause

- **File:** `<exact file path>`
- **Line/Symbol:** `<line number or function/class name>`
- **Mechanism:** <why it's broken — the actual code-level explanation>

## Acceptance Check

<measurable condition that proves it's fixed — a JS expression, DOM query, computed style check, or element count>

```js
// Example: element should be centered
const rect = document.querySelector('.target').getBoundingClientRect();
Math.abs((rect.left + rect.width/2) - window.innerWidth/2) < 2; // true
```

## Fix Approach

<specific code change needed>

## Screenshots / Attachments

<drag-and-drop screenshots directly here — they live on the issue, not in the repo>
EOF
)"
```

### Attaching Screenshots via CLI

**From Slack:** When the user reports bugs with screenshots in Slack, download them first:

```bash
# 1. Get the bot token
TOKEN=$(grep SLACK_BOT_TOKEN ~/.openclaw/.env | cut -d= -f2)

# 2. Get the private URL for a Slack file (file IDs are in the thread message metadata)
URL=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://slack.com/api/files.info?file=<FILE_ID>" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['file']['url_private'])")

# 3. Download using the private URL (NOT the /download/ variant)
curl -sL -H "Authorization: Bearer $TOKEN" "$URL" -o /tmp/screenshot.png
```

**Important:** Use `url_private` (not `url_private_download`) — the download variant returns 404 for some file types.

**Attaching to GitHub Issues:** `gh` CLI doesn't support image upload in issue comments. Workarounds:

1. **Link Slack public permalinks** (simplest — if the file has `permalink_public`):
   ```bash
   gh issue comment <N> --body "![screenshot](<slack-public-permalink-url>)"
   ```

2. **Upload via GitHub web UI** — drag-and-drop onto the issue in browser

3. **Reference by raw URL** — commit to a temp branch, link the raw GitHub URL, clean up after

**Key point:** Screenshots and evidence live on the GitHub Issue. Never commit them to the source tree. This keeps the repo clean and the bug context self-contained.

### Linking Issues to PRs

- If the bug is on a PR: mention `PR #N` in the Context section and comment on the PR linking to the issue
- If the bug is on main: just reference the branch/commit
- If the bug is from a user report: include the reproduction URL (Pages link, localhost port, etc.)

## Step 3: Fix

Spawn a sub-agent:

```
task: "Read these GitHub Issues: #X, #Y, #Z in <owner/repo>.
Fix each bug per the acceptance checks. One conventional commit per bug:
fix(scope): description (fixes #N). Push to <branch>.
Comment the fix commit SHA on each issue."
model: opus
```

The fix agent, for each bug:
1. Reads the issue (`gh issue view <N>`)
2. Implements the fix approach
3. Verifies locally against the acceptance check (measurable)
4. Commits with `fix(scope): description (fixes #<issue>)` — GitHub auto-links the commit
5. Pushes to the target branch
6. Comments on the issue with the commit SHA: `gh issue comment <N> --body "Fix committed: <SHA>"`

## Step 4: Verify

Spawn a **separate** sub-agent — not the same one that fixed:

```
task: "Verify fixes for GitHub Issues #X, #Y, #Z in <owner/repo>.
For each issue, read the acceptance check, serve the app locally,
and verify using browser tool. Comment PASS or FAIL with measurable
evidence on each issue."
model: opus
```

The verify agent, for each bug:
1. Reads the issue to get the acceptance check
2. Serves the web app locally (`python3 -m http.server` or project dev server)
3. Opens in browser, navigates to the bug's context
4. Runs the measurable check:
   - DOM queries (`document.querySelectorAll('.class').length`)
   - Computed styles (`getComputedStyle(el).opacity`)
   - SVG geometry (`el.getBBox()`, `el.getScreenCTM()`)
   - Layout measurements (`el.getBoundingClientRect()`)
   - Element counts, class presence, attribute values
5. For subtle visual issues: temporarily exaggerate the suspect feature (red outlines, high opacity, center guides) to confirm, then remove
6. Comments on the issue:
   - `✅ VERIFIED` with evidence (exact values, screenshot if needed)
   - or `❌ FAILED` with what's still wrong

**Why a separate agent:** The fixer has confirmation bias. An independent verifier catches failures the fixer missed.

## Step 5: Handle Failures

For any `❌ FAILED` from the verify agent:

1. Read the failure comment on the issue
2. Diagnose the real root cause (often different from the original hypothesis)
3. Update the issue body with the revised root cause and fix approach
4. Either fix directly (if small) or re-spawn a fix agent for just the failed issues
5. Re-spawn a verify agent for just the re-fixed issues
6. Repeat until all `✅ VERIFIED`

## Step 6: Close

After ALL bugs are verified:

1. Close each issue — `gh issue close <N> --comment "Verified and closed. Fix: <SHA>"`
   - GitHub auto-closes if commit message had `fixes #N`, but verify it happened
2. If bugs were from a PR, update the PR description with final summary:

```markdown
## Bugs Fixed
- #<issue>: <description> — <commit SHA>
- #<issue>: <description> — <commit SHA>

## Verification
- All bugs independently verified via browser automation
- <specific evidence summary>
```

3. Post result to user (Slack/thread)

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

- **GitHub Issues are the bug tracker** — no markdown files, no `bug-reports/` directories
- **Attachments live on issues** — screenshots, recordings, evidence — never in the source tree
- **Any source, any branch** — works for PR reviews, main branch bugs, Pages bugs, user reports
- **Don't guess when the bug report is unclear** — ask the user
- **One bug per issue, one bug per commit** — easy to track, easy to revert
- **Fix and verify are always separate agents** — eliminates confirmation bias
- **Measurable checks, not visual impression** — "looks fine" is not a check
- **Agents update issues as they go** — investigating → fix committed → verified → closed
- **Commit messages link to issues** — `fixes #N` for auto-close, SHA in comments for traceability
