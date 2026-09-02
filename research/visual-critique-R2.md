# VISUAL CRITIQUE — R2 (2026-09-02)

Reviewer: zero-loyalty visual reviewer, applying the same E13 protocol and binding priorities used in `research/visual-critique-R1.md`.

Scope: the four supplied 1440×900 screenshots, judged at 100% zoom and only on what is visible. No hidden behavior earns credit.

## Executive verdict

The rebuild is materially better than R1, but it is **not ready to hand to the owner**.

The four claimed fixes land unevenly:

- **P0-1, first-viewport compression:** landed, but only just in Shot 00/01. The stage header is compact and the preview row now enters the viewport, although only the upper part of the cards is visible. Shot 02/03 are materially stronger because the cards start much higher.
- **P0-2, Persona realism gate:** failed. The default `all 20` view still visibly leads with anime/stylized imagery and includes a card tagged `Anima`. The presence of a `style: anime 42` chip does not make those results look gated behind that choice while `all` is active.
- **P0-3, computed Stack builder:** landed. The empty state is explicit and actionable, and Shot 03 visibly becomes a selected, live plan with totals and manifest controls.
- **P0-4, typography:** mostly landed. Entry names and comparison labels are now large, wrapped, and readable; primary names no longer visibly ellipsize. Secondary utility text is still small, but the previous typography failure is substantially reduced.

The remaining Persona mismatch is a trust failure, not a taste issue. Shot 03 also introduces a data-integrity-looking failure: a selected base produces `VRAM TOTAL 0 GB`, while `DISK TOTAL 2033 MB` has no visible manifest row backing it. Overall: **6/10 — NO-GO**.

## Shot 00 — home

### Fix verification

**P0-1: partially successful.** The header is now a compact working band: `Persona`, `realism bases + identity`, and `pulled 1763 → kept 62` sit on one line of information. There is no visible collision. The first preview row begins at about y619, so previews do enter the 900px viewport. However, the search/filter block and the comparison matrix still consume roughly the first 606px of content; only the upper image portions and the very beginning of the card names are visible at the bottom. This meets the literal “previews reach the first viewport” test more than it achieves a preview-first composition.

**P0-2: failed.** The active-looking `all 20` view visibly includes non-realism material. The third preview is an overt anime close-up, the fourth is stylized/fantasy-like, and the matrix includes `Niji semi realism` tagged `Anima`. `style: anime 42` is exposed as a chip, but the results do not read as anime being behind a deliberate style choice; `all` is the visible selection while anime is already in the default wave.

**P0-3: successful for the empty state.** The rail now says `Select a base to start`, followed by `ADD TO PLAN` and a `BASE` catalog. It no longer falsely claims to be live or renders the old `No vetted input loaded` dead end. The catalog is visibly subordinate to the empty plan.

**P0-4: mostly successful.** Card names, matrix options, and rail candidates are visibly around the requested 20px scale and wrap instead of truncating. `Urban Samurai | v0.14 | Clothing LoRA` is long but fully exposed across multiple lines. The small `NEED`, `PERSONA`, and filter/status labels remain utility-sized, which is acceptable only because the main decision text is now readable.

### Axes

**Density — improved, still middling.** The compact header recovers a meaningful amount of vertical space and the first row is no longer completely below the fold. But a 273px comparison block sits above the cards, and the bottom of the viewport shows images without enough of the card verdict to make a decision. The rail remains a large persistent column even when no base is selected.

**Readability — pass with caveats.** The major names and the one-line counter are clear at 100%. Long matrix names wrap cleanly. `fastest 0`, `low vram 0`, and `max quality 0` are visibly disabled but still low-contrast; they are readable, not comfortable.

**Hierarchy — improved, but the matrix still wins over the evidence.** The page now gets to actual media, and the empty rail gives a clear next action. The comparison strip remains visually taller and more structured than the candidate cards, so the interface still asks for analysis before showing enough evidence.

**Noise — moderate.** The top status line, stage nav, pulled/kept counter, search label, five chips, matrix label, score labels, and repeated `BASE` pills are all defensible individually. Together they still make the upper half feel instrumented before it feels useful. The three zero-result chips are especially close to dead weight.

**Internal tool or marketing site? — clearly an internal tool now.** The compact stage band and explicit plan action reduce the previous landing-page feel. The gallery-like images and score treatment still add a catalog/showcase note, but the tool register is dominant.

