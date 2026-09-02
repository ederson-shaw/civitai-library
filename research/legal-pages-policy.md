# LEGAL — github pages adult content + civitai access (researched live 2026-09-01)

## github sexually obscene content policy
source: https://docs.github.com/en/site-policy/acceptable-use-policies/github-sexually-obscene-content
- pornographic content NOT allowed, explicitly including "computer-generated images"
- carve-out: nudity/sexuality in artistic/educational/journalistic context MAY be allowed; "in some cases a disclaimer can help"; github may require opt-in before viewing
- pages inherits AUP: https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features + pages limits doc names "sexually obscene content" restriction explicitly

## decision (binding for site architecture)
- NSFW lane SHIPS on the public pages build as: full curation metadata (custom name, purpose, tier, our score, stats, vram, freshness, import guide, civitai link) + NO explicit imagery loaded, hotlinked or cached
- non-explicit nsfw-adjacent previews (portrait/fashion level) allowed only blurred + behind the header toggle (opt-in)
- explicit previews live on civitai behind THEIR auth — our card links out
- optional later: an "unlocked" full-preview build distributed as downloadable artifact (NOT served from github pages) if owner wants it

## civitai access legality
source: https://civitai.com/content/tos (2026-08-26 version) §11.4
- scraping/data-mining banned EXCEPT "through interfaces we expressly provide for automated access, such as our public API or official MCP server... accessed with your own valid credentials and within any applicable rate limits"
- => garimpo via public REST API + owner key = explicitly authorized use

## unresolved (post hostile R1 #15 — probes queued, decisions pending)
- CDN re-display + sig expiry: image.civitai.com URLs are signature-shaped; expiry behavior UNPROBED (garimpo v0.1 probe: re-fetch same model ids, diff image URLs). Local caching of thumbnails FORBIDDEN until this section carries an answer.
- mirror policy (DECIDED): workflow JSON extracted only, never zip archives (uninspectable, can embed explicit imagery = AUP backdoor); redistribution gated on license fields per entry, logged.
- "unlocked" nsfw build: github RELEASES are still github-hosted under the same AUP — "not served from pages" is NOT a safety line. Any full-preview nsfw build must live off-github entirely (owner host/drive) or not exist. OFF-GITHUB or NOTHING.
- textual nsfw lane metadata on pages: names/purpose lines linking to explicit civitai pages — gray zone under AUP "pornographic content" carve-outs; mitigation = professional wording, educational curation framing, opt-in toggle default off. Residual risk accepted until owner rules.

## civitai api facts already confirmed by official docs (detail census lands in civitai-api-census.md)
source: https://developer.civitai.com/site/ + /site/reference/images + /site/guide/authentication
- public REST api v1: models, model-versions, images, articles, collections, creators, tags, users
- /images returns full generation meta (prompt, sampler, resources with modelVersionIds + lora weights) — preview-with-recipe is pullable
- bearer token; public endpoints anonymous-ok but authed callers see up to their browsing level (nsfw needs key); anonymous capped at sfw-ish levels
- CORS open on public endpoints; "Never embed a token in client-side code" → ALL pulls are build-time in the garimpo script, static site ships only json+html
- edge cache 5min on public endpoints; cursor pagination (page*limit<=1000); popular-model image filtering can hit cloudflare 30s — walk cursors instead
