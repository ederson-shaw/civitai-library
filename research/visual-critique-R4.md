# VISUAL CRITIQUE — R4 (2026-09-02)

Reviewer: zero-loyalty visual reviewer, using the same E13 protocol and judging only the four supplied 1440×900 screenshots at 100% zoom.

Score convention: 10 is strongest. For **noise**, 10 means quietest/least cluttered. For **tool-vs-marketing**, 10 means most convincingly an operational internal workbench. No DOM, dataset, or probe result is credited unless its effect is visible in the screenshots.

## Executive verdict

**NO-GO for daily owner use.** The Motion route is now visibly distinct, and the stack rail is a credible operational state. However, the default Persona surface still shows visibly anime/stylized imagery under the active `photoreal 20` filter and the stage promise `realism bases + identity`. The best-pick first frame also changes between visible states without a cue explaining why. Those are trust failures, not polish issues.

## Scorecard

| Shot | Density | Readability | Hierarchy | Noise | Tool-vs-marketing | Visible verdict |
|---|---:|---:|---:|---:|---:|---|
| 00 — Persona home | 7 | 8 | 7 | 6 | 9 | Strong workbench shell; default result category contradicts itself. |
| 01 — Motion stage | 7 | 8 | 8 | 6 | 9 | Stage transition is legible; the rail’s base-first context is ambiguous. |
| 02 — Persona card expanded | 8 | 8 | 8 | 7 | 9 | Good evidence depth; the best-pick preview and category evidence remain unstable. |
| 03 — Stack rail with selection | 8 | 8 | 9 | 7 | 10 | Strongest operational state; selected input, totals, and manifest agree. |

## Shot 00 — Persona home

**Density — 7/10.** The first viewport carries the stage header, search, four filter chips, a best-pick answer, four previews, and the execution rail. `pulled 1763 → kept 62` and `Select a base to start` add useful context without requiring a second screen.

**Readability — 8/10.** The primary decision text is comfortably scannable: `Persona`, `BEST PICK majicMIX sombre 麦橘唯美`, the reason line, and the card names all read at 100%. Mono metadata such as `PERSONA · 6` and the filter counts is appropriately secondary.

**Hierarchy — 7/10.** The intended path is clear—stage → search/filter → `BEST PICK` → candidate cards → plan rail. The semantic hierarchy breaks when the amber-selected `photoreal 20` chip sits above visibly stylized/anime-looking `OrangeChillMix` and `Niji semi realism` previews.

**Noise — 6/10.** The pills, image badges, counts, and catalog rows are individually defensible, but there are many labels before the owner has committed to a model. The rail repeats model names from the gallery, adding moderate visual load.

**Tool-vs-marketing — 9/10.** `LOCAL STAGED DATA`, pulled/kept counts, resource labels, and `ADD TO PLAN` make this read as a curation tool rather than a promotional gallery.

## Shot 01 — Motion stage

**Density — 7/10.** Four motion candidates fit into the first viewport with enough image, name, and tag content to compare them. The long recommendation line consumes horizontal space but communicates a concrete workflow.

**Readability — 8/10.** The stage identity is explicit in the visible pair `Motion` and `image-to-video + movement`. The best pick `Hunyuan 12GB vram @1080p w/Upscale + Framegen + Wildcards` is dense but legible, and the `MOTION` image badges anchor the card category.

**Hierarchy — 8/10.** This is a real improvement over the former duplicate shot: the active `02 Motion` tab, Motion heading, Motion-specific best pick, and motion cards establish a coherent left-to-right scan. The right rail still begins with `BASE` and `Select a base to start`, which makes the stack’s base-first entry state visible even while the Motion catalog is being browsed.

**Noise — 6/10.** Technical tags such as `max quality`, `Flux.1 D`, `fastest`, and `low vram` are useful, but the first card’s multi-line name plus several badges makes the row visually busy.

**Tool-vs-marketing — 9/10.** `vram`, `1080p`, `Framegen`, `Wildcards`, and the `ADD TO PLAN` rail provide operational selection evidence. The visual assets are present, but the language is decisively workflow-oriented.

## Shot 02 — Persona card expanded

**Density — 8/10.** The expanded first card exposes a `PURPOSE` section while the grid still retains four candidates and the rail remains visible. This gives the owner more decision evidence without losing the comparison context.

