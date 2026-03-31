#!/usr/bin/env bash
set -euo pipefail

PROJECT="${1:-}"
DISPLAY_NAME="${2:-}"
BUNDLE_ID="${3:-}"
APP_STORE_ID="${4:-}"
OUT_PATH="${5:-GoogleService-Info.plist}"

if [[ -z "$PROJECT" || -z "$DISPLAY_NAME" || -z "$BUNDLE_ID" ]]; then
  echo "Usage: scripts/create-ios-app.sh <project_id> <display_name> <bundle_id> [app_store_id] [output_path]" >&2
  exit 1
fi

export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.openclaw/secrets/firebase/service-account.json"
if [[ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
  echo "Missing service account: $GOOGLE_APPLICATION_CREDENTIALS" >&2
  exit 1
fi

create_cmd=(npx firebase-tools apps:create ios "$DISPLAY_NAME" -b "$BUNDLE_ID" --project "$PROJECT" --json)
if [[ -n "$APP_STORE_ID" ]]; then
  create_cmd+=( -a "$APP_STORE_ID" )
fi

CREATE_JSON="$(${create_cmd[@]})"
APP_ID="$(python3 - <<'PY' "$CREATE_JSON"
import json,sys
obj=json.loads(sys.argv[1])
# firebase-tools output shape can vary; handle common cases
app_id=(obj.get('result') or {}).get('appId') or obj.get('appId') or ((obj.get('result') or {}).get('sdkConfig') or {}).get('appId')
if not app_id:
    raise SystemExit('Could not parse appId from firebase-tools output')
print(app_id)
PY
)"

npx firebase-tools apps:sdkconfig IOS "$APP_ID" --project "$PROJECT" --out "$OUT_PATH" >/dev/null

echo "Created Firebase iOS app: $APP_ID"
echo "Saved plist: $OUT_PATH"
