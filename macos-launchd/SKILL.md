---
name: macos-launchd
description: "Create, fix, and diagnose macOS LaunchAgent/LaunchDaemon plist files. Use when: (1) setting up a new service to auto-start at login, (2) a service is looping/crashing on restart, (3) duplicate processes from KeepAlive misconfiguration, (4) service not starting after reboot, (5) any launchctl load/unload/kickstart work."
---

# macOS launchd

## KeepAlive — the most common footgun

**Never use `KeepAlive: true` for long-running services.** It restarts on *any* exit, causing a retry storm if the process crashes fast or races on restart.

Use `KeepAlive: { SuccessfulExit: false }` instead — restarts only on crash (non-zero exit):

```xml
<key>KeepAlive</key>
<dict>
    <key>SuccessfulExit</key>
    <false/>
</dict>
<key>ThrottleInterval</key>
<integer>10</integer>
```

`ThrottleInterval` (seconds) adds a minimum gap between restarts. Always include it alongside KeepAlive.

## Creating a LaunchAgent (best-practice template)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.myservice</string>

    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/node</string>
        <string>/path/to/server.js</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/path/to/project</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>ThrottleInterval</key>
    <integer>10</integer>

    <key>StandardOutPath</key>
    <string>/tmp/myservice.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/myservice.error.log</string>
</dict>
</plist>
```

Save to `~/Library/LaunchAgents/<label>.plist`, then:
```bash
launchctl load ~/Library/LaunchAgents/<label>.plist
```

## Diagnosing duplicate process / "already running" loops

**Symptoms:** Service logs repeat "already running (pid XXXX)" every ~10s.

**Cause:** Two instances racing for the same port/lock. `KeepAlive: true` restarts the new instance immediately while the old one is still alive.

**Fix:**
```bash
# 1. Find which PID launchd owns
launchctl list | grep <service-label>   # first column = current PID

# 2. Kill the orphan (the PID NOT owned by launchd)
ps aux | grep <service-name> | grep -v grep
kill -9 <orphan-pid>

# 3. Let launchd's managed instance take over (it auto-restarts via KeepAlive)
# 4. Fix the plist to use SuccessfulExit: false so this can't loop again
```

## Useful launchctl commands

```bash
launchctl list | grep <label>              # status: PID + last exit code
launchctl load ~/Library/LaunchAgents/x.plist
launchctl unload ~/Library/LaunchAgents/x.plist
launchctl kickstart gui/$UID/<label>       # start now
launchctl kickstart -k gui/$UID/<label>    # kill + restart
launchctl bootout gui/$UID/<label>         # force remove (even if unload fails)
```

## Notes

- LaunchAgents run as the user, start at login. LaunchDaemons run as root, start at boot.
- The `node` binary path is typically `/opt/homebrew/bin/node` on Apple Silicon Macs.
- OpenClaw's own gateway plist (`ai.openclaw.gateway`) is managed by OpenClaw — don't edit it directly; it gets overwritten on updates.
- See `references/keepalive-options.md` for all KeepAlive variants.
