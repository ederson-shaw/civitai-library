# UX census: dense visual asset catalogs (live-fetched 2026-09-01)
For: curated civitai workflow/LoRA library (static GH pages, vanilla JS). 4 sites.

## 1. OpenArt — https://openart.ai/workflows (redirects to studio home /suite/home)
- Pivot: old public workflow gallery is GONE; now a closed "AI Creator Studio". Templates live as curated shelves.
- Card anatomy: image thumb (cdn webp) + name + category label + "New" badge + one-line pitch. ZERO stats (no counts, no author).
- Filter system: none on gallery surface — pure editorial shelves: "Direct Your Video" (category cards: Short Film, Product Ads, UGC Ads...), "Viral Seedance Presets" (/suite/home/feed/viral-templates), "Latest models".
- Categories are USE-CASE verbs ("Product Ads", "Social Content"), never model names.
- Preview nav: carousel + "View all / More →". No lightbox on this surface.
- Ranking/tier: shelves ARE the tier — "Viral" (popularity) vs "Latest" (recency). No numbers shown.
- Import UX: every card = "Create Now / Try Now" CTA running preset inside their studio. NO json download, no export. Lock-in.
- NSFW gating: none visible on this surface.
- COPY: use-case-named categories; viral/latest dual shelves; one-line pitch per card; explicit verb CTA per card.
- AVOID: zero-export lock-in; stats-less cards (no trust signal); no filters beyond shelf click.

## 2. Comfy official — https://comfy.org/workflows/ (626+ templates)
- Card anatomy: title follows "MODEL: TASK" convention ("Wan3.0: Reference to Video"); author avatar+name; 1-3 tag CHIPS per card (Image to Video, Video, Partner Nodes); hero carousel cards get model logo + "FEATURED · STAFF PICK" badge. No numeric stats.
- Killer detail: upscale/restore cards (Topaz) show BEFORE/AFTER thumbnails IN the card — proof-of-result without clicking.
- Filter system: segmented ALL / Node Graphs / Comfy Apps + "Filter: Most Popular" dropdown + every chip is a navigable tag page (/workflows/tag/image-to-video/). Tag pages = SEO landing.
- Preview nav: hero carousel up top; grid below; "Load more" (30 of 626 shown).
- Ranking/tier: two explicit tiers — editorial (FEATURED · STAFF PICK carousel) vs popularity (Most Popular filter). Clean separation.
- Import UX: per-card "Try now" (cloud run) + templates auto-check missing models/deps on open in desktop. Dependency awareness at import time.
- Naming: cards named by MODEL first — the opposite of OpenArt (use-case first).
- NSFW gating: none visible.
- COPY: chips-as-links to tag pages; before/after thumbs in card; "MODEL: TASK" title convention; featured-tier carousel above grid; dep-check promise at import.
- AVOID: model-first naming (use-case-first scans better for curators); no per-card difficulty/inputs listed.

## 3. Civitai — https://civitai.com/models (SPA shell via webfetch; data layer via live API /api/v1/models)
- UI shell (SSR-rendered only): nav verticals models/images/videos/3d-models/hubs/articles/comics; browse modes are QUERY-PARAM SORTS rendered server-side — "Highest Rated" (default) / "Most Downloaded" — shareable URL state. Grid is client-rendered; blur/toggle NOT evidenced in fetch (verify by hand once).
- Card/data anatomy (API): type enum (Checkpoint/...), name, creator.username, tags[] free-text ("photorealistic","base model"), license flags (allowCommercialUse/allowDerivatives/allowNoCredit), baseModels[].
- STATS per model: downloadCount, thumbsUpCount, thumbsDownCount, commentCount, tippedAmountCount (money tipped = quality proxy no other site has).
- Version-aware: each modelVersion has baseModel ("SD 1.5 Hyper"), trainedWords[] (prompt tokens that activate the LoRA!), files[].downloadUrl, publishedAt, own stats, paidAccess/earlyAccess gates.
- Preview: images[] per version each with nsfwLevel (numeric 1..N), type, hasMeta (image carries embedded generation metadata — previews can be dragged into ComfyUI to load the workflow).
- NSFW model: numeric levels per image AND per version + top-level nsfw bool + sfwOnly/poi/minor flags. Gating is data-first, UI second.
- Ranking/tier: sort modes (Highest Rated = weighted, Most Downloaded) + tippedAmount as community-vote signal.
- Import UX: direct downloadUrl per version file; hasMeta previews double as workflow import.
- COPY: stats trio on card (downloads/thumbs/comments); trainedWords visible on LoRA cards ("say this to activate"); version picker with baseModel compat chips; license chips; numeric NSFW levels; sort-as-URL.
- AVOID: free-text tag soup without hierarchy (facet pain); login-wall around real browsing.

