# idea analysis 51-75 (comparison views · onboarding · detail pages)

analyst: sisyphus-junior (parallel batch 3 of 4). inputs: codex-design-ideas.md (range 51-75), REQUIREMENTS.md, CRITERIA.md. site reality: static vanilla JS on github pages, python pre-generation allowed, local JSON data, civitai CDN images only external, localStorage for personal state, query params for shareable state, SFW default with mature toggle.

personas: **marcus** (ad guy, RTX 4070 12 GB, client deadlines) · **lia** (OF creator, non-technical, RTX 3060 laptop 8 GB) · **kenji** (comfyui newbie, day 2, 8 GB laptop) · **owner** (curator, taste, fewer clicks).

---

## 51 — persistent compare tray at the bottom of the screen

**restatement:** a fixed bottom tray holds up to 4 picked entries while the user keeps browsing across lanes/tabs; it never loses state until cleared.

**mechanism:** fixed-position `div` (height ~72px) with thumbnail slots + "compare" button + clear-all. Card hover/kebab menu exposes "add to compare". State = array of entry ids in `localStorage` (`cl.compare`), so it survives hash-route changes and reloads. Grid gets `padding-bottom: 88px` so the tray never covers the last card row. Tray collapses to a 32px pill ("compare · 3") when idle, expands on hover/click. 5th add attempt: tray shakes once + toast "tray full — remove one", never silently drops.

**simulation:** marcus, thursday 23:40, client pitch friday morning. he browses campaign lab, opens three image-to-video workflows in different tabs over 20 minutes, hits "add to compare" on each. the tray waits at the bottom the entire time — switching lanes, filtering, going back — picks still there. he feels the site holding his shortlist for him instead of forcing him to remember or screenshot. at 23:47 he clicks "compare" and the decision starts.

**micro-criteria:** (1) add-click → thumbnail appears in tray < 200ms, zero page scroll jump; (2) tray content identical after lane switch AND full reload (localStorage read on init); (3) 5th add produces visible feedback within 300ms, tray never exceeds 4 slots.

**cost:** low. one fixed element + one storage key. mobile: tray stacks to a bottom bar above content padding; watch iOS safe-area inset.

**verdict:** ADOPT 9 — comparison is the core decision product; a persistent tray is the cheapest way to compare across a browsing session, not just a single list.

---

## 52 — compare 2-4 entries in aligned rows

**restatement:** the compare view renders a strict attribute table: one column per entry (2-4), one row per attribute, identical order every time.

