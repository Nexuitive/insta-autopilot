"""Cinematic editorial kinetic-typography Reel: scale-contrast type, 3D camera, motion blur, film grain, soundtrack."""
import html, io, math, os, random, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import audio
import kinetic
import voice

B = audio.BEAT
DUR_BEATS = {"none": 4, "bell": 6, "hourglass": 7, "bulb": 6, "gears": 6, "growth": 7, "dashboard": 7, "checklist": 8, "phone_chat": 9}
END_DUR = 9 * B
FPS = 24
EXTRA = {  # per theme: wf = headline char width (em), waf = accent char width (em), lop = light strength
    "paper": dict(wf=0.54, waf=0.40, lop=0.20), "noir": dict(wf=0.68, waf=0.40, lop=0.30),
    "azure": dict(wf=0.56, waf=0.58, lop=0.16), "forest": dict(wf=0.42, waf=0.42, lop=0.32),
    "brand": dict(wf=0.54, waf=0.40, lop=0.30),
}
TRANS = ["zoom", "whip", "rise"]

CCSS = """
#v{perspective:1800px}
.bgl{position:absolute;inset:0;overflow:hidden}
.light{position:absolute;border-radius:50%;background:radial-gradient(circle,var(--ac) 0%,transparent 64%);opacity:var(--lop)}
.l1{width:1300px;height:1300px;left:-450px;top:-300px;animation:lt1 14s ease-in-out infinite alternate}
.l2{width:1100px;height:1100px;right:-500px;bottom:-250px;opacity:calc(var(--lop) * .7);animation:lt2 11s ease-in-out infinite alternate}
@keyframes lt1{to{transform:translate(260px,380px) scale(1.2)}}
@keyframes lt2{to{transform:translate(-320px,-300px) scale(1.15)}}
.dust i{position:absolute;border-radius:50%;background:var(--fg);opacity:0;animation:dust linear infinite}
@keyframes dust{0%{opacity:0;transform:translateY(0)}15%{opacity:.4}85%{opacity:.4}100%{opacity:0;transform:translateY(-560px)}}
.frame{position:absolute;inset:34px;border:2px solid rgba(128,128,128,.22);z-index:6}
.meta.l{left:70px}.meta.r{right:70px}
.meta{position:absolute;top:104px;font-family:var(--mf);font-size:24px;letter-spacing:.22em;text-transform:uppercase;opacity:.72;z-index:7}
.cbeat{position:absolute;inset:0}
.cinner{position:absolute;inset:0;box-sizing:border-box;padding:210px 80px 270px;display:flex;flex-direction:column;justify-content:center;gap:54px;align-items:var(--al)}
@keyframes cam{from{transform:perspective(2000px) rotateY(-1.6deg) scale(1)}to{transform:perspective(2000px) rotateY(1.6deg) scale(1.05)}}
@keyframes zin{from{opacity:0;transform:scale(.62)}to{opacity:1;transform:none}}
@keyframes zout{from{opacity:1;transform:none}to{opacity:0;transform:scale(1.7)}}
@keyframes win{from{opacity:1;transform:translateX(115%) skewX(-9deg)}to{opacity:1;transform:none}}
@keyframes wout{from{opacity:1;transform:none}to{opacity:1;transform:translateX(-115%) skewX(9deg)}}
@keyframes rin{from{opacity:0;transform:translateY(46%) scale(.94)}to{opacity:1;transform:none}}
@keyframes rout{from{opacity:1;transform:none}to{opacity:0;transform:translateY(-34%) scale(1.06)}}
.ghost2{position:absolute;right:-30px;top:170px;font-family:var(--hf);font-weight:800;font-size:760px;line-height:1;letter-spacing:-.06em;opacity:.05;color:var(--fg);animation:gdrift 6s ease-out both}
@keyframes gdrift{from{transform:translateX(-120px)}to{transform:none}}
.tw{width:100%;display:flex;flex-direction:column;gap:.18em;font-family:var(--hf);font-weight:var(--hw);text-transform:var(--ht);letter-spacing:var(--htr);line-height:var(--hlh)}
.tw.V0{text-align:center;align-items:center}.tw.V1{text-align:left;align-items:flex-start}
.tw.V2{height:1050px;justify-content:space-between}
.tw.V2 .pre{align-self:flex-start;text-align:left}.tw.V2 .post{align-self:flex-end;text-align:right}.tw.V2 .acc{align-self:center}
.pre,.post{max-width:900px;text-wrap:balance}
.wm{display:inline-block;overflow:hidden;padding:.06em .1em .18em .04em;margin:-.06em -.02em -.18em -.02em;vertical-align:top}
.wm i{display:inline-block;font-style:normal;transform:translateY(112%);animation:wrise .55s cubic-bezier(.2,.9,.25,1) both}
@keyframes wrise{from{transform:translateY(112%)}to{transform:none}}
.sp{display:inline-block;width:.26em}
.acc{font-family:var(--af);font-style:var(--ai);font-weight:var(--aw);color:var(--ac);text-transform:none;letter-spacing:-.015em;line-height:.98;perspective:900px;max-width:940px}
.aw{display:inline-block;white-space:nowrap}
.ch{display:inline-block;transform-origin:50% 100%;opacity:0;animation:chflip .6s cubic-bezier(.2,.9,.3,1.25) both}
@keyframes chflip{from{opacity:0;transform:rotateX(-88deg) translateY(.5em)}to{opacity:1;transform:none}}
.uw{position:relative;display:inline-block}
.ul{position:absolute;left:0;bottom:-.1em;width:100%;height:.2em;overflow:visible}
.ul path{fill:none;stroke:var(--ac);stroke-width:7px;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:2400;stroke-dashoffset:2400;animation:draw .7s ease-out both}
.pillw{display:inline-block;background:var(--ac);color:var(--acfg);padding:.02em .26em .08em;border-radius:.2em;transform-origin:left;animation:growx .5s cubic-bezier(.2,.9,.3,1) both}
.pillw .acc{color:var(--acfg)}
.lab{display:flex;align-items:center;gap:20px;font-family:var(--mf);font-size:26px;letter-spacing:.24em;text-transform:uppercase;font-weight:500;color:var(--fg);opacity:.85;margin-bottom:.9em;font-size:26px}
.lab i{display:block;width:96px;height:3px;background:var(--ac);transform-origin:left;animation:growx .6s both}
.lab span{opacity:0;animation:r2 .6s both}
.stage{flex:none;width:100%;height:700px;perspective:1500px;display:flex;justify-content:center;align-items:flex-start}
.stage .vis{transform:scale(1.16) rotateY(-9deg) rotateX(5deg);transform-origin:50% 0;margin-bottom:0;animation:float3d 5s ease-in-out infinite alternate}
@keyframes float3d{from{transform:scale(1.16) rotateY(-10deg) rotateX(6deg) translateY(0)}to{transform:scale(1.16) rotateY(8deg) rotateX(2deg) translateY(-20px)}}
.streak{position:absolute;left:-20%;width:140%;height:5px;background:linear-gradient(90deg,transparent,var(--ac),#fff,var(--ac),transparent);box-shadow:0 0 50px 10px var(--ac);opacity:0;animation:streak .8s ease-out both;z-index:8}
@keyframes streak{0%{opacity:0;transform:translateX(-70%)}30%{opacity:.85}100%{opacity:0;transform:translateX(70%)}}
.brandbig{font-family:var(--hf);font-weight:var(--hw);text-transform:var(--ht);letter-spacing:var(--htr);line-height:.95;text-align:center}
.endnote{font-family:var(--mf);font-size:28px;letter-spacing:.2em;text-transform:uppercase;opacity:.75;text-align:center}
"""


