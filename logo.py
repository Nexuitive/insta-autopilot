"""Splits the brand logo into its parts (gear, monogram, swoosh, every letter, icons) so each part can be animated.
The parts always add up to the original logo, pixel for pixel."""
import base64, io, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_logo():
    for p in ("logo.png", "assets/logo.png", "Logo.png"):
        f = os.path.join(ROOT, p)
        if os.path.exists(f):
            return f
    return None


def _uri(arr):
    b = io.BytesIO()
    Image.fromarray(arr).save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def split(path):
    """Returns {'size': (w, h), 'full': uri, 'g': {group: [layer, ...]}} or None if the logo does not look like the expected design.
    A layer is {x, y, w, h, uri}."""
    im = Image.open(path).convert("RGBA")
    if im.size != (500, 500):
        im = im.resize((500, 500), Image.LANCZOS)
    a = np.array(im)
    alpha = a[..., 3]
    lab, n = ndimage.label(alpha > 20)
    areas = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    lab = np.where(np.isin(lab, np.flatnonzero(areas >= 12) + 1), lab, 0)  # specks are absorbed by their nearest big part
    idx = ndimage.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    full = np.where(alpha > 0, lab[idx[0], idx[1]], 0)  # every visible pixel belongs to exactly one part
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        area = int((lab[sl] == i).sum())
        if area >= 12:
            comps.append(dict(id=i, x0=sl[1].start, x1=sl[1].stop, y0=sl[0].start, y1=sl[0].stop, area=area))
    # tiny leftovers (antialiasing specks) join the nearest big part automatically via `full`
    groups = {"gear": [], "swoosh": [], "mono": [], "pixels": [], "syed": [], "auto": [], "rules": [], "tag": [], "div": [], "i1": [], "i2": [], "i3": [], "i4": []}
    for c in comps:
        w, h, cx, cy = c["x1"] - c["x0"], c["y1"] - c["y0"], (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
        if c["y1"] <= 222:
            if c["area"] >= 2500 and c["x0"] >= 280 and c["y1"] <= 140:
                g = "gear"
            elif c["x0"] <= 100 and c["x1"] >= 400 and c["area"] > 3500:
                g = "swoosh"
            elif c["y0"] >= 175 and c["x0"] >= 295 and c["area"] < 400:
                g = "pixels"
            else:
                g = "mono"
        elif 330 <= c["y0"] and c["y1"] <= 366 and h <= 24:
            g = "rules" if (h <= 4 and w > 50) else "tag"
        elif c["y0"] >= 372:
            g = "div" if (w <= 6 and h >= 45) else ("i1" if cx < 125 else "i2" if cx < 245 else "i3" if cx < 360 else "i4")
        elif 215 <= c["y0"] <= 248 and c["y1"] <= 296:
            g = "syed"
        elif c["y0"] >= 278 and c["y1"] <= 336:
            g = "auto"
        else:
            g = "mono"
        groups[g].append(c)
    if len(groups["syed"]) != 4 or not (9 <= len(groups["auto"]) <= 11) or not groups["gear"] or not groups["swoosh"]:
        return None
    ids_of = lambda cs: [c["id"] for c in cs]
    # the dot of the i joins its stem: merge letters whose x-ranges overlap
    def letters(cs):
        cs = sorted(cs, key=lambda c: c["x0"])
        out = []
        for c in cs:
            if out and c["x0"] < out[-1]["x1"] - 0.5 * min(c["x1"] - c["x0"], out[-1]["x1"] - out[-1]["x0"]):
                out[-1]["ids"].append(c["id"]); out[-1]["x1"] = max(out[-1]["x1"], c["x1"])
            else:
                out.append(dict(ids=[c["id"]], x0=c["x0"], x1=c["x1"]))
        return [o["ids"] for o in out]

    def layer(ids):
        m = np.isin(full, ids)
        ys, xs = np.where(m)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        crop = a[y0:y1, x0:x1].copy()
        crop[~m[y0:y1, x0:x1]] = 0
        return dict(x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0), uri=_uri(crop))

    G = {"gear": [layer(ids_of(groups["gear"]))], "swoosh": [layer(ids_of(groups["swoosh"]))],
         "mono": [layer([c["id"]]) for c in sorted(groups["mono"], key=lambda c: c["x0"])],
         "pixels": [layer([c["id"]]) for c in sorted(groups["pixels"], key=lambda c: c["x0"])],
         "syed": [layer([c["id"]]) for c in sorted(groups["syed"], key=lambda c: c["x0"])],
         "auto": [layer(ids) for ids in letters(groups["auto"])],
         "rules": [layer([c["id"]]) for c in sorted(groups["rules"], key=lambda c: c["x0"])],
         "tag": [layer(ids_of(groups["tag"]))] if groups["tag"] else [],
         "div": [layer([c["id"]]) for c in sorted(groups["div"], key=lambda c: c["x0"])]}
    for k in ("i1", "i2", "i3", "i4"):
        G[k] = [layer(ids_of(groups[k]))] if groups[k] else []
    return {"size": (500, 500), "full": _uri(a), "g": G}


def parts_composite(parts):
    """For testing: stack all layers back together."""
    canvas = Image.new("RGBA", parts["size"], (0, 0, 0, 0))
    for layers in parts["g"].values():
        for L in layers:
            im = Image.open(io.BytesIO(base64.b64decode(L["uri"].split(",", 1)[1]))).convert("RGBA")
            canvas.alpha_composite(im, (L["x"], L["y"]))
    return canvas


