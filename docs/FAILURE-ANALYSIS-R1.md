# FAILURE ANALYSIS R1 — civitai-library v0 (owner verdict 2026-09-02: "lixo fingindo ser pronto, resultado é uma bosta, total")

ROOT (one line, influencer-v3 law 77): validation avoidance — every layer stopped at first output, grading was always "next", garbage compounded until the owner saw it.

## A. PRODUCT SHAPE — every shape decision wrong
1. public editorial site ("Field Guide", hero, marketing framing) vs INTERNAL TOOL dense and total — owner said "library pessoal" on message 1; I ratified codex's public-site direction instead of his words.
2. SFW-default toggle ceremony vs NSFW ON BY DEFAULT (owner m0124) — his tool, his default; I imported a public-site safety pattern he never asked for.
3. flat list per lane vs PIPELINE organization: the library's job is creating an influencer end to end (persona total realism -> movement -> speech/voice -> camera/angle -> ads with her -> nsfw/OF). no stage structure exists.
4. no DECISION MATRICES: "this one low vram, this one max quality, this one for X" — alternatives per purpose with trade-off labels, nowhere.
5. no ENHANCEMENT-LAYER class: LoRAs/workflows that stack on top as improvement layers (skin detail, lighting, motion physics) — a first-class concept in his head ("ponta do iceberg"), absent in my model.
6. open-source-leaning lens (owner m0119) — no open/closed badge anywhere.
7. "best according to whom" (m0117) unanswerable on screen — criteria lived in docs, never surfaced as visible reasoning.

## B. DATA/FUNNEL — the core fraud
8. funnel of ONE PAGE: 100 candidates (1 sort x 1 period x 1 page per lane) presented as "the shortlist". owner's model: pull 5k-10k, THEN filter. my garimpo never funneled — it grabbed.
9. lane pulls not purpose-driven: generic Highest Rated caught the anime wave; persona lane = 38 anime vs ~10 realism entries; Takorin (anime illustrator LoRA) answers zero of the 3 lanes (owner's own kill question).
10. community census (75 URLs, 14 threads, named consensus: Wan 2.2 realism magic, Chroma/Biglust/Lustify/Aramanta amateur-look, Anteros XXXL/BigASP photoreal, LTX2 audio) NEVER became pull seeds — research as decoration.
11. no scraping depth: census documented cursor pagination, 5 sorts, 5 periods, tag queries, collections, articles, image-walk with meta — garimpo used one slice.
12. criteria "calibrated" on the same shallow pull — circular calibration, anchors from 100 top-rated rows.
13. lane-fit axis (10 pts in criteria v2) defined, never executed on any entry before render — the exact axis that would have killed Takorin.

## C. UX/MICRO — his original asks, unimplemented
14. hover does NOTHING: no gallery scrub, no video autoplay (m0126) — the 20-micro-interactions doc existed and was never wired into the build spec as mandatory.
15. too many clicks, too much scroll (m0127) — violates his message-1 "menos cliques de navegação"; detail-page-required browsing instead of expand-in-place density.
16. text small, hard to read (m0123/m0117).
17. previews missing at render (m0117/m0123) while data had 86/100 galleries — render bug shipped.
18. categories illegible (m0117) — lanes existed, belonging didn't.
19. models tab doesn't answer melhor/pq/nota/avaliação (m0117) — data had verdicts, page didn't lead with them.

## D. PROCESS — validation theater
20. site shipped ungraded: my own todo "grade codex site with browser probe" was pending when the owner opened it.
21. probe m0118 FOUND the breakage (personas page missing, 0 imgs on home) and the turn ENDED without a fix — found broken, did nothing.
22. hostile rounds attacked documents, never the rendered product — no visual/browser adversary before his eyes.
23. "done" claims with commits+closes while product broken — fake-ready (owner: "lixo fingindo ser pronto").
24. predictions unscored: this complaint was predictable — my own m0076 error list named "quality reactive to owner pushes" and the same disease repeated within the session.
25. curation review approved the anime imbalance with "ships as-is, next pull tops up" (law 61 violation — mediocrity shipped with a note attached).

## SPEC DELTA (from m0119+m0123+m0124+m0126+m0127 — binding for rebuild)
- internal tool: no hero, dense grid, readable sizes, NSFW ON default
- IA = the influencer pipeline: stages Persona/Realism -> Motion (i2v) -> Speech/Voice -> Camera/Angle -> Ads assembly -> NSFW/OF, plus ENHANCEMENT LAYERS as stackable class with "stacks-on" tags
- every stage: decision matrix (low vram | max quality | purpose-X alternatives), trade-off labeled, open/closed badge
- hover = play (video autoplay, gallery scrub); previews real and everywhere; video previews where they exist
- big funnel: 5-10k pulled (cursors, sorts x periods x tags x types, census seeds) -> criteria at scale -> top per stage + transparent cut panel ("pulled X -> shown Y, why")
- scores with visible why (breakdown popover: community anchors + our verdict)
- minimal clicks: expand-in-place, filters inline, one screen per stage
