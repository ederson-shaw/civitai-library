#!/usr/bin/env python3
"""garimpo v0.3 — THE BIG FUNNEL: 5-10k civitai candidates before site filters.

Reuses garimpo.py's http_get (429/5xx retry ladder), thumb450, to_candidate
(assembly law — same schema as data/candidates-*.json). Cursor-walks one slice
at a time, writes data/funnel/raw-<lane>-<slice>.json after EVERY walk, and
rewrites index.json + all-candidates.json after every lane, so a die mid-run
still leaves a fresh partial funnel on disk.

IN:  ~/.config/civitai/api.key (bearer; nsfw lane needs it)
OUT: data/funnel/raw-<lane>-<slice>.json (per walk, candidate schema),
     data/funnel/all-candidates.json ({id: candidate}, deduped),
     data/funnel/index.json {total_pulled, per_lane, per_slice, deduped_total,
     pulled_at, stopped}
Caps: 90 min wall clock, 8000 deduped candidates — whichever first, stop clean.
No gallery/usage walks this round (that is post-filter enrichment).
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).parent))
import garimpo
from garimpo import http_get, to_candidate, load_key

API = garimpo.API
CREATORS_API = "https://civitai.com/api/v1/creators"
FUNNEL = Path("/home/eder/Documentos/civitai-library/data/funnel")
WALL_SECONDS = 90 * 60
DEDUP_CAP = 8000
POLITE = 0.5

START = time.monotonic()
DEADLINE = START + WALL_SECONDS
deduped = {}
per_slice = {}
per_lane = {}
stopped = None


class Budget(Exception):
    pass


def budget_hit():
    if time.monotonic() >= DEADLINE:
        return "wall-clock 90min"
    if len(deduped) >= DEDUP_CAP:
        return "8000 deduped candidates"
    return None


def write_index():
    index = {
        "total_pulled": sum(per_slice.values()),
        "per_lane": per_lane,
        "per_slice": per_slice,
        "deduped_total": len(deduped),
        "pulled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stopped": stopped,
    }
    (FUNNEL / "index.json").write_text(json.dumps(index, indent=2))
    (FUNNEL / "all-candidates.json").write_text(
        json.dumps(deduped, ensure_ascii=False))


def absorb(cands):
    for c in cands:
        deduped.setdefault(c["id"], c)


def walk(lane, slice_name, params, want, period=None):
    """Cursor-walk one slice, write its raw file, return candidate count."""
    seen, cands = set(), []
    url = f"{API}?{params}"
    while url and len(cands) < want:
        stop = budget_hit()
        if stop:
            global stopped
            stopped = stop
            raise Budget()
        page = http_get(url, load_key())
        if page is None:
            print(f"{lane}/{slice_name}: page failed, slice truncated",
                  file=sys.stderr)
            break
        items = page.get("items") or []
        if not items:
            break
        for m in items:
            mid = m.get("id")
            if mid not in seen:
                seen.add(mid)
                cands.append(to_candidate(m, period))
        url = (page.get("metadata") or {}).get("nextPage")
        if url:
            time.sleep(POLITE)
    picked = cands[:want]
    per_slice[slice_name] = len(picked)
    path = FUNNEL / f"raw-{lane}-{slice_name}.json"
    path.write_text(json.dumps(picked, ensure_ascii=False, indent=2))
    absorb(picked)
    print(f"[{lane}/{slice_name}] slice={len(picked)} "
          f"deduped_total={len(deduped)} pulled={sum(per_slice.values())} "
          f"elapsed={int(time.monotonic() - START)}s", file=sys.stderr)
    return len(picked)


def creator_seed(seed, want=200):
    """Community-named model search. query= may be broken (census OPEN item):
    probe it, fall back to /creators?query= then walk that creator's catalogue."""
    q = urlencode({"limit": 100, "query": seed, "nsfw": "true",
                   "sort": "Most Downloaded"}, doseq=True)
    page = http_get(f"{API}?{q}", load_key())
    if page and (page.get("items") or []):
        return walk("nsfw", f"query-{seed}", q, want)
    print(f"query={seed}: broken/empty -> /creators fallback", file=sys.stderr)
    cq = urlencode({"limit": 5, "query": seed}, doseq=True)
    cpage = http_get(f"{CREATORS_API}?{cq}", load_key())
    creators = (cpage or {}).get("items") or []
    if not creators:
        per_slice[f"creator-{seed}"] = 0
        print(f"nsfw/creator-{seed}: no creator found, slice=0", file=sys.stderr)
        return 0
    username = creators[0]["username"]
    print(f"creator seed {seed} -> username={username}", file=sys.stderr)
    uq = urlencode({"limit": 100, "username": username, "nsfw": "true",
                    "sort": "Most Downloaded"}, doseq=True)
    return walk("nsfw", f"creator-{username}", uq, want)


