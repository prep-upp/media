# Prep'Up brag soundtrack: 120 BPM, A minor, 21 s. Every event sits on the beat grid from t=0.
import json, sys, wave
import numpy as np

SR, BPM, DUR = 48000, 120, 21.0
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)

def buf(): return np.zeros((N, 2))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a, d, sus=0.0, rel=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / d))
    if rel: e *= np.clip((n / SR - t) / rel, 0, 1)
    return e
def put(b, x, t, pan=0.0, g=1.0):
    i = int(round(t * SR)); x = x[: max(0, N - i)]
    b[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    b[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))
def lp_unused(x, a):  # unused
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def lp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / cutoff) ** 4), len(x))

# chords per bar (2 s): Am F C G
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOT = [45, 41, 48, 43]
def chord_at(t): return int(t // (4 * BEAT)) % 4

pad, bass, drums, keys, fx = buf(), buf(), buf(), buf(), buf()

# pad: soft detuned saws, low-passed, whole piece
for bar in range(11):
    t0 = bar * 4 * BEAT; n = int(4 * BEAT * SR) + SR // 4
    tt = np.arange(n) / SR; c = CH[bar % 4]; x = np.zeros(n)
    for m in c + [c[0] + 12]:
        for det in (-0.08, 0.08):
            ph = (hz(m + det) * tt) % 1.0; x += 2 * ph - 1
    x = lp_fast(x, 1400 if t0 >= 3 else 900) * env(n, 0.25, 9, 1, 0.3) * 0.05
    put(pad, x, t0, 0, 1)

# kick + sidechain from 3.0 to 20.0
kick_times = [b * BEAT for b in range(6, 40)]
for t in kick_times:
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 48 + 110 * np.exp(-tt * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
    put(drums, x * 0.55, t)
duck = np.ones(N)
for t in kick_times:
    i = int(t * SR); n = int(0.3 * SR); tt = np.arange(n) / SR
    duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.55 * np.exp(-tt * 14))

# hats on offbeats, clap on 2 & 4
for b in range(6, 40):
    n = int(0.06 * SR); x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 70)
    x = x - lp_fast(x, 7000)
    put(drums, x * 0.07, b * BEAT + BEAT / 2, 0.3)
    if b % 2 == 1:
        n = int(0.2 * SR); x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 22)
        x = lp_fast(x - lp_fast(x, 900), 6000)
        put(drums, x * 0.12, b * BEAT, -0.1)

# bass: 8th-note pulse on roots
for k in range(12, 80):
    t = k * BEAT / 2
    if t >= 20.0: break
    m = ROOT[chord_at(t)] - 12 + (12 if k % 4 == 3 else 0)
    n = int(BEAT / 2 * SR * 0.95); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * hz(m) * tt) + 0.3 * np.sin(4 * np.pi * hz(m) * tt)
    put(bass, x * env(n, 0.005, 0.18, 0.4, 0.03) * 0.2, t)

# pluck voice (soft, round)
def pluck(m, n_sec=0.5, bright=1.0):
    n = int(n_sec * SR); tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * hz(m) * h * tt) * (bright ** (h - 1)) / h for h in (1, 2, 3))
    return x * env(n, 0.002, 0.16)

# hook: two gentle notes + landing on 2.0
for t, m in [(0.0, 76), (0.5, 72), (1.0, 69), (1.5, 72)]:
    put(keys, pluck(m, 0.6, 0.4) * 0.16, t, 0.2)
for m in (69, 72, 76, 81):
    put(keys, pluck(m, 1.2, 0.5) * 0.12, 2.0, 0)

# melody from 3.0: A-minor pentatonic motif on 8ths, sparse
motif = [76, None, 74, 72, None, 69, 72, None]
for k in range(6, 40):
    t = k * BEAT; m = motif[k % 8]
    if m is None or 6.0 <= t < 9.0: continue  # leave room for typing ticks
    put(keys, pluck(m, 0.45, 0.35) * 0.10, t, -0.25)

# typing ticks: chord tones, on 16ths (times from the composition)
chars = json.load(open(sys.argv[1]))
for i, (t, _f, _p) in enumerate(chars):
    c = CH[chord_at(t)]; m = c[i % 3] + 24
    put(fx, pluck(m, 0.12, 0.2) * 0.07, t, 0.35 if i % 2 else -0.35)

# tap on the button
put(fx, pluck(84, 0.25, 0.3) * 0.12, 10.5)
# cards: rising chord tones, one per beat
for t, m in [(15.75, 69), (16.25, 72), (16.75, 76)]:
    put(keys, pluck(m + 12, 0.5, 0.4) * 0.13, t, 0)

# whooshes into each cut (filtered noise swell ending on the beat)
for t in (3.0, 6.0, 11.0, 15.5, 18.0):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    x = lp_fast(rng.standard_normal(n), 2500) * (tt / tt[-1]) ** 2.5
    put(fx, x * 0.08, t - 0.5, 0)

# outro: soft impact + final Am chord ringing out
n = int(0.6 * SR); tt = np.arange(n) / SR
put(drums, np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 6) * 0.5, 18.0)
for m in (57, 64, 69, 72, 76):
    put(keys, pluck(m, 3.0, 0.5) * 0.09, 20.0, 0)

# light shared room on keys + fx so they sit in the same space
def reverb(x, sec=1.4, mix=0.22):
    n = int(sec * SR); ir = rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / SR * 4.5)[:, None]
    out = np.empty_like(x)
    for ch in range(2):
        L = len(x) + n
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], L) * np.fft.rfft(ir[:, ch], L), L)[: len(x)] * 0.02
    return x + out * mix / 0.22 * 0.22

wet = reverb(keys + fx + pad * 0.5)
mix = (pad * 0.5 + bass) * duck[:, None] + drums + wet
mix[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))[:, None]
mix /= np.max(np.abs(mix)) / 0.89

with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', np.max(np.abs(mix)))
