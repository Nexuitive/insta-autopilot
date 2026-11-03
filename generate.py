"""Creates the day's post (idea, headline, caption, hashtags) with the Claude API."""
import os, json, re, random, requests

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

RULES = """You write Instagram posts for {name} ({handle}), who sells {niche} to {audience}.
Rules:
- Never invent statistics, client names, testimonials or results. Speak about what automation CAN do.
- Headline: max 9 words, punchy, a hook. Subline: max 18 words.
- Caption: 80-140 words, {language}, strong first line, short paragraphs, one clear call to action: {cta}
- 8-12 relevant hashtags, no banned or spammy tags.
- Pick a topic different from the recent ones and use the trend notes if they help.
Return ONLY JSON with keys: topic, post_type, headline, subline, caption, hashtags (list), insight_note (1 sentence: why this post today)."""


def _gemini(system, user):
    model = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash"
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "content-type": "application/json"},
        json={"system_instruction": {"parts": [{"text": system}]},
              "contents": [{"role": "user", "parts": [{"text": user}]}],
              "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 1500}}, timeout=90)
    r.raise_for_status()
    return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])


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


def make_post(cfg, trends, history):
    b = cfg["brand"]
    system = RULES.format(name=b["name"], handle=b["handle"], cta=b["cta"], niche=cfg["niche"],
                          audience=cfg["audience"], language=cfg.get("language", "English"))
    recent = [h.get("topic", "") for h in history[-14:]]
    user = (f"Post type to prefer today: {random.choice(cfg['post_types'])}\n"
            f"Recent topics (avoid): {recent}\nTrend and competitor notes:\n{trends}")
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", _call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)
            assert all(k in d for k in ("headline", "subline", "caption", "hashtags"))
            assert len(d["headline"].split()) <= 12 and len(d["caption"]) < 1900
            d["hashtags"] = [h.lstrip("#") for h in d["hashtags"]][:12]
            d.setdefault("topic", d["headline"]); d.setdefault("insight_note", "")
            return d
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid post: {last}")
