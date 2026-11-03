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

VID = Template("""<html><head><meta charset="utf-8">$fonts<style>
body{margin:0}
#v{position:relative;width:1080px;height:1920px;overflow:hidden;background:$bg;color:$fg;font-family:'Inter',Arial,sans-serif}
.blob{position:absolute;border-radius:50%;background:$ac;opacity:.10}
.b1{width:620px;height:620px;left:-200px;top:260px;animation:d1 7s ease-in-out infinite alternate}
.b2{width:420px;height:420px;right:-120px;top:900px;animation:d2 6s ease-in-out infinite alternate}
.b3{width:300px;height:300px;left:300px;top:1500px;animation:d1 9s ease-in-out infinite alternate-reverse}
@keyframes d1{to{transform:translate(120px,-160px) scale(1.2)}}
@keyframes d2{to{transform:translate(-160px,140px) scale(.85)}}
@keyframes spin{to{transform:rotate(360deg)}}
.gear{position:absolute;right:-300px;bottom:-300px;width:900px;height:900px;opacity:.10;animation:spin 14s linear infinite}
.bar{position:absolute;top:0;left:0;height:12px;width:100%;background:$ac;transform-origin:left;animation:prog 19.6s linear both}
@keyframes prog{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.sc{position:absolute;inset:0;box-sizing:border-box;padding:230px 90px 380px;display:flex;flex-direction:column;justify-content:center;gap:44px;opacity:0}
.s1{animation:sc 3.4s 0s both}
.s2{animation:sc 4.3s 3.1s both}
.s3{animation:sc 5.2s 7.1s both;align-items:center}
.s4{animation:sc 4.3s 12s both}
.s5{animation:sl 3.6s 16s both;align-items:center;text-align:center}
@keyframes sc{0%{opacity:0;transform:translateX(110px)}8%,92%{opacity:1;transform:none}100%{opacity:0;transform:translateX(-110px)}}
@keyframes sl{0%{opacity:0;transform:translateX(110px)}10%,100%{opacity:1;transform:none}}
.r{opacity:0;animation-name:rise;animation-duration:.7s;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1)}
@keyframes rise{from{opacity:0;transform:translateY(80px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes growY{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes draw{from{stroke-dashoffset:90}to{stroke-dashoffset:0}}
@keyframes flow{from{top:-24px}to{top:110px}}
@keyframes ripple{from{transform:scale(1);opacity:.8}to{transform:scale(1.7);opacity:0}}
.kick{font-size:36px;letter-spacing:6px;font-weight:500;opacity:.8}
.chip{align-self:flex-start;padding:14px 34px;border-radius:50px;background:$ac;color:$chip;font-size:38px;letter-spacing:5px;font-weight:500}
h1,.ttl{margin:0;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;line-height:1.03}
h1{font-size:${fs}px}
.ttl{font-size:90px}
.line{width:260px;height:18px;border-radius:9px;background:$ac;transform-origin:left;animation:grow .7s both}
.clock{position:relative;width:240px;height:240px}
.hand{position:absolute;inset:0;width:240px;height:240px}
.item{display:flex;align-items:center;gap:34px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:66px;line-height:1.1}
.txt{position:relative}
.strike{position:absolute;left:-10px;right:-10px;top:50%;height:10px;border-radius:5px;background:$ac;transform-origin:left;animation:grow .45s both}
.node{box-sizing:border-box;width:880px;border:7px solid $fg;border-radius:36px;padding:30px 40px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:62px;line-height:1.1;text-align:center;opacity:0;animation:pop .6s both}
.node small{display:block;font-family:'Inter',Arial,sans-serif;font-size:28px;letter-spacing:5px;font-weight:500;opacity:.75;margin-bottom:10px}
.core{background:$ac;color:$chip;border-color:$ac;display:flex;align-items:center;justify-content:center;gap:34px;padding:44px 40px}
.core small{margin-bottom:8px}
.conn{position:relative;width:10px;height:110px;background:rgba(128,128,128,.45);border-radius:5px;clip-path:inset(0 -24px);transform-origin:top;animation:growY .45s both}
.conn i{position:absolute;left:-5px;width:20px;height:20px;border-radius:50%;background:$ac;top:-24px;animation:flow 1.1s linear infinite both}
.ben{display:flex;align-items:center;gap:36px;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:70px;line-height:1.1}
.ck{stroke-dasharray:90;animation:draw .5s both}
.cta{position:relative;width:440px;height:440px;border-radius:50%;background:$ac;color:$chip;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;line-height:1;opacity:0;animation:pop .7s 16.8s both}
.rip{position:absolute;inset:0;border-radius:50%;border:8px solid $ac;opacity:0;animation:ripple 2s infinite both}
.hd{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:58px;line-height:1.12}
</style></head><body><div id="v">
<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>
<svg class="gear" viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="$fg" stroke-width="12" stroke-dasharray="6.6 6.6"/><circle cx="50" cy="50" r="32" fill="$fg"/><circle cx="50" cy="50" r="11" fill="$bg"/></svg>
<div class="bar"></div>

<div class="sc s1"><div class="r chip" style="animation-delay:.15s">$tag</div><h1 class="r" style="animation-delay:.4s">$hook</h1><div class="line" style="animation-delay:1.1s"></div></div>

<div class="sc s2"><div class="r kick" style="animation-delay:3.3s">THE PROBLEM</div>
<div class="r clock" style="animation-delay:3.4s"><svg viewBox="0 0 100 100" width="240" height="240"><circle cx="50" cy="50" r="46" fill="none" stroke="$fg" stroke-width="5"/><path d="M50 8V16M50 84V92M8 50H16M84 50H92" stroke="$fg" stroke-width="4" stroke-linecap="round"/></svg>
<svg class="hand" viewBox="0 0 100 100" style="animation:spin 1.6s linear infinite"><line x1="50" y1="50" x2="50" y2="16" stroke="$ac" stroke-width="5" stroke-linecap="round"/></svg>
<svg class="hand" viewBox="0 0 100 100" style="animation:spin 19s linear infinite"><line x1="50" y1="50" x2="50" y2="29" stroke="$fg" stroke-width="6" stroke-linecap="round"/></svg></div>
<div class="r ttl" style="animation-delay:3.6s">$ptitle</div>
<div class="r item" style="animation-delay:4.1s"><svg viewBox="0 0 100 100" width="76" height="76"><circle cx="50" cy="50" r="46" fill="$ac"/><path d="M33 33L67 67M67 33L33 67" stroke="$chip" stroke-width="10" stroke-linecap="round"/></svg><span class="txt">$p1<i class="strike" style="animation-delay:5.9s"></i></span></div>
<div class="r item" style="animation-delay:4.6s"><svg viewBox="0 0 100 100" width="76" height="76"><circle cx="50" cy="50" r="46" fill="$ac"/><path d="M33 33L67 67M67 33L33 67" stroke="$chip" stroke-width="10" stroke-linecap="round"/></svg><span class="txt">$p2<i class="strike" style="animation-delay:6.2s"></i></span></div>
<div class="r item" style="animation-delay:5.1s"><svg viewBox="0 0 100 100" width="76" height="76"><circle cx="50" cy="50" r="46" fill="$ac"/><path d="M33 33L67 67M67 33L33 67" stroke="$chip" stroke-width="10" stroke-linecap="round"/></svg><span class="txt">$p3<i class="strike" style="animation-delay:6.5s"></i></span></div></div>

<div class="sc s3"><div class="r kick" style="animation-delay:7.3s;align-self:flex-start">THE AUTOMATED WAY</div>
<div class="node" style="animation-delay:7.6s"><small>WHEN THIS HAPPENS</small>$fin</div>
<div class="conn" style="animation-delay:8.1s"><i style="animation-delay:8.5s"></i></div>
<div class="node core" style="animation-delay:8.4s"><svg viewBox="0 0 100 100" width="120" height="120" style="animation:spin 4s linear infinite;flex:none"><circle cx="50" cy="50" r="38" fill="none" stroke="$chip" stroke-width="12" stroke-dasharray="6.6 6.6"/><circle cx="50" cy="50" r="32" fill="$chip"/><circle cx="50" cy="50" r="11" fill="$ac"/></svg><div><small>AI HANDLES IT</small>$fproc</div></div>
<div class="conn" style="animation-delay:9s"><i style="animation-delay:9.4s"></i></div>
<div class="node" style="animation-delay:9.5s"><small>YOU GET</small>$fout</div></div>

<div class="sc s4"><div class="r kick" style="animation-delay:12.2s">WHAT CHANGES</div>
<div class="r ttl" style="animation-delay:12.3s">Your gain</div>
<div class="r ben" style="animation-delay:12.8s"><svg viewBox="0 0 100 100" width="96" height="96" style="flex:none"><circle cx="50" cy="50" r="46" fill="$ac"/><path class="ck" style="animation-delay:13s" d="M27 52L43 68L74 33" fill="none" stroke="$chip" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg><span>$b1</span></div>
<div class="r ben" style="animation-delay:13.4s"><svg viewBox="0 0 100 100" width="96" height="96" style="flex:none"><circle cx="50" cy="50" r="46" fill="$ac"/><path class="ck" style="animation-delay:13.6s" d="M27 52L43 68L74 33" fill="none" stroke="$chip" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg><span>$b2</span></div>
<div class="r ben" style="animation-delay:14s"><svg viewBox="0 0 100 100" width="96" height="96" style="flex:none"><circle cx="50" cy="50" r="46" fill="$ac"/><path class="ck" style="animation-delay:14.2s" d="M27 52L43 68L74 33" fill="none" stroke="$chip" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg><span>$b3</span></div></div>

<div class="sc s5"><div class="r hd" style="animation-delay:16.3s">$closing</div>
<div class="cta"><div class="rip" style="animation-delay:17.4s"></div><div class="rip" style="animation-delay:18.4s"></div><span style="font-size:110px">DM</span><span style="font-size:60px;margin-top:14px">AUTOMATE</span></div>
<div class="r hd" style="animation-delay:17.1s;font-size:46px;opacity:.9">Free 15-minute automation call</div>
<div class="r hd" style="animation-delay:17.4s;font-size:46px">$handle</div></div>
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


def render_video(reel, cfg, style, out_mp4, fps=24, seconds=19.6):
    """Animated, informative Reel. Frames come from seeking the CSS animations; ffmpeg encodes them."""
    bg, fg, ac, chip = STYLES[style]
    e = lambda s: html.escape(str(s))
    hook = reel["hook"]
    v = dict(fonts=FONTS, bg=bg, fg=fg, ac=ac, chip=chip, hook=e(hook), ptitle=e(reel["problem_title"]),
             p1=e(reel["problem_items"][0]), p2=e(reel["problem_items"][1]), p3=e(reel["problem_items"][2]),
             fin=e(reel["flow_input"]), fproc=e(reel["flow_process"]), fout=e(reel["flow_output"]),
             b1=e(reel["benefits"][0]), b2=e(reel["benefits"][1]), b3=e(reel["benefits"][2]),
             closing=e(reel["closing"]), handle=e(cfg["brand"]["handle"]), tag=e(str(reel.get("audience_label") or "WATCH THIS").upper()),
             fs=132 if len(hook) <= 30 else 112 if len(hook) <= 48 else 96)
    tmp = tempfile.mkdtemp()
    try:
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(VID.safe_substitute(v), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate("window.__a=document.getAnimations(); window.__a.forEach(a=>a.pause())")
            for i in range(int(seconds * fps)):
                pg.evaluate("t=>window.__a.forEach(a=>{a.currentTime=t})", i * 1000.0 / fps)
                pg.screenshot(path=f"{tmp}/{i:04d}.jpg", type="jpeg", quality=92)
            br.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg",
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(fps),
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_mp4], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
