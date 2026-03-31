# UI verification

## Mandatory interaction checklist

After UI changes:
- click every changed button/menu item
- type into every changed input
- test create → edit → use → delete flows when applicable
- test 0 / 1 / many-item states
- reload and verify persistence when applicable
- test dismissal behavior (outside click, Escape, cancel paths)

## Screenshot gate

1. Capture the current state.
2. Make the change.
3. Capture the changed state.
4. Compare the difference against the intended result.

For subtle bugs, prefer measurable checks or temporary visual exaggeration during QA.
