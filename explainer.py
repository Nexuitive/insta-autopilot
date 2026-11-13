"""Motion-graphics explainer Reel (one fixed brand theme): hook, contrast, brand reveal, UI demo, hand-drawn diagram, big number, before/after, CTA."""
import html, io, math, os, random, shutil, subprocess, tempfile, textwrap
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import audio, kinetic, logo as logomod, voice

FPS = 24
MIN_DUR = [3.0, 3.2, 4.2, 7.0, 5.4, 3.4, 3.4, 4.8]
TRANS = ["inUp", "inLeft", "inZoom", "inUp", "inLeft", "inZoom", "inUp", "inLeft"]

CSS = """
body{margin:0}
#v{position:relative;width:1080px;height:1920px;overflow:hidden;background:#F3EFE6;font-family:'Inter',Arial,sans-serif;color:#11131A}
.scn{position:absolute;inset:0;overflow:hidden}
@keyframes inUp{from{transform:translateY(100%)}to{transform:none}}
@keyframes inLeft{from{transform:translateX(100%)}to{transform:none}}
@keyframes inZoom{from{transform:scale(.72);opacity:0}to{transform:none;opacity:1}}
.rise{opacity:0;animation:rise .7s cubic-bezier(.2,.8,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(60px)}to{opacity:1;transform:none}}
.pop{opacity:0;animation:pop .55s cubic-bezier(.3,1.5,.5,1) both}
@keyframes pop{from{opacity:0;transform:scale(.5)}to{opacity:1;transform:none}}
.fade{opacity:0;animation:fade .5s ease both}
@keyframes fade{to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes bob{to{transform:translateY(-14px)}}
.xl{font-weight:800;letter-spacing:-.045em;line-height:1}
.acc{display:inline-block;padding:.02em .22em .1em;border-radius:.2em;color:#fff;box-shadow:0 8px 0 rgba(17,19,26,.14)}
.mono{font-family:'DM Mono',monospace}
/* logo */
"""+logomod.CSS+"""
/* S1 hook */
.s1{background:linear-gradient(160deg,#E8E3D7,#D2CCBC)}
.ncard{position:absolute;width:540px;height:150px;border-radius:34px;background:#fff;box-shadow:0 30px 70px rgba(30,25,10,.22),0 4px 10px rgba(0,0,0,.06);display:flex;align-items:center;gap:26px;padding:0 34px;box-sizing:border-box;opacity:0;animation:drop .75s cubic-bezier(.2,.9,.25,1) both}
.ncard .av{width:78px;height:78px;border-radius:50%;flex:none}
.ncard .ls{flex:1;display:flex;flex-direction:column;gap:14px}
.ncard .ls i{display:block;height:18px;border-radius:9px;background:#DADAE2}
.ncard .bd{position:absolute;right:26px;top:-18px;min-width:46px;height:46px;border-radius:23px;background:#FF3B30;color:#fff;font:800 26px/46px Inter;text-align:center;padding:0 10px;box-sizing:border-box}
@keyframes drop{0%{opacity:0;transform:translateY(-560px) rotate(var(--r0))}62%{opacity:1;transform:translateY(16px) rotate(var(--r))}100%{opacity:1;transform:rotate(var(--r))}}
.stamp{position:absolute;border:9px solid #E5392B;color:#E5392B;border-radius:16px;font:800 58px/1 Inter;letter-spacing:.14em;padding:14px 26px;opacity:0;animation:slam .5s both;rotate:-9deg;background:rgba(255,255,255,.4)}
@keyframes slam{0%{opacity:0;transform:scale(2.6)}70%{opacity:1;transform:scale(.94)}100%{opacity:1;transform:scale(1)}}
/* S2 contrast */
.s2{background:#0B1026}
.pat{position:absolute;inset:-200px;background-image:radial-gradient(rgba(130,150,255,.2) 2.5px,transparent 2.5px);background-size:48px 48px;transform:rotate(-9deg)}
.vcard{position:absolute;left:80px;right:80px;top:250px;height:900px;border-radius:50px;background:#fff;box-shadow:0 50px 110px rgba(0,0,0,.55);overflow:hidden}
.bub2{position:absolute;max-width:600px;padding:26px 34px;border-radius:34px;font-size:38px;line-height:1.25;font-weight:600;opacity:0;animation:pop .5s cubic-bezier(.3,1.5,.5,1) both}
.bub2.u{left:50px;background:#EEF0F5;border-bottom-left-radius:8px}
.bub2.a{right:50px;background:#3558FF;color:#fff;border-bottom-right-radius:8px}
.playb{position:absolute;left:50%;top:50%;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;background:rgba(17,19,26,.82);display:flex;align-items:center;justify-content:center;opacity:0;animation:pop .5s both,fadeout .4s both}
@keyframes fadeout{to{opacity:0;transform:scale(1.4)}}
.pbar{position:absolute;left:50px;right:50px;bottom:46px;height:12px;border-radius:6px;background:#E3E6EF;overflow:hidden}
.pbar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#3558FF,#E8458B);transform-origin:left;animation:growx 2.6s linear both}
/* S3 brand */
.s3{background:radial-gradient(circle at 50% 46%,#E3D9FF,#F3EFE6 62%)}
/* S4 UI demo */
.s4{background-color:#EAF0FF;background-image:linear-gradient(#DCE4FF 2px,transparent 2px),linear-gradient(90deg,#DCE4FF 2px,transparent 2px);background-size:64px 64px}
.chips{position:absolute;left:40px;right:40px;top:140px;display:flex;gap:14px;justify-content:center}
.chip2{padding:16px 24px;border-radius:32px;font:700 29px Inter;display:flex;gap:12px;align-items:center;background:#fff;box-shadow:0 12px 30px rgba(40,60,160,.16);white-space:nowrap}
.chip2 b{border-radius:10px;padding:3px 11px;font:500 23px 'DM Mono';color:#fff}
.win{position:absolute;left:60px;right:60px;top:290px;height:1140px;border-radius:46px;background:#fff;box-shadow:0 46px 100px rgba(40,60,160,.24);overflow:hidden}
.win .hd{height:92px;border-bottom:2px solid #EEF0F6;display:flex;align-items:center;gap:12px;padding:0 34px}
.win .hd i{width:18px;height:18px;border-radius:50%}
.lbl{display:inline-block;padding:8px 20px;border-radius:20px;font:500 24px 'DM Mono';letter-spacing:.12em;color:#fff}
.tl{display:block;white-space:nowrap;clip-path:inset(0 100% 0 0);animation:typeclip var(--dur) steps(var(--n),end) both;font-weight:600;line-height:1.28}
@keyframes typeclip{to{clip-path:inset(0 0 0 0)}}
.hlb{position:absolute;height:50px;border-radius:8px;background:#FFD84D;transform-origin:left;animation:growx .6s ease-out both;mix-blend-mode:multiply}
.btnk{position:absolute;height:104px;border-radius:52px;font:700 40px/104px Inter;text-align:center;color:#fff}
.cur2{position:absolute;opacity:0;animation:curmove 1.1s cubic-bezier(.4,0,.2,1) both;z-index:6}
@keyframes curmove{0%{opacity:0;transform:translate(var(--x0),var(--y0))}15%{opacity:1}100%{opacity:1;transform:none}}
.tap2{position:absolute;width:100px;height:100px;margin:-50px 0 0 -50px;border-radius:50%;border:8px solid #3558FF;opacity:0;animation:tap2 .9s ease-out both;z-index:5}
@keyframes tap2{from{opacity:.9;transform:scale(.3)}to{opacity:0;transform:scale(2.6)}}
.sticker{position:absolute;border:7px solid #22C55E;color:#169B47;background:#fff;border-radius:16px;font:800 44px/1 Inter;letter-spacing:.06em;padding:12px 24px;rotate:-7deg;opacity:0;animation:slam .5s both;z-index:4}
/* S5 diagram */
.s5{background-color:#EFE9FF;background-image:radial-gradient(#D9CFFF 2.5px,transparent 2.5px);background-size:44px 44px}
.dcard{position:absolute;left:50px;right:50px;top:150px;height:1090px;border-radius:50px;background:#fff;box-shadow:0 46px 100px rgba(90,60,200,.22);overflow:hidden}
.dp{fill:none;stroke:#1d1f2b;stroke-width:6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw var(--dd,.8s) ease-in-out both}
.df{opacity:0;animation:fade .6s both}
.hand{font-family:'Caveat',cursive;font-weight:700;font-size:52px;fill:#1d1f2b;opacity:0;animation:fade .5s both}
.cap{position:absolute;left:70px;right:70px;top:1290px;display:flex;justify-content:center;opacity:0;animation:capk var(--cd) both}
@keyframes capk{0%{opacity:0;transform:translateY(24px)}9%{opacity:1;transform:none}91%{opacity:1}100%{opacity:0}}
.cap span{background:#2A2E3B;color:#fff;border-radius:20px;padding:20px 38px;font:600 44px/1.1 Inter;box-shadow:0 14px 30px rgba(0,0,0,.25)}
.cap em{font-style:normal;color:#FFD84D}
.wave{position:absolute;left:70px;right:70px;top:1440px;height:100px;display:flex;align-items:center;gap:7px}
.wave b{flex:1;height:100%;border-radius:5px;transform-origin:center;animation:wv var(--d) ease-in-out infinite alternate}
@keyframes wv{from{transform:scaleY(.18)}to{transform:scaleY(1)}}
/* S6 big number */
.s6{background:radial-gradient(circle at 18% 14%,#1B2C8C,transparent 52%),radial-gradient(circle at 88% 82%,#7A1C72,transparent 52%),#070A20;color:#fff}
.gw{position:absolute;left:50%;top:430px;width:0;height:0;perspective:1300px}
.globe{position:absolute;width:0;height:0;transform-style:preserve-3d;animation:spin3 20s linear infinite}
@keyframes spin3{from{transform:rotateX(-14deg) rotateY(0)}to{transform:rotateX(-14deg) rotateY(360deg)}}
.globe i{position:absolute;width:10px;height:10px;margin:-5px;border-radius:50%;background:#9DB4FF}
.gtag{position:absolute;padding:14px 28px;border-radius:30px;font:700 38px Inter;color:#fff;box-shadow:0 12px 30px rgba(0,0,0,.35);opacity:0;animation:pop .55s cubic-bezier(.3,1.5,.5,1) both,bob 2.4s ease-in-out infinite alternate}
.big{font-weight:800;letter-spacing:-.06em;line-height:.9;background:linear-gradient(90deg,#7AA2FF,#B28CFF,#FF8AD1);-webkit-background-clip:text;background-clip:text;color:transparent}
/* S7 compare */
.s7{background:#3558FF;color:#fff}
.cal{position:absolute;left:90px;top:520px;display:grid;grid-template-columns:repeat(7,112px);gap:14px}
.cal u{display:block;height:112px;border-radius:18px;background:rgba(255,255,255,.18);position:relative;text-decoration:none}
.cal u b{position:absolute;inset:10px;border-radius:14px;background:#fff;display:flex;align-items:center;justify-content:center;opacity:0;animation:pop .35s both;color:#E5392B;font:800 70px/1 Inter}
.strike{position:absolute;left:-12px;right:-12px;top:52%;height:14px;border-radius:7px;background:#FFD84D;transform-origin:left;animation:growx .5s both}
/* S8 CTA */
.s8{background:radial-gradient(circle at 50% 22%,#E3D9FF,#F3EFE6 64%)}
.conf{position:absolute;opacity:0;animation:burst 1.6s ease-out both}
@keyframes burst{0%{opacity:1;transform:translate(0,0) scale(.3)}100%{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}}
.ctab{position:absolute;left:50%;margin-left:-250px;width:500px;height:130px;border-radius:65px;background:#401B9D;color:#fff;font:800 54px/130px Inter;text-align:center;letter-spacing:.02em;box-shadow:0 18px 0 rgba(64,27,157,.28);opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both,press .35s both}
@keyframes press{0%,100%{transform:scale(1)}50%{transform:scale(.93)}}
"""


