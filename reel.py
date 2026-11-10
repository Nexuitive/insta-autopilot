"""Writes the daily Reel: its OWN topic and script, for a different target audience each day."""
import datetime, json, random, re
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


SYSTEM_K = """You script fast kinetic-typography Reels (short bold phrases, ONE idea per screen) for {name} ({handle}), who sells {niche} to {audience_all}.
Teach something useful and solve ONE concrete problem for today's TARGET AUDIENCE (given by the user), so the viewer learns something
even if they never buy. Use a realistic situation for that audience and real actions (WhatsApp or website chat, bookings, order updates,
lead follow-up, reports). Make the topic different from the recent topics. Never invent statistics, client names or results.
Return ONLY JSON with keys: topic, audience_label (max 3 words in capitals, e.g. "FOR DENTAL CLINICS"),
beats (exactly {n_beats} objects, each {{"text": "...", "visual": "...", "vo": "..."}}), caption, hashtags, insight_note.
Beat rules: "vo" is the spoken voiceover for that beat: ONE natural, conversational sentence of 5 to 12 words that says the same idea as the on-screen text in a friendly confident voice (plain words only, no symbols, no hashtags, no stage directions; write numbers as words when needed; the final beat says: DM the word AUTOMATE for a free fifteen minute call). "text" is a punchy on-screen caption of max 8 words. Wrap the 1-2 most important words in *asterisks*, e.g. "Still replying *by hand*?".
Flow: {flow}
The hook (beat 1) must be 7 words or fewer, must stop the scroll within 2 seconds, and should name the audience or a painful problem (for example "Dentists: stop losing night patients").
TODAY'S CONTENT PILLAR: follow this format: {pillar}.
visual must be one of: phone_chat, dashboard, hourglass, bulb, gears, checklist, growth, bell, none.
Use every visual at most once and match it to the text: bell = missed messages or notifications, hourglass = wasted time,
phone_chat = customer replies or booking, checklist = steps or tasks done, dashboard = reports or data, growth = results,
gears = automation at work, bulb = a tip or idea. The first and the last beat should use none.
caption (70-110 words, {language}): line 1 is a strong hook; then the problem and the fix in short lines; then one practical tip the viewer can use
today even without us; then add a line inviting them to save the post and send it to a business owner who needs it; end with this call to action: {cta}
hashtags (exactly 10 strings without the # sign: 3 broad ones such as aiautomation or businessautomation, 4 specific to the target audience and their industry,
2 about this video's topic, and 1 brand tag: {brand_tag}; all lowercase, real tags, nothing spammy or banned).
insight_note (1 sentence: why this video today)."""

PILLARS = {
    0: "MYTH VS FACT: bust one common myth this audience believes about AI bots or automation",
    1: "HOW-TO: a simple step-by-step they can follow",
    2: "PROBLEM TO FIX: one costly manual problem and its automated fix",
    3: "MISTAKES: common mistakes businesses make with this task, and the fix",
    4: "QUICK WIN: one tip they can apply in 10 minutes without paying for anything",
    5: "BEFORE VS AFTER: a realistic day with and without automation",
    6: "FAQ: answer one question owners often ask (cost, time, is it hard, will it replace staff)",
}
FLOW = {
    9: "beat 1 = hook; beats 2-3 = the problem (specific and relatable); beats 4-6 = the fix, explained as concrete steps; "
       "beats 7-8 = the result, or a practical tip they can use today; beat 9 = call to action: DM *AUTOMATE* for a free 15-minute call.",
    7: "beat 1 = hook; beat 2 = the problem (specific and relatable); beats 3-5 = the fix, explained as concrete steps; "
       "beat 6 = the result, or a practical tip they can use today; beat 7 = call to action: DM *AUTOMATE* for a free 15-minute call.",
}

VISUALS = {"phone_chat", "dashboard", "hourglass", "bulb", "gears", "checklist", "growth", "bell", "none"}


