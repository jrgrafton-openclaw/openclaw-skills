---
name: wh40k-simulator
description: "WH40K Simulator project conventions: rendering architecture, visual bug fixing, browser verification, debug menu usage, engine contracts, and deployment pipeline. Use when working on ANY task in the warhammer-40k-simulator repo — engine, content, AI, UI, mockups, map editor, or CI. Covers: (1) visual/UI bugs and drag/rendering/SVG layer work, (2) engine rules and test conventions, (3) integrated mockup architecture, (4) deploy pipeline and verification patterns, (5) sub-agent task descriptions for this project."
---

# WH40K Simulator — Project Conventions

> **⚠️ LIVING DOCUMENT — KEEP THIS UPDATED**
> This skill captures hard-won knowledge about the WH40K simulator. It MUST evolve as the project develops. Every agent that reads this skill has a responsibility:
>
> 1. **Before starting work:** Read this skill AND the project's `AGENTS.md`. If anything here contradicts `AGENTS.md` or the actual codebase, update this skill.
> 2. **After completing work:** If you discovered new architectural patterns, pitfalls, debug techniques, or rendering behaviors — **add them here before finishing.** Don't rely on memory.
> 3. **If a section is stale:** File paths changed? Phase names renamed? New SVG layers added? Fix it now. Wrong docs are worse than no docs.
> 4. **If the mockup version advances** (e.g. v0.5 → v0.6): Update all version-specific paths, layer names, and phase lists. Grep for the old version string.
>
> The cost of NOT updating this skill = another 6-hour debugging session. Write it down.

## Project Location
- **Repo:** `jrgrafton-openclaw/warhammer-40k-simulator`
- **Pages:** `https://jrgrafton-openclaw.github.io/warhammer-40k-simulator/`
- **Project AGENTS.md:** Read it first for architecture contracts, repo structure, and extension points.
- **Current active branch:** Check `git branch` in the worktree — don't assume a specific branch name.
- **Worktrees:** Run `git worktree list` from the main checkout to see all active worktrees.

## 1. Rendering Architecture (Integrated Mockup)

> **Update this section** when SVG layers are added/removed/renamed or the rendering pipeline changes.

### SVG Layer Stack (bottom to top)
```
#battlefield-inner
  ├── #bf-svg-terrain    (SVG, viewBox 0 0 720 528)
  │     ├── terrain sprites, zone rects
  │     ├── #layer-models    (model groups live HERE after layer-order.js)
  │     └── #layer-hulls     (unit hull paths)
  ├── #bf-svg-vignette   (SVG, z-index: 8, edge vignette + zone vignettes)
  └── #bf-svg-drag       (SVG, z-index: 9, overflow:visible, pointer-events:none)
        ├── #drag-hulls    (hull paths during drag)
        └── #drag-models   (model groups during drag)
```

### Key Facts
- **Board dimensions:** 720×528 px (playable area)
- **`layer-order.js`** runs once at map load — reparents some model `<g>` elements from `#bf-svg` to `#bf-svg-terrain` for z-interleaving with terrain sprites
- **`renderModels()`** (in `model-renderer.js`) always creates elements in `#layer-models`. It does NOT know about layer-order reparenting.
- **`#layer-models` is INSIDE `#bf-svg-terrain`** (not a separate SVG)

### Render-Then-Reparent Pattern (CRITICAL)
The **only correct way** to lift elements above the vignette during drag:

1. `renderModels()` recreates all model groups fresh in `#layer-models`
2. `callbacks.afterRender` (per-phase) or `callbacks.afterRenderPersistent` (cross-phase) fires
3. Reparent function clears `#drag-hulls` + `#drag-models` first, then moves freshly-rendered elements there

**NEVER move elements before render.** `renderModels()` recreates everything — pre-render moves create duplicates (one in drag layer from before, one freshly created in layer-models).

