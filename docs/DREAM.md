# DREAM — civitai-library

meta: one link that replaces civitai digging — the curated best LoRAs + workflows for AI-influencer personas, ad pipelines (image+video+voice), and NSFW/OF. always current. always importable.

## destination
person with the link finds THE right workflow for their use in under 60 seconds, previews real results, imports into ComfyUI in one move. zero civitai search, zero dead flows, zero reddit rabbit holes.

## callers
- eder picking flows per new influencer/ad project (weekly)
- friends/collaborators he hands the link to (know nothing about civitai)
- future eder, months later, needing "what's current NOW"

## dream
THE library people link in AI creator circles before opening civitai. rankings stay honest because a re-validation script re-pulls stats on a schedule.

## nightmare
stale awesome-list: dead links, updated 8 months ago, no previews, civitai scores copy-pasted, nobody opens it twice.

## ladder
- P0 planning + live census (this session) → converged plan + hostile review
- P1 garimpo tool (adapt top censused project, never from zero) + first curated batch (~50 entries, 3 lanes)
- P2 static site v1: lanes, cards, previews, nsfw toggle, import guides
- P3 polish: micro-interactions, hostile design review, mobile
- P4 publish github pages (ederson-shaw) + handoff link

## sad paths
- civitai api changes / rate limits → cache layer + key + respect limits
- github pages vs adult content → OWNER OVERRIDE 2026-09-01: full nsfw previews allowed (blur until toggle, sfw default view); hosting risk owned by owner, fallback = rehost on another provider. Legal analysis preserved in research/legal-pages-policy.md as record.
- key revoked → sfw garimpo continues, nsfw degrades gracefully
- flows go stale (base model deprecated) → freshness decay in score + stale flag
- civitai cdn hotlink breaks → CDN sig-expiry probe queued (garimpo v0.1); local caching ONLY after license analysis lands in legal file (currently unresolved — do not cache)
- rank rot → rank-keeper script re-validates on schedule; snapshots from day one

## simulation
marcus, ad guy, phone, 22:47. opens link. taps "ads lane". first card: S-tier "product shot → talking spokesperson", runs on his 16GB card. swipes 3 previews. taps import → workflow json + model list + one command each. 6 minutes, no civitai account. he texts the link to his designer.

## gaps (not absorbed from spec)
- final display format: owner explicitly undecided → 100-idea converge post-research
- final model picks: benchmarks pending (owner likes z-image + minimax-class video — verify, not assume)
- nsfw hosting approach: pages policy check this session