def _split3(text):
    toks, hl = [], False
    text = text.replace("'", "\u2019").replace("...", "\u2026")
    import re
    text = re.sub(r"\*([^*]+)\*([?!.,:;\u2026]+)", r"*\1\2*", text)
    for part in re.split(r"(\*)", text):
        if part == "*":
            hl = not hl
            continue
        toks += [(w, hl) for w in part.split()]
    idx = [i for i, (_, h) in enumerate(toks) if h]
    if not idx:
        idx = [len(toks) - 1]
    a = idx[0]
    b = a
    while b + 1 < len(toks) and toks[b + 1][1]:
        b += 1
    return [w for w, _ in toks[:a]], [w for w, _ in toks[a:b + 1]], [w for w, _ in toks[b + 1:]]


def _mask_words(words, t, step=0.08):
    return "".join(f'<span class="wm"><i style="animation-delay:{t + k * step:.2f}s">{html.escape(w)}</i></span><span class="sp"></span>'
                   for k, w in enumerate(words))


def _acc_chars(words, t):
    out, k = [], 0
    for wi, w in enumerate(words):
        chars = "".join(f'<span class="ch" style="animation-delay:{t + (k + j) * 0.04:.2f}s">{html.escape(c)}</span>' for j, c in enumerate(w))
        k += len(w)
        out.append(f'<span class="aw">{chars}</span>')
    return '<span class="sp"></span>'.join(out), k


