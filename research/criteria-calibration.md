# CRITERIA CALIBRATION — receipts (run 2026-09-02, manager personally, on the live 100-candidate pull)

command: python3 over data/candidates-{persona,workflows,nsfw}.json — distributions below, verbatim from stdout.

persona n=40: dl median 41,162 p25 22,212 p75 96,985 p90 224,437 max 352,057
  thumbs-ratio (dl>=500, n=40): median .085 p75 .138 p90 .177 max .285
  comments: median 0 p75 47 | usage-enriched 10
workflows n=30: dl median 29,926 p25 19,292 p75 41,756 p90 87,774 max 107,938
  thumbs-ratio (n=30): median .033 p75 .043 p90 .079 max .211
  comments: median 0 p75 60 | usage-enriched 10
nsfw n=30: dl median 39,302 p25 24,417 p75 94,561 p90 224,437 max 234,075
  thumbs-ratio (n=30): median .104 p75 .138 p90 .151 max .285
  comments: median 0 p75 0 | usage-enriched 10

## what these numbers killed or forced in v2
1. universal ratio anchor: DEAD — workflows lane ratio median .033 is 2.6x below persona .085; a single anchor mislabels every workflow. v2 anchors per-lane p75, recomputed per pull.
2. commentCount as scored axis: nsfw lane p75 = 0 (platform gating) — scoring it vs type-median gives nsfw structural zeros (hostile #11 confirmed by data). v2: lane-banded, 5pts, disabled where lane p75=0 with weight redistributed.
3. floor 500 dl: kept — irrelevant within this top-rated pull (all pass) but guards future Newest-sorted pulls; ratio without magnitude lets a 600-dl fluke outrank 200k workhorses.
4. magnitude anchor: lane p90 on log10 scale (persona/nsfw 224k vs workflows 88k — different economies, log-normalizes).
5. usage bands: top-10 walk sample showed 100+ / reactions 643 / meta_match true — bands 0/5/10/15 across 0, 1-29, 30-99, 100+ (cap-honest, no fake precision).
6. tier floors S>=70 / A>=55 / B>=35: S floor chosen so a no-external-mention entry (max 85 at launch) can still make A honestly but S demands the gate; rank bands top 10/25/40% keep every lane visually alive at launch (3-4 S per 30-40 entries).

caveat (honest): this pull is top-of-lane by construction (sort=Highest Rated) — anchors skew high. First Newest-sorted pull will stretch the low end; anchors recompute per pull by design, so the system self-corrects. Re-anchor check scheduled at first diverse pull.
