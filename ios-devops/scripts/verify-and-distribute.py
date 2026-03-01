#!/usr/bin/env python3
"""Verify all recent builds are distributed, and fix any that aren't.

This is the SAFETY NET script. Run it after every build, or as a cron/heartbeat
check. It finds any VALID builds that were uploaded but never added to the beta
group, and distributes them automatically.

Usage: python3 verify-and-distribute.py [APP_ID] [GROUP_ID]

Defaults to SingCoach IDs if not specified.
Exit codes:
  0 = all builds distributed (or fixed)
  1 = error (auth, network, INVALID build)
"""
import jwt, time, urllib.request, json, sys, os

APP_ID = sys.argv[1] if len(sys.argv) > 1 else "6759441600"
GROUP_ID = sys.argv[2] if len(sys.argv) > 2 else "7b26e051-1109-4403-b4a3-86873cbf970e"

KEY_PATH = os.path.expanduser("~/.openclaw/secrets/app-store-connect/AuthKey_7UKLD4C2CC.p8")
KEY_ID = "7UKLD4C2CC"
ISSUER = "69a6de70-79a7-47e3-e053-5b8c7c11a4d1"

# How many recent builds to check (high enough to not miss any)
BUILDS_LIMIT = 30


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


def add_to_group(build_id, build_version):
    """Add a build to the beta group. Returns True on success or already-in-group."""
    payload_data = json.dumps({"data": [{"type": "builds", "id": build_id}]}).encode()
    req = urllib.request.Request(
        f"https://api.appstoreconnect.apple.com/v1/betaGroups/{GROUP_ID}/relationships/builds",
        data=payload_data,
        headers=headers(),
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        print(f"  ✅ Build {build_version} added to Internal Testers — testers notified")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 409:
            # Already in group — fine
            return True
        body = e.read().decode()
        print(f"  ❌ ERROR {e.code} adding build {build_version}: {body}", file=sys.stderr)
        return False


# 1. Get all recent builds for the app
print(f"Checking {BUILDS_LIMIT} most recent builds for app {APP_ID}...")
all_builds = get_json(
    f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/builds"
    f"?limit={BUILDS_LIMIT}&fields[builds]=version,processingState,uploadedDate"
)["data"]

# 2. Get builds already in the beta group
group_builds = get_json(
    f"https://api.appstoreconnect.apple.com/v1/betaGroups/{GROUP_ID}/builds"
    f"?limit={BUILDS_LIMIT}&fields[builds]=version"
)["data"]
group_versions = {b["attributes"]["version"] for b in group_builds}

# 3. Find VALID builds not in the group
missing = []
processing = []
for b in all_builds:
    v = b["attributes"]["version"]
    state = b["attributes"]["processingState"]
    if v not in group_versions:
        if state == "VALID":
            missing.append(b)
        elif state == "PROCESSING":
            processing.append(b)

if not missing and not processing:
    print("✅ All recent builds are distributed to Internal Testers.")
    sys.exit(0)

if processing:
    print(f"\n⏳ {len(processing)} build(s) still PROCESSING:")
    for b in processing:
        print(f"  Build {b['attributes']['version']} — PROCESSING (uploaded: {b['attributes'].get('uploadedDate', 'N/A')})")

if missing:
    print(f"\n⚠️  {len(missing)} VALID build(s) NOT distributed — fixing now:")
    fixed = 0
    failed = 0
    for b in sorted(missing, key=lambda x: int(x["attributes"]["version"])):
        v = b["attributes"]["version"]
        uploaded = b["attributes"].get("uploadedDate", "N/A")
        print(f"\n  Build {v} (uploaded: {uploaded})")
        if add_to_group(b["id"], v):
            fixed += 1
        else:
            failed += 1

    print(f"\n{'='*40}")
    print(f"Fixed: {fixed} | Failed: {failed}")
    if failed:
        sys.exit(1)

if processing:
    print(f"\nNote: {len(processing)} build(s) still processing — re-run this script in a few minutes.")

print("\n✅ All fixable builds have been distributed.")
