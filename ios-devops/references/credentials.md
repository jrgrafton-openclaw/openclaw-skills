# iOS DevOps — Credentials & API Reference

All secrets live in `~/.openclaw/secrets/` — never commit these.

## App Store Connect API

**Key:** `~/.openclaw/secrets/app-store-connect/AuthKey_7UKLD4C2CC.p8`  
**Key ID:** `7UKLD4C2CC`  
**Issuer ID:** `69a6de70-79a7-47e3-e053-5b8c7c11a4d1`  
**Team ID:** `B5X96QDRF4`

> **New iOS project setup:** copy `docs/ios/templates/.env.default` → `fastlane/.env.default`.  
> Only `APP_IDENTIFIER` and `SCHEME` need updating — credentials are pre-filled.

### Manual TestFlight Upload
```bash
KEY_CONTENT=$(cat ~/.openclaw/secrets/app-store-connect/AuthKey_7UKLD4C2CC.p8)
cat > /tmp/asc_api_key.json << EOF
{
  "key_id": "7UKLD4C2CC",
  "issuer_id": "69a6de70-79a7-47e3-e053-5b8c7c11a4d1",
  "key": $(echo "$KEY_CONTENT" | jq -Rs .),
  "duration": 1200,
  "in_house": false
}
EOF

fastlane pilot upload --ipa "./build/App.ipa" \
  --skip_waiting_for_build_processing \
  --api-key-path /tmp/asc_api_key.json
```

> **Prefer `bundle exec fastlane beta` over manual upload** — it handles signing, dSYM upload, and Crashlytics in one step.

## Firebase (iOS)

**Service Account:** `~/.openclaw/secrets/firebase/service-account.json`  
**Project ID:** `lobsterproject`

Download `GoogleService-Info.plist`: Firebase Console → Project Settings → iOS app

## Xcode

**Version:** 17C52  
**Path:** `/Applications/Xcode.app`

## Ruby / Fastlane

System Ruby + Bundler per-project (`bundle exec fastlane ...`).
