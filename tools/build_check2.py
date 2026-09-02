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
    html_files = stage_files + [SITE / "layers" / "index.html", SITE / "index.html"]
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
        if 'decision-matrix' not in html:
            fail(f"decision matrix missing in {path.relative_to(ROOT)}")
        if 'class="entry-card"' in html and 'class="media-missing"' in html:
            fail(f"blank preview marker rendered in {path.relative_to(ROOT)}")
    check_banned_words(html_files)
    css = read(SITE / "assets" / "style.css")
    read(SITE / "assets" / "app.js")
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
