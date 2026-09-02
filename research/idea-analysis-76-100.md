# idea analysis 76-100 (analyst 4/4) — import block + workflow presentation + resilience

method: each idea simulated on static vanilla-JS github-pages (local JSON, civitai CDN only). import ideas scored hardest — owner named import speed repeatedly. persons: marcus (ad guy), lia (OF creator), kenji (comfyui newbie), owner.

---

## IMPORT BLOCK (76-80) — highest stakes in range

### 76 — workflows get a primary `Download ComfyUI JSON` action
**mechanism:** detail page top action = single coral button, largest hit-target on page. Build step writes per-entry JSON to `workflows/<slug>.json`, filename = our custom name + version (`soft-window-persona-lock--v2.3.json`, never `workflow(3).json`). Click = native download, no JS gymnastics. Secondary action (copy-to-clipboard) belongs to idea 101, not here — one primary, no twins. Button sits above the fold beside the proof block (idea 73's territory, not mine).
**click-path:** card → detail → click "Download ComfyUI JSON" → file lands in downloads bar → drag onto ComfyUI canvas. 2 clicks from detail to JSON on disk.
**simulation:** marcus lands on detail from lane A, wants the file NOW. He reads nothing, hunts for the button, finds it instantly because it's the only coral thing above the fold. Feels: zero hesitation. The old pattern — hunting through a civitai page, finding the workflow tab, downloading a zip — never happens.
**micro-criteria:** good = button visible without scroll, 1 click → file on disk, filename matches our custom name. bad = button below gallery, or filename `model-12345.json`.
**cost:** trivial. build script emits one JSON per workflow entry.
**verdict:** ADOPT — 9 — the import spine starts here; everything else in this range hangs off this button.

### 77 — import explained as one sentence: `Download JSON → drag onto ComfyUI, or Workflows > Open`
**mechanism:** static one-liner directly under the download button, both paths named (drag-drop is canonical, Workflows > Open is the fallback for people who miss the drop). Rendered before click AND again in the post-click state (button label flips to "JSON downloaded ✓", instruction stays). No accordion, no docs page — one sentence, always visible.
**click-path:** unchanged from 76; this idea removes the "now what?" gap between download and ComfyUI.
**simulation:** kenji downloaded the JSON and is staring at ComfyUI wondering where files go. He glances back at our tab: "drag it onto the canvas." He drags, it loads, nodes appear. The panic moment — "did I download the right thing? where does it GO?" — never happens because the answer is one eye-movement away.
**micro-criteria:** good = ≤20 words, names both load paths, visible pre- and post-click. bad = instruction hidden in FAQ, or only one path named.
**cost:** zero. static text.
**verdict:** ADOPT — 8 — cheapest fix for the biggest newcomer stall point.

### 78 — list missing models + custom nodes BEFORE download
**mechanism:** "What you need" panel rendered ABOVE the download button, generated at build time from our curated manifest (not parsed from workflow JSON at runtime — we curate, python emits): every model row = our name + original civitai name, size in MB/GB, exact target folder path (`models/loras/`, `models/checkpoints/`), civitai link (new tab), "civitai login required" note on gated resources. Every node row = display name + the exact string to type into ComfyUI Manager's search + git URL fallback. Panel collapses only when count = 0.
**click-path:** kenji reads panel → clicks model link → civitai tab → download → back → repeats → clicks our Download JSON → drags into ComfyUI → zero red nodes. Missing-models handling = fully front-loaded: nothing to handle after import because everything was listed first.
**simulation:** kenji's historical trauma: imports a workflow, half the nodes are red, "missing node: RRDBNet", no idea what that is, gives up. Here he sees "2 models, 3 nodes" before downloading, the links are right there, folders are named. He spends 4 minutes in civitai tabs, comes back, drags, everything resolves. First workflow that ever worked on the first try — he feels like the site respects him.
**micro-criteria:** good = model count + node count stated up front, every row has folder path + link, Manager-searchable name for nodes. bad = list appears only after download, or says "see civitai page" without folder paths.
**cost:** manual curation per workflow (~10 min each, one-time); build-time render trivial. This is THE moat-cost of the product.
**verdict:** ADOPT — 10 — single highest-value idea in my range; the difference between a 30-second import and a 2-hour abandonment.

### 79 — pin the exact model version used for the editorial test
**mechanism:** manifest stores `versionId` + version name + file hash (SHA256 from civitai API) at test time. Detail shows "Tested with v2.3" under the download button; the JSON itself references the exact filenames of that version, so loading it can't silently resolve to v3. Build-time check hits civitai API: newer version exists → badge "v3.0 out — untested by us" linking to it. Downloaded JSON stays pinned to what we tested.
**click-path:** unchanged; this idea guarantees the workflow kenji imports behaves like the proof images because it IS the same bytes.
**simulation:** lia imports a persona LoRA, generates, face looks 20% different from the preview. Old world: she blames herself, tweaks seed for an hour. Here the site said "tested with v2.3" and flagged "v3.0 out, untested" — she understands the delta is upstream, not her. Trust survives a mismatch because the mismatch was named in advance.
**micro-criteria:** good = every entry shows pinned version + hash-verified file; newer-version badge when applicable. bad = "latest" downloads with no tested-version note.
**cost:** build-time API check per entry (batched, cacheable); manifest field. Cheap, honest.
**verdict:** ADOPT — 9 — reproducibility is what makes "tested by us" a claim instead of a vibe.

### 80 — recovery panel: `Missing checkpoint? Put it in models/checkpoints, then refresh`
**mechanism:** static troubleshooting accordion on workflow detail, keyed by LITERAL ComfyUI error strings (we hit them during our test runs, log them verbatim): missing-node red boxes → Manager install steps; "Value not in list: lora_name" → file in wrong folder, name the exact folder + "refresh ComfyUI (R or reload)"; CUDA OOM → link to lower-resolution preset note. Static site cannot read ComfyUI state — the panel is a lookup table, not a detector, and says so in one line.
**click-path:** import failed → user switches back to our tab → ctrl-F the error text → row expands: cause in plain english + exact fix + folder path → back to ComfyUI. 3 interactions, no leaving the two tabs.
**simulation:** kenji drags the JSON, ComfyUI throws `Value not in list: lora_name`. His stomach drops — this is where every previous attempt died. He alt-tabs, pastes the error into our box, reads "the LoRA file isn't where ComfyUI looks. Move it to models/loras/, press R." Moves file, presses R, nodes go green. The loop that used to end in a closed tab now ends in a green graph.
**micro-criteria:** good = ≥3 real error strings covered (missing node / value-not-in-list / OOM), each with one-line fix + folder path; searchable via ctrl-F. bad = generic "check the docs" link, or invented error strings we never hit.
**cost:** grows with our test runs (each new error = one row); render trivial.
**verdict:** ADOPT — 8 — closes the loop 78 opens; converts import failures from dead-ends into solved lookups.

---

## WORKFLOW PRESENTATION (81-90)

### 81 — ad pipelines as storyboard: still → motion → audio → voice → export
**mechanism:** lane B detail = horizontal stage strip, one card per pipeline stage, connector lines between. Each stage: thumbnail (proof image for that stage), stage name, which model/node produces it. Click stage → expands the model used + its link. Static DOM: flexbox row, CSS connectors, all data from manifest (stages hand-authored per pipeline at curation).
**click-path:** lane B card → detail → storyboard replaces wall-of-text; marcus scans left-to-right, clicks "voice" stage → sees RVC model + link. Import itself still via 76's button at top.
**simulation:** marcus opens an ad pipeline and instead of a node-graph screenshot (which reads as spaghetti to him) he sees: STILL → MOTION → AUDIO → VOICE → EXPORT, five pictures in a row. In five seconds he understands what the pipeline DOES. He clicks "voice", sees the model, feels in control of a thing he assumed was too complex for him.
**micro-criteria:** good = 3-5 stages, each clickable, thumbnail per stage, full story readable in <10s. bad = stages as text list only, or stage click reveals nothing.
**cost:** hand-authoring stages per pipeline (we curate ~dozens, fine); zero runtime cost.
**verdict:** ADOPT — 7 — makes lane B (owner's ads pipeline) instantly understandable; the visual grammar the lane was missing.

### 82 — every stack shown as `Base model + LoRA + workflow + optional tools`
**mechanism:** one-line formula rendered as chips joined by `+`, on card (truncated at 4 chips, "+2 more") and full on detail. Every chip clickable → scrolls to that component's row in the "What you need" panel (78) or its own entry if curated. Formula order is FIXED (base → lora → workflow → tools) so stacks are comparable at a glance across cards.
**click-path:** none new — this is the 1-second anatomy read before any click.
**simulation:** marcus compares two ad stacks in a list. Card A: `z-image-turbo + Soft-Window LoRA + Ad Starter 04 + RVC voice`. Card B: `SDXL + …`. He instantly sees A has video+voice, B is stills-only. Decision made without opening either detail page — the formula line did the comparing for him.
**micro-criteria:** good = fits one line on card, fixed part order, every chip has a target. bad = free-text sentence, or chips that go nowhere.
**cost:** manifest field + tiny render. Near-free.
**verdict:** ADOPT — 8 — the highest information-per-pixel element for stack cards; directly serves "instantly understandable best-per-category".

### 83 — audio/voice nodes labeled by role: narration, lip sync, cleanup, music
**mechanism:** role = a badge field on dependency rows (78) and storyboard audio stages (81). Rendered as colored pill: `narration` / `lipsync` / `cleanup` / `music`. Data hand-tagged at curation; no inference. Standalone it's just labels — its surfaces are 81 and 78.
**simulation:** lia builds an OF pipeline: she needs voice + lip sync but NOT music. With role pills she scans the dependency list, reads "RVC — narration · LipSync node — lipsync · (none — music)", and knows in 3 seconds this stack does what she wants. Without pills, three audio-ish names mean nothing.
**micro-criteria:** good = every audio dependency carries exactly one role pill; roles from a fixed 4-value set. bad = free-form audio descriptions.
**cost:** one field per dependency row. Free.
**verdict:** MERGE — into 81 + 78 (render there) — score 6 — real value, zero standalone surface.

### 84 — explicit handoff buttons between lanes: `Use this persona in Campaign Lab`
**mechanism:** manifest cross-ref: each persona entry lists compatible pipeline ids (curated). Persona detail renders "Use this persona in Campaign Lab" ONLY when ≥1 compatible pipeline exists. Click = navigates to `?lane=ads&with=<slug>` → lane B filtered, compatible cards carry a "works with <persona name>" badge. Static: pure URL params + precomputed cross-ref, no runtime logic.
**click-path:** persona detail → handoff button → lane B with 3 compatible pipelines shown, badges visible → pick one → import. The A→B journey the owner described (personas FOR ads) becomes one click instead of re-filtering by memory.
**simulation:** marcus finished his persona, felt good about it, and now wants the ad. Old flow: back to lane list, remember which pipelines fit, hope. Here: one button, land in lane B, badges say "works with Soft-Window". The product's core loop — persona → ad — finally has a literal button.
**micro-criteria:** good = button only when ≥1 match; landing lane shows match badges; ≤1 click from persona to filtered lane B. bad = button exists but lands on unfiltered lane.
**cost:** curation cross-ref per persona; trivial render.
**verdict:** ADOPT — 7 — the lanes stop being silos; directly implements owner's persona→ads pipeline intent.

### 85 — switch between `Model view` and `Pipeline view`
**mechanism (as proposed):** global view-mode toggle re-rendering lane content by entry type. BUT requirements already mandate workflows/models tabs per lane, and 81 covers pipeline presentation inside entries. A second toggle = two controls for one distinction, three if you count filters — kenji won't know which knob does what.
**simulation:** kenji on lane A sees tabs (Workflows | Models) AND a view toggle (Model view | Pipeline view). He clicks the toggle, the content shuffles, he can't tell what changed, clicks back. Feels: the site has one control too many, and now he trusts the other controls less. Redundant controls read as beta, not power.
**micro-criteria (if it survived):** good = single axis of control for type distinction. bad = two controls with overlapping effects.
**cost:** avoided confusion is the savings.
**verdict:** MERGE — with lane tabs (requirements) + 81 — score 5 — the distinction is real, the second control is not.

### 86 — `Proven` and `Latest` sorting, never silently mixed
**mechanism:** segmented control top of every lane: `Proven` (default; our composite score/tier order) | `Latest` (version updatedAt desc). Active mode always labeled + in URL (`?sort=latest`); count badge shows result set unchanged between modes so users see it's the same items, reordered. Freshness date visible on every card either way, so "Latest" is confirmation, not revelation.
**click-path:** lane → click `Latest` → same cards reorder, newest-tested first. One click, reversible, shareable URL.
**simulation:** owner returns after a month, wants to know if anything new passed testing. He clicks `Latest`, top card says "added 3 days ago", he's current in two seconds. In `Proven` mode he trusts the top of the list is the best, not the newest — the two questions never blur.
**micro-criteria:** good = default Proven, 1-click switch, active mode in URL, identical result count in both modes. bad = implicit recency boost inside the score, or sort state lost on navigation.
**cost:** trivial — two precomputed orderings client-side.
**verdict:** ADOPT — 8 — owner cares about recency AND ranking; this names both instead of averaging them into mush.

### 87 — estimated generation time as range tied to selected hardware
**mechanism (honest version):** manifest stores MEASURED wall-clock per generation from our test runs, per VRAM bucket actually tested. Rendered only where we have a measurement: "≈45s on 12 GB (measured)". Untested buckets show nothing — never interpolated, never invented (CRITERIA data-honesty; inventing numbers = the exact fraud the doctrine bans).
**simulation:** marcus on a 12 GB card reads "≈45s on 12 GB (measured)" on the top pick — he knows the ad takes under a minute per iteration, commits to the import. On a 16 GB-only entry he'd see a dash and understand why: we didn't run it there. Feels: the site only says things it did.
**micro-criteria (if adopted):** good = ranges appear only with a logged measurement + rig note. bad = "5-15 min depending on hardware" vibes.
**cost:** measurement discipline during testing (we're timing runs anyway for verification); render trivial.
**verdict:** DEFER — 5 — correct shape but no data until benchmarks census produces timed runs; ship the manifest field now, render when measured.

### 88 — mark entries whose preview uses a different base model than the workflow
**mechanism:** build-time check: preview image's embedded metadata (`meta.civitaiResources`, from civitai API `images` withMeta) names a different base/version than the entry's pinned one → badge on card + detail: "Preview generated on <other base>". When preview carries NO usable metadata → different badge: "Preview unverified" (silence would be dishonest too). Ties directly into CRITERIA's preview-honesty axis — this is that axis rendered.
**simulation:** owner QA-ing his own site before publish spots a persona card whose preview face looks SDXL-crisp but the entry is Flux. Badge says so. He fixes the preview. Without the badge, a stranger finds it and the library's "tested by us" claim (90) takes the damage.
**micro-criteria:** good = mismatch → badge; no-metadata → "unverified" badge; clean → nothing. bad = silent pass-through of mismatched previews.
**cost:** build-time metadata walk (garimpo already fetches images+meta); render trivial.
**verdict:** ADOPT — 7 — cheap honesty guard that protects the site's one unforgeable claim.

### 89 — compact dependency graph with clickable explanations
**mechanism:** SVG mini-graph per workflow entry (workflows ONLY): 5-10 nodes — base model → LoRA → sampler → post → output — hand-authored as graph JSON at curation (never auto-parse arbitrary workflow files; our curated shape stays legible). Click node → popover: one plain sentence ("upscales to 2K before video pass") + which file it needs (deep-links into 78's rows).
**click-path:** workflow detail → graph under the storyboard → click "LoRA" node → popover names the file + "get it" links to the matching row in What-you-need.
**simulation:** kenji opens a workflow, sees the graph: five boxes, left to right, one line each. He clicks the box labeled "upscale" and reads one sentence. For the first time a workflow diagram taught him something instead of intimidating him — he now reads the graph BEFORE the prose.
**micro-criteria:** good = ≤10 nodes, every node clickable with a 1-sentence explanation, file links resolve to 78 rows. bad = decorative node spaghetti with no click targets, or auto-parsed raw ComfyUI graphs (unreadable).
**cost:** hand-authoring per workflow (~15 min each); SVG render static. The cap (workflows only, ≤10 nodes) is what keeps it from becoming a project.
**verdict:** ADOPT — 6 — real comprehension win for workflows, capped hard to contain authoring cost; skips non-workflow entries entirely.

### 90 — distinguish `tested by us` from `community-linked`
**mechanism:** binary provenance badge on EVERY entry, from manifest field `verification: hand-tested | community-linked`. Hand-tested = we ran it, proof images exist (our own outputs), recovery panel rows logged. Community-linked = curated from community consensus, score shown but prefixed "provisional", S-tier blocked (matches CRITERIA: S requires external gate + curator verification; completeness axis = curator-verified only). Lane header shows tested/untested counts.
**simulation:** owner hands the link to a friend. Friend sees two cards, both "9.1". One badge says HAND-TESTED with three proof images, the other "community-linked · provisional". He picks the tested one without reading a word — the badge did the editorializing. Without it, identical scores on different evidence = the library lying by layout.
**micro-criteria:** good = badge on 100% of entries; community-linked can never render S tier; hand-tested entries carry ≥1 OUR-output proof image. bad = "verified" badges on entries nobody ran.
**cost:** honest bookkeeping per entry (the testing we already committed to); render free.
**verdict:** ADOPT — 9 — this badge IS the product's trust moat made visible; blocks the site's worst failure mode (unearned authority).

---

## RESILIENCE + CONTENT QUALITY (91-100)

### 91 — versioned static manifest: source IDs + checked dates per entry
**mechanism:** `data/entries/<slug>.json`, schema: `civitaiId, versionId, pulled_at, checked_at, schemaVersion, verification, changelog[], deps[]`. Python build validates every entry against the schema and FAILS the build on missing fields (a manifest you can ship broken is no manifest). schemaVersion lets the site code evolve without silently misreading old data. This is infrastructure: powers 92, 95, 96, 97, 79's build-time version check, and CRITERIA's snapshot deltas.
**simulation:** owner re-tests an entry six weeks later, bumps the score, changes one field. Because the manifest is per-entry and versioned, the changelog (97) writes itself, the provenance date (92) updates, and a typo in one entry can't corrupt the dataset — the build screams instead.
**micro-criteria:** good = build fails on schema violation; every entry carries pulled_at + checked_at; schemaVersion present. bad = one giant models.json nobody dares touch.
**cost:** one build-validation script (~100 lines, one-time); ongoing discipline is per-entry fields the curation flow produces anyway.
**verdict:** ADOPT — 9 — the load-bearing wall under a quarter of my range; without it 92/95/96/97 are vibes.

### 92 — provenance line: creator, original model, version ID, last verification date
**mechanism:** one footer line on every detail page, rendered from the manifest: `Original: "Flux Realism LoRA" by authorX · v2.3 (id 123456) · verified 2026-08-28 · open on Civitai ↗`. Our custom name is the headline; this line is the receipts. Satisfies the requirements' "link back to civitai original on every entry" with provenance attached.
**simulation:** a civitai creator googles his model name, lands on our page with a different title and our score. He reads the provenance line: his name, his model, exact version, linked. Feels credited, not plagiarized — the line is the difference between curation and theft.
**micro-criteria:** good = present on 100% of detail pages, all four fields + working link. bad = provenance only "when convenient".
**cost:** free once 91 exists — it's a render of manifest fields.
**verdict:** ADOPT — 9 — one line, pays trust to creators AND makes dead-link recovery (95) possible.

### 93 — license / usage notes shown BEFORE the import button
**mechanism:** above the download button, from civitai API fields (`allowCommercialUse`, `allowNoCredit`, nsfwLevel) + our manual note: pills like `Commercial: allowed` / `Commercial: personal-only` / `NSFW: yes`. CRITERIA kill-line wired in: license forbids commercial + lane=ads → loud `personal-only` badge; entry stays listed but the constraint is unmissable pre-import. Never AFTER the button — the whole point is the decision is informed before bytes move.
**simulation:** marcus builds an ad campaign on a model whose license is personal-only. In the old world he learns this from a lawyer email. Here the coral "personal-only" pill sat above the download button the whole time; he picks an A-tier alternative two cards down instead. Twenty seconds of pill beats a takedown.
**micro-criteria:** good = license pills render above import on every entry; ads-lane personal-only is visually loud. bad = license buried in detail prose or linked out to civitai terms.
**cost:** field mapping one-time; manual note optional. Trivial.
**verdict:** ADOPT — 8 — legal landmine defusal for the cost of a badge row; CRITERIA kill-line gets a UI.

### 94 — file format + safety scan status from source metadata
**mechanism:** honest split. SHOW (API provides): format (safetensors vs ckpt — safetensors is the no-code-execution format, state that in one line), file size, SHA256. DON'T show: a "safety scan" verdict — civitai's public models API does not expose scan results, so a scan badge on our site would be invented authority (data-honesty kill). Scan intent gets one honest line instead: "safetensors: no embedded code execution. ckpt files can contain code — flagged."
**simulation:** kenji sees "1.2 GB · safetensors · sha256 7f3a…" next to a ckpt entry flagged "can contain code". He doesn't fully understand checksums but understands the green format vs the flagged one — and chooses the safetensors stack. The site taught a safety concept in one line without faking a scan it never ran.
**micro-criteria:** good = format+size shown per file; ckpt flagged with the code-execution line; zero invented "scanned ✓" badges. bad = scan-status theater.
**cost:** free (API fields already in manifest for 79's hashes).
**verdict:** MERGE — into 78 (What-you-need rows) + 92 — score 6 — real fields, no standalone surface; scan-status half is KILL-by-honesty.

### 95 — mark removed/archived civitai sources instead of dead cards
**mechanism:** build-time check per entry: civitai API 404 or archived status → entry re-rendered as grayed state: custom name + provenance line + "Removed from Civitai on <checked date>" + our proof images stay (they're ours). Dead entries never keep live import buttons. The check date is honest: the site claims nothing about TODAY, only about build day, and says so.
**simulation:** lia bookmarked a persona LoRA in June. In August she returns: card is gray, "removed from Civitai, checked 2026-08-30". Disappointing but RESPECTED — no dead download button, no 404 surprise mid-import. She trusts every other green badge more because the site clearly audits itself.
**micro-criteria:** good = removed entries show gray state + last-checked date + zero live import buttons; zero dead civitai links reachable from active cards. bad = cards linking to 404s until a human notices.
**cost:** build-time API batch (already doing it for 79); bake state into static output. Cheap because the site is static — staleness has a hard ceiling of one build.
**verdict:** ADOPT — 8 — static site's secret weapon: audit at build, never lie about live state.

### 96 — visible `Needs re-test` state on stale entries
**mechanism:** manifest `checked_at` older than 90 days → card + detail badge "Needs re-test", score rendered grayed with "(as of <date>)", entry demoted below equally-scored fresh entries in Proven sort. Re-test → date bumps, badge clears, changelog row written (97). Badge is driven by the same build that does 95 — one audit, two states.
**simulation:** owner, a month behind on curation, opens his own site: three entries wear "Needs re-test". The site is grading HIM now, honestly — he knows exactly which testing session to run next, and visitors know those scores are aging. Nobody gets misled by a number that silently rotted.
**micro-criteria:** good = badge auto-appears at 90d without manual flagging; re-test clears it and writes a changelog line. bad = "stale" as a hidden internal flag.
**cost:** one date comparison at build. Free.
**verdict:** ADOPT — 7 — freshness decay (already a CRITERIA axis) made visible; keeps the library honest against its own laziness.

### 97 — editor changelog: score, version, dependency changes
**mechanism:** manifest `changelog[]` rows: `{date, score: 8.1→8.7, version: v2.3→v2.4, deps_added[], note}`. Detail page renders a compact timeline (latest 3 visible, expand). Build script can auto-draft rows from manifest diffs between builds; curator edits the note. Empty state renders "Initial review <date>" — never a blank box.
**simulation:** owner re-tests a workflow after a ComfyUI update and drops it 9.1→7.8, adds a dependency. A regular user revisits, sees the timeline entry "2026-09-01 — score lowered after re-test, new dependency: X". Feels: the library has a memory and a spine — scores move for REASONS, written down.
**micro-criteria:** good = every score/version change produces a row; timeline visible ≤2 clicks from detail top; no empty boxes. bad = changelog as git-log-only (invisible to readers).
**cost:** curation discipline per re-test (small — re-tests are occasional); auto-draft script pays for itself.
**verdict:** ADOPT — 6 — trust compounding for modest ongoing cost; only earns its keep once re-tests (96) actually start happening.

### 98 — lazy-loaded galleries with fixed aspect-ratio boxes (no layout jumps)
**mechanism:** every gallery/media slot gets `aspect-ratio` + explicit width/height attributes (civitai API supplies image dimensions — store them in manifest at build) + `loading="lazy"` + low-cost background placeholder color while loading. Lightbox (idea 12's motion, other range) opens from reserved box. Zero CLS by construction: space exists before pixels do.
**simulation:** marcus scrolls fast through lane B on his laptop. Images pop in as he approaches, cards never shift, his thumb never overshoots a card that jumped. He doesn't notice anything — which is exactly the point; noticing scroll jank is the complaint, smoothness is invisible.
**micro-criteria:** good = zero layout shift on image load (fast-scroll test); dimensions from API not hardcoded. bad = cards reflowing as thumbnails arrive.
**cost:** near-zero — CSS + manifest fields. Pure win, no tradeoff found.
**verdict:** ADOPT — 10 — mandatory baseline; failing this makes every other polish idea measurable-through-jank.

### 99 — `Suggest a test` → GitHub issue template prefilled with the entry
**mechanism:** link on detail → `github.com/<owner>/<repo>/issues/new?template=suggest-a-test.md&title=[Test]+<our name>&body=<url>|<civitaiId>|<versionId>` — URL params do all the work, static-native. Depends on: public repo (pages implies it on free tier) + one issue template file + owner willing to receive issues.
**simulation:** a reddit visitor knows a workflow is broken with the new ComfyUI release. The "Suggest a test" link hands him a prefilled issue — entry id, version, link already in place — he adds one sentence and submits. Owner wakes up to actionable QA he didn't pay for. Feels (visitor): my knowledge has a door in. Feels (owner): free signal, zero spam friction.
**micro-criteria (if adopted):** good = prefill carries entry id + versionId + our-page URL; template file exists; issue lands in one click. bad = "open an issue" pointing at an empty generic form.
**cost:** one template file + a link. Trivial — the cost is owner's inbox appetite.
**verdict:** DEFER — 6 — correct and cheap, but pointless before the site is public and traffic exists; wire it the day the repo goes public.

### 100 — `One-minute route` bookmark: outcome → first import, one shareable URL
**mechanism:** `?start=1` (or `/#start`) renders the guided flow from section 4 of the ideas doc: hero with outcome promise → 3 outcome cards (persona / product ad / mature) → one hardware question (4 chips, no account) → top-3 recommendations with proof block → top card open → download button. State machine lives in URL params (`?start=1&step=3&hw=12gb`) so BACK works and the flow is shareable mid-way. From landing to JSON-on-disk: 4 clicks (outcome, hardware, card, download).
**click-path:** open link → click "Realistic social persona" → click "10–12 GB" → three cards render ranked → click top card → click "Download ComfyUI JSON". Missing-models handled by 78's panel already rendered on that card. This IS the owner's "fewer clicks, instantly understandable best-per-category" law as a URL.
**simulation:** kenji's friend sends him the link at a party. Phone, one thumb, 60 seconds of curiosity. He taps persona, taps his GPU, sees three ranked cards with pictures, taps the top one, taps download. He hasn't read a paragraph, made zero decisions he didn't understand, and holds a working workflow file. He feels: this thing was built for someone exactly like me.
**micro-criteria:** good = fresh visitor → first JSON download in ≤4 clicks / ≤60s; flow state in URL (back/share work); hardware question never asks for account/key/file. bad = flow requires scrolling walls of text, or drops state on refresh.
**cost:** one dedicated landing state reusing existing components (cards, proof block, download button) — the most expensive item in my range is mostly COMPOSITION of already-adopted parts, not new surface.
**verdict:** ADOPT — 9 — the newcomer spine; converts the whole range's parts into one measurable 60-second promise.

---

## 2 NEW ORIGINAL IDEAS (gaps in range: post-download friction + the one-gesture import)

### 101 — enriched import JSON: the workflow file documents itself
**gap found:** 76-80 make OUR page good at import, but the moment kenji is inside ComfyUI, our site is gone — and ComfyUI errors reference raw filenames, not our curated names. Nothing in the range carries our knowledge INTO the file.
**mechanism:** build step takes the original workflow JSON and emits a curated copy: loader nodes get `properties` + note fields injected — our custom name, the exact pinned version, the civitai download URL, the target folder path (`models/loras/`). First-run prompt + seed = the verified values from OUR test run, so kenji's first generation reproduces our proof image. Same file 76 downloads — no extra button, 76's click-path unchanged; the enrichment is invisible until a node fails, then clicking the red node in ComfyUI shows our note: `needs "Soft-Window Persona Lock v2.3" — get it: [link] → put in models/loras/`.
**click-path:** identical to 76 (download → drag). Failure path upgrades: red node → click → note with link + folder path — no tab-switching back to our site at all.
**simulation:** kenji's drag resolves everything except one LoRA — node's red. He clicks it. The note panel says our name, the civitai link, the folder. He never leaves ComfyUI, never re-opens our site, never googles a filename. Feels: the file itself was looking out for him — the site came WITH him instead of staying behind.
**micro-criteria:** good = every loader node carries note + version + link + folder path; first-run prompt/seed = our verified test values; JSON < 200KB. bad = raw passthrough file, or notes only on SOME loaders.
**cost:** one python transform per workflow at build (read nodes by class-type heuristics + our manifest mapping — curated entries only, so the mapping is hand-known); risk: ComfyUI node schema variance → mitigate by testing enrichment against every curated workflow at build (build fails on unparseable file).
**verdict:** ADOPT — 9 — moves our curation from our site into the user's editor; directly serves the owner's import-speed law at the exact moment imports actually die.

### 102 — proof-image import: drag ONE image, get workflow + expected output
**gap found:** even a perfect JSON flow is an abstract transaction — file goes in, picture comes out later. ComfyUI natively loads workflows embedded in PNG metadata (every ComfyUI-generated image carries its workflow in a tEXt chunk; dragging such an image onto the canvas loads it). Nothing in the range exploits that: our proof PNGs are generated BY ComfyUI during testing — they already contain the workflow.
**mechanism:** build step guarantees each hand-tested entry ships a "proof image" — OUR test output — with its embedded workflow verified/normalized against the enriched JSON (101): a python pass reads the PNG's tEXt chunk, patches it to the pinned/enriched workflow, re-embeds. Detail page offers both actions equal weight: "Download JSON" (76) and "Download proof image" — plus one line: "or drag the proof image onto ComfyUI — it loads the workflow AND shows the result you should expect." Import becomes one gesture: drag one PNG → workflow loads + user sees the target output sitting in their own canvas. NSFW lanes: proof image obeys the same blur-until-toggle rules; the embed adds no new exposure.
**click-path:** card → detail → drag proof image (or download it, then drag) onto ComfyUI canvas → nodes appear AND the reference output is visible above them → kenji compares his first generation to the expected one sitting right there. Missing-models handling = 78's panel + 101's node notes, unchanged.
**simulation:** marcus drags the proof image onto ComfyUI. Nodes bloom into place and — this is the part — the finished ad still is right there in the output slot. He's not importing an abstraction anymore; he's standing where the image was made, one Run away from his own copy. Feels like unwrapping the demo unit: the proof IS the product.
**micro-criteria:** good = proof PNG loads in ComfyUI identically to the JSON (build-verified); PNG is OUR test output, never a civitai re-upload (honesty); JSON fallback always present beside it. bad = embedding into random preview images, or PNG/JSON workflows diverging.
**cost:** python PNG tEXt patch step at build (well-documented chunk format, no runtime cost); verification step compares embedded vs enriched JSON per entry — build fails on mismatch. One new honesty rule: proof image must be our own generation.
**verdict:** ADOPT — 9 — the fewest-clicks import possible on a static site (one drag, zero file handling), and the only import path that shows the expected result AT the moment of import.

---

## ROLLUP — range 76-100 (+101, 102)

**import spine (owner's #1):** 76 download button → 77 one-line instruction → 78 what-you-need BEFORE download → 79 pinned versions → 80 recovery panel → 101 enriched JSON → 102 proof-image drag → 100 one-minute route wrapping it all. Every failure mode has a named owner: pre-download (78), at-error (80, 101), first-run-proof (102).
**trust spine:** 90 tested-vs-linked badge, 91 manifest, 92 provenance, 93 license pills, 94 (merged) format honesty, 95 removed-marking, 96 re-test badge, 97 changelog, 88 preview-mismatch guard.
**presentation spine:** 81 storyboard (+83 merged), 82 stack formula, 84 lane handoff, 86 proven/latest, 89 capped dep graph.
**platform:** 98 aspect-ratio galleries (baseline, do first).
**deferred:** 87 gen-time estimates (wait for measured data), 99 suggest-a-test (wait for public launch). **merged:** 83→81+78, 85→lane tabs+81, 94→78+92.

**scores (range 76-100):** 10×2 (78, 98) · 9×6 (76, 79, 90, 91, 92, 100) · 8×6 (77, 80, 82, 86, 93, 95) · 7×4 (81, 84, 88, 96) · 6×5 (83, 89, 94, 97, 99) · 5×2 (85, 87) — total 25. **new ideas:** 101=9, 102=9. verdicts: ADOPT 20, MERGE 3 (83→81+78, 85→lane tabs+81, 94→78+92), DEFER 2 (87, 99), KILL 0 (94's scan-status half killed inside its MERGE).
**build order this range implies:** 98 (baseline) → 91 (manifest wall) → 76+77+78+79 (import core) → 80+101+102 (failure+gesture layer) → 100 (composition) → trust spine → presentation spine.



