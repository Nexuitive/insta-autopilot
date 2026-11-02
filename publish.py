"""Publishes a single image post through the official Instagram Graph API."""
import os, time, requests

G = "https://graph.facebook.com/v21.0"


def _env():
    return os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]


def publish_image(image_url, caption):
    uid, tok = _env()
    r = requests.post(f"{G}/{uid}/media", data={"image_url": image_url, "caption": caption, "access_token": tok}, timeout=60)
    r.raise_for_status()
    cid = r.json()["id"]
    for _ in range(12):  # wait until Instagram finishes processing
        s = requests.get(f"{G}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram rejected the image: {s}")
        time.sleep(5)
    r = requests.post(f"{G}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    r.raise_for_status()
    mid = r.json()["id"]
    link = requests.get(f"{G}/{mid}", params={"fields": "permalink", "access_token": tok}, timeout=30).json().get("permalink")
    return mid, link


def get_stats(media_id):
    """Yesterday's numbers. Returns a short string, or None if unavailable."""
    _, tok = _env()
    try:
        r = requests.get(f"{G}/{media_id}/insights", params={"metric": "reach,likes,comments,saved,shares", "access_token": tok}, timeout=30)
        r.raise_for_status()
        return ", ".join(f"{m['name']} {m['values'][0]['value']}" for m in r.json()["data"])
    except Exception:
        try:
            d = requests.get(f"{G}/{media_id}", params={"fields": "like_count,comments_count", "access_token": tok}, timeout=30).json()
            return f"likes {d.get('like_count', '?')}, comments {d.get('comments_count', '?')}"
        except Exception:
            return None
