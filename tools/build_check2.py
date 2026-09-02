#!/usr/bin/env python3
"""Hostile static checks for the v2 generated workbench."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
STAGE_IDS = ("persona", "motion", "speech-voice", "camera-angle", "ads", "nsfw")
BANNED_WORDS = ("curated", "premium", "discover", "explore", "showcase", "welcome", "hero", "our", "seamless", "powerful")


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def check_banned_words(html_files: list[Path]) -> None:
    for path in html_files:
        content = read(path).lower()
        chrome_only = re.sub(r'<article class="entry-card".*?</article>', "", content, flags=re.S)
        for word in BANNED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", chrome_only):
                fail(f"banned UI word {word!r} in {path.relative_to(ROOT)}")


def check_fonts(css: str) -> None:
    body = re.search(r"body\s*\{([^}]*)\}", css, re.S)
    if not body:
        fail("body CSS block missing")
    body_sizes = [float(value) for value in re.findall(r"font(?:-size)?\s*:\s*(\d+(?:\.\d+)?)px", body.group(1))]
    if not body_sizes or max(body_sizes) < 18:
        fail(f"base font is below 18px: {body_sizes}")
    names = re.search(r"\.entry-name\s*\{([^}]*)\}", css, re.S)
    if not names:
        fail("entry-name CSS block missing")
    name_sizes = [float(value) for value in re.findall(r"font(?:-size)?\s*:\s*(\d+(?:\.\d+)?)px", names.group(1))]
    if not name_sizes or max(name_sizes) < 20:
        fail(f"entry name font is below 20px: {name_sizes}")


def check_owner_surfaces(html_files: list[Path], css: str, js: str, demo: bool = False) -> None:
    persona = read(SITE / "persona" / "index.html")
    if not demo:
        default_filter = re.search(
            r'data-filter-facet="visual: realism-photoreal"[^>]*data-default-filter="true"[^>]*aria-pressed="true"',
            persona,
        )
        if not default_filter:
            fail("persona does not default to an active realism-photoreal filter")
        first_cluster = persona.find("data-visual-cluster=")
        if first_cluster < 0 or 'data-style="anime-illustration"' in persona[:first_cluster]:
            fail("anime entry leaked into the persona default group")
    if re.search(r'<button[^>]+data-filter-facet="all"', persona, re.I):
        fail("all filter chip is still rendered")
    if "margin-top: auto" not in css or "card-content { flex: 1; }" not in css:
        fail("card footer pinning rules are missing")
    if "filter: blur" in css:
        fail("NSFW preview blur is still present")
    if "setInterval(advance, 1200)" not in js or "data-gallery" not in js:
        fail("gallery carousel behavior is missing")
    if "video.muted = false" not in js or "data-speaker-toggle" not in js:
        fail("audio-first video fallback behavior is missing")
    if "data-stack-manifest" not in js or "folder unknown" not in js or "vramKnown" not in js:
        fail("rail manifest/totals backing logic is missing")
    if not re.search(r'data-stack-vram[^>]*>—</strong>', read(SITE / "index.html")):
        fail("unknown VRAM does not start as an em dash")
    if 'class="requirements-panel"' not in persona or "open exact version on civitai" not in persona:
        fail("expanded rich detail panel is missing")
    if 'class="entry-purpose"' not in read(SITE / "speech-voice" / "index.html"):
        fail("human purpose line is not surfaced on speech cards")
    if re.search(r'<div class="filter-row">.*?<b>0</b>', persona, re.S):
        fail("zero-count filter chip is rendered")


def check_pipeline() -> str:
    import json
    staged = ROOT / "data" / "staged"
    problems = []
    for path in sorted(staged.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("entries") or []
        renderable = [
            e for e in entries
            if e.get("review_flag") is False
            and (e.get("kind") == "engine" or (e.get("preview") or {}).get("url_width450") or (e.get("preview") or {}).get("url_original"))
        ]
        if entries and not renderable:
            problems.append(f"{path.stem}: {len(entries)} pulled, 0 renderable (pipeline break)")
    if problems:
        fail("; ".join(problems))
    return "pipeline: every staged stage has renderable entries"


def check_site(demo: bool) -> list[str]:
    if not SITE.exists():
        fail("site directory is missing; run sitegen2.py first")
    stage_files = [SITE / stage / "index.html" for stage in STAGE_IDS]
    html_files = stage_files + [SITE / "layers" / "index.html", SITE / "recipes" / "index.html", SITE / "index.html"]
    for path in stage_files:
        html = read(path)
        if '<main class="workbench">' not in html:
            fail(f"stage shell missing in {path.relative_to(ROOT)}")
        if 'class="stage-nav"' not in html:
            fail(f"sticky stage navigation missing in {path.relative_to(ROOT)}")
        if 'class="entry-card"' not in html and '0 kept after filters' not in html and not demo:
            fail(f"default empty-state contract missing in {path.relative_to(ROOT)}")
        if 'NSFW ON' not in html:
            fail(f"NSFW default marker missing in {path.relative_to(ROOT)}")
        if 'class="answer-first"' not in html:
            fail(f"answer-first row missing in {path.relative_to(ROOT)}")
        if 'decision-matrix' in html or 'matrix-' in html:
            fail(f"comparison matrix still rendered in {path.relative_to(ROOT)}")
        if 'class="entry-card"' in html and 'class="media-missing"' in html:
            fail(f"blank preview marker rendered in {path.relative_to(ROOT)}")
    check_banned_words(html_files)
    css = read(SITE / "assets" / "style.css")
    js = read(SITE / "assets" / "app.js")
    check_owner_surfaces(html_files, css, js, demo=demo)
    recipes_html = read(SITE / "recipes" / "index.html")
    if 'data-stage="recipes"' not in recipes_html:
        fail("recipes navigation link missing")
    if 'recipes land next pull' not in recipes_html and 'class="recipe-card"' not in recipes_html:
        fail("recipes page has neither recipes nor honest empty state")
    check_fonts(css)
    if "position: sticky" not in css:
        fail("sticky navigation rule missing")
    all_html = "\n".join(read(path) for path in html_files)
    if re.search(r"<footer\b|\bhero\b", all_html, re.I):
        fail("footer or hero element/copy found")
    if demo:
        for stage in (*STAGE_IDS, "layers"):
            count = read(SITE / stage / "index.html").count('data-demo="true"')
            if count != 3:
                fail(f"{stage} has {count} demo entries; expected exactly 3")
        return ["demo entries: 3 per stage/class"]
    if "[DEMO]" in all_html:
        fail("demo entry leaked into default build")
    return ["default build has no demo entries"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the v2 generated site")
    parser.add_argument("--demo", action="store_true", help="expect the in-memory demo build")
    args = parser.parse_args()
    checks = check_site(demo=args.demo)
    checks.append(check_pipeline())
    mode = "demo" if args.demo else "default"
    print(f"build_check2: PASS ({mode})")
    print("  stages: 6 rendered")
    print("  chrome: no footer / no hero")
    print("  fonts: base >= 18px / names >= 20px")
    print("  " + checks[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
