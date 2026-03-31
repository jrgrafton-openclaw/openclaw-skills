---
name: firebase
description: "Manage Firebase projects and app registrations from the terminal using configured service-account credentials. Use when registering a new iOS app in Firebase, fetching GoogleService-Info.plist, or automating routine Firebase app-management tasks. NOT for crash analysis or general GCP billing/admin work outside Firebase app operations."
---

# Firebase app management

Use the provided helper scripts for deterministic Firebase app setup.

## iOS app registration

Use:

```bash
scripts/create-ios-app.sh <project_id> <display_name> <bundle_id> [app_store_id] [output_path]
```

What it does:
1. creates the iOS app
2. resolves the created Firebase app ID
3. downloads `GoogleService-Info.plist`
4. prints the saved output path

## Requirements

- service account file must exist at `~/.openclaw/secrets/firebase/service-account.json`
- `firebase-tools` must be available via `npx`

## Failure handling

If the app already exists, stop and report it rather than creating duplicates.
If plist download fails, report the app ID and the failing command.
