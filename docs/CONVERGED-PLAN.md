# CONVERGED PLAN — v1.1 (post hostile R2: 14 findings fixed; receipts research/hostile-plan-review-R2.md)

## product
name: "The Civitai Field Guide" (short: fieldguide). one-line: the curated shortlist of civitai LoRAs + workflows for AI personas, ad pipelines, and adult content — our names, our tiers, importable in one move.
audience: kenji (comfyui newbie), marcus (ad guy), lia (OF creator), owner.

## design direction (ratified)
codex Direction B "Field Guide" editorial gallery — tokens/typography/color read from research/codex-design-ideas.md §Direction B at build time (binding source, builder does not invent). Direction A's technical proof rail on detail pages. (R2#11 fixed: no "dark default" claim — §B is the palette, whatever it is.)

## content-class model (R2#1+#2 fixed — nsfwLevel gate, not lane gate)
- every entry carries nsfwLevel (API field, already pulled). gate: nsfwLevel >= 8 => preview blurred until header toggle, ON ANY LANE; toggle unblurs globally (session + 30d opt-in).
- mature LANE (curated adult) data lives in separate shipped files: mature-entries.json + mature-search-index.json, fetched ONLY after toggle. SFW pages (home/personas/ads/models) ship ZERO references to mature-lane data — no ids, names, urls in html OR json (R2#2 branch 3).
- blurred-but-present: SFW lanes' nsfwLevel>=8 entries render preview via data-src swapped after toggle (never in initial DOM src), name/chips visible.
- build test (CI-able, extended per R2#2): grep ALL SFW-shipped artifacts (html + js + json) for mature-lane ids/names/urls => must be zero; nsfwLevel>=8 entries' image urls must appear only as data-src. test FAILS build.

## IA — 6 static surfaces (multi-page, shareable URLs, no JS routing)
1. home: 3 lane entries + search (intent chips, 3 example queries) + "start here" strip + fresh-and-proven row (sfw entries only)
2. lane pages ×3 (personas / ads / mature): tier-banded ranked grid, filter bar, live chip counts; mature page = skeleton + post-toggle data load
3. entry detail: gallery / verdict / proof rail / import block / verification badge / provenance line / stats-with-dates / license pills / handoff-next button / link out
4. models tab: per-task leaderboards from models.json (schema: task, rank, board+date, license, comfy support, vram badge, our verdict, CONTESTED marked); row action = civitai link + target folder hint; curation 30 × ~5min (R2#9)
5. guide page: first-60-seconds path (codex §4) + glossary
6. empty states: rescue logic (never a wall)
task axes (image / t2v / i2v-audio / voice / face-consistency) = output-task FILTER crossing lanes (REQUIREMENTS:38 resolved: group discoverable via filter + saved views v1.1; not a 4th silo — owner may promote on seeing it).

## card anatomy (order = reading order)
preview (3:4; blurred if nsfwLevel>=8) → tier badge + "#rank in lane" → our name → one-line purpose → type · base model · vram badge (est.) → stacks formula line ("Base + LoRA + upscale", idea 82) → stats trio (downloads · thumbs · comments) with pulled-date + trend arrow (only when deltas exist) → chips (locks / outputs) → requirements count badge on workflows ("2 models · 3 nodes" — or "requirements being verified", never invisible).

## filter bar
exactly 4 visible: VRAM (first, labeled "est." — R2#10) / base model / output-task / freshness + sort toggle Proven/Latest (idea 86). "+more": type, inputs, locks, duration (video contexts), audio-req (ads lane). live yield counts on every chip (N1), one shared predicate. zero-yield chips disabled. one vocabulary const (gpu, outputs, locks, audio, intents). build coverage report per curation-tax field (guard restored, R2#10).

## ranking display (criteria v2 binding)
tier-first: [S · #2 in Personas] primary; composite/10 secondary; trend when deltas exist. per-lane rank bands + floors + kill-line caps. hysteresis: tier changes need band-floor crossing by ±5 in 2 consecutive pulls; anchors frozen until 4th pull (R2#8). small lanes: S = max(1, round(0.10n)) for n>=5, else single best; filtered views label "in view" rank, never fake lane rank.

## import (the moat — ideas 76/77/78/79/101/102 fixed per R2#5)
detail: "What you need" panel ABOVE button (models w/ folder paths + civitai links + login notes; nodes w/ exact Manager search strings + node-note annotations, idea 101) — uncurated state = visible "requirements being verified", panel NEVER silently collapsed. primary action: coral "Download ComfyUI JSON" (our-slug--version, ENRICHED with our node notes). how-to one-sentence. PNG alternative ONLY when verification.tested_by_us: our proof image with OUR pinned workflow embedded (idea 102 honest — never community previews; absent otherwise). pinned exact version (79) + build-time newer-version badge check.

## verification + provenance (R2#4 — adopted ideas get schema homes)
curated.json gains: verification{tested_by_us, date, proof_images[]}, provenance{creator, version_id, checked_at}, license_pills[], status{removed, needs_retest, changelog[]}, preview_mismatch_badge (idea 88), handoff_next{lane, entry} (idea 84). detail renders: tested-by-us badge (90), provenance line w/ checked date (92), license pills pre-import (93), removed-gray / needs-retest states (95/96), changelog (97).

## search
build-time synonym index (interpretation chip ALWAYS shown on expansion). intent chips ×4 (shared const). alias search (creator + original name, both shown). scope: lane / all-sfw / saved (mature scope only when toggled). recent searches local-only + mature-history guard. empty = 3 build-verified examples + computed rescue (relax most restrictive filter, nearest concept). search-index split SFW/mature per content-class model.

## nsfw (owner decision 2026-09-01 binding: ALLOW)
header toggle + confirm once per session (30d opt-in). blur until toggled (per-entry nsfwLevel gate, any lane), full previews after. mature lane = separate route + post-toggle data load + full filter parity + per-lane normalization. CI grep test as specced in content-class model.

## micro-interactions v1 (capped 8; JS budget 1200 lines, R2#14 — degradation order: thumb-scrub dies first, then sticky band headers, then toast; lightbox/filters/search never)
tier badge hover-explains · chip count number-swap · lightbox arrows/keys/swipe + preload-next-2 · blur reveal on toggle · download button press state · toast on copy · band header fade-in · gallery thumb-scrub (desktop, v1.1 until gallery data verified). prefers-reduced-motion honored.

## data + build
sitegen (python): garimpo candidates (v0.2: gallery[] up to 6 meta-prefered images per entry + FULL usage walk + weekly sig-recheck across snapshots) + curated.json → static html + entries-sfw.json + mature-entries.json + search-index-sfw.json + search-index-mature.json + synonym table + workflows/<slug>.json + models.json. tier/composite computed per criteria v2. CDN resilience: width-450 thumbs cached locally at build when license allows (flag per entry; owner override extends to caching); hotlink default, cache fallback (R2#13). vanilla JS runtime ≤1200 lines, no framework, no server, no runtime key.

## curation effort (R2#6 honest)
personas/nsfw: 10-15min/entry (name/purpose/locks/badge/verdict). workflows: 30-60min/entry (requirements manifest + node notes + test run when GPU available). P2 gate: workflows lane 100% curated, personas/nsfw >= 60%, models.json 100%. test runs can lag — verification badge only on tested; completeness axis accepts confirmed-recipe (criteria v2).

## phase map (R2#4 re-arithmetic'd; tallies from analyst rollups)
- v1 core: 1-25 (21 adopt + 4 merge + 2 new), 26-50 (all adopt + N1 live counts; 43 palette v1.1, 50 surprise v1.1), 51-75 (onboarding 61-64, detail 66-75 core; compare cluster 51-60 WHOLE → v1.1 incl. 51+60, single-rig family 33+59+61/64 merged), 76-82 import+resilience spine WHOLE (incl. 80 recovery, 81 storyboard, 82 stacks on card), 83-100: 83 roles, 84 handoff, 86 proven/latest, 88 mismatch badge, 90 tested badge, 91 versioned manifests + build-fail schema validation, 92 provenance, 93 license pills, 94 scan-status, 95/96/97 staleness family — ALL v1 (schema homes above); DEFER: 87 (measurement), 99 (QR), 43, 50, N2 v1.1
- v1.1: palette 43, surprise 50, compare rows 51-60, named views N2, thumb-scrub
- kills: 0 (analyst consensus; merges absorbed)

## open items
- curation per-entry manager review (my pass over the 3 drafts — next)
- models.json manual fill (30 × 5min)
- first diverse pull (Newest sort) to stress anchors — hysteresis active from pull 4
