"""Kinetic-typography Reel: bold phrases, accent words in a contrasting font, minimal themes, UI mockups and icon animations."""
import base64, os, re, urllib.request

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONT_FILES = {  # key: (css family, style, weight range, path inside the google/fonts repo)
    "bricolage": ("Bricolage Grotesque", "normal", "200 800", "bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf"),
    "instrument-italic": ("Instrument Serif", "italic", "400", "instrumentserif/InstrumentSerif-Italic.ttf"),
    "syne": ("Syne", "normal", "400 800", "syne/Syne%5Bwght%5D.ttf"),
    "anton": ("Anton", "normal", "400", "anton/Anton-Regular.ttf"),
    "outfit": ("Outfit", "normal", "100 900", "outfit/Outfit%5Bwght%5D.ttf"),
    "inter": ("Inter", "normal", "100 900", "inter/Inter%5Bopsz,wght%5D.ttf"),
    "dmmono": ("DM Mono", "normal", "500", "dmmono/DMMono-Medium.ttf"),
    "caveat": ("Caveat", "normal", "400 700", "caveat/Caveat%5Bwght%5D.ttf"),
    "montserrat": ("Montserrat", "normal", "100 900", "montserrat/Montserrat%5Bwght%5D.ttf"),
    "poppins-xb": ("Poppins", "normal", "800", "poppins/Poppins-ExtraBold.ttf"),
    "archivo": ("Archivo Black", "normal", "400", "archivoblack/ArchivoBlack-Regular.ttf"),
    "unbounded": ("Unbounded", "normal", "200 900", "unbounded/Unbounded%5Bwght%5D.ttf"),
    "playfair-italic": ("Playfair Display", "italic", "400 900", "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf"),
}


def font_css(keys):
    """Embeds the fonts as base64 (downloaded once from the Google Fonts GitHub repo), so rendering never depends on a live font server."""
    os.makedirs(FONT_DIR, exist_ok=True)
    css = ""
    for k in keys:
        fam, style, wt, rel = FONT_FILES[k]
        path = os.path.join(FONT_DIR, k + ".ttf")
        if not os.path.exists(path):
            try:
                urllib.request.urlretrieve(_GF + rel, path)
            except Exception as e:
                print(f"Font {k} could not be downloaded ({e}); using a fallback font")
                continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        css += (f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wt};"
                f"src:url(data:font/ttf;base64,{b64}) format('truetype')}}")
    return css


BF = "'Inter',Arial,sans-serif"
THEMES = [  # the five typographic styles chosen by the owner: B neon, C sticker, E outline, F future, G luxe
    dict(name="neon", fx="glow", up=True, bs=104, cs=100, bg="#050505", bgs="#050505", fg="#F4F4F4", ac="#B6FF00", card="#1B1B1B", muted="#8E8E8E", pill=False, acfg="#050505",
         fonts=["anton", "inter"], hf="'Anton',Impact,sans-serif", hw=400, ht="uppercase", htr="0.01em", hlh="1.0", fsm=1.25,
         af="'Anton',Impact,sans-serif", ai="normal", aw=400, asc=1.0),
    dict(name="sticker", fx="sticker", up=False, bs=76, cs=76, bg="linear-gradient(150deg,#5b2bff,#1b0a6b)", bgs="#3a1fb0", fg="#FFFFFF", ac="#FF2E93", card="#3a22b8", muted="#B9A9FF", pill=True, acfg="#FFFFFF",
         fonts=["poppins-xb", "inter"], hf="'Poppins',Arial,sans-serif", hw=800, ht="none", htr="-0.01em", hlh="1.12", fsm=0.9,
         af="'Poppins',Arial,sans-serif", ai="normal", aw=800, asc=1.0),
    dict(name="outline", fx="outline", up=True, bs=70, cs=70, bg="#F6F1E7", bgs="#F6F1E7", fg="#111111", ac="#E5251B", card="#FFFFFF", muted="#8A8478", pill=False, acfg="#FFFFFF",
         fonts=["archivo", "inter"], hf="'Archivo Black','Arial Black',sans-serif", hw=400, ht="uppercase", htr="0", hlh="1.02", fsm=0.88,
         af="'Archivo Black','Arial Black',sans-serif", ai="normal", aw=400, asc=1.0),
    dict(name="future", fx="glow", up=True, bs=50, cs=52, bg="linear-gradient(180deg,#050816,#0a1633)", bgs="#07102a", fg="#FFFFFF", ac="#00F0FF", card="#0f2147", muted="#7F96BF", pill=False, acfg="#050816",
         fonts=["unbounded", "inter"], hf="'Unbounded',Arial,sans-serif", hw=800, ht="uppercase", htr="-0.01em", hlh="1.12", fsm=0.62,
         af="'Unbounded',Arial,sans-serif", ai="normal", aw=800, asc=1.0),
    dict(name="luxe", fx="gold", up=False, bs=80, cs=80, bg="#0B0B0B", bgs="#0B0B0B", fg="#FFFFFF", ac="#E4B94E", card="#161616", muted="#8D8677", pill=False, acfg="#0B0B0B",
         fonts=["montserrat", "playfair-italic", "inter"], hf="'Montserrat',Arial,sans-serif", hw=800, ht="none", htr="-0.03em", hlh="1.06", fsm=0.9,
         af="'Playfair Display',Georgia,serif", ai="italic", aw=900, asc=1.18),
    dict(name="signature", fx="signature", up=False, bs=84, cs=80, bg="#F3EFE6", bgs="#F3EFE6", fg="#11131A", ac="#3558FF", card="#FFFFFF", muted="#8A8FA3", pill=True, acfg="#FFFFFF",
         fonts=["inter"], hf="'Inter',Arial,sans-serif", hw=800, ht="none", htr="-0.045em", hlh="1.0", fsm=0.95,
         af="'Inter',Arial,sans-serif", ai="normal", aw=800, asc=1.0),
]
SIGNATURE = len(THEMES) - 1  # the one fixed brand theme used for every image post


