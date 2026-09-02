# Civitai API + Tooling Census — live-web, 2026-09-01

Method: every claim below was verified against pages fetched TODAY (2026-09-01) from
developer.civitai.com, live `curl` probes against civitai.com/api/v1, and the GitHub
Search API (stars/last-push pulled live 2026-09-01). Nothing here is from training
memory. Old docs URL `developer.civitai.com/docs/api/public-rest` is **404** — the docs
moved to `developer.civitai.com/site/` (verified: 404 on old URL, 200 on new pages).
Docs also expose LLM-friendly `.md` versions (e.g. `/site/reference/models.md`).

Primary sources:
- Docs index: https://developer.civitai.com/site/
- Reference overview (endpoint table): https://developer.civitai.com/site/reference/
- Docs repo: https://github.com/civitai/civitai-developer-docs

---

## 1. API surface (as documented today)

### 1.1 Base + envelope
- Base URL: `https://civitai.com/api/v1`, all responses `application/json; charset=utf-8`
  [source: https://developer.civitai.com/site/reference/]
- List envelopes: `{ items: [...], metadata: { nextCursor, nextPage, currentPage?, pageSize? } }`
  [source: https://developer.civitai.com/site/reference/models]

### 1.2 Endpoint table (public REST surface)
| Resource | Endpoints | Status |
|---|---|---|
| Models | `GET /models`, `GET /models/{id}` | verified [ref/models] |
| Model versions | `GET /model-versions/{id}`, `GET /model-versions/by-hash/{hash}`, `POST /model-versions/by-hash` (≤100 SHA256), `POST /model-versions/by-hash/ids` (≤10 000), `GET /model-versions/mini/{id}` | verified [ref/model-versions] |
| Images | `GET /images` (single endpoint; single lookup via `?imageId=`) | verified [ref/images] |
| Articles | `GET /articles`, `GET /articles/{id}` | listed [ref overview] |
| Collections | `GET /collections`, `GET /collections/{id}` | verified [ref/collections] |
| Creators | `GET /creators` | verified [ref/creators] |
| Tags | `GET /tags` | listed [ref overview] |
| Users | `GET /me` (auth), `GET /users` (ids/prefix search) | verified [ref/users] |
| Permissions | `GET /permissions/check` | listed [ref overview] |
| Vault | `GET /vault/get`, `GET /vault/all`, `GET /vault/check-vault`, `POST /vault/toggle-version` | listed [ref overview] |
| Enums | `GET /enums` | verified live (returns keys: ActiveBaseModel, BaseModel, BaseModelType, ModelFileType, ModelType) |

[source: https://developer.civitai.com/site/reference/ — full endpoint table fetched 2026-09-01]

### 1.3 Auth (anonymous vs api key)
- Three categories: **Public** (full access: /creators, /tags, /images, /models/{id},
  /model-versions/*), **Mixed** (public but some params need token — `GET /models`
  `favorites=`/`hidden=` require auth), **Authenticated** (`GET /me` → 401 without token).
  [source: https://developer.civitai.com/site/guide/authentication]
- Token passing: `Authorization: Bearer $TOKEN` (preferred) or `?token=` query param —
  the query form "exists mainly for download-tool compatibility and leaks the token"
  [source: https://developer.civitai.com/site/guide/authentication]
- Token creation: account settings → API Keys
  [source: https://github.com/ashleykleynhans/civitai-downloader README, fetched 2026-09-01]
- OAuth exists for third-party apps [source: https://developer.civitai.com/site/oauth/]
- CORS: open (`*`) on public endpoints; authenticated requests restricted to
  Civitai-owned origins — matters for a static GH-Pages frontend calling the API with a
  key [source: https://developer.civitai.com/site/guide/authentication]
- Edge cache: public responses `Cache-Control: public, s-maxage=300,
  stale-while-revalidate=150`; authed calls skip cache
  [source: https://developer.civitai.com/site/guide/authentication]

### 1.4 Pagination + rate limits
- `page` is 1-indexed; `page * limit ≤ 1000` hard cap → 429 "You've requested too many
  pages, please use cursors instead". Limit caps: 100 `/models`, 200 `/images`,
  200 `/creators`+`/tags` [source: https://developer.civitai.com/site/guide/pagination]
- Cursor-based: opaque `metadata.nextCursor`; REQUIRED for `?query=` full-text search
  (Meilisearch); `query`+`page` together → 400. Cursors stay consistent while content
  shifts — the right mode for a garimpo walk
  [source: https://developer.civitai.com/site/guide/pagination]
- Rate limits: **no published per-endpoint SLA**. Cloudflare edge limits (DDoS/abuse)
  only; 429 → backoff exponential ~1s→30s, no Retry-After on most failures
  [source: https://developer.civitai.com/site/guide/errors]
- Collections endpoints are "conservatively rate-limited; on a 429 respect the
  Retry-After header" [source: https://developer.civitai.com/site/reference/collections]
- Known wall: `GET /images?modelId=<huge checkpoint>` can exceed Cloudflare's 30s
  timeout — docs advise `postId` or cursor walk at limit=100
  [source: https://developer.civitai.com/site/reference/images]

### 1.5 GET /models — the garimpo workhorse
Params (all verified on the live doc page): `limit` (1–100, def 100), `page`, `cursor`,
`query` (Meilisearch full-text), `ids`, `tag`, `username`, `types` (ModelType[]),
`baseModels` (e.g. `SDXL 1.0`, `Flux.1 D`), `checkpointType` (Standard|Trained|Merge),
`sort` (documented: `Highest Rated` | `Most Downloaded` | `Newest` | "..." — full list
says "see source"; OPEN), `period` (AllTime|Year|Month|Week|Day), `nsfw` (bool, def
false), `supportsGeneration`, `fromPlatform`, `earlyAccess`, `primaryFileOnly`,
`favorites` (auth), `hidden` (auth).
[source: https://developer.civitai.com/site/reference/models)

Response per item includes — directly citable stats for curation ranking:
```json
"stats": { "downloadCount": 1272529, "thumbsUpCount": 79272,
           "thumbsDownCount": 202, "commentCount": 1931, "tippedAmountCount": 156742 },
"modelVersions[].stats": { "downloadCount": 215627, "thumbsUpCount": 13828, "thumbsDownCount": 22 }
```
[source: https://developer.civitai.com/site/reference/models — response example]

Moderation signal: `mode` non-null = model moderated; `Archived` drops files[]+downloadUrl,
`TakenDown` also drops images[] [source: https://developer.civitai.com/site/reference/models]

### 1.6 Model versions + downloads
- `files[]` per version: `{ id, name, type, sizeKB, metadata:{format,size,fp},
  pickleScanResult, virusScanResult, hashes:{AutoV1,AutoV2,AutoV3,SHA256,CRC32,BLAKE3},
  downloadUrl, primary }`
  [source: https://developer.civitai.com/site/reference/model-versions]
- Download URL shape (from docs examples + live probes): 
  `https://civitai.com/api/download/models/{modelVersionId}` — note: `/api/download`,
  NOT `/api/v1/download`; per-file `files[].downloadUrl` also present.
  [source: https://developer.civitai.com/site/reference/models + live probe below]
- `GET /model-versions/mini/{id}` returns `requireAuth` (download needs Bearer or
  `?token=`), `checkPermission` (early-access gate), `earlyAccessEndsAt`,
  `canGenerate`, `downloadUrls[]`, `hashes` — cheapest download-decision endpoint
  [source: https://developer.civitai.com/site/reference/model-versions]
- Hash identify: `GET /model-versions/by-hash/{hash}` (any hash type, case-insensitive);
  bulk `POST /by-hash` ≤100; `POST /by-hash/ids` ≤10 000 → `{modelVersionId, hash}[]`
  [source: https://developer.civitai.com/site/reference/model-versions]
- `air` field = AIR URN (`urn:air:sdxl:checkpoint:civitai:827184@2514310`) — canonical
  id format [source: https://developer.civitai.com/site/reference/model-versions + /site/guide/air]

### 1.7 Images + workflow extraction (the trivia that matters)
- `GET /images` params: `limit` (0–200, def 50), `page`, `cursor`, `postId`, `modelId`,
  `modelVersionId`, `imageId`, `username`, `userId`, `period`, `sort` (Most Reactions |
  Most Comments | Most Collected | Newest | Oldest | Random), `nsfw`
  (None|Soft|Mature|X|boolean — legacy), `browsingLevel` (bitmask, takes precedence),
  `tags` (tag IDs), `type` (image|video|audio), `baseModels`, `withMeta` (bool —
  includes full `meta` object)
  [source: https://developer.civitai.com/site/reference/images]
- Image item stats: `cryCount, laughCount, likeCount, dislikeCount, heartCount,
  commentCount` — community reaction numbers for curation
  [source: https://developer.civitai.com/site/reference/images]
- `meta` is free-form; "tools like Automatic1111 and ComfyUI drop in their own keys";
  `meta.civitaiResources[]` maps each used resource to its `modelVersionId`;
  top-level `modelVersionIds` = deduped resource list
  [source: https://developer.civitai.com/site/reference/images]
- **Workflows ARE extractable from image metadata** — live probe 2026-09-01:
  `curl "https://civitai.com/api/v1/images?limit=8&sort=Most%20Reactions&withMeta=true&type=image"`
  → meta keys observed: `..., comfy, prompt, resources, workflow, ...` — i.e. ComfyUI
  images on Civitai carry the full workflow JSON in `meta.workflow`. (Docs only say
  free-form + ComfyUI keys; the `workflow` key itself is confirmed by probe, not docs.)
- **Workflows are also a first-class model type**: `ModelType` enum includes
  `"Workflows"` [source: https://developer.civitai.com/site/reference/enums + live
  GET /enums probe 2026-09-01]. Live probes of `?types=Workflows` models show the
  workflow payload ships as `files[]` with `type: "Archive"` (zip of ComfyUI json),
  `metadata.format: "Other"` (3 probed: "FLUX.1-DEV & Kontext Workflows Megapack",
  "【WAN2.1】IMG to VIDEO", a Forge regional-prompt guide). `ModelFileType` enum
  (Model, Text Encoder, Pruned Model, Negative, Training Data, VAE, Config, Archive)
  has NO dedicated "Workflow" file type — so: workflow model = version + zip file.
  [source: live probes + https://developer.civitai.com/site/reference/enums]

### 1.8 Creators / Users / Tags / Collections
- `GET /creators`: `limit` (1–200, def 20), `page` only (no cursor), `query` (username
  full-text). Returns `{username, modelCount, link (prebuilt /models query), image}`.
  Walk trick from docs: alphabetical, so `query=A`, `query=B`… beats linear paging.
  [source: https://developer.civitai.com/site/reference/creators]
- `GET /users`: `ids` (map ids→usernames) or `query` (prefix LIKE). Returns lean
  `{id, username, avatarNsfw}` [source: https://developer.civitai.com/site/reference/users]
- `GET /tags`: page-based; counts unreliable ("some report 0") — drive UI off `nextPage`
  [source: https://developer.civitai.com/site/guide/pagination]
- `GET /collections` + `GET /collections/{id}`: PUBLIC collections only (private = 404),
  always evaluated anonymous (token never changes result), edge-cached, conservative
  rate limits. Params: `limit` (1–100), `cursor` (id keyset, Newest sort only),
  `query` (≤100 chars, name full-text), `sort` (Newest|Most Followers), `nsfw` (bool).
  Items: `{id, name, description, type, nsfwLevel, itemCount, coverImageUrl, user}` —
  ready-made community curation signal for a garimpo.
  [source: https://developer.civitai.com/site/reference/collections]

### 1.9 Image CDN URL construction
- API returns absolute CDN urls shaped:
  `https://image.civitai.com/<sig>/<uuid>/original=true/<uuid>.jpeg`
  (live probe 2026-09-01: GET /images?limit=1&sort=Newest)
- Resize transform = path segment swap `original=true` → `width=450`. Live probe
  (2026-09-01): original = 8 330 743 bytes `image/png` (301→200); `width=450` variant =
  70 051 bytes `image/jpeg` (301→200). So thumbnails are real, cheap, and derivable
  client-side from any returned url.
- Independent confirmation of the `width=450` pattern:
  https://github.com/Confuzu/CivitAI-Model-grabber README documents
  `https://image.civitai.com/.../width=450/ID.jpeg` in its output format.
- Other transforms (format=/quality=/height=): OPEN — not documented, not probed.
- `hash` field on images is a BlurHash for placeholders
  [source: https://developer.civitai.com/site/reference/images]

### 1.10 License metadata fields
On every model item: `allowNoCredit` (bool), `allowCommercialUse` (set-string, e.g.
`"{Image,RentCivit}"`), `allowDerivatives` (bool), `allowDifferentLicense` (bool),
plus `minor`, `poi`, `sfwOnly` flags.
[source: https://developer.civitai.com/site/reference/models — response example]
Version level adds `availability` (Public/…), `usageControl` ("Download"),
`uploadType`, `earlyAccessConfig/earlyAccessEndsAt`
[source: https://developer.civitai.com/site/reference/model-versions]

### 1.11 NSFW gating behavior
- Models: `nsfw` bool defaults **false** (mature excluded); `nsfw=true` includes mature;
  param "ignored on SFW-gated regions" (green domain / restricted regions → SFW clamp)
  [source: https://developer.civitai.com/site/reference/models]
- Images: "Authenticated callers see content up to their configured browsing level;
  anonymous callers are capped at the public browsing level". `nsfw` param is legacy
  (None|Soft|Mature|X|bool); `browsingLevel` bitmask takes precedence.
  [source: https://developer.civitai.com/site/reference/images]
- Model-version previews (`images[]`) filtered by caller browsing level
  [source: https://developer.civitai.com/site/reference/model-versions]
- Collections: mature covers/collections clamped to SFW ceiling in restricted regions
  regardless of `nsfw` param [source: https://developer.civitai.com/site/reference/collections]
- OPEN: the exact numeric level of the anonymous "public browsing level" is not
  defined in docs — probe with/without key before assuming what anonymous sees.

### 1.12 Other doc surfaces worth knowing
- Official CLI for read commands: `civitai` CLI (search/fetch endpoints from terminal)
  [source: https://developer.civitai.com/site/guide/cli]
- Orchestration API (paid generation) + MCP server live at
  https://developer.civitai.com/orchestration/ and /site/mcp/ — out of scope for
  garimpo but the MCP docs confirm the same v1 surface.
- Third-party warning worth testing: civitai-mcp-ultimate claims "Civitai REST API
  search is broken since May 2025" (their reason for Meilisearch-first design)
  [source: https://github.com/timoncool/civitai-mcp-ultimate README fetched 2026-09-01].
  Official docs still document `query` as Meilisearch full-text. OPEN: stress-test
  `?query=` before betting the garimpo on it.

---

## 2. Census table — 31 GitHub projects (stars/last-push fetched live 2026-09-01 via GitHub Search API)

DEAD = no commit in ~18+ months or archived. "reuse" = what we steal for garimpo.

| # | name | url | ★ | last push | what it does | reuse |
|---|---|---|---|---|---|---|
| 1 | civitai/civitai | https://github.com/civitai/civitai | 7241 | 2026-09-02 | the platform itself (Next.js monorepo — contains the actual REST API handlers) | source of truth for response shapes/undocumented fields |
| 2 | butaixianran/Stable-Diffusion-Webui-Civitai-Helper | https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper | 2527 | 2026-06-09 | A1111 extension: model manager, metadata fetch, preview dl | metadata-mapping + local-model↔api-id matching logic |
| 3 | civitai/sd_civitai_extension DEAD | https://github.com/civitai/sd_civitai_extension | 2358 | 2024-07-17 | official A1111 integration (all Civitai models in webui) | historical; token/download flow reference |
| 4 | BlafKing/sd-civitai-browser-plus ARCHIVED | https://github.com/BlafKing/sd-civitai-browser-plus | 381 | 2025-07-09 (archived) | full CivitAI browser inside webui: dl, delete, update scan, installed-list, tags | best-ever feature matrix of a civitai browser UI — spec material |
| 5 | giriss/comfy-image-saver | https://github.com/giriss/comfy-image-saver | 343 | 2026-07-17 | saves ComfyUI images with gen-metadata, Civitai-compatible (embeds workflow) | how workflow JSON gets into image meta (confirms §1.7 pipeline) |
| 6 | LuqP2/Image-MetaHub | https://github.com/LuqP2/Image-MetaHub | 318 | 2026-09-01 | local-first AI image library manager (ComfyUI/A1111/InvokeAI), search | library-site UX patterns; active |
| 7 | ScreamingHawk/civitai-web-scraper DEAD | https://github.com/ScreamingHawk/civitai-web-scraper | 242 | 2024-03-08 | scrape images+prompts, ini config, local server | simple scrape loop + config shape |
| 8 | tzwm/sd-webui-model-downloader-cn DEAD | https://github.com/tzwm/sd-webui-model-downloader-cn | 239 | 2024-06-18 | no-VPN civitai model downloads (CN mirror path) | mirror/fallback download tricks |
| 9 | ADVICEsama/CivitaiFreeTool | https://github.com/ADVICEsama/CivitaiFreeTool | 190 | 2026-09-01 | CN tool: model download/manage/reverse-parse (hash→model), free-tier focus | by-hash reverse lookup UX |
| 10 | ashleykleynhans/civitai-downloader | https://github.com/ashleykleynhans/civitai-downloader | 174 | 2026-05-11 | single-file python downloader using api key (`download.py`) | cleanest minimal api-key download reference |
| 11 | civitai/civitai_comfy_nodes | https://github.com/civitai/civitai_comfy_nodes | 171 | 2026-06-17 | official Comfy nodes (resource load by hash) | official hash-resolution client code |
| 12 | BAIKEMARK/ComfyUI-Civitai-Toolkit | https://github.com/BAIKEMARK/ComfyUI-Civitai-Toolkit | 138 | 2026-02-19 | all-in-one Civitai center in ComfyUI: browse online, manage local, community stats | stats-presentation UI |
| 13 | MoonGoblinDev/Civicomfy | https://github.com/MoonGoblinDev/Civicomfy | 119 | 2026-02-14 | civitai model downloader for ComfyUI | download-into-comfy layout logic |
| 14 | Confuzu/CivitAI_Image_grabber | https://github.com/Confuzu/CivitAI_Image_grabber | 116 | 2026-04-29 | bulk image/video downloader by user/modelID/tag/versionId; interactive+CLI; sqlite tracking; concurrent | **API-walking + sqlite dedupe/state skeleton (python)** |
| 15 | dreamfast/go-civitai-downloader | https://github.com/dreamfast/go-civitai-downloader | 109 | 2026-08-18 | go archiver: criteria scan → confirm → concurrent dl; sqlite (models/files/stats/images tables); hash verify; metadata json sidecars | **two-phase scan→confirm flow + normalized stats schema** |
| 16 | Firetheft/ComfyUI_Civitai_Gallery | https://github.com/Firetheft/ComfyUI_Civitai_Gallery | 102 | 2026-02-10 | gallery+models browser node in ComfyUI | in-workflow browse UX |
| 17 | DekoMoon/civitdl | https://github.com/DekoMoon/civitdl | 72 | 2026-06-23 | CLI batch downloader on API v1 | arg parsing for batch ids |
| 18 | Confuzu/CivitAI-Model-grabber | https://github.com/Confuzu/CivitAI-Model-grabber | 64 | 2026-08-31 | bulk model downloader by type (LORA/Checkpoint/Embeddings…), per-user, org by baseModel/version, details.txt + triggerWords.txt sidecars | **per-candidate dossier format (stats+urls+trigger words+preview)** |
| 19 | jmsltnv/civitai-data-manager | https://github.com/jmsltnv/civitai-data-manager | 60 | 2025-07-30 | metadata backup/organizer for local safetensors; generates **static HTML browse pages**; no api key needed | **metadata→static-HTML pipeline = closest to our deliverable** |
| 20 | DemonGatanjieu/Anomalous_Model_Browser | https://github.com/DemonGatanjieu/Anomalous_Model_Browser | 59 | 2026-08-27 | comfy workspace/model manager, zero-dependency civitai scraping | dependency-free fetch patterns |
| 21 | hassan-sd/civitai-image-scraper DEAD | https://github.com/hassan-sd/civitai-image-scraper | 57 | 2023-08-22 | bulk image dl filtered by reaction count | reaction-threshold filter idea |
| 22 | airborne-commando/civitai-mirror-list | https://github.com/airborne-commando/civitai-mirror-list | 57 | 2026-01-27 | takedown-watch list + archive tools (where removed models live) | anti-takedown fallback map |
| 23 | kianxyzw/comfyui-model-linker | https://github.com/kianxyzw/comfyui-model-linker | 66 | 2026-08-15 | relink missing workflow models, fuzzy match, dl from HF/Civitai | workflow→resource resolution |
| 24 | rajeevbarde/SDLora-Organizer | https://github.com/rajeevbarde/SDLora-Organizer | 47 | 2026-07-31 | LoRA organizer on a **pre-scraped civitai database**, browse offline | pre-scraped-sqlite-as-source pattern |
| 25 | mogurt/ComfyDownloader | https://github.com/mogurt/ComfyDownloader | 35 | 2026-04-23 | cross-platform desktop downloader/organizer | desktop UX reference |
| 26 | craftgear/civitai_prompt_scraper | https://github.com/craftgear/civitai_prompt_scraper | 22 | 2025-06-25 | downloads images + metadata together | paired (image, meta) fetch pattern |
| 27 | VeyDlin/Civitai2notion | https://github.com/VeyDlin/Civitai2notion | 22 | 2025-07-26 | sync civitai **bookmarks** → Notion, then auto-download curated set | **curation-queue pattern: bookmarks = manual curation layer** |
| 28 | timoncool/civitai-mcp-ultimate | https://github.com/timoncool/civitai-mcp-ultimate | 21 | 2026-08-31 | MCP server: 14 tools "covering 100% of REST v1", params verified 2026-03-24, NSFW w/ key, trend analysis, image cache | **freshest verified api-client param handling; Meilisearch-first claim to test** |
| 29 | moonwhaler/CivitScraper | https://github.com/moonwhaler/CivitScraper | 19 | 2026-08-20 | scan local models → fetch info/previews → generate HTML gallery per collection | alt static-HTML generator, active |
| 30 | rbbrdckybk/civitai-companion | https://github.com/rbbrdckybk/civitai-companion | 11 | 2025-10-26 | extract prompt metadata from civitai images, auto-dl resources used, template output | meta.workflow/resources → modelVersionId resolution |
| 31 | yokonsan/civitai-analysis DEAD | https://github.com/yokonsan/civitai-analysis | 13 | 2023-04-13 | SFW image data analysis | stat-analysis precedent |

Runners-up (fetched, not tabled): kale5195/chilloutai (806★, 2023, image-gen site, DEAD,
tangential); Vetchems/sd-civitai-browser (176★, 2023-12, DEAD, predecessor of #4);
etherealxx/batchlinks-webui (186★, 2023-12, DEAD, HF/MEGA/CivitAI batch dl);
ShinChven/comfydl (11★, 2026-01, comfy CLI dl); Cicatriiz/civitai-mcp-server (12★,
2025-07, MCP browse); jakepurple13/civitaimodelbrowser (12★, 2026-05, favorites/lists
UI); rioX432/CivitDeck (12★, 2026-07, mobile client KMP); AsuraAce/ambit (43★,
2026-09-01, desktop image library).

Deduped from 4 GitHub Search API queries (q=civitai; topic:civitai; civitai scraper;
civitai downloader in:name), fetched 2026-09-01. Official repos (civitai/*) included
even though they're platform, not mining tools — #1 and #11 are directly reusable.

---

## 3. Verdict — top 5 to adapt for the curation garimpo tool

Context: static GH-Pages library site; garimpo script pulls candidate LoRAs/workflows +
community stats for MANUAL curation; owner supplies api key.

1. **jmsltnv/civitai-data-manager** (60★) — already does the exact output shape we need:
   civitai metadata in → static HTML browse pages out, no api key required. Rework its
   input from "local safetensors dir" to "API search results" and the curation-site
   skeleton exists.
2. **dreamfast/go-civitai-downloader** (109★, very active) — the garimpo flow itself:
   criteria scan → summary → human confirmation → fetch, with normalized sqlite
   (models/files/stats/images) and hash verification. Steal the schema + two-phase flow.
3. **Confuzu/CivitAI_Image_grabber** (116★) — most battle-tested python API walker in
   the census: user/model/tag/versionId filters, cursor pagination, sqlite download
   tracking, concurrency, resume. The harvester skeleton.
4. **Confuzu/CivitAI-Model-grabber** (64★, active) — produces per-candidate dossiers
   (details.txt with urls + trigger words, preview images, per-version layout): the
   "candidate card" format a manual curation pass wants, minus the file download.
5. **timoncool/civitai-mcp-ultimate** (21★, active, params re-verified 2026-03-24) —
   freshest full-v1 api client surface (all params incl. NSFW-with-key, browsingLevel,
   trend analysis); use as reference implementation for param handling, and its
   "REST search broken since May 2025" claim is the first thing our garimpo must
   stress-test (query vs cursor walk).

Second wave (steal patterns, not code): VeyDlin/Civitai2notion (bookmarks-as-curation-queue),
rajeevbarde/SDLora-Organizer (pre-scraped sqlite as offline source), civitai/civitai
(ground-truth response shapes when docs go quiet).

---

## OPEN items (explicit)
- Full `sort` enum on GET /models beyond Highest Rated/Most Downloaded/Newest — docs say
  "see source" (https://developer.civitai.com/site/reference/models). Pull from
  civitai/civitai repo or GET /enums when needed.
- Numeric value of anonymous "public browsing level" for /images — undocumented; probe.
- Whether `?query=` (Meilisearch) is reliably working — docs describe it; mcp-ultimate
  claims breakage since May 2025; we must probe before relying.
- Image CDN transforms other than `width=450` (format/quality/height) — only width
  verified live.
- Download endpoint niceties (Content-Disposition filename, resume/Range support) —
  not documented, not probed. Baseline: Bearer or `?token=` per model-versions/mini.
- Articles/Vault/Permissions endpoint param detail — listed in reference overview but
  pages not fetched (out of garimpo scope).
