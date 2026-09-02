#!/usr/bin/env python3
"""garimpo v0 — civitai candidate harvester.

Provenance (assembly law, refs cloned at /tmp/garimpo-refs/):
- Confuzu/CivitAI-Model-grabber/fetch_all_models.py:
  metadata.nextPage URL walking, circular-pagination guard, MAX_PAGES cap,
  bearer token in header never in URL, typed error messages per status.
- dreamfast/go-civitai-downloader/internal/api/client.go:
  retry ladder (429 -> sleep 5s*attempt capped 30s, 5xx -> 3s*attempt,
  401/403 fail fast), polite sleep between pages, nsfw param handling.
- Live API adaptation 2026-09-01: period=90d rejected by API (ZodError,
  valid: Day|Week|Month|Year|AllTime) -> persona lane uses period=Month.

IN:  no args. Optional --nsfw (only honored when ~/.config/civitai/api.key exists).
OUT: data/candidates-persona.json, data/candidates-workflows.json,
     data/candidates-nsfw.json, data/pull_log.json
"""
import json
import sys
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API = "https://civitai.com/api/v1/models"
KEY_FILE = Path.home() / ".config/civitai/api.key"
DATA_DIR = Path("/home/eder/Documentos/civitai-library/data")
MAX_PAGES = 20
PULL_LOG = []


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_key():
    try:
        key = KEY_FILE.read_text().strip()
        return key or None
    except OSError:
        return None


def http_get(url, key, tries=3):
    req = Request(url, headers={"User-Agent": "garimpo/0 (+civitai-library)"})
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    for attempt in range(tries):
        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read())
                PULL_LOG.append({"url": url, "status": resp.status,
                                 "items": len(body.get("items", [])), "at": now()})
                return body
        except HTTPError as e:
            PULL_LOG.append({"url": url, "status": e.code, "items": 0, "at": now()})
            if e.code in (401, 403):
                raise RuntimeError(f"auth failed ({e.code}) for {url}") from e
            if e.code == 429:
                wait = min(5 * (attempt + 1), 30)
                print(f"429 rate limited, sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code >= 500 and attempt < tries - 1:
                wait = 3 * (attempt + 1)
                print(f"{e.code} server error, retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"{e.code} on {url}, skipping", file=sys.stderr)
            return None
        except (OSError, json.JSONDecodeError) as e:
            print(f"network/json error on {url}: {e}", file=sys.stderr)
            if attempt < tries - 1:
                time.sleep(3)
                continue
            return None
    return None


def thumb450(url):
    if url and "original=true" in url:
        return url.replace("original=true", "width=450")
    return url


def to_candidate(m, period):
    versions = m.get("modelVersions") or []
    first = versions[0] if versions else {}
    image = next((i for v in versions for i in (v.get("images") or []) if i.get("url")), {})
    creator = m.get("creator") or {}
    username = creator.get("username")
    return {
        "id": m.get("id"),
        "name": m.get("name"),
        "type": m.get("type"),
        "baseModel": first.get("baseModel"),
        "nsfwLevel": m.get("nsfwLevel"),
        "creator": {"username": username,
                    "href": f"https://civitai.com/users/{username}" if username else None},
        "stats": {**(m.get("stats") or {}),
                  "period": period, "pulled_at": now()},
        "lastUpdated": first.get("publishedAt"),
        "earlyAccessInfo": m.get("earlyAccessInfo") or first.get("earlyAccessInfo"),
        "license": {"allowCommercialUse": m.get("allowCommercialUse"),
                    "allowNoCredit": m.get("allowNoCredit"),
                    "allowDerivatives": m.get("allowDerivatives")},
        "source_url": f"https://civitai.com/models/{m.get('id')}",
        "preview": {"url_width450": thumb450(image.get("url")),
                    "url_original": image.get("url")},
        "versions": [{
            "id": v.get("id"), "name": v.get("name"),
            "baseModel": v.get("baseModel"), "updatedAt": v.get("publishedAt"),
            "downloadUrl": v.get("downloadUrl"),
            "files": [{"name": f.get("name"), "type": f.get("type"),
                       "sizeKB": f.get("sizeKB")} for f in (v.get("files") or [])],
        } for v in versions],
    }


def harvest(lane, params, want, key):
    candidates, seen_ids, seen_pages = [], set(), set()
    url = f"{API}?{params}"
    for _ in range(MAX_PAGES):
        if len(candidates) >= want or url in seen_pages:
            break
        seen_pages.add(url)
        page = http_get(url, key)
        if page is None:
            break
        items = page.get("items") or []
        if not items:
            print(f"{lane}: empty page, lane done", file=sys.stderr)
            break
        for m in items:
            if m.get("id") not in seen_ids:
                seen_ids.add(m.get("id"))
                candidates.append(to_candidate(m, lane.get("period")))
        url = (page.get("metadata") or {}).get("nextPage")
        if not url:
            break
        time.sleep(0.5)
    picked = candidates[:want]
    print(f"{lane['name']}: {len(picked)} candidates", file=sys.stderr)
    return picked


def write_json(name, payload):
    path = DATA_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"wrote {path} ({path.stat().st_size} bytes)", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="civitai candidate harvester")
    parser.add_argument("--nsfw", action="store_true", help="pull nsfw lane (needs api key)")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    key = load_key()
    if not key:
        print("no api key at ~/.config/civitai/api.key, pulling SFW only", file=sys.stderr)

    persona = harvest({"name": "persona", "period": "Month"},
                      "limit=50&types=LORA&types=Checkpoint&sort=Highest%20Rated&period=Month",
                      40, key)
    write_json("candidates-persona.json", persona)

    workflows = harvest({"name": "workflows", "period": None},
                        "limit=50&types=Workflows&sort=Highest%20Rated", 30, key)
    write_json("candidates-workflows.json", workflows)

    if args.nsfw and key:
        nsfw = harvest({"name": "nsfw", "period": "Month"},
                       "limit=50&types=LORA&sort=Highest%20Rated&period=Month&nsfw=true",
                       30, key)
        write_json("candidates-nsfw.json", nsfw)
    else:
        reason = "no key" if not key else "nsfw not requested (--nsfw absent)"
        write_json("candidates-nsfw.json",
                   {"blocked": reason,
                    "tried": ["~/.config/civitai/api.key lookup", "auth check skipped"]})

    write_json("pull_log.json", PULL_LOG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
