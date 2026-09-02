#!/usr/bin/env python3
"""Build the v2 internal pipeline workbench from staged JSON files.

This is intentionally separate from the v1 generator. The default build never
invents entries: a missing or empty staged file becomes an explicit empty state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
STAGED = ROOT / "data" / "staged"

STAGES = (
    {"id": "persona", "label": "Persona", "short": "01", "focus": "realism bases + identity"},
    {"id": "motion", "label": "Motion", "short": "02", "focus": "image-to-video + movement"},
    {"id": "speech-voice", "label": "Speech & Voice", "short": "03", "focus": "talking heads + voices"},
    {"id": "camera-angle", "label": "Camera & Angle", "short": "04", "focus": "posing + perspective"},
    {"id": "ads", "label": "Ads Assembly", "short": "05", "focus": "product + UGC pipelines"},
    {"id": "nsfw", "label": "NSFW / OF", "short": "06", "focus": "explicit production lane"},
)

STAGE_FILES = {stage["id"]: stage["id"].upper().replace("-", "_") for stage in STAGES}

DATA_CONTRACT = {
    "stage",
    "generated",
    "entries",
    "id",
    "our_name",
    "source_name",
    "purpose",
    "composite",
    "tier",
    "visual_class",
    "quality",
    "nsfw_bucket",
    "baseModel",
    "vram_class",
    "tradeoff",
    "open_closed",
    "stats",
    "pulled_at",
    "preview",
    "gallery",
    "stacks_on",
    "verdict_keep",
    "civitai_url",
    "requirements",
}


class EnhancementLayers:
    """The stackable class that sits on top of any pipeline stage."""

    key = "layers"
    label = "Enhancement Layers"
    source_file = "LAYERS.json"
    examples = ("skin detail", "lighting", "motion physics", "anatomy fixes", "upscale")

    @classmethod
    def read(cls) -> dict[str, Any]:
        return read_staged(cls.source_file, expected_stage="LAYERS")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def read_staged(filename: str, expected_stage: str) -> dict[str, Any]:
    """Read the dictated contract without fabricating a fallback entry."""
    path = STAGED / filename
    if not path.exists():
        return {"stage": expected_stage, "generated": None, "entries": [], "missing": True}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "stage": expected_stage,
            "generated": None,
            "entries": [],
            "error": f"Could not read {filename}: {error}",
        }
    if not isinstance(payload, dict):
        return {"stage": expected_stage, "generated": None, "entries": [], "error": "Root must be an object"}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    return {
        "stage": str(payload.get("stage") or expected_stage),
        "generated": payload.get("generated"),
        "entries": [entry for entry in entries if isinstance(entry, dict)],
        "missing": False,
        "error": None,
    }


def source_label(stage_id: str) -> str:
    return "LAYERS" if stage_id == "layers" else STAGE_FILES[stage_id]


def kept_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Vetted entries only: clean vision passes or manager curation keeps."""
    return [entry for entry in data.get("entries") or [] if entry.get("review_flag") is False]


def media_kind(url: str) -> str:
    return "video" if re.search(r"\.(?:mp4|webm|mov)(?:$|\?)", url, re.I) else "image"


def media_urls(entry: dict[str, Any]) -> list[str]:
    preview = entry.get("preview") or {}
    candidates: list[str] = []
    for key in ("video", "url_width450", "url_original"):
        value = preview.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)
    gallery = entry.get("gallery") or []
    for value in gallery:
        if isinstance(value, str) and value:
            candidates.append(value)
        elif isinstance(value, dict) and isinstance(value.get("url"), str):
            candidates.append(value["url"])
    seen: set[str] = set()
    return [url for url in candidates if not (url in seen or seen.add(url))][:8]


def renderable_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Vetted entries without a preview are cut before HTML is emitted (engines render text-first)."""
    return [entry for entry in kept_entries(data) if entry.get("kind") == "engine" or media_urls(entry)]


def entry_name(entry: dict[str, Any]) -> str:
    return str(entry.get("our_name") or entry.get("source_name") or f"Entry {entry.get('id', '—')}")


def entry_role(entry: dict[str, Any], stage_id: str) -> str:
    explicit = str(entry.get("stack_role") or "").lower()
    if explicit in {"base", "layer", "motion", "voice"}:
        return explicit
    return {"persona": "base", "motion": "motion", "speech-voice": "voice", "layers": "layer"}.get(stage_id, "base")


def vram_number(value: Any) -> int:
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def entry_models(entry: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = entry.get("requirements") or {}
    models = requirements.get("models") or []
    return [model for model in models if isinstance(model, dict)]


def entry_disk_mb(entry: dict[str, Any]) -> int:
    direct = entry.get("disk_mb")
    if isinstance(direct, (int, float)):
        return int(direct)
    return sum(int(model.get("size_mb") or 0) for model in entry_models(entry))


def exact_version_url(entry: dict[str, Any]) -> str:
    """Return only an exact-version URL; model-page fallbacks are withheld."""
    for key in ("version_url", "civitai_version_url"):
        value = entry.get(key)
        if isinstance(value, str) and ("modelVersionId=" in value or "/model-versions/" in value):
            return value
    for model in entry_models(entry):
        value = model.get("url")
        if isinstance(value, str) and ("modelVersionId=" in value or "/model-versions/" in value):
            return value
    value = entry.get("civitai_url")
    if isinstance(value, str) and ("modelVersionId=" in value or "/model-versions/" in value):
        return value
    return ""


def demo_art(label: str, background: str, foreground: str) -> str:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1200">
      <rect width="900" height="1200" fill="{background}"/>
      <path d="M0 860L260 590l180 140 220-310 240 340v440H0z" fill="#101417" opacity=".48"/>
      <circle cx="690" cy="190" r="120" fill="{foreground}" opacity=".16"/>
      <text x="54" y="1080" fill="{foreground}" font-family="monospace" font-size="42">{label}</text>
    </svg>'''
    return "data:image/svg+xml," + quote(svg)


def demo_entry(stage: dict[str, Any], index: int) -> dict[str, Any]:
    role = entry_role({}, stage["id"]) if index == 0 else "layer" if index == 1 else "base"
    if stage["id"] == "motion":
        role = "motion" if index == 0 else role
    if stage["id"] == "speech-voice":
        role = "voice" if index == 0 else role
    if stage["id"] == "layers":
        role = "layer"
    title = f"[DEMO] {stage['label']} {index + 1}"
    art = demo_art(title, ("#29363a", "#3a2d2a", "#243843")[index], ("#f1b35b", "#72d7d1", "#9ed69f")[index])
    preview: dict[str, Any] = {"url_width450": art, "url_original": art}
    if index == 1:
        preview["video"] = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
    gallery = [art]
    if index == 2:
        gallery = [
            art,
            demo_art(title + " / 02", "#3a2d2a", "#72d7d1"),
            demo_art(title + " / 03", "#243843", "#f1b35b"),
        ]
    model_name = f"demo-{slugify(stage['id'])}-{index + 1}.safetensors"
    model_url = f"https://civitai.com/models/{900000 + index}?modelVersionId={910000 + index}"
    return {
        "id": f"demo-{stage['id']}-{index + 1}",
        "our_name": title,
        "source_name": title,
        "purpose": ("identity anchor", "fast iteration", "comparison frame")[index],
        "composite": 91 - index * 4,
        "tier": "DEMO",
        "visual_class": "layout sample",
        "quality": 8 - index,
        "nsfw_bucket": "explicit" if stage["id"] == "nsfw" else "safe",
        "baseModel": "Demo model family",
        "vram_class": f"{12 + index * 4} GB",
        "tradeoff": (["max quality"], ["fastest"], ["low vram"])[index],
        "open_closed": "open",
        "stats": {"downloadCount": 1200 - index * 170, "thumbsUpCount": 108 - index * 9},
        "pulled_at": "2026-09-02T00:00:00+00:00",
        "preview": preview,
        "gallery": gallery,
        "stacks_on": [stage["id"].upper()],
        "verdict_keep": True,
        "civitai_url": model_url,
        "requirements": {
            "models": [{"name": model_name, "folder": "models/checkpoints", "size_mb": 4096 + index * 1024, "url": model_url}],
            "nodes": [],
        },
        "stack_role": role,
        "verdict_line": "Layout-only sample; replace with a vetted entry before use.",
    }


def data_for_stage(stage: dict[str, Any], demo: bool = False) -> dict[str, Any]:
    data = read_staged(f"{source_label(stage['id'])}.json", source_label(stage["id"]))
    if demo:
        return {
            "stage": source_label(stage["id"]),
            "generated": "demo-only",
            "entries": [demo_entry(stage, index) for index in range(3)],
            "pulled": 3,
            "demo": True,
        }
    data["pulled"] = len(data.get("entries") or [])
    data["kept_candidates"] = len(kept_entries(data))
    preview_candidates = renderable_entries(data)
    data["preview_candidates"] = len(preview_candidates)
    data["underfilled"] = bool(preview_candidates) and len(preview_candidates) < 3
    data["entries"] = preview_candidates if len(preview_candidates) >= 3 else []
    return data


def nav_markup(current: str, root: bool = False) -> str:
    prefix = "" if root else "../"
    links = []
    for stage in STAGES:
        active = " is-active" if current == stage["id"] else ""
        links.append(
            f'<a class="stage-link{active}" href="{prefix}{stage["id"]}/" '
            f'data-stage="{esc(stage["id"])}"><span>{esc(stage["short"])}</span>{esc(stage["label"])}</a>'
        )
    links.append(
        f'<a class="stage-link layer-link{" is-active" if current == "layers" else ""}" '
        f'href="{prefix}layers/" data-stage="layers"><span>+</span>Layers</a>'
    )
    return "\n".join(links)


def page_shell(title: str, current: str, body: str, root: bool = False) -> str:
    prefix = "" if root else "../"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>{esc(title)} · Pipeline workbench</title>
  <link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body data-page="{esc(current)}">
  <header class="topbar">
    <a class="wordmark" href="{prefix}persona/"><span class="wordmark-mark">//</span><span>pipeline / v2</span></a>
    <div class="topbar-status"><span class="status-dot"></span> local staged data <span class="status-divider"></span> NSFW ON</div>
  </header>
  <nav class="stage-nav" aria-label="Pipeline stages">
    <div class="stage-nav-inner">
      {nav_markup(current, root=root)}
    </div>
  </nav>
  <main class="workbench">
    {body}
  </main>
  <script src="{prefix}assets/app.js" defer></script>
</body>
</html>"""


