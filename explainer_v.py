"""Alternative designs for the explainer scenes. Same colours and brand, different layouts and animations, so videos do not look alike."""
import math, textwrap

CSS = """
/* S1 v1: phone lock screen */
.pl{position:absolute;left:270px;top:140px;width:540px;height:1010px;border-radius:92px;background:#0B0E1A;box-shadow:0 60px 120px rgba(20,16,10,.45),inset 0 0 0 6px #262b3f;rotate:-4deg;opacity:0;animation:pop .7s cubic-bezier(.3,1.4,.5,1) both}
.pl .scr{position:absolute;inset:22px;border-radius:72px;background:linear-gradient(170deg,#2a3678,#0c1030 70%);overflow:hidden}
.pl .isl{position:absolute;left:50%;top:18px;width:150px;height:42px;margin-left:-75px;border-radius:21px;background:#000}
.lcard{position:absolute;left:26px;right:26px;height:132px;border-radius:30px;background:rgba(255,255,255,.17);display:flex;align-items:center;gap:22px;padding:0 26px;box-sizing:border-box;opacity:0;animation:lslide .6s cubic-bezier(.2,.9,.25,1) both}
.lcard .ic{width:64px;height:64px;border-radius:17px;flex:none}
.lcard .ls{flex:1;display:flex;flex-direction:column;gap:12px}
.lcard .ls i{display:block;height:15px;border-radius:8px;background:rgba(255,255,255,.5)}
.lcard .nw{position:absolute;right:24px;top:12px;font:500 20px 'DM Mono';color:rgba(255,255,255,.65)}
@keyframes lslide{from{opacity:0;transform:translateY(-140px) scale(.92)}to{opacity:1;transform:none}}
/* S4 v1: phone chat */
.pc{position:absolute;left:190px;top:290px;width:700px;height:1240px;border-radius:86px;background:#0B0E1A;box-shadow:0 56px 110px rgba(40,60,160,.3)}
.pc .sc2{position:absolute;inset:20px;border-radius:68px;background:#ECE9E1;overflow:hidden}
.pc .hd2{height:140px;background:#3558FF;color:#fff;display:flex;align-items:center;gap:20px;padding:34px 34px 0;box-sizing:border-box;font:700 34px Inter}
.cbub{position:absolute;padding:24px 30px;border-radius:30px;opacity:0;animation:pop .45s cubic-bezier(.3,1.5,.5,1) both}
.cbub.u{left:34px;background:#fff;border-bottom-left-radius:8px}
.cbub.a{right:34px;background:#D6E0FF;border-bottom-right-radius:8px}
.dots3{position:absolute;left:34px;display:flex;gap:10px;padding:26px 30px;border-radius:30px;background:#fff;opacity:0;animation:fade .3s both,fadeout2 .3s both}
.dots3 i{width:16px;height:16px;border-radius:50%;background:#9AA0B5;animation:blip 1s infinite}
.dots3 i:nth-child(2){animation-delay:.2s}.dots3 i:nth-child(3){animation-delay:.4s}
@keyframes blip{50%{opacity:.25}}
@keyframes fadeout2{to{opacity:0}}
/* S4 v2: kanban */
.kb{position:absolute;left:50px;right:50px;top:290px;height:1180px;border-radius:46px;background:#fff;box-shadow:0 46px 100px rgba(40,60,160,.24);overflow:hidden}
.kcol{position:absolute;top:140px;width:288px;height:960px;border-radius:30px;background:#F2F5FF}
.kcol h4{margin:0;padding:24px 0 0 24px;font:500 24px 'DM Mono';letter-spacing:.12em}
.kcard{position:absolute;width:250px;border-radius:24px;background:#fff;border:2px solid #E3E8FA;box-shadow:0 12px 28px rgba(40,60,160,.16);padding:20px;box-sizing:border-box}
.kcard i{display:block;height:14px;border-radius:7px;background:#DADFEF;margin-top:12px}
.kcard b{display:inline-block;margin-top:14px;padding:6px 14px;border-radius:14px;font:700 22px Inter;color:#fff;opacity:0;animation:pop .4s both}
@keyframes kmove{0%,36%{transform:translateX(0)}46%,76%{transform:translateX(296px)}86%,100%{transform:translateX(592px)}}
/* S5 v1: hub and spoke */
.hub{fill:none;stroke:#C9C0F5;stroke-width:6;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s ease-out both}
.hubdot{fill:none;stroke:#3558FF;stroke-width:16;stroke-linecap:round;stroke-dasharray:.001 .24;animation:dflow 1.5s linear infinite}
@keyframes dflow{from{stroke-dashoffset:0}to{stroke-dashoffset:-.241}}
.node{opacity:0;animation:pop .5s cubic-bezier(.3,1.5,.5,1) both}
.nlab{font:700 34px Inter;fill:#11131A;text-anchor:middle}
/* S6 v1: 24h ring */
.tick{stroke:rgba(255,255,255,.45);stroke-width:5;stroke-linecap:round}
/* S7 v1: before / after */
.ba{position:absolute;left:60px;right:60px;border-radius:44px;background:#fff;color:#11131A;box-shadow:0 30px 70px rgba(10,20,90,.35);overflow:hidden}
.reveal{clip-path:inset(0 0 100% 0);animation:revealdown .8s ease-out both}
@keyframes revealdown{to{clip-path:inset(0 0 0 0)}}
"""


