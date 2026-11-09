# Alternative soundtracks on the same 120 BPM grid (beat 0.5 s), so every cut, tick and tap still lands.
# usage: python3 synth_styles.py <events.json> <lofi|pop|trap> <out.wav>
import json, sys, wave
import numpy as np

ev = json.load(open(sys.argv[1])); STYLE = sys.argv[2]
SR, BEAT, DUR = 48000, 0.5, ev['dur']
BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(11)
REV, OUT = ev['reveal'], ev['outro']
END = OUT + 2.0  # groove stops, last chord rings

def buf(): return np.zeros((N, 2))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def tt(sec): return np.arange(int(sec * SR)) / SR
def env(n, a, d, sus=0.0, rel=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / d))
    if rel: e *= np.clip((n / SR - t) / rel, 0, 1)
    return e
def put(b, x, t, pan=0.0, g=1.0):
    i = int(round(t * SR))
    if i >= N: return
    x = x[: N - i]
    b[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    b[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if hi: g /= np.sqrt(1 + (f / hi) ** 4)
    if lo: g *= (f / lo) ** 2 / np.sqrt(1 + (f / lo) ** 4)
    return np.fft.irfft(X * g, len(x))
def noise(sec): return rng.standard_normal(int(sec * SR))

# --- instruments ---
def rhodes(m, sec, vel=1.0):
    t = tt(sec); f = hz(m)
    mod = 1.8 * np.exp(-t * 3) * np.sin(2 * np.pi * f * t)
    x = np.sin(2 * np.pi * f * t + mod) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
    return x * env(len(t), 0.004, 1.2, 0.0, 0.15) * (1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)) * vel
def bell(m, sec=1.2):
    t = tt(sec); f = hz(m)
    x = np.sin(2 * np.pi * f * t + 2.2 * np.exp(-t * 5) * np.sin(2 * np.pi * 3.5 * f * t))
    return x * env(len(t), 0.002, 0.45)
def pluck(m, sec=0.4, bright=0.4):
    t = tt(sec)
    x = sum(np.sin(2 * np.pi * hz(m) * h * t) * bright ** (h - 1) / h for h in (1, 2, 3, 4))
    return x * env(len(t), 0.002, 0.12)
def supersaw(ms, sec, cutoff=3500):
    t = tt(sec); x = np.zeros(len(t))
    for m in ms:
        for d in (-0.18, -0.09, 0, 0.09, 0.18):
            x += 2 * ((hz(m + d) * t + rng.random()) % 1.0) - 1
    return filt(x, hi=cutoff) / (len(ms) * 3)
def kick(punch=110, decay=9, base=48):
    t = tt(0.4); f = base + punch * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)
def snare(dark=False):
    t = tt(0.25)
    x = filt(noise(0.25), lo=900, hi=4000 if dark else 8000) * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    return x
def clap():
    x = np.zeros(int(0.3 * SR))
    for k, d in enumerate((0, 0.011, 0.022)):
        n = filt(noise(0.2), lo=1000, hi=7000) * np.exp(-tt(0.2) * (40 if k < 2 else 14))
        i = int(d * SR); x[i:i + len(n)] += n[: len(x) - i]
    return x
def hat(open_=False, dark=False):
    sec = 0.25 if open_ else 0.05
    x = filt(noise(sec), lo=7000, hi=12000 if not dark else 9000) * np.exp(-tt(sec) * (12 if open_ else 80))
    return x
def bass808(m, sec, glide_from=None):
    t = tt(sec); f = np.full(len(t), hz(m))
    if glide_from is not None: f = hz(m) + (hz(glide_from) - hz(m)) * np.exp(-t * 18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.004, 0.9, 0.0, 0.08)
    return np.tanh(2.2 * x) * 0.8
def sub(m, sec):
    t = tt(sec)
    return (np.sin(2 * np.pi * hz(m) * t) + 0.25 * np.sin(4 * np.pi * hz(m) * t)) * env(len(t), 0.005, 0.25, 0.5, 0.04)
def riser(sec):
    t = tt(sec); x = noise(sec)
    return filt(x, lo=400, hi=6000) * (t / t[-1]) ** 2.2
def whoosh(): return riser(0.5) * 0.9
def crash():
    return filt(noise(1.8), lo=4000) * np.exp(-tt(1.8) * 2.2)

def reverb(x, sec=1.6, decay=3.8):
    n = int(sec * SR); out = np.empty_like(x); L = len(x) + n
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * decay)
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], L) * np.fft.rfft(ir, L), L)[: len(x)] * 0.02
    return out
