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
STAGES = ["PERSONA", "MOTION", "SPEECH_VOICE", "CAMERA_ANGLE", "ADS", "NSFW", "LAYERS", "MODELS"]

TALK = re.compile(r"talk|lip.?sync|speech|voice|narrat|s2v", re.I)
CAM = re.compile(r"camera|angle|pose|perspect|fov", re.I)
AD = re.compile(r"\bad\b|advertis|product|commercial|ugc|brand", re.I)
LAYER = re.compile(r"detail|skin|light|upscale|booster|enhancer|finish|polish|texture|grain|fix", re.I)


def load_labels():
    labels = {}
    for f in sorted(FUNNEL.glob("vision-labels*.json")):
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


def engine_entry(e, pulled_at):
    return {
        "id": f"engine-{e.get('task')}-{(e.get('name') or '').lower().replace(' ', '-')[:30]}",
        "kind": "engine",
        "our_name": None,
        "source_name": e.get("name"),
        "purpose": e.get("verdict_keep"),
        "composite": None, "tier": None,
        "visual_class": "n/a", "quality": None, "nsfw_bucket": None,
        "name_fit": None, "review_flag": False,
        "baseModel": None,
        "vram_class": e.get("vram_class"),
        "tradeoff": e.get("tradeoff"),
        "open_closed": e.get("open_closed"),
        "stats": {"downloadCount": None, "thumbsUpCount": None},
        "pulled_at": pulled_at,
        "preview": {}, "gallery": [], "stacks_on": [],
        "verdict_keep": e.get("verdict_keep"),
        "license_note": e.get("license_note"),
        "civitai_url": None, "model_url": e.get("source_url"),
        "requirements": {"models": [], "nodes": []},
        "heuristic": {"lane": f"models.json {e.get('task')}", "layer": None, "era": None},
    }


def merge_engines(buckets):
    models = ROOT / "data" / "models.json"
    if not models.exists():
        return
    d = json.loads(models.read_text())
    pulled_at = d.get("generated_at")
    for e in d.get("entries", []):
        if e.get("task") == "voice":
            buckets["SPEECH_VOICE"].append(engine_entry(e, pulled_at))


def apply_decisions(buckets):
    f = FUNNEL / "curation-decisions.json"
    if not f.exists():
        return
    dec = json.loads(f.read_text())
    applied = {"keep": 0, "cut": 0, "move-nsfw": 0}
    moved = []
    move_targets = {"move-nsfw": ("NSFW", moved), "move-layers": ("LAYERS", [])}
    for stage in list(buckets):
        kept = []
        for e in buckets[stage]:
            if e.get("heuristic", {}).get("moved_from"):
                kept.append(e)
                continue
            d = dec.get(str(e.get("id")))
            if not d or d.get("stage_from") != stage:
                kept.append(e)
                continue
            act = d.get("action")
            applied[act] = applied.get(act, 0) + 1
            if act == "keep":
                e["review_flag"] = False
                e["curated_by"] = d.get("reviewed_by")
                e["curated_note"] = d.get("reason")
                kept.append(e)
            elif act.startswith("move-"):
                target = {"move-nsfw": "NSFW", "move-layers": "LAYERS",
                          "move-persona": "PERSONA", "move-camera-angle": "CAMERA_ANGLE"}.get(act)
                if target:
                    e["heuristic"]["moved_from"] = stage
                    e["stacks_on"] = e.get("stacks_on") or (["PERSONA", "NSFW"] if target == "LAYERS" else [])
                    move_targets.setdefault(act, (target, []))[1].append(e)
        buckets[stage] = kept
    for act, (target, entries) in move_targets.items():
        if not entries:
            continue
        ids = {str(e.get("id")) for e in buckets[target]}
        buckets[target].extend(e for e in entries if str(e.get("id")) not in ids)
    print(f"curation decisions applied: {applied}", file=sys.stderr)


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
    merge_engines(buckets)
    apply_decisions(buckets)
    models = ROOT / "data" / "models.json"
    if models.exists():
        d = json.loads(models.read_text())
        buckets["MODELS"] = [engine_entry(e, d.get("generated_at")) for e in d.get("entries", [])]
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
