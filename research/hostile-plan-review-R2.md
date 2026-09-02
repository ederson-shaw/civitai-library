# HOSTILE PLAN REVIEW — R2 (2026-09-01)

Reviewer: zero-loyalty hostile agent. R1 read first; every finding below is NEW (R1 overlaps named and excluded explicitly). Every data claim verified by running python over `data/candidates-*.json` (output pasted in-line where cited). Line numbers = current files on disk.

---

## FINDINGS (worst first)

### 1. [NSFW/DATA/LEGAL] CONVERGED-PLAN.md:20,35 (whole plan) — the plan is nsfwLevel-blind: the "SFW" lanes carry explicit-level previews, and the plan's gating keys on LANE, not content level

R1 #1 was DREAM-vs-legal doc contradiction. This is different and worse: the DATA now proves the lane model itself leaks. Verified by execution:

```
persona n=40:   entries nsfwLevel>=10: 31  (max 31 — 'One obsession', 'Babes', 'MiaoMiao Harem', 'RedCraft')
workflows n=30: entries nsfwLevel>=10: 16  (max 31 — 'ComfyUI Image Workflows', 'Smooth Workflow (txt2img)')
nsfw n=30:      entries nsfwLevel>=10: 26  (max 60)
all lanes: entries with >2 preview urls: 0  (every entry ships exactly ONE preview image, 2 sizes of it)
```

31 of 40 persona entries — the lane behind the default SFW route — sit at civitai explicit levels, every one with a `preview.url_width450` that card anatomy (CONVERGED-PLAN.md:20, "preview (3:4)" first element) bakes into the personas page. The plan never mentions `nsfwLevel` (grep over the file: zero hits). Blur, toggle, and the build test (CONVERGED-PLAN.md:35) all key on lane-C membership ("mature"), so the grep test PASSES while explicit imagery hotlinks on `/personas/` with no toggle — violating REQUIREMENTS.md:12 ("header NSFW switch, sfw default"), the legal record (legal-pages-policy.md:10, "NO explicit imagery loaded, hotlinked or cached"), and the plan's own test intent. Second-order kill: CRITERIA.md:12's parity fix ("tiers per-lane, composites never compare across lanes") assumes lane = content class; persona lane is majority-explicit, so gated-nsfw entries compete inside lane A on civitai's clamped stats — the exact disease parity was designed to kill, now inside a "SFW" lane. The CRITERIA.md:61 worked example is literally an nsfwLevel-31 entry in the persona lane.

**Cost if unfixed:** explicit images render on the SFW github-pages routes at first paint; the R1#1 takedown scenario returns through the data instead of the doc; owner's "sfw default" promise false on lane A's first screen.
**Fix:** per-entry nsfwLevel gate in sitegen: preview selection filtered by level threshold on ALL lanes (SFW routes draw from level≤X previews only, else placeholder+link-out); lane-C blur rules re-keyed on nsfwLevel, not lane; build test extended to assert zero nsfwLevel≥threshold preview URLs on any SFW route; curation step either re-lanes the explicit persona entries or the plan admits lane A is a mixed lane and gates it.

### 2. [NSFW/PIPELINE] CONVERGED-PLAN.md:32,35,41 — the mature preview pipeline has no consistent branch: every implementable option violates one of the plan's own specs, and the grep test scopes itself away from the leak

The plan mandates simultaneously: (a) "blur until toggled, full previews after" (:35); (b) search scope "all" with a "mature-history guard" (:32) — implying mature entries are in the client-side search corpus; (c) one `entries.json` (:41) emitted by sitegen; (d) build test "zero mature names/images/urls in SFW-state DOM" (:35). Three implementable branches, all defective:

- **img src in `/mature/*.html`, CSS blur:** explicit bytes load from civitai CDN on page load, pre-toggle, on github pages — legal record bans it (legal-pages-policy.md:10); owner override (OPEN.md:6) accepts hosting risk, but then "blur until toggled" is a false statement about what loads.
- **URLs injected post-toggle from entries.json/search-index.json:** mature names + URLs + aliases (original civitai names of explicit models, frequently explicit strings) ship in static JSON to every SFW visitor. The grep test scopes "SFW-state DOM" — JSON files are not DOM; the test passes while the leak ships. Search scope "all" (:32) makes the mature index load unavoidable for the search box to work.
- **separate mature.json fetched only post-toggle:** fixes the leak — but breaks "scope: all" search in SFW state and is not what :41 (single entries.json) says.