### Shot 00 verdict

**6/10.** The shell is now usable and the empty-state rail is honest, but the default Persona result set visibly contradicts the stage promise and the first viewport still gives the cards too little decision surface.

## Shot 01 — Persona stage

### Fix verification

The same fixes are visible here as in Shot 00: the one-line `pulled 1763 → kept 62` header treatment is present, previews reach the lower part of the first viewport, `all 20` and `style: anime 42` are visible, and the rail says `Select a base to start`.

**P0-2 remains failed for the same reason.** The visible default wave is not realism-only: the anime close-up and the `Niji semi realism` / `Anima` entry are plainly present without a visible active anime selection.

**P0-4 remains mostly successful.** The entry names and comparison text are substantially more readable than R1, with no visible primary-name ellipsis.

The important additional observation is that Shot 01 is visually indistinguishable from Shot 00 at the supplied resolution. Both show the same active `01 Persona` nav item, same counts, same matrix, same previews, and same empty rail. If this is meant to demonstrate a transition from home into the Persona stage, the screenshot provides no state evidence beyond the already-active nav underline.

### Axes

**Density — improved from R1, but not yet dense enough.** The first row is technically present, but most of the visible workspace before it is search, filters, and matrix chrome.

**Readability — pass with caveats.** Primary text is now comfortably scannable. The muted mono labels and disabled filter states still look like secondary texture rather than strong evidence.

**Hierarchy — state-legibility failure.** The compact header is no longer a hero, but the screenshot does not communicate a distinct Persona-stage state because it is the same visible state as Shot 00. The active nav alone is too weak to prove a stage transition.

**Noise — moderate-high.** Repeated orientation signals are less bulky than in R1, but they still consume space without adding a visibly different result state. `all 20` beside `style: anime 42` is also semantically noisy when the content itself includes anime.

**Internal tool or marketing site? — tool shell, but static-looking.** It reads as an internal catalog/workbench surface, yet the identical state makes it look like a static mockup rather than a stage that has just loaded or changed.

### Shot 01 verdict

**5/10 for visible state legibility.** The typography and shell fixes are present, but this shot does not prove that a distinct Persona-stage state exists, and the Persona defaults still violate the lane promise.

## Shot 02 — Persona card expanded

### Fix verification

**P0-1: successful in this state.** The search and matrix sit immediately below the sticky nav, and the preview cards begin around y403. Four image-first cards, their names, metadata, scores, and stack actions all enter the first viewport. This is the first supplied shot that genuinely feels preview-forward.

**P0-2: failed, with one sub-fix successful.** The visible wave still contains an overt anime close-up and a stylized/fantasy-like fourth image; `Niji semi realism` carries the `Anima` tag. The `style: anime 42` chip is visible, but `all 20` is the active-looking chip, so the screenshot does not support the claim that anime is only shown after an explicit style choice. On the positive side, missing fields are now omitted: the cards no longer render the old `Purpose not staged`, `STATUS NOT STAGED`, or `VRAM —` placeholders. That omission improves trust even though the source curation is still wrong.

**P0-3: successful empty plan.** The rail clearly communicates the pre-selection state with `Select a base to start`, then moves into the `BASE` options. It is no longer pretending that an empty catalog is a computed plan.

**P0-4: successful for the primary surface.** Names such as `majicMIX sombre 麦橘唯美`, `Experience`, `OrangeChillMix`, and `Niji semi realism` are large and readable. The card descriptions are legible, and names are wrapped rather than ellipsized.

### Axes

**Density — good.** The four cards are visible as actual decision objects: image, name, tag, score, and action. The matrix is compressed enough that it no longer completely blocks the evidence. The right rail still uses substantial height for a catalog that is empty as a plan, but the left workspace is now efficient.

**Readability — good, not complete.** The card names and descriptions are the right scale. Long names wrap naturally. The `PERSONA` sublabels and `ADD` actions in the rail are smaller than the main names, and the repeated row rhythm makes them less prominent, but they remain legible.

**Hierarchy — strongest of the empty states.** Preview → name → metadata → score → `ADD TO STACK` is a coherent scan path. The missing purpose/evidence on the third and fourth cards leaves those cards visibly sparse, though that is preferable to fake placeholder content. There is still no explicit comparative verdict or selected relationship between a card and the empty rail.

