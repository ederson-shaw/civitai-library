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


def stage_entries(data: dict[str, Any], stage_id: str, style: str = "default") -> list[dict[str, Any]]:
    entries = renderable_entries({**data, "entries": kept_entries(data)})
    if stage_id != "persona":
        return entries
    if data.get("demo"):
        return entries if style == "default" else []
    if style == "anime":
        return [entry for entry in entries if entry.get("visual_class") == "anime-illustration"]
    return [entry for entry in entries if entry.get("visual_class") == "realism-photoreal"]


def entry_name(entry: dict[str, Any]) -> str:
    return str(entry.get("our_name") or entry.get("source_name") or "")


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
        "review_flag": False,
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


def cut_list_markup(stage_id: str) -> str:
    key = stage_id.upper().replace("-", "_")
    try:
        data = json.loads((STAGED / "cuts.json").read_text(encoding="utf-8"))
        blob = (data.get("stages") or {}).get(key) or {}
    except (OSError, json.JSONDecodeError):
        blob = {}
    cuts = blob.get("cuts") or []
    if not cuts:
        return ""
    rows = "".join(
        f'<li><strong>{esc(c.get("name") or c.get("id"))}</strong> — {esc(c.get("reason") or "")}</li>'
        for c in cuts if isinstance(c, dict)
    )
    return (
        f'<details class="cut-details"><summary>{len(cuts)} curated cuts — view why</summary>'
        f"<ul>{rows}</ul></details>"
    )


def cut_panel(stage: dict[str, Any], data: dict[str, Any]) -> str:
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    source = source_label(stage["id"])
    kept = int(data.get("kept_count", data.get("preview_candidates", len(kept_entries(data)))))
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
      {cut_list_markup(stage["id"])}
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
    if stage_id == "persona" and entry.get("visual_class") == "anime-illustration":
        chips.insert(0, "style: anime")
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
    return ""


def score_payload(entry: dict[str, Any]) -> dict[str, Any]:
    stats = entry.get("stats") or {}
    payload: dict[str, Any] = {}
    score = score_value(entry)
    if score:
        payload["score"] = score
    community = {
        key: stats[source]
        for key, source in (("downloads", "downloadCount"), ("thumbs_up", "thumbsUpCount"))
        if stats.get(source) is not None
    }
    if community:
        payload["community"] = community
    axes = {key: entry[key] for key in ("quality", "lane_fit", "freshness") if entry.get(key) is not None}
    if axes:
        payload["axes"] = axes
    if entry.get("verdict_line"):
        payload["verdict"] = entry["verdict_line"]
    if entry.get("pulled_at"):
        payload["pulled_at"] = entry["pulled_at"]
    return payload


def score_popover_markup(entry: dict[str, Any]) -> str:
    payload = esc(json.dumps(score_payload(entry), ensure_ascii=False, separators=(",", ":")))
    score = score_value(entry)
    if not score:
        return ""
    return f'<button class="score-button" type="button" data-score-payload="{payload}" aria-expanded="false">score {esc(score)}</button><div class="score-popover" hidden></div>'


def filter_bar(entries: list[dict[str, Any]], stage_id: str, anime_entries: list[dict[str, Any]] | None = None) -> str:
    facets = {"low vram", "max quality", "fastest"}
    for entry in entries:
        tradeoff = entry.get("tradeoff")
        if isinstance(tradeoff, list):
            facets.update(str(value).strip().lower() for value in tradeoff if value)
        elif tradeoff:
            facets.add(str(tradeoff).strip().lower())
    chips = []
    for facet in sorted(facets):
        count = sum(facet in facet_values(entry) for entry in entries)
        chips.append(
            f'<button class="filter-chip" type="button" data-filter-facet="{esc(facet)}" '
            f'data-filter-count="{count}" aria-pressed="false" disabled>{esc(facet)} <b>{count}</b></button>'
        )
    if stage_id == "persona":
        anime_count = len(anime_entries or [])
        disabled = " disabled" if anime_count == 0 else ""
        chips.insert(
            0,
            f'<button class="filter-chip style-filter" type="button" data-filter-facet="style: anime" '
            f'data-filter-count="{anime_count}" aria-pressed="false"{disabled}>style: anime <b>{anime_count}</b></button>',
        )
    return f"""
    <section class="filters" aria-label="Filter entries">
      <label class="search-field"><span>Find an entry</span><input id="entry-search" type="search" autocomplete="off" placeholder="name, purpose, model…"></label>
      <div class="filter-row"><button class="filter-chip is-all" type="button" data-filter-facet="" aria-pressed="true">all <b data-all-count>{len(entries)}</b></button>{''.join(chips)}</div>
    </section>
    """


