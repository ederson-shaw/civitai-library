# CRITERIA — v1 (evidence-based; sources: research/civitai-api-census.md, research/community-sources.md, research/model-benchmarks.md)

owner's four open questions, answered with evidence:
- nota/tempo? YES → engagement decayed by time (period stats + recency), never raw all-time counts (complaint: download counts ≠ usage, stat windows mislabeled)
- comentarios? YES → commentCount + engagement-ratio axis (proxy for real usage)
- documentação? YES → completeness axis (usage instructions, trigger words, workflow file, model list)
- low vram? YES → hardware axis + vram tier badge (community: 6/8/12/16/24+ GB are the real splits; Z-Image 6-16GB, H3 12-42GB per benchmarks census)

## scoring (workflow/LoRA entries) — 0-100, weights fixed v1
community engagement (30)
- thumbsUp/downloads ratio (period > all-time when available)
- commentCount relative to type-median
- image reactions on preview posts (likeCount, heartCount from /images)

external validation (20)
- reddit/x mentions found in community census sources; recency-weighted
- S-tier REQUIRES ≥1 external mention (kills civitai-only hype)

freshness (15)
- version lastUpdated <90d full points / <180d partial / else decay
- base model generation currency (benchmarks census: what's current NOW)

completeness (15)
- usage instructions present
- trigger words listed
- workflow file attached (Workflows type) or recipe embedded in preview meta
- required models/nodes named

hardware (10)
- vram tier: <=12 full / 16 partial / 24+ minimal
- runtime class where known

preview honesty (10)
- preview carries generation meta (API: meta present = real output, not showcase)

manual layer (owner law: names/rankings are OURS, one by one, english)
- our score 1-10 with one-line named justification
- tier S/A/B
- custom name + purpose line ("what this is FOR, one line")
- manual override ±15, must cite reason

## kill-lines
- base model 2+ generations stale → cap B
- zero docs AND zero comments → never S
- creator inactive 6m+ AND broken reports → stale flag
- license forbids commercial AND lane=ads → badge "personal-only"
- nsfwLevel X/XX → nsfw lane only, never in sfw view even blurred-heavy

## community complaints → criteria map (each complaint = one criterion, receipts in community-sources.md §2E)
1. downloads ≠ usage → rank on engagement ratios + period stats; re-pull via API (rank-keeper)
2. hype asymmetry hides good models (ANIMA case) → external-validation axis mandatory for S
3. popularity sort biases 12GB checkpoints → per-type normalization (LoRAs ranked among LoRAs)
4. merge clutter ("base with a lora baked in") → merge penalty unless doc'd value; LoRA-first era
5. civitai search broken (4 github issues) → our ranks never inherit civitai sort order
6. stats frozen → pulled_at timestamp on every stat + rank-keeper re-validation
7. tagging broken → our own lane taxonomy, manual assignment
8. monetization revolt / creators leaving → mirror workflow json locally (license permitting) + license field surfaced
9. cost opacity (buzz/early-access) → entry field: cost status (free / early-access / buzz)
10. stat-window mislabeling → explicit period param on every pull

## model-side criteria (models.json leaderboards)
- live benchmark position with board + date (benchmarks census: arena.ai, artificialanalysis — NEVER dead boards; Magic Hour marked stale)
- open weights status + license (H3 territorial landmine flagged)
- ComfyUI support (native/extension/none)
- vram tier
- community consensus quotes (linked)
- our verdict line (english, one line, named)

## data honesty rules
- every stat carries pulled_at + period
- contested rankings marked CONTESTED (t2v #1 splits: Wan 3.0 vs Gemini Omni vs minimax-h3)
- owner-affection models (z-image, minimax) verified not assumed: z-image = budget/fast lane, minimax-h3 = #1 i2v arena + best open video, license landmine noted
