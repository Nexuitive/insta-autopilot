"""Usage: python main.py prepare | publish"""
import os, sys, json, time, datetime
from pathlib import Path
import analyze, generate, render, publish, notify, reel, cinematic, voice

ROOT = Path(__file__).parent


def load(p, default):
    f = ROOT / p
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else default


def save(p, obj):
    f = ROOT / p
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def cleanup(today):
    """Keep the repo small: delete post files older than 7 days."""
    for f in (ROOT / "posts").glob("*"):
        try:
            d = datetime.date.fromisoformat(f.name[:10])
            if (today - d).days > 7:
                f.unlink()
        except ValueError:
            pass


def posts_today(hist, today):
    return [h for h in hist if h.get("date") == today and (h.get("media_id") or h.get("reel_media_id"))]


def plan_of(cfg):
    """What each post of the day is, in order. Default: reel, image, reel."""
    return cfg.get("plan") or ["reel", "image", "reel"]


def can_post_now(cfg, hist, today):
    """Allows up to posts_per_day posts per day, at least min_gap_hours apart (stops accidental double runs)."""
    mine = posts_today(hist, today)
    if len(mine) >= int(cfg.get("posts_per_day", len(plan_of(cfg)))):
        return False
    stamps = [h["ts"] for h in mine if h.get("ts")]
    if stamps:
        last = datetime.datetime.fromisoformat(max(stamps))
        gap = (datetime.datetime.now(datetime.timezone.utc) - last).total_seconds() / 3600
        if gap < float(cfg.get("min_gap_hours", 1.5)):
            return False
    return True


def wait_for_slot():
    """Scheduled runs build everything early, then wait here until the posting time (UTC, e.g. 18:00 = 11 PM Pakistan)."""
    at = os.getenv("POST_AT_UTC")
    if not at or os.getenv("GITHUB_EVENT_NAME") != "schedule":
        return
    h, mi = map(int, at.split(":"))
    now = datetime.datetime.now(datetime.timezone.utc)
    target = now.replace(hour=h, minute=mi, second=0, microsecond=0)
    wait = (target - now).total_seconds()
    if 0 < wait <= 5 * 3600:
        print(f"Waiting {int(wait)} seconds until {at} UTC...")
        time.sleep(wait)


def voice_test():
    """Run the workflow with dry_run = voice: sends one sample per candidate male voice to Telegram."""
    cfg = load("config.json", {})
    with __import__("tempfile").TemporaryDirectory() as d:
        samples = voice.sample_voices(d, cfg)
        notify.send_text(f"Voice test: {len(samples)} samples coming. Listen, then tell Claude the code of your favourite (for example G1 or E2).")
        for label, path in samples:
            notify.send_audio(path, label)
        if not samples:
            notify.send_text("Voice test: no sample could be created (check GEMINI_API_KEY and the run log).")


