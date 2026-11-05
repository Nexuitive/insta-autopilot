"""Branded image (1080x1080) and animated Reel (1080x1920 MP4) from the day's post."""
import html, os, shutil, subprocess, tempfile
from string import Template
from playwright.sync_api import sync_playwright

STYLES = {  # bg, text, accent, text-on-accent
    "amber": ("#FFB547", "#0E1B2C", "#0E1B2C", "#FFB547"),
    "dark":  ("#0E1B2C", "#F5F7FA", "#FFB547", "#0E1B2C"),
    "paper": ("#F5F7FA", "#0E1B2C", "#FFB547", "#0E1B2C"),
}
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&'
         'family=Inter:wght@500&display=swap" rel="stylesheet">')

IMG = Template("""<html><head><meta charset="utf-8">$fonts<style>body{margin:0}</style></head><body>
<div style="width:1080px;height:1080px;box-sizing:border-box;padding:84px;display:flex;flex-direction:column;justify-content:space-between;background:$bg;color:$fg;font-family:'Inter',Arial,sans-serif">
<div style="display:flex;justify-content:space-between;align-items:center;font-size:26px;letter-spacing:4px;font-weight:500"><span>AI AUTOMATION</span><span style="padding:10px 24px;border-radius:40px;background:$ac;color:$chip">$tag</span></div>
<div><h1 style="margin:0;font-family:'Space Grotesk',Arial,sans-serif;font-size:${fs}px;line-height:1.05;font-weight:700">$head</h1>
<div style="margin-top:36px;font-size:40px;line-height:1.3;font-weight:500;opacity:.9">$sub</div></div>
<div style="display:flex;justify-content:space-between;align-items:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:32px"><span>$handle</span><span>DM &quot;AUTOMATE&quot;</span></div>
</div></body></html>""")

def render(post, cfg, style, out_path):
    """Branded 1080x1080 image post."""
    bg, fg, ac, chip = STYLES[style]
    head = post["headline"]
    v = dict(fonts=FONTS, bg=bg, fg=fg, ac=ac, chip=chip, head=html.escape(head), sub=html.escape(post["subline"]),
             handle=html.escape(cfg["brand"]["handle"]),
             tag=html.escape(post.get("post_type", "TIP").replace("_", " ").upper()),
             fs=124 if len(head) <= 24 else 104 if len(head) <= 42 else 86)
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1080})
        pg.set_content(IMG.safe_substitute(v), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=out_path)
        br.close()

import math, random as _rnd

NAVY, AMBER, TEAL, CORAL, CREAM, SKIN, WHITE = "#0E1B2C", "#FFB547", "#2EC4B6", "#FF6B5A", "#FFF4E0", "#F2C6A0", "#F5F7FA"
T = {1: (0, 3.6), 2: (3.6, 9.6), 3: (9.6, 15.6), 4: (15.6, 21.6), 5: (21.6, 27.0), 6: (27.0, 31.4), 7: (31.4, 36.4)}
DUR = 36.4
BG = {1: AMBER, 2: NAVY, 3: CREAM, 4: NAVY, 5: CREAM, 6: NAVY, 7: AMBER}
FG = {1: NAVY, 2: WHITE, 3: NAVY, 4: WHITE, 5: NAVY, 6: WHITE, 7: NAVY}


def D(s, t):
    return f"{T[s][0] + t:.2f}"