The plan picks none. This is the exact mandate question ("which URLs get baked into HTML?") and the binding artifact has no answer.

**Cost if unfixed:** builder picks a branch at build time; two of three ship mature URLs/names to every visitor or hotlink explicit bytes pre-toggle; the CI-able test gives false green on all of them.
**Fix:** declare branch 3 in the plan: `mature.json` separate artifact, fetched only after toggle confirm; search index split SFW/full, scope "all" resolves client-side to whichever corpus is loaded; grep test extended from "SFW-state DOM" to "all shipped artifacts of the SFW build" (html + json).

### 3. [COVERAGE/DATA] REQUIREMENTS.md:11 vs CONVERGED-PLAN.md:13,20,38,41 — "navigate between examples" has NO data source: one preview image per entry, and the curated schema has no images field

Owner requirement verbatim: "lora/workflow RESULTS visible: preview images, navigate between examples." The plan specs: detail "gallery" (:13), "lightbox arrows/keys/swipe + preload-next-2" (:38), "gallery thumb-scrub on card hover" (:38). Verified data reality: all 100 entries carry exactly ONE preview image (`preview` = 2 URLs of the same image; `entries with >2 preview urls: 0` across all three lanes). `curated.json` fields (:41) list `our_name, purpose, verdict_line, axes scores, ..., requirements{models[],nodes[]}, aliases, lane` — **no images[] / gallery field exists anywhere in the plan's schema**. The `/images?modelVersionId=` walks in pull_log.json were pulled for usage counting; their images are not carried into any artifact the plan names. So the gallery is a surface with nothing to render, the lightbox has no next-2 to preload, and thumb-scrub has no thumbs.

**Cost if unfixed:** builder hits it at build time; ships single-image "gallery" — the owner's requirement reads unmet, arrows dead, scrub dead — or improvises a collector the plan never commissioned (scope creep under deadline).
**Fix:** add `images[]` (url, nsfwLevel, width/height, meta_match) to curated.json; garimpo v0.1's existing /images walk extended to persist top-N meta-matched images per shortlisted version; card preview picks the best level-safe image; gallery renders from the same field.

### 4. [COVERAGE/ARITHMETIC] CONVERGED-PLAN.md:44-46 — "83-100 core subset — full sweep at build" is a hole masquerading as a plan: ≥12 adopted ideas (scores 7-10) have no surface, no schema field, no phase — and the "all 104 land somewhere" arithmetic does not reconcile

Named adopted-but-unplaced (each ADOPT, each absent from every surface/card/detail/build spec in the plan; grep proof: zero hits for verification/provenance/changelog/editor/community/images in CONVERGED-PLAN.md):