DUR_BY_VISUAL = {"none": 2.1, "phone_chat": 4.8, "dashboard": 3.6, "hourglass": 3.4, "bulb": 3.2, "gears": 3.2,
                 "checklist": 3.8, "growth": 3.4, "bell": 3.4}
END_DUR = 4.6
OVERLAP = 0.15

CSS = """
body{margin:0}
#v{position:relative;width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--fg);font-family:var(--bf)}
.grid{position:absolute;inset:-90px;background-image:linear-gradient(rgba(128,128,128,.11) 2px,transparent 2px),linear-gradient(90deg,rgba(128,128,128,.11) 2px,transparent 2px);background-size:90px 90px;animation:grid 9s linear infinite}
@keyframes grid{to{transform:translate(90px,90px)}}
.glow{position:absolute;right:-300px;top:-300px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,var(--ac) 0%,transparent 68%);opacity:.28;animation:gl 6s ease-in-out infinite alternate}
@keyframes gl{to{transform:translate(-160px,200px) scale(1.25)}}
.seg{position:absolute;left:70px;right:70px;top:58px;display:flex;gap:8px;z-index:9}
.seg i{flex:1;height:7px;border-radius:4px;background:rgba(128,128,128,.28);overflow:hidden}
.seg b{display:block;height:100%;background:var(--ac);transform-origin:left;transform:scaleX(0);animation-name:growx;animation-timing-function:linear;animation-fill-mode:both}
.lock{position:absolute;left:70px;top:98px;display:flex;align-items:center;gap:16px;z-index:7;font-size:28px;font-weight:600;opacity:.78}
.mono{width:54px;height:54px;border-radius:50%;background:var(--ac);color:var(--acfg);display:flex;align-items:center;justify-content:center;font-family:var(--hf);font-weight:800;font-size:30px;text-transform:none}
.cnt{position:absolute;right:70px;top:108px;font-size:28px;font-weight:600;letter-spacing:3px;opacity:.6;z-index:7}
.ghost{position:absolute;right:-20px;top:150px;font-family:var(--hf);font-weight:800;font-size:720px;line-height:1;letter-spacing:-.06em;opacity:.045;color:var(--fg)}
.inner{position:absolute;inset:0;box-sizing:border-box;padding:190px 70px 230px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px}
@keyframes drift{from{transform:scale(1)}to{transform:scale(1.05)}}
.beat{position:absolute;inset:0;opacity:0}
@keyframes bshow{0%{opacity:0;transform:scale(.94)}9%{opacity:1;transform:none}88%{opacity:1;transform:none}100%{opacity:0;transform:scale(1.08)}}
@keyframes bstay{0%{opacity:0;transform:scale(.94)}9%,100%{opacity:1;transform:none}}
.txt{max-width:940px;text-align:center;font-family:var(--hf);font-weight:var(--hw);text-transform:var(--ht);letter-spacing:var(--htr);line-height:var(--hlh);font-size:var(--fs);text-wrap:balance}
.wd{display:inline-block;margin:0 .1em .03em;vertical-align:top}
.rise .wd{overflow:hidden;padding:.08em .14em .2em .06em;margin:-.08em -.04em -.17em -.04em}
.wi{display:inline-block;opacity:0}
.pop .wi{animation:wpop .6s cubic-bezier(.3,1.4,.5,1) both}
.rise .wi{animation:wrise .6s cubic-bezier(.2,.9,.3,1) both}
.drop .wi{animation:wdrop .55s cubic-bezier(.3,1.3,.5,1) both}
@keyframes wpop{from{opacity:0;transform:scale(.55) translateY(40px)}to{opacity:1;transform:none}}
@keyframes wrise{from{opacity:1;transform:translateY(110%)}to{opacity:1;transform:none}}
@keyframes wdrop{from{opacity:0;transform:translateY(-90px) rotate(-5deg)}to{opacity:1;transform:none}}
.h{color:var(--ac);font-family:var(--af);font-style:var(--ai);font-weight:var(--aw);font-size:calc(1em * var(--asc));line-height:1;letter-spacing:0;text-transform:none}
.forest-up .h{text-transform:uppercase}
.pillth .h{background:var(--ac);color:var(--acfg);padding:0 .22em;border-radius:.22em}
.vis{position:relative;width:900px;height:640px;flex:none;transform:scale(1.22);transform-origin:50% 0;margin-bottom:140px}
.swipe{position:absolute;top:0;bottom:0;left:0;width:1300px;background:var(--ac);transform:translateX(-2300px) skewX(-14deg);animation:sw .55s ease-in-out both;z-index:8}
@keyframes sw{0%{transform:translateX(-2300px) skewX(-14deg)}100%{transform:translateX(2300px) skewX(-14deg)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes bob{to{transform:translateY(-16px)}}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes rip{from{transform:scale(.4);opacity:.7}to{transform:scale(2.6);opacity:0}}
@keyframes blip{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes swing{0%{transform:rotate(-20deg)}100%{transform:rotate(20deg)}}
.pp{opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both}
.phone{position:absolute;left:250px;top:0;width:400px;height:640px;box-sizing:border-box;border:12px solid var(--fg);border-radius:60px;background:var(--card);overflow:hidden;opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both}
.phone::before{content:"";position:absolute;left:50%;top:12px;width:110px;height:26px;margin-left:-55px;border-radius:14px;background:var(--fg)}
.cb{position:absolute;max-width:290px;padding:16px 22px;border-radius:26px;font-size:27px;line-height:1.2;font-weight:500;opacity:0;animation:pop .45s cubic-bezier(.3,1.5,.5,1) both}
.cb.u{left:22px;background:rgba(128,128,128,.3);color:var(--fg);border-bottom-left-radius:6px}
.cb.a{right:22px;background:var(--ac);color:var(--acfg);border-bottom-right-radius:6px}
.card{position:absolute;border-radius:36px;background:var(--card);box-shadow:0 24px 60px rgba(0,0,0,.22);opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both,bob 2.2s ease-in-out infinite alternate}
.ln{stroke-dasharray:700;stroke-dashoffset:700;animation:draw 1.4s ease-out both}
.rowc{position:absolute;left:40px;right:40px;height:110px;display:flex;align-items:center;gap:30px}
.rowc i{flex:none;width:76px;height:76px;border-radius:20px;border:7px solid var(--fg);display:flex;align-items:center;justify-content:center;font-style:normal}
.rowc b{flex:1;height:26px;border-radius:13px;background:var(--muted);opacity:.55;transform-origin:left;animation:growx .6s both}
.ck{stroke-dasharray:70;stroke-dashoffset:70;animation:draw .45s both}
.chip{position:absolute;padding:16px 30px;border-radius:30px;background:var(--card);box-shadow:0 18px 40px rgba(0,0,0,.2);font-size:28px;font-weight:700;color:var(--fg);display:flex;align-items:center;gap:16px;opacity:0;animation:pop .45s cubic-bezier(.3,1.5,.5,1) both}
.chip em{width:18px;height:18px;border-radius:50%;background:var(--ac);display:block}
.cta{position:relative;padding:34px 90px;border-radius:80px;background:var(--ac);color:var(--acfg);font-family:var(--hf);font-size:84px;font-weight:var(--hw);letter-spacing:2px;text-transform:uppercase;opacity:0;animation:pop .6s cubic-bezier(.3,1.5,.5,1) both,press .35s both,glow2 1.6s infinite}
@keyframes press{0%,100%{transform:scale(1)}50%{transform:scale(.93)}}
@keyframes glow2{0%,100%{box-shadow:0 0 0 0 rgba(128,128,128,.35)}50%{box-shadow:0 0 0 34px rgba(128,128,128,0)}}
.cur{position:absolute;left:62%;top:30%;opacity:0;animation:cur 1.2s cubic-bezier(.4,0,.2,1) both}
@keyframes cur{0%{opacity:0;transform:translate(300px,420px)}15%{opacity:1}100%{opacity:1;transform:none}}
.tap{position:absolute;left:68%;top:52%;width:90px;height:90px;margin:-45px 0 0 -45px;border-radius:50%;border:8px solid var(--fg);opacity:0;animation:tp 1s ease-out both}
@keyframes tp{from{opacity:.9;transform:scale(.3)}to{opacity:0;transform:scale(3)}}
@keyframes shrink{to{transform:scaleY(0)}}
@keyframes fall{to{stroke-dashoffset:-36}}
.rise2{opacity:0;animation:r2 .7s cubic-bezier(.2,.8,.2,1) both}
@keyframes r2{from{opacity:0;transform:translateY(60px)}to{opacity:1;transform:none}}
"""


