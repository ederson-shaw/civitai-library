#!/usr/bin/env python3
"""cluster v1 — near-duplicate family detection for funnel candidates (REBUILD-SPEC noise rule:
"near-duplicate style families: cluster, keep best-1, note cuts").

Family = same normalized name-signature (token set, order-free) AND same base model family.
Best-1 by (composite_auto, thumbs ratio, downloadCount) — falls back gracefully when
score.py has not run yet (uses stats directly).

IN:  data/funnel/raw-*.json (any subset on disk)
OUT: --dry-run (default): prints families + what would be cut, writes NOTHING
     --apply: writes data/funnel/clusters.json
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

FUNNEL = Path(__file__).resolve().parent.parent / "data" / "funnel"
STOP = {"the", "a", "v", "for", "and", "with", "of", "in", "on", "my", "your", "lora", "checkpoint",
        "flux", "sdxl", "sd15", "sd", "pony", "illustrious", "xl", "turbo", "style", "model"}


def signature(name):
    tokens = sorted({t for t in re.findall(r"[a-z0-9]+", (name or "").lower()) if t not in STOP and len(t) > 2})
    return " ".join(tokens[:6])


def base_family(entry):
    base = (entry.get("baseModel") or entry.get("baseModels") or "")
    if isinstance(base, list):
        base = base[0] if base else ""
    return (base or "?").split()[0].lower() if base else "?"


def quality(entry):
    stats = entry.get("stats") or {}
    dl = stats.get("downloadCount") or 0
    th = stats.get("thumbsUpCount") or 0
    ratio = th / dl if dl >= 500 else 0.0
    return (ratio, dl)


def main():
    apply_mode = "--apply" in sys.argv
    families = defaultdict(list)
    seen_ids = set()
    for f in sorted(FUNNEL.glob("raw-*.json")):
        try:
            items = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for it in items if isinstance(items, list) else []:
            if not isinstance(it, dict) or it.get("id") in seen_ids:
                continue
            seen_ids.add(it.get("id"))
            families[(signature(it.get("name")), base_family(it))].append(it)

    dupes = {k: v for k, v in families.items() if len(v) > 1}
    cut_total = 0
    report = []
    for (sig, base), members in sorted(dupes.items(), key=lambda kv: -len(kv[1])):
        ranked = sorted(members, key=quality, reverse=True)
        keep = ranked[0]
        cuts = ranked[1:]
        cut_total += len(cuts)
        report.append({
            "family": f"{sig} [{base}]",
            "keep": {"id": keep.get("id"), "name": keep.get("name"), "stats": keep.get("stats")},
            "cut": [{"id": m.get("id"), "name": m.get("name")} for m in cuts],
        })
    out = {"families": len(dupes), "cut_total": cut_total, "note": "kept best by ratio+downloads; cuts listed for transparency panel", "report": report}
    for fam in report[:15]:
        print(f"{fam['family']}: keep {fam['keep']['name']} | cut {len(fam['cut'])}", file=sys.stderr)
    print(f"FAMILIES {len(dupes)} CUT_TOTAL {cut_total} (of {len(seen_ids)} unique candidates)", file=sys.stderr)
    if apply_mode:
        (FUNNEL / "clusters.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
        print("wrote data/funnel/clusters.json", file=sys.stderr)


if __name__ == "__main__":
    main()
