# HOSTILE PLAN REVIEW — R1 (2026-09-01)

Reviewer: zero-context hostile agent. Every finding verified against file contents on disk + live-pulled data in `data/`. Line numbers refer to current files. Severity order: worst first.

---

## FINDINGS

### 1. [LEGAL/CONTRADICTION] docs/DREAM.md:28 vs research/legal-pages-policy.md:10-11 — DREAM still plans the exact thing legal banned

DREAM sad path: *"github pages vs adult content → nsfw off by default, **blurred previews, explicit imagery loads only after toggle**"*. The legal doc's binding decision: *"NO explicit imagery loaded, **hotlinked or cached**"* on the pages build. DREAM was written 22:07, legal landed 22:09, DREAM never updated.

**Cost if unfixed:** whoever builds P2 from DREAM (the doc that structures the build) ships toggle-gated explicit previews on github.io → the exact AUP takedown the legal research exists to prevent. Repo + pages nuked, final link dead, owner's one deliverable gone.
**Fix:** rewrite DREAM:26-31 to restate the legal decision verbatim (metadata-only lane C, no explicit assets in pages build) and mark the toggle-gated-imagery idea as REJECTED.

### 2. [FEASIBILITY] docs/CRITERIA.md:4,11 + :50 — the owner's #1 answered question ("nota/tempo? YES") is built on a stat the API does not return

