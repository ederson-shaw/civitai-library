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

