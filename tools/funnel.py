#!/usr/bin/env python3
"""garimpo v0.3 — the big funnel: 5-8k candidates across 4 lanes, site filters later.

Reuses garimpo.py wholesale (assembly law): http_get (bearer, UA garimpo/0.1,
429/5xx retry ladder), to_candidate schema (id/name/type/baseModel/nsfwLevel/
creator/stats/lastUpdated/license/source_url/preview/versions minimal),
thumb450, now. NO gallery/usage walks this round — that is post-filter
enrichment owned by v0.1/v0.2 collectors.

Lanes (task 2026-09-02, seeds from research/community-sources.md 2A/2E,
api surface from research/civitai-api-census.md):
- workflows: types=Workflows x {Most Downloaded, Highest Rated, Newest} x
  {AllTime, Year, Month}, ~800 each, cursor walk (limit=100, 0.5s polite).
- persona: types=LORA+Checkpoint x same 3 sorts x {AllTime, Year} ~800 each,
  PLUS tag seeds (realistic, photorealistic, photography, instagram,
  portrait) ~400 each.
- nsfw (key required): nsfw=true types=LORA x {Most Downloaded, Highest
  Rated} x {AllTime, Year} ~500, tag=nsfw ~400, community model query seeds
  (chroma, biglust, lustify, aramanta, araminta, anteros, bigasp) ~150 each,
  PLUS same-creator catalogue walks (username param, top creators of the
  matched models, ~150 each, max 12).
- video: types=Workflows tag seeds (wan, ltx, hunyuan, minimax, video) ~300.

query param rules: cursor mode only (never page together with query — 400).
OUT: data/funnel/raw-<lane>-<slice>.json (flushed after EVERY page),
data/funnel/index.json (rewritten after every slice), data/funnel/
all-candidates.json (id-keyed dedupe, first-wins in walk order),
data/funnel/pull_log.json. Caps: 8000 unique OR ~85 min, whichever first,
then stop cleanly. 3 slice-aborts (each already past garimpo's internal
retry ladder) -> /tmp/garimpo03-attempts.md and exit 2.
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garimpo
from garimpo import API, http_get, load_key, now, to_candidate

FUNNEL = Path("/home/eder/Documentos/civitai-library/data/funnel")
MAX_UNIQUE = 8000
MAX_SECONDS = 85 * 60
MAX_CREATOR_WALKS = 12
ATTEMPTS_FILE = Path("/tmp/garimpo03-attempts.md")


def q(**params):
    return urlencode(params, doseq=True, quote_via=quote)


def slug(text):
    return text.lower().replace(" ", "")


def slices():
    wf = {"types": ["Workflows"]}
    persona = {"types": ["LORA", "Checkpoint"]}
    plan = []
    for sort in ("Most Downloaded", "Highest Rated", "Newest"):
        for period in ("AllTime", "Year", "Month"):
            plan.append({"lane": "workflows", "slice": f"{slug(sort)}-{period.lower()}",
                         "want": 800, "label": f"{sort}/{period}",
                         "params": {**wf, "sort": sort, "period": period}})
    for sort in ("Most Downloaded", "Highest Rated", "Newest"):
        for period in ("AllTime", "Year"):
            plan.append({"lane": "persona", "slice": f"{slug(sort)}-{period.lower()}",
                         "want": 800, "label": f"{sort}/{period}",
                         "params": {**persona, "sort": sort, "period": period}})
    for tag in ("realistic", "photorealistic", "photography", "instagram", "portrait"):
        plan.append({"lane": "persona", "slice": f"tag-{tag}",
                     "want": 400, "label": f"tag={tag}",
                     "params": {**persona, "tag": tag,
                                "sort": "Most Downloaded", "period": "AllTime"}})
    for sort in ("Most Downloaded", "Highest Rated"):
        for period in ("AllTime", "Year"):
            plan.append({"lane": "nsfw", "slice": f"{slug(sort)}-{period.lower()}",
                         "want": 500, "label": f"{sort}/{period}/nsfw",
                         "params": {"types": ["LORA"], "nsfw": "true",
                                    "sort": sort, "period": period}})
    plan.append({"lane": "nsfw", "slice": "tag-nsfw", "want": 400,
                 "label": "tag=nsfw",
                 "params": {"types": ["LORA"], "nsfw": "true", "tag": "nsfw",
                            "sort": "Most Downloaded", "period": "AllTime"}})
    for seed in ("chroma", "biglust", "lustify", "aramanta", "araminta",
                 "anteros", "bigasp"):
        plan.append({"lane": "nsfw", "slice": f"query-{seed}", "want": 150,
                     "label": f"query={seed}", "seed": seed,
                     "harvest_creators": True,
                     "params": {"nsfw": "true", "query": seed,
                                "sort": "Most Downloaded", "period": "AllTime"}})
    for tag in ("wan", "ltx", "hunyuan", "minimax", "video"):
        plan.append({"lane": "video", "slice": f"tag-{tag}", "want": 300,
                     "label": f"tag={tag}/video",
                     "params": {**wf, "tag": tag,
                                "sort": "Most Downloaded", "period": "AllTime"}})
    return plan


def walk(key, spec, state, started):
    records = []
    seen_pages = set()
    url = f"{API}?{q(limit=100, **spec['params'])}"
    path = FUNNEL / f"raw-{spec['lane']}-{spec['slice']}.json"
    while url and url not in seen_pages and len(records) < spec["want"]:
        if len(state["seen"]) >= MAX_UNIQUE or time.time() - started > MAX_SECONDS:
            state["stop"] = True
            break
        seen_pages.add(url)
        try:
            page = http_get(url, key)
        except RuntimeError as e:
            state["auth_dead"] = str(e)
            break
        if page is None:
            state["fails"] += 1
            state["attempts"].append(f"{now()} slice {spec['lane']}/{spec['slice']}"
                                     f" aborted after retry ladder (see pull_log)")
            break
        state["fails"] = 0
        items = page.get("items") or []
        if not items:
            break
        for m in items:
            state["fetched"] += 1
            mid = m.get("id")
            if mid is None or mid in state["seen"]:
                continue
            state["seen"].add(mid)
            records.append(to_candidate(m, spec["label"]))
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        print(f"[{spec['lane']}/{spec['slice']}] +{len(items)} page "
              f"slice={len(records)}/{spec['want']} "
              f"unique={len(state['seen'])} fetched={state['fetched']} "
              f"elapsed={int(time.time() - started)}s", file=sys.stderr)
        url = (page.get("metadata") or {}).get("nextPage")
        time.sleep(0.5)
    return records


def pick_creators(records, seed):
    matched = [r for r in records if seed in (r.get("name") or "").lower()]
    matched.sort(key=lambda r: (r.get("stats") or {}).get("downloadCount") or 0,
                 reverse=True)
    names = []
    for r in matched[:3]:
        username = (r.get("creator") or {}).get("username")
        if username:
            names.append(username)
    return names


def write_index(counts, state, started, key):
    payload = {
        "total_pulled": state["fetched"],
        "per_lane": counts["per_lane"],
        "per_slice": counts["per_slice"],
        "deduped_total": len(state["seen"]),
        "pulled_at": now(),
        "capped_by": ("unique" if len(state["seen"]) >= MAX_UNIQUE
                      else "time" if time.time() - started > MAX_SECONDS
                      else "completed"),
        "nsfw_lane": ("pulled" if counts["per_lane"].get("nsfw")
                      else "skipped-no-key" if not key else "cut-by-cap"),
    }
    (FUNNEL / "index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2))


def write_blocked(state):
    lines = ["# garimpo v0.3 BLOCKED — " + now(), ""]
    lines += [f"- {a}" for a in state["attempts"]]
    if state.get("auth_dead"):
        lines.append(f"- auth dead: {state['auth_dead']}")
    bad = [e for e in garimpo.PULL_LOG if e.get("status") != 200]
    lines.append("")
    lines += [f"- non-200: {e['status']} {e['url'][:160]} at {e['at']}"
              for e in bad[-10:]]
    ATTEMPTS_FILE.write_text("\n".join(lines) + "\n")
    print(f"BLOCKED — attempts written to {ATTEMPTS_FILE}", file=sys.stderr)


def merge_all():
    files = sorted(FUNNEL.glob("raw-*.json"))
    merged = {}
    for f in files:
        for rec in json.loads(f.read_text()):
            merged.setdefault(rec["id"], rec)
    (FUNNEL / "all-candidates.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2))
    return len(merged)


def main():
    FUNNEL.mkdir(parents=True, exist_ok=True)
    key = load_key()
    started = time.time()
    state = {"seen": set(), "fetched": 0, "fails": 0, "attempts": [],
             "stop": False, "auth_dead": None}
    counts = {"per_lane": {}, "per_slice": {}}
    plan = slices()
    if not key:
        plan = [s for s in plan if s["lane"] != "nsfw"]
        print("no api key at ~/.config/civitai/api.key — nsfw lane skipped",
              file=sys.stderr)

    done_creators = set()
    creator_walks = 0
    i = 0
    while i < len(plan):
        if state["stop"] or state["auth_dead"] or state["fails"] >= 3:
            break
        spec = plan[i]
        i += 1
        records = walk(key, spec, state, started)
        if records or (FUNNEL / f"raw-{spec['lane']}-{spec['slice']}.json").exists():
            pass
        name = f"{spec['lane']}/{spec['slice']}"
        counts["per_slice"][name] = len(records)
        counts["per_lane"][spec["lane"]] = counts["per_lane"].get(spec["lane"], 0) \
            + len(records)
        write_index(counts, state, started, key)
        print(f"== slice done {name}: {len(records)} stored", file=sys.stderr)
        if spec.get("harvest_creators") and creator_walks < MAX_CREATOR_WALKS:
            for username in pick_creators(records, spec["seed"]):
                if username in done_creators or creator_walks >= MAX_CREATOR_WALKS:
                    continue
                done_creators.add(username)
                creator_walks += 1
                plan.insert(i, {
                    "lane": "nsfw", "slice": f"creator-{username}", "want": 150,
                    "label": f"username={username}",
                    "params": {"nsfw": "true", "username": username,
                               "sort": "Most Downloaded", "period": "AllTime"}})
                print(f"++ creator walk queued: {username}", file=sys.stderr)

    (FUNNEL / "pull_log.json").write_text(
        json.dumps(garimpo.PULL_LOG, ensure_ascii=False, indent=2))
    deduped = merge_all()
    write_index(counts, state, started, key)
    print(f"FUNNEL DONE unique={len(state['seen'])} fetched={state['fetched']} "
          f"deduped_file={deduped} capped_by="
          f"{('unique' if len(state['seen']) >= MAX_UNIQUE else 'time' if time.time() - started > MAX_SECONDS else 'completed')}",
          file=sys.stderr)
    if state["auth_dead"] or state["fails"] >= 3:
        write_blocked(state)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