def _g(x):
    return f"{x:.2f}s"


def _acc(text, esc, pill_color="#FF6A3D", pill_delay=0.0, size=None):
    """'Nobody answers *2 AM* messages.' -> words, accent words inside a coloured pill."""
    out, hl, buf = [], False, []
    parts = text.replace("*", "\u0000*\u0000").split("\u0000")
    for p in parts:
        if p == "*":
            hl = not hl
            continue
        if not p.strip():
            continue
        if hl:
            out.append(f'<span class="acc pop" style="background:{pill_color};animation-delay:{_g(pill_delay)}">{esc(p.strip())}</span>')
        else:
            out.append(esc(p.strip()))
    return " ".join(out)


def _typed(lines, t, cps, esc, size, events=None):
    """Typewriter: each line is revealed in steps. Returns (html, end_time)."""
    h = ""
    for ln in lines:
        n = max(len(ln), 1)
        dur = n / cps
        h += f'<span class="tl" style="--dur:{dur:.2f}s;--n:{n};animation-delay:{_g(t)};font-size:{size}px">{esc(ln)}</span>'
        if events is not None:
            for k in range(0, n, 2):
                events.append({"kind": "tick", "t": t + k / cps})
        t += dur + 0.12
    return h, t


def _cursor(x, y, x0, y0, t, color="#fff"):
    return (f'<svg class="cur2" style="left:{x}px;top:{y}px;--x0:{x0}px;--y0:{y0}px;animation-delay:{_g(t)}" width="96" height="96" viewBox="0 0 100 100">'
            f'<path d="M18 8L18 78L38 62L52 92L66 86L52 56L78 56Z" fill="{color}" stroke="#11131A" stroke-width="6" stroke-linejoin="round"/></svg>')


