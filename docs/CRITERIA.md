# CRITERIA — v2 (manager's personal deep review of every point; calibration receipts in research/criteria-calibration.md, run 2026-09-02 on the real 100-candidate pull)

## review verdicts on v1.1 (each point, personally)
- engagement 25: KEPT but rebuilt — universal ratio anchor was garbage (workflows ratio median .033 vs persona .085 — one anchor misranks a whole lane). Per-lane anchors from pull data, recomputed every pull. Comment component: medians are 0 in all lanes (nsfw p75 = 0) — comment scoring becomes lane-banded, dropped to 5 pts, display-only where lane p75 = 0.
- usage 15: KEPT, banded (fake precision on capped estimate was garbage — "100+" cap makes log-scale dishonest). Bands: 0 / 1-29 / 30-99 / 100+ → 0/5/10/15.
- external 15 + S-gate: KEPT, but launch reality = most entries have no logged mention yet; rescued by per-lane rank tiers (below) so the site does not look broken at birth.
- freshness 15: KEPT as age bands only (mixing generation currency into scoring was double-counting — generation staleness is a kill-line, not a score). Re-upload cap: changelog not pullable → curator-logged, capped effective 10.
- completeness 10: KEPT curator-verified only. Exact checklist fixed: ran-it OR confirmed-recipe + trigger words + model list + node list (4 x 2.5).
- preview honesty 10: KEPT binary meta_match (meta.civitaiResources contains versionId). "Unknown" (no /images walk yet) = 0 + "unverified" label.
- lane fit 10: KEPT, rubric fixed at 0/5/10 (off-lane / fits / exemplar-for-the-lane).
- hardware in score: stays OUT (API has no vram field — proven). Badge + filter only.
- parity: SOLVED STRUCTURALLY — tiers are per-lane rank bands (below), not absolute cuts; raw composites never compare across lanes.
- composite: v1.1's "display composite/10" read as garbage at low composites (37 → "3.7/10" feels dead). Display is TIER-FIRST: badge + lane rank primary, composite secondary.
- delta-decay: v1.1 language was vague garbage. Staged honestly: v1 = trend display only; scoring impact requires >= 4 weekly snapshots.

## scoring v2 — exact formulas (anchors = lane percentiles of current pull, stored in build stats; data-cited, not vibes)
engagement 25 [collector: /models stats]
- ratio_component 10 = min(1, ratio / lane_p75_ratio) * 10, where ratio = thumbsUpCount/downloadCount, eligible only if downloadCount >= 500 (else 0 + flag)
- magnitude_component 10 = min(1, log10(max(downloadCount,1)) / log10(lane_p90_downloads)) * 10
- comments_component 5 = commentCount >= lane_p75_comments ? 5 : commentCount > lane_median ? 3 : 0; if lane_p75_comments == 0 (nsfw today) → component disabled, weight redistributes to ratio (ratio becomes 15) — evidence: nsfw p75 = 0
usage 15 [collector: /images walk, garimpo v0.1]
- bands on posted_images_est (meta-matched images per version): 0 → 0; 1-29 → 5; 30-99 → 10; 100+ → 15
external validation 15 + S-GATE [manual evidence log]
- 1 qualifying mention = 10; 2+ = 15. Qualifying: thread >= 10 upvotes OR account >= 1yr; curator logs URL
- S badge REQUIRES >= 1 qualifying mention
freshness 15 [/models version updatedAt]
- <= 90d: 15; <= 180d: 10; <= 365d: 5; older: 2. Re-uploads without curator-verified change cap at 10 effective
completeness 10 [curator-verified only]
- ran-it-or-confirmed-recipe 2.5 + trigger words 2.5 + model list 2.5 + node list 2.5
preview honesty 10 [/images withMeta]
- meta_match true = 10; false = 0; not-walked = 0 + unverified label
lane fit 10 [manual rubric]
- 0 off-lane / 5 fits / 10 exemplar; reason logged

## tiers v2 — per-lane rank bands + absolute floors (auditable, parity-free)
- S: top 10% of lane by composite (min 5 entries in lane, else single best only) AND composite >= 70 AND external gate AND curator-verified
- A: next 25% of lane AND composite >= 55
- B: next 40% AND composite >= 35
- C: rest
- kill-line caps apply regardless of rank: stale base generation → max B; zero docs AND zero comments → max B
- display order: [tier badge + "#rank in Lane"] primary, composite/10 one decimal secondary, trend arrow when deltas exist
- tier disputes resolvable by: recompute(composite) from logged axes + rank check — both mechanical

## manual layer + audit trail
- override +/- 10 composite, CANNOT cross tier band edge, reason + author + date in curation log
- every entry carries: curated_by, curated_at, confidence (high/med/low), one-line verdict (english)
- display score derives from composite; curator's raw 1-10 gut note stays internal (never displayed — two visible numbers was ambiguity garbage)

## anti-farm block (unchanged, now with calibrated teeth)
- ratio floor 500 dl + magnitude blend (sock farm must first pass real-distribution scale)
- usage banded + meta-matched (faking requires posting generated images with honest meta)
- completeness curator-verified; mentions quality-gated; override tier-locked; merge penalty via checkpointType + curator flag

## data honesty
- every stat {value, window:"all-time", pulled_at}; anchors {lane, p75_ratio, p90_dl, p75_comments, computed_at} stored per pull in build stats
- first batch label: "no delta history" — deltas display-only until >= 4 weekly snapshots, then decay enters scoring (v2.1)

## model-side criteria (models.json) — unchanged from v1.1
live benchmark position + board + date; open weights + license landmines; ComfyUI support; vram badge manual; consensus quotes linked; our one-line verdict. Contested marked CONTESTED.

## worked example (real entry, persona[0] "One obsession", pull 2026-09-02)
dl 245,327 / thumbs 17,050 / ratio .0695 / usage 100+ meta_match true
- ratio: .0695 / lane_p75 .138 = .50 -> 5.0
- magnitude: log10(245327)=5.39 / log10(224437)=5.35 -> capped 1.0 -> 10.0
- comments: (entry commentCount vs lane p75 47) — banded at build
- usage: 100+ -> 15; honesty: true -> 10
- engagement+usage+honesty so far: 5+10+15+10 = 40 + freshness/external/completeness/lane-fit per curation
- sanity: formula rewards magnitude+usage, does not crown a sock farm (floor + anchors from real distribution)
