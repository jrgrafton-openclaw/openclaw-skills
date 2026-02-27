#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_crash.ips_or.crash>"
    exit 1
fi

CRASH_FILE="$1"

if [ ! -f "$CRASH_FILE" ]; then
    echo "Error: File $CRASH_FILE not found."
    exit 1
fi

echo "=== Crash Summary ==="
echo "File: $CRASH_FILE"

# Extract exception type
grep -E "Exception Type:|Exception Codes:|Termination Reason:" "$CRASH_FILE"

# Extract crashed thread number
CRASHED_THREAD=$(grep -E "^Thread.*Crashed:" "$CRASH_FILE" | awk '{print $2}')
if [ -z "$CRASHED_THREAD" ]; then
    CRASHED_THREAD=$(grep -E "Triggered by Thread:" "$CRASH_FILE" | awk '{print $4}')
fi

echo ""
echo "=== Crashing Thread: $CRASHED_THREAD ==="

if [ -n "$CRASHED_THREAD" ]; then
    # Print the stack of the crashed thread until an empty line or "Thread "
    awk "/^Thread ${CRASHED_THREAD} name:/, /^Thread [0-9]+/" "${CRASH_FILE}" | grep -v "^Thread [0-9]\+ " | grep -v "^Thread ${CRASHED_THREAD} crashed with"
else
    echo "Could not parse crashing thread."
fi
