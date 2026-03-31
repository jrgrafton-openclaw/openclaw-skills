---
name: ios-devops
description: "Build, sign, upload, and distribute iOS apps to TestFlight via Fastlane and the App Store Connect API. Use when asked to deploy, ship, build, push to TestFlight, run fastlane beta, or recover a partially completed iOS release. NOT for project setup/prototyping, crash diagnosis, or Swift concurrency debugging."
---

# iOS DevOps — build and ship to TestFlight

## Critical rules

1. Always set `LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8` before Fastlane.
2. Never claim a build shipped until distribution is verified.
3. Never run a long build in the background without a progress/reporting plan.
4. Always audit current build state before starting a new release.
5. Always run the post-build verification/distribution safety-net script.

## Standard release workflow

### 1. Pre-flight

Before every build:
- check git status and recent commits
- check whether an IPA already exists
- check the current build number
- audit recent ASC builds

Use:
- `scripts/check-asc-builds.py`

### 2. Build

```bash
cd <PROJECT_ROOT>
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bundle exec fastlane beta
```

### 3. Verify distribution

Always run after the build completes, times out, or is interrupted:

```bash
python3 <SKILL_DIR>/scripts/verify-and-distribute.py [APP_ID] [GROUP_ID]
```

### 4. Recover partial failures

If upload succeeded but distribution or commit/push did not:
- audit ASC state
- distribute missing VALID builds
- repair local git state

## Scripts

| Script | Purpose |
|---|---|
| `scripts/check-asc-builds.py` | show recent builds and distribution gaps |
| `scripts/distribute-build.py <VERSION>` | wait for VALID, then distribute one build |
| `scripts/verify-and-distribute.py` | safety-net: distribute all missing VALID builds |

## References

- `references/troubleshooting.md` — common failures
- `references/credentials.md` — secret locations and API details
- `references/project-config.md` — per-app IDs and paths

Keep project-specific IDs out of `SKILL.md`; store them in references or project docs.