CSS = """
.lgbox{position:absolute;width:500px;height:500px;transform-origin:0 0}
.lgl{position:absolute;opacity:0;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.9,.25,1.1)}
.lggear{animation-name:lgGear}.lgsl{animation-name:lgSl}.lgsr{animation-name:lgSr}.lgwipe{animation-name:lgWipe;animation-timing-function:ease-in-out}
.lgpop{animation-name:lgPop}.lgrise{animation-name:lgRise}.lggrow{animation-name:lgGrow;animation-timing-function:ease-out}
.lggrowy{animation-name:lgGrowY;animation-timing-function:ease-out}.lgfade{animation-name:lgFade;animation-timing-function:ease-out}
@keyframes lgGear{from{opacity:0;transform:rotate(-260deg) scale(.15)}to{opacity:1;transform:none}}
@keyframes lgSl{from{opacity:0;transform:translateX(-110px) skewX(-14deg)}to{opacity:1;transform:none}}
@keyframes lgSr{from{opacity:0;transform:translateX(110px) skewX(14deg)}to{opacity:1;transform:none}}
@keyframes lgWipe{from{opacity:1;clip-path:inset(0 100% 0 0)}to{opacity:1;clip-path:inset(0 0 0 0)}}
@keyframes lgPop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
@keyframes lgRise{from{opacity:0;transform:translateY(44px)}to{opacity:1;transform:none}}
@keyframes lgGrow{from{opacity:1;clip-path:inset(0 50% 0 50%)}to{opacity:1;clip-path:inset(0 0 0 0)}}
@keyframes lgGrowY{from{opacity:1;clip-path:inset(50% 0 50% 0)}to{opacity:1;clip-path:inset(0 0 0 0)}}
@keyframes lgFade{from{opacity:0}to{opacity:1}}
.lgshine{position:absolute;inset:0;overflow:hidden;-webkit-mask-size:100% 100%;mask-size:100% 100%}
.lgshine i{position:absolute;top:-20%;bottom:-20%;left:0;width:34%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.95),transparent);transform:translateX(-130%) skewX(-20deg);animation:lgSweep 1s ease-in-out both}
@keyframes lgSweep{from{transform:translateX(-130%) skewX(-20deg)}to{transform:translateX(480%) skewX(-20deg)}}
"""


def animate_html(parts, t0, speed=1.0, include=None, shine=True):
    """Returns (html, sound_events). Everything lands exactly on the original logo; `speed` < 1 plays faster."""
    G = parts["g"]
    inc = include or list(G.keys())
    out, ev = [], []

    def add(cls, L, d, dur):
        out.append(f'<img class="lgl {cls}" src="{L["uri"]}" style="left:{L["x"]}px;top:{L["y"]}px;width:{L["w"]}px;height:{L["h"]}px;'
                   f'animation-delay:{t0 + d * speed:.2f}s;animation-duration:{dur * speed:.2f}s">')

    if "gear" in inc:
        add("lggear", G["gear"][0], 0.05, 0.85); ev.append({"kind": "pop", "t": t0 + 0.1 * speed})
    if "mono" in inc:
        for k, L in enumerate(G["mono"]):
            add("lgsl" if k == 0 else "lgsr", L, 0.15 + 0.12 * k, 0.55)
        ev.append({"kind": "hit", "t": t0 + 0.4 * speed, "g": 0.6})
    if "swoosh" in inc:
        add("lgwipe", G["swoosh"][0], 0.55, 0.8); ev.append({"kind": "whoosh", "t": t0 + 0.75 * speed, "pan": 0.3})
    if "pixels" in inc:
        for k, L in enumerate(G["pixels"]):
            add("lgpop", L, 0.95 + 0.09 * k, 0.4); ev.append({"kind": "pop", "t": t0 + (0.95 + 0.09 * k) * speed})
    if "syed" in inc:
        for k, L in enumerate(G["syed"]):
            add("lgrise", L, 1.05 + 0.07 * k, 0.5); ev.append({"kind": "tick", "t": t0 + (1.1 + 0.07 * k) * speed})
    if "auto" in inc:
        for k, L in enumerate(G["auto"]):
            add("lgrise", L, 1.4 + 0.05 * k, 0.5); ev.append({"kind": "tick", "t": t0 + (1.45 + 0.05 * k) * speed})
    if "rules" in inc:
        for L in G["rules"]:
            add("lggrow", L, 1.95, 0.55)
    if "tag" in inc:
        for L in G["tag"]:
            add("lgfade", L, 2.1, 0.5)
    if "div" in inc:
        for k, L in enumerate(G["div"]):
            add("lggrowy", L, 2.25 + 0.15 * k, 0.45)
    for k, key in enumerate(("i1", "i2", "i3", "i4")):
        if key in inc:
            for L in G[key]:
                add("lgpop", L, 2.3 + 0.18 * k, 0.5)
            ev.append({"kind": "pop", "t": t0 + (2.35 + 0.18 * k) * speed})
    if shine:
        d = (2.95 if "i1" in inc else 1.75) * speed
        out.append(f'<div class="lgshine" style="-webkit-mask-image:url({parts["full"]});mask-image:url({parts["full"]})"><i style="animation-delay:{t0 + d:.2f}s;animation-duration:{1.0 * speed + 0.3:.2f}s"></i></div>')
        ev.append({"kind": "chime", "t": t0 + d + 0.1})
    return "".join(out), ev