def _label(i, n):
    if i == 0:
        return ""
    if i == n - 1:
        return "YOUR MOVE"
    if i <= max(1, round(n * 0.25)):
        return "THE PROBLEM"
    if i == n - 2:
        return "THE RESULT"
    return f"THE FIX / {i - max(1, round(n * 0.25)):02d}"


def build(reel, cfg, theme_idx=0, vo_durs=None):
    th = kinetic.THEMES[theme_idx % len(kinetic.THEMES)]
    ex = EXTRA[th["name"]]
    beats = reel["beats"]
    n = len(beats)
    handle = html.escape(cfg["brand"]["handle"])
    events, beats_html, segs, streaks = [], "", "", ""
    starts, t = [], 0.0
    durs = []
    for i, b in enumerate(beats):
        d = DUR_BEATS.get(b.get("visual", "none"), 4) * B
        if vo_durs and vo_durs[i]:  # each beat lasts long enough for its voice line
            d = max(d, math.ceil((0.30 + vo_durs[i] + 0.3) / B) * B)
        durs.append(d)
    for d in durs:
        starts.append(t)
        t += d
    end = t
    total = end + END_DUR
    boundaries = [(starts[i + 1] if i + 1 < n else end) for i in range(n)]
    tr = [TRANS[j % 3] for j in range(n + 1)]  # tr[j] = transition INTO beat j (j=0 is the opening)
    streak_y = [620, 1180, 820, 1400, 700, 1000, 900]
    for i, bt in enumerate(beats):
        t0, d = starts[i], durs[i]
        vis = bt.get("visual", "none")
        pre, acc, post = _split3(bt["text"])
        has_v = vis in kinetic.VISUALS
        variant = (i % 2) if has_v else [0, 1, 2, 1][i % 4]
        plen = len(" ".join(pre)); alen = len(" ".join(acc)); olen = len(" ".join(post))
        side = max(plen, olen, 1)
        S = max(54, min(134 * th["fsm"], 880 / (min(side, 14) * ex["wf"])))
        if has_v:
            S *= 0.8
        A = min(S * (2.3 if has_v else 2.9), 940 / (max(alen, 1) * ex["waf"]))
        A = max(A, S * 1.15)
        if variant == 2:
            S *= 0.72
            A = min(A * 1.3, 940 / (max(alen, 1) * ex["waf"]))
        a0 = t0 + 0.2 + len(pre) * 0.08 + 0.1
        acc_html, nch = _acc_chars(acc, a0)
        ae = a0 + nch * 0.04 + 0.45
        acc_block = f'<div class="acc" style="font-size:{A:.0f}px">{acc_html}</div>'
        if th["pill"]:
            acc_block = f'<div style="line-height:1"><span class="pillw" style="animation-delay:{a0 - 0.05:.2f}s"><span class="acc" style="font-size:{A:.0f}px">{acc_html}</span></span></div>'
        else:
            acc_block = (f'<div class="acc" style="font-size:{A:.0f}px"><span class="uw">{acc_html}'
                         f'<svg class="ul" viewBox="0 0 300 20" preserveAspectRatio="none"><path style="animation-delay:{ae - 0.2:.2f}s" d="M4 13C60 3 150 20 296 7"/></svg></span></div>')
        lab = _label(i, n)
        lab_html = (f'<div class="lab"><i style="animation-delay:{t0 + 0.12:.2f}s"></i><span style="animation-delay:{t0 + 0.2:.2f}s">{lab}</span></div>' if lab else "")
        pre_html = f'<div class="pre" style="font-size:{S:.0f}px">{_mask_words(pre, t0 + 0.2)}</div>' if pre else ""
        post_html = f'<div class="post" style="font-size:{S:.0f}px">{_mask_words(post, ae - 0.25)}</div>' if post else ""
        stage = f'<div class="stage">{kinetic.VISUALS[vis](t0 + 0.65)}</div>' if has_v else ""
        al = "flex-start" if variant == 1 else "center"
        tin = tr[i]
        tout = tr[i + 1]
        anim = (f"z{'in'} .5s {t0:.2f}s backwards" if tin == "zoom" else f"{'win' if tin == 'whip' else 'rin'} .5s {t0:.2f}s backwards")
        anim = {"zoom": "zin", "whip": "win", "rise": "rin"}[tin] + f" .5s cubic-bezier(.1,.75,.2,1) {t0:.2f}s backwards, " + \
               {"zoom": "zout", "whip": "wout", "rise": "rout"}[tout] + f" .42s cubic-bezier(.6,0,.9,.45) {boundaries[i] - 0.05:.2f}s forwards"
        beats_html += (f'<div class="cbeat" style="animation:{anim}"><div class="ghost2" style="animation-delay:{t0:.2f}s">{i + 1:02d}</div>'
                       f'<div class="meta r">{i + 1:02d} / {n:02d}</div>'
                       f'<div class="cinner" style="--al:{al};animation:cam {d + 0.6:.2f}s {t0:.2f}s linear both">'
                       f'<div class="tw V{variant}">{lab_html}{pre_html}{acc_block}{post_html}</div>{stage}</div></div>')
        segs += f'<i><b style="animation-duration:{d:.2f}s;animation-delay:{t0:.2f}s"></b></i>'
        events.append({"kind": "hit", "t": a0 + 0.04, "g": 0.8 if i else 1.0})
        if i + 1 <= n:
            events.append({"kind": "whoosh", "t": boundaries[i], "pan": (-0.4 if i % 2 else 0.4)})
            streaks += f'<div class="streak" style="top:{streak_y[i % 7]}px;animation-delay:{boundaries[i] - 0.15:.2f}s"></div>'
    # ---- end card
    cur_t = end + 1.5
    segs += f'<i><b style="animation-duration:{END_DUR:.2f}s;animation-delay:{end:.2f}s"></b></i>'
    brand = html.escape(cfg["brand"]["name"])
    end_html = f'''<div class="cbeat" style="animation:{ {"zoom": "zin", "whip": "win", "rise": "rin"}[tr[n]] } .5s cubic-bezier(.1,.75,.2,1) {end:.2f}s backwards"><div class="cinner" style="--al:center;gap:34px">
<svg viewBox="0 0 100 100" width="250" height="250" class="pp" style="animation-delay:{end + 0.35:.2f}s"><g style="transform-origin:50px 50px;animation:spin 10s linear infinite"><circle cx="50" cy="50" r="40" fill="none" stroke="var(--ac)" stroke-width="12" stroke-dasharray="5.2 5.2"/></g><circle cx="50" cy="50" r="33" fill="var(--ac)"/><text x="50" y="66" text-anchor="middle" font-size="46" font-weight="800" fill="var(--acfg)" style="font-family:var(--hf)">S</text></svg>
<div class="brandbig rise2" style="font-size:{th["bs"] + 14}px;white-space:nowrap;animation-delay:{end + 0.6:.2f}s">{brand}</div>
<div class="endnote rise2" style="animation-delay:{end + 0.8:.2f}s">AI bots &middot; automations &middot; web apps</div>
<div style="position:relative;margin-top:26px"><div class="cta" style="font-size:{th["cs"]}px;white-space:nowrap;animation-delay:{end + 1.1:.2f}s,{cur_t + 1.1:.2f}s,{cur_t + 1.6:.2f}s">DM AUTOMATE</div><div class="tap" style="animation-delay:{cur_t + 1.15:.2f}s"></div>
<svg class="cur" style="animation-delay:{cur_t:.2f}s" width="110" height="110" viewBox="0 0 100 100"><path d="M18 8L18 78L38 62L52 92L66 86L52 56L78 56Z" fill="#fff" stroke="#111" stroke-width="6" stroke-linejoin="round"/></svg></div>
<div class="rise2" style="font-size:44px;font-weight:700;animation-delay:{end + 1.5:.2f}s">Free 15-minute automation call</div>
<div class="endnote rise2" style="animation-delay:{end + 1.8:.2f}s">Follow {handle} for daily tips</div></div></div>'''
    events += [{"kind": "riser", "t": max(end - 0.4, 0), "dur": 1.5}, {"kind": "sting", "t": end + 1.12}, {"kind": "click", "t": cur_t + 1.15}]
    rnd = random.Random(11)
    dust = "".join(f'<i style="left:{rnd.randint(30, 1050)}px;top:{rnd.randint(500, 1900)}px;width:{(s := rnd.randint(4, 10))}px;height:{s}px;animation-duration:{rnd.randint(7, 14)}s;animation-delay:-{rnd.randint(0, 12)}s"></i>' for _ in range(22))
    page = (f'<html><head><meta charset="utf-8"><style>{kinetic.font_css(th["fonts"] + ["dmmono"])}{kinetic.CSS}{CCSS}</style></head><body>'
            f'<div id="v" style="--bg:{th["bg"]};--fg:{th["fg"]};--ac:{th["ac"]};--card:{th["card"]};--muted:{th["muted"]};--acfg:{th["acfg"]};--lop:{ex["lop"]};'
            f'--hf:{th["hf"]};--hw:{th["hw"]};--ht:{th["ht"]};--htr:{th["htr"]};--hlh:{th["hlh"]};--af:{th["af"]};--ai:{th["ai"]};--aw:{th["aw"]};--asc:1;--bf:{kinetic.BF};--mf:\'DM Mono\',monospace">'
            f'<div class="bgl"><div class="light l1"></div><div class="light l2"></div></div><div class="grid"></div><div class="dust">{dust}</div>'
            f'{beats_html}{end_html}{streaks}<div class="frame"></div><div class="seg">{segs}</div><div class="meta l">{handle}</div></div></body></html>')
    trans_windows = [(b - 0.2, b + 0.55) for b in boundaries]
    return page, total, events, trans_windows, starts, end


