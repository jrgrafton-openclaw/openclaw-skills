# Verification patterns

Prefer checks like:
- DOM element counts
- computed styles
- bounding box / geometry comparisons
- class presence / attribute values
- timeline instrumentation for animation bugs

## Animation bugs

A single screenshot is not enough. Capture state over time and inspect where values jump or snap unexpectedly.

## Diagnostic exaggeration

When a visual defect is subtle, temporarily exaggerate the suspect feature during QA, then remove the instrumentation before commit.

## Cache discipline

When testing static or CDN-cached web assets, verify the changed code is actually running before trusting visual results.