def duck_curve(times, depth, rel):
    d = np.ones(N)
    for t in times:
        i = int(t * SR); n = int(0.45 * SR); k = 1 - depth * np.exp(-np.arange(n) / SR * rel)
        d[i:i + n] = np.minimum(d[i:i + n], k[: N - i])
    return d

ticks, taps, cuts, hook = sorted(ev['ticks']), ev['taps'], ev['cuts'], ev['hook']
beats = lambda a, b: [k * BEAT for k in range(int(round(a / BEAT)), int(round(b / BEAT)))]
near_typing = lambda t: any(abs(t - x) < 0.3 for x in ticks)
bar_of = lambda t: int(t // BAR)

keys, drums, bass, fx = buf(), buf(), buf(), buf()

if STYLE == 'lofi':
    # warm study beat: Rhodes 7th chords, half-time boom-bap, vinyl, everything soft
    CH = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
    for b in range(int(DUR // BAR) + 1):
        t0 = b * BAR
        if t0 >= END + 0.1: break
        for j, m in enumerate(CH[b % 4]):
            put(keys, rhodes(m, BAR + 0.3, 0.16 if t0 < REV else 0.2), t0 + 0.012 * j, -0.3 + 0.2 * j)
    for i, t in enumerate(hook):
        put(keys, bell([76, 79, 84][i], 1.4) * 0.14, t, 0.2)
    for t in beats(REV, END):
        pos = round((t % BAR) / BEAT)
        if pos == 0: put(drums, kick(80, 7, 46) * 0.6, t)
        if pos == 1: put(drums, kick(80, 7, 46) * 0.4, t + BEAT / 2)
        if pos == 2: put(drums, snare(dark=True) * 0.32, t, -0.05)
        put(drums, hat(dark=True) * 0.05, t, 0.25); put(drums, hat(dark=True) * 0.03, t + BEAT / 2, 0.25)
        if pos in (0, 2): put(bass, sub([41, 40, 38, 36][bar_of(t) % 4], 0.9) * 0.28, t)
    mel = [72, None, 76, 74, None, 72, 69, None]
    for k, t in enumerate(beats(REV, OUT)):
        m = mel[k % 8]
        if m and not near_typing(t): put(keys, bell(m + 12, 0.9) * 0.05, t, 0.35)
    for i, t in enumerate(ticks): put(fx, rhodes(CH[bar_of(t) % 4][i % 4] + 24, 0.25, 0.09), t, 0.3 if i % 2 else -0.3)
    for t in taps: put(fx, bell(84, 0.6) * 0.09, t)
    for t in cuts: put(fx, filt(whoosh(), hi=3000) * 0.05, t - 0.5)
    for m in (53, 60, 64, 69, 72): put(keys, rhodes(m, 3.2, 0.14), END)
    vinyl = np.zeros(N)
    for i in rng.integers(0, N, int(DUR * 9)): vinyl[i] = rng.uniform(-1, 1)
    vinyl = filt(vinyl, lo=1500, hi=6000) * 0.5 + filt(noise(DUR), hi=3000)[:N] * 0.004
    fx[:, 0] += vinyl; fx[:, 1] += vinyl
    dk = duck_curve([t for t in beats(REV, END) if round((t % BAR) / BEAT) == 0], 0.3, 6)
    mix = (keys + bass) * dk[:, None] + drums + fx + reverb(keys + fx) * 0.35
    for ch in range(2): mix[:, ch] = filt(mix[:, ch], hi=7500)  # soft top end

elif STYLE == 'pop':
    # bright future-bass pop: C major, pumping supersaw chords, riser into the drop at the reveal
    CH = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]  # C G Am F
    ROOT = [36, 31, 33, 29]
    put(fx, riser(REV) * 0.12, 0)
    for i, t in enumerate(hook):
        put(keys, supersaw([[72], [76], [79, 84]][i], 0.45, 6000) * 0.5 * env(int(0.45 * SR), 0.003, 0.15), t)
    for t in beats(REV, END):
        c = CH[bar_of(t) % 4]
        put(keys, supersaw(c, BEAT, 4200) * 0.55, t)
        put(drums, kick(130, 10, 50) * 0.6, t)
        put(drums, hat(open_=True) * 0.06, t + BEAT / 2, 0.3)
        if round((t % BAR) / BEAT) in (1, 3): put(drums, clap() * 0.3, t, -0.1)
        put(bass, sub(ROOT[bar_of(t) % 4], BEAT * 0.9) * 0.3, t)
        put(bass, sub(ROOT[bar_of(t) % 4] + 12, BEAT * 0.4) * 0.12, t + BEAT / 2)
    put(drums, crash() * 0.12, REV)
    arp = [0, 1, 2, 3, 2, 1, 2, 3]
    for k in range(int(REV / (BEAT / 2)), int(OUT / (BEAT / 2))):
        t = k * BEAT / 2
        if near_typing(t): continue
        c = CH[bar_of(t) % 4]; put(keys, pluck(c[arp[k % 8]] + 12, 0.3, 0.5) * 0.09, t, 0.3 if k % 2 else -0.3)
    for i, t in enumerate(ticks): put(fx, pluck(CH[bar_of(t) % 4][i % 4] + 24, 0.15, 0.3) * 0.08, t, 0.3 if i % 2 else -0.3)
    for t in taps: put(fx, pluck(84, 0.3, 0.6) * 0.12, t)
    for t in cuts: put(fx, whoosh() * 0.07, t - 0.5)
    put(drums, crash() * 0.12, OUT)
    put(keys, supersaw([60, 64, 67, 72, 76], 3.0, 3000) * 0.6 * env(int(3 * SR), 0.01, 1.2), END)
    dk = duck_curve(beats(REV, END), 0.7, 9)
    mix = (keys + bass) * dk[:, None] + drums + fx + reverb(keys + fx) * 0.3

elif STYLE == 'trap':
    # dark half-time trap: piano/bell over Am, 808 glides, 16th hats with 32nd rolls
    CH = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]  # Am F G Em
    ROOT808 = [33, 29, 31, 28]
    for b in range(int(DUR // BAR) + 1):
        t0 = b * BAR
        if t0 >= END + 0.1: break
        for j, m in enumerate(CH[b % 4]):
            put(keys, rhodes(m + 12, 1.0, 0.12) , t0 + 0.01 * j, -0.2 + 0.2 * j)
            put(keys, rhodes(m + 12, 1.0, 0.08), t0 + BAR / 2 + 0.01 * j, -0.2 + 0.2 * j)
    for i, t in enumerate(hook):
        put(keys, bell([81, 79, 76][i], 1.2) * 0.14, t, 0.1)
    put(bass, bass808(33, 2.0) * 0.32, 1.5)  # 808 hit under the 4th hook line
    kpat = [0, 3, 6, 10]  # 16th steps in a bar (16 steps)
    for b in range(int(REV // BAR), int(END // BAR) + 1):
        t0 = b * BAR
        for s in range(16):
            t = t0 + s * BEAT / 4
            if t < REV or t >= END: continue
            if s in kpat: put(drums, kick(90, 8, 45) * 0.45, t)
            if s == 8: put(drums, clap() * 0.32, t)
            roll = (s >= 12 and b % 2 == 1)
            if roll:
                put(drums, hat() * 0.05, t, 0.3); put(drums, hat() * 0.04, t + BEAT / 8, 0.3)
            elif s % 2 == 0 or s in (5, 11):
                put(drums, hat() * (0.06 if s % 4 == 0 else 0.04), t, 0.3)
        if REV <= t0 < END:
            r = ROOT808[b % 4]; prev = ROOT808[(b - 1) % 4]
            put(bass, bass808(r, 1.4, glide_from=prev) * 0.4, t0)
            put(bass, bass808(r, 0.5) * 0.28, t0 + 3 * BEAT / 4 * 2)
    mel = [76, None, 72, None, 74, 72, None, 69]
    for k, t in enumerate(beats(REV, OUT)):
        m = mel[k % 8]
        if m and not near_typing(t): put(keys, bell(m + 12, 0.8) * 0.06, t, 0.3)
    for i, t in enumerate(ticks): put(fx, bell(CH[bar_of(t) % 4][i % 3] + 24, 0.25) * 0.06, t, 0.3 if i % 2 else -0.3)
    for t in taps: put(fx, bell(88, 0.5) * 0.08, t)
    for t in cuts: put(fx, filt(whoosh(), hi=4000) * 0.06, t - 0.5)
    for m in (57, 64, 69, 72): put(keys, rhodes(m + 12, 3.0, 0.12), END)
    put(bass, bass808(33, 2.5) * 0.35, END)
    dk = duck_curve([t for t in beats(REV, END) if round((t % BAR) / BEAT) == 0], 0.35, 5)
    mix = keys * dk[:, None] + bass + drums + fx + reverb(keys + fx) * 0.3
else:
    sys.exit('unknown style')

mix[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.2) / np.tanh(1.2) * 0.89  # gentle glue, no hard clipping
with wave.open(sys.argv[3], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', STYLE)
