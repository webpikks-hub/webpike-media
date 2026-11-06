"""Original background music for Webpikë videos (no copyright issues).

Usage: python3 make_music.py OUT.wav DURATION_SECONDS [SEED] [CUT_TIMES_COMMA_SEPARATED]
Generates an upbeat, clean electronic loop (kick, hats, bass, chord stabs) with a
fade in/out and a soft "whoosh" at each scene cut. SEED changes key/chords/tempo
so every video sounds a bit different.
"""
import sys, wave, random
import numpy as np

SR = 44100


def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e


def tone(freq, n, kind="saw"):
    t = np.arange(n) / SR
    if kind == "sine":
        return np.sin(2 * np.pi * freq * t)
    if kind == "tri":
        return 2 * np.abs(2 * ((freq * t) % 1) - 1) - 1
    # soft saw (few harmonics)
    return sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 7)) * 0.6


def add(buf, sig, start):
    s = int(start * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(sig))
    buf[s:e] += sig[: e - s]


def main():
    out = sys.argv[1]
    dur = float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    cuts = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else []
    rnd = random.Random(seed)

    bpm = rnd.choice([100, 105, 110, 115, 120])
    beat = 60 / bpm
    root = rnd.choice([45, 47, 48, 50, 52])  # MIDI A2..E3
    progs = [[0, 5, 7, 3], [0, 7, 9, 5], [0, 3, 5, 7], [0, 9, 5, 7]]
    prog = rnd.choice(progs)
    minor = rnd.random() < 0.5
    third = 3 if minor else 4
    mf = lambda m: 440 * 2 ** ((m - 69) / 12)

    n = int(dur * SR)
    L = np.zeros(n); R = np.zeros(n)

    nbeats = int(dur / beat) + 1
    for b in range(nbeats):
        t0 = b * beat
        bar = b // 4
        chord_root = root + prog[bar % 4]
        # kick on every beat
        kn = int(0.25 * SR)
        tt = np.arange(kn) / SR
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * 0.9
        add(L, kick, t0); add(R, kick, t0)
        # clap on 2 and 4
        if b % 2 == 1:
            cn = int(0.18 * SR)
            clap = np.random.default_rng(seed + b).standard_normal(cn) * env(cn, 0.001, 0.05) * 0.25
            add(L, clap, t0); add(R, clap * 0.9, t0)
        # hats on off-beats
        for k, off in enumerate((0.5, 0.75) if b % 4 == 3 else (0.5,)):
            hn = int(0.06 * SR)
            hat = np.random.default_rng(seed * 7 + b * 3 + k).standard_normal(hn)
            hat = np.diff(np.concatenate([[0], hat])) * env(hn, 0.001, 0.015) * 0.18
            add(L, hat * 0.7, t0 + off * beat); add(R, hat, t0 + off * beat)
        # bass: root on beat, octave on the "and"
        bn = int(beat * 0.45 * SR)
        bass = tone(mf(chord_root - 12), bn, "tri") * env(bn, 0.005, 0.18) * 0.35
        add(L, bass, t0); add(R, bass, t0)
        bass2 = tone(mf(chord_root), bn, "tri") * env(bn, 0.005, 0.12) * 0.18
        add(L, bass2, t0 + beat / 2); add(R, bass2, t0 + beat / 2)
        # chord stabs (off-beat)
        if b % 2 == 0:
            sn = int(beat * 0.35 * SR)
            stab = sum(tone(mf(chord_root + 12 + iv), sn) for iv in (0, third, 7)) * env(sn, 0.004, 0.09) * 0.07
            add(L, stab, t0 + beat * 0.5); add(R, stab * 0.8, t0 + beat * 0.5 + 0.01)
        # soft pad per bar
        if b % 4 == 0:
            pn = int(beat * 4 * SR)
            pad = sum(tone(mf(chord_root + 12 + iv), pn, "sine") for iv in (0, third, 7, 12))
            pe = np.minimum(1, np.arange(pn) / (0.3 * SR)) * np.minimum(1, (pn - np.arange(pn)) / (0.3 * SR))
            add(L, pad * pe * 0.035, t0); add(R, pad * pe * 0.035, t0)

    # whoosh on cuts
    for c in cuts:
        wn = int(0.5 * SR)
        noise = np.random.default_rng(int(c * 100)).standard_normal(wn)
        # simple low-pass by cumulative smoothing, rising envelope
        k = 12
        noise = np.convolve(noise, np.ones(k) / k, mode="same")
        we = np.sin(np.linspace(0, np.pi, wn)) ** 2 * 0.35
        add(L, noise * we, c - 0.35); add(R, noise[::-1] * we, c - 0.35)

    mix = np.stack([L, R], axis=1)
    # fades
    f = int(0.4 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]
    fo = int(1.2 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    # soft clip + normalize
    mix = np.tanh(mix * 1.2)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.85
    data = (mix * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"{out}: {dur}s bpm={bpm} root={root} minor={minor}")


main()
