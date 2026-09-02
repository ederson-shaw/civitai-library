#!/usr/bin/env python3
"""CI-style checks for content-class separation and basic static quality."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def main() -> int:
    failures: list[str] = []
    if not SITE.exists():
        print("FAIL: site/ does not exist; run tools/sitegen.py first")
        return 1

    mature_candidates = json.loads((ROOT / "data/candidates-nsfw.json").read_text(encoding="utf-8"))
    mature_curations = json.loads((ROOT / "research/curation-draft-nsfw.json").read_text(encoding="utf-8"))
    forbidden: dict[str, str] = {}
    for item in mature_candidates:
        for value in [item.get("id"), item.get("name"), item.get("source_url")]:
            if value is not None and str(value).strip():
                forbidden[str(value).lower()] = f"mature candidate {item.get('id')}"
        preview = item.get("preview") or {}
        for value in preview.values():
            if value:
                forbidden[str(value).lower()] = f"mature preview {item.get('id')}"
        for gallery in item.get("gallery") or []:
            if gallery.get("url"):
                forbidden[str(gallery["url"]).lower()] = f"mature gallery {item.get('id')}"
    for item in mature_curations:
        for value in [item.get("id"), item.get("our_name")]:
            if value is not None and str(value).strip():
                forbidden[str(value).lower()] = f"mature curation {item.get('id')}"

    # Mature route/data are intentionally allowed to contain the mature payload.
    sfw_files = [
        path for path in SITE.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".html", ".json", ".js"}
        and "mature-entries.json" not in str(path)
        and "search-index-mature.json" not in str(path)
        and (not path.relative_to(SITE).parts or path.relative_to(SITE).parts[0] != "mature")
    ]
    for path in sfw_files:
        content = path.read_text(encoding="utf-8").lower()
        for needle, owner in forbidden.items():
            if needle in content:
                fail(f"{path.relative_to(ROOT)} contains {owner}: {needle[:80]}", failures)
                break

    # A gated media URL may be present as data-src, but never as initial src.
    sfw_html = [path for path in SITE.rglob("*.html") if not path.relative_to(SITE).parts or path.relative_to(SITE).parts[0] != "mature"]
    gated_urls: set[str] = set()
    for lane in ("persona", "workflows"):
        for item in json.loads((ROOT / f"data/candidates-{lane}.json").read_text(encoding="utf-8")):
            if int(item.get("nsfwLevel", 0)) < 8:
                continue
            preview = item.get("preview") or {}
            gated_urls.update(str(value).lower() for value in preview.values() if value)
            gated_urls.update(str(gallery.get("url")).lower() for gallery in item.get("gallery") or [] if gallery.get("url"))
    for path in sfw_html:
        content = path.read_text(encoding="utf-8").lower()
        for url in gated_urls:
            if re.search(rf"(?<![a-z0-9_-])src\s*=\s*['\"]{re.escape(url)}['\"]", content):
                fail(f"gated preview URL appears in initial src on {path.relative_to(ROOT)}", failures)
                break

    # Every shipped image has dimensions and lazy loading; blurred media starts without src.
    for path in sfw_html:
        for tag in re.findall(r"<img\b[^>]*>", path.read_text(encoding="utf-8"), flags=re.I):
            if not re.search(r"\bwidth\s*=", tag, re.I) or not re.search(r"\bheight\s*=", tag, re.I):
                fail(f"image missing width/height on {path.relative_to(ROOT)}", failures)
            if not re.search(r"\bloading\s*=\s*['\"]lazy['\"]", tag, re.I):
                fail(f"image missing loading=lazy on {path.relative_to(ROOT)}", failures)

    app = SITE / "assets/app.js"
    if not app.exists():
        fail("site/assets/app.js is missing", failures)
    elif len(app.read_text(encoding="utf-8").splitlines()) > 1200:
        fail("site/assets/app.js exceeds the 1200-line budget", failures)

    if failures:
        print(f"{len(failures)} build check(s) failed")
        return 1
    print(f"build check passed: {len(sfw_files)} SFW artifacts scanned; gated media has no initial src")
    return 0


if __name__ == "__main__":
    sys.exit(main())