def s1_phone(reel, esc, D, ev, H):
    cols = ["#F4A261", "#6C8CFF", "#7BD389", "#E8458B", "#FFD84D"]
    cards = ""
    for k in range(5):
        cards += (f'<div class="lcard" style="top:{150 + k * 150}px;animation-delay:{H["g"](D(0, 0.5 + 0.22 * k))}"><div class="ic" style="background:{cols[k]}"></div>'
                  f'<div class="ls"><i style="width:{80 - k * 6}%"></i><i style="width:{50 + k * 5}%"></i></div><span class="nw">now</span></div>')
        ev.append({"kind": "pop", "t": D(0, 0.55 + 0.22 * k)})
    ev.append({"kind": "hit", "t": D(0, 1.9), "g": 0.8})
    return f'''<div class="scn s1"><div class="pl" style="animation-delay:{H["g"](D(0, 0.1))}"><div class="scr"><div class="isl"></div>
<div style="position:absolute;left:0;right:0;top:80px;text-align:center;color:#fff;font:500 28px 'DM Mono';letter-spacing:.16em">NEW MESSAGES</div>{cards}</div></div>
<div class="stamp" style="left:560px;top:880px;animation-delay:{H["g"](D(0, 1.9))}">UNREAD</div>
<div class="xl rise" style="position:absolute;left:70px;top:1250px;width:940px;font-size:128px;animation-delay:{H["g"](D(0, 0.4))}">{H["acc"](reel["hook"], esc, "#FF6A3D", D(0, 1.0))}</div>
<div class="mono fade" style="position:absolute;left:74px;top:1720px;font-size:28px;color:#8A8478;animation-delay:{H["g"](D(0, 1.4))}">Locked screen &middot; nobody replied</div></div>'''


def s4_chat(reel, esc, D, ev, H):
    steps, cols3 = reel["steps"], ["#3558FF", "#E8458B", "#22C55E"]
    chip_t = [0.2, 2.5, 5.0]
    chips = "".join(f'<div class="chip2 pop" style="animation-delay:{H["g"](D(3, chip_t[i]))}"><b style="background:{cols3[i]}">0{i + 1}</b>{esc(steps[i]["label"])}</div>' for i in range(3))
    q = textwrap.wrap(reel["ui_q"], 20)[:3]
    a = textwrap.wrap(reel["ui_a"], 22)[:4]
    qh, qe = H["typed"](q, D(3, 0.9), 20, esc, 36, ev)
    ah, ae = H["typed"](a, D(3, 3.3), 22, esc, 36, ev)
    ev += [{"kind": "click", "t": D(3, 5.7)}, {"kind": "chime", "t": D(3, 5.85)}]
    return f'''<div class="scn s4"><div class="chips">{chips}</div>
<div class="pc pop" style="animation-delay:{H["g"](D(3, 0.1))}"><div class="sc2"><div class="hd2"><i style="width:64px;height:64px;border-radius:50%;background:#fff;display:block"></i>Customer</div>
<div class="cbub u" style="top:190px;animation-delay:{H["g"](D(3, 0.7))}">{qh}</div>
<div class="dots3" style="top:600px;animation-delay:{H["g"](D(3, 2.2))},{H["g"](D(3, 3.2))}"><i></i><i></i><i></i></div>
<div class="cbub a" style="top:560px;animation-delay:{H["g"](D(3, 3.2))}">{ah}</div>
<div style="position:absolute;left:30px;right:30px;bottom:30px;height:150px;border-radius:40px;background:#fff"></div>
<div class="btnk" style="left:150px;top:1010px;width:380px;background:#11131A;animation:fadeout .3s {H["g"](D(3, 5.7))} both">Approve reply</div>
<div class="btnk pop" style="left:150px;top:1010px;width:380px;background:#22C55E;animation-delay:{H["g"](D(3, 5.75))}">Sent &#10003;</div></div>
{H["cursor"](520, 1080, 200, 150, D(3, 4.7), "#fff")}<div class="tap2" style="left:360px;top:1062px;animation-delay:{H["g"](D(3, 5.65))}"></div></div></div>'''