def make_kinetic(cfg, trends, history, audience, image_post=None, theme=0):
    b = cfg["brand"]
    brand_tag = re.sub(r"[^a-z0-9]", "", b["handle"].lower())
    n_beats = 9 if int(cfg.get("reel_beats", 7)) >= 9 else 7
    now = datetime.datetime.now(datetime.timezone.utc)
    slot = len([h for h in history if h.get("date") == now.date().isoformat() and (h.get("media_id") or h.get("reel_media_id"))])
    pillar = PILLARS[(now.weekday() + slot) % 7]  # the 2nd post of the day uses a different content format
    system = SYSTEM_K.format(name=b["name"], handle=b["handle"], niche=cfg["niche"], audience_all=cfg["audience"],
                             language=cfg.get("language", "English"), cta=b["cta"], brand_tag=brand_tag,
                             n_beats=n_beats, flow=FLOW[n_beats], pillar=pillar)
    recent = [h.get("reel_topic", "") for h in history[-14:] if h.get("reel_topic")]
    avoid = f"Image post topic today (do NOT reuse): {image_post['topic']}\n" if image_post else ""
    user = (f"TARGET AUDIENCE today: {audience}\n{avoid}Recent reel topics (avoid): {recent}\n"
            f"Trend and competitor notes:\n{trends}")
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", generate._call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)
            raw = d["beats"]
            assert 7 <= len(raw) <= 11
            used, beats = set(), []
            for x in raw:
                text = _clip(x["text"], 9)
                if "*" not in text:
                    parts = text.split()
                    text = " ".join(parts[:-1] + ["*" + parts[-1] + "*"]) if parts else text
                if text.count("*") % 2:
                    text = text.replace("*", "")
                v = str(x.get("visual", "none")).strip().lower()
                if v not in VISUALS or (v != "none" and v in used):
                    v = "none"
                used.add(v)
                vo = re.sub(r"[*#@_]", "", str(x.get("vo") or "")).strip() or text.replace("*", "")
                beats.append({"text": text, "visual": v, "vo": _clip(vo, 16)})
            r = {
                "style": "kinetic", "theme": theme, "topic": d.get("topic") or beats[0]["text"], "audience": audience,
                "audience_label": _clip(d.get("audience_label") or "WATCH THIS", 3).upper(),
                "beats": beats, "hook": beats[0]["text"].replace("*", ""), "insight_note": d.get("insight_note", ""),
            }
            r["caption"] = d["caption"].strip()[:1700] + "\n\n" + " ".join("#" + t for t in _tags(d["hashtags"], brand_tag))
            return r
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid reel script: {last}")


SYSTEM_X = """You write the script for a 30-second motion-graphics explainer Reel for {name} ({handle}), who sells {niche} to {audience_all}.
Style: a premium SaaS-style explainer. Story: (1) a painful hook, (2) a contrast, (3) brand reveal, (4) a 3-step demo of a chat flow,
(5) a diagram of the tools the automation updates, (6) a big "always on" moment, (7) before and after, (8) call to action.
Today's TARGET AUDIENCE is given by the user: use a realistic situation for that audience (their customers' messages, bookings, orders, enquiries).
Be concrete. Never invent statistics, client names, testimonials or results.
TODAY'S CONTENT ANGLE: {pillar}.
Return ONLY JSON with these keys (respect the word limits):
topic, audience_label (max 3 words in capitals, e.g. FOR DENTAL CLINICS),
hook (max 7 words about the audience's pain; wrap the 1-2 key words in *asterisks*; example: "Nobody answers *2 AM* messages."),
contrast (max 7 words; example: "But everyone expects *instant replies.*"),
steps (exactly 3 objects {{"label": "max 3 words"}}: the customer step, the AI step, the owner approval step; for example Customer asks, AI replies, You approve),
ui_q (a realistic customer message for this audience, max 9 words),
ui_a (the AI's helpful reply, two short sentences, max 18 words),
diagram ({{"customer": "max 2 words for who writes, e.g. Patient, Buyer, Guest", "outputs": ["3 tools or places the automation updates", "max 2 words each", "e.g. Calendar, Google Sheet, CRM"]}}),
captions (exactly 3 short subtitle lines, max 5 words each, one key word in *asterisks*),
big ({{"value": "one of: 24/7, 3 steps, 1 inbox, Instant", "label": "max 6 words"}}),
compare ({{"before": "max 4 words naming the repeated manual work for this audience"}}),
cta ({{"stop": "max 5 words ending with a full stop: what to stop doing", "start": "max 3 words ending with a full stop"}}),
vo (exactly 8 spoken lines, one per scene in order, each 5 to 14 words, natural, confident and energetic; scene 3 is a short brand intro such as "Meet {name}."; the last line ends with: DM the word AUTOMATE),
caption ({caption_words} words, {language}: a strong first line, the problem and the fix in short lines, one practical tip viewers can use today even without us, a line inviting them to save the post and send it to a business owner who needs it, then this call to action: {cta}),
hashtags (exactly 10 strings without the # sign, lowercase: 3 broad such as aiautomation, 4 specific to the audience and their industry, 2 about the topic, 1 brand tag: {brand_tag}),
insight_note (1 sentence: why this video today)."""


