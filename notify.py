"""Daily progress report to Telegram (prints to the log if Telegram is not set up)."""
import os, requests


def _api(method, **kw):
    t = os.getenv("TELEGRAM_BOT_TOKEN")
    if not t:
        return False
    return requests.post(f"https://api.telegram.org/bot{t}/{method}", timeout=60, **kw).ok


def send_text(text):
    print(text)
    _api("sendMessage", data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": text[:4000]})


def report(p, caption, dry, link):
    post = p["post"]
    lines = [
        f"Instagram Autopilot | {p['date']}",
        "PREVIEW ONLY, not posted" if dry else "POSTED",
        f"Topic: {post['topic']}",
        f"Headline: {post['headline']}",
        f"Why today: {post.get('insight_note', '-')}",
        f"Hashtags: {len(post['hashtags'])}",
        f"Link: {link or '-'}",
        f"Yesterday's post: {p.get('yesterday') or 'no data yet'}",
        f"Trend notes ({'live data' if p.get('analysis_ok') else 'fallback'}):\n{p['analysis'][:900]}",
        f"\nCaption:\n{caption[:1200]}",
    ]
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.path.exists(p["image"]):
        with open(p["image"], "rb") as f:
            _api("sendPhoto", data={"chat_id": os.getenv("TELEGRAM_CHAT_ID")}, files={"photo": f})
    send_text("\n".join(lines))
