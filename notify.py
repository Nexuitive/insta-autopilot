"""Daily progress report to Telegram (prints to the log if Telegram is not set up)."""
import os, requests


def _api(method, **kw):
    t = os.getenv("TELEGRAM_BOT_TOKEN")
    if not t:
        print("Telegram: no bot token set")
        return False
    r = requests.post(f"https://api.telegram.org/bot{t}/{method}", timeout=120, **kw)
    if not r.ok:
        print(f"TELEGRAM ERROR {method}: {r.status_code} {r.text[:200]}")
    return r.ok


def send_text(text):
    print(text)
    _api("sendMessage", data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": text[:4000]})


def report(p, caption, dry, res):
    post = p["post"]
    chat = os.getenv("TELEGRAM_CHAT_ID")
    lines = [
        f"Instagram Autopilot | {p['date']}",
        "PREVIEW ONLY, not posted" if dry else "POSTED",
        f"Topic: {post['topic']}",
        f"Headline: {post['headline']}",
        f"Why today: {post.get('insight_note', '-')}",
        f"Image post: {res.get('link') or '-'}",
        f"Reel: {res.get('reel_link') or '-'}",
    ]
    if res.get("reel_error"):
        lines.append(f"Reel problem: {res['reel_error']}")
    lines += [
        f"Yesterday: {p.get('yesterday') or 'no data yet'}",
        f"Trend notes ({'live data' if p.get('analysis_ok') else 'fallback'}):\n{p['analysis'][:700]}",
        f"\nCaption:\n{caption[:900]}",
    ]
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        if os.path.exists(p["image"]):
            with open(p["image"], "rb") as f:
                _api("sendPhoto", data={"chat_id": chat}, files={"photo": f})
        if p.get("video") and os.path.exists(p["video"]):
            with open(p["video"], "rb") as f:
                _api("sendVideo", data={"chat_id": chat}, files={"video": f})
    send_text("\n".join(lines))