**Noise — moderate.** The matrix, filter chips, image `BASE` pills, scores, and rail catalog all remain visible, but their order is now understandable. The inconsistency between richly described first cards and nearly empty `OrangeChillMix` / `Niji semi realism` cards is a new curation-quality signal: the grid looks partially vetted rather than intentionally concise.

**Internal tool or marketing site? — internal tool with catalog leakage.** The expanded card actions and empty plan make the workflow real. The large image row and uniform score styling still make it resemble a model gallery more than a strongly opinionated curation matrix.

### Shot 02 verdict

**7/10.** This is a real improvement in density and card anatomy. It is held back by the wrong default visual category, uneven evidence depth between cards, and the absence of a visible selected decision.

## Shot 03 — Stack rail with selected base

### Fix verification

**P0-1: successful.** The card row is already visible and the selected card has a clear amber outline. The content is compact enough to show the card and the active rail together.

**P0-2: failed.** The selected base is visually realistic enough to support the lane, but the surrounding default wave still includes anime/stylized entries, including the visible `Niji semi realism` card tagged `Anima`. Selecting one good base does not repair the default result set.

**P0-3: successful, and strongest proof of the fix.** The rail now has a coherent active state: green `LIVE`, an amber `SELECTED INPUTS` block containing `BASE` and `majicMIX sombre 麦橘唯美`, a pinned `BASE` plan slot, empty `LAYERS`, `MOTION`, and `VOICE` slots, `VRAM TOTAL` / `DISK TOTAL`, and `DOWNLOAD MANIFEST` with `COPY ALL`. The corresponding card is outlined and its action changes to `REMOVE FROM STACK`. This is visibly a computed plan, not the old catalog-only rail.

**P0-4: successful.** The selected input, base slot, totals, and card name are all readable at 100%. There is no visible truncation of the primary base name.

### Axes

**Density — good plan density, with a conspicuous hole.** The selected input and empty slots are scannable in a narrow rail. However, the manifest heading is followed by a large blank region before `ADD TO PLAN`; no filename, folder, size, or download row is visible. The rail looks unfinished exactly where it claims to expose the build output.

**Readability — good mechanically, questionable semantically.** `LIVE`, the selected base, section labels, and totals are clear. But `VRAM TOTAL 0 GB` is high-contrast and precise-looking in a way that reads as a real zero, not an unknown value. For a selected SD 1.5 base, that is a trust problem unless zero is genuinely the intended cost. `DISK TOTAL 2033 MB` has no visible manifest item beside it to substantiate the number.

**Hierarchy — mostly correct.** The amber selected-input panel, matching card outline, and `REMOVE FROM STACK` action establish a clear relationship between the grid and the rail. The duplicate presentation of the base—once inside `SELECTED INPUTS`, then again under `BASE`—adds some unnecessary repetition. The empty `LAYERS`, `MOTION`, and `VOICE` slots correctly communicate what remains to be built.

**Noise — moderate.** `LIVE` is justified now. The repeated base name and the large filled `REMOVE FROM STACK` button are visually forceful, but the bigger issue is the blank manifest area: empty space becomes a visual claim that output is missing.

**Internal tool or marketing site? — clearly an operational internal tool.** This is the most convincing screenshot in the set. It shows selection, state, totals, and next actions. The tool still needs trustworthy arithmetic and a visible manifest to feel production-ready.

### Shot 03 verdict

**7/10.** The flagship interaction finally reads correctly, but `0 GB` and the empty manifest block make the computed result look unreliable or incomplete.

## New defects and regressions

These are in addition to the improvements verified above. Severity reflects handoff risk visible in the screenshots.

### [P0] The default Persona gate is still semantically broken

Evidence: `all 20` is the visible active filter while the matrix and cards include `Niji semi realism` tagged `Anima`, an overt anime close-up, and other stylized imagery. The `style: anime 42` chip is present but does not read as an applied choice.

Impact: the first visual impression still contradicts `realism bases + identity`. A curator cannot trust that “Persona” means realism without manually policing the results. This is the same core blocker as R1, not a cosmetic remnant.

Required correction: make the default result query/render gate realism-photoreal entries. Keep anime/stylized content out of `all`, or make the style chip visibly selected before it can appear. The active filter and the visible image category must agree.