CSS = """
body{margin:0}
#v{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0E1B2C;font-family:'Inter',Arial,sans-serif}
.sc{position:absolute;inset:0;opacity:0;overflow:hidden}
@keyframes show{0%,99.9%{opacity:1}100%{opacity:0}}
@keyframes stay{from{opacity:1}to{opacity:1}}
.cam{position:absolute;inset:0;box-sizing:border-box;padding:230px 80px 330px;display:flex;flex-direction:column;align-items:center;gap:34px;transform-origin:50% 50%}
@keyframes zoom{from{transform:scale(1)}to{transform:scale(1.06)}}
.bar{position:absolute;top:0;left:0;height:14px;width:100%;background:#2EC4B6;transform-origin:left;animation:prog 36.4s linear both;z-index:9}
@keyframes prog{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.wipe{position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;border-radius:50%;transform:scale(0);animation:wc 1s both;z-index:8}
@keyframes wc{0%{transform:scale(0)}40%,60%{transform:scale(1)}100%{transform:scale(0)}}
.stripes{position:absolute;inset:0;display:flex;z-index:8}
.stripes i{flex:1;transform:translateY(-101%);animation:ws 1.1s both}
@keyframes ws{0%{transform:translateY(-101%)}35%,65%{transform:none}100%{transform:translateY(101%)}}
.slab{position:absolute;left:50%;margin-left:-800px;top:-300px;width:1600px;height:2520px;transform:translateX(-1800px) skewX(-12deg);animation:wl 1s both;z-index:8}
@keyframes wl{0%{transform:translateX(-1800px) skewX(-12deg)}38%,62%{transform:translateX(0) skewX(-12deg)}100%{transform:translateX(1800px) skewX(-12deg)}}
.fl{position:absolute;opacity:.25;animation:fl 5s ease-in-out infinite alternate}
@keyframes fl{to{transform:translate(60px,-90px) rotate(40deg)}}
.r{opacity:0;animation-name:rise;animation-duration:.7s;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1)}
@keyframes rise{from{opacity:0;transform:translateY(80px)}to{opacity:1;transform:none}}
.p{opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes bob{to{transform:translateY(-14px)}}
@keyframes shake{from{transform:rotate(-5deg)}to{transform:rotate(5deg)}}
@keyframes wave{from{transform:rotate(-22deg)}to{transform:rotate(22deg)}}
@keyframes cheer{from{transform:rotate(150deg)}to{transform:rotate(190deg)}}
@keyframes blink{0%,90%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
@keyframes sweat{0%{opacity:0;transform:translateY(-10px)}30%{opacity:1}100%{opacity:0;transform:translateY(60px)}}
@keyframes blip{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.35)}}
@keyframes tw{0%,100%{transform:scale(.3) rotate(0);opacity:.2}50%{transform:scale(1) rotate(45deg);opacity:1}}
.kick{font-size:36px;letter-spacing:7px;font-weight:500;opacity:.85}
.ttl{margin:0;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:84px;line-height:1.1;text-align:center}
.hl{background:linear-gradient(#FFB547,#FFB547) no-repeat 0 90%/0% 34%;animation:hl .8s both;padding:0 8px}
@keyframes hl{to{background-size:100% 34%}}
.s2 .hl,.s4 .hl,.s6 .hl{background-image:linear-gradient(#FF6B5A,#FF6B5A)}
.chip{padding:14px 34px;border-radius:50px;background:#0E1B2C;color:#FFB547;font-size:38px;letter-spacing:5px;font-weight:500}
.hook{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:var(--hs);line-height:1.08;text-align:center}
.w{display:inline-block;margin:0 14px 10px;opacity:0;animation:wpop .7s cubic-bezier(.3,1.4,.5,1) both}
.w.last{background:#0E1B2C;color:#FFB547;padding:0 26px;border-radius:30px}
@keyframes wpop{0%{opacity:0;transform:translateY(70px) scale(.5) rotate(-8deg)}100%{opacity:1;transform:none}}
.ring{position:absolute;left:50%;top:50%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;border:10px solid #0E1B2C;opacity:0;animation:ripple 2.4s ease-out infinite both}
@keyframes ripple{from{transform:scale(.4);opacity:.45}to{transform:scale(4.2);opacity:0}}
.art{position:relative;width:920px;height:560px;flex:none}
.bub{position:absolute;width:120px;height:86px;border-radius:26px;background:#F5F7FA;animation:pop .5s cubic-bezier(.3,1.5,.5,1) both,bob 1.6s ease-in-out infinite alternate;opacity:0}
.bub::after{content:"";position:absolute;left:18px;bottom:-14px;border:14px solid transparent;border-top-color:#F5F7FA;border-bottom:0}
.bub i{position:absolute;right:-14px;top:-14px;width:40px;height:40px;border-radius:50%;background:#FF6B5A;color:#fff;font:700 28px/40px 'Space Grotesk',Arial,sans-serif;text-align:center;font-style:normal}
.bub b{position:absolute;left:22px;right:22px;top:26px;height:10px;border-radius:5px;background:#0E1B2C;opacity:.7;box-shadow:0 20px 0 #0E1B2C}
.note{box-sizing:border-box;width:820px;padding:20px 36px;border-radius:14px;color:#0E1B2C;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:52px;line-height:1.1;box-shadow:0 14px 0 rgba(0,0,0,.28);opacity:0;animation:dropin .8s both;transform:rotate(var(--rot))}
@keyframes dropin{0%{opacity:0;transform:translateY(-700px) rotate(-14deg)}55%{opacity:1;transform:translateY(18px) rotate(var(--rot))}75%{transform:translateY(-8px) rotate(var(--rot))}100%{opacity:1;transform:rotate(var(--rot))}}
.notes{position:relative;display:flex;flex-direction:column;gap:34px;align-items:center}
.stamp{position:absolute;right:20px;bottom:-104px;border:9px solid #FF6B5A;color:#FF6B5A;border-radius:16px;padding:4px 24px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:64px;letter-spacing:5px;background:rgba(14,27,44,.92);opacity:0;animation:slam .5s both;z-index:3}
@keyframes slam{0%{opacity:0;transform:scale(2.8) rotate(-14deg)}70%{opacity:1;transform:scale(.94) rotate(-14deg)}100%{opacity:1;transform:scale(1) rotate(-14deg)}}
.chp{box-sizing:border-box;width:880px;padding:22px 40px;border-radius:44px;text-align:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:56px;line-height:1.1}
.chp small{display:block;font-family:'Inter',Arial,sans-serif;font-size:26px;letter-spacing:5px;font-weight:500;opacity:.8;margin-bottom:6px}
.stream{position:relative;width:300px;height:120px;flex:none}
.m{position:absolute;left:100px;top:0;width:100px;height:70px;border-radius:22px;background:#fff;border:6px solid #0E1B2C;opacity:0;animation:drop 1.5s linear infinite both}
.m.o{background:#2EC4B6;animation-name:drop2}
.m.o::after{content:"";position:absolute;left:28px;top:12px;width:22px;height:34px;border:solid #0E1B2C;border-width:0 9px 9px 0;transform:rotate(40deg) scale(.7)}
@keyframes drop{0%{opacity:0;transform:translateY(-20px) scale(.7)}20%{opacity:1}80%{opacity:1}100%{opacity:0;transform:translateY(80px) scale(.3)}}
@keyframes drop2{0%{opacity:0;transform:translateY(-10px) scale(.3)}25%{opacity:1}80%{opacity:1}100%{opacity:0;transform:translateY(90px) scale(.9)}}
.step{box-sizing:border-box;display:flex;align-items:center;gap:36px;width:920px;padding:26px 36px;border-radius:40px;background:#16304D;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:56px;line-height:1.12;opacity:0;animation:slidein .8s cubic-bezier(.2,1.2,.4,1) both}
@keyframes slidein{from{opacity:0;transform:translateX(var(--from))}to{opacity:1;transform:none}}
.num{flex:none;width:120px;height:120px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:72px;color:#0E1B2C}
.vline{width:12px;height:46px;border-radius:6px;background:rgba(245,247,250,.4);transform-origin:top;transform:scaleY(0);animation:growY .4s both}
@keyframes growY{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.live{padding:16px 44px;border-radius:50px;background:#2EC4B6;color:#0E1B2C;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:46px;letter-spacing:3px;opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both}
.pan{position:relative;box-sizing:border-box;width:920px;height:470px;border-radius:48px;overflow:hidden;padding:38px 46px;flex:none}
.pan .lab{display:inline-block;padding:10px 30px;border-radius:40px;font-size:34px;letter-spacing:6px;font-weight:500}
.pan .txt{margin-top:26px;max-width:520px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:62px;line-height:1.1}
.pb{background:#0E1B2C;color:#F5F7FA;opacity:0;animation:slidein .8s cubic-bezier(.2,1.2,.4,1) both;--from:-600px}
.pa{background:#2EC4B6;color:#0E1B2C;clip-path:inset(0 0 100% 0);animation:reveal .9s ease-out both}
@keyframes reveal{to{clip-path:inset(0 0 0 0)}}
.spark{position:absolute;opacity:0;animation:tw 1.4s ease-in-out infinite}
.row{display:flex;align-items:center;gap:44px;width:900px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:70px;line-height:1.1}
.badge{flex:none;width:150px;height:150px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.conf{position:absolute;left:540px;top:1000px;opacity:0;animation:burst 1.5s ease-out both}
@keyframes burst{0%{opacity:1;transform:translate(0,0) scale(.3)}100%{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}}
.hd{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:72px;line-height:1.1;text-align:center}
.btn{position:relative;width:800px;height:210px;border-radius:60px;background:#0E1B2C;color:#FFB547;display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:100px;letter-spacing:4px;opacity:0;animation:pop .7s cubic-bezier(.3,1.5,.5,1) both,press .35s both,glow 1.6s infinite}
@keyframes press{0%,100%{transform:scale(1)}50%{transform:scale(.93)}}
@keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(14,27,44,.4)}50%{box-shadow:0 0 0 30px rgba(14,27,44,0)}}
.cur{position:absolute;left:560px;top:120px;opacity:0;animation:cur 1.3s cubic-bezier(.4,0,.2,1) both}
@keyframes cur{0%{opacity:0;transform:translate(300px,420px)}15%{opacity:1}100%{opacity:1;transform:translate(0,0)}}
.tap{position:absolute;left:640px;top:150px;width:90px;height:90px;margin:-45px 0 0 -45px;border-radius:50%;border:8px solid #FFF4E0;opacity:0;animation:tap 1s ease-out both}
@keyframes tap{from{opacity:.9;transform:scale(.3)}to{opacity:0;transform:scale(3)}}
"""