- **90 tested-vs-linked badge (ADOPT 9, idea-analysis-76-100.md:126)** — "the product's trust moat made visible". CRITERIA v2 *depends* on it (community-linked entries can't render S — CRITERIA.md:25 curator-verified gate) yet no `verification` field exists in curated.json (:41) and no badge in card anatomy (:20).
- **91 per-entry versioned manifest + build-fail schema validation (ADOPT 9, :133)** — directly CONTRADICTED by :41's single `curated.json` with no schemaVersion, no per-entry files, no "build fails on violation" anywhere in the build section.
- **92 provenance line (ADOPT 9, :140)** — REQUIREMENTS.md:8 ("link back to civitai original on every entry") survives only as ":13 link out" with no creator/versionId/verified-date spec.
- **93 license pills above import (ADOPT 8, :151)** — the ads-lane personal-only landmine defusal; absent.
- **95 removed-source gray state, 96 needs-re-test badge, 97 changelog (ADOPT 8/7/6, :161-179)** — the whole staleness audit family; absent (":13 stats-with-dates" is not a state machine).
- **101 enriched JSON node-notes (ADOPT 9, :214)** — the range rollup names it part of the import spine (:229: "76 → 77 → 78 → 79 → 80 → 101 → 102 → 100"); the plan's import section (:29) omits it entirely.
- **84 lane handoff `Use this persona in Campaign Lab` (ADOPT 7, :82)** — the owner's persona→ads loop as a button; absent from all 6 surfaces.
- **86 Proven|Latest segmented sort (ADOPT 8, :97)** — only a freshness FILTER exists (:23); filtering ≠ sorting; REQUIREMENTS.md:41 "workflow age/recency visible" gets dates but the adopted dual-sort is gone.
- **88 preview-mismatch badge (ADOPT 7, :111)** — absent.
- **82 stack formula chips (ADOPT 8, :67)** — absent from card anatomy.
- **16 editor-vs-community split (ADOPT 10, idea-analysis-01-25 range table: "CRITERIA anti-farm thesis needs its visual face; blending banned")** — absent.
- **51 + 60** — compare cluster mapped as "52-59" (:44) but the analyst defines the cluster as 51-60, ONE module (idea-analysis-51-75.md:481: "table + row-set (52+53) → deltas (55) → tray (51) → diff toggle (58) → rig filter (59) → export (60)"); tray (51) and export (60) silently fall out of both v1 and v1.1.

Arithmetic: ":44 1-30 … 23 adopt, 3 merges" = 26 of 30, and analyst 1's own tally is "21 ADOPT, 4 MERGE, 1 scoped-adopt, +2 NEW" (≠23/3, ≠30) — four ideas unaccounted while the header claims "all 104 verdicts land somewhere (nothing adopted silently drops)" (:43). A coverage claim whose own numbers don't close is not coverage.

**Cost if unfixed:** "full sweep at build" delegates placement to the builder's discretion — the top-trust mechanics (90/91/92/93/95/96/97) are exactly the ones with no schema field, so they CAN'T ship even if wanted; the site launches without its trust spine and the phase map calls that compliance.
**Fix:** enumerate each of these into a surface + a curated.json field or an explicit v1.1 line, by idea number, in the plan; re-run the 1-30/26-50/51-75/76-100 tallies and make the four range counts sum to 104+news.

### 5. [IMPORT CORRUPTION] CONVERGED-PLAN.md:29 — the plan's PNG import path violates its own source idea: "preview PNG with embedded workflow meta" loads the COMMUNITY's workflow, not our pinned one

Idea 102's micro-criteria (idea-analysis-76-100.md:221): "bad = embedding into random preview images"; mechanism (:218): proof PNG must be OUR test output, tEXt chunk patched to the pinned/enriched workflow, build-verified against the JSON. The plan (:29) writes: "Alternative path: preview PNG with embedded workflow meta → drag PNG onto canvas." Civitai preview PNGs with meta (ux-census.md:33) embed whatever workflow the RANDOM community author used — possibly a different base model (idea 88's exact mismatch disease), unverified, unpinned. Importing it silently defeats 79's pinning in the same paragraph: user chooses the PNG path, gets an untested workflow wearing our site's endorsement.

**Cost if unfixed:** the one-gesture import path imports the wrong bytes; "tested by us" claim broken by the plan's own alternative button; bug reports land as "your workflow gave me a different face."
**Fix:** PNG path = our proof image only (102 as written), never civitai previews; civitai preview PNGs may link out with a "community workflow, unverified" label.

### 6. [FEASIBILITY/SEQUENCING] CONVERGED-PLAN.md:51 — curation estimate is 5-10x low and there is no ship-with-lag story: the moat is the first thing to silently vanish

":51 100 entries × (name/purpose/locks/requirements/verdict) at ~10min each ≈ 2 focused sessions." What the 10 minutes must actually cover, per the plan's own adoptions: requirements panel per workflow (idea 78, :30 — "~10 min each" ALONE, "THE moat-cost"); storyboard stages (81); dependency graphs ~15min each (89, :118); audio role tags (83); persona→pipeline cross-refs (84); synonym authoring (:32); vram badges (manual, CRITERIA.md:59); models-tab verdict lines (:50 — a separate curation pass, outside the 100×10min entirely); and idea 90/102's hand-test RUNS — GPU executions with proof outputs per entry, the thing "tested by us" and the completeness axis (CRITERIA.md:8 "ran-it OR confirmed-recipe") literally require. Realistic 30-60+ min/entry; test runs make it worse. Sequencing: no gate anywhere says detail pages need requirements before publish, and 78's own spec ("Panel collapses only when count = 0", :26) means an uncurated workflow ships with the moat collapsed — indistinguishable from a model with no dependencies. The plan defines no empty/partial state for the import block.

