"""Royalty-free soundtrack generated in code: ambient pad, soft kick, hats, plucks, plus whooshes and impacts synced to the video."""
import wave
import numpy as np
from scipy import signal

SR = 44100
BPM = 112
BEAT = 60.0 / BPM
NOTE = {"A1": 55.0, "F1": 43.65, "C2": 65.41, "G1": 49.0}


def _t(n):
    return np.arange(n) / SR


def _hz(m):  # MIDI note -> frequency
    return 440.0 * 2 ** ((m - 69) / 12.0)


def _lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def _hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _sweep_noise(dur, f0, f1, rng, kind="low"):
    """Noise whose filter cutoff glides from f0 to f1 (whoosh / riser body)."""
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    blk, zi = 512, None
    for s in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (s / max(n, 1))
        b, a = signal.butter(2, min(fc, SR / 2 - 200) / (SR / 2), kind)
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        seg, zi = signal.lfilter(b, a, noise[s:s + blk], zi=zi)
        out[s:s + blk] = seg
    return out


def _place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0:
        return
    x = x[: len(buf) - i]
    l, r = gain * (1 - max(pan, 0)), gain * (1 + min(pan, 0))
    buf[i:i + len(x), 0] += x * l
    buf[i:i + len(x), 1] += x * r


def _reverb(x, rng, secs=1.7, wet=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / (SR * secs / 4.5))[:, None]
    ir[:, 0] = _lp(ir[:, 0], 5000)
    ir[:, 1] = _lp(ir[:, 1], 5000)
    out = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in (0, 1)], axis=1)
    return x * (1 - wet) + out * wet * 0.06


