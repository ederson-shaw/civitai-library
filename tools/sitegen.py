#!/usr/bin/env python3
"""Build the static Civitai Field Guide site from the pulled candidate data.

The generator deliberately keeps the editorial data model small and explicit. It
does not call Civitai at runtime: every page is static, with the mature lane
loaded only after the user confirms the header gate.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import math
import re
import shutil
from pathlib import Path
from statistics import median
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
RESEARCH = ROOT / "research"

PULL_DATE = dt.date(2026, 9, 2)
TODAY = max(dt.date.today(), PULL_DATE)

LANE_LABELS = {
    "persona": "personas",
    "workflows": "ads",
    "nsfw": "mature",
}

OUTPUT_LABELS = {
    "portrait": "portrait",
    "full-body": "full-body",
    "reel": "motion",
    "image": "image",
    "video": "video",
    "audio": "audio",
    "voice": "voice",
    "character": "face consistency",
    "t2v": "text to video",
    "i2v-audio": "image to video + audio",
}

INTENTS = [
    {"id": "persona", "label": "build a persona", "task": "portrait"},
    {"id": "face", "label": "keep the same face", "task": "identity"},
    {"id": "ad", "label": "make an ad", "task": "motion"},
    {"id": "voice", "label": "add voice + speech", "task": "voice"},
]

SYNONYMS = {
    "same face": ["identity", "face consistency", "identity lock"],
    "identity lock": ["same face", "face consistency", "identity"],
    "face consistency": ["same face", "identity lock", "character consistency"],
    "character consistency": ["same face", "identity", "face lock"],
    "identity": ["same face", "face consistency"],
    "ad": ["campaign", "product ad", "motion"],
    "campaign": ["ad", "product ad", "motion"],
    "voice": ["speech", "narration", "tts", "audio"],
    "speech": ["voice", "dialogue", "lip sync"],
    "low vram": ["8 gb", "12 gb", "gpu"],
    "comfy": ["comfyui", "workflow", "nodes"],
    "workflow": ["comfyui", "pipeline", "nodes"],
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def jdump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[: eighty] if (eighty := 84) else value


def date_only(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def date_label(value: str | None) -> str:
    parsed = date_only(value)
    return parsed.strftime("%d %b %Y") if parsed else "date unavailable"


def compact_number(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}m".replace(".0m", "m")
    if number >= 1_000:
        return f"{number / 1_000:.1f}k".replace(".0k", "k")
    return str(int(number))


def parse_number(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return default
    match = re.search(r"\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group(0)) if match else default


def vram_number(value: object) -> int | None:
    if isinstance(value, dict):
        value = value.get("badge")
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else None


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def media_kind(url: str) -> str:
    return "video" if re.search(r"\.(mp4|webm|mov)(?:$|\?)", url, re.I) else "image"


def normalize_license(license_data: dict | None) -> list[str]:
    if not license_data:
        return ["license details unavailable"]
    pills = []
    commercial = license_data.get("allowCommercialUse") or []
    if commercial:
        pills.append("commercial: " + ", ".join(str(x).lower() for x in commercial[:3]))
    pills.append("credit required" if not license_data.get("allowNoCredit") else "credit optional")
    pills.append("derivatives allowed" if license_data.get("allowDerivatives") else "no derivatives")
    return pills


def load_source_lanes() -> tuple[dict[str, list[dict]], dict[str, dict]]:
    candidates = {}
    curations = {}
    for lane in ("persona", "workflows", "nsfw"):
        candidates[lane] = read_json(DATA / f"candidates-{lane}.json")
        curations[lane] = {str(x["id"]): x for x in read_json(RESEARCH / f"curation-draft-{lane}.json")}
    return candidates, curations


def choose_media(candidate: dict) -> list[dict]:
    gallery = candidate.get("gallery") or []
    selected = sorted(gallery, key=lambda item: (not bool(item.get("has_meta")),))[:6]
    media = []
    seen = set()
    for item in selected:
        url = item.get("url")
        if url and url not in seen:
            media.append({"url": url, "kind": media_kind(url), "has_meta": bool(item.get("has_meta"))})
            seen.add(url)
    preview = candidate.get("preview") or {}
    fallback = preview.get("url_width450") or preview.get("url_original")
    if fallback and fallback not in seen:
        media.insert(0, {"url": fallback, "kind": media_kind(fallback), "has_meta": False})
    return media[:6]


def archive_file(candidate: dict) -> dict | None:
    for version in candidate.get("versions") or []:
        for file_info in version.get("files") or []:
            if str(file_info.get("type", "")).lower() == "archive":
                return {
                    "name": file_info.get("name", "workflow archive"),
                    "download_url": version.get("downloadUrl"),
                    "version_id": version.get("id"),
                    "version_name": version.get("name"),
                }
    return None


def compute_anchors(items: list[dict]) -> dict:
    ratios = []
    downloads = []
    comments = []
    for item in items:
        stats = item.get("stats") or {}
        dl = parse_number(stats.get("downloadCount"))
        thumbs = parse_number(stats.get("thumbsUpCount"))
        ratios.append(thumbs / dl if dl else 0.0)
        downloads.append(dl)
        comments.append(parse_number(stats.get("commentCount")))
    return {
        "lane": items[0].get("lane") if items else "unknown",
        "p75_ratio": round(percentile(ratios, 0.75), 6),
        "p90_downloads": round(percentile(downloads, 0.90), 2),
        "p75_comments": round(percentile(comments, 0.75), 2),
        "median_comments": round(percentile(comments, 0.50), 2),
        "computed_at": PULL_DATE.isoformat(),
        "source": "current pull; anchors frozen until pull 4",
    }


def freshness_score(updated_at: str | None) -> int:
    parsed = date_only(updated_at)
    if not parsed:
        return 2
    age = max(0, (TODAY - parsed).days)
    if age <= 90:
        return 15
    if age <= 180:
        return 10
    if age <= 365:
        return 5
    return 2


def usage_score(value: object) -> tuple[int, bool, int | None]:
    if value is None or value == "":
        return 0, True, None
    text = str(value).strip().lower()
    if text == "100+":
        return 15, False, 100
    number = int(parse_number(text))
    if number <= 0:
        return 0, False, 0
    if number < 30:
        return 5, False, number
    if number < 100:
        return 10, False, number
    return 15, False, number


def stack_line(candidate: dict, draft: dict) -> str:
    typ = str(candidate.get("type", "")).lower()
    base = str(candidate.get("baseModel") or "base model")
    if "workflow" in typ:
        return f"{base} + workflow + optional tools"
    if "lora" in typ:
        return f"{base} + LoRA + upscale"
    return f"{base} checkpoint + identity lock + optional LoRA"


def task_values(draft: dict) -> list[str]:
    values = [str(x) for x in (draft.get("outputs") or [])]
    return values or ["image"]


def normalize_entry(candidate: dict, draft: dict, lane: str, anchors: dict) -> dict:
    stats_raw = candidate.get("stats") or {}
    pulled = stats_raw.get("pulled_at") or candidate.get("lastUpdated")
    latest = (candidate.get("versions") or [{}])[0]
    usage_raw = candidate.get("usage") or {}
    media = choose_media(candidate)
    usage_points, walk_pending, posted_est = usage_score(usage_raw.get("posted_images_est"))
    downloads = parse_number(stats_raw.get("downloadCount"))
    thumbs = parse_number(stats_raw.get("thumbsUpCount"))
    comments = parse_number(stats_raw.get("commentCount"))
    ratio = thumbs / downloads if downloads else 0.0
    ratio_weight = 15 if anchors["p75_comments"] == 0 else 10
    ratio_component = min(1.0, ratio / anchors["p75_ratio"]) * ratio_weight if anchors["p75_ratio"] else 0
    p90_dl = max(1.0, anchors["p90_downloads"])
    magnitude_component = min(1.0, math.log10(max(downloads, 1)) / math.log10(p90_dl)) * 10
    if anchors["p75_comments"] == 0:
        comments_component = 0
    elif comments >= anchors["p75_comments"]:
        comments_component = 5
    elif comments > anchors["median_comments"]:
        comments_component = 3
    else:
        comments_component = 0
    external_mentions = draft.get("external_mentions") or []
    external_score = 15 if len(external_mentions) >= 2 else 10 if external_mentions else 0
    completeness_axes = {
        "ran_it_or_confirmed_recipe": bool(draft.get("ran_it") or draft.get("confirmed_recipe")),
        "trigger_words": bool(draft.get("trigger_words")),
        "model_list": bool((draft.get("requirements") or {}).get("models")),
        "node_list": bool((draft.get("requirements") or {}).get("nodes")),
    }
    completeness_score = sum(2.5 for value in completeness_axes.values() if value)
    preview_walked = "meta_match" in usage_raw
    meta_match = bool(usage_raw.get("meta_match"))
    preview_score = 10 if preview_walked and meta_match else 0
    lane_fit = int(draft.get("lane_fit", 5))
    base_score = (
        ratio_component
        + magnitude_component
        + comments_component
        + usage_points
        + external_score
        + freshness_score(candidate.get("lastUpdated"))
        + completeness_score
        + preview_score
        + lane_fit
    )
    if walk_pending:
        base_score = base_score * 100 / 70
    if posted_est == 0 and comments == 0:
        base_score = min(base_score, 54.9)
    source_name = candidate.get("name") or "unnamed source"
    our_name = draft.get("our_name") or source_name
    slug = slugify(our_name)
    requirements = draft.get("requirements") or {}
    creator = candidate.get("creator") or {}
    return {
        "id": candidate["id"],
        "slug": slug,
        "lane": lane,
        "lane_label": LANE_LABELS[lane],
        "name": our_name,
        "original_name": source_name,
        "purpose": draft.get("purpose") or "A pulled candidate awaiting an editorial note.",
        "verdict_line": draft.get("verdict_line") or "The source is linked below while this recommendation is being verified.",
        "creator": {"username": creator.get("username", "unknown creator"), "href": creator.get("href")},
        "type": candidate.get("type", "unknown").lower(),
        "base_model": candidate.get("baseModel") or "base model not listed",
        "nsfwLevel": candidate.get("nsfwLevel", 0),
        "source_url": candidate.get("source_url"),
        "vram_badge": (draft.get("vram_badge") or {}).get("badge") if isinstance(draft.get("vram_badge"), dict) else draft.get("vram_badge") or "unlisted",
        "vram_basis": (draft.get("vram_badge") or {}).get("basis", "manual estimate; API has no vram field") if isinstance(draft.get("vram_badge"), dict) else "manual estimate; API has no vram field",
        "vram_confidence": (draft.get("vram_badge") or {}).get("confidence", "low") if isinstance(draft.get("vram_badge"), dict) else "low",
        "locks": draft.get("locks") or [],
        "inputs": draft.get("inputs") or [],
        "outputs": task_values(draft),
        "audio": draft.get("audio") or [],
        "duration": draft.get("duration"),
        "requirements": requirements,
        "requirements_ready": False,
        "requirements_summary": "requirements being verified",
        "confidence": draft.get("confidence", "low"),
        "curated_by": draft.get("curated_by", "not recorded"),
        "curation_notes": draft.get("curation_notes", "No curation note was supplied."),
        "stack": stack_line(candidate, draft),
        "stats": {
            "downloads": {"value": int(downloads), "window": "all-time", "pulled_at": pulled},
            "thumbs": {"value": int(thumbs), "window": "all-time", "pulled_at": pulled},
            "comments": {"value": int(comments), "window": "all-time", "pulled_at": pulled},
        },
        "usage": {
            "posted_images_est": usage_raw.get("posted_images_est"),
            "reactions_sum": usage_raw.get("reactions_sum", 0),
            "meta_match": meta_match,
            "walk_pending": walk_pending,
        },
        "media": media,
        "preview_gated": int(candidate.get("nsfwLevel", 0)) >= 8,
        "preview_mismatch_badge": bool(media and preview_walked and not meta_match),
        "preview_honesty": "metadata matched" if preview_walked and meta_match else "unverified",
        "latest_version": {
            "id": latest.get("id"),
            "name": latest.get("name") or "version not listed",
            "base_model": latest.get("baseModel") or candidate.get("baseModel"),
            "updated_at": latest.get("updatedAt") or candidate.get("lastUpdated"),
            "download_url": latest.get("downloadUrl"),
        },
        "archive": archive_file(candidate),
        "license_pills": normalize_license(candidate.get("license")),
        "verification": {
            "tested_by_us": bool(draft.get("verification", {}).get("tested_by_us")),
            "date": draft.get("verification", {}).get("date"),
            "proof_images": draft.get("verification", {}).get("proof_images", []),
        },
        "provenance": {
            "creator": creator.get("username", "unknown creator"),
            "version_id": latest.get("id"),
            "checked_at": pulled,
        },
        "status": {
            "removed": False,
            "needs_retest": True,
            "changelog": draft.get("changelog", []),
        },
        "score_components": {
            "ratio": round(ratio_component, 2),
            "magnitude": round(magnitude_component, 2),
            "comments": round(comments_component, 2),
            "usage": usage_points,
            "external": external_score,
            "freshness": freshness_score(candidate.get("lastUpdated")),
            "completeness": completeness_score,
            "preview_honesty": preview_score,
            "lane_fit": lane_fit,
            "ratio_eligible": downloads >= 500,
            "completeness_axes": completeness_axes,
        },
        "composite": round(max(0.0, min(100.0, base_score)), 2),
        "trend": None,
        "stats_note": "no delta history",
    }


def assign_ranks(items: list[dict]) -> None:
    items.sort(key=lambda item: (-item["composite"], -item["stats"]["downloads"]["value"], item["name"]))
    n = len(items)
    s_count = max(1, round(0.10 * n)) if n >= 5 else 1
    a_count = max(1, round(0.25 * n))
    b_count = max(1, round(0.40 * n))
    for index, item in enumerate(items):
        item["rank"] = index + 1
        item["rank_band"] = {
            "s": s_count,
            "a_end": s_count + a_count,
            "b_end": s_count + a_count + b_count,
        }
        external_gate = item["score_components"]["external"] > 0
        curator_verified = bool(item["curated_by"] and item["curated_by"] != "not recorded")
        if index < s_count and item["composite"] >= 70 and external_gate and curator_verified:
            tier = "S"
        elif index < s_count + a_count and item["composite"] >= 55:
            tier = "A"
        elif index < s_count + a_count + b_count and item["composite"] >= 35:
            tier = "B"
        else:
            tier = "C"
        if item["usage"]["posted_images_est"] in (0, "0") and item["stats"]["comments"]["value"] == 0:
            tier = min(tier, "B", key=lambda x: "SABC".index(x))
        item["tier"] = tier
        item["tier_note"] = {
            "S": "top lane band, 70+ composite, outside evidence, and curator verified",
            "A": "strong lane fit with a 55+ composite floor",
            "B": "useful shortlist entry; verify the recipe before production",
            "C": "kept for coverage, but not a first pick",
        }[tier]


def build_models() -> list[dict]:
    """Transcribe the live snapshot tables into a modest, auditable model tab."""
    rows = [
        ("image", 1, "GPT Image 2", "#1 AR photorealistic · 1380±6", "Arena photorealistic", "2026-08-25", "Proprietary", "cloud only", "API", "best prompt adherence and text-in-image; expensive", False, "cloud / no local folder", []),
        ("image", 2, "MAI-Image-2.6-Preview", "#3 AR photorealistic · 1324", "Arena photorealistic", "2026-08-25", "Proprietary", "cloud only", "API", "new and strong; API access is still coming", True, "cloud / no local folder", ["API access"]),
        ("image", 3, "Ideogram 4.0", "#1 open weights on AA · 1219", "Artificial Analysis image", "2026-08", "terms open", "native", "OPEN", "the open-weight image pick; local VRAM is still unverified", False, "models/checkpoints/", ["VRAM", "license terms"]),
        ("face-consistency", 1, "PuLID-FLUX", "community consensus proxy", "community consensus", "2026-06", "check repo license", "extension", "8 GB class", "tight face lock for Flux without training", False, "models/pulid/", ["blind benchmark"]),
        ("face-consistency", 2, "InstantID", "community consensus proxy", "community consensus", "2026-06", "Apache 2.0", "extension", "8 GB class", "high identity fidelity on SDXL; can over-anchor prompts", True, "models/instantid/", ["blind benchmark"]),
        ("face-consistency", 3, "Character LoRA", "production practice ceiling", "community consensus", "2026-06", "varies by training set", "native", "8–12 GB class", "highest ceiling when you can train on 50+ images", True, "models/loras/", ["single benchmark", "license"]),
        ("t2v", 1, "Gemini Omni 1.1 Flash", "#1 AR t2v · 1515±16", "Arena text-to-video", "2026-08-25", "Proprietary", "cloud", "API", "current AR quality leader; contested against Wan 3.0 on AA", True, "cloud / no local folder", []),
        ("t2v", 2, "Wan 3.0", "#1 AA with audio · 1242", "Artificial Analysis video", "2026-08", "Proprietary", "cloud", "API", "audio board leader; open-weights status unconfirmed", True, "cloud / no local folder", ["open-weights status"]),
        ("t2v", 3, "MiniMax H3", "#6 AR · 1460; #4 AA audio · 1227", "Arena + Artificial Analysis", "2026-08-25", "community license", "native", "12 GB floor / 24 GB comfortable", "best local/open video option; territorial license warning", False, "models/diffusion_models/", ["license territory"]),
        ("t2v", 4, "LTX-2.5 Pro", "open-weights AA list", "Artificial Analysis video", "2026-08", "ltx-community", "native", "unverified", "fast local audio-to-video path; exact VRAM is open", True, "models/checkpoints/", ["VRAM"]),
        ("i2v-audio", 1, "MiniMax H3", "#1 AR i2v · 1494±6", "Arena image-to-video", "2026-08-25", "community license", "native", "12 GB floor / 24 GB comfortable", "strongest local same-pass audio workflow; territory restrictions apply", False, "models/diffusion_models/", ["license territory"]),
        ("i2v-audio", 2, "Seedance 2.0", "#4 AR i2v · 1477", "Arena image-to-video", "2026-08-25", "Proprietary", "cloud", "API", "best defined-speech path when uploaded audio is the input", False, "cloud / no local folder", []),
        ("i2v-audio", 3, "Kling 3.0", "#17 AR i2v · 1356", "Arena image-to-video", "2026-08-25", "Proprietary", "cloud", "API", "voice binding is useful; overall audio ordering is contested", True, "cloud / no local folder", ["voice quality"]),
        ("voice", 1, "Realtime TTS-2", "#1 controlled voice · 1123", "Artificial Analysis controlled voice", "2026-08", "Proprietary", "API", "API", "current cloning-board leader for fast voice control", False, "cloud / no local folder", []),
        ("voice", 2, "Sonic 3.6", "#1 provider voice · 1282; #2 cloning · 1119", "Artificial Analysis TTS", "2026-08", "Proprietary", "API", "API", "best provider-voice score in this snapshot", False, "cloud / no local folder", []),
        ("voice", 3, "Breeze TTS 2", "#1 open weights · 1212 provider", "Artificial Analysis provider voice", "2026-08", "license terms open", "OPEN", "unverified", "the open local pick until license and VRAM are checked", True, "models/tts/", ["license", "VRAM", "ComfyUI path"]),
        ("voice", 4, "Kokoro 82M", "Elo ~1056", "Artificial Analysis controlled voice", "2026-08", "Apache 2.0", "extension", "CPU", "small and practical; do not use the stale tts.ai #1 ordering", False, "models/tts/", []),
    ]
    result = []
    for task, rank, name, position, board, date, license_name, comfy, vram, verdict, contested, folder, unverified in rows:
        result.append({
            "task": task,
            "rank": rank,
            "name": name,
            "position": position,
            "board": board,
            "date": date,
            "license": license_name,
            "comfyui": comfy,
            "vram_badge": vram,
            "our_verdict": verdict,
            "contested": contested,
            "target_folder_hint": folder,
            "unverified_fields": unverified,
            "source_url": "https://arena.ai/leaderboard/image-to-video" if task == "i2v-audio" else "https://artificialanalysis.ai",
        })
    return result


def base_path(root: str, title: str, body: str, attrs: str = "") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="The Civitai Field Guide — curated LoRAs and ComfyUI workflows for real production work.">
  <title>{esc(title)} · civitai-library</title>
  <link rel="stylesheet" href="{root}assets/style.css">
</head>
<body {attrs} data-site-root="{root}">
  {header(root)}
  {body}
  {mature_dialog()}
  <dialog class="lightbox" id="lightbox" aria-label="image viewer">
    <button class="lightbox-close" type="button" data-lightbox-close aria-label="close viewer">×</button>
    <button class="lightbox-arrow lightbox-prev" type="button" data-lightbox-prev aria-label="previous image">←</button>
    <div class="lightbox-stage"><img alt="" width="900" height="1200" loading="lazy" data-lightbox-image><video width="900" height="1200" muted loop playsinline controls data-lightbox-video></video></div>
    <button class="lightbox-arrow lightbox-next" type="button" data-lightbox-next aria-label="next image">→</button>
    <p class="lightbox-caption" data-lightbox-caption></p>
  </dialog>
  <div class="toast" role="status" aria-live="polite" data-toast></div>
  <noscript><div class="noscript-note">this guide needs a small amount of javascript for search, filters, and the mature-mode confirmation.</div></noscript>
  <script src="{root}assets/app.js" defer></script>
</body>
</html>'''


def header(root: str) -> str:
    return f'''<header class="site-header">
  <a class="brand" href="{root}"><span>civitai-library</span><small>the field guide</small></a>
  <nav class="main-nav" aria-label="main navigation">
    <a href="{root}personas/">personas</a>
    <a href="{root}ads/">ads</a>
    <a href="{root}models/">models</a>
    <a href="{root}guide/">guide</a>
  </nav>
  <div class="header-tools">
    <form class="site-search" data-search-form>
      <label class="sr-only" for="site-search-input">search the field guide</label>
      <input id="site-search-input" type="search" placeholder="search outcomes, locks, creators" autocomplete="off" data-search-input>
      <button type="submit" aria-label="search">↗</button>
    </form>
    <button class="mature-toggle" type="button" data-mature-toggle aria-pressed="false"><span class="toggle-dot"></span> mature lane <span class="toggle-state">locked</span></button>
    <button class="reset-mature" type="button" data-reset-mature>reset to sfw</button>
  </div>
</header>'''


def mature_dialog() -> str:
    return '''<dialog class="mature-dialog" id="mature-dialog" aria-labelledby="mature-dialog-title">
  <form method="dialog">
    <p class="eyebrow">before you continue</p>
    <h2 id="mature-dialog-title">mature metadata, no explicit previews</h2>
    <p>this lane contains workflows intended for adult content. this site shows metadata and links only. explicit previews remain on the original source.</p>
    <label class="remember-choice"><input type="checkbox" data-remember-mature> remember mature mode on this device for 30 days</label>
    <small>shared device? leave this unchecked and the choice lasts for this session only.</small>
    <div class="dialog-actions">
      <button type="button" class="button quiet" data-mature-cancel>keep sfw mode</button>
      <button type="button" class="button coral" data-mature-confirm>continue to mature metadata</button>
    </div>
  </form>
</dialog>'''


def media_markup(item: dict, root: str, detail: bool = False) -> str:
    url = item.get("url")
    if not url:
        return '<div class="preview-placeholder"><span>preview unavailable</span></div>'
    gated = item.get("gated", False)
    attr = f'data-src="{esc(url)}"' if gated else f'src="{esc(url)}"'
    class_name = "media blurred" if gated else "media"
    alt = "mature workflow preview hidden" if gated else "curated field guide preview"
    if item.get("kind") == "video":
        return f'<video class="{class_name}" {attr} width="450" height="600" muted loop playsinline preload="metadata" aria-label="{alt}"></video>'
    return f'<img class="{class_name}" {attr} width="450" height="600" loading="lazy" alt="{alt}">' 


def card_media(entry: dict, root: str) -> str:
    if not entry.get("media"):
        return '<div class="preview-placeholder"><span>preview unavailable</span></div>'
    item = dict(entry["media"][0])
    item["gated"] = entry.get("preview_gated", False)
    cover = '<span class="mature-cover">preview hidden · unlock in header</span>' if item["gated"] else ""
    return media_markup(item, root) + cover


def stat_markup(entry: dict) -> str:
    stats = entry["stats"]
    return f'''<ul class="stats-trio" aria-label="community stats">
  <li><strong>{compact_number(stats["downloads"]["value"])}</strong><span>downloads</span><small>pulled {date_label(stats["downloads"]["pulled_at"])}</small></li>
  <li><strong>{compact_number(stats["thumbs"]["value"])}</strong><span>thumbs</span><small>pulled {date_label(stats["thumbs"]["pulled_at"])}</small></li>
  <li><strong>{compact_number(stats["comments"]["value"])}</strong><span>comments</span><small>pulled {date_label(stats["comments"]["pulled_at"])}</small></li>
</ul>'''


def card_markup(entry: dict, root: str, view_rank: int | None = None, mature: bool = False) -> str:
    outputs = " · ".join(OUTPUT_LABELS.get(value, value.replace("-", " ")) for value in entry["outputs"][:3])
    locks = " · ".join(entry["locks"][:3]) if entry["locks"] else "no explicit lock"
    rank_label = f"#{entry['rank']} in {entry['lane_label']}" if view_rank is None else f"#{view_rank} in view · #{entry['rank']} in {entry['lane_label']}"
    href = f"{root}{'mature/entries/' if mature else 'entries/'}{quote(entry['slug'])}/"
    req = entry["requirements"]
    req_count = f"{len(req.get('models') or [])} models · {len(req.get('nodes') or [])} nodes" if req else "requirements being verified"
    data_attrs = f'data-entry-id="{entry["id"]}" data-entry-slug="{esc(entry["slug"])}" data-composite="{entry["composite"]}" data-vram="{esc(vram_number(entry["vram_badge"]) or "")}" data-base="{esc(entry["base_model"])}" data-tasks="{esc(",".join(entry["outputs"]))}" data-freshness="{esc(entry["latest_version"]["updated_at"] or "")}" data-saved-id="{entry["id"]}"'
    return f'''<article class="entry-card tier-{entry["tier"].lower()}" {data_attrs}>
  <a class="card-preview" href="{href}" aria-label="open {esc(entry['name'])}">{card_media(entry, root)}<span class="preview-corner">{esc(entry["type"])}</span></a>
  <div class="card-copy">
    <div class="rank-row"><span class="tier-badge" title="{esc(entry['tier_note'])}">{entry["tier"]}</span><span class="rank-label">{rank_label}</span><span class="score">{entry["composite"] / 10:.1f} / 10</span></div>
    <h3><a href="{href}">{esc(entry["name"])}</a></h3>
    <p class="purpose">{esc(entry["purpose"])}</p>
    <p class="card-meta"><span>{esc(entry["type"])}</span><span>{esc(entry["base_model"])}</span><span>{esc(entry["vram_badge"])} gb <em>est.</em></span></p>
    <p class="stack-formula"><span>stack</span> {esc(entry["stack"])}</p>
    {stat_markup(entry)}
    <div class="chip-row"><span class="chip">{esc(locks)}</span><span class="chip">{esc(outputs)}</span>{'<span class="chip warning">preview unverified</span>' if entry['preview_mismatch_badge'] else ''}</div>
    <div class="card-footer"><span class="requirements-badge">{esc(req_count if entry['type'] == 'workflows' else entry['confidence'] + ' confidence')}</span><button class="save-button" type="button" data-save-entry="{entry['id']}" aria-label="save {esc(entry['name'])}">♡</button></div>
  </div>
</article>'''


def filter_options(entries: list[dict], group: str) -> list[tuple[str, str]]:
    if group == "vram":
        return [(str(value), f"{value} gb") for value in (8, 12, 16, 24)]
    if group == "base":
        values = sorted({entry["base_model"] for entry in entries})
        return [(value, value) for value in values]
    if group == "task":
        values = sorted({task for entry in entries for task in entry["outputs"]})
        return [(value, OUTPUT_LABELS.get(value, value.replace("-", " "))) for value in values]
    if group == "freshness":
        return [("90", "last 90 days"), ("180", "last 180 days"), ("365", "last year")]
    return []


def filter_bar(entries: list[dict], skeleton: bool = False) -> str:
    groups = [("vram", "vram", "est."), ("base", "base model", ""), ("task", "output-task", ""), ("freshness", "freshness", "")]
    options_html = []
    for key, label, suffix in groups:
        options = filter_options(entries, key) if not skeleton else filter_options([], key)
        if skeleton and key == "base":
            options = []
        chips = '<button type="button" class="filter-choice active" data-filter-group="%s" data-filter-value="all">all <span class="chip-count">%s</span></button>' % (key, len(entries) if not skeleton else "—")
        for value, visible in options:
            count = sum(1 for entry in entries if value in [str(vram_number(entry["vram_badge"]))] if key == "vram") if key == "vram" else len(entries)
            if key == "task":
                count = sum(1 for entry in entries if value in entry["outputs"])
            if key == "base":
                count = sum(1 for entry in entries if entry["base_model"] == value)
            if key == "freshness":
                updated = date_only(entry_date) if (entry_date := "") else None
                count = len(entries)
            chips += f'<button type="button" class="filter-choice" data-filter-group="{esc(key)}" data-filter-value="{esc(value)}">{esc(visible)} <span class="chip-count">{count}</span></button>'
        options_html.append(f'<div class="filter-group" data-filter-group-wrap="{key}"><span class="filter-label">{esc(label)} {esc(suffix)}</span><div class="filter-choices">{chips}</div></div>')
    more = '''<div class="more-filters" data-more-filters hidden>
      <div class="filter-group"><span class="filter-label">type</span><div class="filter-choices"><button type="button" class="filter-choice" data-filter-group="type" data-filter-value="lora">LoRA <span class="chip-count">—</span></button><button type="button" class="filter-choice" data-filter-group="type" data-filter-value="workflows">workflow <span class="chip-count">—</span></button><button type="button" class="filter-choice" data-filter-group="type" data-filter-value="checkpoint">checkpoint <span class="chip-count">—</span></button></div></div>
      <div class="filter-group"><span class="filter-label">inputs</span><div class="filter-choices"><button type="button" class="filter-choice" data-filter-group="inputs" data-filter-value="image">image <span class="chip-count">—</span></button><button type="button" class="filter-choice" data-filter-group="inputs" data-filter-value="text">text <span class="chip-count">—</span></button></div></div>
      <div class="filter-group"><span class="filter-label">locks</span><div class="filter-choices"><button type="button" class="filter-choice" data-filter-group="locks" data-filter-value="identity">identity <span class="chip-count">—</span></button><button type="button" class="filter-choice" data-filter-group="locks" data-filter-value="scene">scene <span class="chip-count">—</span></button></div></div>
      <div class="filter-group"><span class="filter-label">duration / audio</span><div class="filter-choices"><button type="button" class="filter-choice" data-filter-group="duration" data-filter-value="has">has duration <span class="chip-count">—</span></button><button type="button" class="filter-choice" data-filter-group="audio" data-filter-value="has">audio req. <span class="chip-count">—</span></button></div></div>
    </div>'''
    return f'''<section class="filter-shell" aria-label="filter results" data-filter-shell>
      <div class="filter-bar">{"".join(options_html)}<button class="more-button" type="button" data-more-toggle aria-expanded="false">+ more</button><div class="sort-toggle" role="group" aria-label="sort"><span>sort</span><button type="button" class="sort-choice active" data-sort-choice="proven">proven</button><button type="button" class="sort-choice" data-sort-choice="latest">latest</button></div></div>{more}
    </section>'''


def tier_sections(entries: list[dict], root: str, mature: bool = False) -> str:
    sections = []
    for tier in "SABC":
        tier_entries = [entry for entry in entries if entry["tier"] == tier]
        if not tier_entries:
            if tier == "S":
                sections.append('<section class="tier-band empty-band"><div class="band-heading"><span class="band-index">s</span><div><h2>s tier</h2><p>s requires outside evidence plus a confirmed recipe.</p></div></div><div class="empty-inline">no s tier is published in this pull yet.</div></section>')
            continue
        cards = "".join(card_markup(entry, root, mature=mature) for entry in tier_entries)
        sections.append(f'''<section class="tier-band" data-tier-band="{tier.lower()}"><div class="band-heading"><span class="band-index">{tier.lower()}</span><div><h2>{tier} tier</h2><p>{esc(tier_entries[0]['tier_note'])}</p></div><span class="band-count">{len(tier_entries)} entries</span></div><div class="entry-grid">{cards}</div></section>''')
    return "".join(sections)


def lane_page(lane: str, entries: list[dict], root: str) -> str:
    title = LANE_LABELS[lane]
    intro = {
        "persona": "realistic faces, styles, and identity locks for social content",
        "workflows": "the full path from a finished frame to motion, voice, and publish",
        "nsfw": "adult-content metadata, with original-source links and no explicit previews here",
    }[lane]
    if lane == "nsfw":
        body = f'''<main class="page-shell mature-route" data-lane="mature" data-mature-route>
  <section class="lane-hero"><p class="eyebrow">lane / mature</p><h1>adult metadata, handled plainly.</h1><p>{intro}. confirm the header toggle to load this lane; until then, nothing from it is requested.</p><div class="gate-callout"><span class="gate-mark">18+</span><span>metadata and links only · explicit previews stay on the original source</span></div></section>
  <div class="mature-skeleton" data-mature-skeleton aria-live="polite"><div class="skeleton-line wide"></div><div class="skeleton-line"></div><div class="skeleton-grid"><i></i><i></i><i></i></div><p>mature metadata is locked until you confirm above.</p></div>
  <div class="mature-loaded" data-mature-loaded hidden>{filter_bar([], skeleton=True)}<div id="lane-results" class="tier-results"></div></div>
</main>'''
    else:
        body = f'''<main class="page-shell" data-lane="{lane}">
  <section class="lane-hero"><p class="eyebrow">lane / {title}</p><h1>{title}, curated around the outcome.</h1><p>{intro}. every rank is local to this lane; the score is secondary to the editorial verdict.</p><div class="lane-meta"><span>{len(entries)} visible entries</span><span>pulled {PULL_DATE.strftime('%d %b %Y')}</span><span>first pull · no delta history</span></div></section>
  {filter_bar(entries)}
  <div id="lane-results" class="tier-results">{tier_sections(entries, root)}</div>
</main>'''
    attrs = 'data-page="lane" data-lane="mature" data-mature-route' if lane == "nsfw" else f'data-page="lane" data-lane="{lane}"'
    return base_path(root, title, body, attrs)


def home_page(lanes: dict[str, list[dict]], root: str) -> str:
    top_blocks = []
    for lane in ("persona", "workflows", "nsfw"):
        if lane == "nsfw":
            top_blocks.append('''<a class="lane-card mature-card" href="./mature/" data-mature-link><span class="lane-number">03</span><h3>mature metadata</h3><p>adult-content notes, dependency paths, and honest source links.</p><span class="lane-link">unlock the lane ↗</span></a>''')
            continue
        entries = lanes[lane][:3]
        cards = "".join(card_markup(entry, root) for entry in entries)
        top_blocks.append(f'<section class="home-lane"><div class="home-lane-head"><span class="lane-number">0{"1" if lane == "persona" else "2"}</span><div><p class="eyebrow">lane / {LANE_LABELS[lane]}</p><h2>{"realistic personas" if lane == "persona" else "ad pipelines"}</h2></div><a href="{root}{LANE_LABELS[lane]}/">see the lane ↗</a></div><div class="entry-grid home-grid">{cards}</div></section>')
    fresh = sorted([entry for lane in ("persona", "workflows") for entry in lanes[lane]], key=lambda item: item["latest_version"]["updated_at"] or "", reverse=True)[:4]
    fresh_cards = "".join(card_markup(entry, root) for entry in fresh)
    body = f'''<main class="home-shell" data-home>
  <section class="home-hero">
    <div class="hero-copy"><p class="eyebrow">civitai-library / field guide v1</p><h1>build a consistent AI persona, then turn it into an ad.</h1><p class="hero-dek">a hand-curated shortlist of LoRAs and ComfyUI workflows. choose the result first. we explain the rest.</p><div class="hero-actions"><a class="button cobalt" href="{root}personas/">create a persona</a><a class="button outline" href="{root}ads/">make an ad</a><a class="text-link" href="{root}mature/" data-mature-link>explore mature metadata ↗</a></div></div>
    <aside class="hero-note"><span class="note-pin">editor’s note</span><p>the useful question is not “what is popular?” it is “what survives the next shot?”</p><small>ranks use lane-local anchors from the current pull. hardware is an estimate, never a hidden score input.</small></aside>
  </section>
    <section class="search-stage"><div><p class="eyebrow">search by the thing you need to make</p><h2>say it like a person.</h2></div><form class="big-search" data-search-form><label class="sr-only" for="home-search">search all sfw lanes</label><input id="home-search" data-search-input type="search" placeholder="try “same face”, “12 gb video”, or “voice”"><select class="search-scope" data-search-scope aria-label="search scope"><option value="all-sfw">all sfw</option><option value="lane">this lane</option><option value="saved">saved</option><option value="mature" disabled>mature · unlock first</option></select><button class="button coral" type="submit">find a stack ↗</button></form><div class="intent-row">{"".join(f'<button type="button" class="intent-chip" data-query="{esc(item["label"])}">{esc(item["label"])} <span>↗</span></button>' for item in INTENTS)}</div><div class="interpretation" data-interpretation hidden></div><div class="recent-searches" data-recent-searches hidden></div><div class="search-results" data-search-results></div></section>
  <section class="start-strip"><div><p class="eyebrow">start here</p><h2>one minute to your first import.</h2></div><div class="start-steps"><span><b>01</b> choose an outcome</span><span><b>02</b> pick a tested stack</span><span><b>03</b> drag JSON into ComfyUI</span></div><a class="button acid" href="{root}guide/">take the one-minute route ↗</a></section>
  <section class="home-lanes"><p class="eyebrow">three working lanes</p>{"".join(top_blocks)}</section>
  <section class="fresh-section"><div class="section-head"><div><p class="eyebrow">fresh + proven</p><h2>recently checked against the pull.</h2></div><span class="quiet-note">newest sort is explicit; it never replaces proven silently.</span></div><div class="entry-grid home-grid">{fresh_cards}</div></section>
</main>'''
    return base_path(root, "the field guide", body, 'data-page="home"')


def requirements_markup(entry: dict) -> str:
    req = entry.get("requirements") or {}
    models = req.get("models") or []
    nodes = req.get("nodes") or []
    model_rows = []
    for model in models:
        if isinstance(model, str):
            model_rows.append(f'<li><strong>{esc(model)}</strong><span>folder path not listed</span></li>')
        else:
            model_rows.append(f'<li><strong>{esc(model.get("our_ref", "model"))}</strong><span>{esc(model.get("folder", "folder path not listed"))}</span></li>')
    node_rows = [f'<li><strong>{esc(node.get("name", "custom node"))}</strong><span>Manager: {esc(node.get("manager_search", "search this exact name"))}</span></li>' for node in nodes]
    if not model_rows:
        model_rows.append('<li><strong>no model manifest pulled</strong><span>requirements being verified</span></li>')
    if not node_rows:
        node_rows.append('<li><strong>no custom nodes listed</strong><span>requirements being verified</span></li>')
    archive_link = ''
    if entry.get("archive") and entry["archive"].get("download_url"):
        archive_link = f'<a class="source-download" href="{esc(entry["archive"]["download_url"])}" target="_blank" rel="noreferrer">download source archive · {esc(entry["archive"].get("version_name", "pinned version"))} ↗</a>'
    return f'''<div class="requirements-status"><span class="status-dot"></span>{esc(entry["requirements_summary"])}<span class="confidence">{esc(entry["confidence"])} confidence</span></div>
    <div class="requirements-columns"><div><h3>models + folder paths</h3><ul class="requirement-list">{"".join(model_rows)}</ul></div><div><h3>nodes + manager search</h3><ul class="requirement-list">{"".join(node_rows)}</ul></div></div>
    <p class="recovery-note"><strong>recovery:</strong> missing checkpoint? put it in the folder above, then refresh.</p>{archive_link}'''


def gallery_markup(entry: dict) -> str:
    if not entry.get("media"):
        return '<div class="gallery-empty">no gallery was pulled. the source preview is unavailable right now.</div>'
    pieces = []
    for index, media in enumerate(entry["media"]):
        item = dict(media)
        item["gated"] = entry.get("preview_gated", False)
        pieces.append(f'<button type="button" class="gallery-thumb {"active" if index == 0 else ""}" data-gallery-index="{index}" aria-label="open preview {index + 1}">{media_markup(item, "./")}</button>')
    first = dict(entry["media"][0])
    first["gated"] = entry.get("preview_gated", False)
    return f'<div class="gallery-main" data-gallery-main data-gallery-index="0" data-gallery-items="{esc(jdump(entry["media"]))}">{media_markup(first, "./", detail=True)}<button class="gallery-open" type="button" data-lightbox-open aria-label="open gallery full screen">open gallery ↗</button></div><div class="gallery-thumbs">{"".join(pieces)}</div>'


def detail_page(entry: dict, root: str, mature: bool = False) -> str:
    if mature:
        body = f'''<main class="page-shell mature-detail" data-mature-detail data-entry-slug="{esc(entry["slug"])}"><div class="skeleton-detail"><p class="eyebrow">mature metadata</p><h1>confirm mature mode to load this entry.</h1><p>the entry payload is fetched only after the header confirmation.</p><div class="skeleton-grid"><i></i><i></i></div></div><div id="detail-app" hidden></div></main>'''
        return base_path(root, "mature entry", body, f'data-page="mature-detail" data-mature-detail="{esc(entry["slug"])}"')
    handoff = "ads" if entry["lane"] == "persona" else "guide"
    handoff_label = "use this persona in campaign lab" if entry["lane"] == "persona" else "follow the one-minute route"
    verified = "tested by us" if entry["verification"]["tested_by_us"] else "not tested by us yet"
    proof_images = entry["verification"].get("proof_images") or []
    png = f'<a class="button outline" href="{esc(proof_images[0])}" target="_blank" rel="noreferrer">open proof PNG ↗</a>' if proof_images and entry["verification"]["tested_by_us"] else ""
    gallery = gallery_markup(entry)
    stats = entry["stats"]
    storyboard = ""
    if entry["type"] == "workflows":
        storyboard = '<section class="storyboard"><p class="eyebrow">pipeline view</p><div class="storyboard-row"><span>still</span><i>→</i><span>motion</span><i>→</i><span>audio</span><i>→</i><span>voice</span><i>→</i><span>publish</span></div></section>'
    workflow_href = f'{root}mature/workflows/{quote(entry["slug"])}.json' if mature else f'{root}workflows/{quote(entry["slug"])}.json'
    body = f'''<main class="page-shell detail-shell" data-page="detail" data-entry-id="{entry["id"]}">
  <div class="breadcrumb"><a href="{root}{entry["lane_label"]}/">{entry["lane_label"]}</a><span>/</span><span>entry</span></div>
  <section class="detail-heading"><div><p class="eyebrow">{entry["lane_label"]} / {entry["type"]}</p><h1>{esc(entry["name"])}</h1><p class="alias">source name: <span>{esc(entry["original_name"])}</span> · by <a href="{esc(entry['creator'].get('href') or '#')}" target="_blank" rel="noreferrer">{esc(entry['creator'].get('username'))} ↗</a></p></div><div class="detail-rank"><span class="tier-badge">{entry["tier"]}</span><strong>#{entry["rank"]} in {entry["lane_label"]}</strong><span>{entry["composite"] / 10:.1f} / 10</span></div></section>
  <div class="detail-layout"><div class="detail-main">
    <section class="proof-gallery" aria-label="output gallery"><div class="section-head"><div><p class="eyebrow">output proof</p><h2>the result, before the mechanism.</h2></div><span class="gallery-note">{len(entry["media"])} pulled example{"s" if len(entry["media"]) != 1 else ""}</span></div>{gallery}</section>
    <section class="editor-note"><p class="eyebrow">editor’s note</p><p class="verdict">“{esc(entry["verdict_line"])}”</p><p>{esc(entry["purpose"])}</p>{'<span class="warning-label">preview uses a different or unverified base · check before matching results.</span>' if entry['preview_mismatch_badge'] else ''}</section>
    {storyboard}
    <section class="import-panel" id="import"><p class="eyebrow">import / pinned version {esc(entry["latest_version"]["name"])} <button class="inline-copy" type="button" data-copy="{esc(entry["latest_version"]["name"])}">copy version</button></p><h2>what you need</h2>{requirements_markup(entry)}<div class="import-action"><a class="button coral download-button" href="{workflow_href}" download data-download>download comfyui json ↗</a><p>download the JSON, drag it onto the ComfyUI canvas, then install the highlighted missing models.</p></div></section>
    <section class="detail-footer"><div><p class="eyebrow">handoff next</p><h2>keep the loop moving.</h2><a class="button acid" href="{root}{handoff}/">{handoff_label} ↗</a></div><a class="original-link" href="{esc(entry['source_url'] or '#')}" target="_blank" rel="noreferrer">open original on Civitai ↗</a></section>
  </div><aside class="proof-rail" aria-label="technical proof rail"><div class="rail-sticky"><p class="eyebrow">decision proof</p><h2>why it sits here.</h2><div class="rail-badge {"verified" if entry["verification"]["tested_by_us"] else "pending"}"><span>●</span>{verified}</div><dl class="proof-list"><div><dt>tier / rank</dt><dd>{entry["tier"]} · #{entry["rank"]} in {entry["lane_label"]}</dd></div><div><dt>composite</dt><dd>{entry["composite"] / 10:.1f} / 10 <small>lane-local</small></dd></div><div><dt>vram <em>est.</em></dt><dd>{esc(entry["vram_badge"])} gb <small>{esc(entry["vram_confidence"])} confidence</small></dd></div><div><dt>base model</dt><dd>{esc(entry["base_model"])}</dd></div><div><dt>freshness</dt><dd>{date_label(entry["latest_version"]["updated_at"])}</dd></div><div><dt>source stats</dt><dd>{compact_number(stats["downloads"]["value"])} downloads <small>pulled {date_label(stats["downloads"]["pulled_at"])}</small></dd></div></dl><div class="rail-block"><span class="rail-label">verification</span><p>{esc(entry["preview_honesty"])} · {esc(entry["stats_note"])}</p><p>anchors recomputed from this lane’s pull. tier hysteresis is ready after pull 4.</p></div><div class="rail-block"><span class="rail-label">provenance</span><p>creator <strong>{esc(entry["provenance"]["creator"])}</strong><br>version id <strong>{esc(entry["provenance"]["version_id"])}</strong><br>checked <strong>{date_label(entry["provenance"]["checked_at"])}</strong></p></div><div class="rail-block"><span class="rail-label">license notes</span><div class="pill-list">{"".join(f'<span class="license-pill">{esc(pill)}</span>' for pill in entry["license_pills"])}</div></div>{'<div class="rail-block stale"><span class="rail-label">needs re-test</span><p>the source is still live, but this recipe has not been run by us yet.</p></div>' if entry['status']['needs_retest'] else ''}{png}</div></aside></div>
</main>'''
    return base_path(root, entry["name"], body, f'data-page="detail" data-entry-id="{entry["id"]}"')


def models_page(models: list[dict], root: str) -> str:
    tasks = []
    for task in ("image", "face-consistency", "t2v", "i2v-audio", "voice"):
        rows = [model for model in models if model["task"] == task]
        task_label = {"image": "image generation", "face-consistency": "face consistency", "t2v": "text to video", "i2v-audio": "image to video + native audio", "voice": "voice / TTS"}[task]
        row_html = []
        for model in rows:
            row_html.append(f'''<article class="model-row {"contested" if model["contested"] else ""}"><div class="model-rank">{model["rank"]:02d}</div><div class="model-name"><h3>{esc(model["name"])}</h3><p>{esc(model["position"])}</p></div><div><span class="model-label">board</span><strong>{esc(model["board"])}</strong><small>{esc(model["date"])}</small></div><div><span class="model-label">license / vram</span><strong>{esc(model["license"])}</strong><small>{esc(model["vram_badge"])}</small></div><div><span class="model-label">comfyui</span><strong>{esc(model["comfyui"])}</strong><small>{esc(model["target_folder_hint"])}</small></div><div class="model-verdict"><p>{esc(model["our_verdict"])}</p>{'<span class="contested-badge">contested</span>' if model["contested"] else ''}{f'<span class="unverified">unverified: {esc(", ".join(model["unverified_fields"]))}</span>' if model["unverified_fields"] else ''}<a href="{esc(model["source_url"])}" target="_blank" rel="noreferrer">open board ↗</a></div></article>''')
        tasks.append(f'<section class="model-task"><div class="model-task-head"><p class="eyebrow">task / {task}</p><h2>{task_label}</h2><span>positions are snapshot evidence, not a permanent truth.</span></div>{"".join(row_html)}</section>')
    body = f'''<main class="page-shell models-page" data-page="models"><section class="lane-hero"><p class="eyebrow">tab / models</p><h1>choose the engine after you choose the job.</h1><p>leaderboard positions pulled from the live research snapshot. open weights, license landmines, ComfyUI support, and unverified gaps stay visible together.</p><div class="lane-meta"><span>5 task axes</span><span>research checked 01 Sep 2026</span><span>contested picks are marked</span></div></section><div class="models-intro"><p>use this tab when a workflow card names a job but you still need a model. local folders are hints, not a promise; check the source before a commercial handoff.</p><a class="button outline" href="{root}guide/">read the first 60 seconds ↗</a></div>{"".join(tasks)}</main>'''
    return base_path(root, "models", body, 'data-page="models"')


def guide_page(root: str) -> str:
    body = f'''<main class="page-shell guide-page" data-page="guide"><section class="lane-hero guide-hero"><p class="eyebrow">guide / first 60 seconds</p><h1>outcome first. mechanism second.</h1><p>civitai is where the originals live. this library narrows the choice to setups worth trying, then gives you the shortest honest handoff into ComfyUI.</p><a class="button cobalt" href="{root}personas/">start with personas ↗</a></section><section class="minute-route"><div class="route-heading"><p class="eyebrow">the one-minute route</p><h2>from “what should i use?” to a canvas with a plan.</h2></div><div class="route-grid"><article><span>01 / outcome</span><h3>choose a result</h3><p>start with a realistic social persona, a product-ready face, or a talking-head creator.</p></article><article><span>02 / hardware</span><h3>name your GPU</h3><p>use the vram filter as an estimate: 6–8 gb, 10–12 gb, 16 gb+, or cloud.</p></article><article><span>03 / proof</span><h3>read the verdict</h3><p>look at the output gallery, the caveat, the pinned version, and the proof rail.</p></article><article><span>04 / import</span><h3>drag the JSON</h3><p>download the note, drag it onto ComfyUI, then install the two highlighted missing models.</p></article></div></section><section class="guide-columns"><div><p class="eyebrow">glossary</p><h2>plain words for technical things.</h2><dl class="glossary"><div><dt>identity lock</dt><dd>a method for keeping the recognizable face stable across shots.</dd></div><div><dt>base model</dt><dd>the checkpoint or engine that gives a stack its broad visual language.</dd></div><div><dt>workflow</dt><dd>a ComfyUI graph: models, nodes, and the order they run in.</dd></div><div><dt>lane-local rank</dt><dd>a rank that only compares entries doing the same kind of job.</dd></div><div><dt>preview honesty</dt><dd>whether the pulled example is tied to the listed version’s metadata.</dd></div><div><dt>proven</dt><dd>a sort that keeps editorial evidence ahead of a newly updated source.</dd></div></dl></div><aside class="guide-aside"><p class="eyebrow">import language</p><h2>download JSON → drag onto ComfyUI, or use Workflows &gt; Open.</h2><p>the download is enriched with our notes. when the source only exposes an archive, the file is clearly labeled as a note and links you to the real Civitai archive.</p><a href="{root}ads/" class="text-link">see ad pipelines ↗</a></aside></section></main>'''
    return base_path(root, "guide", body, 'data-page="guide"')


def workflow_stub(entry: dict) -> dict:
    archive_note = entry.get("archive")
    return {
        "format": "civitai-library.workflow-note",
        "format_version": "1.0",
        "honest_status": "no embedded ComfyUI graph was available in the pulled source",
        "entry": {"id": entry["id"], "slug": entry["slug"], "our_name": entry["name"], "source_url": entry["source_url"]},
        "pinned_version": entry["latest_version"],
        "our_notes": [entry["purpose"], entry["verdict_line"], "download this note, then open the linked source archive when one is available."],
        "requirements": entry["requirements"],
        "source_archive": archive_note,
        "import_instruction": "download the JSON, drag it onto the ComfyUI canvas, then install the highlighted missing models.",
    }


def main() -> None:
    candidates, curations = load_source_lanes()
    mature_ids = {int(item["id"]) for item in candidates["nsfw"]}
    visible_candidates = {
        lane: [item for item in items if lane == "nsfw" or int(item["id"]) not in mature_ids]
        for lane, items in candidates.items()
    }
    entries_by_lane: dict[str, list[dict]] = {}
    anchors_by_lane: dict[str, dict] = {}
    for lane, items in visible_candidates.items():
        for item in items:
            item["lane"] = lane
        anchors = compute_anchors(items)
        anchors_by_lane[lane] = anchors
        entries = [normalize_entry(item, curations[lane][str(item["id"])], lane, anchors) for item in items]
        assign_ranks(entries)
        entries_by_lane[lane] = entries

    sfw_entries = [entry for lane in ("persona", "workflows") for entry in entries_by_lane[lane]]
    mature_entries = entries_by_lane["nsfw"]
    all_entries = {entry["id"]: entry for entry in sfw_entries + mature_entries}

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "data").mkdir(parents=True, exist_ok=True)

    # Shared data is intentionally split by content class. Do not merge these files.
    write_text(SITE / "data/entries-sfw.json", jdump({"generated_at": PULL_DATE.isoformat(), "anchors": {k: v for k, v in anchors_by_lane.items() if k != "nsfw"}, "entries": sfw_entries, "intent_chips": INTENTS}))
    write_text(SITE / "data/mature-entries.json", jdump({"generated_at": PULL_DATE.isoformat(), "anchors": {"nsfw": anchors_by_lane["nsfw"]}, "entries": mature_entries}))
    write_text(SITE / "data/search-index-sfw.json", jdump([{"id": entry["id"], "slug": entry["slug"], "lane": entry["lane"], "name": entry["name"], "original_name": entry["original_name"], "creator": entry["creator"]["username"], "purpose": entry["purpose"], "verdict": entry["verdict_line"], "locks": entry["locks"], "outputs": entry["outputs"], "base_model": entry["base_model"], "nsfwLevel": entry["nsfwLevel"]} for entry in sfw_entries]))
    write_text(SITE / "data/search-index-mature.json", jdump([{"id": entry["id"], "slug": entry["slug"], "lane": "nsfw", "name": entry["name"], "original_name": entry["original_name"], "creator": entry["creator"]["username"], "purpose": entry["purpose"], "verdict": entry["verdict_line"], "locks": entry["locks"], "outputs": entry["outputs"], "base_model": entry["base_model"], "nsfwLevel": entry["nsfwLevel"]} for entry in mature_entries]))
    write_text(SITE / "data/synonyms.json", jdump({"synonyms": SYNONYMS, "intents": INTENTS, "scope_labels": ["this lane", "all sfw", "saved"]}))
    models = build_models()
    write_text(DATA / "models.json", jdump({"generated_at": PULL_DATE.isoformat(), "source": "research/model-benchmarks.md", "entries": models}))
    write_text(SITE / "data/models.json", jdump({"generated_at": PULL_DATE.isoformat(), "source": "research/model-benchmarks.md", "entries": models}))

    write_text(SITE / "index.html", home_page({"persona": entries_by_lane["persona"], "workflows": entries_by_lane["workflows"], "nsfw": mature_entries}, "./"))
    write_text(SITE / "personas/index.html", lane_page("persona", entries_by_lane["persona"], "../"))
    write_text(SITE / "ads/index.html", lane_page("workflows", entries_by_lane["workflows"], "../"))
    write_text(SITE / "mature/index.html", lane_page("nsfw", [], "../"))
    write_text(SITE / "models/index.html", models_page(models, "../"))
    write_text(SITE / "guide/index.html", guide_page("../"))

    for entry in sfw_entries:
        write_text(SITE / "entries" / entry["slug"] / "index.html", detail_page(entry, "../../"))
        write_text(SITE / "workflows" / f'{entry["slug"]}.json', jdump(workflow_stub(entry)))
    for entry in mature_entries:
        write_text(SITE / "mature/entries" / entry["slug"] / "index.html", detail_page(entry, "../../../", mature=True))
        write_text(SITE / "mature/workflows" / f'{entry["slug"]}.json', jdump(workflow_stub(entry)))

    # Keep the static implementation self-contained and auditable.
    write_text(SITE / "assets/style.css", CSS)
    write_text(SITE / "assets/app.js", JS)
    print(f"built {len(sfw_entries)} sfw entries + {len(mature_entries)} mature entries")
    print(f"anchors: {', '.join(sorted(anchors_by_lane))}; pull date {PULL_DATE.isoformat()}")


CSS = r''':root {
  --paper: #f0eee7;
  --ink: #171717;
  --cobalt: #315bff;
  --acid: #d9ff4d;
  --warm-grey: #c9c5bb;
  --lavender: #dcd9ff;
  --coral: #ff705c;
  --muted: #68675f;
  --line: rgba(23, 23, 23, .18);
  --display: "Bricolage Grotesque", "Arial Narrow", sans-serif;
  --body: "Literata", Georgia, serif;
  --mono: "Azeret Mono", "SFMono-Regular", Consolas, monospace;
  color: var(--ink);
  background: var(--paper);
  font-family: var(--body);
  font-synthesis: none;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); line-height: 1.5; }
body::before { content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .11; z-index: 20; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.2'/%3E%3C/svg%3E"); mix-blend-mode: multiply; }
a { color: inherit; }
button, input { font: inherit; color: inherit; }
button { cursor: pointer; }
:focus-visible { outline: 3px solid var(--cobalt); outline-offset: 3px; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; }
.site-header { min-height: 84px; padding: 18px clamp(18px, 4vw, 62px); border-bottom: 1px solid var(--line); display: grid; grid-template-columns: 1.2fr auto 1.5fr; gap: 24px; align-items: center; position: relative; z-index: 21; background: color-mix(in srgb, var(--paper) 94%, white); }
.brand { text-decoration: none; display: inline-flex; align-items: baseline; gap: 9px; font: 700 19px/1 var(--display); letter-spacing: -.03em; }
.brand small { font: 10px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.main-nav { display: flex; gap: 20px; font: 11px var(--mono); text-transform: lowercase; }
.main-nav a { text-decoration: none; padding: 8px 0; border-bottom: 2px solid transparent; }
.main-nav a:hover, .main-nav a[aria-current="page"] { border-color: var(--cobalt); }
.header-tools { display: flex; justify-content: flex-end; align-items: center; gap: 10px; }
.site-search { border: 1px solid var(--ink); display: flex; width: min(310px, 100%); background: var(--paper); }
.site-search input { min-width: 0; width: 100%; border: 0; background: transparent; padding: 10px 12px; font: 11px var(--mono); }
.site-search button { border: 0; border-left: 1px solid var(--ink); background: var(--acid); padding: 0 12px; }
.mature-toggle, .reset-mature { border: 0; background: transparent; font: 10px var(--mono); white-space: nowrap; }
.mature-toggle { display: flex; align-items: center; gap: 6px; }
.toggle-dot { width: 25px; height: 14px; border: 1px solid var(--ink); border-radius: 99px; position: relative; display: inline-block; }
.toggle-dot::after { content: ""; width: 8px; height: 8px; background: var(--ink); position: absolute; left: 2px; top: 2px; border-radius: 50%; transition: transform .22s ease; }
.mature-toggle[aria-pressed="true"] .toggle-dot { background: var(--coral); }
.mature-toggle[aria-pressed="true"] .toggle-dot::after { transform: translateX(11px); }
.toggle-state { color: var(--muted); }
.reset-mature { color: var(--muted); text-decoration: underline; text-underline-offset: 3px; }
.page-shell, .home-shell { width: min(1400px, calc(100% - 36px)); margin: 0 auto; }
.eyebrow, .model-label, .rail-label, .filter-label, .section-head .quiet-note { font: 10px var(--mono); letter-spacing: .09em; text-transform: uppercase; color: var(--muted); }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { font-family: var(--display); letter-spacing: -.045em; line-height: .98; }
h1 { font-size: clamp(44px, 7vw, 91px); max-width: 900px; margin-bottom: 20px; }
h2 { font-size: clamp(28px, 4vw, 51px); }
h3 { font-size: 22px; }
.button { display: inline-flex; justify-content: center; align-items: center; min-height: 44px; padding: 10px 16px; border: 1px solid var(--ink); text-decoration: none; font: 11px var(--mono); text-transform: lowercase; transition: transform .18s ease, background-color .18s ease; }
.button:hover { transform: translateY(-2px); }
.button.cobalt { background: var(--cobalt); border-color: var(--cobalt); color: white; }
.button.coral { background: var(--coral); border-color: var(--coral); }
.button.acid { background: var(--acid); }
.button.outline { background: transparent; }
.button.quiet { border-color: var(--line); background: transparent; }
.text-link { font: 11px var(--mono); text-decoration-thickness: 1px; text-underline-offset: 4px; }
.home-hero { padding: clamp(54px, 9vw, 132px) 0 78px; display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(280px, .7fr); gap: clamp(28px, 8vw, 130px); border-bottom: 1px solid var(--line); }
.hero-dek { font-size: 19px; line-height: 1.45; max-width: 620px; }
.hero-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 30px; }
.hero-note { align-self: end; border-left: 5px solid var(--cobalt); padding: 17px 0 17px 24px; max-width: 370px; }
.note-pin { display: block; color: var(--cobalt); font: 10px var(--mono); text-transform: uppercase; letter-spacing: .1em; margin-bottom: 18px; }
.hero-note p { font: 25px/1.08 var(--display); }
.hero-note small { display: block; color: var(--muted); font-size: 12px; line-height: 1.45; }
.search-stage { padding: 84px 0 92px; border-bottom: 1px solid var(--line); }
.search-stage > div:first-child { display: flex; justify-content: space-between; align-items: end; }
.big-search { border-bottom: 2px solid var(--ink); display: flex; max-width: 880px; margin: 20px 0 18px; }
.big-search input { flex: 1; border: 0; background: transparent; padding: 13px 0; font: 19px var(--body); min-width: 0; }
.search-scope { border: 0; border-left: 1px solid var(--line); background: transparent; padding: 0 11px; font: 9px var(--mono); text-transform: lowercase; }
.intent-row { display: flex; flex-wrap: wrap; gap: 8px; }
.intent-chip, .chip { border: 1px solid var(--line); background: transparent; padding: 7px 10px; font: 10px var(--mono); }
.intent-chip:hover, .intent-chip:focus-visible { background: var(--lavender); border-color: var(--cobalt); }
.interpretation { margin-top: 16px; padding: 9px 12px; background: var(--acid); font: 11px var(--mono); width: fit-content; }
.recent-searches { margin-top: 16px; color: var(--muted); font: 9px var(--mono); }
.recent-searches button { border: 0; border-bottom: 1px solid var(--line); background: transparent; padding: 3px 7px 3px 0; margin-right: 8px; font: inherit; }
.start-strip { background: var(--ink); color: var(--paper); padding: 30px; display: grid; grid-template-columns: 1fr 1.4fr auto; gap: 28px; align-items: center; }
.start-strip .eyebrow { color: var(--acid); }
.start-strip h2 { margin: 0; font-size: 30px; }
.start-steps { display: flex; justify-content: space-between; gap: 18px; font: 11px var(--mono); }
.start-steps b { color: var(--acid); margin-right: 7px; }
.home-lanes, .fresh-section { padding: 90px 0 0; }
.home-lane { margin-top: 34px; }
.home-lane-head, .section-head { display: flex; justify-content: space-between; align-items: end; gap: 18px; border-bottom: 1px solid var(--line); padding-bottom: 15px; margin-bottom: 22px; }
.home-lane-head h2, .section-head h2 { margin: 3px 0 0; font-size: 38px; }
.home-lane-head > a { font: 10px var(--mono); }
.lane-number { font: 44px var(--display); color: var(--cobalt); line-height: .8; }
.mature-card { min-height: 250px; background: var(--lavender); border: 1px solid var(--ink); padding: 24px; display: flex; flex-direction: column; text-decoration: none; margin-top: 32px; }
.mature-card h3 { font-size: 35px; margin: 30px 0 10px; }
.mature-card p { max-width: 330px; }
.lane-link { margin-top: auto; font: 10px var(--mono); }
.entry-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.home-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.entry-card { min-width: 0; border-top: 1px solid var(--ink); background: rgba(255,255,255,.17); transition: transform .18s ease, box-shadow .18s ease; }
.entry-card:hover { transform: translateY(-3px); box-shadow: 8px 8px 0 var(--lavender); }
.card-preview { display: block; position: relative; aspect-ratio: 3 / 4; overflow: hidden; background: var(--warm-grey); text-decoration: none; }
.media { width: 100%; height: 100%; display: block; object-fit: cover; transition: transform .18s ease, filter .18s ease; }
.entry-card:hover .media { transform: scale(1.025); }
.media.blurred { filter: blur(28px); transform: scale(1.08); }
.mature-cover { position: absolute; inset: auto 12px 12px; background: var(--ink); color: var(--paper); padding: 8px 10px; font: 10px var(--mono); text-align: center; }
.preview-corner { position: absolute; top: 10px; left: 10px; background: var(--acid); padding: 5px 7px; font: 9px var(--mono); }
.preview-placeholder { height: 100%; display: grid; place-items: center; color: var(--muted); font: 10px var(--mono); text-transform: uppercase; }
.card-copy { padding: 16px 16px 14px; }
.rank-row { display: flex; align-items: center; gap: 8px; min-height: 24px; font: 10px var(--mono); }
.tier-badge { width: 28px; height: 28px; display: inline-grid; place-items: center; background: var(--cobalt); color: white; font: 700 14px var(--display); cursor: help; }
.tier-badge:hover { background: var(--ink); }
.rank-label { color: var(--muted); }
.score { margin-left: auto; font-weight: 700; }
.card-copy h3 { margin: 18px 0 8px; font-size: 27px; }
.card-copy h3 a { text-decoration: none; }
.purpose { font-size: 14px; line-height: 1.4; min-height: 60px; }
.card-meta { display: flex; flex-wrap: wrap; gap: 6px 10px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 9px 0; margin: 13px 0 10px; font: 9px var(--mono); text-transform: uppercase; color: var(--muted); }
.card-meta em { font-style: normal; color: var(--cobalt); }
.stack-formula { font: 10px var(--mono); min-height: 31px; color: var(--muted); }
.stack-formula span { color: var(--cobalt); text-transform: uppercase; margin-right: 5px; }
.stats-trio { display: grid; grid-template-columns: repeat(3, 1fr); list-style: none; margin: 0; padding: 11px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); gap: 8px; }
.stats-trio li { min-width: 0; display: flex; flex-direction: column; }
.stats-trio strong { font: 700 15px var(--display); }
.stats-trio span, .stats-trio small { font: 9px var(--mono); color: var(--muted); }
.stats-trio small { font-size: 7px; margin-top: 5px; white-space: nowrap; }
.chip-row { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 11px; min-height: 29px; }
.chip { font-size: 8px; padding: 5px 6px; }
.chip.warning, .warning-label { color: #a53c2d; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.requirements-badge { font: 8px var(--mono); text-transform: uppercase; color: var(--muted); }
.save-button { border: 0; background: transparent; font-size: 21px; padding: 0 2px; line-height: 1; }
.save-button.is-saved { color: var(--cobalt); }
.fresh-section { padding-bottom: 100px; }
.quiet-note { max-width: 260px; text-align: right; }
.lane-hero { padding: 76px 0 45px; border-bottom: 1px solid var(--line); }
.lane-hero > p:not(.eyebrow) { max-width: 650px; font-size: 17px; }
.lane-meta { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 28px; font: 10px var(--mono); color: var(--muted); }
.lane-meta span + span::before { content: "·"; margin-right: 18px; color: var(--cobalt); }
.filter-shell { padding: 20px 0 30px; border-bottom: 1px solid var(--line); }
.filter-bar { display: flex; flex-wrap: wrap; align-items: end; gap: 17px 22px; }
.filter-group { min-width: 0; }
.filter-label { display: block; margin-bottom: 7px; }
.filter-choices { display: flex; flex-wrap: wrap; gap: 5px; }
.filter-choice, .sort-choice, .more-button { border: 1px solid var(--line); background: transparent; padding: 6px 8px; font: 9px var(--mono); }
.filter-choice.active, .sort-choice.active { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.filter-choice:disabled { opacity: .32; cursor: not-allowed; text-decoration: line-through; }
.chip-count { color: var(--cobalt); margin-left: 3px; }
.filter-choice.active .chip-count { color: var(--acid); }
.more-button { color: var(--cobalt); border-color: var(--cobalt); }
.sort-toggle { display: flex; align-items: center; gap: 5px; margin-left: auto; }
.sort-toggle > span { font: 9px var(--mono); color: var(--muted); margin-right: 2px; }
.more-filters { display: flex; flex-wrap: wrap; gap: 18px 28px; padding: 19px 0 0; border-top: 1px solid var(--line); margin-top: 18px; }
.more-filters[hidden] { display: none; }
.tier-results { padding-bottom: 80px; }
.tier-band { padding-top: 43px; }
.band-heading { display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--ink); padding-bottom: 12px; margin-bottom: 18px; opacity: .78; transform: translateY(5px); transition: opacity .22s ease, transform .22s ease; }
.band-heading.is-visible { opacity: 1; transform: translateY(0); }
.band-index { width: 39px; height: 39px; display: grid; place-items: center; background: var(--acid); font: 700 23px var(--display); }
.band-heading h2 { font-size: 31px; margin: 0; }
.band-heading p { margin: 3px 0 0; color: var(--muted); font-size: 12px; }
.band-count { margin-left: auto; font: 10px var(--mono); color: var(--muted); }
.empty-inline { border: 1px dashed var(--line); padding: 24px; color: var(--muted); font: 11px var(--mono); }
.gate-callout { display: flex; align-items: center; gap: 13px; width: fit-content; background: var(--lavender); padding: 11px 13px; font: 10px var(--mono); }
.gate-mark { display: inline-grid; place-items: center; width: 27px; height: 27px; background: var(--ink); color: var(--acid); }
.mature-skeleton { min-height: 470px; padding: 70px 0; }
.mature-skeleton p { font: 11px var(--mono); color: var(--muted); }
.skeleton-line { height: 13px; width: 33%; background: var(--warm-grey); margin: 12px 0; }
.skeleton-line.wide { width: 61%; height: 50px; }
.skeleton-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 30px 0; }
.skeleton-grid i { display: block; aspect-ratio: 3 / 4; background: linear-gradient(100deg, var(--warm-grey), #dbd8cf, var(--warm-grey)); background-size: 200% 100%; animation: skeleton-shimmer 1.7s infinite; }
.mature-route .filter-shell { opacity: .7; }
@keyframes skeleton-shimmer { to { background-position: -200% 0; } }
.detail-shell { padding-bottom: 90px; }
.breadcrumb { display: flex; gap: 9px; padding: 22px 0; font: 10px var(--mono); color: var(--muted); }
.breadcrumb a { color: var(--cobalt); }
.detail-heading { display: flex; justify-content: space-between; align-items: end; gap: 24px; padding: 30px 0 44px; border-bottom: 1px solid var(--line); }
.detail-heading h1 { font-size: clamp(44px, 7vw, 86px); max-width: 800px; margin-bottom: 14px; }
.alias { margin: 0; color: var(--muted); font-size: 12px; }
.alias span { color: var(--ink); }
.alias a { color: var(--cobalt); }
.detail-rank { display: grid; grid-template-columns: auto auto; align-items: center; gap: 9px 12px; min-width: 230px; font: 11px var(--mono); }
.detail-rank .tier-badge { grid-row: span 2; width: 50px; height: 50px; font-size: 25px; }
.detail-rank span:last-child { color: var(--muted); }
.detail-layout { display: grid; grid-template-columns: minmax(0, 1fr) 310px; gap: clamp(28px, 6vw, 80px); padding-top: 45px; }
.detail-main { min-width: 0; }
.proof-gallery { border-bottom: 1px solid var(--line); padding-bottom: 34px; }
.proof-gallery .section-head { margin-bottom: 18px; }
.proof-gallery h2 { font-size: 34px; margin: 0; }
.gallery-note { font: 10px var(--mono); color: var(--muted); }
.gallery-main { aspect-ratio: 3 / 4; max-height: 790px; background: var(--warm-grey); position: relative; overflow: hidden; }
.gallery-main .media { width: 100%; height: 100%; object-fit: cover; }
.gallery-main .mature-cover { bottom: 22px; left: 22px; right: 22px; padding: 12px; }
.gallery-open { position: absolute; right: 14px; bottom: 14px; border: 1px solid white; background: var(--ink); color: white; padding: 8px 10px; font: 10px var(--mono); }
.gallery-thumbs { display: flex; gap: 7px; overflow-x: auto; padding-top: 9px; }
.gallery-thumb { width: 66px; height: 83px; flex: 0 0 auto; border: 1px solid transparent; padding: 0; background: var(--warm-grey); overflow: hidden; }
.gallery-thumb.active { border: 3px solid var(--cobalt); }
.gallery-thumb .media { width: 100%; height: 100%; object-fit: cover; }
.gallery-empty { padding: 70px 20px; border: 1px dashed var(--line); color: var(--muted); font: 11px var(--mono); }
.editor-note { padding: 45px 0; border-bottom: 1px solid var(--line); max-width: 800px; }
.verdict { font: clamp(25px, 3.7vw, 45px)/1.08 var(--display); max-width: 800px; }
.editor-note > p:last-of-type { max-width: 690px; font-size: 17px; }
.warning-label { display: inline-block; margin-top: 8px; font: 10px var(--mono); }
.storyboard { padding: 32px 0; border-bottom: 1px solid var(--line); }
.storyboard-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font: 10px var(--mono); }
.storyboard-row span { border: 1px solid var(--ink); padding: 9px; }
.storyboard-row span:first-child { background: var(--acid); }
.storyboard-row i { color: var(--cobalt); font-style: normal; }
.import-panel { margin-top: 36px; padding: 30px; background: var(--ink); color: var(--paper); }
.import-panel .eyebrow { color: var(--acid); }
.import-panel h2 { color: white; margin-bottom: 24px; }
.requirements-status { display: flex; align-items: center; gap: 8px; font: 11px var(--mono); padding-bottom: 16px; border-bottom: 1px solid rgba(240,238,231,.25); }
.status-dot { width: 8px; height: 8px; background: var(--coral); border-radius: 50%; }
.confidence { margin-left: auto; color: var(--warm-grey); }
.requirements-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 25px 0; }
.requirements-columns h3 { color: var(--acid); font-size: 19px; }
.requirement-list { list-style: none; padding: 0; margin: 0; }
.requirement-list li { border-top: 1px solid rgba(240,238,231,.25); padding: 10px 0; display: flex; flex-direction: column; gap: 3px; font-size: 13px; }
.requirement-list span { color: var(--warm-grey); font: 9px var(--mono); }
.recovery-note { color: var(--warm-grey); font-size: 12px; }
.recovery-note strong { color: white; }
.source-download { display: inline-block; color: var(--acid); font: 10px var(--mono); margin-top: 5px; }
.import-action { border-top: 1px solid rgba(240,238,231,.25); margin-top: 20px; padding-top: 22px; display: flex; align-items: center; gap: 18px; }
.import-action p { max-width: 420px; color: var(--warm-grey); font-size: 12px; margin: 0; }
.proof-rail { border-left: 1px solid var(--line); padding-left: 25px; }
.rail-sticky { position: sticky; top: 28px; }
.proof-rail h2 { font-size: 32px; margin-bottom: 18px; }
.rail-badge { display: inline-flex; gap: 7px; align-items: center; padding: 8px 10px; font: 10px var(--mono); margin-bottom: 16px; }
.rail-badge.verified { background: var(--acid); }
.rail-badge.pending { background: var(--lavender); }
.proof-list { border-top: 1px solid var(--ink); margin: 0; }
.proof-list > div { display: flex; justify-content: space-between; gap: 12px; padding: 11px 0; border-bottom: 1px solid var(--line); }
.proof-list dt { font: 9px var(--mono); color: var(--muted); text-transform: uppercase; }
.proof-list dd { text-align: right; margin: 0; font-size: 13px; }
.proof-list dd small { display: block; color: var(--muted); font: 8px var(--mono); margin-top: 3px; }
.proof-list em { color: var(--cobalt); font-style: normal; }
.rail-block { padding: 19px 0; border-bottom: 1px solid var(--line); font-size: 12px; }
.rail-label { display: block; margin-bottom: 7px; }
.rail-block p { margin: 0; color: var(--muted); }
.rail-block strong { color: var(--ink); }
.pill-list { display: flex; flex-wrap: wrap; gap: 5px; }
.license-pill { padding: 5px 6px; background: var(--lavender); font: 8px var(--mono); }
.rail-block.stale { color: #a53c2d; }
.detail-footer { padding: 45px 0 0; display: flex; justify-content: space-between; align-items: end; gap: 20px; }
.detail-footer h2 { font-size: 34px; margin: 5px 0 18px; }
.original-link { font: 10px var(--mono); }
.models-intro { border: 1px solid var(--ink); padding: 18px; display: flex; justify-content: space-between; gap: 20px; align-items: center; margin: 28px 0 70px; }
.models-intro p { max-width: 700px; margin: 0; font-size: 14px; }
.model-task { padding-bottom: 63px; }
.model-task-head { display: flex; align-items: end; gap: 16px; border-bottom: 1px solid var(--ink); padding-bottom: 13px; margin-bottom: 0; }
.model-task-head h2 { font-size: 34px; margin: 0; }
.model-task-head > span { margin-left: auto; font: 9px var(--mono); color: var(--muted); }
.model-row { display: grid; grid-template-columns: 45px 1.2fr 1fr .85fr .85fr 1.4fr; gap: 16px; padding: 19px 0; border-bottom: 1px solid var(--line); align-items: start; }
.model-row.contested { background: rgba(220,217,255,.45); }
.model-rank { font: 20px var(--mono); color: var(--cobalt); }
.model-name h3 { font-size: 23px; margin: 0 0 4px; }
.model-name p, .model-row strong, .model-row small, .model-verdict p, .model-verdict a { display: block; }
.model-name p, .model-row strong, .model-row small, .model-verdict p, .model-verdict a { font-size: 11px; margin: 0; }
.model-row strong { font-family: var(--mono); }
.model-row small { color: var(--muted); font: 9px var(--mono); margin-top: 5px; }
.model-verdict { position: relative; }
.model-verdict p { line-height: 1.4; margin-bottom: 9px; }
.model-verdict a { color: var(--cobalt); font: 9px var(--mono); margin-top: 8px; }
.contested-badge, .unverified { display: inline-block; padding: 4px 5px; background: var(--coral); font: 8px var(--mono); margin: 0 4px 4px 0; }
.unverified { background: var(--acid); }
.minute-route { padding: 80px 0; border-bottom: 1px solid var(--line); }
.route-heading { max-width: 650px; margin-bottom: 35px; }
.route-grid { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--ink); border-left: 1px solid var(--ink); }
.route-grid article { padding: 22px; border-right: 1px solid var(--ink); border-bottom: 1px solid var(--ink); min-height: 220px; }
.route-grid span { font: 9px var(--mono); color: var(--cobalt); }
.route-grid h3 { margin: 28px 0 9px; font-size: 27px; }
.guide-columns { padding: 80px 0; display: grid; grid-template-columns: 1.1fr .9fr; gap: 90px; }
.glossary { border-top: 1px solid var(--ink); }
.glossary div { display: grid; grid-template-columns: 180px 1fr; gap: 20px; padding: 15px 0; border-bottom: 1px solid var(--line); }
.glossary dt { font: 11px var(--mono); color: var(--cobalt); }
.glossary dd { margin: 0; font-size: 14px; }
.guide-aside { background: var(--lavender); padding: 30px; align-self: start; }
.guide-aside h2 { font-size: 34px; }
.mature-dialog, .lightbox { border: 1px solid var(--ink); background: var(--paper); color: var(--ink); padding: 0; max-width: 550px; box-shadow: 12px 12px 0 var(--cobalt); }
.mature-dialog::backdrop, .lightbox::backdrop { background: rgba(23,23,23,.64); }
.mature-dialog form { padding: 30px; }
.mature-dialog h2 { font-size: 35px; }
.mature-dialog p:not(.eyebrow) { font-size: 15px; }
.remember-choice { display: block; font: 10px var(--mono); margin: 22px 0 7px; }
.mature-dialog small { color: var(--muted); font-size: 11px; }
.dialog-actions { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; margin-top: 24px; }
.lightbox { width: min(94vw, 1100px); max-width: none; min-height: 80vh; background: var(--ink); color: var(--paper); display: grid; grid-template-columns: 60px 1fr 60px; grid-template-rows: 1fr auto; align-items: center; }
.lightbox-stage { min-height: 70vh; display: grid; place-items: center; overflow: hidden; }
.lightbox-stage img, .lightbox-stage video { max-width: 100%; max-height: 75vh; width: auto; height: auto; object-fit: contain; }
.lightbox-stage video { display: none; }
.inline-copy { border: 1px solid var(--acid); background: transparent; color: var(--acid); padding: 4px 6px; font: 8px var(--mono); text-transform: uppercase; }
.count-swap { animation: count-swap .18s ease both; }
@keyframes count-swap { 50% { opacity: .15; transform: translateY(3px); } }
.empty-search { border: 1px dashed var(--line); padding: 32px; margin-top: 22px; }
.search-heading { display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding: 16px 0; margin-bottom: 18px; font: 10px var(--mono); }
.lightbox-close, .lightbox-arrow { border: 0; background: transparent; color: white; font-size: 32px; padding: 15px; }
.lightbox-close { position: absolute; top: 4px; right: 8px; }
.lightbox-caption { grid-column: 1 / -1; padding: 10px 25px 18px; color: var(--warm-grey); font: 10px var(--mono); margin: 0; }
.toast { position: fixed; left: 50%; bottom: 22px; transform: translate(-50%, 20px); background: var(--ink); color: var(--paper); padding: 10px 14px; font: 10px var(--mono); opacity: 0; pointer-events: none; z-index: 30; transition: opacity .18s ease, transform .18s ease; }
.toast.is-visible { opacity: 1; transform: translate(-50%, 0); }
.noscript-note { position: fixed; bottom: 0; left: 0; right: 0; background: var(--coral); padding: 10px; text-align: center; z-index: 30; font: 11px var(--mono); }
.mature-detail { min-height: 70vh; }
.skeleton-detail { padding: 90px 0; }
.skeleton-detail h1 { font-size: clamp(40px, 6vw, 76px); }
@media (max-width: 1080px) { .site-header { grid-template-columns: 1fr auto; } .main-nav { order: 3; grid-column: 1 / -1; } .header-tools { grid-column: 2; grid-row: 1; } .entry-grid, .home-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .model-row { grid-template-columns: 40px 1.2fr 1fr 1fr; } .model-row > div:nth-child(5) { display: none; } .model-verdict { grid-column: 2 / -1; } }
@media (max-width: 760px) { .site-header { display: flex; flex-wrap: wrap; gap: 15px; } .header-tools { width: 100%; justify-content: flex-start; flex-wrap: wrap; } .site-search { flex: 1 1 230px; } .main-nav { width: 100%; order: 0; overflow-x: auto; } .home-hero, .detail-layout, .guide-columns { grid-template-columns: 1fr; } .home-hero { padding-top: 65px; } h1 { font-size: clamp(43px, 15vw, 70px); } .start-strip { grid-template-columns: 1fr; } .start-steps { flex-direction: column; gap: 8px; } .entry-grid, .home-grid { grid-template-columns: 1fr; } .filter-bar { align-items: stretch; flex-direction: column; gap: 15px; } .sort-toggle { margin-left: 0; } .filter-group { width: 100%; } .filter-choices { overflow-x: auto; flex-wrap: nowrap; } .filter-choice { flex: 0 0 auto; } .band-heading { align-items: start; } .band-count { display: none; } .detail-heading { display: block; } .detail-rank { margin-top: 24px; } .proof-rail { border-left: 0; border-top: 1px solid var(--line); padding: 32px 0 0; } .rail-sticky { position: static; } .requirements-columns { grid-template-columns: 1fr; gap: 20px; } .import-action, .detail-footer, .models-intro { align-items: stretch; flex-direction: column; } .model-task-head { display: block; } .model-task-head > span { display: block; margin-top: 9px; } .model-row { grid-template-columns: 38px 1fr; gap: 8px 14px; } .model-row > div:nth-child(3), .model-row > div:nth-child(4) { grid-column: 2; } .model-row > div:nth-child(3), .model-row > div:nth-child(4) { display: block; } .model-verdict { grid-column: 2; } .route-grid { grid-template-columns: 1fr 1fr; } .glossary div { grid-template-columns: 1fr; gap: 6px; } .lightbox { grid-template-columns: 42px 1fr 42px; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; } }
'''


JS = r'''(() => {
  "use strict";
  const body = document.body;
  const root = body.dataset.siteRoot || "./";
  const matureKey = "civitai-library.mature-mode";
  const matureExpiryKey = "civitai-library.mature-expiry";
  const savedKey = "civitai-library.saved";
  const state = { mature: false, entries: [], index: [], sfwIndex: [], matureIndex: [], synonyms: {}, selected: {}, sort: "proven", lightbox: { items: [], index: 0 } };

  const qs = (selector, scope = document) => scope.querySelector(selector);
  const qsa = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  const text = (value) => String(value == null ? "" : value);
  const escapeHtml = (value) => text(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
  const number = (value) => Number(value || 0);
  const dateOnly = (value) => value ? new Date(value).getTime() : 0;
  const formatCount = (value) => { const n = number(value); if (n >= 1e6) return `${(n / 1e6).toFixed(1).replace(".0", "")}m`; if (n >= 1e3) return `${(n / 1e3).toFixed(1).replace(".0", "")}k`; return String(Math.round(n)); };

  function getSaved() { try { return JSON.parse(localStorage.getItem(savedKey) || "[]"); } catch (_) { return []; } }
  function saveSaved(ids) { try { localStorage.setItem(savedKey, JSON.stringify(ids)); } catch (_) {} }
  function toast(message) { const element = qs("[data-toast]"); if (!element) return; element.textContent = message; element.classList.add("is-visible"); window.setTimeout(() => element.classList.remove("is-visible"), 1800); }
  function dateLabel(value) { const date = value ? new Date(value) : null; return date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "date unavailable"; }
  function vramValue(value) { const match = text(value).match(/\d+/); return match ? Number(match[0]) : 0; }

  function matureRemembered() { try { return localStorage.getItem(matureKey) === "true" && Number(localStorage.getItem(matureExpiryKey)) > Date.now(); } catch (_) { return false; } }
  function setMatureUI(on) { state.mature = on; qsa("[data-mature-toggle]").forEach((button) => { button.setAttribute("aria-pressed", String(on)); const status = qs(".toggle-state", button); if (status) status.textContent = on ? "open" : "locked"; }); qsa("[data-search-scope] option[value=\"mature\"]").forEach((option) => { option.disabled = !on; if (!on && option.parentElement.value === "mature") option.parentElement.value = "all-sfw"; }); body.classList.toggle("mature-on", on); qsa("[data-mature-link]").forEach((link) => link.setAttribute("aria-label", on ? "open mature metadata" : "open mature metadata; confirmation required")); if (on) revealBlurred(); else reblur(); }
  function openMatureConfirm() { const dialog = qs("#mature-dialog"); if (!dialog) return; if (dialog.showModal) dialog.showModal(); else dialog.setAttribute("open", ""); }
  function confirmMature() { const remember = qs("[data-remember-mature]"); try { sessionStorage.setItem("civitai-library.mature-session", "true"); if (remember && remember.checked) { localStorage.setItem(matureKey, "true"); localStorage.setItem(matureExpiryKey, String(Date.now() + 30 * 24 * 60 * 60 * 1000)); } } catch (_) {} const dialog = qs("#mature-dialog"); if (dialog && dialog.close) dialog.close(); setMatureUI(true); loadMatureData(); }
  function resetMature() { try { sessionStorage.removeItem("civitai-library.mature-session"); localStorage.removeItem(matureKey); localStorage.removeItem(matureExpiryKey); } catch (_) {} setMatureUI(false); const route = body.dataset.page === "mature-detail" || body.dataset.matureRoute !== undefined; if (route) location.href = `${root}mature/`; }
  function initMature() { qsa("[data-mature-toggle]").forEach((button) => button.addEventListener("click", () => state.mature ? resetMature() : openMatureConfirm())); qsa("[data-reset-mature]").forEach((button) => button.addEventListener("click", resetMature)); const confirm = qs("[data-mature-confirm]"); if (confirm) confirm.addEventListener("click", confirmMature); const cancel = qs("[data-mature-cancel]"); if (cancel) cancel.addEventListener("click", () => { const dialog = qs("#mature-dialog"); if (dialog && dialog.close) dialog.close(); }); setMatureUI(matureRemembered()); if (state.mature && (body.hasAttribute("data-mature-route") || body.hasAttribute("data-mature-detail") || body.hasAttribute("data-home"))) loadMatureData(); }
  function revealBlurred() { qsa("[data-src]").forEach((media) => { if (!media.getAttribute("src")) { media.dataset.gatedSrc = media.dataset.src; media.setAttribute("src", media.dataset.src); media.removeAttribute("data-src"); media.classList.remove("blurred"); if (media.tagName === "VIDEO") media.load(); } }); qsa(".mature-cover").forEach((cover) => { cover.textContent = "preview unlocked for this session"; }); }
  function reblur() { qsa("[data-gated-src]").forEach((media) => { media.dataset.src = media.dataset.gatedSrc; media.removeAttribute("src"); media.classList.add("blurred"); if (media.tagName === "VIDEO") media.load(); }); qsa(".mature-cover").forEach((cover) => { cover.textContent = "preview hidden · unlock in header"; }); }

  async function fetchJson(path) { const response = await fetch(path, { credentials: "same-origin" }); if (!response.ok) throw new Error(`could not load ${path}`); return response.json(); }
  function entryMedia(entry) { return entry.media || []; }
  function mediaMarkup(entry, media) { if (!media || !media.url) return `<div class="preview-placeholder"><span>preview unavailable</span></div>`; const gated = entry.preview_gated && !state.mature; const attr = gated ? `data-src="${escapeHtml(media.url)}"` : `src="${escapeHtml(media.url)}"`; const klass = gated ? "media blurred" : "media"; if (media.kind === "video") return `<video class="${klass}" ${attr} width="450" height="600" muted loop playsinline preload="metadata" aria-label="${gated ? "mature workflow preview hidden" : "curated preview"}"></video>`; return `<img class="${klass}" ${attr} width="450" height="600" loading="lazy" alt="${gated ? "mature workflow preview hidden" : "curated field guide preview"}>`; }
  function cardMarkup(entry, viewRank, mature) { const href = `${root}${mature ? "mature/entries/" : "entries/"}${encodeURIComponent(entry.slug)}/`; const outputs = (entry.outputs || []).slice(0, 3).map((value) => escapeHtml(value.replaceAll("-", " "))).join(" · "); const locks = (entry.locks || []).slice(0, 3).join(" · ") || "no explicit lock"; const req = entry.requirements || {}; const reqLabel = entry.type === "workflows" ? "requirements being verified" : `${escapeHtml(entry.confidence || "low")} confidence`; const rankLabel = viewRank ? `#${viewRank} in view · #${entry.rank} in ${escapeHtml(entry.lane_label)}` : `#${entry.rank} in ${escapeHtml(entry.lane_label)}`; const saved = getSaved().includes(entry.id); const first = entryMedia(entry)[0]; return `<article class="entry-card tier-${text(entry.tier).toLowerCase()}" data-entry-id="${entry.id}" data-entry-slug="${escapeHtml(entry.slug)}" data-composite="${entry.composite}" data-vram="${vramValue(entry.vram_badge)}" data-base="${escapeHtml(entry.base_model)}" data-tasks="${escapeHtml((entry.outputs || []).join(","))}" data-freshness="${escapeHtml(entry.latest_version && entry.latest_version.updated_at || "")}" data-saved-id="${entry.id}"><a class="card-preview" href="${href}" aria-label="open ${escapeHtml(entry.name)}">${mediaMarkup(entry, first)}${entry.preview_gated && !state.mature ? `<span class="mature-cover">preview hidden · unlock in header</span>` : ""}<span class="preview-corner">${escapeHtml(entry.type)}</span></a><div class="card-copy"><div class="rank-row"><span class="tier-badge" title="${escapeHtml(entry.tier_note)}">${escapeHtml(entry.tier)}</span><span class="rank-label">${rankLabel}</span><span class="score">${(number(entry.composite) / 10).toFixed(1)} / 10</span></div><h3><a href="${href}">${escapeHtml(entry.name)}</a></h3><p class="purpose">${escapeHtml(entry.purpose)}</p><p class="card-meta"><span>${escapeHtml(entry.type)}</span><span>${escapeHtml(entry.base_model)}</span><span>${escapeHtml(entry.vram_badge)} gb <em>est.</em></span></p><p class="stack-formula"><span>stack</span> ${escapeHtml(entry.stack)}</p><ul class="stats-trio" aria-label="community stats"><li><strong>${formatCount(entry.stats.downloads.value)}</strong><span>downloads</span><small>pulled ${dateLabel(entry.stats.downloads.pulled_at)}</small></li><li><strong>${formatCount(entry.stats.thumbs.value)}</strong><span>thumbs</span><small>pulled ${dateLabel(entry.stats.thumbs.pulled_at)}</small></li><li><strong>${formatCount(entry.stats.comments.value)}</strong><span>comments</span><small>pulled ${dateLabel(entry.stats.comments.pulled_at)}</small></li></ul><div class="chip-row"><span class="chip">${escapeHtml(locks)}</span><span class="chip">${outputs}</span></div><div class="card-footer"><span class="requirements-badge">${reqLabel}</span><button class="save-button ${saved ? "is-saved" : ""}" type="button" data-save-entry="${entry.id}" aria-label="save ${escapeHtml(entry.name)}">${saved ? "♥" : "♡"}</button></div></div></article>`; }

  function expandQuery(query) { const lower = query.toLowerCase().trim(); const terms = [lower]; Object.entries(state.synonyms).forEach(([key, values]) => { if (lower.includes(key)) terms.push(...values); }); return [...new Set(terms.filter(Boolean))]; }
  function matchesQuery(item, terms) { const haystack = [item.name, item.original_name, item.creator, item.purpose, item.verdict, item.base_model, ...(item.locks || []), ...(item.outputs || [])].join(" ").toLowerCase(); return terms.some((term) => term.split(/\s+/).every((part) => haystack.includes(part))); }
  function recentQueries() { try { return JSON.parse(localStorage.getItem("civitai-library.recent-searches") || "[]"); } catch (_) { return []; } }
  function rememberQuery(query, scope) { if (!query.trim() || scope === "mature") return; try { const next = [query.trim(), ...recentQueries().filter((item) => item !== query.trim())].slice(0, 5); localStorage.setItem("civitai-library.recent-searches", JSON.stringify(next)); } catch (_) {} }
  function renderRecent() { const element = qs("[data-recent-searches]"); if (!element) return; const items = recentQueries(); element.hidden = !items.length; element.innerHTML = items.length ? `recent: ${items.map((item) => `<button type="button" data-query="${escapeHtml(item)}">${escapeHtml(item)}</button>`).join("")}` : ""; }
  function searchResults(query, scope) { const terms = expandQuery(query); let source = scope === "mature" ? state.matureIndex : state.sfwIndex; if (scope === "lane") { const lane = body.dataset.lane; source = source.filter((item) => item.lane === lane); } if (scope === "saved") { const saved = getSaved(); source = source.filter((item) => saved.includes(item.id)); } const hits = source.filter((item) => matchesQuery(item, terms)); return { hits, source, expanded: terms.length > 1, terms }; }
  function renderSearch(query) { const output = qs("[data-search-results]"); if (!output) return; const scope = qs("[data-search-scope]")?.value || "all-sfw"; if (!query.trim()) { output.innerHTML = ""; return; } const result = searchResults(query, scope); const interpretation = qs("[data-interpretation]"); if (interpretation) { interpretation.hidden = !result.expanded; interpretation.textContent = result.expanded ? `we read that as: ${result.terms.slice(1).join(" · ")}` : ""; } if (!result.hits.length) { const rescue = result.source.slice(0, 3); output.innerHTML = `<div class="empty-search"><p class="eyebrow">no exact match</p><h3>nothing broke. loosen one word.</h3><p>try one of these verified routes, or search by the original creator/name alias.</p><div class="intent-row">${rescue.map((item) => `<button type="button" class="intent-chip" data-query="${escapeHtml(item.name)}">${escapeHtml(item.name)} ↗</button>`).join("")}</div></div>`; return; } output.innerHTML = `<div class="search-heading"><span>${result.hits.length} result${result.hits.length === 1 ? "" : "s"} · ${scope}</span><button type="button" class="text-link" data-clear-search>clear</button></div><div class="entry-grid">${result.hits.slice(0, 12).map((item) => { const full = state.entries.find((entry) => entry.id === item.id); return full ? cardMarkup(full, null, full.lane === "nsfw") : ""; }).join("")}</div>`; }
  async function initSearch() { try { state.sfwIndex = await fetchJson(`${root}data/search-index-sfw.json`); state.index = state.sfwIndex; const synonyms = await fetchJson(`${root}data/synonyms.json`); state.synonyms = synonyms.synonyms || {}; if (body.hasAttribute("data-home")) { const data = await fetchJson(`${root}data/entries-sfw.json`); state.entries = data.entries || []; } } catch (_) { state.sfwIndex = []; state.index = []; } qsa("[data-search-form]").forEach((form) => form.addEventListener("submit", (event) => { event.preventDefault(); const input = qs("[data-search-input]", form); const query = input ? input.value : ""; const scope = qs("[data-search-scope]")?.value || "all-sfw"; rememberQuery(query, scope); if (qs("[data-search-results]")) renderSearch(query); else location.href = `${root}?q=${encodeURIComponent(query)}&scope=${encodeURIComponent(scope)}`; renderRecent(); })); qsa("[data-query]").forEach((button) => button.addEventListener("click", () => { const input = qs("[data-search-input]"); if (input) { input.value = button.dataset.query; input.focus(); renderSearch(input.value); } })); document.addEventListener("click", (event) => { const queryButton = event.target.closest("[data-query]"); if (queryButton && !queryButton.closest(".intent-row")) { const input = qs("[data-search-input]"); if (input) { input.value = queryButton.dataset.query; input.focus(); renderSearch(input.value); } } const clear = event.target.closest("[data-clear-search]"); if (clear) { const input = qs("[data-search-input]"); if (input) input.value = ""; renderSearch(""); } }); qsa("[data-search-input]").forEach((input) => input.addEventListener("input", () => { if (qs("[data-search-results]")) renderSearch(input.value); })); const params = new URLSearchParams(location.search); const initial = params.get("q"); const initialScope = params.get("scope"); const scopeSelect = qs("[data-search-scope]"); if (initialScope && scopeSelect && [...scopeSelect.options].some((option) => option.value === initialScope && !option.disabled)) scopeSelect.value = initialScope; const input = qs("[data-search-input]"); if (initial && input) { input.value = initial; renderSearch(initial); } renderRecent(); }

  function selectedFilters() { return state.selected; }
  function populateFiltersFromData() { ["base", "task"].forEach((group) => { const wrap = qs(`[data-filter-group-wrap="${group}"]`); const choices = wrap && qs(".filter-choices", wrap); if (!choices) return; const values = group === "base" ? [...new Set(state.entries.map((entry) => entry.base_model))].sort() : [...new Set(state.entries.flatMap((entry) => entry.outputs || []))].sort(); values.forEach((value) => { if (qs(`[data-filter-group="${group}"][data-filter-value="${CSS.escape(value)}"]`)) return; const button = document.createElement("button"); button.type = "button"; button.className = "filter-choice"; button.dataset.filterGroup = group; button.dataset.filterValue = value; button.innerHTML = `${escapeHtml(group === "task" ? value.replaceAll("-", " ") : value)} <span class="chip-count">0</span>`; choices.appendChild(button); }); }); }
  function predicate(entry, ignoreGroup) { return Object.entries(selectedFilters()).every(([group, value]) => { if (group === ignoreGroup || !value || value === "all") return true; if (group === "vram") return vramValue(entry.vram_badge) <= Number(value); if (group === "base") return entry.base_model === value; if (group === "task") return (entry.outputs || []).includes(value); if (group === "freshness") { const age = (Date.now() - dateOnly(entry.latest_version && entry.latest_version.updated_at)) / 86400000; return age <= Number(value); } if (group === "type") return entry.type.includes(value); if (group === "inputs") return (entry.inputs || []).includes(value); if (group === "locks") return (entry.locks || []).includes(value); if (group === "duration") return Boolean(entry.duration); if (group === "audio") return (entry.audio || []).length > 0; return true; }); }
  function sortEntries(entries) { return [...entries].sort((a, b) => state.sort === "latest" ? dateOnly(b.latest_version.updated_at) - dateOnly(a.latest_version.updated_at) : b.composite - a.composite); }
  function filterCards() { const results = qs("#lane-results"); if (!results) return; const filtered = sortEntries(state.entries.filter((entry) => predicate(entry))); const mature = body.dataset.lane === "mature"; if (!filtered.length) { const rescue = state.entries.slice(0, 3); results.innerHTML = `<div class="empty-search"><p class="eyebrow">zero-yield view</p><h3>that combination is too narrow for this pull.</h3><p>we relaxed nothing silently. start with the nearest concept:</p><div class="entry-grid">${rescue.map((entry) => cardMarkup(entry, null, mature)).join("")}</div></div>`; } else { const groups = ["S", "A", "B", "C"].map((tier) => { const items = filtered.filter((entry) => entry.tier === tier); if (!items.length) return ""; return `<section class="tier-band"><div class="band-heading"><span class="band-index">${tier.toLowerCase()}</span><div><h2>${tier} tier</h2><p>${escapeHtml(items[0].tier_note)}</p></div><span class="band-count">${items.length} in view</span></div><div class="entry-grid">${items.map((entry, index) => cardMarkup(entry, index + 1, mature)).join("")}</div></section>`; }).join(""); results.innerHTML = groups; } updateCounts(); observeBands(); updateSaveButtons(); }
  function updateCounts() { qsa("[data-filter-group][data-filter-value]").forEach((button) => { const group = button.dataset.filterGroup; const value = button.dataset.filterValue; const count = value === "all" ? state.entries.filter((entry) => predicate(entry, group)).length : state.entries.filter((entry) => { state.selected[group] = value; const okay = predicate(entry); delete state.selected[group]; return okay; }).length; const countElement = qs(".chip-count", button); if (countElement) { countElement.textContent = String(count); countElement.classList.remove("count-swap"); void countElement.offsetWidth; countElement.classList.add("count-swap"); } button.disabled = count === 0 && value !== "all"; }); }
  function initFilterEvents() { document.addEventListener("click", (event) => { const choice = event.target.closest("[data-filter-group][data-filter-value]"); if (choice) { const group = choice.dataset.filterGroup; state.selected[group] = choice.dataset.filterValue; qsa(`[data-filter-group="${CSS.escape(group)}"]`).forEach((button) => button.classList.toggle("active", button.dataset.filterValue === state.selected[group])); filterCards(); } const sortChoice = event.target.closest("[data-sort-choice]"); if (sortChoice) { state.sort = sortChoice.dataset.sortChoice; qsa("[data-sort-choice]").forEach((button) => button.classList.toggle("active", button === sortChoice)); filterCards(); } const more = event.target.closest("[data-more-toggle]"); if (more) { const panel = qs("[data-more-filters]"); if (panel) { const opening = panel.hidden; panel.hidden = !opening; more.setAttribute("aria-expanded", String(opening)); more.textContent = opening ? "− less" : "+ more"; } } }); }
  async function initLane() { const lane = body.dataset.lane; if (!lane || lane === "mature") return; try { const data = await fetchJson(`${root}data/entries-sfw.json`); state.entries = data.entries.filter((entry) => entry.lane === lane); updateSaveButtons(); updateCounts(); observeBands(); } catch (_) {} }
  async function loadMatureData() { if (!body.hasAttribute("data-mature-route") && !body.hasAttribute("data-mature-detail") && !body.hasAttribute("data-home")) return; try { const data = await fetchJson(`${root}data/mature-entries.json`); const matureEntries = data.entries || []; state.entries = body.hasAttribute("data-home") ? [...state.entries.filter((entry) => entry.lane !== "nsfw"), ...matureEntries] : matureEntries; state.matureIndex = await fetchJson(`${root}data/search-index-mature.json`); if (body.hasAttribute("data-mature-route")) { const skeleton = qs("[data-mature-skeleton]"); const loaded = qs("[data-mature-loaded]"); if (skeleton) skeleton.hidden = true; if (loaded) loaded.hidden = false; populateFiltersFromData(); filterCards(); } if (body.hasAttribute("data-mature-detail")) renderMatureDetail(); const input = qs("[data-search-input]"); if (input && qs("[data-search-scope]")?.value === "mature") renderSearch(input.value); } catch (_) { const skeleton = qs("[data-mature-skeleton]"); if (skeleton) skeleton.innerHTML = "<p>mature metadata could not be loaded. check the connection and try again.</p>"; } }
  function renderMatureDetail() { const target = qs("#detail-app"); const slug = body.dataset.matureDetail; const entry = state.entries.find((item) => item.slug === slug); if (!target || !entry) return; target.hidden = false; qs(".skeleton-detail")?.remove(); const gallery = entryMedia(entry); target.innerHTML = `<div class="breadcrumb"><a href="${root}mature/">mature</a><span>/</span><span>entry</span></div><section class="detail-heading"><div><p class="eyebrow">mature / ${escapeHtml(entry.type)}</p><h1>${escapeHtml(entry.name)}</h1><p class="alias">source name: <span>${escapeHtml(entry.original_name)}</span> · by ${escapeHtml(entry.creator.username)}</p></div><div class="detail-rank"><span class="tier-badge">${escapeHtml(entry.tier)}</span><strong>#${entry.rank} in mature</strong><span>${(number(entry.composite) / 10).toFixed(1)} / 10</span></div></section><div class="detail-layout"><div class="detail-main"><section class="proof-gallery"><div class="section-head"><div><p class="eyebrow">output proof</p><h2>preview unlocked for this session.</h2></div><span class="gallery-note">${gallery.length} pulled examples</span></div><div class="gallery-main" data-gallery-main data-gallery-index="0" data-gallery-items="${escapeHtml(JSON.stringify(gallery))}">${mediaMarkup(entry, gallery[0])}<button class="gallery-open" type="button" data-lightbox-open aria-label="open gallery full screen">open gallery ↗</button></div></section><section class="editor-note"><p class="eyebrow">editor’s note</p><p class="verdict">“${escapeHtml(entry.verdict_line)}”</p><p>${escapeHtml(entry.purpose)}</p></section><section class="import-panel"><p class="eyebrow">import / pinned version ${escapeHtml(entry.latest_version.name)}</p><h2>what you need</h2><div class="requirements-status"><span class="status-dot"></span>requirements being verified</div><p>${escapeHtml((entry.requirements.models || []).map((model) => model.our_ref || model).join(" · "))}</p><a class="button coral download-button" href="${root}mature/workflows/${encodeURIComponent(entry.slug)}.json" download data-download>download comfyui json ↗</a><p>download the JSON, then open the linked original source archive when one is available.</p></section></div><aside class="proof-rail"><div class="rail-sticky"><p class="eyebrow">decision proof</p><h2>why it sits here.</h2><div class="rail-badge pending"><span>●</span>not tested by us yet</div><dl class="proof-list"><div><dt>tier / rank</dt><dd>${entry.tier} · #${entry.rank} in mature</dd></div><div><dt>vram <em>est.</em></dt><dd>${escapeHtml(entry.vram_badge)} gb</dd></div><div><dt>base model</dt><dd>${escapeHtml(entry.base_model)}</dd></div><div><dt>freshness</dt><dd>${dateLabel(entry.latest_version.updated_at)}</dd></div></dl></div></aside></div>`; }

  function updateSaveButtons() { const saved = getSaved(); qsa("[data-save-entry]").forEach((button) => { const isSaved = saved.includes(Number(button.dataset.saveEntry)); button.classList.toggle("is-saved", isSaved); button.textContent = isSaved ? "♥" : "♡"; }); }
  function initSave() { document.addEventListener("click", (event) => { const button = event.target.closest("[data-save-entry]"); if (!button) return; event.preventDefault(); event.stopPropagation(); const id = Number(button.dataset.saveEntry); const saved = getSaved(); const next = saved.includes(id) ? saved.filter((item) => item !== id) : [...saved, id]; saveSaved(next); updateSaveButtons(); toast(next.includes(id) ? "saved to your shortlist" : "removed from your shortlist"); }); }

  function selectGallery(index) { const main = qs("[data-gallery-main]"); if (!main) return; const items = JSON.parse(main.dataset.galleryItems || "[]"); const entry = state.entries.find((item) => String(item.id) === String(body.dataset.entryId)); if (entry && items[index]) { main.dataset.galleryIndex = String(index); main.innerHTML = `${mediaMarkup(entry, items[index])}<button class="gallery-open" type="button" data-lightbox-open aria-label="open gallery full screen">open gallery ↗</button>`; qsa("[data-gallery-index]").forEach((item) => item.classList.toggle("active", Number(item.dataset.galleryIndex) === index)); } }
  function initGallery() { document.addEventListener("click", (event) => { const thumb = event.target.closest("[data-gallery-index]"); if (thumb && qs("[data-gallery-main]")) selectGallery(Number(thumb.dataset.galleryIndex)); if (event.target.closest("[data-lightbox-open]")) { const main = qs("[data-gallery-main]"); if (main) { const items = JSON.parse(main.dataset.galleryItems || "[]"); openLightbox(items, Number(main.dataset.galleryIndex || 0)); } } }); qsa(".gallery-thumb").forEach((thumb) => thumb.addEventListener("mouseenter", () => { if (window.innerWidth > 900) selectGallery(Number(thumb.dataset.galleryIndex)); })); }
  function openLightbox(items, index) { if (!items.length) return; const entry = state.entries.find((item) => String(item.id) === String(body.dataset.entryId)); if (entry && entry.preview_gated && !state.mature) { toast("unlock mature previews in the header first"); return; } state.lightbox.items = items; state.lightbox.index = index; const lightbox = qs("#lightbox"); if (!lightbox) return; renderLightbox(); if (lightbox.showModal) lightbox.showModal(); else lightbox.setAttribute("open", ""); preloadLightbox(); }
  function renderLightbox() { const item = state.lightbox.items[state.lightbox.index]; const image = qs("[data-lightbox-image]"); const video = qs("[data-lightbox-video]"); const caption = qs("[data-lightbox-caption]"); if (!item) return; if (item.kind === "video") { if (image) { image.hidden = true; image.removeAttribute("src"); } if (video) { video.style.display = "block"; video.src = item.url; video.load(); } } else { if (video) { video.style.display = "none"; video.removeAttribute("src"); video.load(); } if (image) { image.hidden = false; image.src = item.url; image.alt = `preview ${state.lightbox.index + 1} of ${state.lightbox.items.length}`; } } if (caption) caption.textContent = `preview ${state.lightbox.index + 1} of ${state.lightbox.items.length}`; }
  function preloadLightbox() { [1, 2].forEach((offset) => { const item = state.lightbox.items[(state.lightbox.index + offset) % state.lightbox.items.length]; if (item && item.kind !== "video") { const image = new Image(); image.src = item.url; } }); }
  function shiftLightbox(delta) { if (!state.lightbox.items.length) return; state.lightbox.index = (state.lightbox.index + delta + state.lightbox.items.length) % state.lightbox.items.length; renderLightbox(); preloadLightbox(); }
  function initLightbox() { qs("[data-lightbox-close]")?.addEventListener("click", () => qs("#lightbox")?.close()); qs("[data-lightbox-prev]")?.addEventListener("click", () => shiftLightbox(-1)); qs("[data-lightbox-next]")?.addEventListener("click", () => shiftLightbox(1)); document.addEventListener("keydown", (event) => { const box = qs("#lightbox"); if (!box || !box.open) return; if (event.key === "ArrowLeft") shiftLightbox(-1); if (event.key === "ArrowRight") shiftLightbox(1); if (event.key === "Escape") box.close(); }); let touchX = 0; qs("#lightbox")?.addEventListener("touchstart", (event) => { touchX = event.changedTouches[0].clientX; }, { passive: true }); qs("#lightbox")?.addEventListener("touchend", (event) => { const delta = event.changedTouches[0].clientX - touchX; if (Math.abs(delta) > 45) shiftLightbox(delta < 0 ? 1 : -1); }, { passive: true }); }
  function initDownload() { document.addEventListener("click", (event) => { const button = event.target.closest("[data-download]"); if (!button) return; button.dataset.originalLabel = button.textContent; window.setTimeout(() => { button.textContent = "json ready ✓"; }, 120); window.setTimeout(() => { button.textContent = button.dataset.originalLabel; }, 2600); }); }
  function initCopy() { document.addEventListener("click", async (event) => { const button = event.target.closest("[data-copy]"); if (!button) return; try { await navigator.clipboard.writeText(button.dataset.copy); toast("copied"); } catch (_) { toast("copy unavailable; select the text"); } }); }
  function observeBands() { if (!("IntersectionObserver" in window)) { qsa(".band-heading").forEach((item) => item.classList.add("is-visible")); return; } const observer = new IntersectionObserver((items) => items.forEach((item) => { if (item.isIntersecting) { item.target.classList.add("is-visible"); observer.unobserve(item.target); } }), { threshold: .15 }); qsa(".band-heading").forEach((item) => observer.observe(item)); }
  function init() { initMature(); initSave(); initGallery(); initLightbox(); initDownload(); initCopy(); initFilterEvents(); initSearch(); initLane(); }
  document.addEventListener("DOMContentLoaded", init);
})();
'''


if __name__ == "__main__":
    main()
