---
name: ios-design
description: "iOS design iteration using an Ionic web prototype as the primary surface and a native iOS preview pass as the fidelity gate. Use when iterating on iOS app UI/UX, validating layout/states/copy in web first, then checking native behavior before handoff to the app. NOT for shipping builds, crash diagnosis, or Swift concurrency debugging."
---

# iOS design iteration

Use a web-first workflow, then switch to the native gate only when it matters.

## Default: web iteration

1. Make focused changes in the Ionic prototype.
2. Keep the prototype deployable at all times.
3. Force iOS rendering mode explicitly.
4. After each change, report routes to open, states to verify, and what to look for.

## Switch to native only when needed

Use the iOS preview/native pass for:
- text truncation/wrapping
- keyboard avoidance and forms
- safe areas
- list/scroll behavior
- sheets, gestures, transitions
- accessibility-sensitive flows

## Handoff

Once web is 90% correct and the native gate passes:
1. port the changes into the app
2. re-run the native checklist on the real screen
3. commit with a prototype reference where useful

## Theme policy

Do not auto-update the Ionic theme package. Only update it intentionally and re-validate affected screens.
