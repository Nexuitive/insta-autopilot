"""Voiceover: one spoken clip per beat. Microsoft Edge neural voices first, Gemini TTS as backup; clips are trimmed and levelled."""
import asyncio, base64, os, subprocess, tempfile
import numpy as np
import requests
from scipy import signal

SR = 44100
DEFAULTS = {"engines": ["gemini", "edge"], "gemini": "Fenrir", "edge": "en-US-AndrewMultilingualNeural", "edge_rate": "+10%", "edge_pitch": "-2Hz"}


def _decode(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def prep(x):
    """Trim silence, remove rumble, level and fade the clip."""
    if len(x) < SR // 10:
        raise ValueError("voice clip too short")
    env = np.convolve(np.abs(x), np.ones(441) / 441, mode="same")
    idx = np.where(env > 0.012 * max(env.max(), 1e-6) + 0.004)[0]
    x = x[max(idx[0] - 1500, 0): idx[-1] + 2500] if len(idx) else x
    b, a = signal.butter(2, 90 / (SR / 2), "high")
    x = signal.lfilter(b, a, x)
    lo = signal.lfilter(*signal.butter(2, 260 / (SR / 2), "low"), x)
    bp = signal.lfilter(*signal.butter(2, [2200 / (SR / 2), 5200 / (SR / 2)], "band"), x)
    x = x + 0.38 * lo + 0.28 * bp  # warmth and presence, so the voice sounds fuller and bolder
    x = x / max(np.abs(x).max(), 1e-6)
    x = np.tanh(x * 1.7) / np.tanh(1.7)  # gentle compression
    x = x * 0.92
    f = int(0.012 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    return x.astype(np.float32)


def _edge(lines, v):
    import edge_tts
    clips = []
    for text in lines:
        last = None
        for _ in range(3):
            try:
                with tempfile.TemporaryDirectory() as d:
                    p = os.path.join(d, "v.mp3")
                    asyncio.run(edge_tts.Communicate(text, v["edge"], rate=v["edge_rate"], pitch=v["edge_pitch"]).save(p))
                    clips.append(prep(_decode(p)))
                last = None
                break
            except Exception as e:
                last = e
        if last:
            raise RuntimeError(f"edge-tts failed: {last}")
    return clips


STYLE = "Speak in a bold, confident, energetic male voice, like a charismatic creator pitching with real conviction. Strong emphasis on the key words, natural breaths, lively pacing, genuine emotion. Never monotone, never robotic."


def split_on_gaps(x, n):
    """Cuts one long recording into n clips at its n-1 longest silences. Returns None if it cannot find them."""
    env = np.convolve(np.abs(x), np.ones(882) / 882, mode="same")
    quiet = env < (0.02 * env.max() + 0.003)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], quiet.astype(np.int8), [0]))))
    gaps = []
    for s, e in zip(edges[0::2], edges[1::2]):
        if e - s >= 0.30 * SR and s > 0 and e < len(x):
            gaps.append((e - s, (s + e) // 2))
    if len(gaps) < n - 1:
        return None
    cuts = sorted(sorted(gaps, reverse=True)[: n - 1], key=lambda g: g[1])
    bounds = [0] + [c[1] for c in cuts] + [len(x)]
    return [x[bounds[k]: bounds[k + 1]] for k in range(n)]


def _gemini_call(base, key, model, voice_name, text):
    for attempt in range(4):
        r = requests.post(f"{base}/models/{model}:generateContent", headers={"x-goog-api-key": key}, timeout=120, json={
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}}}})
        if r.status_code in (429, 500, 503):
            import time
            time.sleep(15 * (attempt + 1))
            continue
        r.raise_for_status()
        part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
        pcm = np.frombuffer(base64.b64decode(part["data"]), dtype="<i2").astype(np.float32) / 32768
        rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1] or 24000)
        return signal.resample_poly(pcm, SR, rate).astype(np.float32)
    raise RuntimeError("Gemini TTS busy")


