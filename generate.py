"""Creates the day's post (idea, headline, caption, hashtags) with the Claude API."""
import os, json, re, random, time, requests

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

RULES = """You write Instagram image posts for {name} ({handle}), who sells {niche} to {audience_all}.
Today's TARGET AUDIENCE is given by the user. The post must be PROBLEM-SOLVING or RESULT-DRIVEN:
either name one costly problem and show how to fix it, or show a concrete outcome and how to get it.
Be specific and useful (real tasks such as WhatsApp replies, bookings, order updates, lead follow-up, reports), never vague hype.
Never invent statistics, client names, testimonials or results.
Return ONLY JSON with keys: topic, kind ("problem" or "result"),
headline (max 9 words, a scroll-stopping hook for that audience; wrap the 1-2 most important words in *asterisks*),
subline (max 18 words: how it works or why it matters),
visual (one of phone_chat, dashboard, hourglass, bulb, gears, checklist, growth, bell, none; pick the one that matches the idea),
caption (80-140 words, {language}: line 1 is a strong hook; then the problem and the fix in short lines; then one practical tip they can use today;
then a line inviting them to save the post and send it to a business owner who needs it; end with this call to action: {cta}),
hashtags (exactly 10 strings without the # sign, lowercase: 3 broad such as aiautomation, 4 specific to the audience and their industry, 2 about the topic, 1 brand tag; real tags, never spammy or banned),
insight_note (1 sentence: why this post today)."""


_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _flash_models(key):
    """Ask Google which Flash models this key can use (used when the main model is overloaded)."""
    try:
        r = requests.get(f"{_BASE}/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=30)
        r.raise_for_status()
        names = [m["name"].split("/", 1)[1] for m in r.json().get("models", [])
                 if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]
                 and not any(x in m["name"] for x in ("image", "tts", "live", "audio", "embed", "robotics", "computer", "native"))]
        return sorted(names, key=lambda n: ("preview" in n or "exp" in n, "lite" not in n, n))
    except Exception as e:
        print(f"Could not list Gemini models: {e}")
        return []


def _try_model(model, system, user, key, waits):
    """Returns text, or None if this model is busy/unavailable."""
    for wait in waits:
        time.sleep(wait)
        r = requests.post(
            f"{_BASE}/models/{model}:generateContent",
            headers={"x-goog-api-key": key, "content-type": "application/json"},
            json={"system_instruction": {"parts": [{"text": system}]},
                  "contents": [{"role": "user", "parts": [{"text": user}]}],
                  "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 8192}}, timeout=90)
        if r.status_code in (429, 500, 502, 503, 504):
            print(f"Gemini model {model} busy (HTTP {r.status_code}), retrying...")
            continue
        if r.status_code in (400, 404):
            print(f"Gemini model {model} not usable (HTTP {r.status_code}), skipping")
            return None
        r.raise_for_status()
        return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
    return None


def _gemini(system, user):
    """Main model first; if it stays busy, automatically try other free Flash models."""
    key = os.environ["GEMINI_API_KEY"]
    tried = []
    for model in [os.getenv("GEMINI_MODEL") or "gemini-3.5-flash", os.getenv("GEMINI_FALLBACK_MODEL")]:
        if model and model not in tried:
            tried.append(model)
            out = _try_model(model, system, user, key, (0, 10, 25))
            if out:
                return out
    for model in _flash_models(key):
        if model not in tried and len(tried) < 7:
            tried.append(model)
            out = _try_model(model, system, user, key, (0, 15))
            if out:
                print(f"Used fallback Gemini model: {model}")
                return out
    raise RuntimeError(f"All Gemini models were busy or unavailable (tried: {', '.join(tried)})")


def _call(system, user):
    if os.getenv("GEMINI_API_KEY"):  # free option
        return _gemini(system, user)
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": MODEL, "max_tokens": 1200, "system": system,
              "messages": [{"role": "user", "content": user}]}, timeout=90)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"])


VISUALS = {"phone_chat", "dashboard", "hourglass", "bulb", "gears", "checklist", "growth", "bell", "none"}


def make_post(cfg, trends, history, audience=None):
    b = cfg["brand"]
    system = RULES.format(name=b["name"], handle=b["handle"], cta=b["cta"], niche=cfg["niche"],
                          audience_all=cfg["audience"], language=cfg.get("language", "English"))
    recent = [h.get("topic", "") for h in history[-14:]]
    user = (f"TARGET AUDIENCE today: {audience or cfg['audience']}\n"
            f"Recent topics (avoid): {recent}\nTrend and competitor notes:\n{trends}")
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", _call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)
            assert all(k in d for k in ("headline", "subline", "caption", "hashtags"))
            assert len(d["headline"].replace("*", "").split()) <= 12 and len(d["caption"]) < 1900
            if "*" not in d["headline"]:
                w = d["headline"].split()
                d["headline"] = " ".join(w[:-1] + ["*" + w[-1] + "*"])
            if d["headline"].count("*") % 2:
                d["headline"] = d["headline"].replace("*", "")
            d["hashtags"] = [h.lstrip("#").lower().replace(" ", "") for h in d["hashtags"]][:12]
            v = str(d.get("visual", "none")).strip().lower()
            d["visual"] = v if v in VISUALS else "none"
            d["post_type"] = "result" if str(d.get("kind", "")).lower() == "result" else "problem_fix"
            d.setdefault("topic", d["headline"].replace("*", "")); d.setdefault("insight_note", "")
            return d
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid post: {last}")