def build(reel, cfg, vo_durs=None):
    esc = lambda s: html.escape(str(s).replace("'", "\u2019"))
    brand = esc(cfg["brand"]["name"])
    handle = esc(cfg["brand"]["handle"])
    durs = [max(m, (vo_durs[i] + 0.7) if vo_durs else m) for i, m in enumerate(MIN_DUR)]
    st, t = [], 0.0
    for d in durs:
        st.append(t)
        t += d
    total = t
    ev = []
    D = lambda i, s: st[i] + s
    scenes = []

    # ---------------- S1 hook ----------------
    rnd = random.Random(4)
    cards = ""
    spots = [(470, 80, -6), (60, 300, 5), (520, 330, 3), (150, 560, -4), (470, 590, 6), (40, 860, -3), (500, 880, 5), (250, 150, -2)]
    cols = ["#F4A261", "#6C8CFF", "#7BD389", "#E8458B", "#FFD84D", "#8E7CFF", "#FF8A65", "#4DC3C3"]
    for k, (x, y, r) in enumerate(spots):
        cards += (f'<div class="ncard" style="left:{x}px;top:{y}px;--r:{r}deg;--r0:{r * 3}deg;animation-delay:{_g(D(0, 0.15 + 0.14 * k))}">'
                  f'<div class="av" style="background:{cols[k]}"></div><div class="ls"><i style="width:{70 - rnd.randint(0, 25)}%"></i><i style="width:{45 + rnd.randint(0, 25)}%"></i></div>'
                  f'<div class="bd">{[1, 3, 2, 5, 1, 4, 2, 7][k]}</div></div>')
        ev.append({"kind": "pop", "t": D(0, 0.35 + 0.14 * k)})
    ev.append({"kind": "hit", "t": D(0, 1.75), "g": 0.8})
    scenes.append(f'''<div class="scn s1">{cards}
<div class="stamp" style="left:560px;top:150px;animation-delay:{_g(D(0, 1.7))}">UNREAD</div>
<div class="xl rise" style="position:absolute;left:70px;top:1130px;width:940px;font-size:136px;animation-delay:{_g(D(0, 0.3))}">{_acc(reel["hook"], esc, "#FF6A3D", D(0, 0.9))}</div>
<div class="mono fade" style="position:absolute;left:74px;top:1640px;font-size:28px;color:#8A8478;animation-delay:{_g(D(0, 1.3))}">WhatsApp_Inbox &middot; replied 0 times</div></div>''')

    # ---------------- S2 contrast ----------------
    bubs = [("u", "Hi, are you open tomorrow?", 90, 0.6), ("a", "Yes! I can book you in right now.", 290, 1.4), ("u", "Perfect, 11 AM please.", 520, 2.2), ("a", "Booked. See you at 11!", 700, 2.9)]
    bh = "".join(f'<div class="bub2 {k}" style="top:{y}px;animation-delay:{_g(D(1, tt))}">{esc(s)}</div>' for k, s, y, tt in bubs)
    for _, _, _, tt in bubs:
        ev.append({"kind": "pop", "t": D(1, tt)})
    scenes.append(f'''<div class="scn s2"><div class="pat"></div>
<div class="vcard pop" style="animation-delay:{_g(D(1, 0.1))}">{bh}<div class="playb" style="animation-delay:{_g(D(1, 0.2))},{_g(D(1, 0.8))}"><svg width="60" height="60" viewBox="0 0 60 60"><path d="M16 8L52 30L16 52Z" fill="#fff"/></svg></div><div class="pbar"><i style="animation-delay:{_g(D(1, 0.6))}"></i></div></div>
<div class="xl rise" style="position:absolute;left:80px;top:1290px;width:920px;font-size:118px;color:#fff;animation-delay:{_g(D(1, 0.5))}">{_acc(reel["contrast"], esc, "linear-gradient(90deg,#3558FF,#8E5BFF)", D(1, 1.1))}</div></div>''')

    # ---------------- S3 brand ----------------
    lp = logomod.find_logo()
    parts = logomod.split(lp) if lp else None
    if parts:
        lg, lev = logomod.animate_html(parts, D(2, 0.1), 1.0)
        ev += lev
        scenes.append(f'''<div class="scn s3"><div class="lgbox" style="left:40px;top:440px;transform:scale(2)">{lg}</div></div>''')
    else:
        letters = "".join(f'<span class="pop" style="display:inline-block;animation-delay:{_g(D(2, 0.55 + 0.045 * k))}">{"&nbsp;" if c == " " else esc(c)}</span>' for k, c in enumerate(cfg["brand"]["name"]))
        ev.append({"kind": "sting", "t": D(2, 0.2)})
        scenes.append(f'''<div class="scn s3"><div style="position:absolute;left:50%;top:640px;margin-left:-130px" class="pop"><svg viewBox="0 0 100 100" width="260" height="260" style="animation:none"><g style="transform-origin:50px 50px;animation:spin 8s linear infinite"><circle cx="50" cy="50" r="40" fill="none" stroke="#3558FF" stroke-width="12" stroke-dasharray="5.2 5.2"/></g><circle cx="50" cy="50" r="33" fill="#3558FF"/><text x="50" y="66" text-anchor="middle" font-size="46" font-weight="800" fill="#fff" font-family="Inter">S</text></svg></div>
<div class="xl" style="position:absolute;left:0;right:0;top:960px;text-align:center;font-size:118px;white-space:nowrap">{letters}</div></div>''')

    # ---------------- S4 UI demo ----------------
    steps = reel["steps"]
    cols3 = ["#3558FF", "#E8458B", "#22C55E"]
    chip_t = [0.2, 2.5, 5.0]
    chips = "".join(f'<div class="chip2 pop" style="animation-delay:{_g(D(3, chip_t[i]))}"><b style="background:{cols3[i]}">0{i + 1}</b>{esc(steps[i]["label"])}</div>' for i in range(3))
    qlines = textwrap.wrap(reel["ui_q"], 26)[:2]
    alines = textwrap.wrap(reel["ui_a"], 29)[:3]
    qh, qend = _typed(qlines, D(3, 0.8), 22, esc, 50, ev)
    hl = "".join(f'<i class="hlb" style="left:{-10}px;top:{4 + k * 64}px;width:{min(len(l), 26) * 27 + 14}px;animation-delay:{_g(D(3, 2.0 + 0.25 * k))}"></i>' for k, l in enumerate(qlines))
    ah, aend = _typed(alines, D(3, 2.9), 24, esc, 46, ev)
    ev += [{"kind": "click", "t": D(3, 5.35)}, {"kind": "chime", "t": D(3, 5.5)}]
    scenes.append(f'''<div class="scn s4"><div class="chips">{chips}</div>
<div class="win pop" style="animation-delay:{_g(D(3, 0.1))}"><div class="hd"><i style="background:#FF5F57"></i><i style="background:#FEBC2E"></i><i style="background:#28C840"></i><span class="mono" style="margin-left:18px;color:#8A8FA3;font-size:26px">inbox &middot; AI assistant on</span></div>
<div style="position:absolute;left:50px;top:140px;right:50px"><span class="lbl fade" style="background:#3558FF;animation-delay:{_g(D(3, 0.5))}">CUSTOMER</span>
<div style="position:relative;margin-top:26px;height:130px"><div style="position:absolute;left:0;top:0">{hl}<div style="position:relative">{qh}</div></div></div></div>
<svg class="fade" style="position:absolute;left:470px;top:400px;animation-delay:{_g(D(3, 2.4))}" width="140" height="110" viewBox="0 0 140 110"><path d="M70 6V84M40 58L70 90L100 58" fill="none" stroke="#E8458B" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div style="position:absolute;left:50px;top:540px;right:50px"><span class="lbl fade" style="background:#E8458B;animation-delay:{_g(D(3, 2.6))}">AI REPLY &middot; YOUR RULES</span><div style="margin-top:28px">{ah}</div></div>
<div class="btnk" style="left:270px;top:930px;width:460px;background:#11131A;animation:fadeout .3s {_g(D(3, 5.4))} both">Approve reply</div>
<div class="btnk pop" style="left:270px;top:930px;width:460px;background:#22C55E;animation-delay:{_g(D(3, 5.45))}">Sent &#10003;</div>
{_cursor(660, 990, 220, 160, D(3, 4.2), "#fff")}<div class="tap2" style="left:500px;top:982px;animation-delay:{_g(D(3, 5.3))}"></div>
<div class="sticker" style="right:40px;top:790px;animation-delay:{_g(D(3, 5.7))}">YOUR RULES</div></div></div>''')

    # ---------------- S5 diagram ----------------
    dg = reel["diagram"]
    P = lambda d, t, extra="": f'<path class="dp" pathLength="1" d="{d}" style="animation-delay:{_g(D(4, t))};{extra}"/>'
    R = lambda x, y, w, h, r, t: f'<rect class="dp" pathLength="1" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" style="animation-delay:{_g(D(4, t))}"/>'
    svg = f'''<svg viewBox="0 0 900 960" style="position:absolute;inset:0;width:100%;height:100%"><defs><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter></defs>
<g filter="url(#rough)">
<rect class="df" x="70" y="90" width="170" height="300" rx="34" fill="#6C8CFF" fill-opacity=".22" style="animation-delay:{_g(D(4, 1.0))}"/>{R(70, 90, 170, 300, 34, 0.3)}{P("M108 170H202M108 215H170M108 265H202", 0.9)}<text class="hand" x="52" y="450" style="animation-delay:{_g(D(4, 1.1))}">{esc(dg["customer"])}</text>
{P("M255 240C320 240 335 300 405 300M388 278L408 300L382 318", 1.2)}
<rect class="df" x="430" y="210" width="210" height="170" rx="44" fill="#FFD84D" fill-opacity=".55" style="animation-delay:{_g(D(4, 1.9))}"/>{R(430, 210, 210, 170, 44, 1.5)}{R(455, 392, 160, 130, 36, 1.8)}
<circle class="dp" pathLength="1" cx="500" cy="285" r="15" style="animation-delay:{_g(D(4, 2.0))}"/><circle class="dp" pathLength="1" cx="570" cy="285" r="15" style="animation-delay:{_g(D(4, 2.1))}"/>{P("M495 335Q535 362 575 335", 2.1)}{P("M535 210V150", 2.2)}<circle class="dp" pathLength="1" cx="535" cy="136" r="16" style="animation-delay:{_g(D(4, 2.3))}"/>
<text class="hand" x="655" y="462" style="animation-delay:{_g(D(4, 2.2))}">AI assistant</text>
{P("M490 530C400 600 270 625 185 690M470 520L478 543M185 690L178 666M185 690L208 678", 2.5)}{P("M535 535V690M512 664L535 696L558 664", 2.7)}{P("M580 530C670 600 700 625 745 690M745 690L720 676M745 690L742 664", 2.9)}
<rect class="df" x="60" y="700" width="210" height="190" rx="20" fill="#FF6A3D" fill-opacity=".3" style="animation-delay:{_g(D(4, 3.4))}"/>{R(60, 700, 210, 190, 20, 3.0)}{P("M60 755H270M105 688V724M225 688V724M100 800H130M160 800H190M100 845H130M160 845H230", 3.2)}
<rect class="df" x="340" y="700" width="210" height="190" rx="20" fill="#22C55E" fill-opacity=".3" style="animation-delay:{_g(D(4, 3.8))}"/>{R(340, 700, 210, 190, 20, 3.4)}{P("M340 760H550M340 825H550M412 700V890", 3.6)}
<rect class="df" x="620" y="700" width="210" height="190" rx="20" fill="#3558FF" fill-opacity=".25" style="animation-delay:{_g(D(4, 4.2))}"/>{R(620, 700, 210, 190, 20, 3.8)}{P("M655 860V800M715 860V760M775 860V730", 4.0, "stroke-width:18")}
<text class="hand" x="95" y="945" style="animation-delay:{_g(D(4, 3.4))}">{esc(dg["outputs"][0])}</text><text class="hand" x="365" y="945" style="animation-delay:{_g(D(4, 3.8))}">{esc(dg["outputs"][1])}</text><text class="hand" x="660" y="945" style="animation-delay:{_g(D(4, 4.2))}">{esc(dg["outputs"][2])}</text></g></svg>'''
    for tt in (1.0, 1.9, 3.4, 3.8, 4.2):
        ev.append({"kind": "pop", "t": D(4, tt)})
    caps = reel["captions"]
    cap_t = [(0.9, 1.9), (2.8, 1.5), (4.3, 1.1)]
    caps_h = "".join(f'<div class="cap" style="--cd:{cd:.2f}s;animation-delay:{_g(D(4, a))}"><span>{_acc_caption(caps[i], esc)}</span></div>' for i, (a, cd) in enumerate(cap_t))
    bars = "".join(f'<b style="--d:{0.35 + (k * 37 % 50) / 100:.2f}s;animation-delay:-{(k * 13 % 9) / 10:.1f}s;background:{"#E8458B" if k % 3 else "#3558FF"}"></b>' for k in range(38))
    scenes.append(f'''<div class="scn s5"><div class="dcard pop" style="animation-delay:{_g(D(4, 0.1))}">{svg}</div>{caps_h}
<div class="wave fade" style="animation-delay:{_g(D(4, 0.6))}">{bars}</div>
<div class="mono fade" style="position:absolute;left:74px;top:1570px;font-size:26px;color:#7C6FB3;animation-delay:{_g(D(4, 0.8))}">&#9679; AI voice &middot; follows every step</div></div>''')

    # ---------------- S6 big number ----------------
    bg_ = reel["big"]
    tags = [("Salam", "#E8458B", 90, 230, 0.7), ("Hello", "#3558FF", 700, 180, 1.0), ("\u0645\u0631\u062d\u0628\u0627", "#22C55E", 760, 520, 1.3), ("Hola", "#FF6A3D", 70, 600, 1.6), ("Bonjour", "#8E5BFF", 380, 720, 1.9)]
    tg = "".join(f'<div class="gtag" style="left:{x}px;top:{y}px;background:{c};animation-delay:{_g(D(5, a))},{_g(D(5, a))}">{s}</div>' for s, c, x, y, a in tags)
    for _, _, _, _, a in tags:
        ev.append({"kind": "pop", "t": D(5, a)})
    ev.append({"kind": "hit", "t": D(5, 0.3), "g": 0.9})
    scenes.append(f'''<div class="scn s6"><div class="gw"><div class="globe"></div></div>{tg}
<div class="big rise" style="position:absolute;left:0;right:0;top:880px;text-align:center;font-size:{int(min(330, 1000 / max(len(bg_["value"]) * 0.56, 1)))}px;animation-delay:{_g(D(5, 0.3))}">{esc(bg_["value"])}</div>
<div class="xl rise" style="position:absolute;left:80px;right:80px;top:1260px;text-align:center;font-size:84px;animation-delay:{_g(D(5, 0.8))}">{esc(bg_["label"])}</div></div>
<script>(function(){{var g=document.querySelector('.globe'),n=240,R=250,ga=Math.PI*(3-Math.sqrt(5));for(var i=0;i<n;i++){{var y=1-(i/(n-1))*2,r=Math.sqrt(1-y*y),th=ga*i,x=Math.cos(th)*r,z=Math.sin(th)*r,d=document.createElement('i');d.style.transform='translate3d('+(x*R)+'px,'+(y*R)+'px,'+(z*R)+'px)';g.appendChild(d)}}}})();</script>''')

    # ---------------- S7 compare ----------------
    cmp_ = reel["compare"]
    cells = ""
    xs = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]
    for k in range(21):
        has = k < 13
        cells += f'<u>{f"<b style=animation-delay:{_g(D(6, 0.5 + 0.07 * k))}>&#10005;</b>" if has else ""}</u>'
        if has:
            ev.append({"kind": "tick", "t": D(6, 0.55 + 0.07 * k)})
    scenes.append(f'''<div class="scn s7"><div class="xl rise" style="position:absolute;left:90px;top:150px;font-size:150px;animation-delay:{_g(D(6, 0.1))}">Hours</div>
<div class="xl rise" style="position:absolute;left:90px;top:320px;font-size:84px;width:900px;animation-delay:{_g(D(6, 0.25))}"><span style="position:relative;display:inline-block">of {esc(cmp_["before"])}<i class="strike" style="animation-delay:{_g(D(6, 1.5))}"></i></span></div>
<div class="cal">{cells}</div>
<svg class="pop" style="position:absolute;left:690px;top:1150px;animation-delay:{_g(D(6, 1.7))}" width="300" height="300" viewBox="0 0 380 380"><circle cx="190" cy="190" r="150" fill="none" stroke="rgba(255,255,255,.25)" stroke-width="26"/><circle cx="190" cy="190" r="150" fill="none" stroke="#FFD84D" stroke-width="26" stroke-linecap="round" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1;transform:rotate(-90deg);transform-origin:190px 190px;animation:draw 1.4s ease-out {_g(D(6, 1.9))} both"/><rect x="170" y="10" width="40" height="22" rx="8" fill="#fff"/><line x1="190" y1="190" x2="190" y2="80" stroke="#fff" stroke-width="12" stroke-linecap="round" style="transform-origin:190px 190px;animation:spin 1.6s linear {_g(D(6, 1.9))} 1 both"/></svg>
<div class="xl rise" style="position:absolute;left:90px;top:1180px;font-size:76px;width:520px;animation-delay:{_g(D(6, 1.8))}">handled in</div>
<div class="xl rise" style="position:absolute;left:90px;top:1290px;font-size:128px;animation-delay:{_g(D(6, 2.1))}">seconds<span style="color:#FFD84D">.</span></div></div>''')
    ev.append({"kind": "chime", "t": D(6, 3.2)})

    # ---------------- S8 CTA ----------------
    conf = ""
    crnd = random.Random(9)
    ccols = ["#3558FF", "#FF6A3D", "#22C55E", "#E8458B", "#FFD84D"]
    for k in range(44):
        a, dd = crnd.random() * 6.283, crnd.randint(300, 760)
        conf += (f'<div class="conf" style="left:540px;top:1300px;--x:{int(math.cos(a) * dd)}px;--y:{int(math.sin(a) * dd - 260)}px;--r:{crnd.randint(-540, 540)}deg;'
                 f'width:{crnd.randint(14, 30)}px;height:{crnd.randint(8, 16)}px;background:{crnd.choice(ccols)};border-radius:3px;animation-delay:{_g(D(7, 1.9) + crnd.random() * 0.2)}"></div>')
    cta = reel["cta"]
    ev += [{"kind": "riser", "t": max(D(7, 0) - 0.9, 0), "dur": 0.9}, {"kind": "click", "t": D(7, 2.25)}, {"kind": "chime", "t": D(7, 2.35)}]
    if parts:
        lg8, lev8 = logomod.animate_html(parts, D(7, 0.05), 0.42, ["gear", "mono", "swoosh", "pixels", "syed", "auto"])
        ev += lev8
        top_block = f'<div class="lgbox" style="left:253px;top:63px;transform:scale(1.15)">{lg8}</div>'
    else:
        top_block = (f'<svg class="pop" style="position:absolute;left:50%;top:170px;margin-left:-70px;animation-delay:{_g(D(7, 0.1))}" viewBox="0 0 100 100" width="140" height="140"><g style="transform-origin:50px 50px;animation:spin 8s linear infinite"><circle cx="50" cy="50" r="40" fill="none" stroke="#3558FF" stroke-width="12" stroke-dasharray="5.2 5.2"/></g><circle cx="50" cy="50" r="33" fill="#3558FF"/><text x="50" y="66" text-anchor="middle" font-size="46" font-weight="800" fill="#fff" font-family="Inter">S</text></svg>'
                     f'<div class="xl rise" style="position:absolute;left:0;right:0;top:340px;text-align:center;font-size:80px;animation-delay:{_g(D(7, 0.2))}">{brand}</div>')
    scenes.append(f'''<div class="scn s8">{top_block}
<div class="xl rise" style="position:absolute;left:70px;right:70px;top:540px;font-size:96px;color:#9A9787;animation-delay:{_g(D(7, 0.5))}"><span style="position:relative;display:inline-block">Stop {esc(cta["stop"])}<i class="strike" style="background:#FF6A3D;height:12px;animation-delay:{_g(D(7, 1.0))}"></i></span></div>
<div class="xl rise" style="position:absolute;left:70px;right:70px;top:860px;font-size:104px;animation-delay:{_g(D(7, 1.3))}">Start <span class="acc pop" style="background:linear-gradient(90deg,#401B9D,#7B3FE4);animation-delay:{_g(D(7, 1.6))}">{esc(cta["start"])}</span></div>
{conf}<div class="ctab" style="top:1400px;animation-delay:{_g(D(7, 1.9))},{_g(D(7, 2.3))}">DM AUTOMATE</div>
{_cursor(640, 1470, 260, 300, D(7, 1.0), "#fff")}<div class="tap2" style="left:600px;top:1465px;animation-delay:{_g(D(7, 2.25))}"></div>
<div class="mono fade" style="position:absolute;left:0;right:0;top:1590px;text-align:center;font-size:32px;color:#6B7190;letter-spacing:.14em;animation-delay:{_g(D(7, 2.6))}">FREE 15-MINUTE CALL &middot; {handle}</div></div>''')

    wraps = []
    for i, s in enumerate(scenes):
        a = "" if i == 0 else f' style="z-index:{i};animation:{TRANS[i]} .6s cubic-bezier(.2,.8,.2,1) {_g(st[i] - 0.05)} backwards"'
        wraps.append(s.replace('<div class="scn', f'<div{a} class="scn', 1) if i else s)
    for i in range(1, len(st)):
        ev.append({"kind": "whoosh", "t": st[i], "pan": 0.4 if i % 2 else -0.4})
    page = (f'<html><head><meta charset="utf-8"><style>{kinetic.font_css(["inter", "dmmono", "caveat"])}{CSS}</style></head><body><div id="v">{"".join(wraps)}</div></body></html>')
    windows = [(st[i] - 0.1, st[i] + 0.65) for i in range(1, len(st))]
    return page, total, ev, windows, st


