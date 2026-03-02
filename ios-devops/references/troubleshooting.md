# SingCoach Ship — Troubleshooting

## errSecInternalComponent (codesign fails)

The build keychain is locked. Run:

```bash
security unlock-keychain -p "" ~/Library/Keychains/build.keychain-db
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "" ~/Library/Keychains/build.keychain-db
security list-keychains -d user -s \
  ~/Library/Keychains/build.keychain-db \
  ~/Library/Keychains/login.keychain-db \
  /Library/Keychains/System.keychain
```

Then re-run `fastlane beta`.

## Build number already incremented but upload failed

Don't re-run `fastlane beta` — it will increment again. Build only at the current number:

```bash
cd /Users/familybot/.openclaw/workspace/projects/SingCoach
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec fastlane run build_app \
  project:"SingCoach.xcodeproj" \
  scheme:"SingCoach" \
  export_method:"app-store" \
  clean:true \
  output_directory:"./build" \
  output_name:"SingCoach.ipa"
```

Then upload manually — see "Upload-only" below.

## Upload-only (IPA already built)

```bash
IPA_PATH=$(realpath ./build/SingCoach.ipa)
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
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 fastlane pilot upload \
  --ipa "$IPA_PATH" \
  --skip_waiting_for_build_processing \
  --app_identifier "com.jrgrafton.singcoach" \
  --api-key-path /tmp/asc_api_key.json
```

Then manually add to testers via the ASC API (see Fastfile python block for the polling/distribution script).

## "invalid byte sequence in US-ASCII" (gym error handler crash)

Fastlane Ruby encoding bug. Always prefix the command:

```bash
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec fastlane beta
```

## Build number reset to 1 after xcodegen

`xcodegen generate` must NOT be run during a build — it resets `CURRENT_PROJECT_VERSION` in the pbxproj. The Fastfile reads from `Info.plist` (not pbxproj) specifically to avoid this. If it happened anyway:

```bash
# Check what the latest build on ASC was, then set Info.plist to that number
/usr/libexec/PlistBuddy -c 'Set CFBundleVersion <LAST_GOOD_BUILD>' SingCoach/Info.plist
# Then run fastlane beta normally — it increments by 1
```

## Build stuck in PROCESSING on ASC (never reaches VALID)

Normal wait is 5–15 min. If it stays in PROCESSING >20 min, the build may have been silently rejected (e.g. missing export compliance). Check App Store Connect web UI. If INVALID, fix the underlying issue and re-run the full lane.

## "No orientations were specified in the bundle" — Apple validation rejects build

XcodeGen overwrote `Info.plist` and stripped `UISupportedInterfaceOrientations`. See `docs/ios/xcodegen.md` to restore. Do NOT add `info.path` to project.yml.

## pilot distribute lies about success — testers don't get notified

`fastlane pilot distribute` silently succeeds without actually distributing. The Fastfile uses the ASC API directly (the python block) to add builds to the Internal Testers group. If you need to manually add a build:

```python
# Use the ASC API directly:
# POST https://api.appstoreconnect.apple.com/v1/betaGroups/7b26e051-1109-4403-b4a3-86873cbf970e/relationships/builds
# body: {"data": [{"type": "builds", "id": "<build-id>"}]}
# Get build-id from: GET /v1/apps/6759441600/builds?filter[version]=<build-number>
```