**mechanism:** hash route `#compare?ids=a,b,c` renders a table: sticky header row = thumbnail + our name + tier badge per column; first column = row labels; body rows = attributes (row set defined by 53). columns equal width (`grid-template-columns: 160px repeat(n, 1fr)`, max-width cap so 2 entries don't stretch ugly). Same JSON objects feed every column, so alignment is structural, not hand-tuned. scroll-x on narrow screens with the label column sticky.

**simulation:** kenji, day 2, three persona LoRAs open in compare. he reads it like the spreadsheet he knows from work: eyes go straight down the VRAM row, one column says 24 GB — dead to him, 4 seconds. then down the score row. no tab-switching, no memory load, no scrolling tennis between detail pages. he feels: "I can read this."

**micro-criteria:** (1) all attribute values vertically aligned to the pixel (same row height, no per-cell wrapping drift); (2) works at n=2 without stretched cells (max column width cap); (3) label column stays visible while scrolling horizontally on mobile.

**cost:** trivial — one table render fed by existing entry JSON. zero data cost.

**verdict:** ADOPT 9 — the table IS the format for "best-per-category" decisions; aligned rows are the minimal correct presentation.

---

## 53 — compare editor score, tier, VRAM, base model, freshness, dependencies

**restatement:** the compare row set is fixed and ordered by elimination power: what rules an entry OUT comes before what differentiates among survivors.

**mechanism:** rows, in order: (1) VRAM requirement, (2) editor score + tier badge, (3) base model family, (4) dependencies count ("2 models · 3 nodes"), (5) freshness (version date), (6) license note when it matters (personal-only badge per CRITERIA kill-lines). every field already exists per entry JSON — this idea is pure spec of row set + row ORDER. rationale: owner law "formato e ordem importa mt" — VRAM first because it eliminates impossible options before hope forms (mirrors filter rationale, idea 32); score second because it ranks survivors.

**simulation:** lia compares two persona LoRAs for her page. VRAM row first: one needs 16 GB, she has 8 — eliminated before she falls in love with its gallery. score row settles the survivor question. she never has to un-decide anything, and that is the whole point: the table ordered the pain away from her.

**micro-criteria:** (1) VRAM row renders above score row, always, in compare AND detail proof block (73) — one shared constant; (2) every cell filled or explicit "—", never blank; (3) score cells use the same one-decimal format as cards (`8.9`), no format drift between surfaces.

**cost:** zero beyond 52 — it is 52's row spec.

**verdict:** MERGE into 52 (row-set spec) — 8 — right fields, but the original order (score first) buries the eliminator; reorder VRAM-first is the improvement this merge carries.

---

## 54 — compare preview galleries using the same prompt or scenario label

**restatement:** comparable scenario rows: for curator-tagged scenarios ("same prompt, three ways", "outfit change", "low light"), each entry's preview image for that scenario sits side by side.

**mechanism:** entry galleries in our JSON get optional `scenarios: [{id, label, imageIdx}]` (curator-assigned). compare view renders one gallery row per scenario id shared by ≥ 2 compared entries: label above, entry images in their columns, same aspect-ratio box (no layout jump), "no preview" placeholder for a missing cell. SFW rule: a mature entry's preview stays placeholder/blurred in compare until the mature toggle is on — the toggle governs every surface, compare included. no scenarios shared → section hidden entirely, never an empty scaffold.

**simulation:** marcus needs "the same woman, two workflows" for a client. scenario row "identity under outfit change": left workflow holds the face, right one drifts into a cousin. one glance, decision made — he does not re-run prompts at midnight to prove what the site could have shown him. this row is worth more to him than every number in the table.

**micro-criteria:** (1) images in one scenario row share identical height box, zero layout shift on load; (2) scenario label ≤ 5 words, sits above the row; (3) mature placeholder logic identical to cards (no SFW leak through the compare back door).

**cost:** code trivial; DATA cost real — curator must tag comparable scenarios per entry. sparse coverage risk: ship with whatever scenarios exist, degrade silently.

**verdict:** ADOPT 7 — the only comparison feature that shows RESULTS instead of numbers (owner requirement verbatim: "resultados visíveis"); gated on curation discipline, so v1 ships partial with graceful absence.

---

## 55 — highlight score deltas rather than coloring every value

**restatement:** in compare rows, only the difference is marked: best value gets one accent tint, deltas render as "+0.7" chips; every other cell stays neutral.

**mechanism:** render-time computation per numeric/date row: best value cell gets `--accent` tint + delta chip (absolute diff vs best, e.g. `−0.7`); ties = all tinted, no chips. text rows (base model): differing values get a subtle underline, identical values dim slightly. no per-cell rainbow — one accent per row maximum. delta chip carries the meaning in TEXT so grayscale readers lose nothing (beautiful-law: contrast is communication, not decoration).

**simulation:** kenji reads the score row: `8.9 · 8.2 (−0.7) · 7.8 (−1.1)`. he never re-reads two numbers and does mental subtraction — the gap is already words. the table feels calm instead of lit up like a dashboard, and calm is what makes him trust the numbers he does read.

**micro-criteria:** (1) exactly ≤ 1 tinted cell per numeric row (ties allowed), zero full-row coloring; (2) delta chips ≤ 4 chars incl. sign; (3) meaning survives grayscale screenshot (chip text readable, tint never the only signal).

**cost:** trivial — pure render logic.

**verdict:** ADOPT 9 — deletes the "wall of colored values" anti-pattern at zero cost; the restraint IS the polish here.

---

## 56 — mini workflow graph for each compared workflow

**restatement:** each compared workflow column shows a thumbnail DAG — nodes as pills, edges as lines — so structural complexity is visible at a glance before download.

**mechanism:** python build step parses each stored ComfyUI workflow JSON (UI format `nodes[].type` or API format `class_type`), extracts node count, node types, link structure, and bakes a compact `{nodes, edges}` or a pre-rendered SVG string into our entry JSON. compare view renders the SVG at ~200px wide; node color = node role (loader / sampler / vae / custom), identical palette across all columns. hover tooltip = node type name. graceful fallback if parsing slips schedule: "18 nodes · 6 custom" pill instead — never a broken image.

**simulation:** kenji compares two talking-head workflows. left column: 18 pills in a clean spine. right column: 40-node spaghetti with three loops. nobody taught him graph theory — he still instantly feels "the left one looks fixable, the right one looks like a curse". that feeling is accurate and it took 2 seconds.

**micro-criteria:** (1) graph readable at 200px: node shapes/count distinguishable, no text squinting required; (2) same node type = same color across ALL compared graphs (comparison is the point); (3) pre-baked SVG renders < 50ms, zero runtime parsing.

**cost:** medium — build-time extractor is real work, BUT it is the same parser idea 57 (dependency list) and idea 78 (pre-import missing list) need. build once, feed three features.

**verdict:** ADOPT 7 — real differentiator for newbies (complexity at a glance) and it amortizes the workflow parser we need anyway; if the parser slips, ship the node-count pill, upgrade later.

---

## 57 — display dependency differences: missing nodes, models, extensions, voice tools

**restatement:** a compare row (and detail section) that lists exactly what each entry REQUIRES — custom nodes, model files, extensions, voice tools — with items not shared by all compared entries marked as diffs.

**mechanism:** from the same build-time parse as 56: node types outside comfy core → custom nodes (core list version-dependent → heuristic + curator override field); loader nodes → required model files; audio nodes labeled by role (narration / lip sync / cleanup / music, idea 83's vocabulary). compare renders a "what you need" row per entry: count + expandable plain-text list, every item selectable/copyable. items missing from the OTHER compared entries get the diff underline (55's vocabulary). labeled honestly: "detected from workflow file" — heuristics don't masquerade as certainty.

**simulation:** marcus, near midnight, about to grab workflow A for a client delivery. compare shows A needs 6 custom nodes he doesn't have; B needs 2 he already installed this month. he picks B and sleeps. without this row he'd have downloaded A, hit a red console error at 00:40, and blamed the site — the exact newbie-death this library exists to prevent.

**micro-criteria:** (1) every dependency item renders as plain selectable text (copyable), not icon soup; (2) diff marking survives grayscale; (3) heuristic-sourced items visibly distinguished from curator-verified items ("detected" vs "confirmed").

**cost:** medium — the parser (shared with 56). the honest-labeling discipline is the ongoing maintenance.

**verdict:** ADOPT 9 — "list missing before download" is the #1 newbie painkiller and directly serves the owner's fast-import law; the parser is a shared investment, not a dedicated cost.

---

## 58 — "show only differences" toggle in comparison

**restatement:** a single checkbox collapses the compare table to rows where entries actually differ — identical rows hide.

**mechanism:** checkbox above the table; render filter comparing normalized values (lowercase, trimmed, dates normalized to month precision) across columns; rows with all-equal values hide. toggle state goes into the compare URL (`#compare?ids=…&diff=1`) so a differences-only view is shareable. after toggling, a count line: "3 of 9 rows differ". pure render filter — no data mutation, instant.

**simulation:** lia compares two SDXL persona LoRAs — same base, same VRAM class, same tier. nine rows, six identical, noise. she taps "only differences": score, trigger word, freshness remain. three rows answer her actual question ("which one, then?"). she feels smart instead of overwhelmed, and overwhelmed is one tap from closing the tab.

**micro-criteria:** (1) toggle round-trip < 100ms, no layout jump (hidden rows collapse, container height animates ≤ 200ms); (2) "N of M rows differ" always shown while active; (3) `&diff=1` in a fresh browser renders the same filtered view (URL is the state).

**cost:** trivial.

**verdict:** ADOPT 8 — cheap accelerator for the most common compare case (2 similar entries); free shareable state as a side effect.

---

## 59 — "use with my rig" hides incompatible options inside comparison

**restatement:** one toggle in compare dims/hides columns whose VRAM requirement exceeds the user's saved rig profile — the same profile the filter bar uses.

**mechanism:** rig profile lives at `cl.rig` in localStorage (set by onboarding 61/64 or the GPU preset filter, idea 33 — ONE key, three consumers: filter bar, card badges, compare). compare toggle "use with my rig" reads it: incompatible columns get dimmed style + "needs 16 GB" tag, never silently deleted (dimmed-but-visible beats vanishing — the user learns WHY). no profile set → the toggle shows as a prompt chip "set your GPU (10s)" linking to the one-click picker, not a dead control.

**simulation:** kenji, 8 GB laptop. three columns in compare, he taps "use with my rig": the third dims with a small "needs 16 GB" tag. no drama, no false hope, no downloading something that will OOM his machine at 1am. the site knew his machine because he told it once, and it remembered everywhere.

**micro-criteria:** (1) rig profile settable in ≤ 2 clicks from inside compare (prompt chip, not a settings page); (2) dimmed column still readable (opacity floor, tag carries the reason); (3) same `cl.rig` key as filter bar and card badges — verified by grep, one source of truth.

**cost:** trivial — filter logic already exists for the grid; reuse in compare.

**verdict:** MERGE into the single rig-profile system (with 33 + 61/64) — 8 — the feature is right but it must be ONE profile feeding three surfaces, not three implementations drifting apart.

---

## 60 — export shortlist as Markdown or a stable share URL

**restatement:** any current view (and the saved shortlist) serializes to a query-param URL that renders identically in a fresh browser, plus a client-side `.md` download.

**mechanism:** URL: `?lane=ads&ids=…&sort=proven&diff=1` — JS reads `location.search` on load and reconstructs state (this is idea 10's URL-state law applied to shortlists; no server, no encoding service, github-pages safe). markdown export: build a string — per entry: our name, verdict line, score/tier, VRAM, civitai original link, our import link — and download via `Blob` + `a[download]`. copy-to-clipboard variant for the URL with a checkmark flip (micro-interaction #14 vocabulary).

**simulation:** owner, friday night, wants to show a friend his top 3 for face consistency. he hits "share", pastes one URL into chat. his friend opens it on a phone: identical view, his names, his scores, no onboarding wall. ten minutes later the owner exports the same list as markdown into his project notes. the site respects his time twice in one evening, and every shared URL is a free ad for the library.

**micro-criteria:** (1) URL opened in a clean browser profile (no localStorage) renders identical entries/order — tested, not assumed; (2) exported markdown passes a lint parse and contains name+score+civitai link+import link for every entry; (3) URL ≤ 2000 chars for a 4-entry shortlist.

**cost:** low — query-param serialization is half-built by idea 10; markdown template is one function.

**verdict:** ADOPT 9 — shareability is the static site's only growth loop and it costs almost nothing; markdown export doubles as the owner's own curation workflow tool.

---

## 61 — onboarding: three questions — desired output, hardware, experience level

**restatement:** first visit offers a 3-tap setup (one question per screen, zero typing) that sets lane, rig profile, and display mode — then lands on a list that already fits.

**mechanism:** overlay on first load (`cl.onboarded` flag in localStorage; flag checked before render so returning users never see it). Q1 "what do you want to make?" → 3-4 image cards (persona / product ad / talking video / voice) mapping to lanes. Q2 "what GPU are you using?" → GPU-name presets (spec of 64) writing `cl.rig`. Q3 "how deep do you want the details?" → `beginner / technical` writing `cl.mode` (65). every screen carries a visible "skip — just browsing" that completes with defaults (lane=persona, rig=unset, mode=beginner). mature lane NEVER appears in Q1 — newcomers reach it only via the header toggle, per the first-60-seconds spec. re-openable forever via the "start here" shelf (idea 6).

**simulation:** kenji, day 2 after installing comfyui and generating one brown blob. he lands, taps "talking video", taps "RTX 3060 laptop", taps "beginner" — fifteen seconds — and the page that loads already shows talking-head workflows that run on 8 GB with plain-english labels. no filter wall, no jargon, no account. his second ever win with AI tooling, and it took less time than the first error message did.

**micro-criteria:** (1) full completion ≤ 20s / 4 taps (3 answers + done) — timed on a real pass; (2) skip completes and never blocks browsing (overlay dismissible on every screen, esc works); (3) all three answers visibly reflected in the landing view (lane tab active, rig chip in header, beginner labels on) within one render.

**cost:** low-medium — overlay + routing; the value is that it seeds the SAME three keys (`cl.rig`, `cl.mode`, lane) every other feature reads. build keys first, overlay second.

**verdict:** ADOPT 9 — this IS "instantly understandable" for newcomers; doubles as the configuration system for a third of this range (59, 64, 65).

---

## 62 — one complete sample persona instead of an empty grid

**restatement:** the persona lane's first view is one fully-populated, real, curated stack — "the library sample" — not a wall of 40 cards; newcomers imitate a finished thing before they browse.

**mechanism:** the featured first card is a REAL S-tier entry (or stack) rendered at 2× size with everything a detail page has: ≥ 4 navigable preview images, trigger word + copy, version pin, VRAM, "what you need" checklist, import button above the fold. it is curation, not a demo stub — every field must be production data (CRITERIA: no stub fields survive). remaining entries follow below as the normal grid. the sample is chosen by curator and rotates when a better stack earns the slot.

**simulation:** kenji finishes onboarding and the first thing on screen is ONE finished thing: a woman's face holding across four photos, a trigger word he can copy, a button that says what it does. forty cards would have asked him forty questions; this asks him none. he clicks import because it is the only obvious action, and the library's credibility is established by the second success of his life.

**micro-criteria:** (1) zero stub fields in the sample (empty field = ship blocker); (2) import button + at least one preview + trigger word visible without scrolling at 1366×768 AND 390×844; (3) gallery ≥ 4 images, navigable with keyboard arrows.

**cost:** trivial code (it's a featured render of existing data); real cost is the curation pick — which is the job anyway.

**verdict:** ADOPT 10 — the single highest-leverage onboarding move in this range; empty grids kill newcomers, one working thing converts them.

---

## 63 — LoRA defined in a tooltip (jargon glossary)

**restatement:** every technical term (LoRA, checkpoint, VRAM, trigger word, custom node, base model) renders with a dotted underline + plain-english tooltip from one shared glossary.

**mechanism:** one `glossary.json` (term → ≤ 15-word definition); build step (or runtime regex over text fields) wraps known terms with `<dfn class="term" data-term="lora">`. single tooltip component: CSS-positioned div, 300ms hover delay, dismiss on click-outside/esc, tap-to-toggle on touch, viewport-edge flipping so it never clips. same term → same definition everywhere — cards, detail, compare, onboarding. glossary doubles as beginner-mode vocabulary source (65).

**simulation:** kenji reads "Soft-Window Persona Lock — LoRA for SDXL". he hovers the dotted word: "a small add-on file that changes how the base model behaves". two seconds, no new tab, no google, no feeling stupid for not knowing. he keeps reading. that is the entire difference between bouncing at 30 seconds and staying for the import.

**micro-criteria:** (1) tooltip appears ≤ 300ms after hover-stabilize and never renders off-viewport (edge flip); (2) each term has exactly ONE definition across all surfaces (grep the glossary, single source); (3) touch: first tap opens tooltip, second tap on the term navigates/activates as normal.

**cost:** trivial.

**verdict:** ADOPT 9 — cheapest possible jargon removal; the glossary file becomes shared infrastructure for beginner mode.

---

## 64 — ask VRAM in plain language: "what GPU are you using?"

**restatement:** hardware questions and filter presets use consumer GPU names + GB together ("RTX 3060 laptop · 8 GB"), never bare gigabyte numbers.

**mechanism:** copy + data spec, not new code: the preset list for onboarding Q2 and the GPU filter (33) = named presets — `RTX 3060 laptop · 8 GB`, `RTX 4060 · 8 GB`, `RTX 4070 · 12 GB`, `RTX 4090 / 5090 · 24 GB+`, `cloud (no GPU)`, `not sure`. "not sure" maps to no filter + a one-line hint ("check your laptop model — or pick cloud"). selection writes the same `cl.rig` key as 59/61. card VRAM badges keep the short form `12 GB` (space) but questions always speak GPU names (clarity).

**simulation:** lia does not know what VRAM is and never will. she knows exactly one relevant fact: her machine is "the laptop my brother recommended — a 3060 something". the question says "what GPU are you using?", she finds her brother's recommendation BY NAME, taps it, and the site silently knew that means 8 GB. she feels spoken to instead of quizzed.

**micro-criteria:** (1) every preset shows GPU name AND GB — GB-only options banned in questions; (2) ≤ 6 presets + "not sure" fallback that never dead-ends (writes no filter, shows the hint); (3) answer changeable later in ≤ 2 clicks (header rig chip → picker).

**cost:** zero — it is the copy/preset spec for 61 Q2 and the filter bar.

**verdict:** MERGE into 61 (it IS question 2's content spec) — 8 — the improvement it carries: never interrogate users about specs they don't know; speak product names.

---

## 65 — beginner and technical display modes

**restatement:** one content model, two visibility levels: beginner hides version strings, node lists, file formats, stat tables; technical shows all — toggled in the header, set by onboarding, remembered.

**mechanism:** `cl.mode` key (`beginner`|`technical`), default beginner for first visits, set by onboarding Q3. implementation = per-field mode tags in the render layer + a body class for CSS-level hides; NOT a second design — same layout, same cards, subset of fields. beginner hides: base-model version pins, dependency raw lists (keeps count + plain summary), file formats, snapshot stats table, extended provenance. glossary tooltips (63) serve both modes. collapsed technical sections (66) are the mechanism: beginner = collapsed defaults, technical = expanded defaults — one implementation, not two.

**simulation:** marcus flips to technical the day he starts shipping: version pins, file sizes, and the raw dependency list appear exactly where the plain summaries were — same screen position, more depth. kenji stays beginner for a month and never once sees "SDXL 1.0 (refiner)" noise. one site serves both without becoming two sites, which is the only way this stays maintainable.

**micro-criteria:** (1) toggle in header, one click, effective on current view without reload; (2) ≥ 6 concrete fields differ between modes (enumerated in build, grep-verifiable); (3) zero layout shift between modes (same grid geometry, cells not reflowed).

**cost:** low-medium — every data field needs a mode tag; discipline, not difficulty. risk = mode drift (new fields default visible); mitigation: new fields default to technical-only unless curated otherwise.

**verdict:** MERGE with 66 (collapsed sections are the mechanism) — 8 — two audiences are real (kenji vs owner/marcus), but two DESIGNS would rot; subset-of-fields + collapse-defaults is the maintainable shape.

---

## 66 — technical fields collapsed until asked

**restatement:** dense technical blocks (versions & files, dependency raw list, stats table, provenance) live inside native collapsible sections with a one-line summary visible when closed.

**mechanism:** native `<details><summary>` — zero JS, keyboard + screen-reader accessible by default. summary always carries a one-line digest ("3 versions · latest 2026-08-14", "6 custom nodes detected") so closed ≠ empty. collapse default comes from display mode (65): beginner = closed, technical = open; user's manual open/close on a section wins for the session. expansion pushes only downward content inside its own container — no page-level reflow of the proof block or import button (72 layout stays stable).

**simulation:** marcus scans twelve cards and one detail page; everything reads as verdict + preview + VRAM. on the ONE entry that matters he expands "versions & files", pins the exact version the editorial test used, collapses it again. peace: the density existed the whole time, but it waited politely until he asked for it, and asking took one click.

**micro-criteria:** (1) closed state always shows a summary line — a bare "technical details ▸" with no digest fails; (2) native element (works without JS, focusable, aria-correct out of the box); (3) open/close shifts nothing outside the section (proof block and import button stay put — verified by screenshot diff).

**cost:** trivial.

**verdict:** ADOPT 9 — native HTML doing exactly its job; also the implementation substrate for 65, so it buys two ideas at once.

---

## 67 — sample gallery before model names

**restatement:** in onboarding choices and lane landings, the image takes ≥ 60% of the card; our name and tier render as a caption below — the eye decides before the words load.

**mechanism:** card anatomy reorder for outcome-choice surfaces: gallery image (fixed aspect-ratio box, civitai CDN) dominant; caption strip = our name + tier badge + one-line purpose. 2-3 images cycle on hover (desktop) / dots (touch), preload only first image; `loading="lazy"` + explicit width/height to kill CLS. applies to onboarding Q1 cards, lane landing cards, "start here" shelf — NOT to dense browse grids (there, idea 21's single dominant preview rule governs; this is the same philosophy escalated for choice moments).

**simulation:** lia picks her lane by LOOK: three cards of faces/product shots/talking heads, the pictures doing all the talking. her taste matches a skin tone and a vibe in two seconds — "that one" — and only then does she read "Realistic social persona". words validate what her eyes already chose. ask her to choose between three names first and she'd have guessed blind.

**micro-criteria:** (1) image region ≥ 60% of card area (measured, not felt) on the choice surfaces; (2) name/tier readable but visually secondary (type size ratio ≥ 2:1 image:name treatment); (3) no CLS from gallery cycling (fixed box) and lazy images carry explicit dimensions.

**cost:** trivial — reorder of existing card anatomy.

**verdict:** ADOPT 9 — "results visible" is owner law verbatim; show the result before the label at every choice moment.

---

## 68 — first import action above the fold on the first recommended card

**restatement:** the top recommendation's card is larger and carries the import button + "why it ranked first" line visible WITHOUT scrolling on desktop and mobile — action before exploration.

**mechanism:** first card spans 2 columns on desktop / full width mobile, containing: preview, our name, one-line why-first, proof block compact (73), and the import button labeled with its effect ("download comfyui JSON"). button placement verified against two reference viewports (1366×768, 390×844) — measured in build with a screenshot check, not eyeballed. import = static workflow file download (`/workflows/<id>.json`, `download` attribute) + the one-sentence instruction (idea 77's copy). after click, button flips to "JSON ready" + next-step panel appears (micro-interaction #15, first-60-seconds spec).

**simulation:** kenji finishes the three questions and the first screen already HAS the button. no scroll, no menu, no decision about where to start — the page hands him one obvious action at the exact moment his attention is warmest. he clicks it before doubt can load. his first minute on the site ends with a file in his downloads folder, which is the entire product promise kept.

**micro-criteria:** (1) import button in first viewport at both reference resolutions — screenshot-verified, not assumed; (2) button label names the effect ("download comfyui JSON"), never mystery-meat ("go"); (3) post-click state change visible < 400ms (label + checkmark, micro-interaction #15).

**cost:** trivial layout + one static file per workflow.

**verdict:** ADOPT 10 — direct execution of the owner's fast-import law; the first card IS the recommendation product.

---

## 69 — three-step breadcrumb: choose result → pick stack → import

**restatement:** onboarding and lane views carry a 3-step progress label so newcomers always know where they are and that the tunnel has an end.

**mechanism:** a slim (≤ 32px) inline stepper reflecting CURRENT view: question screens = step 1, lane/list/compare = step 2, detail-with-import = step 3. pure label — steps are clickable navigational anchors, not an enforced sequence (users jump around; the breadcrumb describes, never blocks). appears during onboarding and on first N visits (`cl.visits < 3`), then auto-hides for veterans; reappearable from the "start here" shelf. step states: done (mint) / current (accent) / upcoming (muted).

**simulation:** kenji, minute two, sees "choose result → pick stack → import" with the second node lit. the label tells him the shape of the whole experience in five words — there is a destination and he is one step from it. without it, an endless scroll of cards reads as "browse forever"; with it, the same page reads as "almost done". the relief of a visible exit is what keeps a newbie scrolling.

**micro-criteria:** (1) current-step marker updates ≤ 1s after view change; (2) never exceeds 3 items or 32px height (no permanent chrome noise — auto-hide after visit 3); (3) clicking a step navigates but NEVER blocks forward movement (no gated wizard).

**cost:** trivial.

**verdict:** ADOPT 7 — good orientation affordance, nearly free; risk is fake linearity — keep it a descriptive label with auto-hide, not a wizard.

---

## 70 — save a shortlist without an account

**restatement:** bookmark icon on every card + detail page saves to a localStorage "saved" list viewable in one click — no account, ever, with an honest "this browser only" label and the share-URL (60) as the cross-device bridge.

**mechanism:** `cl.saved` = array of entry ids in localStorage. bookmark toggle on cards (icon fills bottom-to-top, micro-interaction #20) and detail header. "saved" header nav renders the saved list through the SAME card/compare machinery (saved list is just a filter source — compare tray works from it). empty state: guidance + "start here" link, never blank. persistence honesty: label "saved on this browser" beside the count + "share list as link" button (60) — the static-site answer to sync. mature entries in the saved list respect the SFW toggle (placeholders when locked).

**simulation:** marcus bookmarks five candidates over a rushed lunch between calls. after the 4pm client meeting he reopens the tab: five picks intact, tray intact, compare intact. the site remembered his afternoon for him. when he switches to his home machine, the "share list as link" button bridges what localStorage can't — and the label told him upfront it would work that way, so nothing feels broken.

**micro-criteria:** (1) save toggle feedback < 200ms (icon fill animation, no re-render of the grid); (2) saved view reachable in 1 click from anywhere, compare works from it; (3) empty state renders guidance (not blank), and the "this browser only" label is visible wherever the count is.

**cost:** trivial — one storage key + one view reusing existing renderers.

**verdict:** ADOPT 9 — no-account is the static-site law; localStorage + share-URL covers the real need; the honest limitation label is what makes it trustworthy instead of sneaky-broken.

---

## 71 — detail page opens with the editorial verdict, not the creator's title

**restatement:** detail H1 = our one-line verdict; our custom name sits as the subhead; the creator's original title appears only in the provenance line — judgment first, reference second.

**mechanism:** render order in the detail template: H1 = `verdict` field (≤ 12 words, curated, CRITERIA already mandates a one-line verdict per model), H2 = our custom name + tier badge, then proof block (73), then gallery/editor's note; original civitai title + version id live in the provenance strip near the "open original" link (idea 30/92 territory). the verdict field is REQUIRED in the entry schema — missing verdict = entry doesn't ship (build-time validation, python generator fails loudly).

**simulation:** kenji opens his first detail page. before any scrolling, the page answers the only question he has — "should I use this?" — in one sentence: "the safest first pick for a recognizable face." decision made in three seconds; everything below is confirmation. the creator's original title, a 60-character community-brainstorm, is reference material and it stays in its place. he feels a person with taste talking to him, not a database.

**micro-criteria:** (1) verdict ≤ 12 words, no hedging words (build check: banned list "probably/might/possibly" fails the build); (2) our name + verdict both visible without scroll at both reference viewports; (3) original title findable within one scroll/expand (provenance strip), never orphaned entirely.

**cost:** trivial code; the real cost is curated writing — which is the product.

**verdict:** ADOPT 10 — this IS the product identity: judgment over inventory; owner law: custom names, our verdicts, manual curation.

---

## 72 — two-column detail layout: output proof left, decision proof right

**restatement:** desktop detail = gallery column (what you get) beside a sticky proof column (why/how it runs); mobile stacks verdict → proof block → import → gallery, so decision info precedes the image wall.

**mechanism:** CSS grid: left = large preview + thumbnail rail + scenario labels (54's vocabulary); right = proof block (73), verdict, editor's note (74), dependencies summary (57), import button, "open original on civitai". right column `position: sticky` on desktop scroll. mobile order via flex `order`: verdict, compact proof, import button, THEN gallery — decision before spectacle (the inverse of card surfaces, where 67's image-first is correct; detail pages answer "should I", choice cards answer "do I want"). first-viewport check at 1366×768: one full image + entire proof column + import visible.

**simulation:** marcus evaluates a persona stack for friday's client. left column is what he shows the client — the face holding across four shots. right column is what he checks for himself — license "personal-only" badge kills it for the paid campaign, and he spots it without scrolling past a single image. two audiences of his own attention, both served in one screen. no scroll-tennis between "pretty" and "allowed".

**micro-criteria:** (1) at 1366×768: ≥ 1 full preview + complete proof block + import button in the first viewport — screenshot-verified; (2) mobile order = verdict, proof, import, gallery (DOM order, not just visual); (3) sticky column never overlaps the gallery at any scroll position or viewport ≥ 1024px.

**cost:** low — grid + sticky; the mobile DOM order must be real order (accessibility + performance), not CSS shuffling alone.

**verdict:** ADOPT 9 — correct information architecture for the decision moment; borrows direction A's proof rail exactly as the codex design-lead recommended.

---

## 73 — score, tier, VRAM, base model, freshness in one compact proof block

**restatement:** a single reusable metadata panel — always the same five fields in the same order — rendered identically on cards, detail pages, and compare columns.

**mechanism:** one render function `proofBlock(entry, {compact})` used by three surfaces. rows in FIXED order: (1) score + tier badge, (2) VRAM, (3) base model family, (4) freshness (version date), (5) dependency count. mono metadata font per design direction (IBM Plex Mono / Azeret / Space Mono depending on chosen direction); each label ≤ 8 chars. order constant exported once and shared with compare (53) — grep-verifiable single source. score renders as `8.9 / 10` never stars (idea 14 law). freshness shows relative date ("updated aug 2026") with the CRITERIA staleness cap respected.

**simulation:** kenji learns the block's position ONCE, on his first card. from then on, every card, every detail page, every compare column answers "will it run on mine, is it current" from the same spot in the same order — recognition instead of reading. by visit three he's scanning five fields in under a second and calling it "the specs line". that fluency is what instantly-understandable feels like from the inside.

**micro-criteria:** (1) identical field order across card/detail/compare (single shared constant, verified by grep — no copy-pasted orderings); (2) block ≤ 5 rows forever — a sixth field joining is a design review, not a PR; (3) score format identical everywhere (`8.9 / 10`).

**cost:** trivial once built as the shared component — and building it once is the point.

**verdict:** ADOPT 10 — consistency is the mechanism of "instantly understandable"; owner law: format and order matter a lot; one component, three surfaces, zero drift.

---

## 74 — editor's note explaining the tradeoff in plain english

**restatement:** every entry carries a curated ≤ 2-sentence note naming its ONE real tradeoff; on A/B entries it doubles as the "why this is not S tier" sentence (idea 19).

**mechanism:** required `editorsNote` field in entry JSON — build fails on missing/empty (same build-time validation as 71's verdict). content rules: must name a CONCRETE tradeoff ("great face lock; outfits drift after ~30 frames"), banned: hedging filler ("your mileage may vary", "results vary"), max 2 sentences, plain english, no jargon without a glossary term (63). placement: detail page under the proof block; A/B tier entries phrase it as the not-S reason, S-tier entries phrase it as the honest cost ("fastest to learn; not the absolute best at hands"). the note is also the compare table's tiebreaker context — hovering the score row can surface it.

**simulation:** lia reads "great face lock, but outfits drift after 30 frames" on a detail page. that IS her question — she films outfit changes — answered before she knew to ask it. she picks the A-tier entry whose weakness she can live with over the S-tier whose strength she doesn't need. one sentence moved her decision correctly, which is the entire reason this library exists instead of a civitai search box.

**micro-criteria:** (1) note present on 100% of entries — build fails otherwise (enforced, not hoped); (2) ≤ 2 sentences, concrete tradeoff named (build check against a hedging-phrase list); (3) every A/B note answers "why not S" explicitly (spot-check in curation review).

**cost:** trivial code; genuine writing labor — the core curation work, not overhead.

**verdict:** ADOPT 10 — the note IS editorial trust; without it we're a directory with scores. highest writing-cost-per-word feature in the range and worth every word.

---

## 75 — trigger words beside a copy button

**restatement:** every trigger word renders as an individual mono chip with its own copy button; one click puts the exact string on the clipboard, icon flips to a checkmark.

**mechanism:** detail page (and card quick-view where present): each trigger word = `chip + copy icon` pair; click → `navigator.clipboard.writeText(word)` (github pages = https, API available) with `document.execCommand('copy')` textarea fallback for local file previews; icon flip-to-checkmark 260ms (micro-interaction #14 exactly as specced). copied payload = the word EXACTLY — no quotes, no trailing whitespace (strip in code, test asserts the clipboard string). multiple trigger words = multiple chips, each independently copyable; tooltip on chip hover: "click to copy". works in beginner AND technical modes (trigger words are recipe, not jargon).

**simulation:** kenji, sixty seconds after import: workflow loaded, prompt box open, one brown blob in his history because he typed the trigger word from memory and misspelled it. this time he clicks the chip — exact string on his clipboard, paste, generate — and the preview face appears. first generation that MATCHES the site's promise. the copy button is two millimeters of code standing between him and quitting, and it just paid for the whole site.

**micro-criteria:** (1) clipboard payload byte-identical to the field value (tested assertion, no whitespace/quote pollution); (2) checkmark feedback ≤ 260ms and reverts after ~1.5s so the next copy is discoverable; (3) multiple words = multiple chips, each copyable independently — never a comma-joined string copy.

**cost:** trivial.

**verdict:** ADOPT 10 — the highest-frequency action in the entire product (every single generation needs the trigger word) at near-zero cost; pairs with the workflow JSON to make the recipe complete.

---

# new original ideas (gaps found inside range 51-75)

## N1 — baseline column: "compare against my current pick"

**gap:** ideas 51-59 compare CANDIDATES against each other, but the real decision question is comparative against the user's PRESENT: "is it better than what I already run?" comparison without an anchor makes every switch feel like a leap.

**restatement:** any entry can be flagged "this is what I use"; every compare involving ≥ 1 challenger then auto-includes that entry as the pinned leftmost baseline column, with all deltas (55) computed against IT instead of against the best-in-table.

**mechanism:** bookmark-adjacent action on cards/detail: "mark as my current" → `cl.baseline = entryId` (one entry per type: one current persona LoRA, one current workflow — keyed per category so switching lanes doesn't drag the persona baseline into a video compare). compare renderer: if baseline exists for the compared category and is not already a column, it prepends as column 1, visually pinned (header tinted "yours"), and 55's delta chips reference the baseline column rather than the row best. removing the flag is one click on the baseline column header.

**simulation:** marcus has run the same persona workflow for two months. he adds two challengers to the tray and hits compare — his daily driver is already sitting in the left column, tagged "yours", with the challengers' score rows reading "+0.4" and "−0.2" against it. nobody made him re-add his own tool or remember its stats. the table answered his actual question — "is switching worth my friday night?" — in the framing he thinks in. he closes the tab in 30 seconds this time. a compare tool that respects your sunk cost is a tool that gets trusted with your next decision too.

**micro-criteria:** (1) baseline auto-appears in compare within one render when set for the category, zero extra clicks; (2) delta chips and highlight logic re-anchor to baseline (not row-best) when baseline present — the framing change is the feature; (3) one baseline per category max, replaceable in one click, clearable from the column header.

**cost:** low — one more localStorage key + column-prepending logic in the existing compare renderer; shares all machinery with 51-55.

**verdict:** ADOPT 8 — converts the compare module from "side by side" into "versus", which is how non-experts actually decide; cheapest emotional win in the comparison cluster.

---

## N2 — persistent per-entry setup checklist: "ready to run"

**gap:** onboarding (61-70) ends at the import click, and detail pages (71-80) list dependencies (57/78) — but the newbie journey to a FIRST successful generation spans days and multiple visits (install nodes, find models, restart comfyui). nothing in range 51-75 keeps the site useful across that gap; the import moment is treated as the finish line when it's the starting gun.

**restatement:** the "what you need" dependency list becomes an interactive checklist whose ticks persist per entry in localStorage; when every item is ticked, the card/detail earns a "ready to run" state — the site becomes a multi-day setup companion instead of a one-shot brochure.

**mechanism:** each dependency item (57's list) renders with a checkbox; ticks write `cl.setup.<entryId> = [itemIds]` in localStorage. progress surfaces in three places: detail checklist (with an encouraging counter "2 of 3 installed"), card badge (thin progress ring or "ready" dot next to the tier badge), saved-list view. all-ticked → "ready to run" state + the import button promotes to primary action. untick path exists (node uninstalled / broke). beginner mode keeps the same list with plain-language item labels ("install the face-swap add-on" + copyable real name on the item). pure client state — no accounts, no sync, same honesty label as 70.

**simulation:** kenji imports the sample persona on night one, and the checklist shows 3 missing pieces. he installs one custom node before bed. tuesday he's busy. wednesday he ticks the second item, finds the third model's civitai link right there on the checklist row, downloads it into `models/checkpoints` — the recovery copy from idea 80 told him the folder. thursday: "ready to run" on the card, import button glowing, first good generation. the site walked beside him for four days at zero server cost. without the checklist he'd have hit the first missing-node error, closed everything, and told his discord the library "doesn't work".

**micro-criteria:** (1) tick survives reload and lane switches (localStorage keyed per entry, verified); (2) progress visible from the CARD (no detail-page visit needed to know where you stand); (3) "ready to run" state appears ≤ 200ms after the final tick, with an obvious promotion of the import action.

**cost:** low — checkboxes + one storage shape + badge states; rides entirely on 57's dependency data existing. maintenance: none beyond the shared list.

**verdict:** ADOPT 8 — the only idea in the range that serves the multi-DAY reality of comfyui onboarding; converts dependency honesty (57) into a retention loop; deepens "fast import" into "fast first success", which is what the owner actually sold.

---

# range summary 51-75

| # | idea | verdict | score |
|---:|---|---|---:|
| 51 | persistent compare tray | ADOPT | 9 |
| 52 | aligned-row compare table | ADOPT | 9 |
| 53 | compare row set (VRAM-first order) | MERGE→52 | 8 |
| 54 | scenario-labeled gallery compare | ADOPT | 7 |
| 55 | delta chips, no rainbow | ADOPT | 9 |
| 56 | mini workflow graph | ADOPT | 7 |
| 57 | dependency diff list | ADOPT | 9 |
| 58 | only-differences toggle | ADOPT | 8 |
| 59 | use-with-my-rig filter | MERGE→rig profile | 8 |
| 60 | share URL + markdown export | ADOPT | 9 |
| 61 | 3-question onboarding | ADOPT | 9 |
| 62 | one complete sample persona | ADOPT | 10 |
| 63 | jargon glossary tooltips | ADOPT | 9 |
| 64 | GPU-name hardware questions | MERGE→61 | 8 |
| 65 | beginner/technical modes | MERGE→66 | 8 |
| 66 | collapsed technical sections | ADOPT | 9 |
| 67 | gallery before names | ADOPT | 9 |
| 68 | import above the fold | ADOPT | 10 |
| 69 | 3-step breadcrumb | ADOPT | 7 |
| 70 | accountless shortlist | ADOPT | 9 |
| 71 | verdict as H1 | ADOPT | 10 |
| 72 | two-column detail layout | ADOPT | 9 |
| 73 | shared proof block | ADOPT | 10 |
| 74 | editor's tradeoff note | ADOPT | 10 |
| 75 | trigger-word copy chips | ADOPT | 10 |
| N1 | baseline compare column (new) | ADOPT | 8 |
| N2 | per-entry setup checklist (new) | ADOPT | 8 |

## pattern findings (for the synthesizer)

1. **comparison cluster (51-60) is ONE module, not ten ideas.** build order: table + row-set (52+53) → deltas (55) → tray (51) → diff toggle (58) → rig filter (59) → export (60); galleries (54) and graphs (56) bolt on when curation/parser data lands. one compare renderer, one entry-JSON source.
2. **three localStorage keys power the whole range**: `cl.rig` (61/64/59 + filter bar), `cl.mode` (61/65/66), `cl.saved`/`cl.baseline`/`cl.setup` (70/N1/N2). define the storage schema ONCE before any feature code; every idea above assumes it.
3. **detail cluster (71-75) is render order + curated writing, zero code risk.** the build-time validators (verdict required, editors-note required, hedging banned) are what make the writing real — enforce in the python generator, not in review discipline.
4. **no KILL in range** — weakest are 54 and 56 (both gated on curation/parser data, both degrade gracefully); the merges (53→52, 59→rig system, 64→61, 65→66) each carry a concrete sharpening: VRAM-first row order, one rig key, GPU names not gigabytes, collapse-defaults as the mode mechanism.
5. **cross-range dependencies flagged**: URL state (idea 10, analyst 1) is prerequisite for 58/60; "start here" shelf (idea 6) is the re-entry path for 61/69; dependency parser shared with 78/89 (analyst 4); recovery-panel copy (80) is quoted inside N2.