### Callback Lifecycle
| Callback | Set by | Cleared by | Survives phase transitions? |
|----------|--------|------------|---------------------------|
| `callbacks.afterRender` | Each scene (deploy, move, shoot, etc.) | `scene-registry.js transitionTo()` | ❌ No |
| `callbacks.afterRenderPersistent` | `svg-renderer.js initModelInteraction()` | Never cleared | ✅ Yes |
| `callbacks.selectUnit` | Each scene | `scene-registry.js transitionTo()` | ❌ No |
| `callbacks.updateRangeCircles` | `svg-renderer.js` module init | Never cleared | ✅ Yes |

> **When adding new callbacks:** Decide if they need to survive phase transitions. If yes, add a `Persistent` variant in `model-renderer.js` and document it in this table.

### Deploy Phase Drag (Special Case)
Deploy has its **own** drag reparenting in `deployment.js`:
- Uses `deployState.placingUnit` (not `simState.drag`) to determine which unit to reparent
- Registers its reparent via `callbacks.afterRender`
- Has a `defineProperty` interceptor on `simState.drag` for blocking enemy drags and calling `startPlacement()`
- `cleanupDeployment()` removes the interceptor (restores plain property)

**Rule:** `svg-renderer.js`'s `_reparentDraggedUnit()` must skip during deploy (`phase-deploy` body class check). Deploy owns its own reparenting.

## 2. Board Boundary Clamping

