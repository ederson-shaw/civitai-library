# OPEN — state & queue

## state
P0 in progress — planning docs written, 4 librarian censuses + codex design running in background. no code yet BY DESIGN (assembly law: census before build).

## queue
- P0 close: digest censuses → CONVERGED-PLAN.md (final IA + rigid criteria + 100-idea list) → hostile review on the plan → only then build
- P1: garimpo tool (adapt top censused project) + api key + first pull + curation-layer data format
- P2: static site v1 (vanilla, lanes, cards, nsfw toggle, import guides)
- P3: polish + micro-interactions + hostile design review + mobile
- P4: publish under ederson-shaw (per-command GH_TOKEN, never gh auth switch) + handoff link

## blockers (need owner)
- civitai api key (offered) — required for nsfw pull + rate limits. drop at ~/.config/civitai/api.key or paste in chat.
- github account: RESOLVED — ederson-shaw exists, active, owner named it explicitly (session spec wins over owner.md preference).

## decisions log
- publish under ederson-shaw per explicit owner request this session (owner.md "prefer edersonff" overridden by live spec)
- static site on github pages, no server ever (sheol doctrine)
- organize by lane/use + task, NOT by model brand (owner hint)
- nsfw: toggle off default; public pages build carries ZERO explicit imagery (github bans pornographic CG content — receipt in research/legal-pages-policy.md); nsfw lane = full metadata + civitai link-out; optional "unlocked" full-preview build as downloadable artifact, never served from pages
- naming/curation manual, one-by-one, english
- garimpo = adapt existing censused tool, never from zero (assembly law)
- rank-keeper (unasked idea): scheduled re-validation script re-pulls stats so rankings never rot