def _g(x):
    return f"{x:.2f}s"


def vis_phone(b):
    bub = [("u", "Hi, are you open tomorrow?", 90, 0.9), ("a", "Yes! I can book you right now.", 210, 1.7),
           ("u", "Great, 11 AM please.", 350, 2.5), ("a", "Booked for 11 AM. See you!", 450, 3.3)]
    h = "".join(f'<div class="cb {k}" style="top:{y}px;animation-delay:{_g(b + t)}">{s}</div>' for k, s, y, t in bub)
    return f'<div class="vis"><div class="phone" style="animation-delay:{_g(b)}">{h}</div></div>'


def vis_dashboard(b):
    return f'''<div class="vis">
<div class="card" style="left:20px;top:20px;width:620px;height:340px;animation-delay:{_g(b)},{_g(b)}"><svg viewBox="0 0 620 340" width="620" height="340">
<path d="M40 280H580M40 210H580M40 140H580M40 70H580" stroke="var(--muted)" stroke-width="2" opacity=".35"/>
<path class="ln" style="animation-delay:{_g(b + .5)}" d="M40 260C130 240 170 150 260 175S400 80 580 60" fill="none" stroke="var(--ac)" stroke-width="12" stroke-linecap="round"/></svg></div>
<div class="card" style="left:560px;top:230px;width:320px;height:320px;animation-delay:{_g(b + .35)},{_g(b + .35)}"><svg viewBox="0 0 320 320" width="320" height="320">
<circle cx="160" cy="160" r="95" fill="none" stroke="var(--muted)" stroke-width="30" opacity=".3"/>
<circle class="ln" style="animation-delay:{_g(b + .9)};stroke-dasharray:600;stroke-dashoffset:600;transform:rotate(-90deg);transform-origin:160px 160px" cx="160" cy="160" r="95" fill="none" stroke="var(--ac)" stroke-width="30" stroke-linecap="round"/></svg></div>
<div class="card" style="left:70px;top:390px;width:440px;height:230px;animation-delay:{_g(b + .6)},{_g(b + .6)}"><svg viewBox="0 0 440 230" width="440" height="230">
{"".join(f'<rect x="{40 + i * 78}" y="{190 - h}" width="48" height="{h}" rx="10" fill="var(--ac)" style="transform-origin:0 190px;animation:grow .6s {_g(b + 1.0 + i * .15)} both"/>' for i, h in enumerate((50, 90, 70, 130, 160)))}</svg></div></div>'''


