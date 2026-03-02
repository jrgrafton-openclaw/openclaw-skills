---
name: firebase
description: Manage Firebase projects and apps from the terminal using a GCP Service Account — no manual login required. Use when: registering a new iOS app in Firebase, fetching GoogleService-Info.plist, or automating Firebase project operations. NOT for: crash analysis (use ios-crash-diagnosis) or general GCP billing.
---

# Firebase Skill

Operations for managing Firebase apps (like iOS apps) directly from the terminal without manual login, by relying on the GCP Service Account secret.

## Operations
- To create a new iOS app and fetch `GoogleService-Info.plist`: use `./create-ios-app.sh <project_id> <display_name> <bundle_id> [app_store_id]`