def matrix_markup(stage: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    if not entries:
        body = '<p class="matrix-empty">No kept entries to compare yet.</p>'
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
        for purpose, options in list(groups.items())[:1]:
            option_markup = []
            for entry in options[:4]:
                name = entry_name(entry)
                name_markup = f'<strong>{esc(name)}</strong>' if name else ""
                score = score_value(entry)
                score_markup = f'<em>score {esc(score)}</em>' if score else ""
                option_markup.append(f'<div class="matrix-option">{name_markup}<span>{entry_chip_markup(entry, stage["id"])}</span>{score_markup}</div>')
            options_markup = "".join(option_markup)
            rows.append(f'<div class="matrix-row"><div class="matrix-need"><span>Need</span><strong>{esc(purpose)}</strong></div><div class="matrix-options">{options_markup}</div></div>')
        body = "".join(rows)
    return f"""
    <section class="decision-matrix" aria-label="Decision matrix">
      <div class="matrix-body"><span class="matrix-count">{len(entries)} options</span>{body}</div>
    </section>
    """


def entry_payload(entry: dict[str, Any], stage_id: str) -> dict[str, Any]:
    models = []
    for model in entry_models(entry):
        payload_model: dict[str, Any] = {}
        for key in ("name", "folder", "url"):
            if model.get(key):
                payload_model[key] = model[key]
        if model.get("size_mb") is not None:
            payload_model["size_mb"] = int(model["size_mb"])
        if payload_model:
            models.append(payload_model)
    if not models and isinstance(entry.get("download"), dict):
        d = entry["download"]
        self_row: dict[str, Any] = {"name": d.get("name"), "folder": d.get("folder")}
        if d.get("url"):
            self_row["url"] = d["url"]
        if d.get("size_mb") is not None:
            self_row["size_mb"] = int(d["size_mb"])
        if self_row.get("name"):
            models.append(self_row)
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
    detail_items = []
    if entry.get("source_name"):
        detail_items.append(f'<div><span class="detail-label">Source</span><strong>{esc(entry["source_name"])}</strong></div>')
    if entry.get("baseModel"):
        detail_items.append(f'<div><span class="detail-label">Base model</span><strong>{esc(entry["baseModel"])}</strong></div>')
    stacks = entry.get("stacks_on") or []
    if stacks:
        detail_items.append(f'<div><span class="detail-label">Stacks on</span><strong>{esc(", ".join(str(value) for value in stacks))}</strong></div>')
    if exact_url:
        detail_items.append(f'<div><span class="detail-label">Version</span><strong><a href="{esc(exact_url)}" target="_blank" rel="noreferrer">open vetted version ↗</a></strong></div>')
    model_rows = []
    for model in models:
        raw_url = model.get("url") if isinstance(model.get("url"), str) else ""
        url = raw_url if ("modelVersionId=" in raw_url or "/model-versions/" in raw_url) else ""
        row_parts = []
        if model.get("name"):
            row_parts.append(f'<strong>{esc(model["name"])}</strong>')
        if model.get("folder"):
            row_parts.append(esc(model["folder"]))
        if model.get("size_mb") is not None:
            row_parts.append(f'{esc(model["size_mb"])} MB')
        if url:
            row_parts.append(f'<a href="{esc(url)}" target="_blank" rel="noreferrer">exact file link ↗</a>')
        if row_parts:
            model_rows.append(f'<li>{" · ".join(row_parts)}</li>')
    detail_body = []
    if detail_items:
        detail_body.append(f'<div class="detail-grid">{"".join(detail_items)}</div>')
    if entry.get("verdict_line"):
        detail_body.append(f'<p class="detail-verdict">{esc(entry["verdict_line"])}</p>')
    if model_rows:
        detail_body.append(f'<ul class="manifest-preview">{"".join(model_rows)}</ul>')
    if not detail_body:
        return ""
    return f"""
      <div class="card-detail" hidden>
        {"".join(detail_body)}
      </div>
    """


def media_markup(entry: dict[str, Any], stage_id: str) -> str:
    urls = media_urls(entry)
    if not urls:
        if entry.get("kind") == "engine":
            return '<div class="engine-spec">engine</div>'
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
    explicit = str(entry.get("nsfw_bucket") or "").lower() in {"explicit", "nsfw", "adult"} or stage_id == "nsfw"
    media_class = "card-media is-explicit" if explicit else "card-media"
    facets = esc(json.dumps(facet_values(entry), ensure_ascii=False, separators=(",", ":")))
    demo_attr = ' data-demo="true"' if str(entry.get("tier")) == "DEMO" else ""
    visual_class = str(entry.get("visual_class") or "")
    style_attr = f' data-style="{esc(visual_class)}"' if visual_class else ""
    hidden_attr = ' hidden' if stage_id == "persona" and visual_class == "anime-illustration" else ""
    topline_items = []
    if entry.get("open_closed"):
        topline_items.append(f'<span class="open-badge">{esc(str(entry["open_closed"]).lower())}</span>')
    if demo_badge:
        topline_items.append(demo_badge)
    topline = f'<div class="card-topline">{"".join(topline_items)}</div>' if topline_items else ""
    name = entry_name(entry)
    name_markup = f'<h2 class="entry-name">{esc(name)}</h2>' if name else ""
    purpose = f'<p class="entry-purpose">{esc(entry["purpose"])}</p>' if entry.get("purpose") else ""
    chips = entry_chip_markup(entry, stage_id)
    chips_markup = f'<div class="entry-chips">{chips}</div>' if chips else ""
    style_reason = ''
    if stage_id == "persona" and visual_class == "anime-illustration":
        style_reason = '<p class="style-reason">Reason: deliberate anime style choice; outside the realism default.</p>'
    footer_items = []
    score = score_popover_markup(entry)
    if score:
        footer_items.append(score)
    if entry.get("vram_class"):
        footer_items.append(f'<span>VRAM {esc(entry["vram_class"])}</span>')
    footer_items.append('<button class="card-add" type="button" data-card-add aria-pressed="false">add to stack</button>')
    footer = f'<div class="card-footer">{"".join(footer_items)}</div>' if footer_items else ""
    return f"""
    <article class="entry-card" tabindex="0" aria-expanded="false"{demo_attr}{hidden_attr}{style_attr} data-entry-id="{esc(entry.get('id') or '')}" data-stack-role="{esc(role)}" data-stack-payload="{payload}" data-search="{esc(search_text(entry))}" data-facets="{facets}">
      <div class="{media_class}" data-gallery-surface>
        {media_markup(entry, stage_id)}
        <span class="media-index">{esc(role)}</span>
      </div>
      <div class="card-body">
        {topline}
        {name_markup}
        {purpose}
        {style_reason}
        {chips_markup}
        {footer}
        {entry_detail_markup(entry, stage_id)}
      </div>
    </article>
    """


def stack_option(entry: dict[str, Any], stage_id: str) -> str:
    payload = esc(json.dumps(entry_payload(entry, stage_id), ensure_ascii=False, separators=(",", ":")))
    role = entry_role(entry, stage_id)
    visual_class = str(entry.get("visual_class") or "")
    anime_attr = ' data-style="anime"' if stage_id == "persona" and visual_class == "anime-illustration" else ""
    anime_class = " persona-anime-option" if anime_attr else ""
    hidden_attr = " hidden" if anime_attr else ""
    sub_parts = [stage_id]
    if entry.get("vram_class"):
        sub_parts.append(str(entry["vram_class"]))
    sub = " · ".join(sub_parts)
    name = entry_name(entry)
    name_markup = f'<span class="stack-option-name">{esc(name)}</span>' if name else ""
    return f"""
    <button class="stack-option{anime_class}" type="button" data-stack-entry="{payload}"{anime_attr}{hidden_attr} aria-pressed="false">
      <span class="stack-option-main">{name_markup}<span class="stack-option-sub">{esc(sub)}</span></span>
      <span class="stack-option-action">add</span>
    </button>
    """


def stack_builder(catalog: dict[str, list[dict[str, Any]]]) -> str:
    role_labels = (("base", "Base"), ("layer", "Layers"), ("motion", "Motion"), ("voice", "Voice"))
    groups = []
    for role, label in role_labels:
        options = []
        anime_options = []
        for stage_id, entries in catalog.items():
            for entry in entries:
                if entry_role(entry, stage_id) == role:
                    option = stack_option(entry, stage_id)
                    if stage_id == "persona" and entry.get("visual_class") == "anime-illustration":
                        anime_options.append(option)
                    else:
                        options.append(option)
        if options or anime_options:
            groups.append(f'<section class="stack-catalog-group" data-stack-catalog="{role}"><h3>{label}</h3>{"".join(options[:6] + anime_options)}</section>')
    return f"""
    <aside class="stack-builder" id="stack-builder" data-stack-builder>
      <div class="stack-heading">
        <div><p class="eyebrow">Execution plan</p><h2>Stack builder</h2></div>
        <span class="stack-live" data-stack-live hidden><span></span> live</span>
      </div>
      <div class="stack-empty" data-stack-empty><strong>Select a base to start</strong></div>
      <div class="stack-plan" data-stack-plan hidden>
        <div class="stack-selected" data-stack-selected aria-live="polite"></div>
        <div class="stack-slots" data-stack-slots>
          <section class="stack-plan-slot" data-plan-slot="base"><h3>Base</h3><div data-plan-selection></div></section>
          <section class="stack-plan-slot" data-plan-slot="layer"><h3>Layers</h3><div data-plan-selection></div></section>
          <section class="stack-plan-slot" data-plan-slot="motion"><h3>Motion</h3><div data-plan-selection></div></section>
          <section class="stack-plan-slot" data-plan-slot="voice"><h3>Voice</h3><div data-plan-selection></div></section>
        </div>
        <div class="stack-totals" aria-live="polite">
          <div><span>VRAM total</span><strong data-stack-vram>0 GB</strong></div>
          <div><span>Disk total</span><strong data-stack-disk>0 MB</strong></div>
        </div>
        <div class="manifest-heading"><h3>Download manifest</h3><button class="copy-all" type="button" data-copy-all disabled>copy all</button></div>
        <div class="manifest" data-stack-manifest></div>
        <p class="copy-status" data-copy-status aria-live="polite"></p>
      </div>
      <div class="stack-catalogs" data-stack-catalogs>
        <p class="catalog-heading">Add to plan</p>
        {"".join(groups)}
      </div>
    </aside>
    """


def render_stage(stage: dict[str, Any], data: dict[str, Any], generated_on: str, catalog: dict[str, list[dict[str, Any]]], root: bool = False) -> str:
    entries = stage_entries(data, stage["id"])
    anime_entries = stage_entries(data, stage["id"], style="anime")
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    kept_count = int(data.get("preview_candidates", len(entries)))
    state = empty_state(stage, data) if not entries else f"""
    <section class="entry-grid" aria-label="{esc(stage['label'])} entries">
      {''.join(entry_card(entry, stage['id']) for entry in entries)}
    </section>
    """
    style_cluster = ""
    if stage["id"] == "persona" and anime_entries:
        style_cluster = f"""
    <section class="entry-grid style-cluster" aria-label="Anime style entries" data-anime-cluster hidden>
      {''.join(entry_card(entry, stage['id']) for entry in anime_entries)}
    </section>
    """
    stage_content = filter_bar(entries, stage["id"], anime_entries) + matrix_markup(stage, entries) + state + style_cluster
    return page_shell(
        stage["label"],
        stage["id"],
        f"""
    <section class="stage-header">
      <div class="stage-heading">
        <h1>{esc(stage["label"])}</h1>
        <p class="stage-focus">{esc(stage["focus"])}</p>
      </div>
      <strong class="stage-funnel">pulled {pulled} → kept {kept_count}</strong>
    </section>
    <div class="stage-layout">
      <div class="stage-main">{stage_content}</div>
      {stack_builder(catalog)}
    </div>
    {cut_panel(stage, {**data, "entries": entries, "pulled": pulled, "kept_count": kept_count})}
    {layer_class_markup({"entries": catalog.get("layers", [])})}
        """,
        root=root,
    )


def render_layers(data: dict[str, Any], generated_on: str, catalog: dict[str, list[dict[str, Any]]]) -> str:
    stage = {"id": "layers", "label": "Enhancement Layers", "short": "+", "focus": "stackable additions for any pipeline"}
    entries = stage_entries(data, stage["id"])
    pulled = int(data.get("pulled", len(data.get("entries") or [])))
    kept_count = int(data.get("preview_candidates", len(entries)))
    state = empty_state(stage, data) if not entries else f'<section class="entry-grid" aria-label="Enhancement Layers entries">{"".join(entry_card(entry, "layers") for entry in entries)}</section>'
    stage_content = filter_bar(entries, stage["id"]) + matrix_markup(stage, entries) + state
    return page_shell(
        stage["label"],
        "layers",
        f"""
    <section class="stage-header">
      <div class="stage-heading">
        <h1>{esc(stage["label"])}</h1>
        <p class="stage-focus">{esc(stage["focus"])}</p>
      </div>
      <strong class="stage-funnel">pulled {pulled} → kept {kept_count}</strong>
    </section>
    <div class="stage-layout">
      <div class="stage-main">{stage_content}</div>
      {stack_builder(catalog)}
    </div>
    {cut_panel(stage, {**data, "entries": entries, "pulled": pulled, "kept_count": kept_count})}
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
  --topbar-height: 56px;
  --stage-nav-height: 56px;
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
  min-height: var(--topbar-height);
  padding: 0 clamp(18px, 4vw, 64px);
}
.wordmark { align-items: center; display: inline-flex; font: 700 18px/1 var(--mono); gap: 11px; letter-spacing: .03em; }
.wordmark-mark { color: var(--amber); font-size: 22px; letter-spacing: -.18em; }
.topbar-status { color: var(--text); font: 15px/1 var(--mono); letter-spacing: .04em; text-transform: uppercase; }
.status-dot { background: var(--green); border-radius: 50%; display: inline-block; height: 8px; margin-right: 7px; width: 8px; }
.status-divider { border-left: 1px solid var(--line); display: inline-block; height: 15px; margin: 0 12px -3px; }
.stage-nav { background: #12171a; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 10; }
.stage-nav-inner { display: flex; margin: 0 auto; max-width: 1540px; overflow-x: auto; padding: 0 clamp(12px, 3.7vw, 60px); scrollbar-width: thin; }
.stage-link { align-items: center; border-bottom: 3px solid transparent; color: var(--muted); display: inline-flex; flex: 0 0 auto; font-size: 18px; gap: 9px; min-height: var(--stage-nav-height); padding: 0 16px; transition: opacity .16s ease, transform .16s ease; }
.stage-link span { color: var(--faint); font: 15px/1 var(--mono); }
.stage-link:hover, .stage-link:focus-visible, .stage-link.is-active { color: var(--text); }
.stage-link.is-active { border-color: var(--amber); }
.stage-link.is-active span { color: var(--amber); }
.layer-link { margin-left: auto; }
.workbench { margin: 0 auto; max-width: 1540px; padding: 12px clamp(18px, 4vw, 64px) 72px; }
.stage-header { align-items: center; border-bottom: 1px solid var(--line); display: flex; gap: 24px; justify-content: space-between; min-height: 82px; padding: 8px 0; }
.stage-heading { align-items: baseline; display: flex; flex-wrap: wrap; gap: 12px 20px; min-width: 0; }
.eyebrow, .meta-label, .section-kicker, .class-badge { color: var(--amber); font: 15px/1.2 var(--mono); letter-spacing: .07em; text-transform: uppercase; }
h1, h2, p { margin-top: 0; }
h1 { font-size: clamp(30px, 4vw, 40px); letter-spacing: -.045em; line-height: 1; margin: 0; }
h2 { font-size: clamp(25px, 3vw, 38px); letter-spacing: -.025em; line-height: 1.1; }
.stage-focus { color: var(--muted); font-size: 18px; margin: 0; }
.stage-funnel { color: var(--text); flex: 0 0 auto; font: 18px/1.2 var(--mono); }
.empty-state, .loaded-state { align-items: flex-start; background: var(--surface); border: 1px solid var(--line); display: flex; gap: 25px; max-width: 890px; padding: clamp(27px, 4vw, 48px); }
.empty-sigil { align-items: center; border: 1px solid var(--amber); color: var(--amber); display: flex; flex: 0 0 auto; font: 700 15px/1 var(--mono); height: 48px; justify-content: center; width: 48px; }
.empty-state h2, .loaded-state h2 { margin-bottom: 9px; }
.empty-note, .loaded-state p:last-child { color: var(--muted); margin-bottom: 18px; max-width: 650px; }
.text-link { color: var(--cyan); display: inline-flex; font-size: 18px; gap: 8px; }
.text-link:hover, .text-link:focus-visible { color: var(--text); text-decoration: underline; text-underline-offset: 4px; }
.cut-panel { align-items: center; border: 1px solid var(--line); display: flex; gap: 42px; justify-content: space-between; margin-top: 58px; padding: 25px 28px; }
.cut-panel h2 { font: 700 21px/1.2 var(--mono); margin: 10px 0 0; white-space: nowrap; }
.cut-panel h2 span { color: var(--amber); padding: 0 5px; }
.cut-reason { color: var(--muted); margin: 0; max-width: 760px; }
.cut-details { color: var(--muted); margin-top: 10px; max-width: 760px; }
.cut-details summary { cursor: pointer; font-size: 15px; }
.cut-details ul { margin: 8px 0 0; padding-left: 18px; }
.cut-details li { font-size: 15px; margin: 4px 0; }
.layers-class { background: var(--surface-raised); border: 1px solid var(--line-strong); margin-top: 58px; padding: 27px 28px 30px; }
.section-kicker { align-items: center; display: flex; gap: 10px; }
.section-rule { background: var(--cyan); display: inline-block; height: 1px; width: 27px; }
.layers-heading { align-items: start; display: flex; gap: 22px; justify-content: space-between; margin-top: 22px; }
.layers-heading h2 { margin-bottom: 7px; }
.class-badge { border: 1px solid var(--line-strong); color: var(--cyan); padding: 8px 10px; white-space: nowrap; }
.layer-summary { color: var(--muted); margin: 0; }
.layer-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 21px; }
.layer-chip { background: var(--amber-soft); border: 1px solid #725633; color: #ffd99e; font-size: 15px; padding: 6px 10px; }
.layer-contract { color: var(--muted); font: 16px/1.5 var(--mono); margin: 24px 0 0; }
code { color: var(--cyan); font-family: var(--mono); }
.stage-layout { align-items: start; display: grid; gap: clamp(24px, 3vw, 36px); grid-template-columns: minmax(0, 1fr) minmax(320px, 360px); }
.stage-main { min-width: 0; }
.entry-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
.entry-card { background: var(--surface); border: 1px solid var(--line); cursor: pointer; min-width: 0; outline: none; overflow: hidden; transition: transform .16s ease, opacity .16s ease; }
.entry-card:hover { border-color: var(--line-strong); transform: translateY(-2px); }
.entry-card:focus-visible { border-color: var(--amber); box-shadow: 0 0 0 2px var(--amber-soft); }
.card-media { aspect-ratio: 4 / 3; background: #0d1113; overflow: hidden; position: relative; }
.card-image, .card-video { display: block; height: 100%; object-fit: cover; width: 100%; }
.media-index { background: rgba(13, 17, 19, .84); bottom: 10px; color: var(--cyan); font: 15px/1 var(--mono); left: 10px; padding: 6px 7px; position: absolute; text-transform: uppercase; }
.media-missing { align-items: center; color: var(--faint); display: flex; font: 18px/1 var(--mono); height: 100%; justify-content: center; }
.engine-spec { align-items: center; color: var(--faint); display: flex; font: 18px/1 var(--mono); height: 100%; justify-content: center; letter-spacing: .08em; text-transform: uppercase; }
.card-body { padding: 15px 16px 13px; }
.card-topline, .card-footer { align-items: center; display: flex; justify-content: space-between; }
.card-topline { min-height: 19px; }
.open-badge, .demo-badge { font: 16px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; }
.open-badge { color: var(--green); }
.demo-badge { color: var(--amber); }
.entry-name { font-size: 20px; letter-spacing: -.02em; line-height: 1.16; margin: 12px 0 6px; overflow-wrap: anywhere; }
.entry-purpose { color: var(--muted); font-size: 18px; line-height: 1.35; margin-bottom: 13px; overflow-wrap: anywhere; }
.entry-chips { display: flex; flex-wrap: wrap; gap: 5px; min-height: 27px; }
.entry-chip { background: var(--surface-soft); border: 1px solid var(--line); color: var(--muted); font: 18px/1.15 var(--mono); padding: 6px 7px; }
.card-footer { border-top: 1px solid var(--line); color: var(--muted); font: 18px/1.2 var(--mono); margin-top: 15px; padding-top: 12px; text-transform: uppercase; }
.card-detail { border-top: 1px solid var(--line-strong); margin-top: 15px; padding-top: 15px; }
.detail-grid { display: grid; gap: 12px; }
.detail-grid > div { display: grid; gap: 3px; }
.detail-label { color: var(--muted); font: 15px/1 var(--mono); text-transform: uppercase; }
.detail-grid strong { font-size: 18px; font-weight: 500; overflow-wrap: anywhere; }
.detail-grid a, .manifest-preview a { color: var(--cyan); }
.detail-verdict { border-left: 2px solid var(--amber); color: var(--muted); font-size: 18px; margin: 18px 0; padding-left: 10px; }
.manifest-preview { color: var(--muted); font-size: 18px; margin: 0; padding-left: 18px; }
.manifest-preview li { margin: 7px 0; overflow-wrap: anywhere; }
.stack-builder { background: #12171a; border: 1px solid var(--line-strong); max-height: calc(100vh - var(--stage-nav-height) - 24px); overflow: auto; padding: 18px 16px 20px; position: sticky; top: calc(var(--stage-nav-height) + 12px); }
.stack-heading, .manifest-heading { align-items: start; display: flex; justify-content: space-between; }
.stack-heading h2 { font-size: 29px; margin: 9px 0 0; }
.stack-live { color: var(--green); font: 18px/1 var(--mono); letter-spacing: .04em; padding-top: 5px; text-transform: uppercase; }
.stack-live span { background: var(--green); border-radius: 50%; display: inline-block; height: 7px; margin-right: 5px; width: 7px; }
.stack-empty { background: var(--surface); border: 1px solid var(--line); margin: 16px 0 20px; padding: 14px; }
.stack-empty strong { color: var(--text); font-size: 22px; line-height: 1.2; }
.stack-plan { display: grid; gap: 16px; margin: 16px 0 22px; }
.stack-selected { background: var(--amber-soft); border: 2px solid var(--amber); display: grid; gap: 8px; padding: 13px; }
.stack-selected::before { color: var(--amber); content: "Selected inputs"; font: 15px/1 var(--mono); letter-spacing: .07em; text-transform: uppercase; }
.stack-selected-item { align-items: baseline; display: flex; flex-wrap: wrap; gap: 8px 12px; }
.stack-selected-item strong { font-size: 20px; line-height: 1.18; overflow-wrap: anywhere; }
.stack-selected-item span { color: var(--text); font: 16px/1.2 var(--mono); text-transform: uppercase; }
.stack-slots { display: grid; gap: 12px; }
.stack-plan-slot, .stack-catalog-group { border-top: 1px solid var(--line); padding-top: 11px; }
.stack-plan-slot h3, .stack-catalog-group h3, .manifest-heading h3 { color: var(--text); font: 700 18px/1.2 var(--mono); letter-spacing: .03em; margin: 0 0 8px; text-transform: uppercase; }
.stack-plan-slot [data-plan-selection] { color: var(--muted); font-size: 18px; line-height: 1.3; }
.plan-selection-item { display: block; font-size: 20px; overflow-wrap: anywhere; }
.stack-catalogs { border-top: 1px solid var(--line-strong); margin-top: 12px; padding-top: 16px; }
.catalog-heading { color: var(--cyan); font: 18px/1.2 var(--mono); margin: 0 0 12px; text-transform: uppercase; }
.stack-option { align-items: center; background: var(--surface); border: 1px solid transparent; color: var(--text); cursor: pointer; display: flex; font: inherit; gap: 10px; justify-content: space-between; margin: 4px 0; padding: 9px 10px; text-align: left; transition: transform .16s ease, opacity .16s ease; width: 100%; }
.stack-option:hover, .stack-option[aria-pressed="true"] { border-color: var(--amber); }
.stack-option[aria-pressed="true"] { background: var(--amber-soft); }
.stack-option-main { display: grid; gap: 3px; min-width: 0; }
.stack-option-name { font-size: 20px; line-height: 1.18; overflow-wrap: anywhere; }
.stack-option-sub { color: var(--muted); font: 18px/1.25 var(--mono); text-transform: uppercase; }
.stack-option-action { color: var(--cyan); font: 18px/1 var(--mono); text-transform: uppercase; }
.stack-empty, .manifest-empty { color: var(--muted); font-size: 18px; margin: 0; }
.stack-totals { border-bottom: 1px solid var(--line); border-top: 1px solid var(--line); display: grid; gap: 10px; grid-template-columns: 1fr 1fr; margin: 22px 0 18px; padding: 14px 0; }
.stack-totals div { display: grid; gap: 3px; }
.stack-totals span { color: var(--muted); font: 18px/1 var(--mono); text-transform: uppercase; }
.stack-totals strong { color: var(--amber); font: 700 20px/1.1 var(--mono); }
.manifest-heading { align-items: center; margin-bottom: 10px; }
.copy-all { background: transparent; border: 1px solid var(--cyan); color: var(--cyan); cursor: pointer; font: 18px/1 var(--mono); padding: 7px 8px; text-transform: uppercase; }
.copy-all:disabled { border-color: var(--line); color: var(--faint); cursor: not-allowed; }
.copy-all:not(:disabled):hover { background: var(--cyan); color: var(--ink); }
.manifest { display: grid; gap: 7px; }
.manifest-row { background: var(--surface); border-left: 2px solid var(--cyan); display: grid; gap: 4px; padding: 9px 10px; }
.manifest-row strong { font-size: 18px; overflow-wrap: anywhere; }
.manifest-row span { color: var(--muted); font: 18px/1.35 var(--mono); overflow-wrap: anywhere; }
.manifest-row a { color: var(--cyan); }
.copy-status { color: var(--green); font: 16px/1.3 var(--mono); margin: 12px 0 0; min-height: 20px; }
.style-reason { border-left: 2px solid var(--cyan); color: var(--muted); font-size: 18px; line-height: 1.3; margin: 0 0 13px; padding-left: 10px; }
.card-footer { align-items: center; flex-wrap: wrap; gap: 10px; }
.card-add { background: transparent; border: 1px solid var(--cyan); color: var(--cyan); cursor: pointer; font: 18px/1.1 var(--mono); margin-left: auto; padding: 7px 8px; text-transform: uppercase; }
.card-add:hover, .card-add[aria-pressed="true"] { background: var(--cyan); color: var(--ink); }
.entry-card.is-stack-selected { border: 2px solid var(--amber); box-shadow: 0 0 0 3px var(--amber-soft); }
[hidden] { display: none !important; }
.filters { background: rgba(23, 28, 32, .97); border: 1px solid var(--line); margin-bottom: 12px; padding: 10px 12px; position: sticky; top: var(--stage-nav-height); z-index: 8; }
.search-field { align-items: center; display: flex; gap: 16px; }
.search-field span { color: var(--amber); flex: 0 0 auto; font: 16px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; }
.search-field input { background: var(--ink); border: 1px solid var(--line-strong); color: var(--text); font: 18px/1.2 var(--sans); min-width: 0; outline: none; padding: 10px 12px; width: 100%; }
.search-field input:focus { border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(114, 215, 209, .16); }
.search-field input::placeholder { color: var(--faint); }
.filter-row { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 13px; }
.filter-chip { background: transparent; border: 1px solid var(--line-strong); color: var(--muted); cursor: pointer; font: 16px/1.1 var(--mono); padding: 8px 9px; }
.filter-chip b { color: var(--cyan); font-weight: 500; }
.filter-chip:hover:not(:disabled), .filter-chip[aria-pressed="true"] { background: var(--amber-soft); border-color: var(--amber); color: var(--text); }
.filter-chip:disabled { color: var(--faint); cursor: not-allowed; opacity: .6; }
.filter-chip:disabled b { color: var(--faint); }
.decision-matrix { background: #12171a; border: 1px solid var(--line); margin-bottom: 12px; padding: 10px 14px; }
.matrix-count { color: var(--cyan); display: block; font: 18px/1 var(--mono); margin-bottom: 7px; white-space: nowrap; }
.matrix-body { margin-top: 0; }
.matrix-empty { color: var(--muted); margin: 0; }
.matrix-row { border-top: 1px solid var(--line); display: grid; gap: 18px; grid-template-columns: minmax(130px, .35fr) minmax(0, 1fr); padding: 15px 0; }
.matrix-need { display: grid; gap: 5px; align-content: start; }
.matrix-need span { color: var(--muted); font: 15px/1 var(--mono); text-transform: uppercase; }
.matrix-need strong { font-size: 18px; line-height: 1.25; }
.matrix-options { display: grid; gap: 7px; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.matrix-option { align-items: flex-start; background: var(--surface); display: flex; flex-direction: column; gap: 7px; justify-content: space-between; min-width: 0; padding: 9px 11px; }
.matrix-option > strong { font-size: 20px; line-height: 1.18; overflow-wrap: anywhere; }
.matrix-option em { align-self: flex-end; color: var(--amber); font: 18px/1 var(--mono); white-space: nowrap; }
.score-button { background: transparent; border: 0; color: var(--amber); cursor: pointer; font: 18px/1 var(--mono); padding: 0; text-transform: uppercase; }
.score-button:hover { color: var(--text); text-decoration: underline; text-underline-offset: 4px; }
.card-footer { position: relative; }
.score-popover { background: #0d1113; border: 1px solid var(--amber); bottom: 28px; color: var(--muted); font-size: 18px; left: 0; min-width: 255px; padding: 14px; position: absolute; z-index: 3; }
.score-popover strong { color: var(--amber); font: 700 20px/1 var(--mono); }
.score-popover p { margin: 10px 0 0; }
.score-popover ul { border-bottom: 1px solid var(--line); border-top: 1px solid var(--line); list-style: none; margin: 10px 0 0; padding: 8px 0; }
.score-popover li { display: flex; justify-content: space-between; padding: 3px 0; }
.score-popover li span { color: var(--muted); }
.score-popover .score-date { color: var(--muted); font: 15px/1.3 var(--mono); }
.is-explicit .card-image, .is-explicit .card-video { filter: blur(15px); }
.is-explicit:hover .card-image, .is-explicit:hover .card-video { filter: none; }
@media (max-width: 760px) {
  .topbar-status { font-size: 14px; }
  .status-divider, .topbar-status .status-dot { display: none; }
  .stage-header, .cut-panel { align-items: flex-start; flex-direction: column; gap: 10px; }
  .stage-heading { align-items: flex-start; flex-direction: column; gap: 4px; }
  .stage-meta { min-width: 0; }
  .layer-link { margin-left: 0; }
  .layers-heading { flex-direction: column; }
  .empty-state { flex-direction: column; }
  .stage-layout { grid-template-columns: 1fr; }
  .stack-builder { max-height: none; position: static; }
  .search-field { align-items: flex-start; flex-direction: column; gap: 8px; }
  .matrix-row { grid-template-columns: 1fr; }
  .matrix-options { grid-template-columns: 1fr; }
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

  const selected = {base: null, layer: [], motion: null, voice: null};
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
  const updateStyleVisibility = () => {
    const animeMode = page === 'persona' && activeFacet === 'style: anime';
    document.querySelectorAll('.persona-anime-option').forEach((option) => { option.hidden = !animeMode; });
  };
  const matches = (card, query, facet = '') => {
    const textMatch = !query || (card.dataset.search || '').includes(query);
    const animeMode = page === 'persona' && (activeFacet === 'style: anime' || facet === 'style: anime');
    const isAnime = card.dataset.style === 'anime-illustration';
    const styleMatch = page !== 'persona' || (animeMode ? isAnime : !isAnime);
    const facetMatch = !facet || (facet === 'style: anime' ? isAnime : cardFacets(card).includes(facet));
    return textMatch && styleMatch && facetMatch;
  };
  const updateFilters = () => {
    const query = (searchInput?.value || '').trim().toLowerCase();
    cards.forEach((card) => { card.hidden = !matches(card, query, activeFacet); });
    const animeCluster = document.querySelector('[data-anime-cluster]');
    if (animeCluster) animeCluster.hidden = !(page === 'persona' && activeFacet === 'style: anime');
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
    updateStyleVisibility();
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
  updateFilters();

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
      const scoreMarkup = score.score ? `<strong>score ${escapeHtml(score.score)}</strong>` : '';
      const communityMarkup = score.community ? `<p>Community anchors: ${Object.entries(score.community).map(([key, value]) => `${escapeHtml(value)} ${escapeHtml(key)}`).join(' · ')}</p>` : '';
      const axesMarkup = axes ? `<ul>${axes}</ul>` : '';
      const verdictMarkup = score.verdict ? `<p>${escapeHtml(score.verdict)}</p>` : '';
      const dateMarkup = score.pulled_at ? `<span class="score-date">pulled ${escapeHtml(score.pulled_at)}</span>` : '';
      popover.innerHTML = `${scoreMarkup}${communityMarkup}${axesMarkup}${verdictMarkup}${dateMarkup}`;
      popover.hidden = false;
      button.setAttribute('aria-expanded', 'true');
    });
  });

  const roleLabel = (role) => ({base: 'base', layer: 'layer', motion: 'motion', voice: 'voice'}[role] || role);
  const selectedItems = () => [selected.base, ...selected.layer, selected.motion, selected.voice].filter(Boolean);
  const isSelected = (item) => {
    if (!item || !item.role) return false;
    return item.role === 'layer' ? selected.layer.some((entry) => entry.id === item.id) : selected[item.role]?.id === item.id;
  };
  const toggleSelected = (item) => {
    if (!item || !item.id || !Object.prototype.hasOwnProperty.call(selected, item.role)) return;
    if (item.role === 'layer') {
      const index = selected.layer.findIndex((entry) => entry.id === item.id);
      if (index >= 0) selected.layer.splice(index, 1); else selected.layer.push(item);
      return;
    }
    selected[item.role] = selected[item.role]?.id === item.id ? null : item;
  };
  const updateSelectionVisuals = () => {
    document.querySelectorAll('.stack-option[data-stack-entry]').forEach((option) => {
      let item;
      try { item = JSON.parse(option.dataset.stackEntry || '{}'); } catch (error) { item = {}; }
      const active = isSelected(item);
      option.setAttribute('aria-pressed', String(active));
      const action = option.querySelector('.stack-option-action');
      if (action) action.textContent = active ? 'remove' : 'add';
    });
    document.querySelectorAll('.entry-card[data-stack-payload]').forEach((card) => {
      let item;
      try { item = JSON.parse(card.dataset.stackPayload || '{}'); } catch (error) { item = {}; }
      const active = isSelected(item);
      card.classList.toggle('is-stack-selected', active);
      const addButton = card.querySelector('[data-card-add]');
      if (addButton) {
        addButton.setAttribute('aria-pressed', String(active));
        addButton.textContent = active ? 'remove from stack' : 'add to stack';
      }
    });
  };
  const updatePlan = () => {
    const items = selectedItems();
    const hasStack = items.length > 0;
    const empty = document.querySelector('[data-stack-empty]');
    const plan = document.querySelector('[data-stack-plan]');
    const live = document.querySelector('[data-stack-live]');
    if (empty) empty.hidden = hasStack;
    if (plan) plan.hidden = !hasStack;
    if (live) live.hidden = !hasStack;
    const selectedSummary = document.querySelector('[data-stack-selected]');
    if (selectedSummary) {
      selectedSummary.innerHTML = items.map((item) => `<div class="stack-selected-item"><span>${escapeHtml(roleLabel(item.role))}</span><strong>${escapeHtml(item.name)}</strong></div>`).join('');
    }
    document.querySelectorAll('[data-plan-slot]').forEach((slot) => {
      const role = slot.dataset.planSlot;
      const values = role === 'layer' ? selected.layer : (selected[role] ? [selected[role]] : []);
      const target = slot.querySelector('[data-plan-selection]');
      if (target) target.innerHTML = values.map((item) => `<span class="plan-selection-item">${escapeHtml(item.name)}</span>`).join('');
    });
  };
  const manifestRows = () => {
    const rows = [];
    const seen = new Set();
    selectedItems().forEach((item) => {
      const models = Array.isArray(item.models) ? item.models : [];
      models.forEach((model) => {
        if (!model.name || !model.folder || model.size_mb == null || !exactVersion(model.url)) return;
        const key = `${model.name}|${model.url}`;
        if (seen.has(key)) return;
        seen.add(key);
        rows.push({name: model.name, folder: model.folder, size: model.size_mb, url: model.url});
      });
    });
    return rows;
  };

  const updateStack = () => {
    const items = selectedItems();
    const vram = items.reduce((sum, item) => sum + (Number(item.vram) || 0), 0);
    const disk = items.reduce((sum, item) => sum + (Number(item.disk) || 0), 0);
    updatePlan();
    updateSelectionVisuals();
    const vramNode = document.querySelector('[data-stack-vram]');
    const diskNode = document.querySelector('[data-stack-disk]');
    if (vramNode) vramNode.textContent = `${vram} GB`;
    if (diskNode) diskNode.textContent = formatSize(disk);
    const rows = manifestRows();
    const manifest = document.querySelector('[data-stack-manifest]');
    const copyButton = document.querySelector('[data-copy-all]');
    if (manifest) {
      manifest.innerHTML = rows.map((row) => `<div class="manifest-row"><strong>${escapeHtml(row.name)}</strong><span>${escapeHtml(row.folder)} · ${formatSize(row.size)}</span><a href="${escapeHtml(row.url)}" target="_blank" rel="noreferrer">exact version ↗</a></div>`).join('');
    }
    if (copyButton) copyButton.disabled = rows.length === 0;
  };

  document.querySelectorAll('.stack-option').forEach((option) => {
    option.addEventListener('click', () => {
      let item;
      try { item = JSON.parse(option.dataset.stackEntry || '{}'); } catch (error) { return; }
      toggleSelected(item);
      updateStack();
    });
  });

  document.querySelectorAll('[data-card-add]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const card = button.closest('.entry-card');
      if (!card) return;
      let item;
      try { item = JSON.parse(card.dataset.stackPayload || '{}'); } catch (error) { return; }
      toggleSelected(item);
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