def empty_state(stage: dict[str, Any], data: dict[str, Any]) -> str:
    if data.get("error"):
        note = data["error"]
    elif data.get("missing"):
        note = f"data/staged/{source_label(stage['id'])}.json is not present yet."
    elif data.get("underfilled"):
        note = f"{data['preview_candidates']} kept preview entries are held until this stage has at least three."
    elif data.get("kept_candidates"):
        note = f"{data['kept_candidates']} kept candidate(s) have no working preview and were cut."
    elif data.get("entries") or data.get("pulled"):
        note = "The pull contains candidates, but none has verdict_keep=true yet."
    else:
        note = "The staged file has no entries yet."
    return f"""
    <section class="empty-state" aria-live="polite">
      <div class="empty-sigil">{esc(stage["short"])}</div>
      <div>
        <p class="eyebrow">No staged entries</p>
        <h2>0 kept after filters</h2>
        <p class="empty-note">{esc(note)}</p>
        <a class="text-link" href="#cut-panel">View cut panel <span>↗</span></a>
      </div>
    </section>
    """


def layer_class_markup(data: dict[str, Any]) -> str:
    count = len(kept_entries(data))
    if count:
        summary = f"{count} staged layer{'s' if count != 1 else ''} ready to attach."
        content = f'<p class="layer-summary">{esc(summary)}</p>'
    else:
        content = '<p class="layer-summary">No layer files loaded. This class remains available to stack on any stage.</p>'
    chips = "".join(f'<span class="layer-chip">{esc(example)}</span>' for example in EnhancementLayers.examples)
    return f"""
    <section class="layers-class" id="layers">
      <div class="section-kicker"><span class="section-rule"></span>Stackable class</div>
      <div class="layers-heading">
        <div>
          <h2>{esc(EnhancementLayers.label)}</h2>
          {content}
        </div>
        <span class="class-badge">CLASS · NOT A STAGE</span>
      </div>
      <div class="layer-chips" aria-label="Layer examples">{chips}</div>
      <p class="layer-contract">Each layer carries <code>stacks_on</code>: stage(s) and base model(s).</p>
    </section>
    """


def cut_panel(stage: dict[str, Any], data: dict[str, Any]) -> str:
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    source = source_label(stage["id"])
    kept = len(kept_entries(data))
    if data.get("underfilled"):
        reason = f"{data.get('preview_candidates', kept)} kept preview entries are held until the stage has at least three."
    elif kept:
        reason = "Kept entries have explicit verdicts and working previews; excluded candidates remain in the pull record."
    elif pulled:
        reason = "Candidates were pulled, but no entry has both an explicit keep verdict and a working preview."
    else:
        reason = f"No staged candidates came from {source}.json yet."
    return f"""
    <section class="cut-panel" id="cut-panel">
      <div>
        <p class="eyebrow">Funnel record</p>
        <h2>pulled {pulled} <span>→</span> kept {kept}</h2>
        <a class="text-link" href="#cut-reasons">why this count <span>↗</span></a>
      </div>
      <p class="cut-reason" id="cut-reasons">{esc(reason)} Preview-less candidates are cut before render.</p>
    </section>
    """


def entry_chip_markup(entry: dict[str, Any], stage_id: str) -> str:
    chips = []
    tradeoff = entry.get("tradeoff")
    if isinstance(tradeoff, list):
        chips.extend(str(value) for value in tradeoff if value)
    elif tradeoff:
        chips.append(str(tradeoff))
    if entry.get("vram_class"):
        chips.append(str(entry["vram_class"]))
    if entry.get("baseModel"):
        chips.append(str(entry["baseModel"]))
    if not chips:
        chips.append(f"role: {entry_role(entry, stage_id)}")
    return "".join(f'<span class="entry-chip">{esc(value)}</span>' for value in chips[:3])


