# VISUAL CRITIQUE — R1 (2026-09-02)

Reviewer: zero-loyalty visual reviewer, applying E13 protocol against `docs/REBUILD-SPEC.md`.

Scope: the four supplied 1440×900 screenshots, judged at 100% zoom and only on what is visible. The binding priorities are an internal workbench, density over polish, previews before text, base font ≥18px, entry names ≥20px, mouse-first decisions, and a live stack builder. Hidden behavior earns no credit in a screenshot review.

## Executive verdict

**Rejected as shown.** The shell is competent and recognizably operational, but the visual order is wrong. The page spends its first viewport on a stage title, status chrome, filters, and an empty rail while the actual previews are below the fold. When previews do appear, the Persona lane looks like an anime image gallery with incomplete curation metadata, not a realistic-persona decision matrix. The supposed flagship—the Stack builder—is a catalog rail with an empty state, not an execution plan.

The work reads more like a dark dashboard template with internal-tool styling than “the best internal curation workbench it could be.” The monospace labels, thin rules, stage numbering, and amber/cyan accents establish a tool register, but they do not yet produce a distinctive or deeply useful workbench.

## Shot 00 — home

### Density — fail

The first viewport is chrome-heavy rather than decision-dense. From the sticky nav to the stage divider, roughly 247px are spent on the stage eyebrow, oversized `Persona` title, subtitle, funnel metadata, and breathing room. The search/filter block then consumes another roughly 118px before the decision rows begin. At 900px tall, no preview-dominant card is visible.

The right rail occupies about 390px of the 1,324px content width and is already long enough to scroll, yet it contains no selected input. That is a large permanent allocation for an empty builder. The left column is not empty, but its compact matrix rows are still text-first and image-free.

### Readability — fail

The `Persona` heading is very readable; the information the curator must compare is not consistently so. The visible matrix option names are around 16px, purposes are around 16px, filter chips are 13px, and metadata/utility text sits around 10–15px with muted contrast. That directly misses the spec’s 18px base and 20px entry-name floor. The low-contrast gray labels (`NEED`, `FUND`, `STAGED`, `VRAM —`, and card metadata) become texture at 100% zoom instead of dependable evidence.

### Hierarchy — wrong

The first thing seen is a stage introduction, then the title of the execution rail. The previews and candidate names—the stated primary decision material—are absent from the first screen. `Pipeline stage · 01` and the active `01 Persona` nav item also repeat the same orientation signal.

The stage header behaves like a hero section even though the spec explicitly bans a hero. `Pick a need, compare the trade-off` is the right product idea, but it arrives after a large title block and is still rendered as a scan-heavy list rather than an answer-first recommendation.

### Noise — too much

The individual status signals are defensible, but too many of them compete before the user reaches a candidate: `LOCAL STAGED DATA`, `NSFW ON`, `PIPELINE STAGE · 01`, `FUNNEL`, `STAGED`, `DECISION VIEW`, `62 options`, `EXECUTION PLAN`, and `LIVE`. The empty builder’s instructional paragraph is generic orientation copy occupying high-value space. The three zero-yield filter chips are correctly disabled, but still add visual weight to a bar already carrying search, counts, and labels.

The main noise problem is not any one label; it is the accumulation of labels around a screen with too little decision output.

### Internal tool or marketing site? — mixed, leaning tool

The status language, data count, mono utility face, and square rules read as an internal tool. The oversized editorial heading, large breathing zone, and explanatory `Choose one base...` copy borrow the visual behavior of a product landing page. It is not a public marketing site, but it has a marketing-style opening where a workbench should have started working.

### Shot 00 verdict

**4/10 — structurally a dashboard landing panel, not a preview-first curation workbench.** The page asks the user to admire the stage framing before making a choice.

## Shot 01 — Persona stage grid

This screenshot is visually identical to Shot 00 at the supplied resolution. There is no visible transition from “home” to “Persona stage grid”: no new grid, no selected stage change beyond the same nav highlight, no changed count, and no new preview payload. That is itself a severe interaction/state-legibility failure.

### Density — fail

The evidence is the same as Shot 00: the first viewport contains the title, search, matrix start, and empty builder, not the promised stage grid. A user cannot confirm that the Persona results loaded without relying on an identical-looking shell.

### Readability — fail

The same typography problem remains: the high-value comparison text is below the 18px base requirement, while small mono labels and muted metadata carry state the user needs to trust. The large `Persona` title consumes the strongest typographic contrast without conveying a decision.

### Hierarchy — fail