def make_soundtrack(events, total, out_wav, seed=1, vo_clips=None):
    rng = np.random.default_rng(seed)
    n = int((total + 1.5) * SR)
    t = _t(n)
    # --- harmony: Am9 - Fmaj7 - Cmaj7 - Gsus, each chord lasts 2 bars
    chords = [([57, 60, 64, 67, 71], "A1"), ([53, 57, 60, 64], "F1"), ([48, 55, 60, 64, 67], "C2"), ([55, 60, 62, 67], "G1")]
    seg = BEAT * 8
    pad = np.zeros((n, 2))
    bass = np.zeros(n)
    k = 0
    while k * seg < total + 1.5:
        notes, root = chords[k % 4]
        i0, i1 = int(k * seg * SR), min(int((k + 1) * seg * SR + SR), n)
        tt = _t(i1 - i0)
        env = np.minimum(1, tt / 1.0) * np.minimum(1, (tt[-1] - tt) / 1.0 + 0.0)
        env = np.clip(np.minimum(tt / 1.2, (tt[-1] - tt) / 1.2), 0, 1) ** 1.3
        voice = np.zeros((len(tt), 2))
        for j, m in enumerate(notes):
            for det, pan in ((-0.07, -0.5), (0.07, 0.5)):
                f = _hz(m) * 2 ** (det / 12)
                w = signal.sawtooth(2 * np.pi * f * tt + rng.random() * 6)
                voice[:, 0] += w * (1 - max(pan, 0) * 0.8)
                voice[:, 1] += w * (1 + min(pan, 0) * 0.8)
        cutoff = 900 + 700 * np.sin(2 * np.pi * tt / (seg * 1.7) + k)
        # time-varying cutoff approximated with two filtered copies cross-faded
        lo, hi = _lp(voice, 700, 2), _lp(voice, 2200, 2)
        mix = ((cutoff - 200) / 1400)[:, None]
        pad[i0:i1] += (lo * (1 - mix) + hi * mix) * env[:, None] * 0.028
        bass[i0:i1] += np.sin(2 * np.pi * NOTE[root] * tt) * env * 0.55
        k += 1
    # --- drums
    kick = np.zeros(n)
    hats = np.zeros(n)
    ph = np.full(n, 10.0)  # seconds since last kick (for sidechain)
    nb = int((total + 1.5) / BEAT) + 1
    for b in range(nb):
        s = int(b * BEAT * SR)
        if s >= n:
            break
        ln = min(int(0.32 * SR), n - s)
        tk = _t(ln)
        f = 48 + 100 * np.exp(-tk * 28)
        kick[s:s + ln] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 11) * (0.55 if b >= 2 else 0.0)
        ph[s:] = np.minimum(ph[s:], _t(n - s))
        h = int((b + 0.5) * BEAT * SR)
        if h < n and b >= 4:
            hl = min(int(0.06 * SR), n - h)
            hats[h:h + hl] += _hp(rng.standard_normal(hl), 7000) * np.exp(-_t(hl) * 70) * 0.05
    duck = 1 - 0.6 * np.exp(-ph / 0.16)
    pad *= duck[:, None]
    bass *= duck
    # --- plucks (echoing 8th-note arpeggio)
    pl = np.zeros((n, 2))
    scale = [69, 72, 76, 79, 81, 84]
    step = BEAT / 2
    for q in range(int((total + 1.5) / step)):
        if q < 8 or rng.random() < 0.35:
            continue
        m = scale[(q * 3 + int(rng.integers(0, 3))) % len(scale)]
        ln = int(0.4 * SR)
        tk = _t(ln)
        x = (np.sin(2 * np.pi * _hz(m) * tk) + 0.35 * signal.sawtooth(2 * np.pi * _hz(m) * tk)) * np.exp(-tk * 9) * 0.05
        _place(pl, x, q * step, 1.0, pan=float(rng.uniform(-0.5, 0.5)))
        _place(pl, x * 0.4, q * step + step * 1.5, 1.0, pan=float(rng.uniform(-0.6, 0.6)))
    music = pad + pl
    music = _reverb(music, rng)
    music[:, 0] += bass + kick + hats
    music[:, 1] += bass + kick + hats
    # opening boom
    tk = _t(int(1.4 * SR))
    boom = np.sin(2 * np.pi * (42 + 30 * np.exp(-tk * 3)) * tk) * np.exp(-tk * 2.2) * 0.7
    _place(music, boom, 0.0)
    # --- sound effects synced to the picture
    fx = np.zeros((n, 2))
    for ev in events:
        kind, at = ev["kind"], float(ev["t"])
        if kind == "whoosh":
            d = 0.6
            w = _sweep_noise(d, 250, 6500, rng, "low") * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) ** 1.5
            _place(fx, w * 0.5, max(at - 0.18, 0), 1.0, pan=float(ev.get("pan", 0)))
        elif kind == "hit":
            ln = int(0.5 * SR)
            tk = _t(ln)
            x = np.sin(2 * np.pi * (70 + 60 * np.exp(-tk * 20)) * tk) * np.exp(-tk * 7) * 0.75
            x += _hp(rng.standard_normal(ln), 2500) * np.exp(-tk * 45) * 0.18
            _place(fx, x * float(ev.get("g", 1.0)), at)
        elif kind == "riser":
            d = float(ev.get("dur", 1.5))
            m = int(d * SR)
            body = _sweep_noise(d, 300, 9000, rng, "low") * (np.linspace(0, 1, m) ** 2.2)
            tone = np.sin(2 * np.pi * np.cumsum(180 + 1100 * np.linspace(0, 1, m) ** 2) / SR) * (np.linspace(0, 1, m) ** 2.5) * 0.35
            _place(fx, body * 0.6 + tone * 0.5, at)
        elif kind == "click":
            ln = int(0.08 * SR)
            _place(fx, _hp(rng.standard_normal(ln), 1500) * np.exp(-_t(ln) * 80) * 0.5, at)
        elif kind == "sting":
            ln = int(2.2 * SR)
            tk = _t(ln)
            x = sum(np.sin(2 * np.pi * f * tk) for f in (440, 659.3, 880, 1318.5)) * np.exp(-tk * 2.2) * 0.07
            _place(fx, x, at)
    fx = _reverb(fx, rng, 1.2, 0.18)
    if vo_clips:
        vb = np.zeros(n)
        for vt, vx in vo_clips:
            i = int(vt * SR)
            seg = vx[: max(0, n - i)]
            vb[i:i + len(seg)] += seg
        env = np.clip(_lp(np.abs(vb), 12, 1) / 0.12, 0, 1)  # follows the voice: music dips while someone speaks
        music = music * (1 - 0.6 * env)[:, None] * 0.5
        fx = fx * (1 - 0.35 * env)[:, None] * 0.85
        mix = music + fx
        mix[:, 0] += vb
        mix[:, 1] += vb
        mix = np.tanh(mix * 1.1) / 1.1
    else:
        mix = music + fx
        mix = np.tanh(mix * 1.3) / 1.3
    f_in, f_out = int(0.25 * SR), int(1.4 * SR)
    mix[:f_in] *= np.linspace(0, 1, f_in)[:, None]
    end = int((total + 0.4) * SR)
    mix[end - f_out:end] *= np.linspace(1, 0, f_out)[:, None]
    mix[end:] = 0
    mix = mix[:end] / max(np.abs(mix).max(), 1e-6) * 0.85
    data = (mix * 32767).astype("<i2")
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return out_wav
