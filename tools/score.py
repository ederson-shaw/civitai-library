#!/usr/bin/env python3
"""score v1 — funnel scoring at scale (fixes the circular calibration condemned in FAILURE-ANALYSIS-R1).

Anchors (p75 ratio, p90 downloads) recompute from the ACTUAL funnel distribution per stage,
never from a 100-entry sample. Composite per docs/CRITERIA.md v2, adapted to stages.

IN:  data/funnel/raw-*.json (slice files, one list per walk; slice name carries stage)
     data/funnel/all-candidates.json (merged id-keyed, optional — raws are source of truth)
OUT: data/funnel/scored.json   (entries + composite + anchors used + stage(s))
     data/funnel/cut-list.json (below-floor cuts with reason — the transparency panel)
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

FUNNEL = Path(__file__).resolve().parent.parent / "data" / "funnel"
DL_FLOOR = 500

STAGE_OF_SLICE = [
    ("persona", "PERSONA"), ("realism", "PERSONA"),
    ("workflows", "MOTION"), ("video", "MOTION"), ("wan", "MOTION"),
    ("ltx", "MOTION"), ("hunyuan", "MOTION"), ("minimax", "MOTION"),
    ("nsfw", "NSFW"), ("chroma", "NSFW"), ("biglust", "NSFW"),
    ("lustify", "NSFW"), ("aramanta", "NSFW"), ("anteros", "NSFW"), ("bigasp", "NSFW"),
    ("ads", "ADS"), ("product", "ADS"), ("ugc", "ADS"), ("commercial", "ADS"),
    ("speech", "SPEECH_VOICE"), ("talking", "SPEECH_VOICE"), ("voice", "SPEECH_VOICE"),
]


def stage_for(slice_name):
    low = slice_name.lower()
    for key, stage in STAGE_OF_SLICE:
        if key in low:
            return stage
    return "UNSORTED"


def pctl(values, q):
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[idx]


def load_slices():
    stages = defaultdict(dict)
    for f in sorted(FUNDIR.glob("raw-*.json")) if (FUNDIR := FUNNEL).exists() else []:
        try:
            items = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(items, list):
            continue
        stage = stage_for(f.stem.replace("raw-", ""))
        for it in items:
            if isinstance(it, dict) and it.get("id") is not None:
                stages[stage].setdefault(it["id"], it)
    return stages


def ratio(entry):
    stats = entry.get("stats") or {}
    dl = stats.get("downloadCount") or 0
    th = stats.get("thumbsUpCount") or 0
    return (th / dl) if dl >= DL_FLOOR else None


def score_stage(entries):
    ratios = [r for r in (ratio(e) for e in entries.values()) if r is not None]
    dls = [e.get("stats", {}).get("downloadCount") or 0 for e in entries.values()]
    anchors = {"ratio_p75": pctl(ratios, .75) or 0.0001, "dl_p90": max(1.0, pctl(dls, .90))}
    scored = []
    for e in entries.values():
        stats = e.get("stats") or {}
        r = ratio(e)
        comp = 0.0
        parts = {}
        if r is None:
            parts["ratio"] = 0
            parts["magnitude"] = 0
        else:
            parts["ratio"] = round(min(1.0, r / anchors["ratio_p75"]) * 10, 1)
            parts["magnitude"] = round(min(1.0, math.log10(max(1, stats.get("downloadCount") or 0)) / math.log10(anchors["dl_p90"])) * 10, 1)
        comp += parts["ratio"] + parts["magnitude"]
        scored.append({"id": e.get("id"), "name": e.get("name"), "stats": stats,
                       "type": e.get("type"), "baseModel": e.get("baseModel"),
                       "nsfwLevel": e.get("nsfwLevel"), "preview": e.get("preview"),
                       "parts": parts, "composite_auto": round(comp, 1),
                       "curation_pending": True})
    scored.sort(key=lambda x: -x["composite_auto"])
    return anchors, scored


def main():
    stages = load_slices()
    if not stages:
        print("no raw-*.json slices found in data/funnel/", file=sys.stderr)
        sys.exit(1)
    out = {"generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
           "dl_floor": DL_FLOOR, "stages": {}}
    cuts = []
    for stage, entries in sorted(stages.items()):
        anchors, scored = score_stage(entries)
        kept = [s for s in scored if ratio_lookup(entries, s["id"])]
        cut_n = len(scored) - len(kept)
        top10 = max(1, len(kept) // 10)
        for i, s in enumerate(kept):
            band = i + 1 <= top10
            s["tier_auto"] = "S-candidate" if band and s["composite_auto"] >= 20 else ("A-candidate" if i + 1 <= top10 * 3 else "B-candidate")
        out["stages"][stage] = {"count": len(entries), "anchors": anchors,
                                "kept_above_floor": len(kept), "cut_below_floor": cut_n,
                                "entries": kept}
        cuts.append({"stage": stage, "cut": cut_n, "reason": f"downloads < {DL_FLOOR} (anti-farm floor)"})
    (FUNNEL / "scored.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (FUNNEL / "cut-list.json").write_text(json.dumps({"generated": out["generated"], "cuts": cuts}, indent=1))
    for stage, blob in out["stages"].items():
        top = blob["entries"][0] if blob["entries"] else {}
        print(f"{stage}: {blob['count']} pulled, {blob['kept_above_floor']} kept, cut {blob['cut_below_floor']} | top: {top.get('name','?')} {top.get('composite_auto')}", file=sys.stderr)


def ratio_lookup(entries, cid):
    e = entries.get(cid) or {}
    stats = e.get("stats") or {}
    return (stats.get("downloadCount") or 0) >= DL_FLOOR


if __name__ == "__main__":
    main()
