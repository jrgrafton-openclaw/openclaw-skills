---
name: ios-crash-diagnosis
description: "Expert guide and tools for diagnosing iOS crashes (EXC_BREAKPOINT, EXC_BAD_ACCESS, etc.). Use when the user provides a crash log, an app crashes in Firebase Crashlytics, or a TestFlight build crashes. Includes scripts for parsing crashes, querying BigQuery Crashlytics data, and checking compiler-generated isolation behavior via SIL."
---

# iOS crash diagnosis

Do not guess the root cause. Follow the protocol.

## Mandatory diagnosis protocol

1. **Parse** the crash log.
2. **Classify** it against a known crash pattern.
3. **Check compiler output** if the frame points to `<stdin>:0`, `<compiler-generated>`, or a thunk.
4. **Write one hypothesis** and the smallest experiment that will prove or disprove it.
5. **Test the fix** with a targeted verification step.
6. **Escalate after two failed attempts in the same hypothesis class.** Do not keep guessing.

## Known high-value patterns

### Swift 6 actor-isolation thunk crash

Signature:
- `EXC_BREAKPOINT`
- `_dispatch_assert_queue_fail`
- `_swift_task_checkIsolatedSwift`
- source often `<stdin>:0` or `<compiler-generated>`

Root cause:
- a closure was defined inside a `@MainActor` lexical scope, so the compiler injected an actor isolation check into the generated thunk

Correct fix:
- move closure creation to a `nonisolated` scope
- do **not** assume `[weak self]` or capture changes fix it

See `references/compiler-generated-thunks.md`.

### Main-thread-only API called from background thread

Signature:
- `SIGABRT` / `EXC_BAD_INSTRUCTION` in UIKit / AVFoundation UI code

Fix:
- move the specific UI call back to main

### SwiftData cross-actor transfer

Signature:
- sendability errors or runtime crashes when a `@Model` crosses task boundaries

Fix:
- extract primitives before crossing the boundary

## Tooling

- `scripts/parse-crash.sh <file>` — summarize raw crash logs
- `scripts/query-crashes.py --project <gcp_project> --app <bundle_id>` — fetch recent Crashlytics events
- `scripts/emit-sil.sh <file.swift>` — inspect compiler output for generated isolation behavior

## Post-fix

After fixing a recurring crash pattern, update the project crash-patterns reference if one exists.