def _gemini(lines, v):
    key = os.environ["GEMINI_API_KEY"]
    base = "https://generativelanguage.googleapis.com/v1beta"
    models = []
    try:
        r = requests.get(f"{base}/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=30)
        models = [m["name"].split("/", 1)[1] for m in r.json().get("models", [])
                  if "tts" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", [])]
    except Exception:
        pass
    models = sorted(models, key=lambda n: ("flash" not in n, n)) or ["gemini-2.5-flash-preview-tts"]
    for model in models[:3]:
        try:
            # one single take (consistent, natural flow), cut into one clip per line at the pauses
            whole = _gemini_call(base, key, model, v["gemini"],
                                 STYLE + " Leave a clear pause of about one second between the lines, and do not read any numbering.\n\n" + "\n\n".join(lines))
            parts = split_on_gaps(whole, len(lines))
            if parts:
                return [prep(p) for p in parts]
            print("Gemini TTS: pauses not found, speaking line by line")
            return [prep(_gemini_call(base, key, model, v["gemini"], STYLE + "\n\n" + t)) for t in lines]
        except Exception as e:
            print(f"Gemini TTS model {model} failed: {e}")
    raise RuntimeError("Gemini TTS failed")


ENGINES = {"edge": _edge, "gemini": _gemini}


def synthesize(lines, cfg):
    """Returns (clips, engine_name). On total failure returns ([], 'none') so the video is made with music only."""
    v = dict(DEFAULTS)
    v.update(cfg.get("voice", {}))
    if "urdu" in str(cfg.get("language", "")).lower() and "edge" not in cfg.get("voice", {}):
        v["edge"] = "ur-PK-AsadNeural"
    for name in v["engines"]:
        try:
            clips = ENGINES[name](lines, v)
            if len(clips) == len(lines):
                return clips, name
        except Exception as e:
            print(f"Voice engine {name} failed: {e}")
    return [], "none"


TEST_TEXT = "Dentists, are you losing patients who message you at night? Here is how to fix it in minutes."
GEMINI_TEST = ["Fenrir", "Puck", "Orus", "Alnilam", "Charon", "Algenib"]
EDGE_TEST = ["en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-ChristopherNeural", "en-US-GuyNeural", "en-GB-RyanNeural", "en-IN-PrabhatNeural"]


def sample_voices(out_dir, cfg=None):
    """Makes one short sample per candidate male voice. Returns [(label, mp3_path)]."""
    out = []
    v = dict(DEFAULTS)
    v.update((cfg or {}).get("voice", {}))
    jobs = [(f"G{i + 1}  Gemini  {n}", "g", n) for i, n in enumerate(GEMINI_TEST)] + [(f"E{i + 1}  Edge  {n}", "e", n) for i, n in enumerate(EDGE_TEST)]
    base = "https://generativelanguage.googleapis.com/v1beta"
    key = os.getenv("GEMINI_API_KEY")
    for label, kind, name in jobs:
        try:
            if kind == "g":
                if not key:
                    continue
                models = []
                try:
                    r = requests.get(f"{base}/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=30)
                    models = [m["name"].split("/", 1)[1] for m in r.json().get("models", []) if "tts" in m["name"]]
                except Exception:
                    pass
                model = sorted(models, key=lambda n: ("flash" not in n, n))[0] if models else "gemini-2.5-flash-preview-tts"
                clip = prep(_gemini_call(base, key, model, name, STYLE + "\n\n" + TEST_TEXT))
            else:
                import edge_tts
                with tempfile.TemporaryDirectory() as d:
                    p = os.path.join(d, "v.mp3")
                    asyncio.run(edge_tts.Communicate(TEST_TEXT, name, rate=v["edge_rate"], pitch=v["edge_pitch"]).save(p))
                    clip = prep(_decode(p))
            wav = os.path.join(out_dir, label.split()[0] + ".wav")
            import wave
            with wave.open(wav, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes((np.clip(clip, -1, 1) * 32767).astype("<i2").tobytes())
            mp3 = wav.replace(".wav", ".mp3")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", mp3], check=True)
            out.append((label, mp3))
        except Exception as e:
            print(f"Voice sample {label} failed: {e}")
    return out
