#!/usr/bin/env python3
"""gallery + usage collectors and snapshot history — hostile R1 #2/#5/#17,
v0.2 receipts: R2 #3 (gallery data missing — every entry now carries
images[]) + R2 #7 (usage walk was top-10 only — now every entry).

Gallery: walks GET /api/v1/images?modelVersionId=<latest>&limit=6&withMeta=true
(authed) for EVERY entry, keeps up to 6 images, meta-bearing first.
Usage: walks the same endpoint with limit=100 for EVERY entry and merges a
"usage" key. Politeness: 0.5s sleep per request. The API returns all-time
stats only — the time axis is growth between snapshots, stamped per date dir.

IN:  candidates json file (list), api key, injected http_get (+ injected
     width=450 url shrinker for gallery, garimpo.thumb450);
     snapshot writers take the data dir + the pull's output filenames.
OUT: same file with gallery [{url, nsfwLevel, has_meta}] (<= 6, meta first)
     and usage {posted_images_est, reactions_sum, meta_match} on every entry;
     data/snapshots/YYYY-MM-DD/<files> (last 30 kept) +
     data/snapshots/deltas.json (per-id downloadCount/thumbsUpCount growth
     between the two newest dates; {"history": false} until 2 dates exist).
"""
import json
import shutil
import sys
import time
from pathlib import Path

IMAGES_API = "https://civitai.com/api/v1/images"
KEEP_SNAPSHOTS = 30


def load_lane(path, job):
    try:
        candidates = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError):
        print(f"{job}: unreadable {Path(path).name}, skipped", file=sys.stderr)
        return None
    if not isinstance(candidates, list) or not candidates:
        print(f"{job}: {Path(path).name} empty or blocked, skipped", file=sys.stderr)
        return None
    return candidates


def latest_version_id(candidate):
    versions = candidate.get("versions") or []
    return versions[0].get("id") if versions else None


def usage_for(version_id, page):
    items = page.get("items") or []
    reactions = 0
    meta_match = False
    for image in items:
        stats = image.get("stats") or {}
        reactions += (stats.get("likeCount") or 0) + (stats.get("heartCount") or 0)
        for resource in ((image.get("meta") or {}).get("civitaiResources") or []):
            if resource.get("modelVersionId") == version_id:
                meta_match = True
    return {
        "posted_images_est": "100+" if len(items) >= 100 else str(len(items)),
        "reactions_sum": reactions,
        "meta_match": meta_match,
    }


def walk_images(candidates, key, get, limit, job):
    walked = []
    for candidate in candidates:
        version_id = latest_version_id(candidate)
        if version_id is None:
            continue
        page = get(f"{IMAGES_API}?modelVersionId={version_id}&limit={limit}&withMeta=true", key)
        time.sleep(0.5)
        walked.append((candidate, page))
    print(f"{job}: {len(walked)}/{len(candidates)} entries walked", file=sys.stderr)
    return walked


def enrich_lane_usage(path, key, get):
    path = Path(path)
    candidates = load_lane(path, "usage")
    if candidates is None:
        return
    for candidate, page in walk_images(candidates, key, get, 100, "usage"):
        candidate["usage"] = (usage_for(latest_version_id(candidate), page)
                              if page is not None else {"error": "images fetch failed"})
    path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    enriched = sum(1 for c in candidates if "usage" in c)
    print(f"usage: {path.name} enriched {enriched}/{len(candidates)}", file=sys.stderr)


def gallery_for(page, shrink):
    items = sorted(page.get("items") or [], key=lambda i: not i.get("meta"))
    return [{"url": shrink(i.get("url")),
             "nsfwLevel": i.get("nsfwLevel"),
             "has_meta": bool(i.get("meta"))}
            for i in items[:6]]


def enrich_lane_gallery(path, key, get, shrink):
    path = Path(path)
    candidates = load_lane(path, "gallery")
    if candidates is None:
        return
    for candidate, page in walk_images(candidates, key, get, 6, "gallery"):
        candidate["gallery"] = (gallery_for(page, shrink)
                                if page is not None else {"error": "images fetch failed"})
    path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    filled = sum(1 for c in candidates if isinstance(c.get("gallery"), list))
    print(f"gallery: {path.name} filled {filled}/{len(candidates)}", file=sys.stderr)


def snapshot_dirs(data_dir):
    parent = Path(data_dir) / "snapshots"
    return sorted(p for p in parent.iterdir() if p.is_dir()) if parent.exists() else []


def write_snapshot(data_dir, today, files, keep=KEEP_SNAPSHOTS):
    data_dir = Path(data_dir)
    snap_dir = data_dir / "snapshots" / today
    snap_dir.mkdir(parents=True, exist_ok=True)
    for name in files:
        src = data_dir / name
        if src.exists():
            shutil.copy2(src, snap_dir / name)
    snaps = snapshot_dirs(data_dir)
    for old in snaps[:-keep]:
        shutil.rmtree(old)
    print(f"snapshot {snap_dir} ({len(snaps[-keep:])} dates kept)", file=sys.stderr)


def lane_growth(prev_lane, last_lane):
    prev_stats = {c.get("id"): c.get("stats") or {} for c in prev_lane}
    growth = []
    for c in last_lane:
        old = prev_stats.get(c.get("id"))
        if old is None:
            continue
        new = c.get("stats") or {}
        growth.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "downloadCount": (new.get("downloadCount") or 0) - (old.get("downloadCount") or 0),
            "thumbsUpCount": (new.get("thumbsUpCount") or 0) - (old.get("thumbsUpCount") or 0),
        })
    return growth


def write_deltas(data_dir, files):
    data_dir = Path(data_dir)
    out_path = data_dir / "snapshots" / "deltas.json"
    snaps = snapshot_dirs(data_dir)
    if len(snaps) < 2:
        out_path.write_text(json.dumps({"history": False}, indent=2))
        print("deltas: single snapshot date, baseline only", file=sys.stderr)
        return
    prev, last = snaps[-2], snaps[-1]
    lanes = {}
    for name in files:
        if not name.startswith("candidates-"):
            continue
        try:
            old = json.loads((prev / name).read_text())
            new = json.loads((last / name).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(old, list) and isinstance(new, list):
            lanes[name[len("candidates-"):-len(".json")]] = lane_growth(old, new)
    out_path.write_text(json.dumps({"history": True, "from": prev.name, "to": last.name,
                                    "lanes": lanes}, ensure_ascii=False, indent=2))
    print(f"deltas: {prev.name} -> {last.name}", file=sys.stderr)
