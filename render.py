"""Turns the headline into a 1080x1080 branded image (Playwright + HTML)."""
import html
from playwright.sync_api import sync_playwright

STYLES = {  # bg, text, accent, chip text
    "amber": ("#FFB547", "#0E1B2C", "#0E1B2C", "#FFB547"),
    "dark":  ("#0E1B2C", "#F5F7FA", "#FFB547", "#0E1B2C"),
    "paper": ("#F5F7FA", "#0E1B2C", "#FFB547", "#0E1B2C"),
}

PAGE = """<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@500&display=swap" rel="stylesheet">
<style>body{{margin:0}}</style></head><body>
<div style="width:1080px;height:1080px;box-sizing:border-box;padding:84px;display:flex;flex-direction:column;justify-content:space-between;background:{bg};color:{fg};font-family:'Inter',Arial,sans-serif">
<div style="display:flex;justify-content:space-between;align-items:center;font-size:26px;letter-spacing:4px;font-weight:500"><span>AI AUTOMATION</span><span style="padding:10px 24px;border-radius:40px;background:{ac};color:{chip}">{tag}</span></div>
<div><h1 style="margin:0;font-family:'Space Grotesk',Arial,sans-serif;font-size:{fs}px;line-height:1.05;font-weight:700">{head}</h1>
<div style="margin-top:36px;font-size:40px;line-height:1.3;font-weight:500;opacity:.9">{sub}</div></div>
<div style="display:flex;justify-content:space-between;align-items:center;font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:32px"><span>{handle}</span><span style="color:{fg}">{cta}</span></div>
</div></body></html>"""


def render(post, cfg, style, out_path):
    bg, fg, ac, chip = STYLES[style]
    head = post["headline"]
    fs = 124 if len(head) <= 24 else 104 if len(head) <= 42 else 86
    page = PAGE.format(bg=bg, fg=fg, ac=ac, chip=chip, fs=fs, tag=html.escape(post.get("post_type", "TIP").replace("_", " ").upper()),
                       head=html.escape(head), sub=html.escape(post["subline"]),
                       handle=html.escape(cfg["brand"]["handle"]), cta="DM &quot;AUTOMATE&quot;")
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1080})
        pg.set_content(page, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=out_path)
        br.close()
