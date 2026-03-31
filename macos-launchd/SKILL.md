---
name: macos-launchd
description: "Create, fix, and diagnose macOS LaunchAgent/LaunchDaemon plist files. Use when setting up a service to start automatically, diagnosing restart loops, fixing duplicate processes from KeepAlive misconfiguration, or doing launchctl load/unload/kickstart work."
---

# macOS launchd

## KeepAlive — the most common footgun

Do not use `KeepAlive: true` for long-running services that bind ports or hold locks. Prefer:

```xml
<key>KeepAlive</key>
<dict>
    <key>SuccessfulExit</key>
    <false/>
</dict>
<key>ThrottleInterval</key>
<integer>10</integer>
```

## Recommended workflow

1. Start from `assets/launchagent.template.plist`.
2. Fill in the label, binary path, args, working directory, and log paths.
3. Validate the file with:

```bash
scripts/validate-plist.sh <path/to/file.plist>
```

4. Load it with `launchctl`.
5. Verify PID / exit status with `launchctl list`.

## Diagnosing duplicate process loops

Symptoms:
- repeated "already running" logs
- rapid restart behavior

Common cause:
- `KeepAlive: true` plus another orphan or already-running instance

Fix:
- identify the launchd-owned PID
- kill the orphan
- correct the plist to `SuccessfulExit: false`

## Reference

See `references/keepalive-options.md` for KeepAlive variants.