def make_explainer(cfg, trends, history, audience, image_post=None):
    b = cfg["brand"]
    brand_tag = re.sub(r"[^a-z0-9]", "", b["handle"].lower())
    now = datetime.datetime.now(datetime.timezone.utc)
    slot = len([h for h in history if h.get("date") == now.date().isoformat() and (h.get("media_id") or h.get("reel_media_id"))])
    system = SYSTEM_X.format(name=b["name"], handle=b["handle"], niche=cfg["niche"], audience_all=cfg["audience"], language=cfg.get("language", "English"),
                             cta=b["cta"], brand_tag=brand_tag, caption_words="70-110", pillar=PILLARS[(now.weekday() + slot) % 7])
    recent = [h.get("reel_topic", "") for h in history[-14:] if h.get("reel_topic")]
    avoid = f"Image post topic today (do NOT reuse): {image_post['topic']}\n" if image_post else ""
    user = f"TARGET AUDIENCE today: {audience}\n{avoid}Recent reel topics (avoid): {recent}\nTrend and competitor notes:\n{trends}"
    last = None
    for _ in range(3):
        try:
            txt = re.sub(r"^```(?:json)?|```$", "", generate._call(system, user).strip(), flags=re.M).strip()
            d = json.loads(txt)

            def hl(s, n):
                s = _clip(s, n)
                if "*" not in s:
                    w = s.split()
                    s = " ".join(w[:-1] + ["*" + w[-1] + "*"]) if w else s
                return s.replace("*", "") if s.count("*") % 2 else s

            vo = [re.sub(r"[*#@_]", "", str(x)).strip() for x in d["vo"]]
            assert len(vo) == 8 and all(vo)
            big = d["big"]["value"] if d["big"]["value"] in ("24/7", "3 steps", "1 inbox", "Instant") else "24/7"
            r = {
                "style": "explainer", "topic": d.get("topic") or d["hook"], "audience": audience,
                "audience_label": _clip(d.get("audience_label") or "WATCH THIS", 3).upper(),
                "hook": hl(d["hook"], 8), "contrast": hl(d["contrast"], 8),
                "steps": [{"label": _clip(s["label"], 3)} for s in d["steps"][:3]],
                "ui_q": _clip(d["ui_q"], 10), "ui_a": _clip(d["ui_a"], 20),
                "diagram": {"customer": _clip(d["diagram"]["customer"], 2), "outputs": [_clip(x, 2) for x in d["diagram"]["outputs"][:3]]},
                "captions": [hl(c, 6) for c in d["captions"][:3]],
                "big": {"value": big, "label": _clip(d["big"]["label"], 7)},
                "compare": {"before": _clip(d["compare"]["before"], 4)},
                "cta": {"stop": _clip(d["cta"]["stop"], 6), "start": _clip(d["cta"]["start"], 4)},
                "vo": [_clip(x, 18) for x in vo], "insight_note": d.get("insight_note", ""),
            }
            assert len(r["steps"]) == 3 and len(r["diagram"]["outputs"]) == 3 and len(r["captions"]) == 3
            r["caption"] = d["caption"].strip()[:1700] + "\n\n" + " ".join("#" + t for t in _tags(d["hashtags"], brand_tag))
            return r
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not generate a valid explainer script: {last}")
