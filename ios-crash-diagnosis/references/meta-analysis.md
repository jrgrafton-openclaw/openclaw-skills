# Meta-Analysis: Why Prior Models Failed & How to Fix Crash Diagnosis

_Written 2026-02-27. Context: SingCoach Build 74 → Build 76 crash resolution._

---

## 1. What Actually Happened (The Case Study)

Two `EXC_BREAKPOINT` crashes kept recurring across ~10+ builds. Both had the same root cause:

- **Crash A:** `PitchDetectionService.start()` — `installTap` closure called on AVFAudio's dispatch queue
- **Crash B:** `ToneGeneratorService.play()` — `AVAudioSourceNode` render block called on the audio IO thread

The crash stack was unambiguous: `_dispatch_assert_queue_fail` → `_swift_task_checkIsolatedSwift` → user closure. Every prior model correctly identified "MainActor isolation on a background thread." None of them fixed it.

**What was actually wrong:** The Swift 6 compiler injects a `@MainActor` isolation check into the *compiler-generated thunk* based on the **lexical scope** where a closure is defined. If you write a closure inside a `@MainActor` method, the thunk gets an isolation assertion — regardless of what the closure captures. Every prior fix focused on captures (`[weak self]`, `Unmanaged`, wrapper types). The fix was moving closure creation into `nonisolated` free functions.

---

## 2. Why Prior Models Failed (Abstract Analysis)

This wasn't a failure of one model on one bug. It represents a **class of failure** that affects AI coding agents broadly. The failure modes are:

### 2.1 Pattern-Matching Without Mechanistic Understanding

LLMs pattern-match against training data. The overwhelming majority of "MainActor crash on background thread" examples in training data are solved by removing `@MainActor` annotations, adding `[weak self]`, or dispatching to main. Models applied these patterns reflexively.

The actual mechanism — **compiler thunk generation based on lexical scope** — is a compiler implementation detail that exists in Swift compiler source code and very few blog posts. It's not a "common pattern" — it's an edge case in how Swift's concurrency annotations interact with closures. Models lack the ability to reason about what the *compiler does to their code* after they write it.

**General principle:** AI agents fail on bugs where the root cause is in the *toolchain's transformation of source code*, not in the source code itself. Other examples:
- C++ template instantiation errors
- Rust lifetime elision surprising behavior
- ObjC message dispatch with Swift bridging
- Webpack/bundler tree-shaking removing apparently-used code

### 2.2 Context Pollution from Repeated Failed Attempts

Each failed fix attempt adds noise to the conversation. By attempt 5, the context window contains:
- 5 different "here's what I think is wrong" analyses (all similar, all wrong)
- 5 different code patches (all variations on captures)
- Crash logs that look identical each time
- Growing frustration from the user

The model effectively learns *within the session* that "captures are the problem" because that's what dominates its context. Each new attempt is a minor variation of the same wrong idea. **There's no mechanism for the model to say "I've exhausted my understanding of this domain and need external help."**

**General principle:** Long debugging sessions create a self-reinforcing echo chamber in the context window. The model's confidence increases while its solution diversity decreases.

### 2.3 Inability to Read Compiler Output at the Right Level

The crash gave a perfect signal: `<stdin>:0` as the source location for the crashing frame. This means the code was *compiler-generated* (not from any `.swift` file the model wrote). A human with deep Swift expertise would recognize this as "the compiler synthesized this closure thunk" and investigate *how* the compiler wraps closures.

Models treated `<stdin>:0` as an unsymbolicated artifact rather than a diagnostic signal. They never asked "what does the compiler actually emit for this closure?"

**General principle:** Crash logs contain metadata signals (source locations, thunk names, frame patterns) that encode information about *how the binary was produced*. Models read crash logs at the "which function crashed" level, not at the "what does this frame pattern tell me about compilation" level.

### 2.4 No Feedback Loop from the Binary

The model writes code, but never inspects what the compiler actually produced. It couldn't run:
```bash
swiftc -emit-sil MyFile.swift  # See the Swift Intermediate Language
otool -tV MyBinary             # Disassemble the binary
swift demangle 's5SingCoach...' # Demangle the symbol name
```

Without seeing the SIL or compiled output, the model is debugging a *mental model* of what the compiler produces, not the *actual artifact*.

**General principle:** Bugs that exist in the gap between "what the source says" and "what the binary does" are invisible to agents that only read/write source code.

---

## 3. Critical Evaluation of Your Ideas