def vis_hourglass(b):
    return f'''<div class="vis"><svg viewBox="0 0 300 420" width="460" height="644" style="position:absolute;left:220px;top:-4px;opacity:0;animation:pop .6s both;animation-delay:{_g(b)}">
<path d="M60 14H240M60 406H240" stroke="var(--fg)" stroke-width="14" stroke-linecap="round"/>
<path d="M70 22L70 60L150 205L70 360L70 398M230 22L230 60L150 205L230 360L230 398" fill="none" stroke="var(--fg)" stroke-width="8" stroke-linejoin="round"/>
<path d="M78 40H222L150 190Z" fill="var(--ac)" style="transform-origin:150px 190px;animation:shrink 2.6s linear {_g(b + .5)} both"/>
<line x1="150" y1="200" x2="150" y2="385" stroke="var(--ac)" stroke-width="5" stroke-dasharray="8 10" style="animation:fall .5s linear infinite"/>
<path d="M82 392H218L150 300Z" fill="var(--ac)" style="transform-origin:150px 392px;animation:grow 2.6s linear {_g(b + .5)} both"/></svg></div>'''


def vis_bulb(b):
    rays = "".join(f'<line x1="0" y1="-150" x2="0" y2="-205" stroke="var(--ac)" stroke-width="12" stroke-linecap="round" transform="rotate({a})" style="opacity:0;animation:pop .4s {_g(b + 1.0 + i * .06)} both"/>' for i, a in enumerate((-70, -35, 0, 35, 70)))
    return f'''<div class="vis"><svg viewBox="-200 -230 400 520" width="520" height="676" style="position:absolute;left:190px;top:-20px;opacity:0;animation:pop .6s both;animation-delay:{_g(b)}">
<circle r="140" cy="-20" fill="var(--ac)" opacity=".35" style="animation:blip 1.2s infinite"/>{rays}
<circle cx="0" cy="-20" r="100" fill="var(--card)" stroke="var(--fg)" stroke-width="10"/>
<path d="M-40 70L-40 130H40L40 70" fill="var(--card)" stroke="var(--fg)" stroke-width="10" stroke-linejoin="round"/>
<path d="M-34 150H34M-24 175H24" stroke="var(--fg)" stroke-width="12" stroke-linecap="round"/>
<path class="ln" style="animation-delay:{_g(b + .5)};stroke-dasharray:300;stroke-dashoffset:300" d="M-40 80L-30 -10L0 30L30 -10L40 80" fill="none" stroke="var(--ac)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'''