def prepare():
    if os.getenv("DRY_RUN") == "voice":
        voice_test()
        return
    cfg, hist = load("config.json", {}), load("data/history.json", [])
    today_d = datetime.date.today()
    today = today_d.isoformat()
    live = os.getenv("DRY_RUN", "yes") == "no"
    if live and not can_post_now(cfg, hist, today):
        print("Daily post limit reached (or the last post was too recent), nothing to prepare.")
        return
    cleanup(today_d)
    plan = plan_of(cfg)
    slot = len(posts_today(hist, today))
    kind = plan[slot] if slot < len(plan) else plan[0]
    kinds = [kind] if live else [k for k in ("image", "reel") if k in plan]  # a preview run shows both kinds
    last_real = next((h for h in reversed(hist) if h.get("media_id") or h.get("reel_media_id")), None)
    yesterday = None
    if last_real and os.getenv("IG_ACCESS_TOKEN"):
        parts = [("Image", last_real.get("media_id")), ("Reel", last_real.get("reel_media_id"))]
        yesterday = " | ".join(f"{n}: {publish.get_stats(i)}" for n, i in parts if i) or None
    ins = analyze.run(cfg)
    audience = reel.pick_audience(cfg, hist)
    tag = f"{today}-{slot + 1}"
    post = img = vid = reel_data = video_error = voice_engine = None
    if "image" in kinds:
        try:
            seen = hist + [{"topic": h["reel_topic"]} for h in hist if h.get("reel_topic")]
            post = generate.make_post(cfg, ins["summary"], seen, audience)
            img = f"posts/{tag}.jpg"
            cinematic.render_image(post, cfg, str(ROOT / img), len(hist))
        except Exception as e:
            post = img = None
            video_error = f"image not created: {str(e)[:300]}"
            notify.send_text(f"Instagram Autopilot: {video_error}")
    if "reel" in kinds:
        try:
            vstyle = cfg.get("video_style", "explainer")
            if vstyle == "explainer":
                reel_data = reel.make_explainer(cfg, ins["summary"], hist, audience, post)
            elif vstyle in ("cinematic", "kinetic"):
                reel_data = reel.make_kinetic(cfg, ins["summary"], hist, audience, post, theme=len(hist))
                reel_data["style"] = vstyle
            else:
                reel_data = reel.make_reel(cfg, ins["summary"], hist, audience, post)
            vid = f"posts/{tag}.mp4"
            voice_engine = render.render_video(reel_data, cfg, "x", str(ROOT / vid))
        except Exception as e:
            vid, reel_data = None, None
            video_error = f"video not created: {str(e)[:300]}"
            notify.send_text(f"Instagram Autopilot: {video_error}")
    save("data/pending.json", {"date": today, "kind": kind if live else "preview", "image": img, "video": vid, "post": post, "reel": reel_data,
                               "audience": audience, "voice": voice_engine or "n/a", "video_error": video_error, "analysis": ins["summary"],
                               "analysis_ok": ins["ok"], "yesterday": yesterday})


def go():
    if os.getenv("DRY_RUN") == "voice":
        return
    p = load("data/pending.json", None)
    if not p:
        sys.exit("Nothing pending.")
    dry = os.getenv("DRY_RUN", "yes") != "no"
    today = datetime.date.today().isoformat()
    if not dry:
        if p.get("date") != today or not can_post_now(load("config.json", {}), load("data/history.json", []), today):
            print("Nothing new to post now (daily limit reached or no fresh video).")
            return
        wait_for_slot()
    post = p.get("post")
    caption = (post["caption"].strip() + "\n\n" + " ".join("#" + h for h in post["hashtags"])) if post else ""
    res = {"reel_error": p.get("video_error")}
    if not dry:
        base = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/{os.getenv('GITHUB_REF_NAME', 'main')}/"
        entry = {"date": p["date"], "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(), "audience": p.get("audience", "")}
        if post and p.get("image"):
            mid, res["link"] = publish.publish_image(base + p["image"], caption)
            entry.update(topic=post["topic"], headline=post["headline"], media_id=mid, permalink=res["link"])
        if p.get("video") and p.get("reel"):
            try:
                rid, res["reel_link"] = publish.publish_reel(base + p["video"], p["reel"]["caption"])
                entry.update(reel_media_id=rid, reel_topic=p["reel"]["topic"], reel_permalink=res["reel_link"])
            except Exception as e:
                res["reel_error"] = str(e)[:300]
        if entry.get("media_id") or entry.get("reel_media_id"):
            hist = load("data/history.json", [])
            hist.append(entry)
            save("data/history.json", hist)
    notify.report(p, caption, dry, res)
    if not dry and not (res.get("link") or res.get("reel_link")):
        sys.exit("Nothing was posted.")


if __name__ == "__main__":
    try:
        {"prepare": prepare, "publish": go}[sys.argv[1]]()
    except Exception as e:
        notify.send_text(f"Instagram Autopilot FAILED at '{sys.argv[1]}': {e}")
        raise
