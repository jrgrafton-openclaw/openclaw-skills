#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
try:
    from google.cloud import bigquery
except ImportError:
    print("Error: google-cloud-bigquery not installed. Try: pip3 install google-cloud-bigquery")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query recent iOS crashes from Firebase Crashlytics via BigQuery.")
    parser.add_argument("--project", default="lobsterproject", help="GCP project ID")
    parser.add_argument("--app", default="com.jrgrafton.singcoach", help="App bundle ID (dots converted to underscores)")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to fetch")
    args = parser.parse_args()

    # Automatically set Google credentials if not present but SA file exists
    key_path = os.path.expanduser(f"~/.config/gcloud/legacy_credentials/{args.project}@{args.project}.iam.gserviceaccount.com/adc.json")
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ and os.path.exists(key_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    client = bigquery.Client(project=args.project)
    
    app_id = args.app.replace(".", "_")
    table_id = f"{args.project}.firebase_crashlytics.{app_id}_IOS_REALTIME"

    query = f"""
    SELECT
      event_timestamp,
      issue_id,
      issue_title,
      error_type,
      device.model as device_model,
      operating_system.display_version as os_version,
      exceptions
    FROM `{table_id}`
    ORDER BY event_timestamp DESC
    LIMIT {args.limit}
    """

    print(f"Querying {table_id} for the latest {args.limit} crashes...")
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
    except Exception as e:
        print(f"Query failed: {e}")
        sys.exit(1)

    if not results:
        print("No recent crashes found.")
        return

    for idx, row in enumerate(results):
        print(f"\n[{idx + 1}] Time: {row.event_timestamp} | Type: {row.error_type}")
        print(f"Title: {row.issue_title} | ID: {row.issue_id}")
        print(f"Device: {row.device_model} | OS: {row.os_version}")
        
        # Exceptions logic
        if getattr(row, "exceptions", None):
            for exc in row.exceptions:
                for frame in getattr(exc, "frames", [])[:5]:
                    lib = getattr(frame, "library", "Unknown")
                    sym = getattr(frame, "symbol", "Unknown")
                    print(f"  > {lib} - {sym}")

if __name__ == "__main__":
    main()