def s4_kanban(reel, esc, D, ev, H):
    steps, cols3 = reel["steps"], ["#3558FF", "#E8458B", "#22C55E"]
    chip_t = [0.2, 2.5, 5.0]
    chips = "".join(f'<div class="chip2 pop" style="animation-delay:{H["g"](D(3, chip_t[i]))}"><b style="background:{cols3[i]}">0{i + 1}</b>{esc(steps[i]["label"])}</div>' for i in range(3))
    heads = [("NEW", "#3558FF", 24), ("AI REPLIED", "#E8458B", 320), ("BOOKED", "#22C55E", 616)]
    cols = "".join(f'<div class="kcol" style="left:{x}px"><h4 style="color:{c}">{t}</h4></div>' for t, c, x in heads)
    q = " ".join(reel["ui_q"].split()[:6])
    main = (f'<div class="kcard pop" style="left:{24 + 19}px;top:230px;animation:pop .5s both,kmove 7s linear both;animation-delay:{H["g"](D(3, 0.5))},{H["g"](D(3, 0.5))}">'
            f'<span class="mono" style="font-size:20px;color:#8A8FA3">CUSTOMER</span><div style="font:700 30px/1.2 Inter;margin-top:10px">{esc(q)}</div><i style="width:80%"></i><i style="width:55%"></i>'
            f'<b style="background:#E8458B;animation-delay:{H["g"](D(3, 2.9))}">AI replied</b><br><b style="background:#22C55E;animation-delay:{H["g"](D(3, 5.3))}">Booked &#10003;</b></div>')
    extras = ""
    for k, (x, y, w) in enumerate([(43, 560, 60), (43, 760, 75), (339, 760, 55)]):
        extras += (f'<div class="kcard pop" style="left:{x}px;top:{y}px;opacity:.9;animation-delay:{H["g"](D(3, 0.9 + 0.25 * k))}"><i style="margin-top:0;width:{w}%"></i><i style="width:{85 - k * 15}%"></i></div>')
        ev.append({"kind": "pop", "t": D(3, 0.95 + 0.25 * k)})
    ev += [{"kind": "whoosh", "t": D(3, 2.5), "pan": 0.2}, {"kind": "whoosh", "t": D(3, 5.0), "pan": 0.2}, {"kind": "chime", "t": D(3, 5.4)}]
    return f'''<div class="scn s4"><div class="chips">{chips}</div><div class="kb pop" style="animation-delay:{H["g"](D(3, 0.1))}">
<div class="hd" style="height:92px;border-bottom:2px solid #EEF0F6;display:flex;align-items:center;gap:12px;padding:0 34px"><i style="width:18px;height:18px;border-radius:50%;background:#FF5F57"></i><i style="width:18px;height:18px;border-radius:50%;background:#FEBC2E"></i><i style="width:18px;height:18px;border-radius:50%;background:#28C840"></i><span class="mono" style="margin-left:18px;color:#8A8FA3;font-size:26px">pipeline &middot; AI assistant on</span></div>
{cols}{extras}{main}</div></div>'''


