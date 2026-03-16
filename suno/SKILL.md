---
name: suno
description: Generate music with Suno AI via browser automation. Use when asked to create, generate, or iterate on music tracks, background music, game soundtracks, or audio loops using Suno. Covers prompt engineering, Custom Mode usage, and downloading generated tracks. NOT for: SFX generation (use ElevenLabs), audio editing/mixing (use ffmpeg), or non-music audio tasks.
---

# Suno Music Generation

Generate music via [suno.com](https://suno.com) using browser automation.

## Prerequisites

- User must be logged into Suno in the browser (openclaw profile or Chrome relay)
- Suno v5 is the current model (as of March 2026)

## Workflow

1. **Navigate** to `https://suno.com/create`
2. **Switch to Custom Mode** (toggle at top) — always use Custom Mode for control
3. **Fill fields:**
   - **Style of Music** (200 char max) — comma-separated tags, most important first
   - **Lyrics** (3,000 char max) — use structure tags or leave empty for instrumental
   - **Title** (80 char max)
4. **Click Create** → wait for generation (~30-60s)
5. **Download** the MP3 from the song page (three-dot menu → Download → Audio)

## Prompt Engineering — Style Field

### Formula (order matters — Suno weights earlier tags more)

```
[Genre], [Mood/Energy], [Key Instruments], [Vocal Style], [Production Quality], [BPM]
```

### Rules

- **200 character limit** — use comma-separated tags, NOT sentences
- **8-12 tags** max — too many dilutes focus
- **Most important first** — genre always leads
- **Negative prompts** supported in v5: append `no vocals`, `no autotune`, `no reverb` etc. at END
- **BPM** as number: `60 BPM`, `120 BPM` — more precise than "slow" or "fast"
- **Era references** over artist names: "late 70s disco" not specific artists
- **For instrumental:** add `instrumental` tag + `no vocals` + leave lyrics empty

### Game Soundtrack Prompts (WH40K reference)

```
# Ambient / Tactical (Command, Deploy, Move phases)
dark ambient, cinematic, orchestral drone, deep reverberating organ, 
distant ethereal choir, industrial machinery undertones, grimdark sci-fi, 
atmospheric, instrumental, no vocals, 60 BPM

# Combat / Tense (Shoot, Charge, Fight phases)  
epic orchestral, dark cinematic, heavy war drums, taiko percussion,
brass fanfare, building intensity, grimdark battle, aggressive,
instrumental, no vocals, 80 BPM

# Tactical Tension (any phase)
dark electronic, brooding synths, pulsing bass, sparse strings,
tactical strategy game, XCOM-style, minimal, tense atmosphere,
instrumental, no vocals, 65 BPM
```

### Lyrics Field — Structure Tags

For instrumental tracks: leave empty or use only structure tags:

```
[Intro]
[Build]
[Instrumental]
[Break]
[Outro]
```

For tracks with vocals: `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`

### Looping Tips

- Suno doesn't have a native "loop" mode — tracks have natural beginnings/endings
- For seamless loops: generate, then use ffmpeg crossfade on head/tail:
  ```bash
  # Crossfade last 2s with first 2s for seamless loop
  ffmpeg -i input.mp3 -af "afade=t=out:st=$(echo "DURATION-2" | bc):d=2" -y faded.mp3
  ```
- Alternatively: generate longer tracks (3-4 min) and extract a loopable middle section

## v5 Features

- **Max length:** 4 minutes per generation (extendable)
- **Studio mode** (paid): stem separation (vocals/drums/bass/other), section editing
- **Negative prompts:** `no autotune`, `no reverb`, `no synths`, `no drums`, `no choir`
- **Better vocal clarity** and instrument separation vs v4

## Tips

- **Generate 3-5 versions** — v5 output varies significantly between generations
- **Iterate on winners** — use "Create Similar" or refine the style prompt
- **Credits:** Free tier = 50 credits/day (~10 songs). Pro = 2,500/month. Premier = 10,000/month.
- **Commercial rights** require a paid plan
