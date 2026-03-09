---
name: sub-agents
description: "Orchestrate sub-agent sessions via sessions_spawn for long-running, parallel, or isolated tasks. Use when a task has 5+ well-defined steps that can run independently, you need parallel workstreams (e.g. implement a phase while continuing conversation), or context would be polluted by a large inline implementation. NOT for quick tasks (under 5 min), tasks needing clarification, or when gateway operator.write scope is unconfirmed."
---

# Sub-Agent Orchestration

## Spawn Decision

Spawn when: isolated task, clear acceptance criteria, full context can be written up front.  
Do inline when: needs clarification, fast (under 5 min), or result feeds immediately into next step.

## `thread: true` — Platform Support Warning

**⚠️ Slack limitation:** Thread-bound sub-agent routing is **not supported on Slack**. Passing `thread: true` will spawn the agent fine, but you'll see:

> *"The sub-agent spawned but the routing hooks aren't available on this channel — it'll run but I won't get an auto-report."*

This is a known OpenClaw platform gap — Discord has `session.threadBindings.*` hooks but Slack's equivalent doesn't exist yet. Tracked at: **https://github.com/openclaw/openclaw/issues/23414**

**On Discord / Telegram** (threaded surfaces that support hooks) — always pass `thread: true`:

```ts
sessions_spawn({
  task: "...",
  mode: "run",
  thread: true,          // ← routes result back to THIS thread, not main channel
  runTimeoutSeconds: 600,
})
```

**On Slack** — omit `thread: true`. Poll manually when needed:

```ts
sessions_spawn({
  task: "...",
  mode: "run",
  // no thread: true — hooks not available on Slack
  runTimeoutSeconds: 600,
})
```

After spawning on Slack: use `subagents(action=list)` → `sessions_history` to check status, then manually post results back to the channel.

## Pre-flight: Gateway Scope Check

Sub-agents require `operator.write`. If you haven't spawned one successfully this session:

```bash
node ~/.openclaw/lib/node_modules/openclaw/dist/index.js devices list
# Scopes must include: operator.write
```

**If `operator.write` is missing** (error 1008 "pairing required"):
1. Edit `~/.openclaw/devices/paired.json` — add `"operator.write"` to device `scopes` and `tokens.operator.scopes`
2. `launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist && sleep 2 && launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist`
3. Verify: `devices list` → scopes now include `operator.write`

This is a one-time fix. Once applied, sub-agents work permanently until device is re-paired.

## Writing Good Task Descriptions

Sub-agents start cold — no session history. Include:

- **What's already done** (files created, decisions made, current state)
- **What to build** (explicit file paths, interfaces, method signatures)
- **Acceptance criteria** (tests passing, build succeeds, specific outputs)
- **Key constraints** (package deps, no external deps, TypeScript strict mode, etc.)
- **Where to report** — "REPORT results when done: test count, any issues"

Bad: `"Implement the shooting phase"`  
Good: `"Implement v0.4 shooting phase for WH40K engine at /path/to/repo. Engine already has SHOOT action stubbed. Add EngineWeapon to BlobUnit, implement hit/wound/save/damage pipeline using transcript events HIT_ROLL/WOUND_ROLL/SAVE_ROLL/DAMAGE_APPLIED/UNIT_DESTROYED. Run pnpm test (target 145+). Build must pass. Commit + tag v0.4.0."`

## Handling Results — MANDATORY VERIFICATION

**⚠️ Sub-agents fabricate completion reports.** They will claim "done, CI passed, files deployed" when:
- Files were written to `/tmp` but `git push` failed (auth, remote conflict, rate limit)
- The task timed out mid-write and the agent composed a summary of what it *intended* to do
- Git committed locally but never pushed

**NEVER trust a sub-agent's self-report. Always verify before telling the user.**

### Verification checklist (run EVERY time a sub-agent reports done):

```bash
# 1. Check if the file actually exists at the deployed URL
curl -sI "https://[expected-url]" | grep "HTTP"
# Must be 200, not 404

# 2. Check CI — does the latest run match the sub-agent's commit?
gh run list --repo [owner/repo] --limit 3
# The commit message should match what the sub-agent claimed to push

# 3. If 404 or CI doesn't match: check /tmp for written-but-not-pushed files
ls /tmp/[workdir]/[expected-file] 2>&1
# If file exists locally but wasn't pushed, push it yourself
```

**If verification fails:** Build the deliverable yourself inline. Do NOT spawn another sub-agent for the same task — it will likely fail the same way.

### Common failure modes (observed):

| Symptom | Root cause | Fix |
|---|---|---|
| Agent reports "pushed + CI green" but URL is 404 | `git push` failed silently (remote conflict, auth) | Pull, rebase, push manually |
| Agent reports files committed but CI shows old commit | Agent committed locally but push rejected | `cd /tmp/[workdir] && git pull --rebase && git push` |
| Agent wrote 2 of 3 files then reported all 3 done | Token/time limit hit mid-task | Build remaining file(s) yourself |
| HTML has broken DOM structure (stray tags) | Agent's removal script left orphan closing tags | Validate HTML structure before pushing |

### Task sizing (prevent failures):

- **1 large HTML file per sub-agent** — never ask for 3 full mockups in one run
- **Budget: ~60KB output max** — beyond this, token limits cause silent truncation
- **Prefer incremental tasks:** "Take v0.11.html, make these 5 specific changes" > "Build v0.12 from scratch"
- **Always include git verification in the task:** end with `curl -sI [url] | grep HTTP` and `gh run list`

## Steering / Killing

```ts
subagents({ action: "list" })                        // see active runs
subagents({ action: "steer", target: "<key>", message: "..." })  // redirect mid-run
subagents({ action: "kill",  target: "<key>" })      // abort
```

Use `steer` when requirements change mid-run. Use `kill` when the task is clearly wrong-headed.
