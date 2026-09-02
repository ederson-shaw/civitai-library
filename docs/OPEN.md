# OPEN — state & queue

## state
P1 in progress — garimpo v0 SHIPPED + first real pull landed: 100 candidates on disk (persona 40, workflows 30, nsfw 30 — key delivered by owner, verified working, preview 200s). P0 closing in parallel: hostile review R1 running (bg_6535ed4d), UX census retrying (bg_4fbb1198). CONVERGED-PLAN.md next when both land.

## queue
- P0 close: hostile findings → fix criteria/plan → CONVERGED-PLAN.md (final IA from ux-census + codex 100 ideas + first-60-seconds; criteria final; model leaderboards format) → hostile round 2 on converged plan
- P1 rest: curation layer (manual names/tiers/scores on the 100 candidates → curated.json) + rank-keeper stub
- P2: static site v1 (vanilla, lanes, cards, nsfw toggle, import guides)
- P3: polish + micro-interactions + hostile design review + mobile
- P4: publish under ederson-shaw (per-command GH_TOKEN, never gh auth switch) + handoff link

## blockers (need owner)
- none — key delivered. owner actions pending: none.

## decisions log
- publish under ederson-shaw per explicit owner request this session (owner.md "prefer edersonff" overridden by live spec)
- static site on github pages, no server ever (sheol doctrine)
- organize by lane/use + task, NOT by model brand (owner hint)
- nsfw: toggle off default; public pages build carries ZERO explicit imagery (github bans pornographic CG content — receipt in research/legal-pages-policy.md); nsfw lane = full metadata + civitai link-out; optional "unlocked" full-preview build as downloadable artifact, never served from pages
- naming/curation manual, one-by-one, english
- garimpo = adapt existing censused tool, never from zero (assembly law)
- rank-keeper (unasked idea): scheduled re-validation script re-pulls stats so rankings never rot
