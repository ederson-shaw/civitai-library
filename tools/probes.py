#!/usr/bin/env python3
"""fail-loud behavior probes — hostile R1 #10 (nsfw clamp) + #15 (cdn sig expiry).

nsfw_clamp_probe: re-fetches nsfw candidates via /models/{id}?nsfw=true with
the key, asserts some version has nsfwLevel > 1. Clamp (all <=1 or 401/403)
-> loud stderr + data/nsfw_probe.json with details + garimpo exits 1.

cdn_sig_probe: re-fetches /models/{id} for persona candidates present in both
the previous run's file (stored urls) and this run's; a stored url that no
longer appears in any fresh version image = rotated (sigs expire, hotlinks
rot, cache policy needed).

IN:  candidate ids/files, api key, injected http_get.
OUT: data/nsfw_probe.json + data/cdn_probe.json + stderr verdicts.
"""
import json
import sys
import time
from pathlib import Path

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


def cdn_sig_probe(old_path, new_candidates, out_path, key, get):
    old_by_id = load_old_previews(old_path)
    comparable = [c for c in new_candidates if c.get("id") in old_by_id]
    checked = rotated = 0
    sample_old = sample_new = None

    for candidate in comparable[:5]:
        try:
            model = get(f"{MODELS_API}/{candidate.get('id')}", key)
        except RuntimeError as e:
            print(f"cdn probe: {e}, skipping model {candidate.get('id')}", file=sys.stderr)
            continue
        time.sleep(0.5)
        if model is None:
            continue
        old_url = old_by_id[candidate.get("id")]["preview"]["url_original"]
        fresh_urls = [i.get("url") for v in (model.get("modelVersions") or [])
                      for i in (v.get("images") or []) if i.get("url")]
        if sample_old is None and fresh_urls:
            sample_old, sample_new = old_url, fresh_urls[0]
        checked += 1
        if old_url not in fresh_urls:
            rotated += 1

    payload = {"checked": checked, "urls_rotated": rotated,
               "sample_old": sample_old, "sample_new": sample_new}
    out_path.write_text(json.dumps(payload, indent=2))
    verdict = "sigs expire, hotlinks rot, cache policy needed" if rotated \
        else "sigs stable across pulls"
    print(f"cdn probe: {rotated}/{checked} urls rotated — {verdict}", file=sys.stderr)
    return rotated
