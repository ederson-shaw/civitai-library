#!/usr/bin/env python3
"""walk_galleries v1 — real gallery data for kept entries (feeds the hover carousel).

The v0.2 gallery walk never reached the funnel; staged entries carry gallery: [].
This walks /images per kept entry's version: up to 8 preview urls (450px) + any
mp4 (video preview for hover-play), write-file-early, nsfw=true (owner default-on).

IN:  data/staged/*.json (kept entries), ~/.config/civitai/api.key
OUT: data/funnel/galleries.json {id: {"images": [urls], "video": mp4|null}}
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
STAGED = ROOT / "data" / "staged"
OUT = ROOT / "data" / "funnel" / "galleries.json"
API = "https://civitai.com/api/v1"
KEY = Path.home().joinpath(".config/civitai/api.key").read_text().strip()
HDRS = {"Authorization": f"Bearer {KEY}", "User-Agent": "garimpo/0"}


def api_get(path):
    req = Request(f"{API}{path}", headers=HDRS)
    with urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def main():
    targets = {}
    for f in STAGED.glob("*.json"):
        if f.stem in ("RECIPES", "cuts", "MODELS"):
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for e in data.get("entries") or []:
            if e.get("review_flag") is False and str(e.get("id", "")).isdigit() and e.get("kind") != "engine":
                targets[str(e["id"])] = e.get("version_url", "")
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = [k for k in targets if k not in out]
    print(f"kept targets: {len(targets)} | todo: {len(todo)}", file=sys.stderr)
    import re
    vid_re = re.compile(r"\.mp4(?:$|\?)", re.I)
    for i, mid in enumerate(todo):
        try:
            m = api_get(f"/models/{mid}")
            ver = (m.get("modelVersions") or [{}])[0]
            vid = ver.get("id")
            imgs, video = [], None
            if vid:
                page = api_get(f"/images?modelVersionId={vid}&limit=8&nsfw=X")
                for it in page.get("items") or []:
                    url = it.get("url") or ""
                    if not url:
                        continue
                    if vid_re.search(url):
                        video = url
                    else:
                        imgs.append(url.replace("original=true", "width=450") if "original=true" in url else url)
            out[mid] = {"images": imgs[:8], "video": video}
        except Exception as ex:
            out[mid] = {"images": [], "video": None, "error": str(ex)[:60]}
        time.sleep(0.4)
        if (i + 1) % 15 == 0:
            OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
            print(f"  early: {len(out)} done", file=sys.stderr)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    with_g = sum(1 for v in out.values() if v.get("images") or v.get("video"))
    with_v = sum(1 for v in out.values() if v.get("video"))
    print(f"done: {len(out)} ids | {with_g} with media | {with_v} with video", file=sys.stderr)


if __name__ == "__main__":
    main()
