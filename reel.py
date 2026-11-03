"""Short, different caption for the daily Reel (so it does not repeat the image caption)."""
import json, re
import generate


def make_reel_caption(cfg, post):
    b = cfg["brand"]
    system = ('You write short Instagram Reel captions. Return ONLY JSON: {"caption": "...", "hashtags": ["5 to 8 tags"]}. '
              "30-60 words, a different hook from the image post, no invented statistics or claims. "
              "End the caption with this call to action: " + b["cta"])
    user = (f"Topic: {post['topic']}\nHeadline: {post['headline']}\nKey point: {post['subline']}\n"
            f"Image post caption (do not repeat it): {post['caption'][:300]}")
    try:
        txt = re.sub(r"^```(?:json)?|```$", "", generate._call(system, user).strip(), flags=re.M).strip()
        d = json.loads(txt)
        tags = [h.lstrip("#") for h in d["hashtags"]][:8]
        return d["caption"].strip() + "\n\n" + " ".join("#" + t for t in tags)
    except Exception:
        return post["subline"] + "\n\n" + b["cta"] + "\n\n" + " ".join("#" + h for h in post["hashtags"][:6])