**Cost if unfixed:** v1 ships on schedule with empty panels — "just another list," the exact product-identity failure Direction B exists to prevent — and nobody defined what the user sees in the meantime.
**Fix:** split curation M1 (name/purpose/lane/tier — card-ready) from M2 (requirements/proof/storyboard — detail-ready); detail publish gated on M2 or renders an explicit "requirements not yet verified by us" state (never silent collapse); recount the estimate per-activity with the idea files' own cost lines.

### 7. [CRITERIA] CRITERIA.md:9,22 + data — "not walked" is scored as "zero": 75% of every lane is structurally capped at 75/100, so launch tiers rank WALK STATUS, not quality

Verified: usage data exists for exactly 10/40 persona, 10/30 workflows, 10/30 nsfw (the calibration sample — `entries with usage data: 10/40, 10/30, 10/30`). CRITERIA v2 scores usage bands "0 → 0" (:22) and honesty "not-walked = 0" (:9) — conflating "not measured" with "measured zero". 30 of 40 persona entries lose 25 points for a data-collection gap they cannot influence; S floor 70 vs cap 75 means S is realistically reachable only by walked entries; rank bands (top 10%) then select among the walked cohort. Nothing in CRITERIA or the plan requires garimpo v0.1 to walk the FULL shortlist (OPEN.md:4 says only "usage/honesty collector" in flight — scope unstated).

**Cost if unfixed:** the site's first-paint tier display is an artifact of which 10 entries a script sampled; a better unwalked entry sits under a worse walked one with a confident badge on it; the exact "looks broken / criteria garbage" reception v2's external-gate rescue (:6) was written to prevent.
**Fix:** either (a) commit: walk coverage = 100% of shortlist before any scoring, garimpo fails loud on partial coverage; or (b) composite normalizes over available axes with a visible "partially measured" state — never score absence as zero. Pick one, write it in CRITERIA.

### 8. [CRITERIA] CRITERIA.md:4,36-39 + criteria-calibration.md:22 — anchors recompute every pull with no stability mechanism: published tiers churn on the first diverse pull; tiny-lane bands and filtered-view ranks undefined

Calibration's own caveat (:22): current anchors come from a Highest-Rated-sorted pull and "skew high; first Newest-sorted pull will stretch the low end." Mechanics of the churn: anchors are per-lane percentiles recomputed every pull (CRITERIA.md:4,55); a diverse pull LOWERS p75_ratio → `ratio/p75` rises for every existing entry → composites move for entries whose real-world stats did not change a single download → rank-band membership (top 10/25/40%, :36-38) flips → published S/A badges swap between visits. The file's answer is "Re-anchor check scheduled at first diverse pull" (calibration:22) — a check, not a mechanism: no anchor freeze, no hysteresis, no minimum dwell before demotion. Second hole in the same block: ":36 min 5 entries in lane, else single best only" defines only the S band of a tiny lane — A "next 25%" and B "next 40%" of a 5-10 entry lane have no rounding rule at all (top 10% of 8 = 0.8 → 1? floor? ceil?). Third: tiers are baked per-lane at build, but the filter bar crosses lanes — a filtered view showing 6 cards will display "#17 in Personas" on the top row; rank display vs visible order disagree with no stated rule.

**Cost if unfixed:** tier oscillation between weekly rank-keeper runs — the "rankings stay honest" promise reads as randomness; tier disputes (the thing :42 claims are "mechanically resolvable") resolve differently depending on which pull's anchors are loaded; small lanes render nonsense bands.
**Fix:** freeze launch anchors for the first N pulls (or until delta > ε on the anchor itself); tier demotion requires K consecutive pulls below the cut; integer rounding rule for bands at n<10; filtered views either hide lane-rank or recompute rank-in-filter with its own label.

