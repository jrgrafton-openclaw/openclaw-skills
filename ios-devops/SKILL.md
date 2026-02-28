---
name: ios-devops
description: Build, sign, upload, and distribute iOS apps to TestFlight via Fastlane and the App Store Connect API. Use when asked to deploy, ship, build, push to TestFlight, run fastlane beta, or distribute any iOS app. Also covers recovery from failed/partial builds, build state auditing, and ASC API operations. NOT for: Xcode project setup (use ios-prototype), crash diagnosis (use ios-crash-diagnosis), or Swift concurrency issues (use ios-swift6-concurrency).
---

# iOS DevOps — Build & Ship to TestFlight

## Critical Rules

1. **ALWAYS set locale before fastlane:** `LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8` — altool crashes without it.
2. **NEVER use `upload_to_testflight` or `pilot distribute`** — they silently lie about distribution. Use altool for upload + ASC API for distribution.
3. **NEVER use `xcpretty`** — it crashes on non-ASCII output and hides the real build result.
4. **NEVER run fastlane in background without feedback** — always run foreground with a timeout, or use `yieldMs: 300000` (5 min) and poll.
5. **ALWAYS audit build state before running `fastlane beta`** — check git status, existing IPA, and ASC builds first.

## Pre-Flight Checklist (MANDATORY before every build)

Run this BEFORE `fastlane beta`:

```bash
cd <PROJECT_ROOT>

# 1. Check git state — if Info.plist is dirty, a prior run failed mid-flight
git status --short
git log --oneline -3

# 2. Check for existing IPA
ls -la build/*.ipa 2>/dev/null

# 3. Check current build number
/usr/libexec/PlistBuddy -c 'Print CFBundleVersion' <PATH_TO_INFO_PLIST>

# 4. Check what's in ASC (use scripts/check-asc-builds.py)
python3 <SKILL_DIR>/scripts/check-asc-builds.py
```

**If Info.plist is modified (dirty):** A prior run crashed after bumping the build number. Reset with `git checkout <Info.plist path>` OR verify the build already uploaded to ASC before retrying.

**If an IPA exists and is recent:** The prior run may have succeeded. Check ASC before rebuilding.

## Running the Build

```bash
cd <PROJECT_ROOT>
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bundle exec fastlane beta
```

**Expected timing:**
- Small app (SwiftDesignPlayground): ~60 seconds
- Medium app (SingCoach): ~4 minutes
- ASC processing poll: additional 2-15 minutes

**Exec pattern for OpenClaw:** Use `yieldMs: 300000` (5 min) for small apps, `yieldMs: 600000` (10 min) for medium apps. Then poll. Do NOT use `background: true` without polling.

```
exec(command: "cd <path> && LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bundle exec fastlane beta", yieldMs: 300000)
```

If the command backgrounds, poll with `process(action: "poll", sessionId: "<id>", timeout: 60000)` every 60 seconds until complete. **Report progress to the user immediately** — don't wait for the full pipeline to finish.

## Recovery from Partial Failures

### Build uploaded but git commit failed
The build is already on TestFlight. Just fix and commit:
```bash
git add <Info.plist> <project.pbxproj>
git commit -m "[ci skip] Bump build to <N>"
git push
```

### Build uploaded but not distributed
Use `scripts/distribute-build.py <BUILD_VERSION>` to add to beta group.

### altool says "bundle version already used"
The build already uploaded. Poll ASC until it appears as VALID, then distribute.

## Project-Specific IDs

### SingCoach
- **ASC App ID:** `6759441600`
- **Bundle ID:** `com.jrgrafton.singcoach`
- **Internal Testers Group:** `7b26e051-1109-4403-b4a3-86873cbf970e`
- **Project Path:** `projects/SingCoach/`
- **Info.plist:** `SingCoach/Info.plist`

### SwiftDesignPlayground
- **ASC App ID:** `6759811915`
- **Bundle ID:** `com.jrgrafton.swift.design.playground`
- **Project Path:** `projects/SwiftDesignPlayground/`
- **Info.plist:** `Info.plist`
- **Internal Testers Group:** `3e9bf740-1bea-4a46-b0e7-e0b569e55f6b`
- **GitHub:** `jrgrafton-openclaw/SwiftDesignPlayground`

