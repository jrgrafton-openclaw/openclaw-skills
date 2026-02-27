#!/bin/bash

# A script to emit Swift Intermediate Language (SIL) for a given Swift file
# to inspect compiler-generated thunks and isolation checks (like hop_to_executor).

if [ -z "$1" ]; then
    echo "Usage: $0 <file.swift>"
    exit 1
fi

SWIFT_FILE="$1"

if [ ! -f "$SWIFT_FILE" ]; then
    echo "Error: File $SWIFT_FILE not found."
    exit 1
fi

echo "Emitting SIL for $SWIFT_FILE..."
# Emits SIL. Using basic flags. For complex projects, might need xcodebuild or import paths.
swiftc -emit-sil "$SWIFT_FILE" | c++filt
