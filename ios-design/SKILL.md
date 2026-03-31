---
name: ios-design
description: "iOS Design Iteration using an Ionic web prototype (primary surface) with a native iOS Preview app as the fidelity gate. Use when: iterating on iOS app UI/UX, verifying layout/states/copy in web first, then validating iOS-native behavior. NOT for: full app builds (use ios-devops), crash diagnosis (use ios-crash-diagnosis), or automated screenshot pipelines."
---

# iOS Design Iteration — Ionic Web-first + Native Gate

## Mental Model

**Web prototype first. Native gate only when it matters.**

- Default: make all changes in the Ionic prototype, deploy to GitHub Pages, review in browser.
- Native gate: switch to the iOS Preview app only for behaviour that web can't validate.

---

## A) Web Iteration (Default)

1. Make changes in the Ionic prototype (small, focused commits).
2. Keep the prototype deployable to GitHub Pages at all times.
3. Force iOS rendering mode — do not rely on user-agent detection:
   ```ts
   // main.ts (or equivalent bootstrap)
   import { setupIonicReact } from '@ionic/react';
   setupIonicReact({ mode: 'ios' });
   ```
4. Theme is `@rdlabo/ionic-theme-ios26` — **pinned version, committed lockfile**. Do not auto-update.
5. After each change, output the **Web Iteration Checklist** below.

### Web Iteration Checklist (output after every change)

```
Routes to open on GitHub Pages:
  - /               (home / default state)
  - /[changed route]

States to verify:
  □ Empty state
  □ Loading state
  □ Error state
  □ Long text / overflow
  □ [Any state specific to this change]

What changed:
  [one-line summary]

What to look for:
  [specific things to confirm visually]
```

---

## B) Native Gate — When to Switch

Invoke the iOS Preview app when **any** of these are true:

- Text-heavy screens where truncation or line-wrap matters
- Forms, keyboard avoidance, safe area insets
- Complex lists, scrolling, sticky headers, pull-to-refresh
- Sheets, detents, navigation transitions, swipe gestures
- Accessibility-sensitive flows (focus order, hit targets)

**Otherwise: stay in web.**

### Native Gate Checklist (run in iOS Preview app)

```
□ Layout matches web prototype at correct scale
□ Text truncation / wrapping correct
□ Safe areas respected (top, bottom, notch)
□ Keyboard avoidance works on form fields
□ Scroll performance acceptable (no jank)
□ Sheet/detent behaviour correct
□ Navigation transitions feel native
□ Tap targets meet minimum size (44×44pt)
□ VoiceOver focus order logical
□ [Any behaviour specific to this screen]
```

---

## C) Definition of "90% Done in Web"

- Layout, hierarchy, spacing, copy, and all states are correct in the browser prototype.
- Only remaining uncertainty is iOS-native behaviour or polish.
- If the native gate checklist passes → proceed to handoff.

---

## D) Handoff to Target App

Once the native gate confirms the design is correct, integrate into the real app:

1. Port the component/screen changes from the Ionic prototype to the target app (e.g. SingCoach).
2. Verify the target app still passes the native gate checklist for the affected screens.
3. Commit with a reference to the prototype change (e.g. `Refs: prototype commit abc123`).

---

## E) Theme Update Policy (Manual Only)

Only update `@rdlabo/ionic-theme-ios26` when explicitly requested:

1. Check upstream for the latest version.
2. Bump the pinned version in `package.json`.
3. Run `npm install` and commit the updated lockfile.
4. Re-validate affected screens against the native gate checklist.

**Never auto-update or fetch remote CSS.**