def facet_values(entry: dict[str, Any]) -> list[str]:
    values: list[str] = []
    tradeoff = entry.get("tradeoff")
    if isinstance(tradeoff, list):
        values.extend(str(value).strip().lower() for value in tradeoff if value)
    elif tradeoff:
        values.append(str(tradeoff).strip().lower())
    purpose = str(entry.get("purpose") or "").strip().lower()
    if purpose:
        values.append(f"purpose: {purpose}")
    return list(dict.fromkeys(values))


def search_text(entry: dict[str, Any]) -> str:
    values = [entry_name(entry), entry.get("source_name"), entry.get("purpose"), entry.get("baseModel"), entry.get("tradeoff")]
    return " ".join(str(value or "") for value in values).lower()


def score_value(entry: dict[str, Any]) -> str:
    value = entry.get("composite")
    if isinstance(value, (int, float)):
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return "—"


def score_payload(entry: dict[str, Any]) -> dict[str, Any]:
    stats = entry.get("stats") or {}
    return {
        "score": score_value(entry),
        "community": {
            "downloads": stats.get("downloadCount") if stats.get("downloadCount") is not None else "not staged",
            "thumbs_up": stats.get("thumbsUpCount") if stats.get("thumbsUpCount") is not None else "not staged",
        },
        "axes": {
            "quality": entry.get("quality") if entry.get("quality") is not None else "not staged",
            "lane fit": entry.get("lane_fit") if entry.get("lane_fit") is not None else "not staged",
            "freshness": entry.get("freshness") if entry.get("freshness") is not None else "not staged",
        },
        "verdict": entry.get("verdict_line") or "No decision note staged.",
        "pulled_at": entry.get("pulled_at") or "not staged",
    }


def score_popover_markup(entry: dict[str, Any]) -> str:
    payload = esc(json.dumps(score_payload(entry), ensure_ascii=False, separators=(",", ":")))
    return f'<button class="score-button" type="button" data-score-payload="{payload}" aria-expanded="false">score {esc(score_value(entry))}</button><div class="score-popover" hidden></div>'


def filter_bar(entries: list[dict[str, Any]]) -> str:
    facets = {"low vram", "max quality", "fastest"}
    for entry in entries:
        facets.update(facet_values(entry))
    chips = []
    for facet in sorted(facets):
        count = sum(facet in facet_values(entry) for entry in entries)
        chips.append(
            f'<button class="filter-chip" type="button" data-filter-facet="{esc(facet)}" '
            f'data-filter-count="{count}" aria-pressed="false" disabled>{esc(facet)} <b>{count}</b></button>'
        )
    return f"""
    <section class="filters" aria-label="Filter entries">
      <label class="search-field"><span>Find an entry</span><input id="entry-search" type="search" autocomplete="off" placeholder="name, purpose, model…"></label>
      <div class="filter-row"><button class="filter-chip is-all" type="button" data-filter-facet="" aria-pressed="true">all <b data-all-count>{len(entries)}</b></button>{''.join(chips)}</div>
    </section>
    """


