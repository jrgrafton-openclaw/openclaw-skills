---
name: web-qa
description: "End-to-end QA workflow for web bugs using GitHub Issues as the system of record. Use when a user reports visual or functional bugs, PR review comments describe broken behavior, or you need structured triage → fix → independent verification for a web project. NOT for greenfield feature work or non-web platforms."
---

# Web QA

Use this workflow for disciplined bug handling:

1. **Triage**
   - clarify ambiguous reports before guessing
   - identify the code-symbol-level root cause
   - define a measurable acceptance check
2. **Track the bug in GitHub Issues**
   - one bug per issue
   - keep screenshots/attachments on the issue, not in source branches
3. **Fix**
   - implement the smallest change that satisfies the acceptance check
4. **Verify independently**
   - separate verifier when the work is non-trivial
   - use measurable browser checks, not "looks fine"
5. **Human verification**
   - tell the user exactly what to click and what "fixed" should look like
6. **Close**
   - close issues only after verification is complete

## Core rules

- If the bug report is unclear, ask before proceeding.
- If you cannot express the acceptance check as something concrete, it is not precise enough.
- Do not trust the fixer to verify their own work for subtle UI bugs.
- Do not store screenshots in feature branches or main.

## References

- `references/issue-template.md`
- `references/verification-patterns.md`
- `references/screenshot-hosting.md`
