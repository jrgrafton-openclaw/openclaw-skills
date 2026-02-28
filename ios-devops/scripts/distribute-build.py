#!/usr/bin/env python3
"""Distribute a specific build to a beta group via ASC API.

Usage: python3 distribute-build.py <BUILD_VERSION> [APP_ID] [GROUP_ID]

Polls until the build is VALID, then adds it to the beta group.
Defaults to SingCoach IDs if not specified.
"""
import jwt, time, urllib.request, json, sys, os

if len(sys.argv) < 2:
    print("Usage: python3 distribute-build.py <BUILD_VERSION> [APP_ID] [GROUP_ID]")
    sys.exit(1)

BUILD_VERSION = sys.argv[1]
APP_ID = sys.argv[2] if len(sys.argv) > 2 else "6759441600"
GROUP_ID = sys.argv[3] if len(sys.argv) > 3 else "7b26e051-1109-4403-b4a3-86873cbf970e"

KEY_PATH = os.path.expanduser("~/.openclaw/secrets/app-store-connect/AuthKey_7UKLD4C2CC.p8")
KEY_ID = "7UKLD4C2CC"
ISSUER = "69a6de70-79a7-47e3-e053-5b8c7c11a4d1"


def make_token():
    key = open(KEY_PATH).read()
    payload = {
        "iss": ISSUER,
        "iat": int(time.time()),
        "exp": int(time.time()) + 1200,
        "aud": "appstoreconnect-v1",
    }
    return jwt.encode(payload, key, algorithm="ES256", headers={"kid": KEY_ID})


def headers():
    return {"Authorization": f"Bearer {make_token()}", "Content-Type": "application/json"}


# Poll until VALID
build_id = None
for attempt in range(90):
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/builds?limit=20&fields[builds]=version,processingState"
    req = urllib.request.Request(url, headers=headers())
    builds = json.loads(urllib.request.urlopen(req).read())["data"]
    match = next((b for b in builds if b["attributes"]["version"] == BUILD_VERSION), None)
    if match:
        state = match["attributes"]["processingState"]
        print(f"[{attempt+1}/90] Build {BUILD_VERSION}: {state}")
        if state == "VALID":
            build_id = match["id"]
            break
        elif state == "INVALID":
            print(f"ERROR: Build {BUILD_VERSION} is INVALID — cannot distribute", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[{attempt+1}/90] Build {BUILD_VERSION} not yet visible in ASC...")
    time.sleep(10)

if not build_id:
    print(f"ERROR: Build {BUILD_VERSION} never reached VALID after 15 minutes", file=sys.stderr)
    sys.exit(1)

print(f"✅ Build {BUILD_VERSION} is VALID: {build_id}")

# Add to beta group
payload_data = json.dumps({"data": [{"type": "builds", "id": build_id}]}).encode()
req = urllib.request.Request(
    f"https://api.appstoreconnect.apple.com/v1/betaGroups/{GROUP_ID}/relationships/builds",
    data=payload_data,
    headers=headers(),
    method="POST",
)
try:
    urllib.request.urlopen(req)
    print(f"✅ Build {BUILD_VERSION} added to beta group — testers will be notified")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if e.code == 409:
        print(f"ℹ️  Build {BUILD_VERSION} was already in the beta group")
    else:
        print(f"ERROR {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

# Verify
time.sleep(3)
url2 = f"https://api.appstoreconnect.apple.com/v1/betaGroups/{GROUP_ID}/builds?limit=5&fields[builds]=version,processingState"
req2 = urllib.request.Request(url2, headers=headers())
result = json.loads(urllib.request.urlopen(req2).read())
print("\nBuilds now in beta group:")
for b in result["data"][:5]:
    print(f"  Build {b['attributes']['version']} — {b['attributes']['processingState']}")
