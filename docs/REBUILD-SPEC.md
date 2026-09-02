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

## EVERY STAGE = DECISION MATRIX
Entries grouped and labeled by trade-off, owner's literal model ("workflow pouco vram e esse para maior qualidade e esse para x y z"):
- chips per entry: `low vram` | `max quality` | `fastest` | `purpose: X` (from curation, not guessed)
- matrix row per capability need (e.g. MOTION: talking-with-audio | silent short clip | long take) — pick need -> see 2-4 vetted options with trade-offs labeled
- open/closed badge on every entry + every models-tab model (open-source-leaning, not exclusive)

## NSFW
ON by default (owner m0124). No toggle ceremony to see the owner's own library. Mature entries render like everything else. Blur ONLY on explicit imagery thumbnails until hover/expand (hover = consent by interaction), never on names/text/data.

## MICRO-INTERACTIONS — MANDATORY (not optional polish)
- hover on any card with video preview = autoplay video immediately
- hover on card with gallery = scrub through gallery frames (mousemove across card scrubs)
- expand-in-place: card click expands to full detail INLINE (no page navigation for comparing)
- scores visible-why: click score -> popover with breakdown (community anchors + our verdict + pulled date)
- filters inline above grid, live chip counts, URL state
- zero hero, zero marketing copy, zero "welcome to" text anywhere

## DENSITY & READABILITY (owner: "tudo é dificil de ler, pequeno")
- base font >= 16px, entry names >= 18px, high contrast
- grid: preview-dominant cards, 1 line of name + 1 line of purpose, chips row — everything else on expand
- minimal scroll per stage: sticky stage nav + filters, virtualize or page if >60 entries
- minimal clicks: any entry's essentials visible in <=1 click from stage view

## DATA CONTRACT (funnel -> filter -> render)
- entries tagged: stage(s), layer_class, tradeoff labels, stacks_on, open/closed, nsfw_level, vram_class, previews[] (images + VIDEOS), gallery, usage stats, our verdict + why
- transparent funnel: header per stage shows "pulled N -> kept M" + cut panel link (what was cut and why — the honesty panel)
- previews mandatory: entry without a working preview = cut from render (no blank cards)

## VERIFICATION GATE (before owner ever sees it)
1. I grade every stage in a real browser: hover=play works, scrub works, expand works, nsfw renders default-on, no empty previews, readable at 100% zoom
2. codex VISION pass on finalist previews: realism-vs-anime check per PERSONA entry, quality check, nsfwLevel sanity
3. hostile review with BLOCK power on the rendered site (not the docs)
4. owner's predicted complaint written BEFORE handoff; if my prediction is "X is hard to read" and X exists, rebuild again
