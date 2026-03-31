# Verification

## Browser QA recipe

1. Open the game URL.
2. Enter the app and clear the audio gate.
3. Progress through start, forge, deploy, and the main phases.
4. Use the debug menu where needed.
5. Capture screenshots for changed states.
6. Check console errors; only known harmless errors are acceptable.

## What counts as verified

Good:
- screenshots
- console check
- element counts / measurable checks

Not enough on its own:
- reading source code
- DOM presence without confirming rendered behavior