def _scene_css():
    out = ""
    for s, (a, b) in T.items():
        name = "stay" if s == 7 else "show"
        out += (f".s{s}{{background:{BG[s]};color:{FG[s]};animation:{name} {b - a:.2f}s {a}s forwards}}"
                f".s{s} .cam{{animation:zoom {b - a:.2f}s {a}s linear both}}")
    return out


def _shapes(color, seed):
    rnd = _rnd.Random(seed)
    return "".join(
        f'<div class="fl" style="left:{rnd.randint(0, 960)}px;top:{rnd.randint(120, 1700)}px;width:{s}px;height:{s}px;'
        f'border-radius:{rnd.choice(["50%", "50%", "22%"])};background:{color};animation-delay:-{rnd.randint(0, 5)}s"></div>'
        for s in [rnd.randint(50, 130) for _ in range(6)])


def _person(happy=False, w=360, h=408, style=""):
    mouth = "M128 148Q150 172 172 148" if happy else "M132 156Q150 142 168 156"
    extra = "" if happy else f'<path d="M208 96q12 20 0 30q-12-10 0-30z" fill="#7FD8FF" style="animation:sweat 1.2s infinite"/>'
    arm_l = (f'<g style="transform-origin:96px 215px;animation:cheer .5s ease-in-out infinite alternate"><rect x="62" y="205" width="34" height="110" rx="17" fill="{TEAL}"/><circle cx="79" cy="322" r="19" fill="{SKIN}"/></g>'
             if happy else
             f'<g style="transform-origin:96px 215px;animation:wave .35s ease-in-out infinite alternate"><rect x="62" y="205" width="34" height="110" rx="17" fill="{TEAL}"/><circle cx="79" cy="322" r="19" fill="{SKIN}"/></g>')
    arm_r = (f'<g style="transform-origin:204px 215px;animation:cheer .5s ease-in-out infinite alternate-reverse"><rect x="204" y="205" width="34" height="110" rx="17" fill="{TEAL}"/><circle cx="221" cy="322" r="19" fill="{SKIN}"/></g>'
             if happy else
             f'<g style="transform-origin:204px 215px;animation:wave .42s ease-in-out infinite alternate-reverse"><rect x="204" y="205" width="34" height="110" rx="17" fill="{TEAL}"/><circle cx="221" cy="322" r="19" fill="{SKIN}"/></g>')
    head_anim = "bob .6s ease-in-out infinite alternate" if happy else "shake .45s ease-in-out infinite alternate"
    return f'''<svg viewBox="0 0 300 340" width="{w}" height="{h}" style="{style}">
<circle cx="150" cy="190" r="140" fill="#1E3A5C"/>{arm_l}<rect x="90" y="190" width="120" height="150" rx="45" fill="{TEAL if not happy else AMBER}"/>{arm_r}
<g style="transform-origin:150px 190px;animation:{head_anim}">
<rect x="132" y="165" width="36" height="35" fill="{SKIN}"/><circle cx="150" cy="120" r="52" fill="{SKIN}"/>
<path d="M98 112A52 52 0 0 1 202 112Q150 82 98 112Z" fill="#2B1B14"/>
<g style="transform-origin:150px 124px;animation:blink 2s infinite"><circle cx="130" cy="124" r="7" fill="{NAVY}"/><circle cx="170" cy="124" r="7" fill="{NAVY}"/></g>
<path d="{mouth}" fill="none" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/>{extra}</g></svg>'''