FIT_JS = """()=>{
  const MAXW = 860;
  const fit = (el, words) => {
    const ws = [...el.querySelectorAll(words)];
    if (!ws.length) return;
    const widest = Math.max(...ws.map(w => w.offsetWidth));
    if (widest > MAXW) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * MAXW / widest) + 'px';
  };
  document.querySelectorAll('.acc').forEach(a => fit(a, '.aw'));
  document.querySelectorAll('.pre,.post').forEach(a => fit(a, '.wm'));
  document.querySelectorAll('.brandbig').forEach(a => { const w = a.offsetWidth; if (w > 900) a.style.fontSize = (parseFloat(getComputedStyle(a).fontSize) * 900 / w) + 'px'; });
}"""


def fit_text(pg):
    """Shrinks any word that would run past the frame (measured after the fonts have loaded)."""
    pg.evaluate("document.fonts.ready")
    pg.evaluate(FIT_JS)
    pg.evaluate(FIT_JS)


ICSS = """
#v{height:1350px}
.ipost{position:absolute;inset:0;box-sizing:border-box;padding:96px 70px 64px;display:flex;flex-direction:column;gap:26px}
.itop{display:flex;justify-content:space-between;align-items:center;font-family:var(--mf);font-size:24px;letter-spacing:.22em;text-transform:uppercase;opacity:.8}
.itop b{padding:10px 22px;border-radius:30px;background:var(--ac);color:var(--acfg);font-weight:500;letter-spacing:.16em}
.ipost .tw{gap:.16em}
.isub{font-size:38px;line-height:1.28;font-weight:500;opacity:.86;max-width:900px}
.ipost .stage{height:560px;margin-top:-6px}
.ipost .stage .vis{transform:scale(.86) rotateY(-8deg) rotateX(4deg);transform-origin:50% 0;animation:none}
.ifoot{margin-top:auto;display:flex;justify-content:space-between;align-items:center}
.save{display:flex;align-items:center;gap:16px;font-family:var(--mf);font-size:26px;letter-spacing:.2em;text-transform:uppercase;opacity:.85}
.pillbtn{padding:20px 46px;border-radius:50px;background:var(--ac);color:var(--acfg);font-family:var(--hf);font-weight:var(--hw);font-size:38px;letter-spacing:2px;text-transform:uppercase}
"""