**Readability — 8/10.** `BEST PICK`, the selected card’s `USE` block, tags, and the beginning of `PURPOSE` are readable. The narrow card column forces long wrapping, but the text remains scannable rather than truncated.

**Hierarchy — 8/10.** The eye can follow recommendation → preview → name → `USE` evidence → `PURPOSE`. The explicit `Select a base to start` empty state keeps the expanded card from being mistaken for an already-planned item. The same category mismatch and changing best-pick frame reduce trust in that otherwise good hierarchy.

**Noise — 7/10.** The expanded content is information-dense but organized. The visible separators and restrained amber/cyan accents keep it quieter than a conventional card matrix.

**Tool-vs-marketing — 9/10.** `PURPOSE`, resource tags, `ADD TO PLAN`, and the empty execution state give the card a clear internal-catalog/workbench character.

## Shot 03 — Stack rail with selection

**Density — 8/10.** The rail communicates selection, three remaining slot categories, resource totals, and a downloadable file within a narrow column. The gallery remains visible enough to verify the amber-outlined source card.

**Readability — 8/10.** The most important rail text is clear: `LIVE`, `SELECTED INPUTS`, `BASE`, `majicMIX sombre 麦橘唯美`, `VRAM TOTAL 6 GB`, `DISK TOTAL 2033 MB`, and `DOWNLOAD MANIFEST`. The repeated base name is acceptable because it appears in summary and slot contexts.

**Hierarchy — 9/10.** The amber `SELECTED INPUTS` panel, amber card outline, `BASE` slot, totals, and manifest form a strong confirmation chain. `LAYERS`, `MOTION`, and `VOICE` visibly communicate the remaining build slots.

**Noise — 7/10.** This is compact but not quiet: status, slot headings, totals, a filename, path, and `COPY ALL` all compete for rail space. Each item supports execution, so the density is justified.

**Tool-vs-marketing — 10/10.** `LIVE`, `COPY ALL`, `open file link ↗`, `majicmixSombre_v20.safetensors`, and `models/checkpoints/ · 2033 MB` are unambiguous operational evidence.

## R3 blocker audit

### Persona anime in the photoreal default — NOT VISUALLY DEAD

Shot 00 visibly presents the stage as `realism bases + identity` with the active amber filter `photoreal 20`. In that same result set, the `OrangeChillMix` preview is an anime-styled close-up and `Niji semi realism` is a visibly stylized/anime-looking character image. The adjacent `style: anime 42` chip is not the selected amber chip, so the result imagery does not visually agree with the current filter state.

Shot 02 repeats the same visible contract: `photoreal 20` remains active under `realism bases + identity`, while `OrangeChillMix` and `Niji semi realism` remain visibly stylized. The expanded best-pick card also shows a silver-haired, stylized character image, which further weakens the realism claim.

Conclusion: the blocker is still present in the rendered evidence. A probe reporting zero anime-classified frames is not enough to pass a screenshot-only review when the images on screen still read as anime/stylized.

### P2 unstable best-pick first frame — NOT RESOLVED AND NOT LEGIBLE

In Shot 00, `majicMIX sombre 麦橘唯美` displays a realistic brunette portrait. In Shot 02, the same named best-pick card displays a materially different silver-haired character in a black outfit; Shot 03 carries that latter image into the selected state. No preview index, carousel position, alternate-frame label, hover/state cue, or other explanation is visible. `BEST PICK` and `USE` describe the item, not the reason its evidence changed.

Conclusion: the first frame is not visibly stable, and the change is not legible as an intentional alternate preview. P2 remains open.

## New defects only

**None identified.** The former duplicate Motion capture is visibly replaced by a Motion-specific surface, and the `Select a base to start` rail state is consistent with a base-first stack. The Persona gate and unstable best-pick frame are carried above as surviving audit items, not reclassified as new defects. No new P0, P1, or P2 defect is visible in these captures.

## Final judgment

The Motion duplicate is visibly fixed, and Shot 03 is a strong operational workbench state: selection, `6 GB` VRAM, `2033 MB` disk, and the manifest reinforce one another. The default Persona experience still fails the visible category promise, and the best-pick evidence changes without explanation.

**NO-GO for daily owner use.** Resolve the photoreal gate in the rendered gallery and make the best-pick preview stable or explicitly labeled before handoff.
