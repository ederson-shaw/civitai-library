# CRITERIA — DRAFT (rigid version lands post-research)

rule: criteria come from research evidence, not from my head. this draft fixes only the AXES; weights + kill-lines decided after census lands in research/.

## axes (draft)
community signal
- civitai: thumbs, downloads, comment count, rating — all time-decayed
- external: reddit/x mentions (cross-source validation)

freshness
- last updated < 90d? base model still current generation?

completeness
- workflow ships node list + model list? usage instructions present?

hardware
- vram tier: <=12GB / 16GB / 24GB+
- runtime per output where measurable

our manual layer (the part civitai cannot give)
- our score 1-10, one-line named justification
- tier S/A/B
- custom name + purpose line in english ("what this is FOR, one line")

preview honesty
- preview = actual workflow output, not creator's unrelated showcase?

## kill-lines (draft, confirm post-research)
- base model 2+ generations stale → cap at B
- zero documentation AND zero comments → excluded from S
- creator inactive 6m+ and flow reported broken → stale flag

## open questions for research to answer
- downloads vs thumbs ratio: what number separates good from gamed?
- does civitai api expose comment timestamps (engagement recency)?
- what does the community actually complain about in civitai discovery? (each complaint = one of our criteria)
- does nsfw content get systematically under-scored vs sfw (parity correction needed)?
- which benchmark sources are live and current (not dead 2024 pages)?
