"""Publishes an image post or a Reel through the official Instagram Graph API."""
import os, time, requests

G = "https://graph.facebook.com/v21.0"


def _env():
    return os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]


def _check(r, what):
    if not r.ok:
        raise RuntimeError(f"{what} failed: {r.status_code} {r.text[:300]}")
    return r.json()


def _publish(params, tries):
    uid, tok = _env()
    params["access_token"] = tok
    cid = _check(requests.post(f"{G}/{uid}/media", data=params, timeout=120), "Create media")["id"]
    for _ in range(tries):  # wait until Instagram finishes processing
        s = requests.get(f"{G}/{cid}", params={"fields": "status_code,status", "access_token": tok}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram rejected the file: {s}")
        time.sleep(5)
    else:
        raise RuntimeError("Instagram took too long to process the file")
    mid = _check(requests.post(f"{G}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=120), "Publish")["id"]
    link = requests.get(f"{G}/{mid}", params={"fields": "permalink", "access_token": tok}, timeout=30).json().get("permalink")
    return mid, link


def publish_image(image_url, caption):
    return _publish({"image_url": image_url, "caption": caption}, 12)


def publish_reel(video_url, caption):
    return _publish({"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"}, 60)


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
