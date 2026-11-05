"""Writes the daily Reel: its OWN topic and script, for a different target audience each day."""
import json, random, re
import generate

DEFAULT_AUDIENCES = [
    "clinics and dental practices", "online stores and e-commerce sellers", "real estate agents",
    "restaurants and cafes", "digital marketing agencies", "coaching and training institutes",
    "salons, spas and gyms", "freelancers and consultants", "schools and academies",
    "travel and tour agencies", "law and accounting firms", "wholesalers and small manufacturers",
]


def pick_audience(cfg, history):
    """Rotate: choose the audience that was used longest ago (never-used first)."""
    aud = cfg.get("audiences") or DEFAULT_AUDIENCES
    last = {a: -1 for a in aud}
    for i, h in enumerate(history):
        if h.get("audience") in last:
            last[h["audience"]] = i
    oldest = min(last.values())
    return random.choice([a for a in aud if last[a] == oldest])


SYSTEM = """You script short, valuable vertical videos (Reels) for {name} ({handle}), who sells {niche} to {audience_all}.
Goal: teach something useful and solve ONE concrete problem, so the viewer learns something even if they never buy.
Today's TARGET AUDIENCE is given by the user. Use a realistic situation specific to that audience, speak to them directly,
and make the topic different from the recent topics given. Be practical and specific (real tools and tasks such as
WhatsApp or website chat, order updates, appointment booking, lead follow-up, reports), not vague hype.
Never invent statistics, client names, testimonials or results.
Return ONLY JSON with these keys (respect the word limits strictly):
topic, audience_label (max 3 words in capitals, e.g. "FOR DENTAL CLINICS"),
hook (max 8 words, a curiosity question or bold claim aimed at the audience),
problem_title (max 6 words), problem_items (exactly 3 items, max 4 words each: the manual tasks that waste time),
flow_input (max 4 words: what triggers it), flow_process (max 4 words: what the AI/automation does), flow_output (max 4 words: the result),
steps (exactly 3 items, max 8 words each: how to set it up, in order, e.g. connect the channel, teach it your rules, let it run),
before (max 7 words: the manual way), after (max 7 words: the automated way),
benefits (exactly 3 items, max 5 words each), closing (max 7 words),
caption ({caption_words} words, {language}: line 1 is a strong hook; then the problem and the fix in short lines;
then one practical tip the viewer can use today even without us; end with this call to action: {cta}),
hashtags (exactly 10 strings without the # sign: 3 broad ones such as aiautomation or businessautomation,
4 specific to the target audience and their industry, 2 about this video's topic, and 1 brand tag: {brand_tag};
all lowercase, no spaces, real tags people use, nothing spammy or banned),
insight_note (1 sentence: why this video today)."""


def _clip(s, n):
    return " ".join(str(s).split()[:n])


def _tags(raw, brand_tag):
    seen, out = set(), []
    for h in list(raw) + [brand_tag]:
        t = re.sub(r"[^a-z0-9_]", "", str(h).lower().lstrip("#"))
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    brand = out.pop(out.index(brand_tag)) if brand_tag in out else brand_tag
    return out[:10] + [brand]


def make_reel(cfg, trends, history, audience, image_post=None):
    b = cfg["brand"]
    brand_tag = re.sub(r"[^a-z0-9]", "", b["handle"].lower())
    system = SYSTEM.format(name=b["name"], handle=b["handle"], niche=cfg["niche"], audience_all=cfg["audience"],
                           language=cfg.get("language", "English"), cta=b["cta"], brand_tag=brand_tag,
                           caption_words="70-110")
    recent = [h.get("reel_topic", "") for h in history[-14:] if h.get("reel_topic")]
    avoid = f"Image post topic today (do NOT reuse): {image_post['topic']}\n" if image_post else ""
    user = (f"TARGET AUDIENCE today: {audience}\n{avoid}Recent reel topics (avoid): {recent}\n"
            f"Trend and competitor notes:\n{trends}")
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", generate._call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)
            for k in ("problem_items", "steps", "benefits"):
                assert len(d[k]) >= 3
            r = {
                "topic": d.get("topic") or d["hook"], "audience": audience,
                "audience_label": _clip(d.get("audience_label") or "WATCH THIS", 3).upper(),
                "hook": _clip(d["hook"], 10), "problem_title": _clip(d["problem_title"], 7),
                "problem_items": [_clip(x, 5) for x in d["problem_items"][:3]],
                "flow_input": _clip(d["flow_input"], 5), "flow_process": _clip(d["flow_process"], 5),
                "flow_output": _clip(d["flow_output"], 5),
                "steps": [_clip(x, 9) for x in d["steps"][:3]],
                "before": _clip(d.get("before") or "Slow, manual work", 8),
                "after": _clip(d.get("after") or "Fast, automatic, 24/7", 8),
                "benefits": [_clip(x, 6) for x in d["benefits"][:3]], "closing": _clip(d["closing"], 8),
                "insight_note": d.get("insight_note", ""),
            }
            r["caption"] = d["caption"].strip()[:1700] + "\n\n" + " ".join("#" + t for t in _tags(d["hashtags"], brand_tag))
            return r
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid reel script: {last}")
