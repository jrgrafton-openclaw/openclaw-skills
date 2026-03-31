# Review, release, and deploy notes

## PR description template

```md
## Features implemented
- ...

## Bugs fixed
- ...

## Verification
- `...`

## Follow-ups / risks
- ...
```

## Manual gh-pages warning

Only update `gh-pages` directly for repos that truly deploy straight from that branch.
If CI rebuilds `gh-pages` from `main`, edit source files on `main` and let the pipeline publish.

## Cache busting

When static assets are CDN cached, update version params and verify the new code is actually executing before declaring success.
