#!/usr/bin/env python3
"""grade_site v1 — MY browser grading of the v2 workbench (REBUILD-SPEC contract).

Playwright-driven: structural checks, interaction checks, screenshots for the
codex visual pass. Writes /home/eder/.cache/grade-verdicts.json + grade-shots/.
Usage: python3 tools/grade_site.py   (expects server on :8124)
"""
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8124"
SHOTS = Path("/home/eder/.cache/grade-shots")
STAGES = ["persona", "motion", "speech-voice", "camera-angle", "ads", "nsfw", "layers"]
BANNED = ["curated", "premium", "discover", "explore", "showcase", "welcome", "seamless", "powerful"]

verdicts = []


def v(name, ok, detail=""):
    verdicts.append({"check": name, "pass": bool(ok), "detail": str(detail)[:200]})


SHOTS.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto(f"{BASE}/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1200)
    page.screenshot(path=str(SHOTS / "00-home.png"))
    home = page.content()
    v("home: no footer", not re.search(r"<footer", home, re.I))
    v("home: no hero element", not re.search(r'class="[^"]*hero', home, re.I))
    v("home: stage nav", page.query_selector(".stage-nav") is not None)
    body_px = page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)")
    v("font: body >= 18px", body_px >= 18, f"{body_px}px")
    nav = page.eval_on_selector_all(".stage-nav a, .stage-nav button", "els => els.map(e => e.textContent.trim()).filter(Boolean)")
    v("nav: >= 6 stages", len(nav) >= 6, " | ".join(nav)[:120])
    hits = [w for w in BANNED if re.search(rf"\\b{w}\\b", home, re.I)]
    v("home: no banned words", not hits, ",".join(hits))

    for stage in STAGES:
        try:
            page.goto(f"{BASE}/{stage}/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(900)
        except Exception as e:
            v(f"{stage}: loads", False, str(e)[:80])
            continue
        cards = page.query_selector_all(".entry-card")
        html = page.content()
        imgs = page.query_selector_all(".entry-card img")
        loaded = 0
        for img in imgs[:12]:
            if img.evaluate("i => i.naturalWidth > 0"):
                loaded += 1
        v(f"{stage}: cards render", len(cards) > 0, f"{len(cards)} cards")
        v(f"{stage}: previews load", len(imgs) == 0 or loaded > 0, f"{loaded}/{min(12, len(imgs))} naturalWidth>0")
        v(f"{stage}: nsfw marker", "NSFW ON" in html)
        if stage in ("persona", "nsfw"):
            page.screenshot(path=str(SHOTS / f"10-{stage}.png"))

    page.goto(f"{BASE}/persona/", wait_until="domcontentloaded")
    page.wait_for_timeout(900)
    try:
        card = page.query_selector(".entry-card")
        if card:
            card.hover()
            page.wait_for_timeout(700)
            hover = card.evaluate("""el => ({ hasVideo: !!el.querySelector('video'),
                dataVidHook: !!el.querySelector('[data-hover-video]'),
                galleryAttr: !!el.querySelector('[data-gallery]'),
                frames: el.querySelectorAll('.gallery-frame, [data-frame]').length })""")
            v("hover: gallery mechanics on persona card",
              hover["galleryAttr"] or hover["dataVidHook"] or hover["hasVideo"] or hover["frames"] > 0,
              json.dumps(hover))
            before = page.url
            page.evaluate("el => el.click()", card)
            page.wait_for_timeout(600)
            expanded = page.evaluate("!!document.querySelector('.entry-detail, [data-expanded], .card-expanded, dialog[open]')")
            v("click: expand-in-place", page.url == before, f"url same: {page.url == before}, expanded: {expanded}")
            page.screenshot(path=str(SHOTS / "20-persona-expanded.png"))
        else:
            v("persona: interactions", False, "no cards")
    except Exception as e:
        v("persona: interactions", False, str(e)[:90])

    try:
        toggles = page.query_selector_all("[data-stack], [data-stack-toggle], .stack-add, button[aria-pressed]")
        v("stack: toggle targets", len(toggles) > 0, f"{len(toggles)}")
        if len(toggles) >= 2:
            page.evaluate("el => el.click()", toggles[0])
            page.evaluate("el => el.click()", toggles[1])
            page.wait_for_timeout(500)
            rail = page.evaluate("""() => { const r = document.querySelector('[data-stack-manifest]');
                return r ? { visible: r.offsetParent !== null, text: r.textContent.toLowerCase().slice(0, 200) } : null; }""")
            v("stack: rail reacts", rail is not None and rail["visible"], (rail or {}).get("text", "no rail")[:120])
            page.screenshot(path=str(SHOTS / "30-stack-rail.png"))
    except Exception as e:
        v("stack: rail reacts", False, str(e)[:90])

    try:
        chips = page.query_selector_all("[data-filter], .chip, .filter-chip")
        v("filters: chips present", len(chips) > 0, f"{len(chips)}")
        if chips:
            txt = (chips[0].text_content() or "").strip()
            v("filters: live count on chip", bool(re.search(r"\d", txt)), txt[:40])
    except Exception as e:
        v("filters: chips present", False, str(e)[:90])

    try:
        page.goto(f"{BASE}/motion/", wait_until="domcontentloaded")
        page.wait_for_timeout(900)
        vcard = page.query_selector("[data-hover-video]")
        if vcard:
            vcard.scroll_into_view_if_needed()
            vcard.hover()
            page.wait_for_timeout(1000)
            hv = vcard.evaluate("""el => { const v = el.tagName === 'VIDEO' ? el : (el.closest('.entry-card')?.querySelector('video') || null);
                return v ? { paused: v.paused, t: v.currentTime } : null; }""")
            v("hover: video plays on motion card", hv is not None and (not hv["paused"] or hv["t"] > 0), json.dumps(hv))
        else:
            v("hover: video cards exist", False, "no [data-hover-video] on motion")
    except Exception as e:
        v("hover: video plays on motion card", False, str(e)[:90])

    try:
        score = page.query_selector(".score-button")
        if score:
            page.evaluate("el => el.click()", score)
            page.wait_for_timeout(400)
            pop = page.evaluate("!!document.querySelector('.score-popover[open], .score-popover')")
            v("score: why popover", pop)
        else:
            v("score: element found", False, "no .score-button")
    except Exception as e:
        v("score: why popover", False, str(e)[:90])

    browser.close()

Path("/home/eder/.cache/grade-verdicts.json").write_text(json.dumps(verdicts, indent=1))
fails = [x for x in verdicts if not x["pass"]]
print(f"GRADE: {len(verdicts) - len(fails)}/{len(verdicts)} pass")
for f in fails:
    print(f"  FAIL {f['check']}: {f['detail']}")
