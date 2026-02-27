---
name: ios-swift6-concurrency
description: "Reference for solving Swift 6 concurrency errors: sendability, actor isolation, and callbacks. Use when: compiler throws 'sending X risks causing data races', a closure traps on a background thread, or you need to fix '@MainActor' isolation bugs in iOS 26+ projects. Includes the critical AudioCallback pattern."
metadata:
  {
    "openclaw": {
      "emoji": "🚦"
    }
  }
---

# Swift 6 Concurrency Patterns

Use this skill to fix Swift 6 concurrency errors and strict concurrency crashes in iOS projects.

## 1. The Audio/Video Callback Crash (`_swift_task_checkIsolatedSwift`)

**The Problem:**
You pass a closure to `AVAudioEngine`, `AVAudioSourceNode`, or a `Timer` that will be invoked on a background thread. If you define this closure inside a `@MainActor` method, the Swift 6 compiler explicitly injects a `@MainActor` check into the generated thunk, even if you never capture `self`. It will crash at runtime with `EXC_BREAKPOINT`.

**The WRONG Fix (Do NOT do this):**
```swift
// Still crashes! The *lexical scope* is what makes the compiler inject the check.
input.installTap(...) { [weak self] buffer, time in ... }
```

**The RIGHT Fix:**
Move the closure creation to a `nonisolated` free function or `nonisolated` static method:

```swift
// 1. In a nonisolated context (e.g. AudioCallbacks.swift)
nonisolated func makeAudioTapHandler(
    sampleRate: Double,
    handler: @escaping @Sendable ([Float], Double) -> Void
) -> ((AVAudioPCMBuffer, AVAudioTime) -> Void) {
    return { buffer, _ in
        // Process buffer on the audio thread...
        DispatchQueue.main.async { handler(samples, sampleRate) }
    }
}

// 2. In your @MainActor class
let tapHandler = makeAudioTapHandler(sampleRate: 44100) { samples, sr in
    MainActor.assumeIsolated {
        self.handleSamples(samples)
    }
}
input.installTap(onBus: 0, bufferSize: 1024, format: format, block: tapHandler)
```

## 2. Model "Sending risks causing data races" (SwiftData)

**The Problem:**
`@Model` objects (like `Lesson` or `Song`) are not `Sendable`. Passing them into a detached task, a network upload service, or a background process triggers a Swift 6 error: "sending X risks causing data races".

**The WRONG Fix:**
Marking the `@Model` class `@unchecked Sendable` (this violates SwiftData threading rules and causes crashes).

**The RIGHT Fix:**
Extract structural/primitive types *before* crossing the actor boundary:

```swift
// DO NOT DO THIS:
Task {
    // Error: sending non-Sendable 'lesson'
    await analysisService.analyze(lesson: lesson)
}

// DO THIS:
let audioURL = lesson.audioFileURL
let isPerformance = lesson.isPerformance
Task {
    // Allowed: URL and Bool are Sendable
    await analysisService.analyze(audioURL: audioURL, isPerformance: isPerformance)
}
```

## 3. Hopping Threads properly

SwiftUI requires `@MainActor`. Non-UI tasks require background threads. Do not mix them improperly.

```swift
// Bad: Using uncontrolled Task inside an audio thread callback (crashes!)
Task { @MainActor in self.updateUI() }

// Good: Safely dispatching back to main from an unknown strict-C thread
DispatchQueue.main.async { self.updateUI() }

// Good: Synchronous main-actor assumption (if you ALREADY KNOW you are on main)
MainActor.assumeIsolated { self.updateUI() }
```

## 4. `nonisolated func` for Protocol Conformance

If a system protocol (like `SFSpeechRecognizerDelegate`) callback comes on a background thread, but your class is `@MainActor`:

```swift
// Fails or crashes depending on context
func speechRecognizer(_ authStatus: SFSpeechRecognizerAuthorizationStatus) { ... }

// Fix
nonisolated func speechRecognizer(_ authStatus: SFSpeechRecognizerAuthorizationStatus) {
    Task { @MainActor in
        self.handleAuth(authStatus)
    }
}
```

*(Note: In UI-callback contexts like this where the system queue isn't a strict realtime audio thread, `Task { @MainActor in }` is acceptable. In CoreAudio realtime threads, it will crash. Use `DispatchQueue.main.async` there.)*