### 9. [COVERAGE] CONVERGED-PLAN.md:14,50 vs REQUIREMENTS.md:10,39 — the models tab (one of 6 surfaces) has no import path, no schema, and its curation is outside every estimate

Plan: ":14 models tab: per-task leaderboards (benchmarks census + our verdict lines, CONTESTED marked)" and ":50 models leaderboard data shape … (curation pass)" — data shape explicitly undecided at convergence. The owner's import requirement ("fast workflow import from our site into comfyui", REQUIREMENTS.md:10) and models-tab requirement (:39) meet nowhere: the import block (:29) exists only on workflow detail pages. A user on the models tab who finds the best i2v-audio checkpoint (model-benchmarks T4) has no path from leaderboard row → download → folder placement — the plan's own import knowledge (exact folders, pinned versions) is simply not wired to this surface. And the ~30 per-task verdict lines are a curation pass not present in the :51 estimate (which covers only the 100 library entries).

**Cost if unfixed:** models tab ships as inert tables (the requirement's "fast import" fails on the second tab the owner explicitly asked for) or slips silently.
**Fix:** per-model leaderboard row → linked entries using that model + folder path + civitai download link (reuse the 78 row renderer); add models.json shape to :41 and its curation line to :51.

### 10. [GUARD DROPPED] CONVERGED-PLAN.md:23 vs idea-analysis-26-50.md:247,249 — the curation-tax filters lost their coverage-report guard; the FIRST filter in the bar runs on unproven manual data

The analyst's build-order note (:247): "curator fields vram/outputs/locks decide whether 32/36/39 ship honest or ship empty — coverage reports in build are the guard." The range's recurring risk (:249): "an under-curated filter silently becomes a lying filter." The plan (:23) ships "exactly 4 visible: VRAM (first — impossibility filter) / base model / output-task / freshness" plus locks/inputs/audio in "+more" — and its build section (:40-41) contains no coverage report, no population threshold, nothing. VRAM is doubly exposed: the badge is manual curator data (CRITERIA.md:59, "vram badge manual" — the API-proven absence R1 #6 documented), so the site's FIRST-positioned "impossibility filter" filters on unverified guesses with no visibility into coverage.

**Cost if unfixed:** users on 8 GB cards are silently excluded from entries that would run (filter says impossible, guess was wrong) — the love-then-betrayal failure idea 25 was adopted to kill, now caused by our own filter; or chips show near-zero yields and the lane looks empty.
**Fix:** build-time coverage report per curation-tax field (idea 26-50's own mechanism: "build prints a coverage report … per lane"); filter auto-hidden below coverage threshold; vram badge carries provenance (measured-on-rig / estimated).

### 11. [CONTRADICTION] CONVERGED-PLAN.md:8 vs research/codex-design-ideas.md:59-78 — "Dark default" contradicts the binding token source it names in the same sentence

":8 codex Direction B … tokens/typography read from research/codex-design-ideas.md §Direction B at build time (binding source, builder does not invent). … Dark default." Direction B's color system (:73-78): Paper `#F0EEE7` (light cream ground), Ink `#171717` — a LIGHT editorial theme; the dark system belongs to Direction C (:127 `#120B2E`). The plan grafts a dark default onto a direction whose binding tokens are light, in the sentence that declares the tokens binding. The builder must either violate "binding source" (invert the palette = inventing) or violate the plan (ship light).

**Cost if unfixed:** guaranteed build-time conflict resolved by whoever codes first, unlogged; or a muddied half-dark theme that is neither direction — the "taste is the advantage" claim dies in the CSS variables.
**Fix:** decide: ship B as tokenized (light, Paper/Ink — the "field guide" identity IS paper) with dark as a later mode; or re-derive a B-dark token set in the codex doc FIRST and keep "binding source" true. One line, now.

### 12. [GAMEABILITY] CRITERIA.md:24 — the R1#4 fix shipped with OR where the attack was cheap-AND: a 1-year-old sock account with a zero-upvote self-post still passes the S-gate

R1 #4 (strategy D) demanded mention quality gates. v2 (:24): "Qualifying: thread >= 10 upvotes OR account >= 1yr." Disjunction: a purchased 1-year-old account posting a 0-upvote thread qualifies; a 1yr account costs pocket change. The S-gate (:25, "S badge REQUIRES >= 1 qualifying mention") remains the cheapest farm path in v2 — one bought account converts a gated A into S, and idea 90's badge (unplaced, finding 4) was the only visible counterweight.

**Cost if unfixed:** first exposed bought-S collapses the "rankings stay honest" thesis the whole criteria document exists to defend.
**Fix:** AND both minimums (≥10 upvotes AND account ≥1yr), or upvote-threshold-only with account age as a scoring nudge; log the ruling in the curation log like any override.

### 13. [FEASIBILITY] CONVERGED-PLAN.md:20,32,38,41 vs data/cdn_probe.json — every preview in the architecture is a hotlinked signature URL whose longevity is probed for ZERO days; caching is forbidden by the legal file; the plan carries no contingency

cdn_probe.json: `checked 5, urls_rotated 0` — same-session, same-day re-fetch; proves nothing about week-scale expiry (the timescale that matters: static build + weekly rank-keeper cadence). legal-pages-policy.md:21: "Local caching of thumbnails FORBIDDEN until this section carries an answer" — still unresolved. The plan bakes `preview.url_*` (sig-shaped image.civitai.com URLs, verified present in all 100 candidate records) into static HTML for every card, with no rot-detection, no placeholder strategy, no fallback. DREAM.md names the risk ("cdn hotlink breaks → probe queued … do not cache"); CONVERGED-PLAN — the binding build doc — does not mention it at all.

**Cost if unfixed:** if sigs expire between builds, 100% of previews 404 mid-cycle and the site renders as gray boxes until the next pull; discovered by the owner, not by any test.
**Fix:** extend the probe to a real timescale (re-fetch same ids across ≥2 weeks pre-launch, log rotations); sitegen gains a preview-health check at build (HEAD each URL, warn on non-200); contingency specced: placeholder + "preview on civitai ↗" swap — decided now, while it's cheap.

### 14. [BUDGET/SCOPE] CONVERGED-PLAN.md:38,41 — "~<500 lines total" runtime vs the adopted interaction inventory: an unmanaged tradeoff waiting to happen in a builder's head

The same plan that adopts: URL-state sync (idea 10), one shared predicate driving grid + live chip counts + rescue (N1), synonym search with interpretation chips + alias + scope lane/all/saved + recent-searches + mature-history guard (:32), lightbox with keys/swipe/preload (:38), blur reveal, session-confirm with 30d remember (:35), toast, sticky band headers, thumb-scrub, plus accountless shortlist (70) — budgets the whole runtime at "<500 lines". Search alone (synonym expansion + alias resolution + scope + guards) is realistically a third of that. The claim is unfalsifiable today, but its function is dangerous: when reality exceeds 500, the cut happens silently mid-build with no priority order — the same silent-drop mechanism as finding 4, one layer down.

**Cost if unfixed:** adopted interactions die unlogged at build time; or the number is quietly ignored and the plan's credibility absorbs it.
**Fix:** per-feature line budget (feature → est lines → may-cut order) or delete the 500 claim. A budget without a kill-order is a trap, not a constraint.

---

## TOP 3 TO FIX FIRST

1. **Finding #1 (nsfwLevel blindness)** — data-proven explicit previews on the default SFW route; same takedown/owner-promise class R1#1 killed, now living in the data and invisible to the plan's own build test. One sitegen gate + test extension removes it; nothing else in the plan is safe to build until the content-class model is coherent.
2. **Finding #2 (mature pipeline branch)** — the mandate's central question has no answer in the binding artifact, and two of the three implementable answers leak mature names/URLs to every visitor while the CI test stays green. Decide branch 3 (separate mature.json + split search index + test over shipped artifacts) before any HTML is generated.
3. **Finding #3 (gallery data missing)** — an owner-verbatim requirement (REQUIREMENTS.md:11) is unimplementable from the plan's own schema today; every day of curation that proceeds without `images[]` in curated.json is data that will have to be re-walked later. Field + collector decision is one edit.