def run_lane(lane):
    per_lane.setdefault(lane, 0)
    for slice_name, params, want, period in SLICES[lane]:
        per_lane[lane] += walk(lane, slice_name, params, want, period)
    if lane == "nsfw":
        per_lane[lane] += creator_seed("chroma")
        per_lane[lane] += creator_seed("biglust")
        per_lane[lane] += creator_seed("lustify")
        per_lane[lane] += creator_seed("aramanta")
        per_lane[lane] += creator_seed("anteros")
        per_lane[lane] += creator_seed("bigasp")
    write_index()
    print(f"== lane {lane} done: {per_lane[lane]} pulled, "
          f"deduped {len(deduped)} ==", file=sys.stderr)


SLICES = {
    "workflows": [
        (f"sort-{s.replace(' ', '')}-period-{p}",
         urlencode({"limit": 100, "types": "Workflows", "sort": s, "period": p}, doseq=True),
         800, p)
        for s in ("Most Downloaded", "Highest Rated", "Newest")
        for p in ("AllTime", "Year", "Month")
    ],
    "persona": [
        (f"sort-{s.replace(' ', '')}-period-{p}",
         urlencode({"limit": 100, "types": ["LORA", "Checkpoint"],
                    "sort": s, "period": p}, doseq=True), 400, p)
        for s in ("Most Downloaded", "Highest Rated", "Newest")
        for p in ("AllTime", "Year")
    ] + [
        (f"tag-{t}",
         urlencode({"limit": 100, "types": ["LORA", "Checkpoint"], "tag": t,
                    "sort": "Most Downloaded"}, doseq=True), 400, None)
        for t in ("realistic", "photorealistic", "photography", "instagram",
                  "portrait")
    ],
    "nsfw": [
        (f"sort-{s.replace(' ', '')}-period-{p}",
         urlencode({"limit": 100, "types": "LORA", "nsfw": "true",
                    "sort": s, "period": p}, doseq=True), 400, p)
        for s in ("Most Downloaded", "Highest Rated")
        for p in ("AllTime", "Year")
    ] + [
        ("tag-nsfw",
         urlencode({"limit": 100, "types": "LORA", "nsfw": "true",
                    "tag": "nsfw", "sort": "Most Downloaded"}, doseq=True), 400, None),
    ],
    "video": [
        (f"tag-{t}",
         urlencode({"limit": 100, "types": "Workflows", "tag": t,
                    "sort": "Most Downloaded"}, doseq=True), 300, None)
        for t in ("wan", "ltx", "hunyuan", "minimax", "video")
    ],
}


def main():
    FUNNEL.mkdir(parents=True, exist_ok=True)
    if not load_key():
        print("no api key: nsfw lane will be clamped/empty", file=sys.stderr)
    try:
        for lane in ("workflows", "persona", "nsfw", "video"):
            run_lane(lane)
    except Budget:
        print(f"budget stop: {stopped}", file=sys.stderr)
    write_index()
    print(f"DONE deduped={len(deduped)} pulled={sum(per_slice.values())} "
          f"slices={len(per_slice)} stopped={stopped}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
