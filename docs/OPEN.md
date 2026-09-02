# OPEN — civitai-library state (2026-09-02 ~04:30)

## WHERE WE ARE
v1 site CONDEMNED by owner (see docs/FAILURE-ANALYSIS-R1.md). Rebuild in flight per docs/REBUILD-SPEC.md (binding).

## LANDED
- data/funnel/: 5786 deduped candidates / 12699 pulled / 42 slices (garimpo3.py; workflows+persona+nsfw+video lanes, community seeds chroma/biglust/lustify/araminta/anteros/bigasp pulled)
- data/funnel/scored.json: composite per stage w/ REAL anchors (PERSONA ratio_p75 .127 dl_p90 64k; NSFW .125/76k; MOTION .047/5.1k) — score.py
- data/funnel/clusters.json: 68 near-dup families, 82 cuts — cluster.py
- data/funnel/vision-shortlists.json: top-250 x {PERSONA,NSFW,MOTION} (anime-base pre-filtered; MOTION motion_era tagged modern/legacy)
- data/models.json: v2 enrichment done (17 entries, open_closed/vram_class/tradeoff/verdict_keep/license_note; "63" was inflated commit msg)
- docs/{FAILURE-ANALYSIS-R1,REBUILD-SPEC}.md committed

## FLYING (2 codex procs)
- codex site-v2 (pid 483141, /tmp/codex-site-v2.log): sitegen v2 rewrite — 6 stage JSON contracts + layers class, honest empty states, --demo flagged synthetic only
- codex vision probe (pid 483755, /tmp/codex-vision-probe.log): calibrating realism/anime/quality/nsfw classifier on 20 persona previews -> research/vision-probe-report.md

## NEXT QUEUE
1. vision probe lands -> BIG VISION PASS on shortlists (300-750 previews; label realism/quality/nsfwLevel; PERSONA realism grouping + NSFW subgrouping)
2. stage-fit + tradeoff curation pass on vision-labeled finalists (the lane-fit axis EXECUTED, finally)
3. codex site-v2 lands -> inject data/staged/<stage>.json -> build
4. MY browser grading every stage (hover=play, expand, nsfw-on, previews, fonts) — adversary w/ BLOCK power — owner sees ONLY after this gate
5. publish gh-pages ederson-shaw

## RULES LIVE
- commits: manager only, serial. nothing ships ungraded. /tmp is 100% FULL — use /home or stdin, never /tmp writes.
- owner defaults: nsfw ON, no hero, mouse-first click-minimal, fonts 18/20px+, open-source-leaning lens
