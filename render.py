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
.gear{position:absolute;right:-300px;bottom:-300px;width:900px;height:900px;opacity:.13;animation:spin 14s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.bar{position:absolute;top:0;left:0;height:12px;width:100%;background:$ac;transform-origin:left;animation:prog 9.6s linear both}
@keyframes prog{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.sc{position:absolute;inset:0;box-sizing:border-box;padding:240px 90px 360px;display:flex;flex-direction:column;justify-content:center;gap:52px;opacity:0}
.s1{animation:sc 3.6s 0s both}
.s2{animation:sc 3.3s 3.5s both}
.s3{animation:sl 3.1s 6.5s both;align-items:center;text-align:center}
@keyframes sc{0%{opacity:0}8%,88%{opacity:1}100%{opacity:0}}
@keyframes sl{0%{opacity:0}12%,100%{opacity:1}}
.r{opacity:0;animation-name:rise;animation-duration:.8s;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1)}
@keyframes rise{from{opacity:0;transform:translateY(90px)}to{opacity:1;transform:none}}
.chip{align-self:flex-start;padding:14px 34px;border-radius:50px;background:$ac;color:$chip;font-size:38px;letter-spacing:5px;font-weight:500}
h1{margin:0;font-family:'Space Grotesk',Arial,sans-serif;font-size:${fs}px;line-height:1.02;font-weight:700}
.sub{font-family:'Space Grotesk',Arial,sans-serif;font-size:76px;line-height:1.15;font-weight:700}
.barx{width:240px;height:18px;border-radius:9px;background:$ac}
.cta{position:relative;width:440px;height:440px;border-radius:50%;background:$ac;color:$chip;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;line-height:1;opacity:0;animation:pop .7s 6.8s both}
@keyframes pop{from{opacity:0;transform:scale(.5)}to{opacity:1;transform:none}}
.rip{position:absolute;inset:0;border-radius:50%;border:8px solid $ac;opacity:0;animation:ripple 2s infinite both}
@keyframes ripple{from{transform:scale(1);opacity:.8}to{transform:scale(1.7);opacity:0}}
.hd{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:56px}
</style></head><body><div id="v">
<svg class="gear" viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="$fg" stroke-width="12" stroke-dasharray="6.6 6.6"/><circle cx="50" cy="50" r="32" fill="$fg"/><circle cx="50" cy="50" r="11" fill="$bg"/></svg>
<div class="bar"></div>
<div class="sc s1"><div class="r chip" style="animation-delay:.15s">$tag</div><h1 class="r" style="animation-delay:.45s">$head</h1></div>
<div class="sc s2"><div class="r barx" style="animation-delay:3.7s"></div><div class="r sub" style="animation-delay:4.0s">$sub</div></div>
<div class="sc s3"><div class="cta"><div class="rip" style="animation-delay:7.4s"></div><div class="rip" style="animation-delay:8.4s"></div><span style="font-size:110px">DM</span><span style="font-size:60px;margin-top:14px">AUTOMATE</span></div>
<div class="r hd" style="animation-delay:7.2s">Free 15-minute automation call</div>
<div class="r hd" style="animation-delay:7.5s;opacity:.85">$handle</div></div>
</div></body></html>""")


def _vals(post, cfg, style):
    bg, fg, ac, chip = STYLES[style]
    head = post["headline"]
    return dict(fonts=FONTS, bg=bg, fg=fg, ac=ac, chip=chip, head=html.escape(head),
                sub=html.escape(post["subline"]), handle=html.escape(cfg["brand"]["handle"]),
                tag=html.escape(post.get("post_type", "TIP").replace("_", " ").upper()), head_len=len(head))


def render(post, cfg, style, out_path):
    v = _vals(post, cfg, style)
    v["fs"] = 124 if v["head_len"] <= 24 else 104 if v["head_len"] <= 42 else 86
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1080})
        pg.set_content(IMG.safe_substitute(v), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=out_path)
        br.close()


def render_video(post, cfg, style, out_mp4, fps=24, seconds=9.6):
    """Animated Reel: frames are captured by seeking the CSS animations, then encoded with ffmpeg."""
    v = _vals(post, cfg, style)
    v["fs"] = 150 if v["head_len"] <= 24 else 124 if v["head_len"] <= 42 else 100
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