CRITERIA.md:4 answers "nota/tempo? YES → engagement decayed by time (**period stats** + recency)". CRITERIA.md:11: "thumbsUp/downloads ratio (**period > all-time when available**)". Receipt in own research, community-sources.md:147 (complaint #10, civitai/cli PR #155): *"the API does not return per-period download totals"*. The `period` param (census §1.5) only selects the sort/discovery window — stats attached to returned items are all-time. "When available" = never. Worse: garimpo's own schema (`data/candidates-persona.json` `stats.period: "Month"` stamped beside all-time counts) reproduces complaint #10's mislabeling inside our data format.

**Cost:** the flagship criteria answer ("we fixed civitai's misleading windows") is itself misleading; any consumer of `stats.period` computes wrong rankings; owner discovers the promise was hollow at first re-validation.
**Fix:** redefine the time axis on what's real: rank-keeper snapshot **deltas** (store all-time counts + pulled_at each run, decay = growth rate between snapshots), label every stat `window=all-time`, and drop "period stats" language from CRITERIA.md entirely.

### 3. [FEASIBILITY] docs/CRITERIA.md:5,12 + :4 — comment recency / "engagement decayed by time" is unpullable: no comments endpoint exists

CRITERIA-DRAFT.md:35 explicitly asked: *"does civitai api expose comment timestamps (engagement recency)?"*. The census endpoint table (civitai-api-census.md:26-38) answers: Models, Model-versions, Images, Articles, Collections, Creators, Tags, Users, Permissions, Vault, Enums — **no comments endpoint**. Only scalar `commentCount` exists (census:90,126). CRITERIA.md v1 shipped anyway promising time-decayed engagement and "commentCount relative to type-median" — the median part is pullable, the decay part is not.

**Cost:** 30-point community axis is half-fictional; the unanswered draft question was silently dropped instead of closed; implementer discovers at build time and improvises.
**Fix:** close the draft question in CRITERIA.md ("comment timestamps: NOT pullable — recency via version `updatedAt` and future snapshot deltas only") and re-weight the engagement axis to what exists.

### 4. [GAMEABILITY] docs/CRITERIA.md:10-17,20,23-27,40 — at least four farm paths to S, none defended

Concrete farming strategies against v1 scoring:

- **Strategy A — ratio sock-puppetry (30 pts):** `thumbsUp/downloads ratio` has no minimum denominator and period spikes are invisible (no period stats, see #2). A merge farm's discord upthumbs a fresh upload: 40 downloads / 35 thumbs = elite ratio, commentCount padded by the same socks ("great model!" ×20 beats type-median). ~25+ pts of the 30-pt axis bought for free.
- **Strategy B — version re-upload freshness farming (15 pts):** "version lastUpdated <90d full points" is **creator-controlled**. Re-uploading a v-whatever zip every 80 days keeps full freshness forever; kill-line "base model 2+ generations stale" doesn't touch merges of a current base.
- **Strategy C — completeness box-ticking (15 pts):** every completeness input (usage instructions, trigger words, attached workflow file, model list) is authored by the same creator being scored. A garbage merge farm maxes 15/15 by filling four text fields. Zero of it is verified by running the workflow.
- **Strategy D — self-planted external mention (S-gate):** "S-tier REQUIRES ≥1 external mention" — one sockpuppet reddit/x post satisfies the gate that exists to "kill civitai-only hype". No independence, vote-quality, or account-age check on the mention.
- **Bonus — manual override ±15 (line 40):** self-cited "reason", no second rater. Combined with D, an entry reaches S by fiat.

**Cost:** the site's entire value proposition is "rankings stay honest"; these four paths make S purchasable by the exact merge farms the community complaints describe (§2E #4). One exposed farm ranking = site dead on arrival in the circles it targets.
**Fix:** floor all ratios (e.g. ≥500 downloads before ratio scores), score completeness only on curator-verified fields (did WE run it), require external mentions with minimum thread engagement + account age, and cap the manual override's ability to cross tier boundaries.

### 5. [COVERAGE/FEASIBILITY] community-sources.md:76,138 vs docs/CRITERIA.md:10-13 — the thesis signal (usage, not downloads) was dropped from the scoring

Community research names CivArchive's usage-based ranking *"exactly our thesis"* (community-sources.md:76) and complaint #1 is "downloads ≠ usage". Yet CRITERIA.md's engagement axis uses only thumbs/comments/reaction ratios — and never the one usage proxy the API actually exposes: `GET /images?modelVersionId=` with `meta.civitaiResources` (census §1.7) counts posted images actually generated with the version. That signal is both harder to farm (requires posting generated images) and pullable.

**Cost:** scoring optimizes the wrong variable the owner explicitly flagged; farmable ratios fill the space the anti-farm usage signal should occupy.
**Fix:** add a usage axis: posted-image count per modelVersionId (capped, log-scaled, pulled via /images walk) replacing at least half the ratio weight.

### 6. [FEASIBILITY] docs/CRITERIA.md:29-31 + :7 — hardware axis (10 pts) + vram tier badge has NO data source

Live-pulled candidate data (`data/candidates-persona.json`) contains zero vram fields; the census documents zero vram fields on any endpoint (license fields §1.10, files §1.6 — sizeKB exists, vram does not). `vram tier: <=12 full / 16 partial / 24+ minimal` scores nothing pullable. Same for the badge ("community: 6/8/12/16/24 GB are the real splits" — a community quote, not an API field).

**Cost:** 10% of every entry's score is invented at curation time with no provenance; "chooses by VRAM before importing" (codex criteria) renders on fabricated data; inconsistent manual guesses across 50 entries.
**Fix:** demote vram to a manual curator field with explicit provenance ("curator-measured on RTX X"), or derive a coarse proxy from `files[].sizeKB` + baseModel type with the derivation written down; stop scoring it as API data.

### 7. [CONTRADICTION] docs/REQUIREMENTS.md:38 vs docs/DREAM.md:21 + docs/OPEN.md:21 — image-to-video-with-audio lane orphaned

Owner requirement verbatim: *"image-to-video is its own lane where audio/speech support exists: HD image first + defined speech + voice-first generation"*. The plan everywhere else says THREE lanes (DREAM:21 "~50 entries, 3 lanes"; OPEN.md:21 "nsfw: toggle"; codex directions A/B/C = Persona/Ads/Mature). Nowhere is it decided whether the i2v+audio requirement lives inside lane B, as a 4th lane, or as a tab. The requirement has no owner downstream.

**Cost:** P2 site ships without the lane the owner explicitly separated; model-benchmarks T4 (the best-researched task in the census!) has no home in the IA; discovered missing at handoff = structural rework, not a patch.
**Fix:** one decision line in OPEN.md: either 4 lanes or "i2v+audio = first tab inside Campaign Lab" — named before CONVERGED-PLAN.md is written.

### 8. [LEGAL] research/legal-pages-policy.md:13 + docs/OPEN.md:21 — the "unlocked build as downloadable artifact" escape hatch does not escape the AUP

Legal doc: explicit imagery allowed in an *"unlocked" full-preview build distributed as downloadable artifact (NOT served from github pages)"*. A github **release asset / repo file** is still content hosted on github's service under the same Acceptable Use Policy that the doc itself cites for pages ("pages inherits AUP"). Moving bytes from the pages branch to a release does not change which company's policy governs them.

**Cost:** owner exercises the nsfw lane's only preview path → explicit imagery sits in a github repo → same takedown, now with the whole curated repo, not just a build.
**Fix:** the unlocked build's home must be off-github entirely (owner's own host, external drive distribution) — or the nsfw lane stays metadata-only forever, stated as final, not "optional later".

### 9. [LEGAL/COVERAGE] docs/REQUIREMENTS.md:11 ("RESULTS visible") vs docs/OPEN.md:21 — lane C permanently fails the owner's core requirement and the plan calls it resolved

Requirement: *"lora/workflow RESULTS visible: preview images, navigate between examples"* — no lane qualifier. Decision (OPEN.md:21): nsfw lane = metadata + link-out, previews "optional later, if owner wants" (legal:13). So one of the 2-3 focus lanes ships with zero result visibility on the ONE link that is the final delivery (REQUIREMENTS:7), and the mitigation is deferred-optional. Nobody flagged this trade-off back to the owner as a requirement conflict.

**Cost:** owner opens his own site, clicks the lane he cares about (OF/NSFW is in the stated focus), sees text-only cards — the nightmare scenario ("no previews... nobody opens it twice") for exactly the audience of lane C.
**Fix:** surface the conflict explicitly: "lane C cannot show previews on github, ever — accept metadata-only, or pick an off-github home now." Owner decides; docs stop pretending the requirement is covered.

### 10. [FEASIBILITY] docs/OPEN.md:14 — the nsfw blocker lists only the API key; the key alone may silently return clamped data

Census §1.11: authenticated callers see content "up to their **configured browsing level**"; the anonymous public level is OPEN and the census's own advice — *"probe with/without key before assuming what anonymous sees"* — has no corresponding task in the P1 queue. If the owner's account browsing level is default, the nsfw pull returns soft-clamped results with HTTP 200: a silent failure (exactly the sad-path class T-SAD exists for), polluting lane C candidates invisibly.

**Cost:** lane C's first batch is silently SFW-clamped; curation happens on incomplete data; nobody notices until the owner sees obvious omissions.
**Fix:** add a P1 probe task: key + account browsing level set to X/XX, pull 10 known-explicit model ids, assert their presence before any bulk nsfw pull; garimpo fails loud on clamp.

### 11. [INTERNAL CONTRADICTION] docs/CRITERIA-DRAFT.md:37 vs docs/CRITERIA.md — the nsfw parity question was asked, then silently dropped

Draft promised: *"does nsfw content get systematically under-scored vs sfw (parity correction needed)?"* — listed as one of five questions research must answer. CRITERIA.md answers four (nota/tempo, comments, docs, vram-source… partially) and contains **nothing** on nsfw parity. Every engagement axis (thumbs ratios, comment medians, external mentions) runs on a platform that gates/hides nsfw by default (census §1.11) and an external-mention source pool where the main nsfw subreddit thread is marked OPEN/unreachable (community-sources:171).

**Cost:** lane C entries are systematically under-scored on 50 pts of axes → the nsfw lane shows all-B tiers at launch → looks broken → owner concludes criteria are garbage.
**Fix:** either answer it (per-lane normalization: rank nsfw entries among nsfw entries, like the per-type normalization already at CRITERIA.md:52) or write "parity: deferred, nsfw scored within-lane only" — but close the question.

### 12. [CONTRADICTION/PROCESS] docs/OPEN.md:4,7 — "no code yet BY DESIGN" is false on disk, and the build jumped its own review gate

OPEN.md:4: *"no code yet BY DESIGN (assembly law: census before build)"*. Queue (OPEN.md:7): garimpo comes at P1, **after** convergence + hostile review. Disk right now: `tools/garimpo.py` (7.4KB) + `data/candidates-*.json` (435KB pulled 22:43, i.e. AFTER CRITERIA.md 22:39). The state file is stale by half an hour of work and the queue gate (hostile review before build) was already jumped by the very session that declared it.

**Cost:** this review reviews artifacts code is already diverging from; garimpo bakes criteria assumptions (period=Month discovery, stats schema) that findings #2/#5 may overturn; every future reader of OPEN.md inherits a lie about machine state — the exact failure class this project's process exists to kill.
**Fix:** update OPEN.md state to what exists (garimpo v0 + 120 candidates pulled, gate jumped — own it), and diff garimpo's assumptions against this review before P1 continues.

### 13. [COVERAGE] research/RESEARCH-PLAN.md:16-17 — RQ4 (ux census) never landed and nobody re-queued it

RESEARCH-PLAN wave 1 lists `ux-census (librarian bg bg_4fbb1198) → research/ux-census.md`. No such file on disk; OPEN.md doesn't track it as missing. The owner's requirements lean hard on format/order/"instantly understandable" — the one census that grounded *how the best catalog sites organize dense visual browsing* is gone, leaving codex-design-ideas as the only design input (and it opens by inventing its own calibration, codex-design-ideas.md:52).

**Cost:** the "format & order matter a lot" requirement (REQUIREMENTS:13) rests on a single LLM's unanchored proposal instead of the planned comparative census; the exact "no reference = slop" failure mode.
**Fix:** re-launch the ux census or write a one-line kill decision with reason in RESEARCH-PLAN.md; do not converge the design direction without it.

### 14. [GAMEABILITY/STRUCTURE] docs/CRITERIA.md:36-40 — four scoring systems, no combination rule

The manual layer defines: 0-100 auto-score (weighted axes), our manual 1-10 score, S/A/B tier, and a ±15 override. Nowhere is the composite defined — how does 1-10 relate to 0-100? Does the tier derive from the composite or is it independent? Can the ±15 override cross a tier boundary? Codex's UI shows "8.9/10" editorial (codex:1203) and "community signal" separately — a THIRD layout of the same numbers.

**Cost:** two curators (or two sessions) produce non-comparable scores; the displayed number cannot be audited back to axes; tier disputes unresolvable because the rule doesn't exist.
**Fix:** one paragraph: composite formula, tier thresholds on the composite, override may not cross tiers, 1-10 is display-only derived from composite.

### 15. [LEGAL] docs/CRITERIA.md:57 + docs/DREAM.md:31 — two load-bearing "license permitting" questions never analyzed by the legal file

The legal file covers exactly two things (github porn policy, API-access authorization). It is silent on: (a) **re-display/caching of civitai CDN images** on a third-party github.io domain — DREAM:31 says "cache thumbnails locally (license permitting)" and the permission question was never asked, while the CDN URLs are signature-shaped (`/<sig>/`, census:166) with expiry behavior unprobed — if sigs expire, every hotlinked preview rots and local caching becomes the only option, licensed or not; (b) **mirroring workflow zips** (CRITERIA:57, anti-takedown answer to complaint #8) — redistribution rights come from `allowDerivatives`/`allowDifferentLicense` (census §1.10), never decoded, and zip contents are uninspected — an nsfw-adjacent workflow archive can embed explicit preview images **inside the repo**, defeating the legal doc's own zero-explicit-imagery rule through the back door.

**Cost:** (a) all previews die at sig expiry or ship as ToS violations; (b) the anti-takedown mirror reintroduces the takedown content through a zip.
**Fix:** legal file gains a section: ToS re-display analysis, CDN sig expiry probe, mirror policy = json-only (never zips) + unzip-inspect rule.

### 16. [STRUCTURE] research/codex-design-ideas.md:1-141 + :143-736 vs :738-1330 — raw transcript: leaked system prompt, shell noise, and the entire output duplicated verbatim

The "research" file opens with 50 lines of the codex system prompt (design-lead persona instructions — not project content), then dead shell transcript from an unrelated directory (`/home/eder/Documentos/sheol` file listing, empty `web search:` calls), then the design content **twice** — lines 143-736 and 738-1330 are byte-identical including the "tokens used 43.178" marker.

**Cost:** every future agent pays 2× read cost and double grep hits on all 100 ideas; the leaked prompt noise can contaminate citations (an agent quoting "design principles" as if they were project doctrine); file is 57KB where ~25KB is signal.
**Fix:** keep one copy starting at the `# civitai-library` header; delete prompt + shell noise + duplicate; note provenance (codex session, date) in a two-line header.

### 17. [FEASIBILITY] docs/CRITERIA.md:13,34 + data/pull — preview honesty (10 pts) and image reactions have no collector

"Image reactions on preview posts (likeCount, heartCount from /images)" and "preview carries generation meta" both require walking `GET /images?modelVersionId=&withMeta=true` — garimpo v0 pulls `/models` only (pull_log.json: 2 URLs, both /models). Live candidate records carry preview URLs but no reaction counts, no `meta`. Also CRITERIA:34's honesty check ("meta present = real output") can't distinguish *which* model produced the preview — `meta.civitaiResources` maps resources, but a farm can attach any honest meta image from a different stronger setup (codex idea #88 flags the preview-baseModel-mismatch risk; the criteria's binary "meta present" does not).

**Cost:** 20 pts of the score (reactions + honesty) silently have no data at curation time → curator eyeballs substitute → non-reproducible scores.
**Fix:** P1 garimpo gains an /images walk per shortlisted version (reactions + meta + resource match to the version being scored); honesty check = "meta resources CONTAIN this versionId", not "meta present".

---

## FIX FIRST (top 3)

1. **Finding #1** (DREAM:28 vs legal) — one doc edit now removes a repo-takedown path that survives into every downstream build artifact. Cheapest catastrophic-risk kill available.
2. **Finding #2 + #3** (period stats / comment recency unpullable) — the owner's first criteria question is answered with fiction; every score computed before this is fixed is built on stats that don't exist. Re-anchor the time axis on snapshot deltas before P1 curation starts.
3. **Finding #4 + #6 + #17** (scoring data-path audit) — before any entry is scored, each of the 100 points must name its collector + field. Right now ~55/100 points (external 20, completeness-verified 15 subshare, hardware 10, reactions+honesty 20→partially) have no data source or are creator/self-supplied. A score computed on undefined inputs cannot be re-validated by rank-keeper — the site's core honesty promise dies at birth.
