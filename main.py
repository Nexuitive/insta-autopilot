"""Usage: python main.py prepare | publish"""
import os, sys, json, time, datetime
from pathlib import Path
import analyze, generate, render, publish, notify, reel

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


def posted_today(hist, today):
    return any(h.get("date") == today and (h.get("media_id") or h.get("reel_media_id")) for h in hist)


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


def prepare():
    cfg, hist = load("config.json", {}), load("data/history.json", [])
    today_d = datetime.date.today()
    today = today_d.isoformat()
    if os.getenv("DRY_RUN", "yes") == "no" and posted_today(hist, today):
        print("Already posted today, nothing to prepare.")
        return
    cleanup(today_d)
    last_real = next((h for h in reversed(hist) if h.get("media_id") or h.get("reel_media_id")), None)
    yesterday = None
    if last_real and os.getenv("IG_ACCESS_TOKEN"):
        parts = [("Image", last_real.get("media_id")), ("Reel", last_real.get("reel_media_id"))]
        yesterday = " | ".join(f"{n}: {publish.get_stats(i)}" for n, i in parts if i) or None
    ins = analyze.run(cfg)
    both = cfg.get("mode", "reel_only") == "both"
    styles = ["amber", "dark", "paper"]
    post, img = None, None
    if both:
        seen = hist + [{"topic": h["reel_topic"]} for h in hist if h.get("reel_topic")]
        post = generate.make_post(cfg, ins["summary"], seen)
        img = f"posts/{today}.png"
        render.render(post, cfg, styles[len(hist) % 3], str(ROOT / img))
    audience = reel.pick_audience(cfg, hist)
    vid, reel_data, video_error = None, None, None
    try:
        reel_data = reel.make_reel(cfg, ins["summary"], hist, audience, post)
        vid = f"posts/{today}.mp4"
        render.render_video(reel_data, cfg, styles[(len(hist) + 1) % 3], str(ROOT / vid))
    except Exception as e:
        vid, video_error = None, f"video not created: {str(e)[:300]}"
        notify.send_text(f"Instagram Autopilot: {video_error}")
    save("data/pending.json", {"date": today, "image": img, "video": vid, "post": post, "reel": reel_data,
                               "audience": audience, "video_error": video_error, "analysis": ins["summary"],
                               "analysis_ok": ins["ok"], "yesterday": yesterday})


def go():
    p = load("data/pending.json", None)
    if not p:
        sys.exit("Nothing pending.")
    dry = os.getenv("DRY_RUN", "yes") != "no"
    today = datetime.date.today().isoformat()
    if not dry:
        if p.get("date") != today or posted_today(load("data/history.json", []), today):
            print("Nothing new to post today (already posted or no fresh video).")
            return
        wait_for_slot()
    post = p.get("post")
    caption = (post["caption"].strip() + "\n\n" + " ".join("#" + h for h in post["hashtags"])) if post else ""
    res = {"reel_error": p.get("video_error")}
    if not dry:
        base = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/{os.getenv('GITHUB_REF_NAME', 'main')}/"
        entry = {"date": p["date"], "audience": p.get("audience", "")}
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
