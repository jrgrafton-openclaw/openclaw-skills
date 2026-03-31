# Architecture notes

## Phase order
`deploy` → `command` → `move` → `shoot` → `charge` → `fight` → `game-end`

## Key boundaries
- `simState` is the single mutable game-state object
- per-phase state stays local to the phase module
- `shared/` code is reusable and import-only
- `renderModels()` recreates model elements, so reparent only after render callbacks

## Regression rule

When behavior regresses after a refactor/migration:
- find the last known-good implementation
- trace the original source of truth
- restore the broken pipeline first
- avoid papering over the issue with fabricated fallback data
