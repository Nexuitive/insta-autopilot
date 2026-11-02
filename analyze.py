"""Competitor + hashtag trend analysis using the official Instagram Graph API.
Never raises: if the API refuses (permissions / app review), returns ok=False
and the generator falls back to general trend knowledge."""
import os, random, re, collections, requests

G = "https://graph.facebook.com/v21.0"
UID = os.getenv("IG_USER_ID", "")
TOK = os.getenv("IG_ACCESS_TOKEN", "")


def _get(path, **p):
    p["access_token"] = TOK
    r = requests.get(f"{G}/{path}", params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def _competitor(username):
    fields = ("business_discovery.username(%s){followers_count,media_count,"
              "media.limit(12){caption,like_count,comments_count,media_type}}" % username)
    d = _get(UID, fields=fields)["business_discovery"]
    media = d.get("media", {}).get("data", [])
    if not media:
        return None
    eng = [(m.get("like_count", 0) + m.get("comments_count", 0)) for m in media]
    best = max(media, key=lambda m: m.get("like_count", 0) + m.get("comments_count", 0))
    types = collections.Counter(m.get("media_type", "?") for m in media)
    return (f"@{username}: {d.get('followers_count', '?')} followers, avg {sum(eng)//len(eng)} "
            f"interactions/post, formats {dict(types)}. Best post hook: "
            f"{(best.get('caption') or '')[:140]!r}")


def _hashtag(tag):
    hid = _get("ig_hashtag_search", user_id=UID, q=tag)["data"][0]["id"]
    top = _get(f"{hid}/top_media", user_id=UID, fields="caption,like_count,comments_count", limit=8)["data"]
    words = collections.Counter()
    for m in top:
        words.update(w.lower() for w in re.findall(r"#(\w+)", m.get("caption") or ""))
    return f"#{tag} top posts also use: " + ", ".join(w for w, _ in words.most_common(6))


def run(cfg):
    lines = []
    if not (UID and TOK):
        return {"ok": False, "summary": "No Instagram credentials; using general trend knowledge."}
    for u in cfg.get("competitors", []):
        try:
            s = _competitor(u.lstrip("@"))
            if s:
                lines.append(s)
        except Exception as e:
            lines.append(f"@{u}: could not read ({str(e)[:80]})")
    tags = cfg.get("hashtags_to_watch", [])
    for t in random.sample(tags, min(3, len(tags))):  # API allows 30 unique hashtags / 7 days
        try:
            lines.append(_hashtag(t))
        except Exception as e:
            lines.append(f"#{t}: could not read ({str(e)[:80]})")
    ok = any("could not read" not in l for l in lines)
    return {"ok": ok, "summary": "\n".join(lines) or "No data available; using general trend knowledge."}
