# UX census: dense visual asset catalogs (live-fetched 2026-09-01)
For: curated civitai workflow/LoRA library (static GH pages, vanilla JS). 4 sites.

## Convergence — 10 IA recommendations (personas / ad pipelines / nsfw-gated, static GH pages vanilla JS)
1. Lane + card categories named as USE-CASE VERBS ("Character personas","Product ad","UGC"), never model names — [OpenArt].
2. Card title = "MODEL: TASK" + mandatory one-line OUTCOME pitch ("turns 1 ref into consistent character sheet") — [comfy.org + RunComfy].
3. 1-3 tag chips per card, every chip a link to a filtered static page (tag pages double as SEO surface) — [comfy.org].
4. Two ranking tiers kept separate: curated "picks" carousel above grid, community sort (Most Downloaded / Highest Rated) below — [comfy.org + civitai].
5. Show stats on card: downloadCount + thumbsUpCount (and tippedAmount-style "works for me" counter if ever dynamic) — [civitai].
6. Enhancement-type cards get BEFORE/AFTER dual thumbnails in-card, no click needed — [comfy.org Topaz].
7. Every card carries a REQUIREMENTS line: base models + custom nodes + VRAM class, stated before download (dep-promise) — [comfy.org templates + RunComfy auto-setup pitch].
8. Import = first-class "Download .json" button + workflow-PNG variant with embedded metadata (drag into ComfyUI loads it) — zero lock-in, the anti-RunComfy/OpenArt — [civitai hasMeta + comfy.org drag-PNG].
9. NSFW lane on its own route: per-asset numeric nsfwLevel, blur default + session toggle persisted in localStorage, license + poi flags on card — [civitai].
10. Filter rows = ONE taxonomy each (tasks row / base-model row / tag row); active filter state lives in URL params so views are shareable — [RunComfy's mixed row = the avoid; civitai sort-as-URL = the copy].

Census fetch log: openart.ai/workflows (redirect->studio), comfy.org/workflows/, civitai.com/models?sort=Most+Downloaded + api/v1/models, runcomfy.com/comfyui-workflows. comfyworkflows.com rejected (HTTP 402). All 2026-09-01.
