"""Voiceover: one spoken clip per beat. Microsoft Edge neural voices first, Gemini TTS as backup; clips are trimmed and levelled."""
import asyncio, base64, os, subprocess, tempfile
import numpy as np
import requests
from scipy import signal

SR = 44100
DEFAULTS = {"engines": ["edge", "gemini"], "edge": "en-US-AndrewNeural", "edge_rate": "+4%", "gemini": "Kore"}


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
    x = x / max(np.abs(x).max(), 1e-6)
    x = np.tanh(x * 1.6) / np.tanh(1.6)  # gentle compression
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
                    asyncio.run(edge_tts.Communicate(text, v["edge"], rate=v["edge_rate"]).save(p))
                    clips.append(prep(_decode(p)))
                last = None
                break
            except Exception as e:
                last = e
        if last:
            raise RuntimeError(f"edge-tts failed: {last}")
    return clips


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
            clips = []
            for text in lines:
                for attempt in range(4):
                    r = requests.post(f"{base}/models/{model}:generateContent", headers={"x-goog-api-key": key}, timeout=90, json={
                        "contents": [{"parts": [{"text": "Say this clearly, in a confident, friendly, energetic tone like a social media explainer: " + text}]}],
                        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v["gemini"]}}}}})
                    if r.status_code in (429, 500, 503):
                        import time
                        time.sleep(15 * (attempt + 1))
                        continue
                    r.raise_for_status()
                    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
                    pcm = np.frombuffer(base64.b64decode(part["data"]), dtype="<i2").astype(np.float32) / 32768
                    rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1] or 24000)
                    clips.append(prep(signal.resample_poly(pcm, SR, rate).astype(np.float32)))
                    break
                else:
                    raise RuntimeError("Gemini TTS busy")
            return clips
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