def _gear(x, y, r, color, direction, delay):
    ring = f'<circle r="{r}" fill="none" stroke="{color}" stroke-width="{r * 0.3:.0f}" stroke-dasharray="{(2 * 3.1416 * r) / 24:.1f} {(2 * 3.1416 * r) / 24:.1f}"/>'
    return (f'<g transform="translate({x} {y})"><g style="animation:spin {7 if r > 80 else 4}s linear infinite {direction}">{ring}'
            f'<circle r="{r * 0.82:.0f}" fill="{color}"/><circle r="{r * 0.3:.0f}" fill="var(--bg)"/></g></g>')


def vis_gears(b):
    return (f'<div class="vis"><svg viewBox="0 0 900 640" width="900" height="640" style="opacity:0;animation:pop .6s both;animation-delay:{_g(b)}">'
            f'{_gear(330, 300, 170, "var(--ac)", "", b)}{_gear(640, 190, 100, "var(--fg)", "reverse", b)}{_gear(600, 470, 80, "var(--muted)", "reverse", b)}</svg></div>')


def vis_checklist(b):
    rows = ""
    for i in range(3):
        t = b + 0.6 + i * 0.8
        rows += (f'<div class="rowc" style="top:{60 + i * 130}px"><i style="background:var(--card)"><svg viewBox="0 0 60 60" width="56" height="56"><path class="ck" style="animation-delay:{_g(t + .3)}" d="M10 32L25 46L50 14" fill="none" stroke="var(--ac)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg></i>'
                 f'<b style="animation-delay:{_g(t)}"></b></div>')
    return (f'<div class="vis"><div class="card" style="left:100px;top:40px;width:700px;height:500px;animation-delay:{_g(b)},{_g(b)}">{rows}'
            f'<div class="pp" style="position:absolute;right:40px;bottom:26px;padding:12px 34px;border-radius:30px;background:var(--ac);color:var(--acfg);font-size:34px;font-weight:700;animation-delay:{_g(b + 3.1)}">DONE</div></div></div>')


