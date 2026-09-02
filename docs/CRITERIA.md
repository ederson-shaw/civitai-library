# CRITERIA — v1.1 (post hostile R1; every axis names its collector + API field or is marked manual)

closed questions (answers from receipts, not vibes):
- nota/tempo? YES, but NOT via civitai period stats — API returns all-time counts only (civitai/cli PR #155; period param selects discovery window, not stat window). Time axis = rank-keeper SNAPSHOT DELTAS: every pull stores {value, window:"all-time", pulled_at}; growth rate computed between snapshots. First batch is honestly labeled "no history yet".
- comment recency? NOT PULLABLE — no comments endpoint, commentCount has no timestamps (census endpoint table). Recency proxies: version updatedAt + future snapshot deltas. Question closed.
- documentação? YES — but creator-authored text is box-ticking, not signal (hostile #4C): completeness scores only CURATOR-VERIFIED facts.
- low vram? YES as FILTER + badge, NOT as score — API returns no vram field (proven by live pull). Badge assigned manually from community sources.
- nsfw parity? ANSWERED: per-lane normalization — nsfw entries ranked among nsfw entries only (platform gates nsfw engagement; cross-lane raw scores are not comparable).

## axes (100 pts) — each with named collector
engagement 25 [collector: /models stats]
- thumbsUp/downloads ratio, ONLY when downloadCount >= 500 (else axis defaults to type-median — kills sock-puppet ratio farming on fresh uploads)
- commentCount vs type-median (type = LoRA/Checkpoint/Workflows, medians recomputed per pull)
- delta-decay once >= 2 snapshots exist

usage 15 [collector: /images?modelVersionId= walk, garimpo v0.1]
- log-scaled count of posted images whose meta.civitaiResources CONTAIN the versionId — the "used, not downloaded" signal (community thesis, complaint #1)
- hardest to farm: faking it requires posting generated images with honest metadata

external validation 15 + S-GATE [collector: manual evidence log, curator]
- mention must carry: thread >= 10 upvotes OR account >= 1yr; curator logs URL per claim
- S-tier REQUIRES >= 1 qualifying mention (self-planted socks fail the quality gate)

freshness 15 [collector: version updatedAt + benchmarks census generation table]
- version updatedAt < 90d full / < 180d partial / decay
- base model generation currency
- NOTE: updatedAt is creator-controlled (re-upload farming) — capped at 10 effective unless changelog diff shows real change (curator call, logged)

completeness 10 [collector: curator-verified only]
- we ran it OR confirmed recipe: trigger words, required models/nodes, workflow file present
- creator-authored docs alone score 0 here (they are context, not signal)

preview honesty 10 [collector: /images withMeta=true, garimpo v0.1]
- preview image meta.civitaiResources CONTAINS the versionId being scored (not just "meta present" — hostile #17)

lane fit 10 [collector: manual, rubric'd]
- does the entry actually serve its lane's job (persona consistency / pipeline completeness / nsfw fit); one-line reason logged

## composite (one rule, auditable)
- auto composite = sum of axes (0-100)
- displayed score 1-10 = derived (composite / 10, one decimal) — manual raw notes stay internal
- tiers on composite: S >= 85 AND external gate AND curator-verified; A >= 70; B >= 50; C < 50
- manual override ± 10, CANNOT cross a tier boundary, reason logged in curation log (auditable trail, not fiat)

## anti-farm block (receipts: hostile R1 #4)
- ratio floor 500 downloads; type-median default below it
- usage is the farm-resistant core
- completeness = verified only
- external mentions quality-gated
- override tier-locked
- merge detection: API checkpointType (Standard|Trained|Merge) where available; LoRA merges = curator flag, logged

## hardware
- vram badge (<=12 / 16 / 24+ GB) manual from community sources; filter, never score

## kill-lines
- base model 2+ generations stale → cap B
- zero verified docs AND zero comments → never S
- creator inactive (no version publishes 6m+ AND no curated-run confirmation) → stale flag
- license forbids commercial AND lane=ads → badge "personal-only"
- nsfwLevel X/XX → nsfw lane only
- mirror policy: workflow JSON only, NEVER zip archives (zips uninspectable — can embed explicit imagery = AUP backdoor, hostile #15); redistribution only when license fields allow, logged per entry

## model-side criteria (models.json)
- live benchmark position with board + date (benchmarks census; contested marked CONTESTED)
- open weights + license (H3 territorial landmine noted)
- ComfyUI support (native/extension/none)
- vram badge (manual)
- community consensus quotes (linked)
- our verdict line (english, one line)

## data honesty
- every stat: {value, window:"all-time", pulled_at}
- first batch labeled "no delta history"
- stats.period field in garimpo data = DISCOVERY window param, NOT stat window (mislabeling risk — hostile #2; schema comment mandatory)