def s5_hub(reel, esc, D, ev, H):
    dg = reel["diagram"]
    P = lambda d, t: f'<path class="hub" pathLength="1" d="{d}" style="animation-delay:{H["g"](D(4, t))}"/>'
    DT = lambda d, t: f'<path class="hubdot" pathLength="1" d="{d}" style="animation-delay:{H["g"](D(4, t))}"/>'
    paths = [("M450 190V330", 0.9), ("M370 600C320 680 230 720 160 790", 1.9), ("M450 630V790", 2.2), ("M530 600C580 680 670 720 740 790", 2.5)]
    lines = "".join(P(d, t) for d, t in paths) + "".join(DT(d, t + 0.7) for d, t in paths)
    icons = [
        '<path d="M-48 -34H48V44H-48Z M-48 -8H48 M-24 -52V-20 M24 -52V-20" fill="none" stroke="#11131A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
        '<path d="M-48 -44H48V44H-48Z M-48 -10H48 M-48 24H48 M-6 -44V44" fill="none" stroke="#11131A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
        '<path d="M-40 40V0M0 40V-24M40 40V-44" fill="none" stroke="#11131A" stroke-width="16" stroke-linecap="round"/>',
    ]
    fills, xs = ["#FFD3C2", "#CDEFD8", "#D6DEFF"], [155, 450, 745]
    outs = "".join(f'<g class="node" style="animation-delay:{H["g"](D(4, 3.0 + 0.4 * k))};transform-origin:{xs[k]}px 880px"><rect x="{xs[k] - 95}" y="790" width="190" height="190" rx="36" fill="{fills[k]}" stroke="#11131A" stroke-width="6"/>'
                   f'<g transform="translate({xs[k]} 876)">{icons[k]}</g><text class="nlab" x="{xs[k]}" y="1030">{esc(dg["outputs"][k])}</text></g>' for k in range(3))
    for k in range(3):
        ev.append({"kind": "pop", "t": D(4, 3.05 + 0.4 * k)})
    ev += [{"kind": "pop", "t": D(4, 0.4)}, {"kind": "pop", "t": D(4, 1.2)}]
    svg = f'''<svg viewBox="0 0 900 1090" style="position:absolute;inset:0;width:100%;height:100%">{lines}
<g class="node" style="animation-delay:{H["g"](D(4, 0.3))};transform-origin:450px 110px"><rect x="340" y="40" width="220" height="150" rx="34" fill="#E4E9FF" stroke="#11131A" stroke-width="6"/><path d="M380 90H520M380 125H470" stroke="#3558FF" stroke-width="10" stroke-linecap="round"/><text class="nlab" x="590" y="128" style="font-size:38px;text-anchor:start">{esc(dg["customer"])}</text></g>
<g class="node" style="animation-delay:{H["g"](D(4, 1.2))};transform-origin:450px 470px"><circle cx="450" cy="470" r="150" fill="#3558FF" stroke="#11131A" stroke-width="6"/><circle cx="405" cy="445" r="20" fill="#fff"/><circle cx="495" cy="445" r="20" fill="#fff"/><path d="M395 510Q450 565 505 510" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/><path d="M450 320V280" stroke="#11131A" stroke-width="8" stroke-linecap="round"/><circle cx="450" cy="268" r="16" fill="#FFD84D" stroke="#11131A" stroke-width="5"/><text class="nlab" x="450" y="668" style="font-size:36px">AI assistant</text></g>{outs}</svg>'''
    caps = reel["captions"]
    cap_t = [(0.9, 1.9), (2.8, 1.5), (4.3, 1.1)]
    caps_h = "".join(f'<div class="cap" style="--cd:{cd:.2f}s;animation-delay:{H["g"](D(4, a))}"><span>{H["cap"](caps[i], esc)}</span></div>' for i, (a, cd) in enumerate(cap_t))
    bars = "".join(f'<b style="--d:{0.35 + (k * 37 % 50) / 100:.2f}s;animation-delay:-{(k * 13 % 9) / 10:.1f}s;background:{"#E8458B" if k % 3 else "#3558FF"}"></b>' for k in range(38))
    return f'''<div class="scn s5"><div class="dcard pop" style="animation-delay:{H["g"](D(4, 0.1))}">{svg}</div>{caps_h}<div class="wave fade" style="animation-delay:{H["g"](D(4, 0.6))}">{bars}</div>
<div class="mono fade" style="position:absolute;left:74px;top:1570px;font-size:26px;color:#7C6FB3;animation-delay:{H["g"](D(4, 0.8))}">&#9679; AI voice &middot; follows every step</div></div>'''