def _robot(scale=1.0):
    return f'''<svg viewBox="0 0 300 340" width="{int(290 * scale)}" height="{int(330 * scale)}" style="animation:bob 1.1s ease-in-out infinite alternate">
<line x1="150" y1="44" x2="150" y2="76" stroke="{NAVY}" stroke-width="8"/><circle cx="150" cy="34" r="15" fill="{CORAL}" style="animation:blip .8s infinite"/>
<g style="transform-origin:88px 232px;animation:wave .6s ease-in-out infinite alternate"><rect x="36" y="222" width="56" height="28" rx="14" fill="{AMBER}" stroke="{NAVY}" stroke-width="6"/></g>
<g style="transform-origin:212px 232px;animation:wave .6s ease-in-out infinite alternate-reverse"><rect x="208" y="222" width="56" height="28" rx="14" fill="{AMBER}" stroke="{NAVY}" stroke-width="6"/></g>
<rect x="88" y="212" width="124" height="104" rx="30" fill="{TEAL}" stroke="{NAVY}" stroke-width="8"/>
<circle cx="150" cy="264" r="16" fill="{CREAM}" style="transform-origin:150px 264px;animation:beat .8s infinite"/>
<rect x="60" y="72" width="180" height="130" rx="44" fill="{AMBER}" stroke="{NAVY}" stroke-width="8"/>
<rect x="86" y="98" width="128" height="78" rx="28" fill="{NAVY}"/>
<g style="transform-origin:150px 132px;animation:blink 2.4s infinite"><circle cx="122" cy="130" r="11" fill="{TEAL}"/><circle cx="178" cy="130" r="11" fill="{TEAL}"/></g>
<path d="M130 154Q150 170 170 154" fill="none" stroke="{TEAL}" stroke-width="7" stroke-linecap="round"/></svg>'''


