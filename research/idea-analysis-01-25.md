# idea analysis — ideas 1-25 (IA · ranks/trust · card anatomy)

analyst 1 of 4. inputs: research/codex-design-ideas.md (Direction B "Field Guide" = stated launch pick), docs/REQUIREMENTS.md, docs/CRITERIA.md.
static-site reality assumed throughout: vanilla JS, local JSON produced by the python generate step, images from civitai CDN only, localStorage for prefs, no runtime server.

personae used in simulations:
- **kenji** — comfyui newbie. installed ComfyUI yesterday via youtube, 6 GB laptop + a 12 GB desktop at home, does not know what a LoRA is.
- **marcus** — ad guy. sells client campaigns, thinks in deadlines and deliverables, not in models. cloud GPU, 24 GB class.
- **lia** — OF creator. non-technical, follows numbered lists, works nights, mature lane native.
- **owner** — eder. curator, nightly curation pass, shares links in discord DMs, allergic to fake greens.

owner's laws applied as the verdict yardstick: fewer clicks · instantly understandable best-per-category · results visible · fast import · format and order matter · max quality as floor.

---

## idea 1 — homepage promises an outcome, not an inventory

**restatement:** hero copy sells the result the visitor wants ("build a consistent AI persona, then turn it into an ad"), never the artifact store we host.

**mechanism:** static hero block in index.html. H1 in Bricolage Grotesque 600: "Build a consistent AI persona, then turn it into an ad." sub-line Literata: "A hand-tested shortlist of LoRAs and ComfyUI workflows. Choose the result first — we explain the rest." three primary actions: `Create a persona` `Make an ad` `Explore mature metadata` (third visually secondary + locked per gating rules). zero JS until a CTA click → navigates `?lane=…` and the lane module renders from local JSON. hero capped at ~45vh mobile so ranked cards peek below the fold — signals depth without a scroll-hint gimmick. only animation is micro-interaction #1 (title rises 8px, 420ms, transform/opacity only, skipped under prefers-reduced-motion).

**simulation:** kenji, 23:10, phone in bed. he typed "how to make consistent AI character" into reddit, a comment linked us. three seconds on the hero and he reads his own sentence back: build a consistent persona. not "browse 40,000 models" — he already closed that tab yesterday. relief first, tap second: `Create a persona`, one thumb-reach action, no account wall, no config. if the hero said "curated civitai model library" he'd have to translate library→his goal, and at 23:10 the translation doesn't happen — the back button does.

**micro-criteria:**
- outcome verb+object readable ≤3s at 375px (display ≥28px, ≤9 words)
- primary CTA above the fold at both 375×667 and 1440×900
- zero jargon tokens above the fold (no LoRA/checkpoint/embedding) — lintable in the generate step

**cost:** build low · perf none · maintenance low (copy rarely changes).

**verdict:** ADOPT — 10/10 — the homepage IS the first click; promising the outcome kills the translation hop. this is owner law "enter through a result" wearing its public face.

---

## idea 2 — lanes named by intent: Persona Studio / Campaign Lab / Mature Lane

**restatement:** lane names are jobs-to-be-done, not content types; sharpen "Campaign Lab" so non-marketers decode it instantly.

**mechanism:** three lane tabs in the sticky header (see idea 3), links to `?lane=persona|ads|mature`. data field `lane` on every entry; render = `entries.filter(e => e.lane === lane)`. mature tab renders locked (sessionStorage + confirm panel per gating spec) regardless of URL. naming micro-decision: "Persona Studio" and "Mature Lane" pass the 5-stranger test; "Campaign Lab" is premium but costs lia a decode hop — ship it with an explicit sub-label "ads & video pipelines" on the tab (tooltip on desktop, inline caption on the lane header first paint). REQUIREMENTS also names image-to-video-with-audio as its own lane — resolve as a stage-tab inside ads lane (motion+voice), NOT a 4th top-level lane: nav stays at 3 items, no wrapping at 320px.

**simulation:** lia, 14:20, laptop, second coffee, arrived from a discord link. she scans the header: Persona Studio — that's the influencer thing, not hers. Campaign Lab — one second of doubt ("campaign? I don't run campaigns"), then the sub-label lands: ads & video pipelines. ok, also not hers. Mature Lane — unmistakable, and the lock state reads as taken-seriously, not hidden-shame. she clicks, gets the calm confirm panel, continues. zero wrong clicks spent. kenji has the mirror experience: "Mature Lane" tells him instantly what to avoid without curiosity-clicking into a gated wall.

**micro-criteria:**
- each lane name passes 5-stranger test: ≥4 correctly guess lane contents from name alone
- nav = 3 top-level lanes + search; no wrap, no hamburger at any width ≥320px
- mature lane visible + identifiable as locked without any scroll (header placement)

**cost:** build low · perf none · maintenance low.

**verdict:** ADOPT — 9/10 — intent-named lanes are the IA backbone; docked one point until "Campaign Lab" carries its plain-english sub-label, because "instantly understandable" outranks "premium" in owner law.

---

## idea 3 — lanes in primary navigation, never buried in a filter menu

**restatement:** lane switching is a persistent, always-visible top-level control — one click from anywhere on the page at any scroll depth.