def s6_ring(reel, esc, D, ev, H):
    bg_ = reel["big"]
    ticks = "".join(f'<line class="tick" x1="{350 + 310 * math.cos(math.radians(a)):.1f}" y1="{350 + 310 * math.sin(math.radians(a)):.1f}" x2="{350 + 336 * math.cos(math.radians(a)):.1f}" y2="{350 + 336 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 15))
    tags = [("Salam", "#E8458B", 90, 140, 0.9), ("Hello", "#3558FF", 780, 190, 1.2), ("\u0645\u0631\u062d\u0628\u0627", "#22C55E", 820, 640, 1.5), ("Hola", "#FF6A3D", 60, 700, 1.8)]
    tg = "".join(f'<div class="gtag" style="left:{x}px;top:{y}px;background:{c};animation-delay:{H["g"](D(5, a))},{H["g"](D(5, a))}">{s}</div>' for s, c, x, y, a in tags)
    for _, _, _, _, a in tags:
        ev.append({"kind": "pop", "t": D(5, a)})
    ev.append({"kind": "hit", "t": D(5, 0.3), "g": 0.9})
    fs = int(min(300, 760 / max(len(bg_["value"]) * 0.56, 1)))
    return f'''<div class="scn s6">{tg}<svg class="pop" style="position:absolute;left:190px;top:260px;animation-delay:{H["g"](D(5, 0.1))}" width="700" height="700" viewBox="0 0 700 700">{ticks}
<circle cx="350" cy="350" r="250" fill="none" stroke="rgba(255,255,255,.14)" stroke-width="22"/>
<circle cx="350" cy="350" r="250" fill="none" stroke="url(#rg)" stroke-width="22" stroke-linecap="round" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1;transform:rotate(-90deg);transform-origin:350px 350px;animation:draw 1.8s ease-out {H["g"](D(5, 0.3))} both"/>
<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7AA2FF"/><stop offset=".5" stop-color="#B28CFF"/><stop offset="1" stop-color="#FF8AD1"/></linearGradient></defs>
<g style="transform-origin:350px 350px;animation:spin 6s linear infinite"><circle cx="350" cy="100" r="30" fill="#FFD84D"/><circle cx="350" cy="600" r="30" fill="#E8ECFF"/><circle cx="364" cy="594" r="26" fill="#0b0f2b"/></g></svg>
<div class="big rise" style="position:absolute;left:190px;width:700px;top:470px;text-align:center;font-size:{fs}px;animation-delay:{H["g"](D(5, 0.5))}">{esc(bg_["value"])}</div>
<div class="xl rise" style="position:absolute;left:80px;right:80px;top:1130px;text-align:center;font-size:84px;animation-delay:{H["g"](D(5, 1.0))}">{esc(bg_["label"])}</div></div>'''


def s7_split(reel, esc, D, ev, H):
    cmp_ = reel["compare"]
    xs = "".join(f'<span class="pop" style="display:inline-flex;width:92px;height:92px;border-radius:22px;background:#FDE6E3;color:#E5392B;font:800 56px/92px Inter;justify-content:center;animation-delay:{H["g"](D(6, 0.5 + 0.1 * k))}">&#10005;</span>' for k in range(8))
    for k in range(8):
        ev.append({"kind": "tick", "t": D(6, 0.55 + 0.1 * k)})
    ev += [{"kind": "whoosh", "t": D(6, 1.9), "pan": 0.0}, {"kind": "chime", "t": D(6, 2.6)}]
    return f'''<div class="scn s7">
<div class="ba pop" style="top:170px;height:620px;padding:46px 54px;box-sizing:border-box;animation-delay:{H["g"](D(6, 0.1))}"><span class="lbl" style="background:#E5392B;display:block;width:max-content">BEFORE</span>
<div class="xl" style="font-size:96px;margin-top:30px">Hours of<br><span style="position:relative;display:inline-block">{esc(cmp_["before"])}<i class="strike" style="background:#E5392B;animation-delay:{H["g"](D(6, 1.4))}"></i></span></div>
<div style="position:absolute;left:54px;bottom:44px;display:flex;gap:14px;flex-wrap:wrap;width:900px">{xs}</div></div>
<div class="ba reveal" style="top:900px;height:640px;padding:46px 54px;box-sizing:border-box;animation-delay:{H["g"](D(6, 1.9))};background:#fff"><span class="lbl" style="background:#22C55E;display:block;width:max-content">AFTER</span>
<div class="xl" style="font-size:96px;margin-top:30px">Handled in<br><span style="color:#22C55E">seconds.</span></div>
<svg style="position:absolute;right:54px;bottom:50px" width="260" height="260" viewBox="0 0 260 260"><circle cx="130" cy="130" r="100" fill="none" stroke="#E3E6EF" stroke-width="22"/><circle cx="130" cy="130" r="100" fill="none" stroke="#22C55E" stroke-width="22" stroke-linecap="round" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1;transform:rotate(-90deg);transform-origin:130px 130px;animation:draw 1s ease-out {H["g"](D(6, 2.3))} both"/><path d="M85 135L118 168L178 98" fill="none" stroke="#22C55E" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1;animation:draw .5s ease-out {H["g"](D(6, 3.0))} both"/></svg></div></div>'''