def matrix_markup(stage: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    if not entries:
        body = '<p class="matrix-empty">No kept entries to compare yet. The matrix opens when three or more vetted previews land in this stage.</p>'
    else:
        groups: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            purpose = str(entry.get("purpose") or "general comparison")
            groups.setdefault(purpose, []).append(entry)
        if len(groups) > 1 and all(len(options) < 2 for options in groups.values()):
            groups = {stage["focus"]: entries}
        elif len(groups) > 1:
            remainder = [entry for options in groups.values() if len(options) < 2 for entry in options]
            groups = {purpose: options for purpose, options in groups.items() if len(options) >= 2}
            if remainder:
                groups["other options"] = remainder
        rows = []
        for purpose, options in groups.items():
            options_markup = "".join(
                f'<div class="matrix-option"><strong>{esc(entry_name(entry))}</strong><span>{entry_chip_markup(entry, stage["id"])}</span><em>score {esc(score_value(entry))}</em></div>'
                for entry in options[:4]
            )
            rows.append(f'<div class="matrix-row"><div class="matrix-need"><span>Need</span><strong>{esc(purpose)}</strong></div><div class="matrix-options">{options_markup}</div></div>')
        body = "".join(rows)
    return f"""
    <section class="decision-matrix" aria-label="Decision matrix">
      <div class="matrix-heading"><div><p class="eyebrow">Decision view</p><h2>Pick a need, compare the trade-off</h2></div><span class="matrix-count">{len(entries)} options</span></div>
      <div class="matrix-body">{body}</div>
    </section>
    """


def entry_payload(entry: dict[str, Any], stage_id: str) -> dict[str, Any]:
    models = []
    for model in entry_models(entry):
        models.append({
            "name": model.get("name") or "unnamed file",
            "folder": model.get("folder") or "folder not staged",
            "size_mb": int(model.get("size_mb") or 0),
            "url": model.get("url") or "",
        })
    return {
        "id": str(entry.get("id") or ""),
        "name": entry_name(entry),
        "role": entry_role(entry, stage_id),
        "stage": stage_id,
        "vram": vram_number(entry.get("vram_class")),
        "disk": entry_disk_mb(entry),
        "models": models,
        "exact_url": exact_version_url(entry),
    }


def entry_detail_markup(entry: dict[str, Any], stage_id: str) -> str:
    exact_url = exact_version_url(entry)
    models = entry_models(entry)
    model_rows = []
    for model in models:
        raw_url = model.get("url") if isinstance(model.get("url"), str) else ""
        url = raw_url if ("modelVersionId=" in raw_url or "/model-versions/" in raw_url) else ""
        url_markup = f'<a href="{esc(url)}" target="_blank" rel="noreferrer">exact file link ↗</a>' if url else "link not staged"
        model_rows.append(
            f'<li><strong>{esc(model.get("name") or "unnamed file")}</strong> · '
            f'{esc(model.get("folder") or "folder not staged")} · {esc(model.get("size_mb") or 0)} MB · {url_markup}</li>'
        )
    if not model_rows:
        model_rows.append("<li>No download rows staged.</li>")
    version_link = f'<a href="{esc(exact_url)}" target="_blank" rel="noreferrer">open vetted version ↗</a>' if exact_url else "exact version link not staged"
    stacks = entry.get("stacks_on") or []
    stacks_text = ", ".join(str(value) for value in stacks) if stacks else "none staged"
    return f"""
      <div class="card-detail" hidden>
        <div class="detail-grid">
          <div><span class="detail-label">Source</span><strong>{esc(entry.get("source_name") or "not staged")}</strong></div>
          <div><span class="detail-label">Base model</span><strong>{esc(entry.get("baseModel") or "not staged")}</strong></div>
          <div><span class="detail-label">Stacks on</span><strong>{esc(stacks_text)}</strong></div>
          <div><span class="detail-label">Version</span><strong>{version_link}</strong></div>
        </div>
        <p class="detail-verdict">{esc(entry.get("verdict_line") or "No decision note staged.")}</p>
        <ul class="manifest-preview">{"".join(model_rows)}</ul>
      </div>
    """


def media_markup(entry: dict[str, Any], stage_id: str) -> str:
    urls = media_urls(entry)
    if not urls:
        return '<div class="media-missing">preview cut</div>'
    first = urls[0]
    name = entry_name(entry)
    if media_kind(first) == "video":
        return (
            f'<video class="card-video" muted loop playsinline preload="metadata" '
            f'data-hover-video aria-label="Preview for {esc(name)}"><source src="{esc(first)}"></video>'
        )
    gallery_attr = esc(json.dumps(urls, ensure_ascii=False, separators=(",", ":")))
    return f'<img class="card-image" src="{esc(first)}" alt="Preview for {esc(name)}" loading="lazy" data-gallery="{gallery_attr}">'


def entry_card(entry: dict[str, Any], stage_id: str) -> str:
    payload = esc(json.dumps(entry_payload(entry, stage_id), ensure_ascii=False, separators=(",", ":")))
    role = entry_role(entry, stage_id)
    demo_badge = '<span class="demo-badge">[DEMO]</span>' if str(entry.get("tier")) == "DEMO" else ""
    open_state = str(entry.get("open_closed") or "status not staged").lower()
    explicit = str(entry.get("nsfw_bucket") or "").lower() in {"explicit", "nsfw", "adult"} or stage_id == "nsfw"
    media_class = "card-media is-explicit" if explicit else "card-media"
    facets = esc(json.dumps(facet_values(entry), ensure_ascii=False, separators=(",", ":")))
    demo_attr = ' data-demo="true"' if str(entry.get("tier")) == "DEMO" else ""
    return f"""
    <article class="entry-card" tabindex="0" aria-expanded="false"{demo_attr} data-entry-id="{esc(entry.get('id') or '')}" data-stack-role="{esc(role)}" data-stack-payload="{payload}" data-search="{esc(search_text(entry))}" data-facets="{facets}">
      <div class="{media_class}" data-gallery-surface>
        {media_markup(entry, stage_id)}
        <span class="media-index">{esc(role)}</span>
      </div>
      <div class="card-body">
        <div class="card-topline"><span class="open-badge">{esc(open_state)}</span>{demo_badge}</div>
        <h2 class="entry-name">{esc(entry_name(entry))}</h2>
        <p class="entry-purpose">{esc(entry.get("purpose") or "Purpose not staged")}</p>
        <div class="entry-chips">{entry_chip_markup(entry, stage_id)}</div>
        <div class="card-footer">{score_popover_markup(entry)}<span>VRAM {esc(entry.get("vram_class") or "—")}</span></div>
        {entry_detail_markup(entry, stage_id)}
      </div>
    </article>
    """


def stack_option(entry: dict[str, Any], stage_id: str) -> str:
    payload = esc(json.dumps(entry_payload(entry, stage_id), ensure_ascii=False, separators=(",", ":")))
    role = entry_role(entry, stage_id)
    return f"""
    <button class="stack-option" type="button" data-stack-entry="{payload}" aria-pressed="false">
      <span class="stack-option-main"><span class="stack-option-name">{esc(entry_name(entry))}</span><span class="stack-option-sub">{esc(stage_id)} · {esc(entry.get('vram_class') or 'VRAM —')}</span></span>
      <span class="stack-option-action">add</span>
    </button>
    """


def stack_builder(catalog: dict[str, list[dict[str, Any]]]) -> str:
    role_labels = (("base", "Base"), ("layer", "Layers"), ("motion", "Motion"), ("voice", "Voice"))
    groups = []
    for role, label in role_labels:
        options = []
        for stage_id, entries in catalog.items():
            for entry in entries:
                if entry_role(entry, stage_id) == role:
                    options.append(stack_option(entry, stage_id))
        if options:
            group_body = "".join(options[:4])
        else:
            group_body = '<p class="stack-empty">No vetted input loaded.</p>'
        groups.append(f'<section class="stack-slot" data-stack-slot="{role}"><h3>{label}</h3>{group_body}</section>')
    return f"""
    <aside class="stack-builder" id="stack-builder">
      <div class="stack-heading">
        <div><p class="eyebrow">Execution plan</p><h2>Stack builder</h2></div>
        <span class="stack-live"><span></span> live</span>
      </div>
      <p class="stack-copy">Choose one base, then add layers, motion, and voice. Totals update from the selected inputs.</p>
      <div class="stack-slots">{"".join(groups)}</div>
      <div class="stack-totals" aria-live="polite">
        <div><span>VRAM total</span><strong data-stack-vram>0 GB</strong></div>
        <div><span>Disk total</span><strong data-stack-disk>0 MB</strong></div>
      </div>
      <div class="manifest-heading"><h3>Download manifest</h3><button class="copy-all" type="button" data-copy-all disabled>copy all</button></div>
      <div class="manifest" data-stack-manifest><p class="manifest-empty">Select an input to build rows.</p></div>
      <p class="copy-status" data-copy-status aria-live="polite"></p>
    </aside>
    """


def render_stage(stage: dict[str, Any], data: dict[str, Any], generated_on: str, catalog: dict[str, list[dict[str, Any]]], root: bool = False) -> str:
    entries = kept_entries(data)
    entries = renderable_entries({**data, "entries": entries})
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    state = empty_state(stage, data) if not entries else f"""
    <section class="entry-grid" aria-label="{esc(stage['label'])} entries">
      {''.join(entry_card(entry, stage['id']) for entry in entries)}
    </section>
    """
    stage_content = filter_bar(entries) + matrix_markup(stage, entries) + state
    return page_shell(
        stage["label"],
        stage["id"],
        f"""
    <section class="stage-header">
      <div>
        <p class="eyebrow">Pipeline stage · {esc(stage["short"])}</p>
        <h1>{esc(stage["label"])}</h1>
        <p class="stage-focus">{esc(stage["focus"])}</p>
      </div>
      <div class="stage-meta">
        <span class="meta-label">Funnel</span>
        <strong>pulled {pulled} → kept {len(entries)}</strong>
        <span class="meta-label">Staged</span>
        <strong>{esc(data.get("generated") or "—")}</strong>
      </div>
    </section>
    <div class="stage-divider"></div>
    <div class="stage-layout">
      <div class="stage-main">{stage_content}</div>
      {stack_builder(catalog)}
    </div>
    {cut_panel(stage, {**data, "entries": entries, "pulled": pulled})}
    {layer_class_markup({"entries": catalog.get("layers", [])})}
        """,
        root=root,
    )


def render_layers(data: dict[str, Any], generated_on: str, catalog: dict[str, list[dict[str, Any]]]) -> str:
    stage = {"id": "layers", "label": "Enhancement Layers", "short": "+", "focus": "stackable additions for any pipeline"}
    entries = renderable_entries(data)
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    state = empty_state(stage, data) if not entries else f'<section class="entry-grid" aria-label="Enhancement Layers entries">{"".join(entry_card(entry, "layers") for entry in entries)}</section>'
    stage_content = filter_bar(entries) + matrix_markup(stage, entries) + state
    return page_shell(
        stage["label"],
        "layers",
        f"""
    <section class="stage-header">
      <div>
        <p class="eyebrow">Pipeline class · stackable</p>
        <h1>{esc(stage["label"])}</h1>
        <p class="stage-focus">{esc(stage["focus"])}</p>
      </div>
      <div class="stage-meta">
        <span class="meta-label">Funnel</span>
        <strong>pulled {pulled} → kept {len(entries)}</strong>
        <span class="meta-label">Staged</span>
        <strong>{esc(data.get("generated") or "—")}</strong>
      </div>
    </section>
    <div class="stage-divider"></div>
    <div class="stage-layout">
      <div class="stage-main">{stage_content}</div>
      {stack_builder(catalog)}
    </div>
    {cut_panel(stage, {**data, "entries": entries, "pulled": pulled})}
    """,
    )


def asset_css() -> str:
    return r"""
:root {
  --ink: #101417;
  --surface: #171c20;
  --surface-raised: #20272c;
  --surface-soft: #242d32;
  --line: #39444a;
  --line-strong: #536169;
  --text: #edf2ef;
  --muted: #aebbb8;
  --faint: #7e8d8c;
  --amber: #f1b35b;
  --amber-soft: #3c3021;
  --cyan: #72d7d1;
  --green: #9ed69f;
  --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}

* { box-sizing: border-box; }
html { background: var(--ink); scroll-behavior: smooth; }
body {
  margin: 0;
  min-width: 320px;
  background: var(--ink);
  color: var(--text);
  font: 18px/1.55 var(--sans);
  letter-spacing: .005em;
}
a { color: inherit; text-decoration: none; }
.topbar {
  align-items: center;
  background: #0d1113;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  min-height: 64px;
  padding: 0 clamp(18px, 4vw, 64px);
}
.wordmark { align-items: center; display: inline-flex; font: 700 18px/1 var(--mono); gap: 11px; letter-spacing: .03em; }
.wordmark-mark { color: var(--amber); font-size: 22px; letter-spacing: -.18em; }
.topbar-status { color: var(--muted); font: 13px/1 var(--mono); letter-spacing: .07em; text-transform: uppercase; }
.status-dot { background: var(--green); border-radius: 50%; display: inline-block; height: 8px; margin-right: 7px; width: 8px; }
.status-divider { border-left: 1px solid var(--line); display: inline-block; height: 15px; margin: 0 12px -3px; }
.stage-nav { background: #12171a; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 10; }
.stage-nav-inner { display: flex; margin: 0 auto; max-width: 1540px; overflow-x: auto; padding: 0 clamp(12px, 3.7vw, 60px); scrollbar-width: thin; }
.stage-link { align-items: center; border-bottom: 3px solid transparent; color: var(--muted); display: inline-flex; flex: 0 0 auto; font-size: 16px; gap: 9px; min-height: 58px; padding: 0 16px; transition: opacity .16s ease, transform .16s ease; }
.stage-link span { color: var(--faint); font: 12px/1 var(--mono); }
.stage-link:hover, .stage-link:focus-visible, .stage-link.is-active { color: var(--text); }
.stage-link.is-active { border-color: var(--amber); }
.stage-link.is-active span { color: var(--amber); }
.layer-link { margin-left: auto; }
.workbench { margin: 0 auto; max-width: 1540px; padding: clamp(34px, 5vw, 78px) clamp(18px, 4vw, 64px) 88px; }
.stage-header { align-items: end; display: flex; gap: 40px; justify-content: space-between; }
.eyebrow, .meta-label, .section-kicker, .class-badge { color: var(--amber); font: 12px/1.2 var(--mono); letter-spacing: .11em; text-transform: uppercase; }
h1, h2, p { margin-top: 0; }
h1 { font-size: clamp(38px, 6vw, 72px); letter-spacing: -.045em; line-height: .98; margin: 13px 0 12px; }
h2 { font-size: clamp(25px, 3vw, 38px); letter-spacing: -.025em; line-height: 1.1; }
.stage-focus { color: var(--muted); margin: 0; }
.stage-meta { border-left: 1px solid var(--line-strong); display: grid; gap: 3px 16px; grid-template-columns: auto auto; min-width: 230px; padding: 3px 0 3px 21px; }
.stage-meta strong { color: var(--text); font: 15px/1.2 var(--mono); overflow-wrap: anywhere; }
.stage-divider { border-top: 1px solid var(--line); margin: 36px 0 38px; }
.empty-state, .loaded-state { align-items: flex-start; background: var(--surface); border: 1px solid var(--line); display: flex; gap: 25px; max-width: 890px; padding: clamp(27px, 4vw, 48px); }
.empty-sigil { align-items: center; border: 1px solid var(--amber); color: var(--amber); display: flex; flex: 0 0 auto; font: 700 15px/1 var(--mono); height: 48px; justify-content: center; width: 48px; }
.empty-state h2, .loaded-state h2 { margin-bottom: 9px; }
.empty-note, .loaded-state p:last-child { color: var(--muted); margin-bottom: 18px; max-width: 650px; }
.text-link { color: var(--cyan); display: inline-flex; font-size: 16px; gap: 8px; }
.text-link:hover, .text-link:focus-visible { color: var(--text); text-decoration: underline; text-underline-offset: 4px; }
.cut-panel { align-items: center; border: 1px solid var(--line); display: flex; gap: 42px; justify-content: space-between; margin-top: 58px; padding: 25px 28px; }
.cut-panel h2 { font: 700 21px/1.2 var(--mono); margin: 10px 0 0; white-space: nowrap; }
.cut-panel h2 span { color: var(--amber); padding: 0 5px; }
.cut-reason { color: var(--muted); margin: 0; max-width: 760px; }
.layers-class { background: var(--surface-raised); border: 1px solid var(--line-strong); margin-top: 58px; padding: 27px 28px 30px; }
.section-kicker { align-items: center; display: flex; gap: 10px; }
.section-rule { background: var(--cyan); display: inline-block; height: 1px; width: 27px; }
.layers-heading { align-items: start; display: flex; gap: 22px; justify-content: space-between; margin-top: 22px; }
.layers-heading h2 { margin-bottom: 7px; }
.class-badge { border: 1px solid var(--line-strong); color: var(--cyan); padding: 8px 10px; white-space: nowrap; }
.layer-summary { color: var(--muted); margin: 0; }
.layer-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 21px; }
.layer-chip { background: var(--amber-soft); border: 1px solid #725633; color: #ffd99e; font-size: 15px; padding: 6px 10px; }
.layer-contract { color: var(--faint); font: 14px/1.5 var(--mono); margin: 24px 0 0; }
code { color: var(--cyan); font-family: var(--mono); }
.stage-layout { align-items: start; display: grid; gap: clamp(24px, 4vw, 54px); grid-template-columns: minmax(0, 1fr) minmax(320px, 390px); }
.stage-main { min-width: 0; }
.entry-grid { display: grid; gap: 18px; grid-template-columns: repeat(auto-fill, minmax(235px, 1fr)); }
.entry-card { background: var(--surface); border: 1px solid var(--line); cursor: pointer; min-width: 0; outline: none; overflow: hidden; transition: transform .16s ease, opacity .16s ease; }
.entry-card:hover { border-color: var(--line-strong); transform: translateY(-2px); }
.entry-card:focus-visible { border-color: var(--amber); box-shadow: 0 0 0 2px var(--amber-soft); }
.card-media { aspect-ratio: 3 / 4; background: #0d1113; overflow: hidden; position: relative; }
.card-image, .card-video { display: block; height: 100%; object-fit: cover; width: 100%; }
.media-index { background: rgba(13, 17, 19, .84); bottom: 10px; color: var(--cyan); font: 11px/1 var(--mono); left: 10px; padding: 6px 7px; position: absolute; text-transform: uppercase; }
.media-missing { align-items: center; color: var(--faint); display: flex; font: 13px/1 var(--mono); height: 100%; justify-content: center; }
.card-body { padding: 15px 16px 13px; }
.card-topline, .card-footer { align-items: center; display: flex; justify-content: space-between; }
.card-topline { min-height: 19px; }
.open-badge, .demo-badge { font: 11px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; }
.open-badge { color: var(--green); }
.demo-badge { color: var(--amber); }
.entry-name { font-size: 21px; letter-spacing: -.02em; line-height: 1.16; margin: 12px 0 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.entry-purpose { color: var(--muted); font-size: 16px; line-height: 1.35; margin-bottom: 13px; min-height: 22px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.entry-chips { display: flex; flex-wrap: wrap; gap: 5px; min-height: 27px; }
.entry-chip { background: var(--surface-soft); border: 1px solid var(--line); color: var(--muted); font: 12px/1.1 var(--mono); padding: 6px 7px; }
.card-footer { border-top: 1px solid var(--line); color: var(--faint); font: 11px/1 var(--mono); margin-top: 15px; padding-top: 12px; text-transform: uppercase; }
.card-detail { border-top: 1px solid var(--line-strong); margin-top: 15px; padding-top: 15px; }
.detail-grid { display: grid; gap: 12px; }
.detail-grid > div { display: grid; gap: 3px; }
.detail-label { color: var(--faint); font: 11px/1 var(--mono); text-transform: uppercase; }
.detail-grid strong { font-size: 15px; font-weight: 500; overflow-wrap: anywhere; }
.detail-grid a, .manifest-preview a { color: var(--cyan); }
.detail-verdict { border-left: 2px solid var(--amber); color: var(--muted); font-size: 15px; margin: 18px 0; padding-left: 10px; }
.manifest-preview { color: var(--muted); font-size: 14px; margin: 0; padding-left: 18px; }
.manifest-preview li { margin: 7px 0; overflow-wrap: anywhere; }
.stack-builder { background: #12171a; border: 1px solid var(--line-strong); max-height: calc(100vh - 145px); overflow: auto; padding: 22px 20px 21px; position: sticky; top: 122px; }
.stack-heading, .manifest-heading { align-items: start; display: flex; justify-content: space-between; }
.stack-heading h2 { font-size: 29px; margin: 9px 0 0; }
.stack-live { color: var(--green); font: 11px/1 var(--mono); letter-spacing: .08em; padding-top: 5px; text-transform: uppercase; }
.stack-live span { background: var(--green); border-radius: 50%; display: inline-block; height: 7px; margin-right: 5px; width: 7px; }
.stack-copy { color: var(--muted); font-size: 16px; line-height: 1.4; margin: 19px 0 22px; }
.stack-slots { display: grid; gap: 16px; }
.stack-slot { border-top: 1px solid var(--line); padding-top: 12px; }
.stack-slot h3, .manifest-heading h3 { color: var(--text); font: 700 15px/1.2 var(--mono); letter-spacing: .03em; margin: 0 0 9px; text-transform: uppercase; }
.stack-option { align-items: center; background: var(--surface); border: 1px solid transparent; color: var(--text); cursor: pointer; display: flex; font: inherit; gap: 10px; justify-content: space-between; margin: 4px 0; padding: 9px 10px; text-align: left; transition: transform .16s ease, opacity .16s ease; width: 100%; }
.stack-option:hover, .stack-option[aria-pressed="true"] { border-color: var(--amber); }
.stack-option[aria-pressed="true"] { background: var(--amber-soft); }
.stack-option-main { display: grid; gap: 3px; min-width: 0; }
.stack-option-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stack-option-sub { color: var(--faint); font: 11px/1.2 var(--mono); text-transform: uppercase; }
.stack-option-action { color: var(--cyan); font: 11px/1 var(--mono); text-transform: uppercase; }
.stack-empty, .manifest-empty { color: var(--faint); font-size: 14px; margin: 0; }
.stack-totals { border-bottom: 1px solid var(--line); border-top: 1px solid var(--line); display: grid; gap: 10px; grid-template-columns: 1fr 1fr; margin: 22px 0 18px; padding: 14px 0; }
.stack-totals div { display: grid; gap: 3px; }
.stack-totals span { color: var(--faint); font: 11px/1 var(--mono); text-transform: uppercase; }
.stack-totals strong { color: var(--amber); font: 700 20px/1.1 var(--mono); }
.manifest-heading { align-items: center; margin-bottom: 10px; }
.copy-all { background: transparent; border: 1px solid var(--cyan); color: var(--cyan); cursor: pointer; font: 11px/1 var(--mono); padding: 7px 8px; text-transform: uppercase; }
.copy-all:disabled { border-color: var(--line); color: var(--faint); cursor: not-allowed; }
.copy-all:not(:disabled):hover { background: var(--cyan); color: var(--ink); }
.manifest { display: grid; gap: 7px; }
.manifest-row { background: var(--surface); border-left: 2px solid var(--cyan); display: grid; gap: 4px; padding: 9px 10px; }
.manifest-row strong { font-size: 14px; overflow-wrap: anywhere; }
.manifest-row span { color: var(--muted); font: 12px/1.35 var(--mono); overflow-wrap: anywhere; }
.manifest-row a { color: var(--cyan); }
.copy-status { color: var(--green); font: 12px/1.3 var(--mono); margin: 12px 0 0; min-height: 16px; }
[hidden] { display: none !important; }
.filters { background: var(--surface); border: 1px solid var(--line); margin-bottom: 24px; padding: 15px 16px 14px; }
.search-field { align-items: center; display: flex; gap: 16px; }
.search-field span { color: var(--amber); flex: 0 0 auto; font: 12px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.search-field input { background: var(--ink); border: 1px solid var(--line-strong); color: var(--text); font: 18px/1.2 var(--sans); min-width: 0; outline: none; padding: 10px 12px; width: 100%; }
.search-field input:focus { border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(114, 215, 209, .16); }
.search-field input::placeholder { color: var(--faint); }
.filter-row { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 13px; }
.filter-chip { background: transparent; border: 1px solid var(--line-strong); color: var(--muted); cursor: pointer; font: 13px/1 var(--mono); padding: 8px 9px; }
.filter-chip b { color: var(--cyan); font-weight: 500; }
.filter-chip:hover:not(:disabled), .filter-chip[aria-pressed="true"] { background: var(--amber-soft); border-color: var(--amber); color: var(--text); }
.filter-chip:disabled { color: var(--faint); cursor: not-allowed; opacity: .6; }
.filter-chip:disabled b { color: var(--faint); }
.decision-matrix { background: #12171a; border: 1px solid var(--line); margin-bottom: 24px; padding: 20px; }
.matrix-heading { align-items: start; display: flex; gap: 20px; justify-content: space-between; }
.matrix-heading h2 { font-size: 23px; margin: 8px 0 0; }
.matrix-count { color: var(--cyan); font: 12px/1 var(--mono); padding-top: 5px; white-space: nowrap; }
.matrix-body { margin-top: 18px; }
.matrix-empty { color: var(--muted); margin: 0; }
.matrix-row { border-top: 1px solid var(--line); display: grid; gap: 18px; grid-template-columns: minmax(130px, .35fr) minmax(0, 1fr); padding: 15px 0; }
.matrix-need { display: grid; gap: 5px; align-content: start; }
.matrix-need span { color: var(--faint); font: 11px/1 var(--mono); text-transform: uppercase; }
.matrix-need strong { font-size: 18px; line-height: 1.25; }
.matrix-options { display: grid; gap: 7px; }
.matrix-option { align-items: center; background: var(--surface); display: grid; gap: 9px; grid-template-columns: minmax(0, 1fr) auto; padding: 9px 11px; }
.matrix-option > strong { font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.matrix-option > span { grid-column: 1 / -1; grid-row: 2; }
.matrix-option em { color: var(--amber); font: 12px/1 var(--mono); grid-column: 2; grid-row: 1; white-space: nowrap; }
.score-button { background: transparent; border: 0; color: var(--amber); cursor: pointer; font: 12px/1 var(--mono); padding: 0; text-transform: uppercase; }
.score-button:hover { color: var(--text); text-decoration: underline; text-underline-offset: 4px; }
.card-footer { position: relative; }
.score-popover { background: #0d1113; border: 1px solid var(--amber); bottom: 28px; color: var(--muted); font-size: 14px; left: 0; min-width: 255px; padding: 14px; position: absolute; z-index: 3; }
.score-popover strong { color: var(--amber); font: 700 20px/1 var(--mono); }
.score-popover p { margin: 10px 0 0; }
.score-popover ul { border-bottom: 1px solid var(--line); border-top: 1px solid var(--line); list-style: none; margin: 10px 0 0; padding: 8px 0; }
.score-popover li { display: flex; justify-content: space-between; padding: 3px 0; }
.score-popover li span { color: var(--faint); }
.score-popover .score-date { color: var(--faint); font: 11px/1.3 var(--mono); }
.is-explicit .card-image, .is-explicit .card-video { filter: blur(15px); }
.is-explicit:hover .card-image, .is-explicit:hover .card-video { filter: none; }
@media (max-width: 760px) {
  .topbar-status { font-size: 11px; }
  .status-divider, .topbar-status .status-dot { display: none; }
  .stage-header, .cut-panel { align-items: flex-start; flex-direction: column; gap: 22px; }
  .stage-meta { min-width: 0; }
  .layer-link { margin-left: 0; }
  .layers-heading { flex-direction: column; }
  .empty-state { flex-direction: column; }
  .stage-layout { grid-template-columns: 1fr; }
  .stack-builder { max-height: none; position: static; }
  .search-field { align-items: flex-start; flex-direction: column; gap: 8px; }
  .matrix-row { grid-template-columns: 1fr; }
  .matrix-option > strong { white-space: normal; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { transition-duration: .001ms !important; }
}
"""


def asset_js() -> str:
    return r"""
(() => {
  const page = document.body.dataset.page;
  document.querySelectorAll('.stage-link').forEach((link) => {
    if (link.dataset.stage === page) link.setAttribute('aria-current', 'page');
  });

  const selected = new Map();
  const exactVersion = (url) => typeof url === 'string' && (/modelVersionId=/.test(url) || /\/model-versions\//.test(url));
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const formatSize = (value) => `${Math.round(Number(value) || 0)} MB`;

  const cards = [...document.querySelectorAll('.entry-card')];
  const filterChips = [...document.querySelectorAll('.filter-chip')];
  const searchInput = document.querySelector('#entry-search');
  let activeFacet = '';
  const syncUrl = () => {
    const url = new URL(window.location.href);
    const query = (searchInput?.value || '').trim();
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (activeFacet) url.searchParams.set('filter', activeFacet); else url.searchParams.delete('filter');
    window.history.replaceState(null, '', url);
  };
  const cardFacets = (card) => {
    try { return JSON.parse(card.dataset.facets || '[]'); } catch (error) { return []; }
  };
  const matches = (card, query, facet = '') => {
    const textMatch = !query || (card.dataset.search || '').includes(query);
    const facetMatch = !facet || cardFacets(card).includes(facet);
    return textMatch && facetMatch;
  };
  const updateFilters = () => {
    const query = (searchInput?.value || '').trim().toLowerCase();
    cards.forEach((card) => { card.hidden = !matches(card, query, activeFacet); });
    const allCount = cards.filter((card) => matches(card, query)).length;
    const allNode = document.querySelector('[data-all-count]');
    if (allNode) allNode.textContent = allCount;
    filterChips.forEach((chip) => {
      const facet = chip.dataset.filterFacet || '';
      if (!facet) return;
      const count = cards.filter((card) => matches(card, query, facet)).length;
      const countNode = chip.querySelector('b');
      if (countNode) countNode.textContent = count;
      chip.disabled = count === 0 && activeFacet !== facet;
    });
    filterChips.forEach((chip) => chip.setAttribute('aria-pressed', String((chip.dataset.filterFacet || '') === activeFacet)));
  };
  filterChips.forEach((chip) => chip.addEventListener('click', () => {
    activeFacet = chip.dataset.filterFacet || '';
    updateFilters();
    syncUrl();
  }));
  if (searchInput) searchInput.addEventListener('input', () => { updateFilters(); syncUrl(); });

  const initialUrl = new URL(window.location.href);
  if (searchInput) searchInput.value = initialUrl.searchParams.get('q') || '';
  const initialFacet = initialUrl.searchParams.get('filter') || '';
  if (initialFacet && filterChips.some((chip) => chip.dataset.filterFacet === initialFacet)) activeFacet = initialFacet;

  document.querySelectorAll('.score-button').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const popover = button.parentElement?.querySelector('.score-popover');
      if (!popover) return;
      document.querySelectorAll('.score-popover').forEach((other) => { if (other !== popover) other.hidden = true; });
      document.querySelectorAll('.score-button').forEach((other) => { if (other !== button) other.setAttribute('aria-expanded', 'false'); });
      const open = button.getAttribute('aria-expanded') === 'true';
      if (open) {
        popover.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        return;
      }
      let score;
      try { score = JSON.parse(button.dataset.scorePayload || '{}'); } catch (error) { score = {}; }
      const axes = Object.entries(score.axes || {}).map(([key, value]) => `<li><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></li>`).join('');
      popover.innerHTML = `<strong>score ${escapeHtml(score.score || '—')}</strong><p>Community anchors: ${escapeHtml(score.community?.downloads)} downloads · ${escapeHtml(score.community?.thumbs_up)} likes</p><ul>${axes}</ul><p>${escapeHtml(score.verdict || 'No decision note staged.')}</p><span class="score-date">pulled ${escapeHtml(score.pulled_at || 'not staged')}</span>`;
      popover.hidden = false;
      button.setAttribute('aria-expanded', 'true');
    });
  });

  const manifestRows = () => {
    const rows = [];
    const seen = new Set();
    selected.forEach((item) => {
      const models = Array.isArray(item.models) ? item.models : [];
      models.forEach((model) => {
        if (!exactVersion(model.url)) return;
        const key = `${model.name}|${model.url}`;
        if (seen.has(key)) return;
        seen.add(key);
        rows.push({name: model.name || 'unnamed file', folder: model.folder || 'folder not staged', size: model.size_mb, url: model.url});
      });
      if (!models.some((model) => exactVersion(model.url)) && exactVersion(item.exact_url)) {
        const key = `${item.name}|${item.exact_url}`;
        if (!seen.has(key)) {
          seen.add(key);
          rows.push({name: item.name, folder: 'version file', size: item.disk, url: item.exact_url});
        }
      }
    });
    return rows;
  };

  const updateStack = () => {
    const vram = [...selected.values()].reduce((sum, item) => sum + (Number(item.vram) || 0), 0);
    const disk = [...selected.values()].reduce((sum, item) => sum + (Number(item.disk) || 0), 0);
    const vramNode = document.querySelector('[data-stack-vram]');
    const diskNode = document.querySelector('[data-stack-disk]');
    if (vramNode) vramNode.textContent = `${vram} GB`;
    if (diskNode) diskNode.textContent = formatSize(disk);
    const rows = manifestRows();
    const manifest = document.querySelector('[data-stack-manifest]');
    const copyButton = document.querySelector('[data-copy-all]');
    if (manifest) {
      manifest.innerHTML = rows.length ? rows.map((row) => `<div class="manifest-row"><strong>${escapeHtml(row.name)}</strong><span>${escapeHtml(row.folder)} · ${formatSize(row.size)}</span><a href="${escapeHtml(row.url)}" target="_blank" rel="noreferrer">exact version ↗</a></div>`).join('') : '<p class="manifest-empty">No exact-version rows in the current selection.</p>';
    }
    if (copyButton) copyButton.disabled = rows.length === 0;
  };

  document.querySelectorAll('.stack-option').forEach((option) => {
    option.addEventListener('click', () => {
      let item;
      try { item = JSON.parse(option.dataset.stackEntry || '{}'); } catch (error) { return; }
      const role = item.role;
      if (selected.get(role)?.id === item.id) {
        selected.delete(role);
      } else {
        selected.set(role, item);
      }
      document.querySelectorAll(`.stack-option[data-stack-entry]`).forEach((candidate) => {
        try {
          const candidateItem = JSON.parse(candidate.dataset.stackEntry || '{}');
          candidate.setAttribute('aria-pressed', String(selected.get(candidateItem.role)?.id === candidateItem.id));
        } catch (error) { /* an invalid option stays visually inactive */ }
      });
      updateStack();
    });
  });

  const copyButton = document.querySelector('[data-copy-all]');
  if (copyButton) copyButton.addEventListener('click', async () => {
    const rows = manifestRows();
    const status = document.querySelector('[data-copy-status]');
    try {
      await navigator.clipboard.writeText(rows.map((row) => row.url).join('\n'));
      if (status) status.textContent = `${rows.length} exact links copied`;
    } catch (error) {
      if (status) status.textContent = 'Clipboard unavailable; copy links from the rows.';
    }
  });

  document.querySelectorAll('.entry-card').forEach((card) => {
    const detail = card.querySelector('.card-detail');
    const toggleDetail = () => {
      if (!detail) return;
      const open = card.getAttribute('aria-expanded') === 'true';
      card.setAttribute('aria-expanded', String(!open));
      detail.hidden = open;
    };
    card.addEventListener('click', (event) => {
      if (event.target.closest('a, button')) return;
      toggleDetail();
    });
    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleDetail();
      }
    });
  });

  document.querySelectorAll('[data-gallery-surface]').forEach((surface) => {
    const image = surface.querySelector('img[data-gallery]');
    if (!image) return;
    let gallery;
    try { gallery = JSON.parse(image.dataset.gallery || '[]'); } catch (error) { gallery = []; }
    if (gallery.length < 2) return;
    surface.addEventListener('mousemove', (event) => {
      const bounds = surface.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(0.999, (event.clientX - bounds.left) / bounds.width));
      image.src = gallery[Math.floor(ratio * gallery.length)];
    });
    surface.addEventListener('mouseleave', () => { image.src = gallery[0]; });
  });

  document.querySelectorAll('[data-hover-video]').forEach((video) => {
    video.addEventListener('mouseenter', () => { video.play().catch(() => {}); });
    video.addEventListener('mouseleave', () => { video.pause(); video.currentTime = 0; });
  });

  updateStack();
})();
"""


def generate(demo: bool = False) -> list[Path]:
    if SITE.exists():
        shutil.rmtree(SITE)
    generated_on = dt.date.today().isoformat()
    outputs: list[Path] = []
    write_text(SITE / "assets" / "style.css", asset_css())
    write_text(SITE / "assets" / "app.js", asset_js())
    outputs += [SITE / "assets" / "style.css", SITE / "assets" / "app.js"]

    stage_data = {stage["id"]: data_for_stage(stage, demo=demo) for stage in STAGES}
    layer_stage = {"id": "layers", "label": "Enhancement Layers", "short": "+", "focus": "stackable additions for any pipeline"}
    stage_data["layers"] = data_for_stage(layer_stage, demo=demo)
    catalog = {stage_id: data.get("entries") or [] for stage_id, data in stage_data.items()}

    for stage in STAGES:
        data = stage_data[stage["id"]]
        destination = SITE / stage["id"] / "index.html"
        write_text(destination, render_stage(stage, data, generated_on, catalog))
        outputs.append(destination)

    layer_destination = SITE / "layers" / "index.html"
    write_text(layer_destination, render_layers(stage_data["layers"], generated_on, catalog))
    outputs.append(layer_destination)

    # Keep the root useful without inventing an extra landing-page experience.
    root_destination = SITE / "index.html"
    write_text(root_destination, render_stage(STAGES[0], stage_data["persona"], generated_on, catalog, root=True))
    outputs.append(root_destination)
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the v2 pipeline workbench")
    parser.add_argument("--demo", action="store_true", help="inject three clearly labeled in-memory entries per stage")
    args = parser.parse_args()
    files = generate(demo=args.demo)
    print(f"sitegen2: generated {len(files)} files in {SITE}")
    print(f"sitegen2: staged source {STAGED}")
    print(f"sitegen2: mode={'demo' if args.demo else 'default'}")
    print("sitegen2: entries are never synthesized in default mode")
    for stage in (*STAGES, {"id": "layers", "label": "Enhancement Layers"}):
        if args.demo:
            print(f"  {stage['label']}: 3 [DEMO] entries (memory only)")
        else:
            filename = "LAYERS.json" if stage["id"] == "layers" else f"{STAGE_FILES[stage['id']]}.json"
            data = read_staged(filename, filename.removesuffix(".json"))
            print(f"  {stage['label']}: {len(data.get('entries') or [])} pulled / {len(renderable_entries(data))} kept with previews")
