---
name: ios-swift6-concurrency
description: "Reference for solving Swift 6 concurrency errors: sendability, actor isolation, and callback/threading traps. Use when the compiler throws sendability/data-race errors, a closure traps on a background thread, or you need to fix @MainActor isolation bugs in modern iOS projects. Use ios-crash-diagnosis when you are starting from a crash log rather than a compiler/runtime pattern."
---

# Swift 6 concurrency patterns

Use this skill for compiler/runtime concurrency issues in iOS code.

## 1. Audio/video callback isolation trap

If a framework callback runs on a background or realtime thread, do not define that closure inside a `@MainActor` scope.

Wrong fix:
- changing captures only

Right fix:
- create the closure in a `nonisolated` function or static helper
- hop back to main only for the UI update

See `references/audio-callback-pattern.md`.

## 2. SwiftData / model sendability

Do not pass model objects across actor/task boundaries.

Correct pattern:
- extract primitives (`URL`, `String`, `Bool`, IDs, etc.) before entering the task

## 3. Thread hopping

- use `DispatchQueue.main.async` when returning from strict callback threads
- use `MainActor.assumeIsolated` only when you truly know you are already on main
- avoid casual `Task { @MainActor in ... }` inside strict realtime callbacks

## 4. Protocol conformance on background callbacks

If a system delegate/callback enters on a background queue but the owning type is `@MainActor`, make the callback `nonisolated` and forward onto main safely.
