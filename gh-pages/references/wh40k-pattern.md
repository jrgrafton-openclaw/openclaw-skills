# WH40K GitHub Pages pattern

Reference repo:
`https://github.com/jrgrafton-openclaw/warhammer-40k-simulator`

## Workflows to mirror

### 1. `ci.yml`
Purpose:
- run tests on PRs and `main`
- deploy built output to `gh-pages` on `main`

Key characteristics:
- CI runs on both `push` to `main` and `pull_request`
- production deploy runs only on `main`
- deploy publishes built `dist/` to `gh-pages`
- `keep_files: true` preserves preview directories already on `gh-pages`

### 2. `pr-preview.yml`
Purpose:
- build PR output
- publish to `gh-pages/preview/pr-<number>/`
- comment the preview URL back on the PR

Key characteristics:
- per-PR concurrency group
- `destination_dir: preview/pr-${{ github.event.pull_request.number }}`
- `keep_files: true`
- PR comment includes the preview URL

### 3. `cleanup-preview.yml`
Purpose:
- delete the preview directory when the PR closes

Key characteristics:
- trigger on `pull_request: types: [closed]`
- check out `gh-pages`
- delete `preview/pr-<number>`
- commit and push the cleanup

## Notes

- Treat `gh-pages` as generated output only.
- If the site needs cache-busting for built JS/HTML, do that in CI before publish.
- Prefer one proven workflow family across repos over ad hoc Pages setups.
