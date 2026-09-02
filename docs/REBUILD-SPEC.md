# REBUILD SPEC v2 — binding (owner messages m0119 m0123 m0124 m0126 m0127 + FAILURE-ANALYSIS-R1)
Internal tool. Not a public site. Every violation of this spec = rebuild rejected before owner sees it.

## WHAT IT IS
The owner's workbench for creating a realistic AI influencer end to end: persona -> movement -> speech -> ads -> nsfw. Density over polish, decision over browsing, previews over text.

## IA — PIPELINE STAGES (primary nav, top, sticky)
1. PERSONA — total-realism bases + identity/persona LoRAs (realistic humans, NOT anime; anime content only if tagged as deliberate style choice, never as default wave)
2. MOTION — image-to-video / animation (wan, ltx, hunyuan, minimax class; movement quality)
3. SPEECH & VOICE — talking heads, lip sync, TTS voices, voice cloning
4. CAMERA & ANGLE — camera control, posing, angle/perspective workflows
5. ADS ASSEMBLY — full ad pipelines with the persona (product shots, UGC, copy-to-video)
6. NSFW / OF — explicit lane, full parity with every other stage
+ ENHANCEMENT LAYERS — a CLASS not a stage: stackable LoRAs/workflows (skin detail, lighting, motion physics, anatomy fixes, upscale). Every layer entry carries stacks_on: [stage(s), base models]. The stack metaphor: base pipeline + N layers = final look.

## EVERY STAGE = ANSWER-FIRST PICK
Entries grouped and labeled by trade-off, owner's literal model ("workflow pouco vram e esse para maior qualidade e esse para x y z"):
- chips per entry: `low vram` | `max quality` | `fastest` | `purpose: X` (from curation, not guessed), with zero-count chips hidden
- each stage leads with one compact best-pick answer and purpose; visual-class chips expose deliberate alternatives without mixing them into the default realism view
- open/closed badge on every entry + every models-tab model (open-source-leaning, not exclusive)

## NSFW
ON by default (owner m0124). No toggle ceremony to see the owner's own library. Mature entries render like everything else, with an NSFW marker and no thumbnail blur.

## MICRO-INTERACTIONS — MANDATORY (not optional polish)
- hover on any card with video preview = autoplay video immediately
- hover on card with gallery = auto-advance gallery frames every ~1.2s; the last-hovered gallery keeps cycling until another card is hovered
- expand-in-place: card click expands to full detail INLINE (no page navigation for comparing)
- scores visible-why: click score -> popover with breakdown (community anchors + our verdict + pulled date)
- filters inline above grid, live chip counts, URL state
- zero hero, zero marketing copy, zero "welcome to" text anywhere

## DENSITY & READABILITY (owner: "tudo é dificil de ler, pequeno" + m0144 "fonte maior e menos ruido")
- base font >= 18px, entry names >= 20px, high contrast, generous line height
- grid: preview-dominant cards, 1 line of name + 1 line of purpose, chips row — everything else on expand
- minimal scroll per stage: sticky stage nav + filters, virtualize or page if >60 entries
- MOUSE-FIRST, CLICK-MINIMAL (owner m0144: keyboard shortcuts NOT wanted, fewer clicks IS the law):
  - hover reveals (preview plays, score-why popover, chips yield) — hover = free information, no click charged
  - click only commits (expand, toggle layer into stack, download, copy)
  - nothing essential is 2 clicks deep: stage -> entry essentials = 1 click; full detail = expand-in-place, never a page navigation
  - no keyboard shortcuts required anywhere (may exist as bonus, never as the path)

## DATA CONTRACT (funnel -> filter -> render)
- entries tagged: stage(s), layer_class, tradeoff labels, stacks_on, open/closed, nsfw_level, vram_class, previews[] (images + VIDEOS), gallery, usage stats, our verdict + why
- transparent funnel: header per stage shows "pulled N -> kept M" + cut panel link (what was cut and why — the honesty panel)
- previews mandatory: entry without a working preview = cut from render (no blank cards)

## VALUE / NOISE / SPEED (owner m0140: "vá mt além do generico, valor em cada detalhe + remover ruido + ser rapido")

### Flagship non-generic: STACK BUILDER
The pipeline made operational: owner toggles 1 base + N layers + 1 motion + 1 voice -> right rail computes LIVE: total VRAM (sum), total disk (sum), complete download manifest (file + folder + link + size rows, exact civitai VERSION links), copy-all button (plain text, paste-ready for a downloader). The library stops being "a list to read" and becomes "a plan to execute". This is the iceberg under his "camadas de melhoramento".

### Value in every detail (each must change a decision or it dies)
- answer-first stage open: each stage leads with one compact best-pick row ("talking + audio on 12GB -> THIS, here is why in one line"), followed by previews
- verdict lines comparative + consequential ("beats X on skin texture, loses on hands, runs 2x slower on 12GB") — "great model" = fired sentence
- every civitai link opens the EXACT VERSION we vetted, never the model page
- file sizes on every download row (disk planning), VRAM badge in his GPU classes (8/12/16/24)
- "verified" date on every verdict (trust has a timestamp)
- score popover = full math (anchors used, each axis, pulled date) in 1 click
- cut panel answers "why isn't X here" with numbers, in 1 click
- NSFW level shown as the precise number (his default-on world, no euphemisms)

### Noise removal (kill list, enforced in review)
- banned words in UI copy: curated, premium, discover, explore, showcase, welcome, "our", seamless, powerful
- banned chrome: footers, onboarding overlays, theme toggle, hero, any marketing sentence, breadcrumbs
- max 3 visible numbers per card (score, downloads, age) — everything else popover
- no category rendered with <3 entries (merge or cut, never a lonely grid)
- near-duplicate style families (funnel will have dozens): cluster, keep best-1, note "cut 47 similar, kept by ratio+freshness"
- entries without working previews = cut from render (no blank cards, ever)
- zero dead clicks: every chip carries live yield count; zero-yield chips disabled

### Speed
- one JSON per stage, prefetched in parallel at load (<200KB each), everything client-side after
- any filter/search interaction <50ms (in-memory, no re-fetch)
- hover-play preloads FIRST video segment only, never full gallery
- animations transform/opacity only, none on the critical path
- as-you-type search, results <=50ms
- mouse does everything; no keyboard path required (click-count is the metric, not keystrokes)

## VERIFICATION GATE (before owner ever sees it)
1. I grade every stage in a real browser: hover=play works, scrub works, expand works, nsfw renders default-on, no empty previews, readable at 100% zoom
2. codex VISION pass on finalist previews: realism-vs-anime check per PERSONA entry, quality check, nsfwLevel sanity
3. hostile review with BLOCK power on the rendered site (not the docs)
4. owner's predicted complaint written BEFORE handoff; if my prediction is "X is hard to read" and X exists, rebuild again