The active nav underline is the only strong stage-state cue, and it is not enough to make the supposed grid state legible. The page hierarchy still goes stage title → chrome → matrix/rail → previews off-screen. The result is not “I can see the best persona options”; it is “I am looking at a generic stage shell.”

### Noise — too much

The duplicated stage numbering and status blocks are especially wasteful here because they do not accompany a visibly changed content state. The interface spends pixels explaining where the user is while failing to show what is there.

### Internal tool or marketing site? — mixed, leaning template

The same tool cues are present, but the lack of a visible grid makes the screenshot look like a static mockup of an internal tool rather than a functioning one. The title treatment is the most polished object on screen; the data state is not.

### Shot 01 verdict

**2/10 for state legibility — indistinguishable from Shot 00.** If this is meant to be the Persona grid, the grid has failed the screenshot test before content quality is even considered.

## Shot 02 — Persona card expanded

### Density — mixed, with real improvement

This is the first shot that honors “previews before text”: three tall previews occupy the top of the main content, and the 3-column arrangement uses the main column efficiently. The preview-dominant card anatomy is directionally right.

But the viewport begins with a clipped fragment of the previous matrix row, then a large empty detail body appears under the cards. The second and third cards reserve the same tall card height while exposing very little information. That is vertical waste disguised as expansion. The right rail is also clipped at the viewport bottom, so the user gets neither a complete card detail nor a complete stack decision in one view.

The image-to-card ratio is good; the information-to-card ratio is not.

### Readability — mixed, still below the bar

The card names are approximately 21px, which clears the name requirement, but the first name is ellipsized (`Pastel-Mix [Stylized An...`) and therefore hides identity at the exact moment comparison matters. Purpose text is approximately 16px and repeated as `Purpose not staged`; status and metadata are around 10–11px with weak contrast. The rail’s `ADD` actions and VRAM sublines are also tiny and truncated.

An expanded card should earn the extra space with a readable verdict, why, verified date, and concrete stack implications. Instead, the most legible content is the model name and the image.

### Hierarchy — better, but semantically wrong

The visual sequence is now preview → name → purpose, which is the correct anatomy. However, all three visible persona previews are overtly stylized/anime imagery: a witch illustration, a silver-haired fantasy character, and a hazmat anime character in a burning scene. The first name even advertises `Stylized Anime Model`; the other two do not explain why they belong in a realism-first Persona lane.

This is not a minor taste issue. The spec says Persona is for total-realism bases and identity/persona LoRAs, with anime only as a deliberate, tagged style choice—not the default wave. The strongest visual signal in this shot contradicts the stage promise.

There is also no obvious selected-card treatment. The expanded detail state and the empty stack state do not visually connect, so the user cannot tell which item, if any, is driving the rail.

### Noise — incomplete data is rendered as UI

`STATUS NOT STAGED`, `Purpose not staged`, `VRAM —`, `No vetted input loaded`, and repeated `ADD` actions expose pipeline incompleteness instead of helping a decision. In an expanded state, source/base-model/stacks-on details can be useful, but the current layout gives them more space than an actual verdict and makes the missing fields look like intentional content.

The `BASE` pill over every image is also weakly informative when every visible card is already a base candidate. It adds a badge without resolving a choice.

### Internal tool or marketing site? — tool with catalog/showcase leakage

The card metadata and rail are recognizably operational. The bright art, uniform score labels, and gallery-like row make the experience feel like a visual catalog. That could be acceptable for a reference library, but this brief calls for a workbench that makes a build decision quickly. The screenshot shows browsing behavior more strongly than committing behavior.

### Shot 02 verdict

**5/10 — the card anatomy is the best part of the rebuild, but it is populated with the wrong Persona signal and under-curated detail.** The screen looks more usable than Shot 00, yet it still fails the lane’s core promise.

## Shot 03 — Stack builder rail active

This screenshot is also visually identical to Shot 02 in the supplied evidence. More importantly, the rail does not look active in the operational sense: it says `LIVE`, but also says `No vetted input loaded`, and every visible candidate still offers `ADD`.

### Density — fail for the flagship surface

The rail is tall and persistent, but its space is spent on an intro paragraph and unselected base/motion catalog rows. There is no visible selected stack, total VRAM, total disk, download manifest, exact version link, or copy-all output. The main grid remains three large cards while the supposedly active execution surface produces no execution result.

### Readability — fail

Rail option names are visually smaller than the required 20px entry floor, and the `ADD` actions plus `PERSONA · VRAM —` sublines are around 11px. Names are truncated (`ipiv's Morph - img2vid AnimateDi...`, `Hunyuan 12GB vram @1080p w/...`), so both the option identity and the hardware implication are hidden. The rail is the place where precision matters most; it currently uses the least readable treatment.

