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
                if not e.get("purpose"):
                    e["purpose"] = d.get("reason")
                if not e.get("verdict_keep"):
                    e["verdict_keep"] = d.get("reason")
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


def merge_requirements(buckets):
    f = FUNNEL / "requirements.json"
    if not f.exists():
        return
    try:
        req = json.loads(f.read_text())
    except json.JSONDecodeError:
        return
    merged = 0
    for stage in buckets:
        for e in buckets[stage]:
            r = req.get(str(e.get("id")))
            if r and isinstance(r, dict) and not r.get("error") and not (e.get("requirements") or {}).get("models"):
                e["requirements"] = {"models": r.get("models") or [], "nodes": r.get("nodes") or []}
                merged += 1
    print(f"requirements merged: {merged} entries", file=sys.stderr)


def emit_cuts():
    f = FUNNEL / "curation-decisions.json"
    if not f.exists():
        return
    dec = json.loads(f.read_text())
    scored = json.loads((FUNNEL / "scored.json").read_text())
    names = {}
    for blob in scored["stages"].values():
        for e in blob["entries"]:
            names.setdefault(str(e.get("id")), e.get("name"))
    cuts = {}
    for cid, d in dec.items():
        if d.get("action") == "cut":
            cuts.setdefault(d.get("stage_from") or "?", []).append(
                {"id": cid, "name": names.get(cid, "?"), "reason": d.get("reason")})
    out = {"note": "manager curation cuts — the honesty panel",
           "stages": {k: {"count": len(v), "cuts": v} for k, v in sorted(cuts.items())}}
    (ROOT / "data" / "staged" / "cuts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"cuts.json: {sum(len(v) for v in cuts.values())} cuts across {len(cuts)} stages", file=sys.stderr)


def attach_downloads(buckets):
    f = FUNNEL / "all-candidates.json"
    if not f.exists():
        return
    try:
        cand = json.loads(f.read_text())
    except json.JSONDecodeError:
        return
    info = {}
    for e in cand.values():
        if not isinstance(e, dict):
            continue
        for v in e.get("versions") or []:
            fobj = next((x for x in (v.get("files") or []) if x.get("name")), None)
            if fobj and v.get("id"):
                info[str(e.get("id"))] = {"type": e.get("type"), "version_id": v.get("id"),
                                          "file": fobj.get("name"), "size_kb": fobj.get("sizeKB")}
                break
    folder_by_type = {"LORA": "models/loras/", "Checkpoint": "models/checkpoints/",
                      "DoRA": "models/loras/", "Workflows": "workflows/"}
    attached = 0
    for stage in buckets:
        for e in buckets[stage]:
            d = info.get(str(e.get("id")))
            if not d:
                continue
            e["type"] = e.get("type") or d["type"]
            e["version_url"] = f"https://civitai.com/models/{e.get('id')}?modelVersionId={d['version_id']}"
            size_mb = int((d["size_kb"] or 0) / 1024) or None
            dl = {"name": d["file"], "folder": folder_by_type.get(d["type"], "models/misc/"),
                  "url": f"https://civitai.com/api/download/models/{d['version_id']}"}
            if size_mb:
                dl["size_mb"] = size_mb
            e["download"] = dl
            if size_mb and not (e.get("requirements") or {}).get("models"):
                e["disk_mb"] = size_mb
            attached += 1
    print(f"downloads attached: {attached} entries", file=sys.stderr)


def polish_entries(buckets):
    """Owner pass m0335/m0337: photoreal ranks higher, tradeoff chips real,
    speech/ads purposes in human words (no jargon)."""
    fast_re = re.compile(r"turbo|lightning|lcm|hyper|distill|few.?step|gguf|accel", re.I)
    for stage in buckets:
        median_comp = None
        comps = sorted((e.get("composite") or 0) for e in buckets[stage] if e.get("composite") is not None)
        if comps:
            median_comp = comps[len(comps) // 2]
        for e in buckets[stage]:
            if e.get("visual_class") == "realism-photoreal" and e.get("composite") is not None:
                e["composite"] = round(e["composite"] + 12, 1)
            chips = []
            name = (e.get("source_name") or "")
            size = (e.get("download") or {}).get("size_mb")
            heavy_kind = e.get("type") in ("Checkpoint", "Workflows", "DoRA")
            if fast_re.search(name):
                chips.append("fastest")
            if e.get("vram_class") in ("6", "8") or (heavy_kind and size and size <= 1500):
                chips.append("low vram")
            if (e.get("quality") or 0) >= 8 and median_comp is not None and (e.get("composite") or 0) >= median_comp:
                chips.append("max quality")
            if chips:
                e["tradeoff"] = chips
            if stage == "SPEECH_VOICE" and e.get("kind") != "engine":
                e["purpose"] = "make a still photo of your persona talk — voice and lip movement"
                if fast_re.search(name) or "ltx" in name.lower() or "wan" in name.lower():
                    e["purpose"] += " (modern video model underneath)"
            if stage == "ADS":
                e["purpose"] = "your persona presenting a product — host style ad shot"
    print("polish: photoreal +12, tradeoff chips, human purposes applied", file=sys.stderr)


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
    merge_requirements(buckets)
    attach_downloads(buckets)
    polish_entries(buckets)
    emit_cuts()
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
