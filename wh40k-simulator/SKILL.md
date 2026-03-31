---
name: wh40k-simulator
description: "WH40K Simulator project conventions: file placement, architecture, rendering, visual verification, debug menu, deploy pipeline, and sub-agent task descriptions. Use when working on ANY task in the warhammer-40k-simulator repo — game, editor, shared modules, mockups, or CI. Covers: (1) file placement rules and structure validation, (2) rendering architecture and SVG layers, (3) game phase system and state management, (4) browser verification and debug menu, (5) deploy pipeline, (6) sub-agent task descriptions. Includes self-staleness detection."
---

# WH40K Simulator — Project Conventions

> **⚠️ STALENESS CHECK — RUN THIS FIRST**
> Before using this skill, verify the documented structure matches reality:
> ```bash
> cd <repo-root>
> echo "=== Top dirs ===" && ls -d game/ shared/ editor/ mockups/ 2>/dev/null
> echo "=== game/ ===" && ls game/
> echo "=== game/phases/ ===" && ls game/phases/
> echo "=== shared/ ===" && ls shared/
> ```
> If any directory listed in this skill doesn't exist, or new directories exist that aren't documented here — **update this skill before proceeding.** Wrong docs cause worse outcomes than no docs.
>
> Last verified: 2026-03-30 (PR #77 production migration)

## Project Location
- **Repo:** `jrgrafton-openclaw/warhammer-40k-simulator`
- **Pages:** `https://jrgrafton-openclaw.github.io/warhammer-40k-simulator/`
- **Local path:** `/Users/familybot/.openclaw/workspace/projects/warhammer-40k-simulator/`
- **Issue tracker:** GitHub Issues on the repo. Check Issue #74 for the current MVP plan.

---

## 1. File Placement Rules (MANDATORY)

**Before creating any new file, check this table.** If your file doesn't fit any category, ask the user — don't guess.

| What you're creating | Where it goes | Example |
|---------------------|---------------|---------|
| Phase game logic (init, cleanup, scene registration) | `game/phases/<phase-name>/` | `game/phases/shoot/shooting.js` |
| Phase helper/utility specific to one phase | `game/phases/<phase-name>/` | `game/phases/charge/charge-helpers.js` |
| Core game infrastructure (state, routing, transitions) | `game/core/` | `game/core/scene-registry.js` |
| Debug tools and overlays | `game/debug/` | `game/debug/debug-menu.js` |
| Deployment state machine and UI | `game/deploy/` | `game/deploy/deployment.js` |
| Map loading and collision | `game/map/` | `game/map/map-pipeline.js` |
| Screen UIs (start, forge, options) | `game/screens/` | `game/screens/screen-forge.js` |
| Visual effects (fog, lightning, explosions) | `game/fx/` | `game/fx/fog-fx.js` |
| Game-specific CSS | `game/css/` | `game/css/shoot.css` |
| Game-specific assets (audio, images) | `game/assets/` | `game/assets/ambient-loop.mp3` |
| Shared state modules (store, units, config) | `shared/state/` | `shared/state/store.js` |
| Shared rendering (SVG, models, terrain) | `shared/world/` | `shared/world/svg-renderer.js` |
| Shared CSS (design tokens, component styles) | `shared/css/` | `shared/css/colors.css` |
| Shared utilities | `shared/lib/` | `shared/lib/coord-helpers.js` |
| Shared assets (sprites, music, SFX) | `shared/assets/` | `shared/assets/sprites/*.png` |
| Shared auth | `shared/auth/` | `shared/auth/auth.js` |
| Shared data (JSON configs) | `shared/data/` | `shared/data/deployment-types.json` |
| Editor code | `editor/js/` | `editor/js/core/state.js` |
| Editor CSS | `editor/css/` | `editor/css/sidebar.css` |
| Tests | `game/__tests__/` or `editor/__tests__/` | `game/__tests__/shoot-integration.test.js` |
| Networking/multiplayer (future) | `game/net/` (create when needed) | `game/net/room.js` |

### File Placement Validation
After creating or moving files, verify:
```bash
# No JS files in game/ root (except app.js, index.html, default-config.json)
ls game/*.js  # Should ONLY show app.js

# No CSS in game/ root
ls game/*.css  # Should show nothing

# No JS in shared/ root
ls shared/*.js  # Should show nothing

# All shared CSS consolidated in shared/css/
ls shared/css/  # Should contain ALL shared CSS (colors, typography, component styles)
```

### Anti-Patterns
- ❌ Creating a new file in `game/` root — belongs in a subdirectory
- ❌ Mixing phase-specific and shared logic in one file
- ❌ CSS in `shared/components/` — consolidated into `shared/css/`
- ❌ Utility functions in `shared/world/` — belongs in `shared/lib/`
- ❌ Files over 400 lines — split by responsibility
- ❌ `window.__` globals for cross-module communication — use ES module imports

---

## 2. Directory Structure

```
game/                          # The game application
  app.js                       # Entry point — imports all phases, wires game flow
  index.html                   # Game HTML (served at / via <base> tag)
  default-config.json          # FX config fallback (Supabase primary)
  core/                        # Game infrastructure
    game-bus.js                #   EventTarget bus for UI events
    phase-state.js             #   Phase state tracking
    scene-registry.js          #   Phase registration + transitionTo()
    screen-router.js           #   Start/Forge/Game screen switching
    transition.js              #   Forge→game transition animation
  debug/                       # Debug tools
    debug.js                   #   Debug panel controller + phase shortcuts
    debug-menu.js              #   Debug menu UI builder
    debug-menu.css             #   Debug menu styles
    debug-deploy.js            #   Auto-deploy logic
    debug-overlays.js          #   Visual debug overlays
  deploy/                      # Deployment state machine
    deployment.js              #   SVG tabletop, staging zones, drag placement
    deploy-helpers.js           #   Deploy validation helpers
    deploy-ui.js               #   Deploy UI (roster pills, status)
  map/                         # Map loading
    map-pipeline.js            #   Supabase map loading + terrain rendering
    collision-layout.js        #   AABB collision from map data
  phases/                      # Game phases (one subdir per phase)
    command/                   #   Command phase (battle-shock, CP, VP)
    deploy/                    #   Deploy scene registration
    move/                      #   Movement (drag, validation, advance)
    shoot/                     #   Shooting (weapon select, hit/wound/save, VFX)
    charge/                    #   Charge (2D6 roll, engagement)
    fight/                     #   Fight (pile-in, melee, consolidation)
    game-end/                  #   Game end overlay
  screens/                     # UI screens
    screen-start.js            #   Start screen (title, menu)
    screen-forge.js            #   Battle Forge (faction select, map, settings)
    screen-options.js          #   Options/settings overlay
  css/                         # Game-specific CSS
  fx/                          # Visual effects (fog, lightning, explosions)
  assets/                      # Game-specific media
  __tests__/                   # Game tests (vitest, jsdom)
  _to-port/                    # TypeScript code to port later (army loader, schemas)

shared/                        # Shared between game + editor
  state/                       # State modules
    store.js                   #   simState, callbacks, scale constants
    units.js                   #   UNITS data, card builder, tooltips
    faction-config.js          #   Dynamic faction loading (setFactions)
    game-config.js             #   Supabase game config CRUD
    map-loader.js              #   Supabase map loading
    terrain-data.js            #   Terrain type definitions
  world/                       # Rendering + world simulation
    svg-renderer.js            #   SVG board rendering, model interaction (~1200 lines)
    model-renderer.js          #   Model circle rendering
    zone-renderer.js           #   Deployment zone rendering
    board-renderer.js          #   Board background rendering
    collision.js               #   Terrain collision detection
    range-rings.js             #   Per-model range ring rendering
    layer-order.js             #   SVG layer z-ordering
    camera.js, pathfinding.js, terrain.js, sprite-renderer.js, etc.
  css/                         # ALL shared CSS
    colors.css                 #   CSS custom properties (faction colors, theme)
    typography.css             #   Font definitions
    action-bar.css, battlefield.css, fx.css, overlays.css, phase-states.css,
    roster.css, stratagem-modal.css, unit-card.css, vp-bar.css
  lib/                         # Shared utilities
    coord-helpers.js           #   Coordinate math, model radius
    drag-scroll.js             #   Horizontal scroll drag for carousels
  assets/                      # Shared media (sprites, music, SFX)
  data/                        # Static JSON (deployment types, terrain layouts)
  auth/                        # Supabase auth wrapper
  audio/                       # SFX module

editor/                        # Level editor (standalone)
  index.html, js/, css/, data/, __tests__/

mockups/                       # Frozen reference mockups (latest version only)
  integrated/v0.5/             # Full game mockup (original)
  phases/*/                    # Standalone phase mockups
  battle-forge/v0.8/           # Battle forge mockup
  shared/                      # Mockup shared assets
```

---

## 3. Game Phase System

### Phase Order
`deploy` → `command` → `move` → `shoot` → `charge` → `fight` → `game-end`

### How Phases Work
Each phase registers with `scene-registry.js`:
```js
registerScene('shoot', {
  init: initShooting,      // Called when entering phase
  cleanup: cleanupShooting, // Called when leaving phase
  config: {
    title: 'SHOOTING PHASE',
    bodyClass: 'phase-shoot',
    cta: { text: 'END SHOOTING →' },
    dotActive: 'SHOOT',
    dotsDone: ['CMD', 'MOVE'],
    nextPhase: 'charge'
  }
});
```

`transitionTo(phase)` handles: cleanup old → update DOM (title, dots, body class, CTA) → init new.

### State Management
- **`simState`** (in `shared/state/store.js`): Single mutable object — `units[]`, `drag`, `activeFaction`, `anim`
- **`callbacks`**: Phase-specific hooks — `selectUnit`, `afterRender` (cleared on transition), `afterRenderPersistent` (survives transitions)
- **Per-phase state**: Local `const state = {}` in each phase module (NOT in simState)
- **DOM as state**: ~533 direct DOM mutations — CSS classes, element attributes used as state flags

### What Each Phase Actually Does
| Phase | Mechanics Implemented |
|-------|----------------------|
| **Deploy** | Drag units from staging → deployment zone, validation, auto-deploy |
| **Command** | Battle-shock tests (2D6 vs Ld), CP gain (+1), VP scoring (objective proximity) |
| **Move** | Normal move + Advance (M" + D6"), drag models, coherency check, engagement range |
| **Shoot** | Full pipeline: weapon profiles → hit roll (BS+) → wound roll (S vs T) → save (AP + Sv) → damage → model removal. LoS, cover, Rapid Fire, projectile VFX |
| **Charge** | 2D6 charge roll, drag-to-engage, engagement range check, success/fail |
| **Fight** | Pile-in (3" drag), melee attacks (WS-based pipeline), consolidation (3" drag), model removal |
| **Game End** | Score display, model counts, PLAY AGAIN |

---

## 4. Rendering Architecture

### SVG Layer Stack (bottom to top)
```
#battlefield-inner
  ├── #bf-svg-terrain    (overflow:VISIBLE, viewBox 0 0 720 528)
  │     ├── terrain sprites, zone rects
  │     ├── #layer-models    (model circles — AFTER layer-order.js reparenting)
  │     └── #layer-hulls     (unit hull outlines)
  ├── #bf-svg            (overflow:HIDDEN)
  │     └── #layer-move-ghosts, #layer-debug-grid, etc.
  ├── #bf-svg-range      (z-index:7, pointer-events:none)
  │     └── range ring circles
  ├── #bf-svg-vignette   (z-index:8, edge/zone vignettes)
  └── #bf-svg-drag       (z-index:9, overflow:visible, pointer-events:none)
        ├── #drag-hulls, #drag-models (during drag)
```

### Render-Then-Reparent (CRITICAL)
1. `renderModels()` recreates ALL model elements in `#layer-models`
2. `callbacks.afterRender` fires AFTER render
3. Reparenting to drag layer happens in callbacks only

**NEVER move elements before render** — `renderModels()` recreates everything, causing duplicates.

### Board Dimensions
- Playable area: 720×528 px
- PX_PER_INCH = 12
- Standard infantry radius: 8px (32mm base)

---

## 5. Browser Verification

### Debug Menu Access
Press `D` key during gameplay (requires admin auth on live, works always locally).

### Debug Phase Skip Buttons
`→ Deploy` | `→ Command` | `→ Move` | `→ Shoot` | `→ Charge` | `→ Fight` | `→ Game End`

Auto-deploy shortcut: `⚡ AUTO DEPLOY ALL`

### Full QA Recipe
```
1. Open game URL
2. Click to enter (audio gate)
3. Wait 3s → screenshot start screen
4. Select factions (Custodes + Orks)
5. BEGIN BATTLE → screenshot deploy
6. Press D → AUTO DEPLOY ALL
7. Skip through each phase → screenshot each
8. Check console errors: browser(action="console", level="error")
9. Only favicon 404 is acceptable
```

### Import Path Rules
| Path type | Resolves relative to | From `game/phases/shoot/` | From `game/` root |
|-----------|---------------------|--------------------------|-------------------|
| `import ... from` | Module file | `../../../shared/` | `../shared/` |
| `import()` dynamic | Module file | `../../../shared/` | `../shared/` |
| `fetch()`, `Audio()` | HTML page (`game/index.html`) | `../shared/` | `../shared/` |
| CSS `url()` | CSS file | `../../assets/` | N/A |

### What "Verified" Means
- ❌ DOM query → proves code was written, not that it renders
- ❌ Reading source code → NOT verification
- ✅ Screenshot → verified
- ✅ Console error check → verified
- ✅ Element count check → verified

---

## 6. Deploy Pipeline

- **No build step** — vanilla JS served directly (no Vite, no bundler)
- CI assembles `dist/`: copies `game/`, `shared/`, `editor/`, `mockups/` → deploys to gh-pages
- Root `/` serves game via `<base href="game/">` tag in `dist/index.html`
- PR previews at `preview/pr-<N>/`
- Cache-bust: `?v=<timestamp>` on JS imports in HTML
- **NEVER commit directly to gh-pages**

### Deploy URLs
- Game: `https://...github.io/warhammer-40k-simulator/` (redirects to game/)
- Editor: `https://...github.io/warhammer-40k-simulator/editor/`
- Mockups: `https://...github.io/warhammer-40k-simulator/mockups/integrated/v0.5/`

---

## 7. Common Pitfalls

| Pitfall | Why it fails | Prevention |
|---------|-------------|------------|
| Moving elements before `renderModels()` | Creates duplicates | Use afterRender callbacks |
| `window.__` globals for state | Untraceable, untestable | Use ES module imports |
| Files > 400 lines | LLM confusion, mixed concerns | Split by responsibility |
| Hardcoded `'imp'`/`'ork'` strings | Breaks with custom factions | Use `factionA.id`/`factionB.id` from faction-config |
| `fetch()` path matching `import` depth | fetch resolves from page, import from module | Different depths — see table above |
| `setTimeout` cascades for animations | Timing-dependent, untestable | CSS animation-delay + animationend events |
| Fixing symptoms not causes | Range rings leak? Don't add overflow:hidden — trace the render path | Start from symptom → trace backward |
| Batching fixes without verifying each | Compound debugging | Fix → verify → screenshot → next fix |

---

## 8. Sub-Agent Task Descriptions

When spawning coding agents for WH40K work, include in the task:

1. **File placement table** (Section 1) — "New files go in these directories"
2. **Import path rules** — static vs dynamic vs runtime resolution
3. **Phase system** — how registerScene works, what init/cleanup do
4. **Verification requirement** — "run `npx vitest run` and verify zero console errors in browser"
5. **This instruction:** "After completing, check if any new patterns or pitfalls were discovered. If so, note them for the orchestrator to add to the WH40K skill."

---

## 9. Architecture Principles

1. **Group by responsibility, not by type** — `game/phases/shoot/` not `game/js/`
2. **Shared modules are import-only** — `shared/` never imports from `game/` or `editor/`
3. **Each phase owns its state** — local `const state = {}`, not globals
4. **CSS by component** — split into `shared/css/` (design tokens, shared components) and `game/css/` (phase-specific)
5. **ES modules everywhere** — explicit imports/exports, no IIFEs, no `window.__`
6. **Tests next to what they test** — `game/__tests__/` for game, `editor/__tests__/` for editor