### ASC API Credentials
- **Key:** `~/.openclaw/secrets/app-store-connect/AuthKey_7UKLD4C2CC.p8`
- **Key ID:** `7UKLD4C2CC`
- **Issuer:** `69a6de70-79a7-47e3-e053-5b8c7c11a4d1`
- **Team ID:** `B5X96QDRF4`

## First-Time App Setup (one-off, before first build)

Before the first `fastlane beta` for a new app, ensure:

1. **Beta group exists** — create via ASC API:
   ```python
   POST /v1/betaGroups  {"data":{"type":"betaGroups","attributes":{"name":"Internal Testers","isInternalGroup":true},"relationships":{"app":{"data":{"type":"apps","id":"<APP_ID>"}}}}}
   ```

2. **Testers are explicitly added to the group** — internal groups do NOT auto-invite team members. You must create/add each tester:
   ```python
   POST /v1/betaTesters  {"data":{"type":"betaTesters","attributes":{"firstName":"James","lastName":"Grafton","email":"jrgrafton@gmail.com"},"relationships":{"betaGroups":{"data":[{"type":"betaGroups","id":"<GROUP_ID>"}]}}}}
   ```
   This sends the TestFlight invite email. Without this step, the build lands in the group but nobody gets notified or can install it. 409 on this endpoint means the tester already exists — that's fine if `inviteType: EMAIL` is set.

3. **Git remote configured** — `gh repo create <org>/<name> --public --source=. --push`

## Fastfile Architecture

Every Fastfile should follow this pattern:

1. `before_all`: Set `LC_ALL`/`LANG`, `setup_ci` if CI
2. `api_key` private lane: Create ASC API key object
3. `create_json_key` private lane: Write JSON key for tools that need file path
4. `beta` lane:
   - Unlock keychain + set partition list
   - `sigh` to download provisioning profile (use `api_key_path`, not `api_key`)
   - Install profile to `~/Library/MobileDevice/Provisioning Profiles/`
   - `update_code_signing_settings` for manual signing
   - Bump build via `PlistBuddy` (NOT `increment_build_number`)
   - Archive with `xcodebuild` (redirect to log, no xcpretty)
   - Export with `xcodebuild -exportArchive` (use dynamic `profile_uuid` in export options)
   - Upload with `xcrun altool` (symlink key to `~/.appstoreconnect/private_keys/`)
   - Poll ASC API until VALID, then add to beta group
   - Git tag, commit (with `allow_nothing_to_commit: true`), push

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid byte sequence in US-ASCII` | Missing `LC_ALL`/`LANG` | Set env vars in `before_all` |
| `errSecInternalComponent` | Keychain locked | `security unlock-keychain` + `set-key-partition-list` |
| `No profiles found` at export | Hardcoded/wrong profile UUID | Use dynamic `profile_uuid` from `sigh` |
| `nothing to commit` at git step | Prior run already committed | Use `allow_nothing_to_commit: true` |
| ASC API 422 on beta group add | Build still PROCESSING | Poll until VALID (10s intervals, 15 min timeout) |
| Crashlytics dSYM upload hangs | Network call blocks xcodebuild | Set `SKIP_CRASHLYTICS_DSYM_UPLOAD=1` |
| altool "version already used" | Duplicate upload | Don't re-upload; poll ASC + distribute |
| `LaunchScreen` / `UILaunchScreen` missing | No launch storyboard in bundle | Add `<key>UILaunchScreen</key><dict/>` to Info.plist (iOS 14+) |
| `push_git_tags` fails "not a git repository" | No git remote configured | `gh repo create <org>/<name> --public --source=. --push` |
| altool fails but pipeline continues | `grep` at end of pipe swallows exit code | Add `set -o pipefail` at start of sh block |
| Build in group but no invite sent | Testers not explicitly added to group | `POST /v1/betaTesters` with group relationship — required even for internal groups |
