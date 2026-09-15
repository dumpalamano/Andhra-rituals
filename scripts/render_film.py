#!/usr/bin/env python3
"""Build ASS titles, Ken-Burns plates, and the final 16:9 film."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
AUDIO = ROOT / "assets" / "audio"
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)

W, H, FPS = 1920, 1080, 30
FADE = 0.85
TOTAL = 190.0

# Hold length before xfade overlap is applied.
PLATES = [
    # file, hold seconds, zoom expression (on = frame count)
    ("scene01_fednow.png", 6.0, "1+0.00045*on"),
    ("scene01_accelerate.png", 6.5, "1.04+0.0007*on"),
    ("scene01_network.png", 9.5, "1+0.0005*on"),
    ("scene02_fragmented.png", 26.0, "1+0.00022*on"),
    ("scene03_split.png", 12.0, "1+0.0003*on"),
    ("scene03_reveal.png", 10.0, "1.02+0.00045*on"),
    ("scene04_convergence.png", 12.0, "1.08-0.00035*on"),
    ("scene04_os.png", 14.5, "1+0.00028*on"),
    ("scene05_theatre.png", 13.5, "1+0.00025*on"),
    ("scene05_control.png", 13.0, "1+0.0003*on"),
    ("scene06_layers.png", 21.0, "1+0.0002*on"),
    ("scene07_mule.png", 21.0, "1.02+0.00032*on"),
    ("scene08_ribbon.png", 16.0, "1+0.0004*on"),
    ("scene09_command.png", 8.0, "1+0.00035*on"),
    ("scene09_emblem.png", 4.5, "1+0.0005*on"),
    ("scene10_booth.png", 11.5, "1+0.0002*on"),
]


def ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_ass() -> Path:
    path = BUILD / "titles.ass"
    header = f"""[Script Info]
Title: ACAMS Kairos Hero Film
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hero,Inter,{72},&H00FFFFFF,&H000000FF,&HAA0A0A0A,&H80000000,1,0,0,0,100,100,6,0,1,0,0,5,80,80,80,1
Style: Sub,Inter,{28},&H00D2B14A,&H000000FF,&HAA0A0A0A,&H80000000,0,0,0,0,100,100,4,0,1,0,0,5,80,80,80,1
Style: Blue,Inter,{26},&H00FFB46A,&H000000FF,&HAA0A0A0A,&H80000000,0,0,0,0,100,100,5,0,1,0,0,5,80,80,80,1
Style: Gold,Inter,{22},&H0033C4E0,&H000000FF,&HAA0A0A0A,&H80000000,1,0,0,0,100,100,8,0,1,0,0,2,80,80,70,1
Style: Stack,Inter,{30},&H00FFFFFF,&H000000FF,&HAA0A0A0A,&H80000000,1,0,0,0,100,100,3,0,1,0,0,5,80,80,80,1
Style: StackSub,Inter,{18},&H00C8C8C8,&H000000FF,&HAA0A0A0A,&H80000000,0,0,0,0,100,100,2,0,1,0,0,5,80,80,80,1
Style: Loop,Inter,{42},&H00FFFFFF,&H000000FF,&HAA0A0A0A,&H80000000,1,0,0,0,100,100,3,0,1,0,0,5,90,90,80,1
Style: LoopSub,Inter,{64},&H00FFB46A,&H000000FF,&HAA0A0A0A,&H80000000,1,0,0,0,100,100,4,0,1,0,0,5,80,80,80,1
Style: Brand,Inter,{18},&H00D2B14A,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,10,0,1,0,0,8,60,60,40,1
Style: Line,Arial,{20},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    def d(start, end, style, text, extra=""):
        events.append(
            f"Dialogue: 0,{ts(start)},{ts(end)},{style},,0,0,0,,{extra}{text}"
        )

    # Persistent brand
    d(1.2, 179.4, "Brand", "KAIROS  ·  CONNECTED FINANCIAL CRIME OPERATIONS", r"{\fad(800,800)}")

    # Scene 1 OST
    d(3.0, 8.6, "Hero", "FINANCIAL CRIME HAS CHANGED", r"{\fad(350,400)\fsp8}")
    d(9.2, 14.4, "Hero", "MONEY MOVES IN REAL TIME", r"{\fad(300,400)\fsp8}")
    d(15.0, 19.6, "Hero", "RISK MOVES WITH IT", r"{\fad(300,400)\fsp10}")

    # Scene 2
    d(24.0, 30.5, "Hero", "ONE CUSTOMER", r"{\fad(300,200)\fsp10}")
    d(31.0, 37.0, "Blue", "MANY SYSTEMS", r"{\fad(250,200)\fsp12}")
    d(37.6, 44.2, "Hero", "FRAGMENTED DECISIONS", r"{\fad(250,400)\fsp8}")

    # Scene 3 — aha
    d(57.2, 60.4, "Hero", "SAME CUSTOMER", r"{\fad(200,150)\fsp10}")
    d(60.5, 63.2, "Hero", "SAME NETWORK", r"{\fad(150,150)\fsp10}")
    d(63.3, 66.4, "Hero", "SAME CRIMINAL ACTIVITY", r"{\fad(150,300)\fsp6}")

    # Scene 4
    d(76.8, 82.0, "Hero", "KAIROS", r"{\fad(500,200)\fsp18\fs96}")
    d(78.6, 86.5, "Sub", "The Operating System for AI-Native Operations", r"{\fad(400,300)\pos(960,640)}")
    d(84.0, 89.6, "Blue", "INTELLIGENCE THAT OPERATES", r"{\fad(300,400)\pos(960,720)\fsp8}")

    # Scene 5
    d(100.5, 106.5, "Hero", "THE AGENT IS THE SURGEON", r"{\fad(400,250)\fsp6}")
    d(107.0, 111.0, "Sub", "The environment determines outcomes", r"{\fad(300,250)}")
    d(111.2, 116.4, "Hero", "KAIROS IS THE OPERATING ROOM", r"{\fad(300,400)\fsp5}")

    # Scene 6 uses the architecture plate's own labels.

    # Scene 7
    d(140.0, 146.5, "Hero", "CRIMINALS DON'T ORGANIZE BY DEPARTMENT", r"{\fad(300,250)\fsp2\fs48}")
    d(147.0, 151.0, "Sub", "Why do banks?", r"{\fad(250,250)}")
    d(151.4, 155.6, "Blue", "FRAML ENABLED BY KAIROS", r"{\fad(250,350)\fsp8}")

    # Scene 8 lifecycle
    d(157.5, 169.2, "Gold", "ONBOARD   ·   MONITOR   ·   INVESTIGATE   ·   ACT   ·   LEARN", r"{\fad(400,400)}")

    # Scene 9
    d(171.2, 173.6, "Hero", "ONE CUSTOMER", r"{\fad(200,120)\fsp10}")
    d(173.7, 175.8, "Hero", "ONE RISK VIEW", r"{\fad(150,120)\fsp10}")
    d(175.9, 177.8, "Hero", "ONE OPERATING SYSTEM", r"{\fad(150,200)\fsp6}")
    d(177.6, 179.9, "Hero", "KAIROS", r"{\fad(250,200)\fsp18\fs92}")
    d(178.2, 179.9, "Sub", "INTELLIGENCE THAT OPERATES", r"{\fad(250,200)\pos(960,640)}")

    # Booth loop
    d(180.4, 183.0, "Loop", "HOW MANY FINANCIAL CRIME SYSTEMS\\NDO YOU OPERATE TODAY?", r"{\fad(200,150)}")
    d(183.1, 185.4, "LoopSub", "5?     10?     20+?", r"{\fad(150,150)}")
    d(185.5, 187.6, "Loop", "WHAT IF THEY OPERATED AS ONE?", r"{\fad(150,150)}")
    d(187.7, 190.0, "Loop", "LET'S TALK ABOUT KAIROS", r"{\fad(150,400)\fsp4}")

    path.write_text(header + "\n".join(events) + "\n")
    return path