## 4. RunComfy — https://www.runcomfy.com/comfyui-workflows (comfyworkflows.com returned HTTP 402 = dead for anon, replaced by this)
- Card anatomy: title + ONE-LINE OUTCOME PITCH ("FameGrid delivers polished fashion portraits fast — cinematic and color-rich") + preview. No stats, no author chip.
- Card actions: THREE verbs — Details / Run Workflow / Deploy as API (+Share). Deploy-as-API per card is unique among all four.
- Filter system: single horizontal chip row MIXING three taxonomies: models (Minimax H3, FLUX), tasks (Generate videos, Restore & Upscale), creators (Alessandro Perilli...). Creators = first-class filter.
- Headline feature: "Auto-Setup Agent — drop your workflow.json, we handle every dependency, custom node, and model. Save 4 hours!"
- Preview nav: grid + Load more; detail pages at SEO slugs (/comfyui-workflows/krea-2-famegrid-spice-...).
- Ranking/tier: "New" chip + "Curated, Runnable Guaranteed" trust line. No public numbers.
- Import UX: everything runs INTO their paid cloud; no json download visible.
- NSFW gating: none visible.
- COPY: outcome-pitch one-liner on every card; Run/API/Share verb triple; "curated + guaranteed runnable" trust copy; creator chips.
- AVOID: one chip row mixing 3 taxonomies (scan cost); zero export (lock-in); SEO-stuffed card titles.

## Convergence — 10 IA recommendations (personas / ad pipelines / nsfw-gated, static GH pages vanilla JS)
1. Lane + card categories named as USE-CASE VERBS ("Character personas","Product ad","UGC"), never model names — [OpenArt].
2. Card title = "MODEL: TASK" + mandatory one-line OUTCOME pitch ("turns 1 ref into consistent character sheet") — [comfy.org + RunComfy].
3. 1-3 tag chips per card, every chip a link to a filtered static page (tag pages double as SEO surface) — [comfy.org].
4. Two ranking tiers kept separate: curated "picks" carousel above grid, community sort (Most Downloaded / Highest Rated) below — [comfy.org + civitai].
5. Show stats on card: downloadCount + thumbsUpCount (+ "works for me" counter if ever dynamic) — [civitai].
6. Enhancement-type cards get BEFORE/AFTER dual thumbnails in-card, no click needed — [comfy.org Topaz].
7. Every card carries a REQUIREMENTS line: base models + custom nodes + VRAM class, stated before download (dep-promise) — [comfy.org templates + RunComfy auto-setup].
8. Import = first-class "Download .json" button + workflow-PNG variant with embedded metadata (drag into ComfyUI loads it) — zero lock-in, the anti-RunComfy/OpenArt — [civitai hasMeta + comfy.org drag-PNG].
9. NSFW lane on its own route: per-asset numeric nsfwLevel, blur default + session toggle in localStorage, license + poi flags on card — [civitai].
10. Filter rows = ONE taxonomy each (tasks row / base-model row / tag row); active filter state lives in URL params so views are shareable — [RunComfy mixed row = the avoid; civitai sort-as-URL = the copy].

Fetch log (2026-09-01): openart.ai/workflows (redirect→studio), comfy.org/workflows/, civitai.com/models?sort=Most+Downloaded + civitai.com/api/v1/models (live JSON), runcomfy.com/comfyui-workflows. comfyworkflows.com rejected: HTTP 402. civitai.com/content/safety = SPA shell, no gating text.
