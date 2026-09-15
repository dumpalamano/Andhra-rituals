#!/usr/bin/env python3
"""Premium enterprise score: atmospheric pulse → restrained rise → quiet triumph."""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "audio" / "score.wav"
OUT.parent.mkdir(parents=True, exist_ok=True)

SR = 48000
DURATION = 190.0
N = int(SR * DURATION)
T = np.arange(N, dtype=np.float64) / SR


def env_adsr(t, a=0.4, d=0.8, s=0.7, r=4.0, peak=1.0):
    e = np.ones_like(t) * s
    a_mask = t < a
    e[a_mask] = np.clip(t[a_mask] / max(a, 1e-6), 0, 1)
    d_mask = (t >= a) & (t < a + d)
    e[d_mask] = 1 - (1 - s) * ((t[d_mask] - a) / max(d, 1e-6))
    r_start = t[-1] - r if t.size else 0
    r_mask = t > r_start
    if r_mask.any():
        e[r_mask] *= np.clip(1 - (t[r_mask] - r_start) / max(r, 1e-6), 0, 1)
    return e * peak


def sine(freq, amp=1.0, phase=0.0):
    return np.sin(2 * np.pi * freq * T + phase) * amp


def detuned_pad(freqs, amp=0.12):
    sig = np.zeros(N)
    for f in freqs:
        for cents, a in ((-9, 0.45), (0, 1.0), (11, 0.4)):
            ff = f * (2 ** (cents / 1200))
            sig += sine(ff, amp * a)
    return sig / max(len(freqs), 1)


def soft_noise(amp=0.04):
    rng = np.random.default_rng(42)
    n = rng.standard_normal(N)
    kernel = np.exp(-np.arange(600) / 90.0)
    kernel /= kernel.sum()
    return np.convolve(n, kernel, mode="same") * amp


def pulse(bpm, amp, start, end, freq=48.0):
    sig = np.zeros(N)
    period = 60.0 / bpm
    t0 = start
    while t0 < end:
        i0 = int(t0 * SR)
        length = int(0.18 * SR)
        i1 = min(N, i0 + length)
        if i0 >= N:
            break
        tt = np.arange(i1 - i0) / SR
        hit = np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 18) * amp
        sig[i0:i1] += hit
        t0 += period
    return sig


def scene_gain(points):
    """Linear envelope from (time, gain) breakpoints."""
    ts, gs = zip(*points)
    return np.interp(T, ts, gs)


def main() -> None:
    rng = np.random.default_rng(7)

    # Opening drone — midnight
    drone = detuned_pad([55.0, 82.5, 110.0], amp=0.22) * scene_gain(
        [(0, 0.0), (1.5, 0.7), (20, 0.85), (65, 0.9), (90, 0.7), (170, 0.8), (180, 0.55), (190, 0.0)]
    )

    # Fifth pad that opens at the architecture reveal
    fifths = detuned_pad([164.8, 220.0, 329.6], amp=0.10) * scene_gain(
        [(0, 0.0), (20, 0.15), (45, 0.25), (65, 0.35), (78, 0.85), (115, 0.7), (155, 0.8), (180, 0.9), (190, 0.0)]
    )

    # High shimmer (gold)
    shimmer = (
        sine(1318.5, 0.015)
        + sine(1568.0, 0.01)
        + sine(2093.0, 0.006)
    ) * scene_gain([(0, 0.0), (10, 0.4), (90, 0.5), (170, 0.9), (182, 0.4), (190, 0)])
    shimmer *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * T)

    # Filtered air
    air = soft_noise(amp=0.035) * scene_gain(
        [(0, 0.2), (20, 0.45), (90, 0.35), (135, 0.5), (190, 0.1)]
    )

    # Low atmospheric pulse that accelerates
    p1 = pulse(52, 0.16, 0.8, 45)
    p2 = pulse(64, 0.18, 45, 90)
    p3 = pulse(76, 0.16, 90, 155)
    p4 = pulse(84, 0.14, 155, 180)
    beats = p1 + p2 + p3 + p4

    # Confident rise around Kairos introduction
    rise_t = np.clip((T - 64) / 14.0, 0, 1)
    rise = (sine(130.8, 0.08) + sine(196.0, 0.06) + sine(261.6, 0.04)) * (rise_t**2) * scene_gain(
        [(0, 0), (64, 0), (78, 1), (92, 0.35), (190, 0.15)]
    )

    # Restrained triumph — major add9, not Hollywood
    triumph = detuned_pad([130.8, 164.8, 196.0, 293.7], amp=0.14) * scene_gain(
        [(0, 0), (165, 0), (172, 0.85), (180, 0.7), (188, 0.2), (190, 0)]
    )

    # Sparse high ticks like F1 telemetry
    ticks = np.zeros(N)
    for t0 in np.arange(11, 180, 3.4):
        i0 = int(t0 * SR)
        n = int(0.012 * SR)
        if i0 + n < N:
            ticks[i0 : i0 + n] += np.hanning(n) * 0.045 * rng.uniform(0.7, 1.0)

    mix = drone + fifths + shimmer + air + beats + rise + triumph + ticks

    # Stereo: slight detune / delay
    delay = int(0.014 * SR)
    left = mix.copy()
    right = np.zeros_like(mix)
    right[delay:] = mix[:-delay] * 0.96
    right[:-delay] += mix[delay:] * 0.08

    stereo = np.stack([left, right], axis=1)
    peak = np.max(np.abs(stereo)) + 1e-9
    stereo = stereo / peak * 0.55
    # fade tails
    fade = int(0.6 * SR)
    stereo[:fade] *= np.linspace(0, 1, fade)[:, None]
    stereo[-int(1.8 * SR) :] *= np.linspace(1, 0, int(1.8 * SR))[:, None]

    pcm = np.clip(stereo, -1, 1)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm16.tobytes())
    print("Wrote", OUT, "peak", float(peak))


if __name__ == "__main__":
    main()