def render_image(post, cfg, out_jpg, theme_idx=0):
    """Editorial single-image post (1080x1350): scale-contrast headline, 3D mockup, save + DM call to action."""
    th = kinetic.THEMES[theme_idx % len(kinetic.THEMES)]
    ex = EXTRA[th["name"]]
    handle = html.escape(cfg["brand"]["handle"])
    vis = post.get("visual", "none")
    has_v = vis in kinetic.VISUALS
    pre, acc, post_w = _split3(post["headline"])
    plen, alen, olen = len(" ".join(pre)), len(" ".join(acc)), len(" ".join(post_w))
    side = max(plen, olen, 1)
    S = max(52, min((118 if not has_v else 92) * th["fsm"], 880 / (min(side, 14) * ex["wf"])))
    A = max(min(S * (2.5 if not has_v else 2.2), 940 / (max(alen, 1) * ex["waf"])), S * 1.15)
    acc_html, nch = _acc_chars(acc, 0.1)
    if th["pill"]:
        acc_block = f'<div style="line-height:1"><span class="pillw"><span class="acc" style="font-size:{A:.0f}px">{acc_html}</span></span></div>'
    else:
        acc_block = (f'<div class="acc" style="font-size:{A:.0f}px"><span class="uw">{acc_html}'
                     f'<svg class="ul" viewBox="0 0 300 20" preserveAspectRatio="none"><path d="M4 13C60 3 150 20 296 7"/></svg></span></div>')
    pre_html = f'<div class="pre" style="font-size:{S:.0f}px">{_mask_words(pre, 0.1)}</div>' if pre else ""
    post_html = f'<div class="post" style="font-size:{S:.0f}px">{_mask_words(post_w, 0.6)}</div>' if post_w else ""
    label = "PROBLEM \u2192 FIX" if post.get("post_type") != "result" else "THE RESULT"
    stage = f'<div class="stage">{kinetic.VISUALS[vis](0.2)}</div>' if has_v else ""
    sub = html.escape(post["subline"].replace("'", "\u2019"))
    body = (f'<div class="ipost {"pillth" if th["pill"] else ""}"><div class="itop"><span>{handle}</span><b>{label}</b></div>'
            f'<div class="tw V1" style="--al:flex-start">{pre_html}{acc_block}{post_html}</div>'
            f'<div class="isub">{sub}</div>{stage}'
            f'<div class="ifoot"><div class="save"><svg width="34" height="40" viewBox="0 0 34 40"><path d="M4 3H30V37L17 28L4 37Z" fill="none" stroke="var(--fg)" stroke-width="3.5" stroke-linejoin="round"/></svg>Save this</div>'
            f'<div class="pillbtn">DM AUTOMATE</div></div></div>')
    rnd = random.Random(5)
    dust = "".join(f'<i style="left:{rnd.randint(30, 1050)}px;top:{rnd.randint(200, 1300)}px;width:{(s := rnd.randint(4, 9))}px;height:{s}px;opacity:.35;animation:none"></i>' for _ in range(16))
    page = (f'<html><head><meta charset="utf-8"><style>{kinetic.font_css(th["fonts"] + ["dmmono"])}{kinetic.CSS}{CCSS}{ICSS}</style></head><body>'
            f'<div id="v" style="--bg:{th["bg"]};--fg:{th["fg"]};--ac:{th["ac"]};--card:{th["card"]};--muted:{th["muted"]};--acfg:{th["acfg"]};--lop:{ex["lop"]};'
            f'--hf:{th["hf"]};--hw:{th["hw"]};--ht:{th["ht"]};--htr:{th["htr"]};--hlh:{th["hlh"]};--af:{th["af"]};--ai:{th["ai"]};--aw:{th["aw"]};--asc:1;--bf:{kinetic.BF};--mf:\'DM Mono\',monospace">'
            f'<div class="bgl"><div class="light l1"></div><div class="light l2"></div></div><div class="grid"></div><div class="dust">{dust}</div>{body}<div class="frame"></div></div></body></html>')
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(page, wait_until="networkidle")
        fit_text(pg)
        pg.evaluate("""()=>{const p=document.querySelector('.ipost');const st=p.querySelector('.stage');const vis=st&&st.querySelector('.vis');let s=0.86;
          for(let i=0;i<12&&p.scrollHeight>p.clientHeight+2;i++){
            if(vis&&s>0.5){s-=0.06;vis.style.transform='scale('+s+') rotateY(-8deg) rotateX(4deg)';st.style.height=(640*s)+'px';}
            else{p.querySelectorAll('.pre,.post,.acc').forEach(e=>{e.style.fontSize=(parseFloat(getComputedStyle(e).fontSize)*0.94)+'px'});}
          }}""")
        pg.evaluate("window.__a=document.getAnimations(); window.__a.forEach(a=>a.pause())")
        pg.evaluate("t=>window.__a.forEach(a=>{a.currentTime=t})", 6000.0)
        pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>requestAnimationFrame(r))))")
        pg.screenshot(path=out_jpg, type="jpeg", quality=95)
        br.close()
    return out_jpg


