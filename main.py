"""Usage: python main.py prepare | publish"""
import os, sys, json, datetime
from pathlib import Path
import analyze, generate, render, publish, notify

ROOT = Path(__file__).parent


def load(p, default):
    f = ROOT / p
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else default


def save(p, obj):
    f = ROOT / p
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def prepare():
    cfg, hist = load("config.json", {}), load("data/history.json", [])
    today = datetime.date.today().isoformat()
    last_real = next((h for h in reversed(hist) if h.get("media_id")), None)
    yesterday = publish.get_stats(last_real["media_id"]) if last_real and os.getenv("IG_ACCESS_TOKEN") else None
    ins = analyze.run(cfg)
    post = generate.make_post(cfg, ins["summary"], hist)
    style = ["amber", "dark", "paper"][len(hist) % 3]
    img = f"posts/{today}.png"
    render.render(post, cfg, style, str(ROOT / img))
    save("data/pending.json", {"date": today, "image": img, "post": post, "analysis": ins["summary"],
                               "analysis_ok": ins["ok"], "yesterday": yesterday})


def go():
    p = load("data/pending.json", None)
    if not p:
        sys.exit("Nothing pending.")
    dry = os.getenv("DRY_RUN", "yes") != "no"
    post = p["post"]
    caption = post["caption"].strip() + "\n\n" + " ".join("#" + h for h in post["hashtags"])
    link = None
    if not dry:
        url = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/{os.getenv('GITHUB_REF_NAME', 'main')}/{p['image']}"
        mid, link = publish.publish_image(url, caption)
        hist = load("data/history.json", [])
        hist.append({"date": p["date"], "topic": post["topic"], "headline": post["headline"], "media_id": mid, "permalink": link})
        save("data/history.json", hist)
    notify.report(p, caption, dry, link)


if __name__ == "__main__":
    try:
        {"prepare": prepare, "publish": go}[sys.argv[1]]()
    except Exception as e:
        notify.send_text(f"Instagram Autopilot FAILED at '{sys.argv[1]}': {e}")
        raise
