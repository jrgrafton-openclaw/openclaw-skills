#!/bin/bash
set -e

PROJECT=$1
DISPLAY_NAME=$2
BUNDLE_ID=$3
APP_STORE_ID=$4

if [ -z "$BUNDLE_ID" ]; then
  echo "Usage: ./create-ios-app.sh <project_id> <display_name> <bundle_id> [app_store_id]"
  exit 1
fi

export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.openclaw/secrets/firebase/service-account.json"

if [ -z "$APP_STORE_ID" ]; then
    npx firebase-tools apps:create ios "$DISPLAY_NAME" -b "$BUNDLE_ID" --project "$PROJECT"
else
    npx firebase-tools apps:create ios "$DISPLAY_NAME" -b "$BUNDLE_ID" -a "$APP_STORE_ID" --project "$PROJECT"
fi

# Fetch the sdk config right after
# Getting the app ID requires parsing the output or listing apps. For simplicity, just tell user to use `apps:sdkconfig`.
echo "App created. To download GoogleService-Info.plist, run: npx firebase-tools apps:sdkconfig IOS <app_id> --project $PROJECT --out GoogleService-Info.plist"
