# KAIROS — ACAMS Hero Film

A 3:00 cinematic motion-graphics film for a 16:9 LED booth loop, produced from the *ACAMS Hero Film / Kairos* shooting script.

**Kairos — Connected Financial Crime Operations**

Style: Bloomberg / Financial Times / Apple keynote / Formula One broadcast graphics.  
Palette: midnight navy, deep black, electric blue, white, gold, amber, green, red.

## Watch

Open [`index.html`](index.html) in a browser and press **Play Film**.  
The finished linear cut is [`acams_kairos_hero_film.mp4`](acams_kairos_hero_film.mp4) (1920×1080, ~3:10 including the silent booth loop).

## Structure

| Time | Scene |
| --- | --- |
| 00:00–00:20 | The world has changed |
| 00:20–00:45 | Fragmented operations |
| 00:45–01:05 | The FRAML problem |
| 01:05–01:30 | Introducing Kairos |
| 01:30–01:55 | The operating room |
| 01:55–02:15 | Inside Kairos |
| 02:15–02:35 | FRAML enabled by Kairos |
| 02:35–02:50 | The connected lifecycle |
| 02:50–03:00 | Future state |
| 03:00–03:10 | Silent booth loop |

The core visual is the script’s mandated transition: **fragmented financial-crime functions → a single risk view**.

## Reproduce

```bash
python3 scripts/generate_music.py
python3 scripts/generate_audio.py
python3 scripts/render_film.py
```

Requires `ffmpeg`, `ffprobe`, Python 3, `edge-tts`, `numpy`, and `pillow`.
