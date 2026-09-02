#!/usr/bin/env python3
"""fail-loud behavior probes — hostile R1 #10 (nsfw clamp) + R1 #15 /
R2 #13 (cdn sig longevity: v0.1 compared same-session, proving nothing
about week-scale expiry).

nsfw_clamp_probe: re-fetches nsfw candidates via /models/{id}?nsfw=true with
the key, asserts some version has nsfwLevel > 1. Clamp (all <=1 or 401/403)
-> loud stderr + data/nsfw_probe.json with details + garimpo exits 1.

sig_recheck_probe: weekly sig-rotation check. With >= 2 snapshot dates,
compares every stored image url (preview + gallery) of entries present in
the two newest snapshots — a stored url that vanished by the newer date =
rotated (sigs expire, hotlinks rot, cache policy needed). With a single
date, falls back to candidates file vs fresh /models fetch for 10 ids
(same membership test as the v0.1 cdn probe, n=10).

IN:  candidate ids/files, api key, injected http_get.
OUT: data/nsfw_probe.json + data/cdn_probe.json + stderr verdicts.
"""
import json
import sys
import time
from pathlib import Path

from collectors import snapshot_dirs

MODELS_API = "https://civitai.com/api/v1/models"


def version_nsfw_peak(model):
    levels = [v.get("nsfwLevel") or 0 for v in (model.get("modelVersions") or [])]
    return max(levels, default=0)


def nsfw_clamp_probe(model_ids, out_path, key, get):
    details, levels, errors = [], [], []
    for model_id in model_ids[:10]:
        try:
            model = get(f"{MODELS_API}/{model_id}?nsfw=true", key)
        except RuntimeError as e:
            errors.append({"id": model_id, "error": str(e)})
            continue
        time.sleep(0.5)
        if model is None:
            errors.append({"id": model_id, "error": "fetch failed"})
            continue
        peak = version_nsfw_peak(model)
        levels.append(peak)
        details.append({"id": model_id, "nsfw_peak": peak})

    clamped = (levels and all(p <= 1 for p in levels)) or (not levels and errors)
    if clamped:
        reason = "every fetched nsfw model returned nsfwLevel<=1" if levels \
            else "all fetches failed or were auth-rejected (401/403)"
        payload = {"clamped": True, "checked": len(levels) + len(errors),
                   "reason": reason, "details": details + errors}
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print("NSFW CLAMPED — set account browsing level", file=sys.stderr)
        return True

    payload = {"clamped": False, "checked": len(levels)}
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"nsfw probe: {len(levels)} checked, no clamp", file=sys.stderr)
    return False


def load_old_previews(old_path):
    try:
        loaded = json.loads(Path(old_path).read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(loaded, list):
        return {}
    return {c.get("id"): c for c in loaded
            if ((c.get("preview") or {}).get("url_original"))}


def stored_urls(candidate):
    preview = candidate.get("preview") or {}
    urls = {preview.get("url_original"), preview.get("url_width450")}
    urls |= {g.get("url") for g in (candidate.get("gallery") or [])
             if isinstance(g, dict)}
    return {u for u in urls if u}


def recheck_snapshots(prev, last):
    checked = rotated = 0
    sample_old = sample_new = None
    for lane in sorted(prev.glob("candidates-*.json")):
        try:
            old_lane = json.loads(lane.read_text())
            new_lane = json.loads((last / lane.name).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not (isinstance(old_lane, list) and isinstance(new_lane, list)):
            continue
        new_by_id = {c.get("id"): c for c in new_lane}
        for old in old_lane:
            new = new_by_id.get(old.get("id"))
            if new is None:
                continue
            old_urls, new_urls = stored_urls(old), stored_urls(new)
            if not old_urls:
                continue
            checked += 1
            missing = old_urls - new_urls
            if missing:
                rotated += 1
                if sample_old is None:
                    sample_old = sorted(missing)[0]
                    sample_new = sorted(new_urls)[0] if new_urls else None
    return checked, rotated, sample_old, sample_new


def recheck_live(data_dir, key, get):
    old_by_id = load_old_previews(Path(data_dir) / "candidates-persona.json")
    checked = rotated = 0
    sample_old = sample_new = None
    for model_id in list(old_by_id)[:10]:
        try:
            model = get(f"{MODELS_API}/{model_id}", key)
        except RuntimeError as e:
            print(f"cdn probe: {e}, skipping model {model_id}", file=sys.stderr)
            continue
        time.sleep(0.5)
        if model is None:
            continue
        old_url = old_by_id[model_id]["preview"]["url_original"]
        fresh_urls = [i.get("url") for v in (model.get("modelVersions") or [])
                      for i in (v.get("images") or []) if i.get("url")]
        checked += 1
        if sample_old is None and fresh_urls:
            sample_old, sample_new = old_url, fresh_urls[0]
        if old_url not in fresh_urls:
            rotated += 1
    return checked, rotated, sample_old, sample_new


def sig_recheck_probe(data_dir, out_path, key, get):
    snaps = snapshot_dirs(data_dir)
    if len(snaps) >= 2:
        prev, last = snaps[-2], snaps[-1]
        across = f"{prev.name} -> {last.name}"
        checked, rotated, sample_old, sample_new = recheck_snapshots(prev, last)
    else:
        across = "live"
        checked, rotated, sample_old, sample_new = recheck_live(data_dir, key, get)

    payload = {"checked": checked, "urls_rotated": rotated,
               "compared_across": across,
               "sample_old": sample_old, "sample_new": sample_new}
    out_path.write_text(json.dumps(payload, indent=2))
    verdict = "sigs expire, hotlinks rot, cache policy needed" if rotated \
        else "sigs stable"
    print(f"cdn probe: {rotated}/{checked} urls rotated across {across} — {verdict}",
          file=sys.stderr)
    return rotated