def _icon(kind):
    paths = {
        "bolt": '<path d="M58 14L28 56H48L42 86L74 42H54Z" fill="#fff"/>',
        "check": '<path d="M26 52L44 70L76 32" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>',
        "smile": '<circle cx="36" cy="38" r="6" fill="#fff"/><circle cx="64" cy="38" r="6" fill="#fff"/><path d="M28 56Q50 78 72 56" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>',
    }
    return f'<svg viewBox="0 0 100 100" width="96" height="96">{paths[kind]}</svg>'


def _star(x, y, size, delay, color=AMBER):
    return (f'<svg class="spark" viewBox="0 0 100 100" width="{size}" height="{size}" style="left:{x}px;top:{y}px;animation-delay:{delay}s">'
            f'<path d="M50 0L58 42L100 50L58 58L50 100L42 58L0 50L42 42Z" fill="{color}"/></svg>')


def _wipes():
    kinds = ["circle", "stripes", "slab", "circle", "stripes", "slab"]
    cols = [TEAL, AMBER, CORAL, TEAL, AMBER, CORAL]
    out = ""
    for s, k, c in zip(range(2, 8), kinds, cols):
        t = T[s][0]
        if k == "circle":
            out += f'<div class="wipe" style="background:{c};animation-delay:{t - 0.5:.2f}s"></div>'
        elif k == "slab":
            out += f'<div class="slab" style="background:{c};animation-delay:{t - 0.5:.2f}s"></div>'
        else:
            out += '<div class="stripes">' + "".join(
                f'<i style="background:{c};animation-delay:{t - 0.65 + j * 0.04:.2f}s"></i>' for j in range(6)) + "</div>"
    return out