**mechanism:** `position: sticky; top: 0` header, 56px desktop / 52px mobile: logo (left, → home), three lane tabs, search icon + mature toggle (far right). tabs are real `<a href="?lane=x">` — middle-clickable, copyable, and functional even pre-JS because the python step can pre-render each lane page. active lane marked by traveling underline (micro-interaction #4, 220ms) + font-weight bump (two cues, colorblind-safe). mobile ≤640px: tabs compress to a 3-segment control — still visible, never a hamburger (hamburger = buried = the exact failure this idea forbids).

**simulation:** owner, 21:47, desktop, screen-sharing to a friend on discord. deep in Campaign Lab comparing video workflows, friend asks "wait — does this work for making the girl first?" owner clicks Persona Studio in the header: one click, no back button, no drawer hunt, scroll position irrelevant because the header never moved. friend: "and the horny stuff?" one more click, confirm panel, laughs, done. three lanes toured in under ten seconds. with drawer-buried lanes each switch is open-drawer → find → apply → drawer-closes, and the friend's question dies mid-sentence. the header's persistence is what makes the demo flow at conversation speed.

**micro-criteria:**
- lane switch from any scroll depth = exactly 1 click, header never hidden
- no hamburger for lanes at any viewport; 3-segment control ≤640px
- active lane identified by ≥2 non-color cues (underline + weight)

**cost:** build low · perf negligible · maintenance low.

**verdict:** ADOPT — 10/10 — "fewer clicks" verbatim; persistent nav is its mechanical expression. cheapest idea in the range with the highest interaction payoff.

---

## idea 4 — stage rail: identity → image → motion → voice → publish

**restatement:** a compact 5-stage strip that shows where each lane fits in the full journey — scope proof for newcomers and the visual grammar for lane handoffs.

**mechanism:** flex row: 8px dots + labels joined by 2px rules; stages served by a lane filled cobalt, unserved warm grey. v1 scope: homepage only, directly under the hero ("where you'll go"), plus a static text line mapping stages→lanes. clicking a stage jumps to the lane that serves it (identity→Persona Studio; motion/voice/publish→Campaign Lab) — a second nav path for people who think in pipeline stages rather than outcomes. lane-page and per-card variants (Direction A's readiness strip) are post-v1: they need a per-entry `stages` tag in curation data — a real metadata field worth adding, but not before the homepage variant proves the concept. mobile: labels drop, dots+numbers remain, ≤24px tall.

**simulation:** marcus, 11:05, office laptop between calls. friday deliverable: talking-head product video. he lands, sees the rail: identity → image → motion → voice → publish. he maps his problem onto stages 3-5 instantly, then notices the client has no persona either — stage 1 — and the rail just told him this site covers the whole chain, not just model files. that "can this site get me to a published video?" question was answered with zero clicks. the rail's job is scope proof: it sells the "then turn it into an ad" half of the hero promise before a single card is read.

**micro-criteria:**
- stranger can name which lane serves which stage in ≤10s of looking at homepage
- rail ≤5% viewport height; dots+numbers variant at ≤640px with no label truncation
- stage→lane mapping accurate for every entry (an entry tagged voice under image stage = structural lie, lintable)

**cost:** build low-med (needs `stages` field for full version; homepage v1 needs only the static mapping) · perf negligible · maintenance low.

**verdict:** ADOPT scoped (homepage v1, lane/card variants post-v1) — 7/10 — good orientation device and the grammar for the handoff loop, but it's supporting signage, not the product; over-building it pre-launch would be polish before function.

---

## idea 5 — enter through "I need a result," not "I need a LoRA"

**restatement:** every entry path is phrased as the visitor's outcome; artifact vocabulary is delayed until it's actionable — and this is enforced by a lint, not by hope.

**mechanism:** three layers: (a) hero CTAs name results (idea 1); (b) default sort in every lane is our editorial rank, so the first paint is the best RESULT preview, never a taxonomy; (c) a banned-vocab lint in the python generate step scans rendered HTML for artifact-jargon (LoRA, checkpoint, embedding, VA E, ControlNet) above the fold on home + lane first-paints — hard fail on generate. jargon's legal homes: below fold, detail technical sections, tooltips, the "What you need" checklist. pairing rule: any term's first appearance ship with a plain-english gloss (ties to idea 63's LoRA tooltip, generalized). this idea is a principle; the lint converts it from style guidance into a gate.

**simulation:** kenji, day two, 19:30, desktop, ComfyUI installed but unused. he doesn't know the word LoRA — he knows "same girl, different outfits." clicks `Create a persona`, sees cards named "Soft-Window Persona Lock" with big face grids — the RESULT is the first thing on screen. the word LoRA first reaches him inside the detail page's "What you need" checklist, at the exact moment it names a file he must download — vocabulary arriving when actionable, not when decorative. compare the civitai path: he typed "realistic," got 4,000 mixed-artifact results, had to learn the taxonomy BEFORE he could shop. we invert that.

**micro-criteria:**
- zero artifact-jargon tokens above the fold on homepage + lane first-paint (automatable, part of generate)
- landing → S-tier card detail ≤2 clicks (hero CTA → top card)
- every jargon term's first appearance paired with a gloss (spot-checkable, lintable via glossary dict)

**cost:** build low (lint + copy discipline) · perf none · maintenance low (lint runs on every generate).

**verdict:** ADOPT — 10/10 — this is the owner's "enter through result" law, and the lint makes it survive every future contributor, including future-us at edit #6 of the night (decay control).

---

## idea 6 — permanent "Start here" shelf, three safe tested entry points

**restatement:** a pinned shelf of exactly three curator-blessed COMPLETE beginner setups, always one click away, never re-ranked by the normal flow.

**mechanism:** `start_here: true` flag in curation.json, capped at 3 by the python linter (>3 = generate fails — a shelf of 8 is a grid, not a shelf). rendered as the first section of every lane page: three wide cards (same card component, larger variant) each with dominant result preview, one-line "what you get", VRAM chip, tested date, and a direct `Download ComfyUI JSON` action. shelf entries should be STACKS (idea 9) so a beginner imports ONE thing, not a parts list. header carries a `Start here` link → `?lane=x#start`, one click from anywhere. each entry also shows "why it's safe": dep count ≤3, tested ≤90d, works on 8 GB.

**simulation:** kenji, 22:15, phone on the commute. yesterday: install went fine, then civitai's 4,000-result wall, tab closed, "wtf which one" texted to a friend. tonight: opens our site, taps `Start here` in the header. three cards, full-width. card 1: "Realistic social persona — complete stack · tested this month · runs on 8 GB." twenty seconds to read all three. taps card 1, gallery shows the same face in six scenes, taps `Download ComfyUI JSON` before his stop. by the time he's home: file in downloads, one instruction sentence memorized — "drag it onto the canvas." three safe options versus four thousand raw ones is the entire difference between a second session and abandonment.

**micro-criteria:**
- exactly 3 entries; each carries tested-date ≤90d, VRAM chip, dependency count ≤3, direct import action (all lintable)
- reachable in 1 click from any page (persistent header anchor)
- every shelf entry is a complete stack — import one thing, get a working result; a bare LoRA on the shelf = fail

**cost:** build low (flag + wide card variant) · perf none · maintenance med (quarterly re-test or the shelf lies — tie to stale-state flags).

**verdict:** ADOPT — 10/10 — "instantly understandable best-per-category" in its purest form: THE three answers, permanent, safe. also the newcomer's entire first minute (codex 60-second walkthrough) compressed into one component.

---

## idea 7 — explain civitai in one sentence

**restatement:** a single line, shown at the right moments, explaining our relationship to civitai — source vs. decision layer — killing the "is this a sketchy mirror?" trust question.

**mechanism:** one sentence in the hero supporting-copy zone: "Civitai is where the original models live — this library narrows the choice to setups worth trying." repeated as: a "what's Civitai?" footnote chip on first lane visit (sessionStorage-dismissed, never nags), a permanent footer one-liner, and contextual proximity to every "Open original on Civitai" cluster where the question actually arises. vocabulary ban: mirror / scrape / catalog (trust vocabulary lint, same family as idea 5's jargon lint). the provenance line on detail pages (idea 92, colleague range) does the deep version; this does the fast version.

**simulation:** marcus, 16:40, office. not an AI person; his intern said "check this site." he sees "Open original on Civitai" on cards and the trust question fires: is this official? reselling? pirated? the hero one-liner settles it — civitai is the vineyard, we're the sommelier. value prop AND attribution ethics in one breath. without it, "civitai-library" pattern-matches to a mirror site, and mirror sites pattern-match to malware; he'd have bounced with the question unasked. with it, he understands the product is the FILTER, which is exactly the thing he'd pay for.

**micro-criteria:**
- ≤25 words, answers both "what is civitai" and "what is this site," present above the fold on homepage
- appears near "Open original" clusters (contextual, not nagging)
- zero banned trust-vocabulary tokens in any user-facing string (lintable)

**cost:** build trivial · perf none · maintenance none.

**verdict:** ADOPT — 8/10 — zero-cost trust fix; also satisfies the owner's link-back ethic at the narrative level, not just the link level. docked from 9-10 only because it is support copy, not structure.

---

## idea 8 — Models and Workflows as tabs inside every lane

**restatement:** a two-tab type switch inside each lane (Models | Workflows) so the two different questions never share one mixed grid.

**mechanism:** sub-tab row under the lane header, visually distinct from lane tabs (smaller, pill-style). `entry.type` filters the lane array; tab state lives in the URL (`&tab=workflows`, rides idea 10). count badges on both tabs before clicking ("Models 12 · Workflows 7") so shelf depth is visible pre-commit. default tab is a per-lane data flag, not a global rule: persona lane defaults to Models (people come for faces), ads lane defaults to Workflows (people come for pipelines) — defaults follow the lane's primary job. keyboard: ←/→ switch tabs when the row has focus. tabs are real links (middle-click safe). with idea 9 adopted, this becomes a 3-tab row where a lane has stacks (Models · Workflows · Stacks).

**simulation:** two sessions. owner, 20:12, nightly curation pass: clicks Workflows tab (badge says 9), scans the ranked list, sees two new entries sitting at B with `TESTED ONCE` labels — mental note queued for tomorrow. the tabs serve his curator scan as much as the user's. and owner-as-user, next evening, wants "the best checkpoint for faces": Models tab; then "the pipeline that turns a still into a 15s ad": Workflows tab. two different questions, two tabs. the alternative — one mixed grid — forces a mental type-sort on every scan of every row, a tax paid hundreds of times per session for zero benefit.

**micro-criteria:**
- tab switch = 1 click, preserves lane + active filters, reflected in URL
- count badge visible on both tabs before any tab click
- default tab differs per lane and is one data flag (not hardcoded per page)

**cost:** build low · perf none · maintenance none.

**verdict:** ADOPT — 9/10 — owner requirement verbatim ("tabs: workflows AND models"); the lane-conditional default is the micro-decision that makes it feel intelligent instead of uniform.

---

## idea 9 — Stacks: complete combinations as a first-class entry type

**restatement:** a third entry type — the stack — bundling base model + LoRA(s) + workflow + tools into ONE scored, importable unit; the library graduates from parts store to ready meals.

**mechanism:** stacks.json: `{id, name, lane, components:[{role, entryId}…], vram, tested_on, score, confidence}`. rendered as a third sub-tab (with idea 8) where stacks exist. stack card: dominant RESULT preview (the output of the combination, never component thumbnails), component chip row `z-image base → persona LoRA → portrait workflow` with each chip linking to its entry's detail page in a new tab (mid-journey context preserved). import: primary button downloads the workflow JSON — our manifest embedded in its metadata; since zips are banned by CRITERIA kill-lines, the stack detail's "What you need" checklist lists components in install order, each with its own import link (fast-import law: one click per component, ordered). stack score is scored as a UNIT (tested together), never an average of component scores — averaging launders incompatibility. v1 phasing: one stack per lane (3 total) doubling as the Start-here shelf (idea 6) — the editorial cost of testing stacks is real, so start where the payoff multiplies.

**simulation:** lia, 01:20, laptop in bed, dark room. node graphs scare her; numbered lists don't. Persona Studio → Stacks tab. "Soft-Window Persona Lock — full stack": the same girl across 8 photos, chips reading `z-image base → persona LoRA → portrait workflow`, `12 GB` chip (her 4070, fine). one button: download workflow JSON. one instruction: "drag onto ComfyUI — it names the 2 files to fetch." she never wanted a LoRA; she wanted the GIRL, and the stack is the girl. this is the single highest-empathy component in my range: it converts three decisions + an ordering problem into one decision. kenji's shelf experience (idea 6) is literally this moment.

**micro-criteria:**
- stack card shows 1 dominant result preview + component chips + single primary import action (never a component collage)
- stack has its OWN curation record tested as a unit; averaging component scores = lint fail
- component chips open entry details in new tab without losing the stack context

**cost:** build med (new data type + relation rendering) · perf low (tiny JSON) · maintenance med-high (a stack is a promise: re-test on any component update — the price of the strongest trust claim).

**verdict:** ADOPT — 10/10 — owner requirement "best flows → for best models" IS the stack; highest editorial cost in my range but the only structure that serves lia and kenji (the non-technical majority) at 1am. phased 3-stack v1.

---

## idea 10 — full state in the URL: every view shareable

**restatement:** lane, tab, filters, sort, search, compare selection — all serialized into the URL; reload and share reproduce the exact view; back/forward work.

**mechanism:** URL is the single source of truth: `?lane=ads&tab=workflows&vram=12&sort=fresh&q=lip` (+#cmp anchors for compare). one ~100-line state module: parse on load → apply → render; on every state change → `history.replaceState` (replaceState for typing/filters = no history spam; pushState only for view-level jumps like lane switches). popstate handles back/forward. deliberate exception: mature toggle is NEVER a URL param — deep links to `?lane=mature` land SFW + confirm panel per gating spec. share affordance: link icon on filtered views → `navigator.clipboard.writeText(location.href)` + toast "Link copied." works on github pages because query strings hit the same index.html. debounced `q=` writes so typing doesn't thrash.

**simulation:** owner, 18:55, discord DM: "which LoRA for faces on 8gb?" old-world answer: "go to civitai, search realistic, sort by…" — three instructions, a screenshot, friction. new-world: he sets the view (Persona · Models · VRAM=8), clicks the link icon, pastes. his friend opens ONE exact view: the two cards that matter, zero words. later, 21:30, owner hard-refreshes mid-curation out of habit — page reopens exactly where he was, filters intact. for a zero-budget github-pages site, shared links ARE the growth engine; this idea is the engine's transmission. it is also the substrate ideas 60 (share shortlist) and 100 (one-minute route) stand on — both in colleague range.

**micro-criteria:**
- reload reproduces view 100%: lane, tab, every active filter, sort, search, scroll-to anchor
- link opened in a fresh browser (no localStorage) reproduces the same view AND mature stays gated
- back/forward traverse state without dead ends or filter amnesia

**cost:** build low-med (one module) · perf none · maintenance low (one param name per new filter).

**verdict:** ADOPT — 10/10 — shareability is free distribution; reload-survival is free UX; and it makes every other stateful idea in the 100 (filters, compare, onboarding hand-off) honest by construction.

---

## idea 11 — S tier defined as "first pick for production"

**restatement:** S is a sentence, not a number: the badge always carries its definition — "first pick for production" — and the definition is backed by the CRITERIA gates so it cannot be decorative.

**mechanism:** tier definitions live in one constants object mirrored by the python linter: `S = "First pick for production"`. surfaces: (a) badge accessible-label + hover/tap tooltip (tap on mobile shows the tooltip, does not navigate — first tap explains, second commits); (b) a one-line legend row pinned above every ranked grid, expanded on first visit per session ("S first pick for production · A reliable, one caveat · B niche match"), collapsible thereafter; (c) lint enforcement: an S entry missing the external-validation receipt or curator verification fails generate — the sentence must be TRUE, and truth is machine-checkable against the curation record.

**simulation:** kenji, 22:40, phone, first pass through Persona Studio. an "S" badge — S for what? size? stars? with the definition attached, the badge self-explains: "S — first pick for production." the claim lands differently than "top rated": it says the curator SHIPS with this, and the detail page (idea 18's tested-rig chip, colleague-range idea 90's tested-by-us mark) backs the claim with receipts. kenji already learned this week that civitai's "most downloaded" means most downloaded, not best — our S is positioned as the exact opposite: a verdict with a definition and a paper trail.

**micro-criteria:**
- badge explains itself on first hover OR first tap (tooltip before navigation)
- legend row visible above the first card on first visit in a session
- zero S-tier entries without external-validation + curator-verified receipts (generate-time lint against CRITERIA gates)

**cost:** build low · perf none · maintenance low.

**verdict:** ADOPT — 9/10 — tier semantics are the site's trust currency; "first pick for production" is the human sentence for CRITERIA's S-gate. not 10 because alone it's a label — its power arrives with 12/17/18.

---

## idea 12 — A tier defined as "reliable with one known caveat" (caveat REQUIRED)

**restatement:** A is dependable-but, and the "but" is a mandatory, concrete, card-visible sentence.

**mechanism:** same legend system as 11. structural enforcement: every A-tier entry carries `caveat: "…"` — python lint fails generation for any A entry without one, and fails again if the caveat is disguised praise ("only downside: it's popular"). rendering: on the card as a quiet line under the purpose line; on the detail page inside the Editor's note, set bold. caveat budget ≤15 words, must name observable behavior ("lip sync drifts past 8 seconds") not adjectives ("can be inconsistent"). NOTE: this field and idea 19's "why not S" are the SAME data for A-tier — see idea 19's merge verdict; one source of truth.

**simulation:** marcus, 09:15, office coffee, planning a client pitch for friday. Campaign Lab, comparing video workflows. card 2, A-tier: "reliable with one known caveat — lip sync drifts past 8 seconds." that one sentence just prevented him from discovering the drift live in front of a client. he books the S-tier for the hero shot and pockets this one for B-roll clips under 8s — the caveat didn't demote the tool, it made the RATING believable. a system that names flaws reads as tested; one that doesn't reads as marketing.

**micro-criteria:**
- ≤15 words, concrete + observable behavior, lint-rejected if generic or if it restates a strength
- caveat visible ON the card (decisions happen at card level, not detail level)
- no A-tier entry ships without it (generate-time hard fail)

**cost:** build trivial · perf none · maintenance low (one field per A entry).

**verdict:** ADOPT — 9/10 — pairs with 11 to make tiers testable claims; the required-caveat lint converts editorial honesty from intention into infrastructure. (merged data model with idea 19 — see there.)

---

## idea 13 — B tier defined as "worth using when its niche matches" (drives LAYOUT)

**restatement:** B is explicitly niche-scoped — and the tier doesn't just label the card, it changes the card's SIZE: S gets hero cards, A standard, B compact rails.

**mechanism:** legend row completes (11+12+13). B entries REQUIRE `best_when` (that field IS idea 24 — merged here): "Anime key-light pack — best when: cel-shaded scenes with hard shadows." layout grammar: tier → component. S = one large hero card (left-anchored, Direction B's "lead preview" slot); A = standard cards; B = compact rail cards ≥40% shorter, denser, quieter. this encodes "format and order matter" structurally: tier is read from geometry before it's read from the badge. a stranger sorting 9 mixed cards into S/A/B by layout alone should land ≥80% correct. B rail's best-when lines render like a specialty menu — the long tail becomes browsable instead of noise.

**simulation:** lia, 15:30, Mature lane (unlocked). B card: "Anime key-light pack — best when: cel-shaded scenes with hard shadows." she shoots realistic content — half-second scroll-past, zero cost. kenji, three weeks later, hunting a stylized VTuber look: he stops at that exact card, because the best-when line matches his intent precisely. B done right is a labeled drawer: the wrong person skips instantly, the right person finds exactly. B done wrong (equal-prominence cards) is the civitai wall rebuilt inside our own site — the disease we exist to kill.

**micro-criteria:**
- 100% of B cards carry a concrete best-when clause (lint); S/A show it when it discriminates beyond the verdict line
- B cards measurably more compact than A (≥40% height reduction — layout grammar encodes tier)
- mixed-sort stranger test: tier identifiable from layout alone ≥80%

**cost:** build low (two card sizes + a field) · perf none · maintenance low.

**verdict:** MERGE (absorbs idea 24's field; tier-driven layout is the adopt) — 9/10 — the merge kills a redundant idea and the layout grammar turns ranking into something you see before you read.

---

## idea 14 — score as `8.7 / 10`, never stars

**restatement:** numeric one-decimal score in mono type; stars banned because 5-bucket quantization destroys exactly the resolution our curation exists to expose.

**mechanism:** score renders in Azeret Mono: `8.7` large + `/10` small, tabular numerals so ranked lists align. direct map of CRITERIA (displayed = composite/10, one decimal). placement: card = top-right of the proof strip; detail = inside the compact proof block (idea 73, colleague range). no value-based color coding (color reserved for tier accents); no star glyph anywhere — lint greps rendered HTML for ★ and fails on hit. score-fill bar animation (micro-interaction #8) reserved for detail pages only — cards stay static-numeral (Direction B restraint). rationale made mechanical: 8.6 vs 8.8 is a defensible curation statement; both are ★★★★★ and the argument dies.

**simulation:** owner, 13:20, weekly re-rank. two persona LoRAs sit at 8.6 and 8.8. with stars, both read 5/5 and his ordering looks arbitrary; with decimals, the .2 gap is a public claim he can defend by opening the axis table one click away. marcus-side, 04:00 deadline: ★★★★☆ versus ★★★★★ is a coin-flip vocabulary; `8.7` with the justification line (idea 15) underneath is an answer. the numeral is auditable; stars are vibes wearing geometry.

**micro-criteria:**
- one decimal always, mono font, right-aligned, tabular numerals (list alignment test)
- zero star glyphs in any rendered HTML (grep lint)
- no color-encoding of score values (colorblind-safe by construction)

**cost:** build trivial · perf none · maintenance none.

**verdict:** ADOPT — 10/10 — CRITERIA verbatim (1-10, one decimal); the format IS the curation's resolution. banning stars is not taste, it's information preservation.

---

## idea 15 — named justification directly under the score

**restatement:** one sentence of WHY, physically adjacent to the number — the score says where, the sentence says why, and they never travel apart.

**mechanism:** field `verdict_line` (already exists in CRITERIA model-side as "our verdict line"). card: directly under the score numeral, ≤15 words. detail: same line opens the entry above the fold (feeds idea 71, colleague range). same field, two placements, never divergent (one source of truth). lint applies a swap-test: a verdict line that would fit ≥3 other entries unchanged ("great quality model") fails; the line must carry a comparative claim tied to the lane's job ("best identity lock under changing light", "fastest still→15s ad", "most consistent lip sync, heavier rig"). this line is Direction B's signature element — the blunt editorial verdict — and the single highest value-per-pixel string on the card.

**simulation:** marcus, 10:02, between meetings, 45 seconds. scanning Campaign Lab's top cards: card 1 reads 9.1 — "The fastest path from still to 15-second ad." the sentence enters pre-chewed: he thinks in ad-seconds. card 2: 8.8 — "Most consistent lip sync, heavier rig." two sentences and he now knows the category's tradeoff AXIS (speed vs sync vs rig weight) without opening either detail page. each verdict line saves one click for every visitor forever — that is compounding interest on fifteen words of editorial writing, which is why the writing burden in the cost slot is a bargain, not a tax.

**micro-criteria:**
- ≤15 words, contains a comparative/superlative claim tied to the lane's job
- identical string on card and detail (field-level single source, no drift)
- swap-test lint: line must not survive unchanged when transplanted to 3 sibling entries

**cost:** build trivial · perf none · maintenance low (the editorial writing IS the curation job — not overhead on it).

**verdict:** ADOPT — 10/10 — the score without the why is a number; with the why it is the product. Direction B's signature made structural, and owner's "our verdict line" requirement verbatim.

---

## idea 16 — editor score separated from community signal

**restatement:** two data tracks, two visually separated clusters on every card — our tested verdict and the crowd's behavior — never blended into one number.

**mechanism:** card proof strip splits: LEFT cluster = ours (tier badge, `8.7`, verdict line — cobalt accents); RIGHT cluster = community (downloads 42k · thumbs 3.1k · "used in 380 posts" — warm grey, mono, smaller, each stat carrying a pulled-date tooltip per CRITERIA `{value, window, pulled_at}` honesty rule). usage ("used in N posted images") gets the most weight inside its cluster — it's the farm-resistant core signal per CRITERIA anti-farm block. lint: no user-facing field may combine editor + community values into a single displayed "overall" — blending is civitai's original sin (download counts laundering quality) and structurally forbidden here. hover/tap on community stats reveals the date ("pulled 2026-08-27") so staleness is honest.

**simulation:** kenji, 20:50, desktop, comparing two persona models. A: editor 9.0, community "12k downloads · 40 posts using it." B: editor 7.2, community "180k downloads · 2.1k thumbs · 900 posts." on civitai B wins (raw counts). here, the split makes him ask the RIGHT question: crowd loves B, tester ranks A far higher — why? one tap into A's detail axis table: preview honesty — B's showcase images don't match its output; A delivers what it shows. he came in trusting crowds; the layout taught him the difference between popularity and delivery in one card glance. that education is the decision layer's entire value proposition, delivered by layout alone.

**micro-criteria:**
- two clusters distinguishable by ≥2 non-color attributes (size, weight, label prefix); stranger test: "which half is the site's own verdict?"
- every community stat carries its pulled-date (tooltip or inline)
- zero blended/overall numbers anywhere user-facing (lint on render output)

**cost:** build low · perf none · maintenance low (dates refresh with each pull).

**verdict:** ADOPT — 10/10 — CRITERIA's anti-farm architecture only means something if the presentation keeps the tracks separate; this is the data model's public face and the trust thesis in one component.

---

## idea 17 — confidence labels: high confidence / tested once / needs more testing

**restatement:** every score carries its own epistemic state — how hardened is this verdict — in exactly three vocabulary values.

**mechanism:** field `confidence: high|once|untested`, rendered as a mono micro-tag beside the score: `HIGH CONFIDENCE` (cobalt), `TESTED ONCE` (neutral grey), `NEEDS MORE TESTING` (coral outline — warning, not shame). curation SOP encoded in lint: `high` requires ≥2 distinct-scenario runs + community cross-check; `untested` entries are tier-capped below S (score-without-confidence also fails generate — label present on 100% of scored entries). detail page expands to one line of evidence ("2 rigs · 3 scenes · 40 generations · cross-checked against 3 community threads"). exactly three values — no 5-level false precision; the difference between them must be behaviorally meaningful.

**simulation:** owner, 23:30, night curation: just ran a new minimax workflow once, looks strong, promotes it to A 8.4. he tags it `TESTED ONCE` — he knows once-run A-tier is how liar libraries get built, and the label lets him be honest without burying a promising entry. two days later marcus hits the card: A-tier, 8.4, TESTED ONCE — his friday-deadline math silently treats it as 7.5-probable; he ships the S pick for the client and bookmarks this one for next week's internal test. both of them behaved correctly BECAUSE the label existed: owner didn't under-rank out of caution, marcus didn't over-trust out of hunger. a score with a confidence state is a claim; without one it's a bluff.

**micro-criteria:**
- present on 100% of scored entries (lint: score without confidence = generate fail)
- untested entries never S and flagged before first click
- vocabulary locked to exactly 3 values (no gradients of false precision)

**cost:** build low · perf none · maintenance low (the discipline is the same testing the criteria already mandate).

**verdict:** ADOPT — 9/10 — the trust moat: honesty about our own test depth. it is what separates a curated library from an affiliate link farm wearing tier badges.

---

## idea 18 — score provenance: hardware + base model that produced it

**restatement:** every score shows the rig and base it was tested on — an 8.7 on 24 GB/flux is not an 8.7 on 8 GB/SDXL, and the card admits it.

**mechanism:** two mono chips in the proof strip + detail proof block: `TESTED: RTX 4070 · 12 GB` and `BASE: z-image turbo` (base derived from entry data; rig is manual curation field `tested_on`, sibling of idea 17's evidence). human hardware labels (idea 26, colleague range — shared data): "8 GB laptop / 12 GB desktop / Cloud". detail page lists every rig tested with date + tested resolution; the score's primary provenance is the rig that produced it. interplay: when a VRAM filter (colleague range 32/33) is active, entries scored on bigger rigs keep their chip visible — no hiding, just standing context next to the filtered list. multi-rig: primary = the score's origin rig; others listed in detail. no averaging across rigs.

**simulation:** kenji, 19:45, 6 GB laptop. sees an S-tier 9.2 — excitement — then the chip: `TESTED: RTX 4090 · 24 GB`. honest deflation instead of dishonest hope. the alternative is: he downloads 12 GB of files, waits 4 minutes per image with offloading, concludes "this site's picks are trash," leaves forever. with the chip he instead taps the VRAM filter once and sees the S pick FOR HIS RIG — 8.6, tested at 8 GB. the chip converts silence into engineering transparency. marcus-side: the BASE chip tells him whether this persona LoRA matches the checkpoint he already has — one chip saving a download-and-fail cycle.

**micro-criteria:**
- chips on 100% of scored entries (lint), mono ≥12px, legible at card scale
- hardware label human-tiered, not GPU-model soup (map via idea 26 labels)
- detail page lists all rigs + dates + resolution; provenance auditable one click from any score

**cost:** build low · perf none · maintenance low (one manual field; multi-rig optional).

**verdict:** ADOPT — 9/10 — makes our numbers auditable claims instead of opinions; the direct enabler of VRAM-first filtering philosophy (colleague range) working at card level.

---

## idea 19 — "why this is not S tier" on every A and B entry

**restatement:** the anti-pitch: each non-S entry names the specific gap that holds it back — and for A-tier, that sentence IS the caveat (one field, not two).

**mechanism:** MERGE ANALYSIS: for A-tier, "reliable with one known caveat" (12) and "why not S" (19) are the same fact — the caveat IS the blocker. keeping both fields invites divergence and double writing. unified model: A entries carry `caveat` (serves 12+19, lint-required); B entries carry `best_when` (13/24) PLUS `not_s_because` defaulting to one of two honest shapes: "S pick does X better" (dominated) or "niche: only Y" (narrow) — curator picks or writes one line. rendering: A card → caveat line; B card → best-when line, with not-S visible in detail's editor note; both traceable on the detail page's axis table (not-S "because external validation missing" → the axis row shows exactly 0/15).

**simulation:** lia, 02:10, Mature lane. A-tier "Soft focus boudoir set, 8.3 — not S because: the S pick holds eye contact better in low light." she shoots mostly daylight window content — the S pick's stated advantage does not apply to her. she takes the A. the why-not line didn't just explain the ranking: it handed her the comparison axis needed to DISAGREE with our ranking for legitimate reasons. that is the deepest trust tier — rank, explain, and let the visitor overrule with cause. the alternative (A with no why) reads as "we liked the other one more": arbitrary, ignorable, exactly what tier systems usually are elsewhere.

**micro-criteria:**
- A-tier: single `caveat` field serving 12+19; lint forbids both fields existing with divergent text
- B-tier: not-S names the dominator or the narrowness — never "taste"
- detail page: the not-S reason traceable to a specific axis row (the sentence must be checkable)

**cost:** build trivial · perf none · maintenance low.

**verdict:** MERGE with 12 (A: caveat==not-S) — 9/10 — the merged model is tighter than two parallel reason fields, and the merge itself is the win: less data, more truth, lint-enforced.

---

## idea 20 — score deltas displayed when entries move after re-testing

**restatement:** score history is public — `8.4 → 8.7 ▲0.3` chips show movement across re-tests, making rankings feel alive and accountable.

**mechanism:** curation record keeps `score_history: [{score, date, note}]`; CRITERIA's snapshot discipline (`{value, window, pulled_at}`) extends to scores naturally. card renders latest delta as mono chip `▲0.3 aug` (arrow + sign + magnitude + month — colorblind-safe: direction never color-only, always glyph+number). history <2 → NO chip rendered (honest absence; first batch says "no history yet", the criteria doc's own pattern). every delta expands (tap) to its one-line reason ("retested on second rig; node compat fixed"). detail page carries the full list — this is the card-level surface of idea 97's editor changelog (colleague range): 20 = the chip, 97 = the ledger; share the data, split the surfaces.

**simulation:** owner, sunday 21:00, weekly re-test: the minimax workflow from idea 17 gets its second rig run — 8.4 → 8.7, note "fixed node compatibility." monday 08:50, marcus (bookmarked it at 8.4, TESTED ONCE) reloads: `8.7 ▲0.3` and the tag now reads HIGH CONFIDENCE. he doesn't re-read a thing — the chip says "this got better while you were away." that is a return-visit hook for the price of one chip. it also disciplines the owner: a score change is a public act people SAW the old value of, so re-tests are defensible events, not mood swings. library sites die when visitors suspect the numbers are vibes; deltas make the numbers accountable.

**micro-criteria:**
- chip = direction glyph + magnitude + month, ≤10 chars, expands to reason note
- no chip when history <2 (never render placeholder movement)
- deltas must match the score_history ledger exactly (rendered from it, never hand-edited)

**cost:** build low · perf none · maintenance med (re-testing is the subscription price of living scores — but that discipline is already the curation job per CRITERIA freshness axis).

**verdict:** ADOPT — 8/10 — alive, auditable rankings; docked to 8 because its full value is gated behind ≥2 test cycles existing — v1 ships the plumbing, the payoff arrives with the first re-test.

---

## idea 21 — one dominant preview per card, never a collage

**restatement:** the card's top is ONE strong result image; extra examples live behind hover-strip/swipe, never as a flat grid of unreadable equals.

**mechanism:** card top = single img in a locked box (`aspect-ratio` fixed: 4:5 portrait lanes, 16:10 workflow outputs — doubles as idea 98's no-layout-jump guard, colleague range). hero image is CURATOR-ASSIGNED: the one image that proves the verdict line (verdict says "identity lock under changing light" → hero shows same face, different light) — never the source's first image by default. interactions: desktop hover → mini-thumb strip (4 dots) slides onto hero's bottom edge, hovering a dot crossfades hero (220ms, micro-interaction #13); mobile → swipe (touch handlers, ~30px threshold) + dots. loading: hero `loading=lazy decoding=async` + next-1 preloaded on IntersectionObserver approach; strip thumbs load on first interaction only. perf win vs collage: first viewport loads ~12 images instead of ~60.

**simulation:** lia, 14:05, phone, couch, thumb-scrolling Mature lane. hero: one full-width portrait, the face fills a third of the frame — skin texture and eye consistency actually judgeable at 375px. swipe: crossfade, different outfit, same face. swipe: different pose. three swipes and the identity-lock quality is a known fact, no detail-page visit needed for go/no-go. the collage alternative gives her six ~90px thumbnails: faces too small to judge lock quality, so EVERY candidate costs a tap into detail — 6 taps become 3 swipes, and the first-impression tap-out risk dies. the dominant preview is the card designed around her actual decision (face consistency at a glance), not around our possession of six images.

**micro-criteria:**
- hero ≥60% of card area; single subject judgeable at 375px (thumbnail blur test: face survives as distinct subject)
- hero image curator-picked to PROVE the verdict line (not source order); field `hero_image_id` in curation data
- swipe/dot swap ≤220ms crossfade, zero layout shift, next image preloaded before swap

**cost:** build low-med (swipe handlers + crossfade) · perf: net WIN (12 imgs vs 60 on first paint) · maintenance low.

**verdict:** ADOPT — 10/10 — "results visible" verbatim; the only mechanism that makes results visible AT CARD SCALE. also the biggest perf lever in the range — the correct choice is also the fast one.

---

## idea 22 — custom english result-names ("Soft-Window Persona Lock")

**restatement:** every entry gets OUR 2-4 word english coinage naming the result; the source's original title survives as provenance metadata, never as headline.

**mechanism:** curation fields: `name` (ours) + `original_name` (source, shown in the detail provenance line "originally 'xxxLora_v3final' on civitai" — attribution honesty, feeds idea 92, colleague range). naming convention lint-enforced: 2-4 words, ≤24 chars, pattern [qualifier/domain]+[role noun]; rejects version suffixes (v2/final/fix), creator handles, base-model names in the title, non-english. uniqueness lint: no two entries share a confusable name stem. search indexes BOTH names (ours for intent, original for civitai-habituated users — feeds colleague-range 48). owner requirement verbatim: "custom names, titles, rankings — our platform naming."

**simulation:** kenji, 21:15, telling a friend on discord: "use the one called… 'realvisxl v3 preview turbo' or something" — friend finds four near-identical names on civitai, two of them sketchy merges. following week, same conversation about our site: "use Soft-Window Persona Lock." zero ambiguity, one result — and the name itself already explained the job. the name is the verdict line compressed until it can travel mouth-to-mouth. lia-side: `sdxlNsfw_net18_v4` tells her nothing; "Nightclub Glow Set" tells her the vibe. custom names are the difference between a library for curators and a library for humans, and they compound: every name is a tiny ad for the site's judgment.

**micro-criteria:**
- 2-4 words, ≤24 chars, english, names the RESULT not the tech (lint)
- original title preserved + visible in provenance (never orphaned — attribution + dedupe with civitai search)
- name-stem uniqueness across the library (lint)

**cost:** build trivial · perf none · maintenance: ~30s/entry of naming labor — which is the owner's stated curation model.

**verdict:** ADOPT — 10/10 — owner requirement verbatim; the naming layer is the brand moat (names outlive links in conversations).

---

## idea 23 — purpose line above technical metadata

**restatement:** card reading order is what-it's-for first, specs second — enforced by DOM order equaling visual order, so the scan path and the accessibility path agree.

**mechanism:** card text stack (top→bottom): name (+VRAM chip, idea 25) → PURPOSE line (≤12 words, what this gets you: "a face that stays recognizable across outfits and locations") → proof strip (tier · score · verdict · confidence) → community cluster. DOM order = visual order, no CSS reordering — screen readers scan the same path eyes do. typography carries the hierarchy: purpose in Literata ~14px (human sentence), metadata in Azeret Mono ~11px (machine enum) — Direction B's editorial voice made structural. purpose ≠ verdict (15): purpose orients a newcomer ("a face that…"), verdict justifies the score ("best X under Y"). both live on the card one line apart; when they collide in meaning (common on S), the detail page still shows both separately — the card compresses, the record never does.

**simulation:** marcus, 16:20, airport, phone, 4 minutes before boarding. scanning Campaign Lab cards between glances at the gate. each card reads in order: name → purpose ("turns one product photo into a 15s reel") → chips (can my rig run it). he never parses a node list, a version hash, or a base-model enum to learn WHAT THE THING IS FOR — the purpose line did the translation before the specs demanded interpretation. on civitai that translation is the visitor's job: read description, check gallery, infer use case. four airport minutes, two products shortlisted, boarding. purpose-first is what makes the site legible at human speed — and human speed is often four minutes.

**micro-criteria:**
- purpose ≤12 words, names the OUTCOME ("a face that…"), never the mechanism ("a LoRA that…") — lint
- DOM order: name → purpose → specs (verified by screen-reader pass: audio order matches visual)
- no spec line out-sizes the purpose line (typography hierarchy measurable: ≥2px + font-family shift)

**cost:** build trivial · perf none · maintenance low (curation field, sibling of verdict).

**verdict:** ADOPT — 10/10 — "format and order matter a lot" verbatim; for a decision library, reading order IS the product.

---

## idea 24 — "Best when" line naming the exact use case

**restatement:** each entry declares its sweet-spot scenario — the specific job where this tool is the right answer; for B-tier it's the reason the entry exists at all.

**mechanism:** field `best_when`, merged into idea 13's analysis (13/24 are one field with tier-dependent prominence): REQUIRED on B (their reason to exist, most prominent line on the B rail card), optional on A, shown on S when it discriminates beyond the verdict (lint allows S omission only when redundant with verdict_line). rendering: card metadata cluster, prefixed `Best when: cel-shaded scenes with hard shadows`; detail proof block gets room for two clauses ("midshot portraits · daylight or single-source light"). scenario text is indexed into search content — querying "hard shadows" surfaces the B card even though no name/tag carries it (feeds colleague-range 41/48). lint: must contain ≥1 concrete visual/usage noun; abstractions ("when you want quality") rejected.

**simulation:** kenji, three weeks in, 22:30 — graduating from "make any face" to "make THIS style." Persona Studio B-rail: "Anime key-light pack — Best when: cel-shaded scenes with hard shadows." until this line, the B rail was invisible to him (13's compact layout). now it reads like a menu of styles: six best-when lines scanned like a wine list, "ink-outline look" matches his VTuber plan exactly. the line turned the long tail into a specialty shelf. and it protects in reverse: an S-tier whose best-when reads "studio portraits" honestly tells him it is NOT for his action-scene idea — the line cuts both ways, which is exactly why it must be specific rather than flattering.

**micro-criteria:**
- ≥1 concrete scenario noun per line (lint rejects abstraction)
- B-tier: 100% required (generate fails otherwise); S/A: shown when it adds discrimination
- indexed in search content (scenario query surfaces the entry — testable)

**cost:** build trivial · perf none · maintenance low.

**verdict:** MERGE (executed inside idea 13 as the unified reason-field family) — 9/10 — one field, three tier-dependent prominence levels; the B rail graduates from discard pile to specialty menu.

---

## idea 25 — VRAM next to the title, not at the card bottom

**restatement:** the hardware-fit number occupies title-row real estate — VRAM is a first-order eliminate-or-keep fact, so it's parsed during the name scan, not after falling in love with the preview.

**mechanism:** VRAM chip sits on the NAME row (same line desktop, directly under name on narrow mobile — never demoted below the purpose line at any breakpoint). mono chip, warm-grey bg: `12 GB`, `8 GB laptop`, `Cloud` (idea 26's human labels, colleague range — shared data), tooltip ties to the tested rig ("tested on RTX 4070 desktop" — idea 18's field). placement rationale, mechanical: F-pattern scans read title rows; VRAM in the title row is judged pre-consciously during the name scan. VRAM at card bottom produces the worst failure mode in discovery UX: love the preview → read specs → "requires 12 GB" → deflation — an investment-then-betrayal loop that teaches visitors our recommendations don't apply to them. with VRAM filters active (colleague range 32/33) the chip stays constant — the filter does the hiding, the chip does the informing.

**simulation:** kenji, 20:10, 6 GB laptop, first minute in Persona Studio. he knows nothing about VRAM budgets — that's why he's here. scanning title rows: "Soft-Window Persona Lock [12 GB]" — the chip met his eye during the name read, impossible to miss. three cards down: "Natural Portrait Anchor [6 GB]" — his number. before opening one detail page, his eye has partitioned the lane into mine / not-mine. the killed failure: open the S-tier first, fall for the gallery, two minutes in hit "requires 12 GB" at the page bottom, close the tab, distrust the site forever. marcus-side (cloud, 24 GB): every chip reads "accessible" — zero cost, ambient confirmation the whole shelf is available to him.

**micro-criteria:**
- chip on the name row at every breakpoint ≥320px (never below purpose line)
- human-readable label + tested-rig tooltip (shared field with idea 18)
- 10px-blur scan test at 375px: name and chip survive as two distinct blobs parsed in one 1-second glance

**cost:** build trivial · perf none · maintenance none.

**verdict:** ADOPT — 10/10 — colleague-range idea 32 says "VRAM first because it eliminates impossible options" — this is where "first" physically lives: at the name, before the heart gets involved.

---

# TWO NEW ORIGINAL IDEAS (gaps found inside 1-25 territory)

## new idea A — provenance cluster on the card: `TESTED: 12 GB · AUG '26`

**born from gap:** REQUIREMENTS says "workflow age/recency visible" — but every freshness idea in the 100 (49 search-by-freshness, 86 proven/latest sort, 96 stale state) is a search mode, a sort mode, or a failure state. NOTHING puts age on the card itself, and card anatomy (my range, 21-25 + colleague 26-30) never carries a date. freshness is currently invisible at the exact moment of choice: the card scan.

**restatement:** one compact chip cluster beside the score showing WHEN this verdict was made and WHEN the crowd numbers were pulled — the audit trail at card scale, ambient rather than on-demand.

**mechanism:** merges with idea 18's hardware chip into a single provenance cluster in the card's proof strip: `TESTED: 12 GB · AUG '26` (+ community cluster already carries pulled-dates per idea 16). data: `tested_at` curation field (set at test time, refreshed at re-test — same event that drives idea 20's deltas; the three ideas 18/20/A share one provenance record). freshness encoding: relative month, not absolute date ("AUG '26" not "2026-08-14" — faster parse); entries tested >90d ago shift the chip to coral outline automatically (>90d = CRITERIA freshness decay threshold, so the visual rule IS the criteria rule); >180d adds the stale glyph. python lint computes chip state from data — no hand-maintained staleness. detail page: same cluster expands to full ledger (every test date, every pull date, every delta — one provenance table).

**simulation:** owner, 23:55, comes back after a 5-week sprint on another project, opens his own site to re-trust it before curating. card 1: `TESTED: 12 GB · JUL '26` — five weeks ago, borderline; the chip is neutral-grey, not coral, so it passes. card 4: `TESTED: 12 GB · FEB '26` — coral outline. he doesn't remember that entry, but the chip just told him: re-test or demote, tonight's queue. the site audited itself for him. and marcus, 10:30, seeing `AUG '26` on everything he scans: the ambient message is "this library is alive, numbers are fresh" — the unspoken fear about static curated sites (abandoned pet project) answered by a chip he half-notices. freshness visible at card level is the difference between a library that reads maintained and one that reads frozen.

**micro-criteria:**
- chip present on 100% of scored entries; state computed from data by lint, never hand-set (hand-set staleness = guaranteed rot)
- coral threshold = CRITERIA 90d freshness decay, exactly — visual rule and scoring rule are one rule
- relative month format; parse time <0.5s in a card-scan blur test

**cost:** build low (extends 18's chip; one field `tested_at`) · perf none · maintenance low (refreshed by the re-test cycle that 17/20 already mandate — no new discipline, just surfacing existing data).

**verdict:** ADOPT — 9/10 — owner requirement ("recency visible") made ambient at the point of choice; unifies 18/20 into one provenance record instead of three scattered date fields. cheaper than it looks because the data already exists in the curation model.

---

## new idea B — cross-lane usage link on cards: "→ used in 3 campaign workflows"

**born from gap:** the product's core loop is persona → ad (the hero promise, idea 4's stage rail, the 60-second walkthrough's ending). colleague-range idea 84 wires the handoff as a directional BUTTON on detail pages ("use this persona in Campaign lab") — one-way, one entry, one page deep. NOTHING makes the loop visible from the default grid, and nothing runs the reverse direction (from an ad/workflow card back to the personas it consumes). the loop is the product; the grid doesn't know it exists.

**restatement:** every entry card that participates in a stack or workflow shows a reverse-usage line linking to its consumers — the persona→ad handoff becomes navigable during browsing, in both directions, without opening detail pages.

**mechanism:** pure derived data — no new curation field: the generate step inverts stacks.json + workflow dependency lists into `used_in: [entryIds]` per entry. card render: one quiet line under the community cluster, `→ used in 3 campaign workflows` (count + lane name); each is a link to the consumer's detail, or to `?lane=ads&tab=stacks` filtered to consumers (rides idea 10's URL state). direction two: workflow/stack cards show `← needs a persona: any S/A pick` when they depend on an identity input but the stack ships without one — an honest gap marker that converts directly into the handoff (tap → Persona lane). suppressed when count = 0. lint: derived `used_in` counts must match the actual graph (no hand-maintained counts — they rot instantly).

**simulation:** kenji, week 3, 21:40: just imported his first persona via the Start-here stack, one successful generation on his desktop, feeling cocky — "ok now what?" back on the site, his persona's card now shows a line he never noticed before: `→ used in 3 campaign workflows`. one tap: Campaign Lab, stacks tab, pre-filtered to what consumes HIS persona. the "now what?" question — the churn cliff where most tools lose people after the first success — answered by a line of derived data. mirror: lia, 01:40, opens a "15s reel from one photo" workflow card and sees `← needs a persona: any S/A pick` — she had skipped persona lane entirely ("that's for influencer people"); the marker just told her the ad pipeline she wants has a prerequisite, with the fix one tap away. both directions, zero new curation labor, the product loop navigable from the grid.

**micro-criteria:**
- line appears exactly when usage exists (count ≥1), count matches the derived graph (lint), zero hand-maintenance
- `← needs a persona` gap markers appear on every dependent-without-provider entry (honesty about incompleteness at card level)
- tap lands on a pre-filtered consumer/provider view via URL state (never a generic lane dump)

**cost:** build low-med (inversion step in generate + one card line) · perf none (derived at generate, not runtime) · maintenance none (derived — this is the idea's whole virtue).

**verdict:** ADOPT — 8/10 — wires REQUIREMENTS' "define the best HANDOFF" into the default grid, both directions, at zero curation cost; docked to 8 because it depends on stacks (9) existing first — its value is a direct function of stack coverage.

---

# VERDICT SUMMARY — ideas 1-25 + 2 new

| idea | verdict | score | one-line reason |
|---:|---|---:|---|
| 1 outcome hero | ADOPT | 10 | first click = the promise; kills the translation hop |
| 2 intent lane names | ADOPT | 9 | IA backbone; "Campaign Lab" needs its plain sub-label |
| 3 lanes in primary nav | ADOPT | 10 | 1-click lane switch at any depth; cheapest, highest payoff |
| 4 stage rail | ADOPT scoped v1 homepage | 7 | scope proof + handoff grammar; supporting signage, not product |
| 5 enter via result | ADOPT | 10 | owner law; the vocab lint makes it a gate not a vibe |
| 6 Start-here shelf ×3 | ADOPT | 10 | THE three answers, permanent, safe; newcomer minute in one component |
| 7 civitai one-liner | ADOPT | 8 | zero-cost trust fix + attribution ethic at narrative level |
| 8 Models/Workflows tabs | ADOPT | 9 | requirement verbatim; per-lane default tab is the smart micro-choice |
| 9 Stacks | ADOPT (phased: 3 in v1) | 10 | "best flows for best models" IS the stack; highest empathy + highest editorial cost |
| 10 URL state | ADOPT | 10 | shareable = free distribution; reload-proof = free UX; substrate for 5 colleague ideas |
| 11 S = first pick for production | ADOPT | 9 | tier semantics backed by machine-checked gates |
| 12 A = one caveat (required) | ADOPT | 9 | required-caveat lint turns honesty into infrastructure |
| 13 B = niche match + tier-driven layout | MERGE (absorbs 24) | 9 | layout grammar encodes rank; B rail becomes specialty menu |
| 14 score 8.7/10 never stars | ADOPT | 10 | preserves the resolution the whole curation exists to expose |
| 15 justification under score | ADOPT | 10 | Direction B signature; highest value-per-pixel string on card |
| 16 editor vs community split | ADOPT | 10 | CRITERIA anti-farm thesis needs its visual face; blending banned |
| 17 confidence labels ×3 | ADOPT | 9 | a score without confidence is a bluff; 3 values, no false precision |
| 18 tested-on rig + base chips | ADOPT | 9 | makes numbers auditable claims; enables VRAM-first at card level |
| 19 "why not S" | MERGE with 12 | 9 | A: caveat==not-S (one field); B: distinct line traceable to axis row |
| 20 score deltas ▲0.3 | ADOPT | 8 | alive + accountable; full payoff gated on 2nd test cycle |
| 21 one dominant preview | ADOPT | 10 | results visible AT CARD SCALE; also the biggest perf lever |
| 22 custom english names | ADOPT | 10 | requirement verbatim; names are the brand moat that travels |
| 23 purpose above specs | ADOPT | 10 | "format and order matter" verbatim; DOM=visual=scan order |
| 24 "Best when" line | MERGE into 13 | 9 | one field, tier-dependent prominence; long tail → browsable |
| 25 VRAM next to title | ADOPT | 10 | kills love-then-betrayal; met during the name scan |
| NEW A provenance cluster | ADOPT | 9 | recency visible at point of choice; unifies 18/20 data |
| NEW B cross-lane usage links | ADOPT | 8 | handoff loop navigable from the grid, both directions, derived free |

**range health:** 21 ADOPT, 4 MERGE (into 2 unified field families), 0 KILL, 1 scoped-adopt. honest note on the spread: this cluster (IA + trust + card anatomy) is the load-bearing core — a weak idea here would have sunk the product before colleague-range ideas (filters, comparison, detail pages) ever mattered, so the high adoption rate reflects the cluster's position, not grading softness. the 4 merges ARE the critical work: 12+13+19+24 collapse into two lint-enforced field families (`caveat`+`best_when`/`not_s`), which is less data to maintain, no divergence risk, and machine-checkable honesty.

**cross-range dependencies flagged for synthesis:** idea 10 (URL state) underlies colleague ideas 44/59/60/100; idea 18's hardware field is shared with 26 (labels) and 32/33 (filters); idea 16's pulled-dates feed 29; idea 9's stacks feed 62, 82, 84; idea 21's locked aspect boxes feed 98. none of these should be built twice.
