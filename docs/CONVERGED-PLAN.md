# CONVERGED PLAN — v1 site (manager's converge of: 104 analyzed ideas, ux-census, codex design, criteria v2, requirements, legal+owner decisions)

## product
name: "The Civitai Field Guide" (short: fieldguide). one-line: the curated shortlist of civitai LoRAs + workflows for AI personas, ad pipelines, and adult content — our names, our tiers, importable in one move.
audience: kenji (comfyui newbie), marcus (ad guy), lia (OF creator), owner.

## design direction (ratified)
codex Direction B "Field Guide" editorial gallery — tokens/typography read from research/codex-design-ideas.md §Direction B at build time (binding source, builder does not invent). Direction A's technical proof rail grafted onto detail pages. Dark default, calm, judgment-first: the site's advantage is TASTE, not inventory.

## IA — 6 static surfaces (multi-page, shareable URLs, no JS routing)
1. home: 3 lane entries + search (intent chips, 3 example queries) + "start here" strip + fresh-and-proven row
2. lane pages ×3 (personas / ads / mature): tier-banded ranked grid, filter bar, live chip counts
3. entry detail: gallery / verdict / proof rail / import block / stats-with-dates / link out
4. models tab: per-task leaderboards (benchmarks census + our verdict lines, CONTESTED marked)
5. guide page: first-60-seconds newcomer path (codex §4) + glossary (LoRA vs checkpoint vs workflow in child words)
6. 404/search-empty: never a wall — rescue logic
task axes (image / t2v / i2v-audio / voice / face-consistency) live as FILTERS crossing lanes — resolves REQUIREMENTS:38 (i2v not a 4th silo)

## card anatomy (order = reading order, top to bottom)
preview (3:4) → tier badge + "#rank in lane" → our name → one-line purpose → type · base model · vram badge → stats trio (downloads · thumbs · comments) with pulled-date + trend arrow → chips (locks / outputs). Requirements count badge on workflow cards ("2 models · 3 nodes").

## filter bar
exactly 4 visible: VRAM (first — impossibility filter) / base model / output-task / freshness. "+more" (type, inputs, locks, duration in video contexts, audio-req in ads lane). EVERY chip carries live yield count (N1) — one shared predicate drives grid + counts + rescue. Zero-yield chips disabled. One vocabulary const at build for: gpu labels, outputs, locks, audio, intents (ideas 26/33/36/39/41/42 share it).

## ranking display (criteria v2 binding)
tier-first: [S · #2 in Personas] primary; composite/10 secondary; trend arrow only when deltas exist. tier bands = per-lane rank bands + absolute floors (S>=70+gate, A>=55, B>=35) + kill-line caps. grid sorted composite-desc within band, band headers sticky.

## import (the moat — ideas 76/77/78/79)
detail page: "What you need" panel ABOVE the button — per model: our name, civitai name, size, exact target folder (models/loras/...), link new-tab, login-required note; per node: display name + exact ComfyUI Manager search string + git fallback. Primary action: coral "Download ComfyUI JSON" (filename = our-slug--version). One-sentence how-to: "Download JSON → drag onto ComfyUI (or Workflows > Open)". Alternative path: preview PNG with embedded workflow meta → drag PNG onto canvas. Pinned exact model version used in our test (79).

## search
build-time synonym index (user phrasing → our vocabulary; interpretation chip ALWAYS shown when expansion fires). intent chips ×4 under box (new persona / product ad / talking video / voice) — same const as output filters. alias search: creator username + original civitai name, both names shown on hit. scope: lane / all / saved. recent searches local-only, mature-history guard (never rendered in SFW state). empty = 3 build-verified examples + computed rescue ("nothing at 6 GB — 5 at 8 GB, show them?").

## nsfw (owner decision 2026-09-01 binding: ALLOW)
header toggle + confirm once per session (30d opt-in remember). blur until toggled, full previews after. separate route (/mature/). full filter parity inside lane. per-lane normalization (criteria v2). build test: zero mature names/images/urls in SFW-state DOM (grep test in build, CI-able).

## micro-interactions v1 (capped at 8)
tier badge hover-explains · chip count number-swap · lightbox arrows/keys/swipe + preload-next-2 · blur reveal on toggle · download button press state · toast on copy · band header fade-in · gallery thumb-scrub on card hover (desktop only, preload on hover only). prefers-reduced-motion honored everywhere.

## data + build
sitegen (python): garimpo candidates + curated.json → static html + entries.json + search-index.json + synonym table. curated.json fields: our_name, purpose, verdict_line, axes scores, curated_by/at, confidence, locks[], inputs[], outputs[], audio[], duration, vram_badge, requirements{models[],nodes[]}, aliases, lane. tier/composite COMPUTED by sitegen from criteria v2 formulas (anchors per pull in build stats). vanilla JS runtime (~<500 lines total), no framework, no server, no runtime key.

## phase map — all 104 verdicts land somewhere (nothing adopted silently drops)
v1 core: 1-30 (IA/cards/ranks core: 23 adopt, 3 merges), 31-42 (filters/search core), 43 DEFER v1.1, 44-50 (search tail + surprise-me 50→v1.1), 51-75: onboarding 61-64 + detail 66-73 core; compare-rows family (52-59, 6×adopt-10) → v1.1 (single-rig profile + compare need real entries first; honest over stubbed), 74-75 core, 76-79 import spine v1 (80-82: resilience checks v1), 83-100: detail/workflow-presentation core subset — full sweep at build; DEFERs respected (43, palette; 2 idea-76-100 DEFERs logged in file)
v1.1: command palette 43, named views N2 + "+N new", surprise-me 50, compare rows 52-59 family, rig profile (33+61/64 merge)
kill: none (0 KILLs across 104 — analyst consensus: the 100 list was strong; the kills happened at MERGE level)

## open items (named, not hidden)
- design tokens: extracted from codex §B at build start (typography/color exact hex)
- models leaderboard data shape: from model-benchmarks.md tables + manual verdict lines (curation pass)
- curation pass = the next real work: 100 entries × (name/purpose/locks/requirements/verdict) at ~10min each ≈ 2 focused sessions or delegated waves with my per-entry review