### Hierarchy — misleading

`Execution plan`, `Stack builder`, and the green `LIVE` marker strongly imply that a plan exists. The actual visual state is an empty picker. A real active state should make the chosen base, layers, motion, voice, and live totals the dominant content, with unselected options secondary. Here, the unselected catalog is dominant and the plan is absent.

### Noise — performative status and dead weight

The green `LIVE` indicator is noise, and arguably misleading, while no computation is visible. The explanatory paragraph repeats the builder’s purpose instead of showing its result. Every `ADD` label is tiny, identical, and visually weaker than the problem it is meant to solve. `No vetted input loaded` is also too passive: it neither tells the user what to select nor turns the empty rail into a next action.

### Internal tool or marketing site? — tool shell, generic dashboard behavior

The panel looks like a standard dark admin/dashboard sidebar: heading, status dot, section dividers, option rows, and tiny action labels. It is clearly not a consumer marketing page, but it is not yet an opinionated workbench. The distinctive stack metaphor is stated in copy and not made visible in the layout.

### Shot 03 verdict

**3/10 — the flagship differentiator is visually absent.** This is a rail of choices, not a live execution plan.

## Three worst visual defects

### 1. [P0] The first viewport is a stage hero, not a working surface

**Evidence:** the 00/01 viewport spends roughly 247px before the divider and reaches the matrix only after the search block; no preview appears at 900px tall.

**Why it is fatal:** it violates zero-hero, previews-over-text, density-over-polish, and the one-click stage → essentials requirement at the first impression. The user must scroll to see the thing they are choosing.

**Concrete fix:** compress the stage header into a compact 72–100px band: stage name, one-line focus, and `pulled N → kept M` on one line. Keep the stage nav and filters sticky. Put one or two filled answer-first matrix rows directly above the preview grid, or collapse the matrix after the first recommendation. The first 900px must show names and at least the first row of preview media. Reduce or collapse the empty rail intro until an input is selected.

### 2. [P0] The Persona lane visually advertises anime instead of realism

**Evidence:** all three visible previews in 02/03 are anime/stylized fantasy images; cards show `Purpose not staged`, and the first name explicitly says `Stylized Anime Model`.

**Why it is fatal:** this contradicts the lane definition, makes the default result wave look semantically wrong, and destroys trust in the curation before the user reads a verdict. A realism workbench cannot lead with three obviously non-realistic examples.

**Concrete fix:** enforce a Persona render gate on stage/tag plus a visual realism label. Default Persona results should be real-human/photorealistic entries only. Put anime/stylized entries behind a deliberate `style choice: anime` filter or separate cluster, with the reason visible. Do not render an entry with `Purpose not staged`, missing preview evidence, or placeholder VRAM as a default top result. Each expanded card needs a one-line comparative verdict, why, verified date, and exact version identity.

### 3. [P0] The Stack builder is an empty, falsely-live catalog rail

**Evidence:** the rail says `LIVE` while saying `No vetted input loaded`; visible content is unselected base/motion rows with `ADD`; no totals or manifest appear.

**Why it is fatal:** the spec identifies the stack builder as the product’s flagship value. In the screenshot it contributes no computed decision: no selected base + N layers + motion + voice, no VRAM/disk sum, no download rows, and no copy-all action. The visual metaphor is promised but not delivered.

**Concrete fix:** make the rail’s empty state explicit and actionable (`Select a base to start`) and remove `LIVE` until a stack exists. After the first click, pin the selected item at the top with a strong selected treatment; show slots for base, layers, motion, and voice; put live VRAM and disk totals above the option catalogs; and render the manifest with filename, folder, exact version URL, and size. Move unselected options below the computed plan. Make selected state obvious in both the card and the rail.

## Cross-cutting blocking fix: typography and contrast

This is not polish. The screenshots fail the binding readability rule. Raise all decision-bearing body and purpose text to ≥18px, all entry names—including matrix and rail options—to ≥20px, and keep utility labels at a readable minimum with stronger contrast. Preserve the mono face for provenance/status, but stop using 10–13px gray text for facts the user must compare. Remove ellipses from names in the primary card/rail view; wrap to two lines or provide the full name on hover without hiding it from the first glance.

## Final judgment

**Generic template, with a promising card skeleton—not the best internal curation workbench it could be.** The dark palette and rule-based chrome are serviceable, but the current composition optimizes for looking like a “pipeline” rather than making a curator decide quickly. The rebuild should not be handed off until the first viewport shows real decisions, Persona defaults look realistic, text is readable at 100%, and the rail visibly computes a stack instead of narrating one.
