# KeepAlive Options Reference

All variants use a dict instead of `<true/>`:

```xml
<key>KeepAlive</key>
<dict>
    <key>KEY</key>
    <VALUE/>
</dict>
```

| Key | Value | Behaviour |
|-----|-------|-----------|
| `SuccessfulExit` | `<false/>` | Restart only on crash (exit ≠ 0). **Most common for servers.** |
| `SuccessfulExit` | `<true/>` | Restart only on clean exit (exit = 0). Rare. |
| `NetworkState` | `<true/>` | Keep alive only while network is up. |
| `PathState` | dict of path→bool | Keep alive based on file/dir existence. |
| `OtherJobEnabled` | dict of label→bool | Keep alive based on another job's state. |

**Recommendation for long-running servers:** `SuccessfulExit: false` + `ThrottleInterval: 10`

**Never use bare `<true/>`** for services that bind to a port or hold a lock file.