### 3.1 Aider-Style Tool Calls for File Editing (Fresh Context)

**Your idea:** Use Aider's approach — a separate tool/process that reads the file fresh, applies the edit, and returns the result — instead of inline edits in the conversation.

**Verdict: Partially helpful, but doesn't address the core failure.**

Aider's `edit` format is excellent for *applying* known fixes accurately. Its repo-map feature provides good context selection. But the failure here wasn't "the model couldn't apply its fix cleanly" — it was "the model didn't know what fix to apply." The diagnosis was wrong, not the edit mechanics.

Where Aider-style tooling *would* help:
- **Repo map** gives the model a condensed view of the codebase structure without loading every file. This reduces context pollution.
- **Fresh file reads** per edit prevent stale-context bugs where the model thinks a file contains code from 3 patches ago.
- **Atomic edit → build → test cycles** with context resets between attempts would prevent the echo chamber problem (§2.2).

**Recommendation:** Yes, but frame it as "fresh-context debugging cycles" rather than "better edit mechanics." The key insight from Aider is the repo map and the ability to selectively include files — not the edit format itself. OpenClaw already has `read`/`edit` tools that accomplish similar things. What's missing is a **structured retry protocol** that clears failed-attempt context between debugging cycles.

### 3.2 New Skills for iOS SWE Agents

**Your idea:** Create installable skills (`.md` + shell scripts, possibly MCP servers) that can be shared across all iOS-focused sub-agents.

**Verdict: This is the highest-impact recommendation. Do this.**

The crash diagnosis failure is fundamentally a *knowledge gap*, not a tooling gap. A skill can inject the right knowledge at the right time. Specifically:

#### Proposed Skill: `ios-crash-diagnosis`

