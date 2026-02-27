---
name: ios-crash-diagnosis
description: "Expert guide and tools for diagnosing iOS crashes (EXC_BREAKPOINT, EXC_BAD_ACCESS, etc.). Use when: user provides a crash log, an app crashes in Firebase Crashlytics, or a TestFlight build crashes. Includes scripts for parsing crashes, querying BigQuery Crashlytics data, and checking Swift 6 actor isolation via SIL."
metadata:
  {
    "openclaw": {
      "emoji": "💥",
      "requires": {
        "bins": ["swiftc", "python3"]
      }
    }
  }
---

# iOS Crash Diagnosis Skill

Use this skill to diagnose and fix iOS crashes. Do not guess the root cause — follow the protocol.

## 🚨 MANDATORY DIAGNOSIS PROTOCOL

When handed an iOS crash log, you MUST follow these steps before writing any code:

1. **PARSE:** Extract the exception type, crashing thread, crashing frame, and source location. Use `scripts/parse-crash.sh <file>` if diagnosing a raw crash log.
2. **CLASSIFY:** Match the crash against the **Known Crash Patterns** below.
3. **VERIFY (Compiler Output):** If the crashing frame shows `<stdin>:0`, `<compiler-generated>`, or a closure thunk, the bug is likely in how the compiler transformed the code. Do not just change captures. Use `scripts/emit-sil.sh <file.swift>` to inspect the compiler's actual output.
4. **HYPOTHESIZE:** Write down exactly ONE hypothesis and the specific experiment that would confirm or refute it.
5. **TEST:** Apply the fix and run a targeted test (not a full app launch).
6. **ESCALATE:** If you fail 2 attempts with the same hypothesis class, you MUST explicitly state `"I've exhausted my understanding of this crash pattern"` and request human input or a different model (e.g., `model=o3-mini`). Do not blindly guess a third time.

---

## Known Crash Patterns

### 1. Swift 6 Actor Isolation (`_swift_task_checkIsolatedSwift`)
- **Signature:** `EXC_BREAKPOINT` + `_dispatch_assert_queue_fail` + `_swift_task_checkIsolatedSwift`
- **Source Location:** Usually `<stdin>:0` or `<compiler-generated>` runtime thunk
- **Root Cause:** A closure was **defined** inside a `@MainActor` lexical scope (e.g., a method on a SwiftUI View or `@MainActor` class), causing the Swift 6 compiler to inject a `@MainActor` check into the closure's thunk. When an external framework (like AVFoundation or a Timer) calls the closure on a background thread, the isolation check traps.
- **The WRONG Fix:** Adding `[weak self]` or `Unmanaged`. The compiler still annotates the thunk based on the *scope*, not the *captures*.
- **The RIGHT Fix:** Move the closure creation into a `nonisolated` scope (e.g., a free function or nonisolated static method) that returns the closure. Pass the nonisolated closure to the framework.

### 2. Main Thread API on Background Thread (UIKit/AVFoundation)
- **Signature:** `SIGABRT` or `EXC_BAD_INSTRUCTION` in `UIKitCore` (e.g., `[UIView setNeedsLayout]`)
- **Root Cause:** Calling a main-thread-only API from a detached Task or background queue.
- **Fix:** Wrap the specific call in `DispatchQueue.main.async { ... }` or `MainActor.assumeIsolated { ... }`.

### 3. SwiftData Concurrency Cross-Actor Transfer
- **Signature:** "sending X risks causing data races" (compile error) or `EXC_BAD_ACCESS` when accessing a `@Model` object across Tasks.
- **Root Cause:** Passing an isolated SwiftData model instance across actor boundaries.
- **Fix:** Extract primitive values (Strings, Ints, UUIDs) *before* the `Task {}` boundary and pass the primitives, not the model object.

---

## Tooling

These scripts are located directly inside the skill directory (`scripts/`). Resolve them explicitly: `$(dirname $(realpath $SKILL_PATH))/scripts/`.

### 1. Crashlytics / BigQuery
**Rule:** All iOS projects must use Firebase Crashlytics.
Use `query-crashes.py --project <gcp_project> --app <bundle_id>` to fetch real-time crash stacks for an app. It automatically handles GCP auth via the default workspace SA.

### 2. Parse Raw Crash Logs
Use `parse-crash.sh <crash.ips>` to extract the crashing thread, exception code, and failing frame in a readable format.

### 3. Check SIL (Swift Intermediate Language)
Use `emit-sil.sh <file.swift>` to dump the compilation output. Search the output for `hop_to_executor` to see if the compiler injected a MainActor check into your closure.

---

## Post-Fix Requirement

After fixing a crash, update `docs/ios/crash-patterns.md` (if it exists) with the signature and fix so the team learns from it.