def _acc_caption(text, esc):
    out, hl = [], False
    for p in text.replace("*", "\u0000*\u0000").split("\u0000"):
        if p == "*":
            hl = not hl
        elif p:
            out.append(f"<em>{esc(p)}</em>" if hl else esc(p))
    return "".join(out)


def render_explainer(reel, cfg, out_mp4, fps=FPS):
    """Returns the voice engine used. Frames come from seeking CSS animations; motion blur on scene changes; ffmpeg adds music + voice."""
    lines = list(reel["vo"])
    clips, engine = voice.synthesize(lines, cfg)
    vo_durs = [len(c) / voice.SR for c in clips] if clips else None
    page, total, events, windows, st = build(reel, cfg, vo_durs)
    tmp = tempfile.mkdtemp()
    try:
        vlist = [(st[i] + 0.35, clips[i]) for i in range(len(clips))] if clips else None
        wav = audio.make_soundtrack(events, total, os.path.join(tmp, "s.wav"), seed=7, vo_clips=vlist)
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(page, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate("window.__a=document.getAnimations(); window.__a.forEach(a=>a.pause())")
            shutter = 0.5 / fps
            for i in range(int(total * fps)):
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
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg", "-i", wav,
                        "-vf", "eq=contrast=1.03:saturation=1.05,format=yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-r", str(fps),
                        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return engine