def ken_burns(src: Path, seconds: float, zoom_expr: str, dest: Path) -> None:
    frames = int(round(seconds * FPS))
    vf = (
        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
        f"crop={W * 2}:{H * 2},"
        f"zoompan=z='min({zoom_expr},1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(src),
            "-vf",
            vf,
            "-frames:v",
            str(frames),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def xfade_concat(clips: list[Path], dest: Path) -> None:
    # Probe durations
    durs = []
    for c in clips:
        r = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(c),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        durs.append(float(r.stdout.strip()))

    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]

    filters = []
    # offsets for xfade chain
    acc = durs[0]
    last = "[0:v]"
    for i in range(1, len(clips)):
        offset = acc - FADE
        out = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
        filters.append(
            f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.3f}{out}"
        )
        last = out
        acc = offset + durs[i]

    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[vout]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    subprocess.run(cmd, check=True)
    print("xfade duration target ~", acc)


def burn_and_mix(video: Path, ass: Path, audio: Path, dest: Path) -> None:
    ass_esc = str(ass).replace("\\", "/").replace(":", "\\:")
    fonts = "/usr/share/fonts/truetype/macos"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-vf",
            f"ass={ass_esc}:fontsdir={fonts},format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            str(TOTAL),
            "-movflags",
            "+faststart",
            str(dest),
        ],
        check=True,
    )


def main() -> None:
    ass = write_ass()
    print("ASS", ass)

    plates_dir = BUILD / "plates"
    plates_dir.mkdir(exist_ok=True)
    jobs = []
    clip_paths = []
    for i, (name, hold, zoom) in enumerate(PLATES):
        dest = plates_dir / f"{i:02d}_{Path(name).stem}.mp4"
        clip_paths.append(dest)
        if not dest.exists():
            jobs.append((IMG / name, hold, zoom, dest, i, name))

    def _job(item):
        src, hold, zoom, dest, i, name = item
        print("plate", i, name, hold, flush=True)
        ken_burns(src, hold, zoom, dest)

    if jobs:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(_job, jobs))

    bg = BUILD / "background.mp4"
    print("concat xfade")
    xfade_concat(clip_paths, bg)

    audio = AUDIO / "mix.wav"
    if not audio.exists():
        audio = AUDIO / "mix.mp3"
    dest = ROOT / "acams_kairos_hero_film.mp4"
    print("burn titles + mix")
    burn_and_mix(bg, ass, audio, dest)
    print("Wrote", dest)


if __name__ == "__main__":
    main()
