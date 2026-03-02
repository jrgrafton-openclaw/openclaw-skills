# Firebase Skill

Operations for managing Firebase apps (like iOS apps) directly from the terminal without manual login, by relying on the GCP Service Account secret.

## Operations
- To create a new iOS app and fetch `GoogleService-Info.plist`: use `./create-ios-app.sh <project_id> <display_name> <bundle_id> [app_store_id]`