# File placement

Use these directories:
- phase game logic → `game/phases/<phase>/`
- core game infrastructure → `game/core/`
- debug tools → `game/debug/`
- deployment state/UI → `game/deploy/`
- map loading/collision → `game/map/`
- screens → `game/screens/`
- game CSS → `game/css/`
- game assets → `game/assets/`
- shared state → `shared/state/`
- shared rendering/world → `shared/world/`
- shared CSS → `shared/css/`
- shared utilities → `shared/lib/`
- editor code/CSS → `editor/js/`, `editor/css/`
- tests → `game/__tests__/` or `editor/__tests__/`

Anti-patterns:
- JS files in `game/` root beyond the approved entry files
- CSS in random roots
- utility code in the wrong subsystem
- `window.__` globals for cross-module state