### `_clampUnitToBoard(unit)` in `svg-renderer.js`
- **PAD = 10** (matches deploy's `_clampToZone`)
- Cohesive shift: computes max overshoot per edge, applies single dx/dy to ALL models (preserves hull shape, no collapse)
- **Offboard exemption:** Only skip clamping when `!simState.drag` AND any model has `x < 0`. During active drag, ALWAYS clamp — prevents units escaping past the left edge.
- Fires on every `mousemove` + safety-net on `mouseup` for all drag types (unit, model, rotate)

## 3. Visual Bug Verification (MANDATORY)

### Debug Menu — Fast Phase Testing
The start screen has a debug panel:
1. Click **⚙ Debug** button (bottom of start screen)
2. Click **→ Deploy**, **→ Move**, **→ Shoot**, etc. to skip directly to that phase
3. Units are auto-deployed, positioned appropriately for the target phase

The in-game debug panel (top-right **⚙ Debug** toggle) also has phase skip buttons + overlay toggles.

**Always use the debug menu for visual testing.** It's dramatically faster than clicking through the full game setup.

### Browser Verification Steps
1. **Serve locally:** `cd packages/ui/public && python3 -m http.server 8767`
2. **Open browser:** `browser(action="open", url="http://localhost:8767/mockups/integrated/v0.5/")`
3. **Cache busting:** Append `?v=N` to URL when changing JS files (ES modules are aggressively cached)
4. **Skip to phase:** Use debug menu buttons or JS: `import('./scene-registry.js').then(sr => sr.transitionTo('move'))`
5. **Programmatic drag test:**
   ```js
   const hull = document.querySelector('.unit-hull[data-unit-id="<unit-id>"]');
   const rect = hull.getBoundingClientRect();
   hull.dispatchEvent(new MouseEvent('mousedown', { clientX: rect.x+10, clientY: rect.y+10, bubbles: true }));
   window.dispatchEvent(new MouseEvent('mousemove', { clientX: targetX, clientY: targetY, bubbles: true }));
   // Check element counts
   document.getElementById('drag-models').querySelectorAll('g[data-unit-id="..."]').length;  // should be N during drag
   document.getElementById('layer-models').querySelectorAll('g[data-unit-id="..."]').length;  // should be 0 during drag
   window.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
   ```
6. **Verify element counts:** During drag: N in drag-models, 0 in layer-models. After drop: 0 in drag-models, N back in layer-models.

### What "Verified" Means
- ❌ DOM query shows attribute exists → NOT verified (proves code was written, not that it renders)
- ❌ Reading source code and concluding it should work → NOT verified
- ✅ Screenshot showing the visual state → verified
- ✅ Element count check during drag (drag-models vs layer-models) → verified
- ✅ Coordinate check after drag (all within board bounds) → verified

## 4. Common Pitfalls

> **When you discover a new pitfall:** Add it to this table immediately.

| Pitfall | Why it fails | Prevention |
|---------|-------------|------------|
| Moving elements before `renderModels()` | `renderModels()` recreates all elements → duplicates | Always use afterRender/afterRenderPersistent callback |
| `if (m.x < 0) skip clamp` during drag | Models cross x=0 during drag → clamp disables | Gate offboard skip with `!simState.drag` |
| Deploy's `defineProperty` interceptor leaking | Persists after deploy cleanup → blocks ork drag, calls `startPlacement()` in wrong phase | `cleanupDeployment()` must `delete simState.drag; simState.drag = currentDrag;` |
| `callbacks.afterRender` cleared on phase transition | Scene-registry nulls it in `transitionTo()` | Use `afterRenderPersistent` for cross-phase behavior |
| Browser caching ES modules | Old code runs despite file changes | Append `?v=N` to URL for cache bust |
| SVG `clipPath` across reparented elements | `clipPath` in `#bf-svg` doesn't clip elements reparented to `#bf-svg-terrain` | Use arc paths or HTML overlay instead of cross-SVG clipPath |
| "Verified" via DOM query only | Proves code was written, not that it renders correctly | Always use browser screenshot or element count checks |

## 5. Deploy Pipeline

- CI runs on push to any PR branch
- PR preview deploys to `preview/pr-<N>/` on `gh-pages`
- **NEVER commit directly to `gh-pages`** — CI rebuilds it from source
- Check CI: `gh run list --repo jrgrafton-openclaw/warhammer-40k-simulator --limit 3`
- Version banner in console: `[v0.5] commit=<hash> built=<timestamp>` — verify the deployed commit matches your push

## 6. Engine & Content Conventions

### Read AGENTS.md First
The project `AGENTS.md` at the repo root defines architecture contracts, dependency direction, extension points, and test conventions. **Read it before any task.** This skill supplements it with hard-won operational knowledge.

### Architecture Contracts (from AGENTS.md — check AGENTS.md for current version)
- **Engine has NO external deps.** Works in Node, Deno, browsers.
- **State is immutable from outside.** `engine.getState()` returns a deep clone. Mutate only via `engine.dispatch(action)`.
- **ALL randomness via `SeededRng`.** Never `Math.random()` in engine/content/ai.
- **Dependency direction:** engine ← content ← ai ← ui (never import upstream)

### Test Commands
```bash
pnpm test              # All engine/content tests (Vitest, no UI rendering tests)
pnpm test -- --watch   # Watch mode
```

### Test Fixtures
- **Custodes 1985pt army:** `packages/content/src/__tests__/fixtures/custodes-test-army.json`
- Use real fixtures for integration testing — don't test with empty/minimal state

### Golden Transcript Tests
Fixed seed → deterministic hash. If you change the pipeline (resolver order, dice logic, ability effects), the hash changes. Update the hash in the test AND explain why in the commit message.

## 7. Worktree Policy
For any non-trivial change, use a git worktree:
```bash
git worktree add /private/tmp/wh40k-<feature> -b <branch> <base-branch>
```
Run `git worktree list` to see existing worktrees before creating new ones. Clean up worktrees when branches are merged.

## 8. Sub-Agent Task Descriptions
When spawning sub-agents for WH40K work, include:
- The rendering architecture summary (Section 1) for any UI task
- The render-then-reparent rule for any drag/layer work
- Debug menu instructions for visual verification
- The exact browser verification steps (Section 3)
- `pnpm test` must pass before committing
- **Remind the sub-agent to update this skill** if they discover new patterns or pitfalls

There are NO automated tests for the rendering layer. All visual verification must be done in-browser using the debug menu.

## 9. Game Phases
> **Update this list** when new phases are added or renamed.

Current phases (in order): `deploy` → `move` → `shoot` → `charge` → `fight` → `game-end`

Each phase has:
- A scene file: `scenes/scene-<phase>.js`
- A scene-registry config registered via `registerScene('<phase>', { ... })`
- A body class: `phase-<phase>`
- Cleanup runs on exit, init runs on entry (via `transitionTo()`)