### [P1] The computed rail reports a suspicious zero VRAM total

Evidence: after selecting `majicMIX sombre 麦橘唯美`, the rail says `VRAM TOTAL 0 GB`.

Impact: a high-contrast numeric total implies a valid calculation. Zero is different from “unknown” and is not credible as a hardware requirement for a selected model unless explicitly defined. This undermines the central promise of a live stack builder.

Required correction: calculate from the selected asset’s known value, or render `—` / `UNKNOWN` with a short reason when the value is missing. Never coerce missing VRAM to zero.

### [P1] The manifest control exists without visible manifest output

Evidence: Shot 03 shows `DOWNLOAD MANIFEST` and `COPY ALL`, plus `DISK TOTAL 2033 MB`, but no filename, folder, version, size, or download row appears in the large space below the heading.

Impact: the control looks performative and the disk total cannot be visually audited. The active plan is therefore only partially computed on screen.

Required correction: render at least the selected base’s manifest row immediately below the heading, or explicitly label the section as pending/empty and disable `COPY ALL` until rows exist. Do not leave an unexplained blank block beside a nonzero total.

### [P1] Shot 00 and Shot 01 do not establish distinct visible states

Evidence: the two supplied shots show the same active nav, header, counts, matrix, card tops, and empty rail. No selection, filter, or content change is visible.

Impact: a reviewer or owner cannot tell whether the Persona stage loaded, whether home is intentionally the Persona default, or whether the navigation interaction did nothing. State changes need a visible result, not only an underline.

Required correction: if home intentionally lands on Persona, call that out in the route/state design and do not present the two captures as distinct states. If they are meant to differ, expose the changed stage title, route, filter, or result payload in the viewport.

### [P1] Shot 00/01 still technically preview-first, not decisively preview-first

Evidence: the first preview row starts around y619, leaving only about 281px of the 900px viewport for media and the first line of card names. The matrix occupies the dominant block above it.

Impact: the fix is visible, but the user still cannot compare complete candidate cards without scrolling. The first impression remains filter/matrix-first.

Required correction: reduce the matrix’s vertical footprint or make the answer row denser so the first row of cards shows the image, full name, and score/action in the initial viewport. Preserve the stronger Shot 02 composition as the target.

### [P2] Chip semantics create contradictory counts and category signals

Evidence: `all 20` sits beside `style: anime 42`, while anime content appears in the visible all-results wave. The chips look like peer filters, but their counts do not describe the same apparent result set.

Impact: users cannot infer whether 20 is the kept set, 42 is a source count, or anime is active. This directly weakens trust in the curation gate.

Required correction: distinguish active filters from available facets visually and explain incompatible counts in a tooltip or compact count label. Keep the visible category aligned with the active filter.

### [P2] Selected-base presentation repeats the same input

Evidence: Shot 03 shows `majicMIX sombre 麦橘唯美` in `SELECTED INPUTS`, then again under the `BASE` section immediately below.

Impact: the repetition consumes scarce rail height and makes the top block feel like a summary of a summary. It is not fatal, but it delays layers and manifest output.

Required correction: use the selected-input block as the summary and turn the `BASE` slot into a compact editable row, or remove the duplicate summary once the slot is populated.

### [P2] Card evidence is uneven after placeholder removal

Evidence: the first two expanded cards contain readable rationale text, while `OrangeChillMix` and `Niji semi realism` visibly reduce to name, tag, score, and action.

Impact: omitting fake fields is correct, but the resulting grid signals inconsistent curation depth. The user cannot tell whether the short cards are intentionally minimal or simply under-researched.

Required correction: use a consistent compact evidence row—such as verified preview count, fit verdict, or source date—or suppress under-evidenced cards from the primary wave until they meet the same threshold.

## Final judgment

The build has crossed from “dashboard landing panel” into a credible internal workbench in the best shot. The compact header, larger type, explicit empty state, selected-card treatment, slot model, live totals, and manifest controls are all visible progress.

It still should **not** be handed to the owner. The default Persona lane visibly violates its own realism promise, and the active rail presents a potentially false `0 GB` total with no visible manifest evidence. Fix those trust defects first; then use Shot 02/03’s density and selection relationship as the visual baseline.

**Overall: 6/10 — NO-GO.**
