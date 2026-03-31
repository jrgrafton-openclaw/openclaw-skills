---
name: suno
description: "Generate music with Suno AI via browser automation. Use when asked to create, generate, or iterate on music tracks, background music, game soundtracks, or loop candidates using Suno. Covers prompt engineering, Custom Mode usage, verification, and downloading generated tracks. NOT for SFX generation, audio editing/mixing, or non-music audio tasks."
---

# Suno music generation

Generate music via `suno.com` using browser automation.

## Preconditions

- The user must already be logged into Suno in the browser profile you are controlling.
- Confirm the create page loads successfully before filling anything.

## Workflow

1. Open `https://suno.com/create`.
2. Confirm you are logged in and can see the create UI.
3. Switch to **Custom Mode** for controlled generation.
4. Fill:
   - **Style of Music** — short, comma-separated tags, most important first
   - **Lyrics** — structured sections or empty for instrumental
   - **Title**
5. Start generation.
6. Wait for both results to finish.
7. Open the preferred result and download the audio file.
8. Verify the download completed and report the saved filename/path.

## Style field formula

```text
[genre], [mood/energy], [key instruments], [vocal style], [production quality], [BPM]
```

Rules:
- keep it concise
- put the most important tags first
- use `instrumental` and `no vocals` for instrumental work
- prefer era/style references over artist-name cloning

## Failure handling

If generation fails:
- capture the visible error
- retry once with the same prompt
- if it fails again, report the failure instead of looping indefinitely

If download controls are missing:
- verify generation is complete
- open the specific track page
- retry the download action once
- report if the account tier or UI state blocks download
