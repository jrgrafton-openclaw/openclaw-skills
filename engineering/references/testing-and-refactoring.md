# Testing and refactoring discipline

## Tests first

1. Write the test that expresses the desired behavior.
2. Run it and confirm it fails.
3. Implement the minimum code to make it pass.
4. Run it again and confirm it passes.

## Reproduce before fixing

- visual bugs: reproduce in the browser/app
- logic bugs: reproduce with a failing test
- crash fixes: reproduce with the smallest discriminating case possible

## Consumer-first refactors

Before unifying N implementations behind a shared interface:
- list every consumer of the old codepaths
- grep for old functions/properties/types
- update consumers before producers
- test each consumer against each supported type/state

## Bulk failure rule

If a change breaks >10 tests:
- stop
- group failures by pattern
- identify the 1–3 root causes
- fix the shared cause first
- if needed, revert to green before trying again