**Format:** SKILL.md + shell scripts (the current OpenClaw skill format is proven and doesn't need MCP overhead).

**Contents:**

1. **`SKILL.md`** — Decision tree for iOS crash triage:
   - `EXC_BREAKPOINT` + `_swift_task_checkIsolatedSwift` → Actor isolation crash. Check if the crashing closure was *defined* in a `@MainActor` context. The fix is to move closure creation to a `nonisolated` scope, NOT to change captures.
   - `EXC_BREAKPOINT` + `swift_dynamicCast` → Type cast failure
   - `EXC_BAD_ACCESS` → Memory corruption / use-after-free
   - `SIGABRT` + `NSInternalInconsistencyException` → UIKit threading violation
   - etc.

2. **`scripts/parse-crash.sh`** — Takes a `.crash` / `.ips` file, extracts:
   - Exception type and codes
   - Crashing thread + its full stack
   - Whether the crashing frame is `<stdin>:0` (compiler-generated)
   - Key system frames that indicate the crash class
   - Outputs a structured JSON summary with a preliminary diagnosis

3. **`scripts/check-isolation.sh`** — Given a Swift file and method name, runs `swiftc -emit-sil` (or `swift-frontend -emit-sil`) to check whether the compiler annotated the closure's thunk with `@MainActor` isolation. This is the "read the compiler output" step models skip.

4. **`scripts/query-crashes.sh`** — Wraps the BigQuery query from `docs/ios/crashlytics.md` to pull recent crashes for a given app. Agents shouldn't need to construct SQL from scratch each time.

5. **Reference patterns** — The `nonisolated` free function pattern, the `Sendable` closure pattern, the `Task.detached` pattern, etc. Pre-written, tested, ready to paste.

**Why .md + shell scripts, not MCP:**
- OpenClaw skills are already this format and they work well
- MCP adds a runtime dependency (server process), transport complexity, and is still evolving (OpenClaw MCP support is in feature-request stage per GitHub issues #4834, #8188, #13248)
- Shell scripts are universally debuggable, version-controllable, and zero-dependency
- The skill format already supports sub-agent distribution via OpenClaw's skill install mechanism

**When MCP makes sense:** If you eventually want to expose Xcode's build system, Instruments data, or Crashlytics queries as a *live service* that multiple agents connect to simultaneously. That's a valid future state, but premature today. Start with scripts, graduate to MCP when the use case demands it.

#### Proposed Skill: `ios-swift6-concurrency`

Focused reference for the most common Swift 6 / iOS 26 concurrency pitfalls:
- Actor isolation inheritance in closures (the exact bug we just fixed)
- `Sendable` conformance for model types
- `nonisolated` escape hatches and when to use them
- SwiftData cross-actor transfer patterns
- Audio/video callback patterns that must be nonisolated
- Testing patterns (`Task.detached` tests that verify no isolation crash)

This skill would be loaded by any sub-agent working on an iOS project with Swift 6 strict concurrency enabled.

### 3.3 Split WebTech SWE and iOS-Build Into Separate Workspaces

**Your idea:** Reduce context bloat by giving different agent types their own workspaces.

**Verdict: Nuanced. Split *agent roles*, not workspaces.**

**Arguments for splitting:**
- The current workspace has `docs/web/`, `docs/ios/`, `projects/SingCoach/`, `projects/spend-dashboard/` — a web-focused sub-agent loading iOS lessons-learned is pure noise
- AGENTS.md, MEMORY.md, lessons-learned.md are large and growing — they consume significant context budget on every session
- Sub-agents spawned for iOS tasks don't need web deploy docs, and vice versa

**Arguments against splitting *workspaces*:**
- Some tasks are cross-cutting (e.g., Firebase config touches both web and iOS)
- Memory fragmentation — you'd need to sync MEMORY.md across workspaces or lose cross-project context
- Operational overhead of managing multiple workspace repos, git histories, memory files
- The calv.info article makes a good point: "splitting separate agents increases coordination overhead and context duplication"

**What to do instead — the two-layer context model:**

#### Layer 1: In-Repo `CLAUDE.md` / `AGENTS.md` (checked into each project's GitHub repo)

This is the SOTA approach and I was wrong to suggest keeping project context only in the workspace. **Every project repo should have its own `CLAUDE.md` (or `AGENTS.md`) at the project root, checked into git.** This is the emerging industry standard:

- **Claude Code** reads `CLAUDE.md` from the project root automatically at session start
- **Cursor, Codex, Cline, Zed, OpenCode** all read `AGENTS.md` from the project root
- **OpenClaw sub-agents** that `cd` into a project directory can `read CLAUDE.md` as their first step
- It lives *with the code it describes*, so it stays in sync with refactors, renames, and architecture changes
- It's versioned alongside the code — `git blame` shows when context changed and why
- Any developer or agent, on any machine, with any tool, gets the same context
- It follows the "progressive disclosure" pattern: the agent discovers project context when it enters the project, not upfront

**What goes in the project-root `CLAUDE.md`:**
```markdown
# SingCoach

One-sentence: iOS vocal coaching app with AI analysis, pitch detection, and tone generation.

## Architecture
- SwiftUI + SwiftData + AVFoundation + Firebase AI Logic (Vertex AI)
- Key services: PitchDetectionService, ToneGeneratorService, GeminiAnalysisService
- Audio callbacks MUST be nonisolated (see AudioCallbacks.swift) — Swift 6 compiler
  injects @MainActor thunk checks based on lexical scope, not captures

## Build & Ship
- `bundle exec fastlane beta` — never xcodebuild directly
- Crashlytics dSYM: SKIP_CRASHLYTICS_DSYM_UPLOAD=1 in xcodebuild env

## Known Gotchas
- Gemini 3.x models require `location: "global"` not default us-central1
- SwiftData models must not cross actor boundaries — extract primitives first
- See docs/ in this repo for detailed patterns
```

**What does NOT go in `CLAUDE.md`:**
- Personal preferences (those stay in the workspace `AGENTS.md` / `SOUL.md`)
- Cross-project memory (stays in workspace `MEMORY.md`)
- Operational secrets / API keys (stay in workspace `TOOLS.md` or secrets)

**Relationship to workspace `docs/ios/projects/singcoach.md`:**
The workspace doc (`docs/ios/projects/singcoach.md`) should become a *mirror or superset* of what's in the project's `CLAUDE.md`, plus any workspace-specific context (ASC IDs, Firebase project IDs, TestFlight group IDs) that the main session needs but that doesn't belong in the public repo. Over time, the workspace doc can thin out as the in-repo `CLAUDE.md` becomes the source of truth.

**Symlink for tool compatibility:**
```bash
# In the project root — both Claude Code and AGENTS.md-aware tools work
ln -s CLAUDE.md AGENTS.md
```

#### Layer 2: Workspace-Level Context Scoping (OpenClaw-specific)

The workspace `AGENTS.md` remains the orchestrator's context — identity, memory rules, safety, heartbeat config. It does NOT need project-specific architecture details if those live in the project repo.

**How scoping actually works in OpenClaw today:**
- Skills are loaded based on the `<available_skills>` list and matched by task description — the agent picks the relevant skill. This is already task-scoped, not globally loaded.
- Sub-agents spawned via `sessions_spawn` get a `task` prompt. The task prompt should say "read CLAUDE.md in the project root first" — this is the scoping mechanism. It's explicit, not automatic.
- The workspace `AGENTS.md` is injected into every session. To keep it lightweight, move project-specific details *out* of it and into the in-repo `CLAUDE.md` files.

**"Role-scoped AGENTS.md files" — correction:** My original recommendation to create `AGENTS-ios.md` / `AGENTS-web.md` was solving the wrong problem. The OpenClaw workspace `AGENTS.md` gets injected into every session regardless of filename — there's no built-in mechanism to load different workspace files per agent role. The real solution is:
1. Keep workspace `AGENTS.md` lean (identity, safety, memory protocol — ~50 lines)
2. Put project context in the project repo's `CLAUDE.md`
3. Sub-agent task prompts say "cd to project dir, read CLAUDE.md, then work"

**"Scoped skill loading" — correction:** Skills aren't globally loaded either. The system presents available skills; the agent reads at most one SKILL.md based on task match. This is already scoped. The improvement is to *create better skills* (like `ios-crash-diagnosis`), not to change the loading mechanism.

#### Aggressive memory curation

MEMORY.md is 80+ lines and growing. Keep it to: project IDs, current state (one line each), cross-cutting decisions. Move everything else to project-specific docs or the in-repo `CLAUDE.md`. The current MEMORY.md already does this reasonably well but will need periodic pruning.

**Bottom line:** The SOTA pattern is a **two-layer system**: lean workspace `AGENTS.md` for orchestration + rich in-repo `CLAUDE.md` for project context. The workspace doc provides identity and memory; the project doc provides architecture and build knowledge. Sub-agents discover project context by reading the `CLAUDE.md` in the directory they're working in — not by having it injected upfront.

#### Immediate Action Items

1. **Create `CLAUDE.md` in `projects/SingCoach/` root** — architecture, build commands, known gotchas, audio callback pattern
2. **Symlink `AGENTS.md → CLAUDE.md`** in the same directory for tool compatibility
3. **Push to GitHub** so it's available to any agent cloning the repo
4. **Thin out `docs/ios/projects/singcoach.md`** to reference the in-repo `CLAUDE.md` + workspace-only IDs
5. **Repeat for any future project** (Language Transfer, spend-dashboard, etc.)

---

## 4. My Own Recommendations

Beyond evaluating your ideas, here are additional recommendations based on this incident:

### 4.1 Structured Crash Diagnosis Protocol

Create a mandatory protocol that any agent follows when handed a crash log. The current approach is ad-hoc: model reads crash, guesses, edits code, builds, repeat.

**Proposed protocol (embed in skill or AGENTS.md):**

```
CRASH DIAGNOSIS PROTOCOL:
1. PARSE: Extract exception type, crashing thread, crashing frame, source location
2. CLASSIFY: Match against known crash patterns (skill decision tree)
3. VERIFY: If the crashing frame shows <stdin>:0 or <compiler-generated>, 
   investigate compiler output (swift -emit-sil) before touching source code
4. HYPOTHESIZE: Write down exactly ONE hypothesis and the specific experiment 
   that would confirm or refute it
5. TEST: Run the experiment (build + specific test, not full app launch)
6. If FAILED after 2 attempts with the same hypothesis class: 
   ESCALATE — explicitly state "I've exhausted my understanding of this crash 
   pattern" and request human input or a different model
```

Step 6 is critical. The SingCoach crash went through 5+ failed attempts because no model ever said "I don't actually understand why this is happening." The escalation protocol prevents the echo chamber.

### 4.2 Build-Test-Diagnose Scripts (Not Just Build-Ship Scripts)

The current `docs/ios/` tooling is heavily focused on *shipping* (Fastlane, TestFlight, provisioning). There's almost nothing for *diagnosis*. Add:

- **`scripts/emit-sil.sh <file>`** — Runs `swift-frontend -emit-sil` on a file with the project's build settings. Outputs the SIL so the agent can see compiler-generated isolation checks.
- **`scripts/reproduce-crash.sh <test_name>`** — Runs a specific test that's known to reproduce a crash pattern. For the audio isolation crash, this would be `AudioCallbackIsolationTests`.
- **`scripts/diff-crash-stacks.sh <crash1> <crash2>`** — Compares two crash files and highlights what changed (did the fix actually change the crash site, or is it the same crash?).

### 4.3 "What Changed" Discipline for Iterative Debugging

When a fix doesn't work, the agent should be required to explain:
1. What specifically it changed
2. What it expected to happen
3. What actually happened (new crash? same crash? different crash?)
4. What this rules out

Currently, agents just try the next variation without learning from the failure. A structured "what changed" log (written to a file, not just conversation) would:
- Prevent repeating the same fix
- Build a cumulative elimination of hypotheses
- Provide context for a fresh sub-agent or human taking over

### 4.4 Escalation to Specialized Models

Not all models are equal at all tasks. The crash diagnosis here required:
- Understanding compiler internals (rare in training data)
- Reasoning about code transformations (not just code patterns)
- Breaking out of a failed hypothesis (metacognition)

**Recommendation:** When a sub-agent fails twice on a crash fix, escalate to a thinking-enabled model (e.g., o3/o4-mini with extended thinking, or Claude with thinking enabled). The cost is higher but the alternative is 10 failed builds at $X each plus human time.

The OpenClaw `sessions_spawn` system already supports model selection. Codify this: "crash diagnosis escalation uses model X with thinking enabled."

### 4.5 Pre-Flight Crash Knowledge Base

Maintain a living document (`docs/ios/crash-patterns.md`) that maps crash signatures to root causes and fixes. Every time a crash is resolved, add an entry:

```markdown
## `_swift_task_checkIsolatedSwift` on audio thread
- **Signature:** EXC_BREAKPOINT + _dispatch_assert_queue_fail + _swift_task_checkIsolatedSwift
- **Source location:** <stdin>:0 or <compiler-generated>
- **Root cause:** Closure defined in @MainActor scope inherits isolation in compiler thunk
- **Fix:** Move closure creation to nonisolated free function
- **See:** docs/ios/lessons-learned.md §57-58, AudioCallbacks.swift
```

This becomes a lookup table for future crashes. It's faster and more reliable than the model reasoning from first principles every time.

---

## 5. Priority-Ordered Action Items

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | **Add `CLAUDE.md` to every project repo root** (SingCoach first, then others) — architecture, build, gotchas. Symlink `AGENTS.md`. Push to GitHub. | 🔴 High | Low |
| 2 | Create `ios-crash-diagnosis` skill (SKILL.md + parse-crash.sh + decision tree) | 🔴 High | Medium |
| 3 | Create `docs/ios/crash-patterns.md` knowledge base, seed with all known crashes | 🔴 High | Low |
| 4 | Add crash diagnosis protocol to AGENTS.md (or as a skill preamble) | 🔴 High | Low |
| 5 | Create `ios-swift6-concurrency` skill with audio callback patterns | 🟡 Medium | Medium |
| 6 | Add `emit-sil.sh` diagnostic script to project | 🟡 Medium | Low |
| 7 | Thin workspace `AGENTS.md` — move project-specific context to in-repo `CLAUDE.md` files | 🟡 Medium | Low |
| 8 | Add escalation protocol: 2 failed fixes → thinking model | 🟡 Medium | Low |
| 9 | Prune MEMORY.md quarterly; move stale entries to project docs | 🟢 Low | Low |
| 10 | Evaluate MCP for live Crashlytics/Xcode integration (future) | 🟢 Low | High |
| 11 | Evaluate Aider-style repo-map for large project navigation (future) | 🟢 Low | High |

---

## 6. Summary

The SingCoach crash wasn't hard because the models were bad. It was hard because it required understanding *compiler behavior* that isn't in the source code. The fix requires three things:

1. **Better knowledge injection** — Skills that encode crash pattern → diagnosis → fix mappings, so models don't have to reason from first principles about compiler internals they don't understand.

2. **Better diagnostic tooling** — Scripts that let agents inspect compiler output (SIL), not just source code. If the agent could see the `@MainActor` annotation in the emitted thunk, it would've solved this in one attempt.

3. **Better failure discipline** — Structured protocols that prevent the echo chamber of "try another capture variation." Escalation after 2 failures. Mandatory hypothesis logging.

The workspace structure is fine as-is. The problem isn't context bloat — it's context *relevance*. Scope what each agent sees, don't split the workspace.

---

_This document should be reviewed and updated after the next significant crash investigation to validate whether these recommendations improved outcomes._
