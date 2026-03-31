# Compiler-generated thunk crashes

Use this reference when the crashing frame points at `<stdin>:0`, `<compiler-generated>`, or a closure thunk.

## Why it matters

The bug may be in what the compiler generated from the source, not in the obvious source-level code itself.

## High-value signal

If the stack shows:
- `_dispatch_assert_queue_fail`
- `_swift_task_checkIsolatedSwift`
- a compiler-generated closure frame

then the closure likely inherited actor isolation from its lexical scope.

## What to do

1. Inspect where the closure is **defined**, not just what it captures.
2. Emit SIL and search for executor hops / isolation checks.
3. Move closure creation into a `nonisolated` function when appropriate.
4. Re-test with the smallest targeted case.
