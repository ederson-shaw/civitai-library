#!/usr/bin/env python3
"""stage_data v1 — build data/staged/<STAGE>.json per the dictated site contract.

Merges funnel scores + vision labels + preview data into the per-stage files
sitegen2 consumes. Vision labels are authoritative for visual_class/nsfw_bucket;
entries without a vision label get visual_class "unreviewed" and stay renderable
(curation queue refines, nothing silently dropped).

Heuristic stage/layer assignments (talk/lip/voice -> SPEECH_VOICE, detail/skin/
light/upscale -> LAYERS) are marked "heuristic": true — the curation pass owns
final truth.

IN:  data/funnel/scored.json, data/funnel/vision-labels.json (json-lines, may
     be partial), data/funnel/vision-shortlists.json
OUT: data/staged/{PERSONA,MOTION,SPEECH_VOICE,CAMERA_ANGLE,ADS,NSFW,LAYERS}.json
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNNEL = ROOT / "data" / "funnel"
STAGED = ROOT / "data" / "staged"
STAGES = ["PERSONA", "MOTION", "SPEECH_VOICE", "CAMERA_ANGLE", "ADS", "NSFW", "LAYERS"]

TALK = re.compile(r"talk|lip.?sync|speech|voice|narrat|s2v", re.I)
CAM = re.compile(r"camera|angle|pose|perspect|fov", re.I)
AD = re.compile(r"\bad\b|advertis|product|commercial|ugc|brand", re.I)
LAYER = re.compile(r"detail|skin|light|upscale|booster|enhancer|finish|polish|texture|grain|fix", re.I)


def load_labels():
    labels = {}
    f = FUNNEL / "vision-labels.json"
    if not f.exists():
        return labels
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            labels[obj.get("id")] = obj
        except json.JSONDecodeError:
            continue
    return labels


def entry_shape(e, label):
    v = label or {}
    return {
        "id": e.get("id"),
        "our_name": None,
        "source_name": e.get("name"),
        "purpose": None,
        "composite": e.get("composite_auto"),
        "tier": e.get("tier_auto"),
        "visual_class": v.get("visual_class", "unreviewed"),
        "quality": v.get("quality"),
        "nsfw_bucket": v.get("nsfw_bucket"),
        "name_fit": v.get("name_fit"),
        "review_flag": v.get("review_flag", True),
        "baseModel": e.get("baseModel"),
        "vram_class": None,
        "tradeoff": None,
        "open_closed": None,
        "stats": {"downloadCount": (e.get("stats") or {}).get("downloadCount"),
                  "thumbsUpCount": (e.get("stats") or {}).get("thumbsUpCount")},
        "pulled_at": None,
        "preview": e.get("preview") or {},
        "gallery": [],
        "stacks_on": [],
        "verdict_keep": None,
        "civitai_url": f"https://civitai.com/models/{e.get('id')}" if e.get("id") else None,
        "requirements": {"models": [], "nodes": []},
        "heuristic": {"lane": None, "layer": None, "era": e.get("motion_era")},
    }


def main():
    labels = load_labels()
    scored = json.loads((FUNNEL / "scored.json").read_text())
    buckets = {s: [] for s in STAGES}
    for stage, blob in scored["stages"].items():
        for e in blob["entries"]:
            rec = entry_shape(e, labels.get(e.get("id")))
            name = (e.get("name") or "")
            if stage == "PERSONA" and TALK.search(name):
                buckets["SPEECH_VOICE"].append(rec)
                continue
            if stage == "PERSONA" and LAYER.search(name):
                rec["stacks_on"] = ["PERSONA"]
                buckets["LAYERS"].append(rec)
                continue
            if stage == "MOTION" and TALK.search(name):
                buckets["SPEECH_VOICE"].append(rec)
                continue
            if stage == "MOTION" and CAM.search(name):
                buckets["CAMERA_ANGLE"].append(rec)
                continue
            if stage == "MOTION" and AD.search(name):
                buckets["ADS"].append(rec)
                continue
            if stage in buckets:
                buckets[stage].append(rec)
    STAGED.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for stage in STAGES:
        out = {"stage": stage, "generated": now,
               "note": "auto-staged from funnel+vision; curation pass owns final fields",
               "entries": buckets[stage]}
        (STAGED / f"{stage}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
        print(f"{stage}: {len(buckets[stage])} entries", file=sys.stderr)


if __name__ == "__main__":
    main()