def vis_growth(b):
    bars = "".join(f'<rect x="{70 + i * 160}" y="{500 - h}" width="110" height="{h}" rx="16" fill="{"var(--ac)" if i == 4 else "var(--muted)"}" style="transform-origin:0 500px;animation:grow .6s {_g(b + .4 + i * .3)} both"/>' for i, h in enumerate((90, 150, 210, 300, 400)))
    return (f'<div class="vis"><svg viewBox="0 0 900 640" width="900" height="640">{bars}'
            f'<path class="ln" style="animation-delay:{_g(b + 1.0)};stroke-dasharray:1200;stroke-dashoffset:1200" d="M70 430L240 330L400 250L560 140L810 40" fill="none" stroke="var(--fg)" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M740 40L810 40L810 110" fill="none" stroke="var(--fg)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" style="opacity:0;animation:pop .3s {_g(b + 2.3)} both"/></svg></div>')


def vis_bell(b):
    rings = "".join(f'<div style="position:absolute;left:350px;top:170px;width:200px;height:200px;border-radius:50%;border:8px solid var(--ac);opacity:0;animation:rip 1.6s {_g(b + .5 + i * .8)} infinite both"></div>' for i in range(2))
    chips = "".join(f'<div class="chip" style="left:{x}px;top:{y}px;animation-delay:{_g(b + 0.9 + i * .4)}"><em></em>New message</div>' for i, (x, y) in enumerate(((20, 40), (600, 130), (60, 430), (590, 470))))
    return (f'<div class="vis">{rings}{chips}<svg viewBox="0 0 300 340" width="330" height="374" style="position:absolute;left:285px;top:130px;opacity:0;animation:pop .6s both;animation-delay:{_g(b)}">'
            f'<g style="transform-origin:150px 20px;animation:swing .35s ease-in-out infinite alternate"><path d="M150 30C90 30 70 90 70 150L70 210L40 250H260L230 210L230 150C230 90 210 30 150 30Z" fill="var(--ac)" stroke="var(--fg)" stroke-width="10" stroke-linejoin="round"/>'
            f'<path d="M120 270Q150 320 180 270" fill="none" stroke="var(--fg)" stroke-width="10" stroke-linecap="round"/></g>'
            f'<circle cx="228" cy="62" r="34" fill="#E5251B" class="pp" style="animation-delay:{_g(b + .7)}"/><text x="228" y="76" text-anchor="middle" font-size="42" font-weight="700" fill="#fff" style="font-family:var(--hf)">!</text></svg></div>')


VISUALS = {"phone_chat": vis_phone, "dashboard": vis_dashboard, "hourglass": vis_hourglass, "bulb": vis_bulb,
           "gears": vis_gears, "checklist": vis_checklist, "growth": vis_growth, "bell": vis_bell}




def _words(text, esc, base, anim):
    """Turns 'Still replying *by hand*?' into animated word spans; *..* marks accent words."""
    text = text.replace("'", "\u2019").replace("...", "\u2026")
    text = re.sub(r"\*([^*]+)\*([?!.,:;\u2026]+)", r"*\1\2*", text)
    out, k, hl = [], 0, False
    for tok in re.split(r"(\*)", text):
        if tok == "*":
            hl = not hl
            continue
        for w in tok.split():
            out.append(f'<span class="wd"><span class="wi{" h" if hl else ""}" style="animation-delay:{_g(base + 0.15 + k * 0.11)}">{esc(w)}</span></span>')
            k += 1
    return "".join(out)


def plain(text):
    return text.replace("*", "")


