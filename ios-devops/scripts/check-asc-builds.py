#!/usr/bin/env python3
"""Check recent builds in App Store Connect and their distribution status.

Usage: python3 check-asc-builds.py [APP_ID] [GROUP_ID]

Defaults to SingCoach IDs if not specified.
"""
import jwt, time, urllib.request, json, sys, os

APP_ID = sys.argv[1] if len(sys.argv) > 1 else "6759441600"
GROUP_ID = sys.argv[2] if len(sys.argv) > 2 else "7b26e051-1109-4403-b4a3-86873cbf970e"

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


def get_json(url):
    req = urllib.request.Request(url, headers=headers())
    return json.loads(urllib.request.urlopen(req).read())


print(f"=== Recent builds for app {APP_ID} ===")
builds = get_json(
    f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/builds?limit=10&fields[builds]=version,processingState"
)
for b in builds["data"]:
    a = b["attributes"]
    print(f"  Build {a['version']} — {a['processingState']}")

if GROUP_ID:
    print(f"\n=== Builds in beta group {GROUP_ID} ===")
    group_builds = get_json(
        f"https://api.appstoreconnect.apple.com/v1/betaGroups/{GROUP_ID}/builds?limit=10&fields[builds]=version,processingState"
    )
    for b in group_builds["data"]:
        a = b["attributes"]
        print(f"  Build {a['version']} — {a['processingState']}")
