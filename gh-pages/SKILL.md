---
name: gh-pages
description: "Manage repositories that publish static files directly from the gh-pages branch without a CI rebuild pipeline. Use when a repo's Pages source is explicitly the gh-pages branch and content must be synced manually. NOT for repos where CI or GitHub Actions rebuilds gh-pages from main or another source branch."
---

# Manual GitHub Pages branch workflow

Use this skill only after confirming the repo really serves directly from `gh-pages`.

## Preflight

1. Confirm what branch GitHub Pages is configured to serve.
2. Inspect recent history on `origin/gh-pages`.
3. If recent commits are automated deploy commits, stop — this skill does **not** apply.

```bash
git log --oneline origin/gh-pages -5
```

## Safe workflow

1. Make and test changes on the source branch first.
2. Check out `gh-pages` locally.
3. Copy only the intended published files from source into `gh-pages`.
4. Commit with a conventional commit.
5. Push `gh-pages`.
6. Verify the live URL.

Example:

```bash
git fetch origin gh-pages
git checkout -B gh-pages origin/gh-pages
git checkout main -- path/to/published/files
git commit -m "docs(pages): sync published static files"
git push origin gh-pages
```

## Guardrails

- Do **not** force-push unless the branch is intentionally disposable and you have confirmed that with the user.
- Do **not** use this workflow for repos with CI-driven Pages deploys.
- Do **not** edit generated output only; always update the source branch too when a build pipeline exists.