def build_kinetic_html(reel, cfg, esc, theme_idx=0):
    th = THEMES[theme_idx % len(THEMES)]
    beats = reel["beats"]
    n = len(beats)
    t, beats_html, swipes, segs = 0.0, "", "", ""
    anims = ["pop", "rise", "drop"]
    for i, bt in enumerate(beats):
        vis = bt.get("visual", "none")
        d = DUR_BY_VISUAL.get(vis, 2.1)
        text = bt["text"]
        ln = len(plain(text))
        base_fs = (100 if vis != "none" else 140) if ln <= 28 else (88 if vis != "none" else 116) if ln <= 44 else (76 if vis != "none" else 96)
        fs = int(base_fs * th["fsm"])
        v_html = VISUALS[vis](t + 0.55) if vis in VISUALS else ""
        beats_html += (f'<div class="beat {"pillth" if th["pill"] else ""}" style="animation:bshow {d:.2f}s {_g(t)} both">'
                       f'<div class="ghost">{i + 1:02d}</div><div class="cnt">{i + 1:02d} / {n:02d}</div>'
                       f'<div class="inner" style="animation:drift {d:.2f}s {_g(t)} linear both">'
                       f'<div class="txt {anims[i % 3]}" style="--fs:{fs}px">{_words(text, esc, t, anims[i % 3])}</div>{v_html}</div></div>')
        segs += f'<i><b style="animation-duration:{d - OVERLAP:.2f}s;animation-delay:{_g(t)}"></b></i>'
        if i and i % 3 == 0:
            swipes += f'<div class="swipe" style="animation-delay:{_g(t - 0.3)}"></div>'
        t += d - OVERLAP
    end = t
    cur_t = end + 1.5
    segs += f'<i><b style="animation-duration:{END_DUR:.2f}s;animation-delay:{_g(end)}"></b></i>'
    brand = esc(cfg["brand"]["name"])
    handle = esc(cfg["brand"]["handle"])
    end_html = f'''<div class="beat" style="animation:bstay {END_DUR:.2f}s {_g(end)} both"><div class="inner" style="gap:30px">
<svg viewBox="0 0 100 100" width="230" height="230" class="pp" style="animation-delay:{_g(end + .3)}"><g style="transform-origin:50px 50px;animation:spin 10s linear infinite"><circle cx="50" cy="50" r="40" fill="none" stroke="var(--ac)" stroke-width="12" stroke-dasharray="5.2 5.2"/></g><circle cx="50" cy="50" r="33" fill="var(--ac)"/><text x="50" y="66" text-anchor="middle" font-size="46" font-weight="800" fill="var(--acfg)" style="font-family:var(--hf)">S</text></svg>
<div class="rise2" style="font-family:var(--hf);font-weight:var(--hw);text-transform:var(--ht);letter-spacing:var(--htr);font-size:{th["bs"]}px;line-height:1;white-space:nowrap;animation-delay:{_g(end + .6)}">{brand}</div>
<div class="rise2" style="font-size:36px;font-weight:500;opacity:.75;animation-delay:{_g(end + .8)}">AI bots, automations &amp; custom web apps</div>
<div style="position:relative;margin-top:24px"><div class="cta" style="font-size:{th["cs"]}px;white-space:nowrap;animation-delay:{_g(end + 1.1)},{_g(cur_t + 1.1)},{_g(cur_t + 1.6)}">DM AUTOMATE</div><div class="tap" style="animation-delay:{_g(cur_t + 1.15)}"></div>
<svg class="cur" style="animation-delay:{_g(cur_t)}" width="110" height="110" viewBox="0 0 100 100"><path d="M18 8L18 78L38 62L52 92L66 86L52 56L78 56Z" fill="#fff" stroke="#111" stroke-width="6" stroke-linejoin="round"/></svg></div>
<div class="rise2" style="font-size:44px;font-weight:700;animation-delay:{_g(end + 1.5)}">Free 15-minute automation call</div>
<div class="rise2" style="font-size:38px;font-weight:500;opacity:.8;animation-delay:{_g(end + 1.7)}">{handle}</div></div></div>'''
    total = end + END_DUR
    page = (f'<html><head><meta charset="utf-8"><style>{font_css(th["fonts"])}{CSS}</style></head><body>'
            f'<div id="v" class="{th["name"]}-up" style="--bg:{th["bg"]};--fg:{th["fg"]};--ac:{th["ac"]};--card:{th["card"]};--muted:{th["muted"]};--acfg:{th["acfg"]};'
            f'--hf:{th["hf"]};--hw:{th["hw"]};--ht:{th["ht"]};--htr:{th["htr"]};--hlh:{th["hlh"]};--af:{th["af"]};--ai:{th["ai"]};--aw:{th["aw"]};--asc:{th["asc"]};--bf:{BF}">'
            f'<div class="grid"></div><div class="glow"></div>{beats_html}{end_html}{swipes}'
            f'<div class="seg">{segs}</div><div class="lock"><span class="mono">S</span><span>{handle}</span></div></div></body></html>')
    return page, total