def render_cinematic(reel, cfg, out_mp4, theme_idx=0, fps=FPS):
    """Renders the Reel. Returns the name of the voice engine used ('none' = music only)."""
    n = len(reel["beats"])
    lines = [(b.get("vo") or b["text"]).replace("*", "") for b in reel["beats"]] + [reel.get("vo_end", "Follow for daily automation tips.")]
    clips, engine = voice.synthesize(lines, cfg)
    vo_durs = [len(c) / voice.SR for c in clips[:n]] if clips else None
    page, total, events, windows, starts, end = build(reel, cfg, theme_idx, vo_durs)
    tmp = tempfile.mkdtemp()
    try:
        vlist = [(starts[i] + 0.30, clips[i]) for i in range(n)] + [(end + 2.0, clips[n])] if clips else None
        wav = audio.make_soundtrack(events, total, os.path.join(tmp, "s.wav"), seed=theme_idx + 3, vo_clips=vlist)
        nframes = int(total * fps)
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(page, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            fit_text(pg)
            pg.evaluate("window.__a=document.getAnimations(); window.__a.forEach(a=>a.pause())")
            shutter = 0.5 / fps
            for i in range(nframes):
                ft = i / fps
                k = 3 if any(a <= ft <= b for a, b in windows) else 1
                offs = [0.0] if k == 1 else [(j / (k - 1) - 0.5) * shutter for j in range(k)]
                shots = []
                for o in offs:
                    pg.evaluate("t=>window.__a.forEach(a=>{a.currentTime=t})", max(ft + o, 0) * 1000.0)
                    shots.append(pg.screenshot(type="jpeg", quality=93))
                if k == 1:
                    open(f"{tmp}/{i:04d}.jpg", "wb").write(shots[0])
                else:
                    arr = np.mean([np.asarray(Image.open(io.BytesIO(s)).convert("RGB"), dtype=np.float32) for s in shots], axis=0)
                    Image.fromarray(arr.astype("uint8")).save(f"{tmp}/{i:04d}.jpg", quality=94)
            br.close()
        vf = "eq=contrast=1.05:saturation=1.08,noise=alls=3:allf=t,vignette=angle=PI/5,format=yuv420p"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg", "-i", wav,
                        "-vf", vf, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "5M", "-bufsize", "10M", "-r", str(fps),
                        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return engine