def build_video_html(reel, cfg, esc):
    words = esc(reel["hook"]).split()
    hs = 150 if len(reel["hook"]) <= 26 else 126 if len(reel["hook"]) <= 42 else 108
    hook = "".join(f'<span class="w{" last" if i == len(words) - 1 else ""}" style="animation-delay:{0.35 + 0.28 * i:.2f}s">{w}</span>'
                   for i, w in enumerate(words))
    label = esc(str(reel.get("audience_label") or "WATCH THIS").upper())
    rnd = _rnd.Random(7)
    conf = "".join(
        f'<div class="conf" style="--x:{int(math.cos(a) * d)}px;--y:{int(math.sin(a) * d - 120)}px;--r:{rnd.randint(-540, 540)}deg;'
        f'width:{s}px;height:{s}px;background:{rnd.choice([AMBER, TEAL, CORAL, WHITE])};border-radius:{rnd.choice(["50%", "20%"])};'
        f'animation-delay:{float(D(6, 1.9)) + rnd.random() * 0.15:.2f}s"></div>'
        for a, d, s in [(rnd.random() * 6.283, rnd.randint(260, 620), rnd.randint(18, 40)) for _ in range(36)])
    bubbles = "".join(
        f'<div class="bub" style="left:{x}px;top:{y}px;animation-delay:{float(D(2, 0.9)) + i * 0.28:.2f}s,{float(D(2, 0.9)) + i * 0.28:.2f}s"><b></b><i>!</i></div>'
        for i, (x, y) in enumerate([(470, 90), (650, 20), (700, 210), (500, 290), (640, 400)]))
    notes = "".join(
        f'<div class="note" style="--rot:{rot}deg;background:{bg};animation-delay:{D(2, 2.3 + i * 0.5)}s">{esc(t)}</div>'
        for i, (t, rot, bg) in enumerate(zip(reel["problem_items"], (-2, 1.5, -1), (AMBER, CREAM, CORAL))))
    streams = lambda cls, d0: "".join(f'<div class="m {cls}" style="animation-delay:{d0 + j * 0.5:.1f}s"></div>' for j in range(3))
    steps = ""
    for i, (t, c, fr) in enumerate(zip(reel["steps"], (AMBER, TEAL, CORAL), ("-700px", "700px", "-700px"))):
        steps += (f'<div class="step" style="--from:{fr};animation-delay:{D(4, 0.9 + i * 1.1)}s"><div class="num" style="background:{c}">{i + 1}</div><span>{esc(t)}</span></div>')
        if i < 2:
            steps += f'<div class="vline" style="animation-delay:{D(4, 1.7 + i * 1.1)}s"></div>'
    rows = "".join(
        f'<div class="row r" style="animation-delay:{D(6, 0.5 + i * 0.6)}s"><div class="badge p" style="background:{c};animation-delay:{D(6, 0.6 + i * 0.6)}s">{_icon(k)}</div><span>{esc(t)}</span></div>'
        for i, (t, c, k) in enumerate(zip(reel["benefits"], (AMBER, TEAL, CORAL), ("bolt", "check", "smile"))))
    clock = (f'<svg viewBox="0 0 100 100" width="170" height="170" class="p" style="position:absolute;right:0;top:-50px;animation-delay:{D(2, 0.4)}s"><circle cx="50" cy="50" r="46" fill="#F5F7FA"/>'
             '<path d="M50 8V16M50 84V92M8 50H16M84 50H92" stroke="#0E1B2C" stroke-width="4" stroke-linecap="round"/>'
             '<g style="transform-origin:50px 50px;animation:spin 1.4s linear infinite"><line x1="50" y1="50" x2="50" y2="16" stroke="#FF6B5A" stroke-width="5" stroke-linecap="round"/></g>'
             '<g style="transform-origin:50px 50px;animation:spin 16s linear infinite"><line x1="50" y1="50" x2="50" y2="29" stroke="#0E1B2C" stroke-width="6" stroke-linecap="round"/></g></svg>')
    sparks = _star(60, 60, 70, D(5, 3.0)) + _star(760, 30, 90, D(5, 3.2), WHITE) + _star(820, 330, 60, D(5, 3.4)) + _star(380, 300, 50, D(5, 3.6), WHITE)
    handle = esc(cfg["brand"]["handle"])
    return f"""<html><head><meta charset="utf-8">{FONTS}<style>{CSS}{_scene_css()}</style></head><body><div id="v">
<div class="sc s1">{_shapes(NAVY, 1)}<div class="ring" style="animation-delay:.2s"></div><div class="ring" style="animation-delay:1.2s"></div>
<div class="cam" style="justify-content:center"><div class="chip r" style="animation-delay:.1s">{label}</div><div class="hook" style="--hs:{hs}px">{hook}</div></div></div>

<div class="sc s2">{_shapes(TEAL, 2)}<div class="cam"><div class="kick r" style="animation-delay:{D(2, 0.2)}s">THE PROBLEM</div>
<div class="ttl r" style="animation-delay:{D(2, 0.35)}s"><span class="hl" style="animation-delay:{D(2, 0.9)}s">{esc(reel["problem_title"])}</span></div>
<div class="art"><div class="p" style="animation-delay:{D(2, 0.5)}s">{_person()}</div>{bubbles}{clock}</div>
<div class="notes">{notes}<div class="stamp" style="animation-delay:{D(2, 4.7)}s">MANUAL</div></div></div></div>

<div class="sc s3">{_shapes(AMBER, 3)}<div class="cam" style="gap:16px"><div class="kick r" style="animation-delay:{D(3, 0.2)}s">THE FIX</div>
<div class="chp p" style="background:#0E1B2C;color:#F5F7FA;animation-delay:{D(3, 0.5)}s"><small>WHEN THIS HAPPENS</small>{esc(reel["flow_input"])}</div>
<div class="stream">{streams("", float(D(3, 1.1)))}</div>
<div class="p" style="animation-delay:{D(3, 0.8)}s">{_robot(0.95)}</div>
<div class="chp p" style="background:#FFB547;animation-delay:{D(3, 1.6)}s"><small>AI HANDLES IT</small>{esc(reel["flow_process"])}</div>
<div class="stream" style="height:100px">{streams("o", float(D(3, 1.8)))}</div>
<div class="chp p" style="background:#2EC4B6;animation-delay:{D(3, 2.2)}s"><small>YOU GET</small>{esc(reel["flow_output"])}</div></div></div>

<div class="sc s4">{_shapes(TEAL, 4)}<div class="cam" style="gap:10px"><div class="kick r" style="animation-delay:{D(4, 0.2)}s">HOW IT WORKS</div>
<div class="ttl r" style="animation-delay:{D(4, 0.35)}s;margin-bottom:26px"><span class="hl" style="animation-delay:{D(4, 0.8)}s">3 simple steps</span></div>
{steps}<div class="live" style="margin-top:44px;animation-delay:{D(4, 4.6)}s">AND IT RUNS 24/7</div></div></div>

<div class="sc s5">{_shapes(AMBER, 5)}<div class="cam" style="gap:26px"><div class="kick r" style="animation-delay:{D(5, 0.2)}s">BEFORE vs AFTER</div>
<div class="pan pb" style="animation-delay:{D(5, 0.5)}s"><span class="lab" style="background:#FF6B5A;color:#0E1B2C">BEFORE</span><div class="txt">{esc(reel["before"])}</div>
<div style="position:absolute;right:-30px;bottom:-60px;width:330px">{_person(False, 330, 374)}</div></div>
<div class="kick r" style="font-size:60px;animation-delay:{D(5, 1.9)}s">&#8595;</div>
<div class="pan pa" style="animation-delay:{D(5, 2.2)}s"><span class="lab" style="background:#0E1B2C;color:#2EC4B6">AFTER</span><div class="txt">{esc(reel["after"])}</div>
<div style="position:absolute;right:-20px;bottom:-60px">{_person(True, 270, 306)}</div><div style="position:absolute;right:240px;bottom:10px">{_robot(0.5)}</div></div>{sparks}</div></div>

<div class="sc s6">{_shapes(TEAL, 6)}<div class="cam" style="gap:70px;justify-content:center"><div class="kick r" style="animation-delay:{D(6, 0.2)}s">WHAT CHANGES</div>{rows}</div>{conf}</div>

<div class="sc s7">{_shapes(NAVY, 7)}<div class="cam" style="gap:46px;justify-content:center"><div class="hd r" style="animation-delay:{D(7, 0.2)}s">{esc(reel["closing"])}</div>
<div style="position:relative"><div class="btn" style="animation-delay:{D(7, 0.6)}s,{D(7, 2.55)}s,{D(7, 3.0)}s">DM AUTOMATE</div><div class="tap" style="animation-delay:{D(7, 2.6)}s"></div>
<svg class="cur" style="animation-delay:{D(7, 1.3)}s" width="110" height="110" viewBox="0 0 100 100"><path d="M18 8L18 78L38 62L52 92L66 86L52 56L78 56Z" fill="#fff" stroke="#0E1B2C" stroke-width="6" stroke-linejoin="round"/></svg></div>
<div class="hd r" style="animation-delay:{D(7, 0.9)}s;font-size:50px">Free 15-minute automation call</div>
<div class="hd r" style="animation-delay:{D(7, 1.2)}s;font-size:50px;opacity:.85">{handle}</div></div></div>
{_wipes()}<div class="bar"></div></div></body></html>"""


def render_video(reel, cfg, style, out_mp4, fps=24, seconds=DUR):
    """Animated 2D explainer Reel (characters, motion graphics). Frames come from seeking CSS animations; ffmpeg encodes."""
    page_html = build_video_html(reel, cfg, html.escape)
    tmp = tempfile.mkdtemp()
    try:
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(page_html, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate("window.__a=document.getAnimations(); window.__a.forEach(a=>a.pause())")
            for i in range(int(seconds * fps)):
                pg.evaluate("t=>window.__a.forEach(a=>{a.currentTime=t})", i * 1000.0 / fps)
                pg.screenshot(path=f"{tmp}/{i:04d}.jpg", type="jpeg", quality=90)
            br.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg",
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(fps),
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_mp4], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
