"""Writes the daily Reel: its OWN topic and script (different from the image post)."""
import json, re
import generate

SYSTEM = """You script short vertical videos (Reels) for {name} ({handle}), who sells {niche} to {audience}.
The video must be educational and concrete: show ONE real business situation (for example a clinic, online store,
agency or real-estate office) where manual work wastes time, then how an AI bot or automation fixes it.
The topic MUST be different from the image post topic and from the recent topics given.
Never invent statistics, client names, testimonials or results.
Return ONLY JSON with these keys (respect the word limits strictly):
topic, hook (max 8 words, a curiosity question or bold claim), problem_title (max 6 words),
problem_items (exactly 3 items, max 4 words each, the manual tasks that waste time),
flow_input (max 4 words, what triggers it, e.g. a customer message), flow_process (max 4 words, what the AI/automation does),
flow_output (max 4 words, the result), benefits (exactly 3 items, max 5 words each), closing (max 7 words),
caption (45-70 words, {language}, strong first line, ends with this call to action: {cta}),
hashtags (5 to 8 strings), insight_note (1 sentence: why this video today)."""


def _clip(s, n):
    return " ".join(str(s).split()[:n])


def make_reel(cfg, trends, history, image_post):
    b = cfg["brand"]
    system = SYSTEM.format(name=b["name"], handle=b["handle"], niche=cfg["niche"], audience=cfg["audience"],
                           language=cfg.get("language", "English"), cta=b["cta"])
    recent = [h.get("reel_topic", "") for h in history[-14:] if h.get("reel_topic")]
    user = (f"Image post topic today (do NOT reuse): {image_post['topic']}\nRecent reel topics (avoid): {recent}\n"
            f"Trend and competitor notes:\n{trends}")
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", generate._call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)
            assert len(d["problem_items"]) >= 3 and len(d["benefits"]) >= 3
            r = {
                "topic": d.get("topic") or d["hook"],
                "hook": _clip(d["hook"], 10), "problem_title": _clip(d["problem_title"], 7),
                "problem_items": [_clip(x, 5) for x in d["problem_items"][:3]],
                "flow_input": _clip(d["flow_input"], 5), "flow_process": _clip(d["flow_process"], 5),
                "flow_output": _clip(d["flow_output"], 5),
                "benefits": [_clip(x, 6) for x in d["benefits"][:3]], "closing": _clip(d["closing"], 8),
                "insight_note": d.get("insight_note", ""),
            }
            tags = [h.lstrip("#") for h in d["hashtags"]][:8]
            r["caption"] = d["caption"].strip()[:1500] + "\n\n" + " ".join("#" + t for t in tags)
            return r
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid reel script: {last}")
