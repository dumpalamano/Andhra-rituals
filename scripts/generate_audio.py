#!/usr/bin/env python3
"""Generate timed voiceover and mix with the score."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)

VOICE = "en-US-GuyNeural"
RATE = "+18%"
PITCH = "-2Hz"

# Scene-aligned VO. Start times leave a visual beat before speech.
# max_s is the window before the next scene; clips are time-fit if needed.
CLIPS = [
    {
        "name": "vo01",
        "start_ms": 1600,
        "max_s": 17.6,
        "text": (
            "The world of financial crime has changed. "
            "Money moves instantly. Risk moves faster. "
            "Criminal networks move across products, channels, and borders. "
            "Financial crime is no longer linear. It is connected."
        ),
    },
    {
        "name": "vo02",
        "start_ms": 21200,
        "max_s": 22.8,
        "text": (
            "Most institutions built financial crime capabilities one function at a time. "
            "One platform for onboarding. Another for fraud. Another for A M L. Another for investigations. "
            "Each team sees part of the story. No one sees the complete customer."
        ),
    },
    {
        "name": "vo03",
        "start_ms": 46200,
        "max_s": 18.4,
        "text": (
            "Fraud teams investigate suspicious activity. "
            "A M L teams investigate suspicious movement of funds. "
            "Too often, both are investigating the same network. "
            "Through different lenses. At different times. In different systems."
        ),
    },
    {
        "name": "vo04",
        "start_ms": 66500,
        "max_s": 22.8,
        "text": (
            "Introducing Kairos. "
            "Firstsource's operating system for A I native operations. "
            "Built from twenty-five years of domain expertise. "
            "Designed to help organizations act during moments that matter. "
            "Not another point solution. "
            "An operating system connecting intelligence, decisions, and execution."
        ),
    },
    {
        "name": "vo05",
        "start_ms": 91200,
        "max_s": 22.8,
        "text": (
            "A I is only as effective as the environment around it. "
            "Just as a surgeon depends on an operating room, "
            "A I depends on context. Expertise. Control. Governance. "
            "The agent is the surgeon. Kairos is the operating room."
        ),
    },
    {
        "name": "vo06",
        "start_ms": 116400,
        "max_s": 17.8,
        "text": (
            "Kairos connects operational intelligence. Institutional context. "
            "Domain expertise. And A I native execution. "
            "Creating a system that learns continuously and improves outcomes over time."
        ),
    },
    {
        "name": "vo07",
        "start_ms": 136200,
        "max_s": 18.0,
        "text": (
            "Kairos enables a connected approach to fraud and anti-money laundering. "
            "Bringing together customer intelligence. Behavioral signals. "
            "Network relationships. And operational decision making. "
            "Creating a single view of risk."
        ),
    },
    {
        "name": "vo08",
        "start_ms": 155800,
        "max_s": 13.6,
        "text": (
            "From onboarding and K Y C. To monitoring. To investigation. To reporting. "
            "To real-time payments and fraud prevention. "
            "Kairos connects the entire financial crime lifecycle."
        ),
    },
    {
        "name": "vo09",
        "start_ms": 169200,
        "max_s": 10.2,
        "text": (
            "Financial crime is evolving. Operations must evolve with it. "
            "One customer. One risk view. One operating system. "
            "Kairos. Intelligence that operates."
        ),
    },
]

DURATION = 190.0


async def synth(clip: dict) -> Path:
    raw = AUDIO / f"{clip['name']}_raw.mp3"
    communicate = edge_tts.Communicate(clip["text"], VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(raw))
    dur = probe_duration(raw)
    out = AUDIO / f"{clip['name']}.mp3"
    max_s = clip["max_s"]
    if dur > max_s + 0.05:
        tempo = min(dur / max_s, 1.85)
        # chain atempo if needed (atempo range 0.5-2.0)
        af = f"atempo={tempo:.4f}"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw), "-filter:a", af, "-codec:a", "libmp3lame", "-q:a", "3", str(out)],
            check=True,
            capture_output=True,
        )
        raw.unlink(missing_ok=True)
    else:
        raw.replace(out)
    return out


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(r.stdout.strip())


async def main() -> None:
    paths = []
    for clip in CLIPS:
        path = await synth(clip)
        dur = probe_duration(path)
        print(f"{clip['name']}: {dur:.2f}s starts {clip['start_ms']/1000:.1f}s")
        paths.append((clip, path, dur))

    inputs: list[str] = []
    filters = []
    for i, (clip, path, _) in enumerate(paths):
        inputs += ["-i", str(path)]
        filters.append(f"[{i}:a]adelay={clip['start_ms']}|{clip['start_ms']},asetpts=PTS-STARTPTS[a{i}]")

    mix_in = "".join(f"[a{i}]" for i in range(len(paths)))
    filters.append(
        f"{mix_in}amix=inputs={len(paths)}:duration=longest:dropout_transition=0:normalize=0,"
        "apad=pad_dur=12[vo]"
    )
    filters.append("[vo]loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]")

    vo_raw = AUDIO / "voiceover_raw.wav"
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[out]",
        "-t",
        str(DURATION),
        "-ar",
        "48000",
        "-ac",
        "2",
        str(vo_raw),
    ]
    subprocess.run(cmd, check=True)

    music = AUDIO / "score.wav"
    if not music.exists():
        raise SystemExit("score.wav missing — run generate_music.py first")

    mix = AUDIO / "mix.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(vo_raw),
            "-i",
            str(music),
            "-filter_complex",
            "[0:a]volume=1.05[vo];"
            "[1:a]highpass=f=40,lowpass=f=11000,volume=0.17[sc];"
            "[vo][sc]amix=inputs=2:duration=first:dropout_transition=4:normalize=0,"
            "alimiter=limit=0.96,loudnorm=I=-14:TP=-1.2:LRA=9[a]",
            "-map",
            "[a]",
            "-t",
            str(DURATION),
            "-ar",
            "48000",
            "-ac",
            "2",
            str(mix),
        ],
        check=True,
    )

    mp3 = AUDIO / "mix.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mix), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3)],
        check=True,
    )
    vo_mp3 = AUDIO / "voiceover.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(vo_raw), "-codec:a", "libmp3lame", "-q:a", "3", str(vo_mp3)],
        check=True,
    )
    print("Wrote", mix, mp3)


if __name__ == "__main__":
    asyncio.run(main())
