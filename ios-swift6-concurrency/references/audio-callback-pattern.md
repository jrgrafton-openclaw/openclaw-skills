# Audio callback pattern

## Problem

A closure defined inside a `@MainActor` method may inherit actor isolation in the compiler-generated thunk even when it does not capture `self` directly.

## Safe pattern

1. Build the callback in a `nonisolated` helper.
2. Do thread-safe processing in the callback.
3. Dispatch back to main only for the UI/update boundary.

## Smell list

If you see any of these in an audio/render callback, stop and reconsider:
- `Task { @MainActor in ... }`
- direct SwiftUI state mutation
- direct model mutation from the callback thread
- assuming `[weak self]` solves the isolation problem
