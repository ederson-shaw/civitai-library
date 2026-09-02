# REQUIREMENTS — civitai-library

owner asks verbatim PT (2026-09-01) + EN reading. nothing dropped, nothing merged.

## product
- personal library site, html, max quality as FLOOR ["tipo um site html... qualidade maxima entrega"]
- published on github (ederson-shaw) → github pages → final delivery = ONE github link ["entrega final seria 1 link github"]
- link back to civitai original on every entry
- everything user-facing in ENGLISH ["tudo em ignles"]
- fast workflow import from our site into comfyui
- lora/workflow RESULTS visible: preview images, navigate between examples
- header NSFW switch, sfw default
- format & order matter a lot ["formato e ordem importa mt"]

## lanes (the 2-3 focus)
- A personas: realistic AI influencers for social media
- B ads: full pipeline with those influencers — voice, image, video
- C nsfw: onlyfans & co (gated behind toggle)

## curation goals (his numbering)
1. expand candidate list
2. define priorities (asked TWICE — candidate ranking AND build priority)
3. good criteria — ours, rigid, NOT civitai's built-ins
4. easy explore interface
5. best community-defined workflows: best flows → for best models → most current → most quality per community

## data rules
- NOTHING from training dataset — live web research only ["n pegue nenhuma coisa do seu dataset"]
- civitai api key available from owner ["posso criar uma key se precisar"]
- existing projects already mine civitai: find + reuse ["tem projetos q fazem"]

## criteria open questions (owner raised, answer post-research)
score/time? comments? documentation quality? low vram?

## organization principles
- organize by QUALITY/USE, not by model brand ["o fator é n separar por modelo talvez mas por qualidade"]
- owner affections (changeable by evidence): z-image base/turbo, minimax-class video
- image-to-video is its own lane where audio/speech support exists: HD image first + defined speech + voice-first generation
- tabs: workflows AND models (model leaderboards per task)
- custom names, titles, rankings — manual one-by-one curation, our platform naming
- workflow age/recency visible
- categories separated: image gen? video? face? which models?
- define the best HANDOFF: top flows for everything, per category

## community research
- deep understanding: reddit, instagram, x.com mainly — opinions + best choices

## process
- subagents in parallel: (1) garimpo script research, (2) benchmarks/model research, (3) codex design ideas
- phases: planning → research → site; heavy parallel
- hard order: meta → quality → mechanisms
- ~100 organization ideas, micro-interactions, perfection bar ("precisa ser perfeito")
- fewer navigation clicks, instantly understandable best-per-category
