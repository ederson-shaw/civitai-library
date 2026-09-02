# Frontend Design

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. This client has already rejected proposals that felt templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take one real aesthetic risk you can justify.

## Ground it in the subject

If the brief does not pin down what the product or subject is, pin it yourself before designing: name one concrete subject, its audience, and the page's single job, and state your choice. If there's any information in your memory about the human's preferences, context about what they're building, or designs you've made before – use that as a hint. The subject's own world, its materials, instruments, artifacts, and vernacular, is where distinctive choices come from. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is a thesis. Open with the most characteristic thing in the subject's world, in whatever form makes sense for it: a headline, an image, an animation, a live demo, an interactive moment. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the template answer, only use if that's truly the best option.

Typography carries the personality of the page. Pair the display and body faces deliberately, not the same families you would reach for on any other project, and set a clear type scale with intentional weights, widths, and spacing. Make the type treatment itself a memorable part of the design, not a neutral delivery vehicle for the content.

Structure is information. Structural devices, numbering, eyebrows, dividers, labels, should encode something true about the content, not decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence - like a real process or a typed timeline where order carries information the reader needs. Question if choices like numbered markers actually make sense before incorporating them.

Leverage motion deliberately. Think about where and if animation can serve the subject: a page-load sequence, a scroll-triggered reveal, hover micro-interactions, ambient atmosphere. An orchestrated moment usually lands harder than scattered effects; choose what the direction calls for. However, sometimes less is more, and extra animation contributes to the feeling that the design is AI-generated.

Match complexity to the vision. Maximalist directions need elaborate execution; minimal directions need precision in spacing, type, and detail. Elegance is executing the chosen vision well.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: brainstorm, explore, plan, critique, build, critique again

For calibration: AI-generated design right now clusters around three looks: (1) a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta accent; (2) a near-black background with a single bright acid-green or vermilion accent; (3) a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns. All three are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. Just like a human designer who's hired, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the human's design brief: create a compact token system with color, type, layout, and signature. Color: describe the palette as 4–6 named hex values. Type: the typefaces for 2+ roles (a characterful display face that's used with restraint, a complementary body face, and a utility face for captions or data if needed). Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Signature: the single unique element this page will be remembered by that embodies the brief in an appropriate way.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan exactly and deriving every color and type decision from it.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and a element-based selector like .cta). This can happen often with paddings/margins between sections.

Try to do a lot of this planning and iteration in your thinking, and only show ideas to the user when you have higher confidence it'll delight them.

## Restraint and self-critique

Spend your boldness in one place. Let the signature element be the one memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Not taking a risk can be a risk itself! Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected. Critique your own work as you build, taking screenshots if your environment supports it – a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creators have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand, and therefore easier to use. They are design material, not decoration. Bring the same intentionality to copy that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's side of the screen. Name things by what people control and recognize, never by how the system is built. A person manages notifications, not webhook config. Describe what something does in plain terms rather than selling it. Being specific is always better than being clever.

Use active voice as default. A control should say exactly what happens when it's used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the register conversational and tuned: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each element do exactly one job. A label labels, an example demonstrates, and nothing quietly does double duty.

codex
Rota: visual. Critérios antes do deliverable: a pessoa entende os 3 lanes sem conhecer Civitai, encontra uma recomendação em até 3 ações, distingue curadoria de popularidade, vê o motivo da nota sem confiar cegamente nela, escolhe por VRAM antes de importar, entende o estado SFW/NSFW sem choque, alcança o link original, importa no ComfyUI sem adivinhar o próximo passo, a galeria prova o resultado, a interface não vira dashboard genérico, o mobile preserva comparação, o site estático continua leve, o vazio aponta o próximo ato, erro diz como recuperar, teclado e reduced motion funcionam. Vou usar isso como régua, junto com referências externas atuais.
web search: 
web search: site:civitai.com models Civitai model page downloads likes metadata versioning ...
web search: 
web search: Civitai models page likes downloads ratings version details official ...
exec
/usr/bin/bash -lc "pwd && rg --files -g '"'!*node_modules*'"' -g '"'!*.lock'"' | sed -n '1,80p'" in /home/eder/Documentos/sheol
 succeeded in 0ms:
/home/eder/Documentos/sheol
dist-workspace.toml
codex-slivers-precure.txt
codex-slivers.txt
codex-flash.txt
opencode.json
rivals.html
multiversus.html
brawlhalla.html
fighterz.html
dbxv2.html
rung4-6-leads-media-columns.png
rung4-5-profile-404.png
rung4-4-content-tab.png
rung4-3-conversations-honest-empty.png
rung4-2-profile-overview.png
rung4-1-profile-selector.png
index.json
OPEN.md
sheol.json
LEDGER.md
AGENTS.md
AGENTS-HUMAN.md
README.md
indications.md
tests/mcp.rs
tests/test_build_doctrine.py
tools/ritual-gauge
scripts/pull_history.py
scripts/verify-history-txt.py
scripts/pre-push
scripts/build-doctrine.py
scripts/pre-commit
scripts/import-cli-sessions.py
workflows/podcast-clip/run.sh
workflows/podcast-clip/test_slice_words.py
workflows/podcast-clip/slice_words.py
build.rs
claude.md/voice-compressed.md
docs/COMMIT-PLAN.md
docs/outreach-marketing-research.md
claude.md/v3/personality.md
claude.md/v3/draft.md
claude.md/tactics.md
claude.md/beauty.md
claude.md/notes.md
claude.md/discipline.md
claude.md/words.md
claude.md/voice.md
claude.md/readme.md
docs/skills/sheol-cli.md
docs/skills/sheol-module.md
MODULE.md
Cargo.toml
docs/fichas/arena.md
docs/fichas/flow-ui.md
docs/fichas/sheol-ux.md
docs/fichas/search.md
docs/fichas/reacting.md
docs/fichas/tth.md
docs/fichas/caption.md
docs/fichas/trending-aggregator.md
docs/fichas/alerts.md
docs/fichas/stocks.md
docs/fichas/publisher.md
docs/fichas/present.md
docs/fichas/socialblade.md
docs/fichas/scheduler.md
docs/fichas/transcribe.md
docs/fichas/news.md
docs/fichas/comfy.md
docs/fichas/cm.md
docs/fichas/silence-cut.md
docs/fichas/agentic.md
docs/fichas/notify.md
docs/fichas/llm-adapter.md
docs/fichas/github.md
docs/fichas/flow.md
docs/playbooks/criteria-template.md
docs/playbooks/ab-battery.md
docs/playbooks/fix-disease.md

codex
# civitai-library

**Why:** Civitai has the supply; `civitai-library` becomes the decision layer that tells a newcomer what to use, why it ranks, what it needs, and how to import it. Civitai’s model data already exposes versions, types, tags, stats, images, files, and NSFW metadata, while ComfyUI supports loading workflows from JSON, templates, and image metadata. [Civitai model API](https://github.com/civitai/civitai-developer-docs/blob/main/site/reference/models.md), [ComfyUI workflow loading](https://docs.comfy.org/get_started/first_generation)

## 1. Three visual design directions

### Direction A: Pro-tool dark, “The Control Room”

**Philosophy:** Reduce decision fatigue. The site feels like a serious production instrument for people shipping content.

**Mood:** Focused, technical, quiet, high-trust.

**Typography:**

- Display: Archivo Semi Condensed, 600
- UI/body: IBM Plex Sans
- Metadata: IBM Plex Mono

**Color system:**

- Carbon: `#0B0D0F`
- Panel: `#14191D`
- Bone text: `#E9E6DC`
- Mint success: `#7DF5C6`
- Coral action: `#FF705C`
- Periwinkle lane: `#AEB8FF`

**Layout skeleton:**

```text
┌──────────────┬─────────────────────────────────────────────┐
│ logo         │ search models, workflows, outcomes      ●   │
│ lanes        ├─────────────────────────────────────────────┤
│ collections  │ “Ship a consistent AI persona”              │
│ saved        │ [Persona] [Ads] [Mature]                    │
│              ├─────────────────────────────────────────────┤
│              │ filters                                      │
│              │ [VRAM] [Base model] [Task] [Freshness]       │
│              ├─────────────────────────────────────────────┤
│              │ S-tier cards                                 │
│              │ [card] [card] [card] [card]                  │
└──────────────┴─────────────────────────────────────────────┘
```

**Signature element:** Every card includes a horizontal readiness strip:

`persona identity → image generation → motion → voice → publish`

Completed stages glow mint. Missing dependencies turn coral.

**Best use:** Dense browsing, comparisons, hardware filtering, repeat users.

**Risk:** It can feel like another AI dashboard. Keep the hero visual and editorial verdict large enough to preserve personality.

---

### Direction B: Editorial gallery, “The Field Guide”

**Philosophy:** Curation is the product. Every entry reads like a recommendation from an expert editor, not a marketplace listing.

**Mood:** Cult magazine, visual reference book, confident restraint.

**Typography:**

- Display: Bricolage Grotesque, 600
- Body: Literata
- Metadata: Azeret Mono

**Color system:**

- Paper: `#F0EEE7`
- Ink: `#171717`
- Cobalt: `#315BFF`
- Acid note: `#D9FF4D`
- Warm grey: `#C9C5BB`
- Muted lavender: `#DCD9FF`

**Layout skeleton:**

```text
┌────────────────────────────────────────────────────────────┐
│ civitai-library        Persona   Ads   Mature       Search │
├────────────────────────────────────────────────────────────┤
│ THE SHORTLIST                                               │
│ Models and workflows that survive actual production.        │
├───────────────────────────────┬────────────────────────────┤
│                               │ Editor’s note               │
│        lead preview           │ “Best identity lock under   │
│                               │ changing light.”             │
├───────────────────────────────┴────────────────────────────┤
│ S TIER                                                       │
│ [large card]       [small card]       [small card]           │
├────────────────────────────────────────────────────────────┤
│ A TIER                                                       │
│ [gallery rail] [gallery rail] [gallery rail]                │
└────────────────────────────────────────────────────────────┘
```

**Signature element:** Each entry has a blunt editorial verdict instead of a generic rating:

> “The safest first pick for a recognizable face.”

**Best use:** Brand differentiation, visual browsing, premium feel, public sharing.

**Risk:** Dense technical information can disappear. Put VRAM, version, dependencies, and import readiness in a fixed “proof rail” beside every detail page.

**My pick for launch:** Direction B. The product’s advantage is judgment, not inventory. Borrow Direction A’s technical proof rail for detail pages.

---

### Direction C: Arcade energy, “The Creator Loadout”

**Philosophy:** Turn model discovery into a confident game-like selection process without making the content childish.

**Mood:** Creative studio, synth console, campaign map.

**Typography:**

- Display: Chakra Petch, 700
- Body: Manrope
- Metadata: Space Mono

**Color system:**

- Deep violet: `#120B2E`
- Purple panel: `#25135C`
- Acid yellow: `#EFFF61`
- Electric cyan: `#57E7FF`
- Hot magenta: `#FF4FD8`
- White lavender: `#F6F2FF`

**Layout skeleton:**

```text
┌─────────────────────────────────────────────────────────────┐
│ CIVITAI-LIBRARY                 [A] [B] [MATURE]   [SEARCH] │
├─────────────────────────────────────────────────────────────┤
│ SELECT YOUR LOADOUT                                         │
│ [Consistent persona] [Product campaign] [Motion + voice]   │
├───────────────┬───────────────────────────────┬─────────────┤
│ rank ladder   │ featured workflow              │ rig check   │
│ S             │ large preview                  │ 8 GB VRAM   │
│ A             │ “Campaign Starter 04”         │ ready       │
│ B             │ [IMPORT JSON]                  │             │
├───────────────┴───────────────────────────────┴─────────────┤
│ [mission card] [mission card] [mission card]                 │
└─────────────────────────────────────────────────────────────┘
```

**Signature element:** A campaign map connects the three lanes:

`Persona seed → Ad still → Image-to-video → Voice pass`

**Best use:** Newcomer onboarding, discovery, experimentation, social sharing.

**Risk:** Too much glow creates visual fatigue. Use animation only for state changes, never as permanent decoration. No flashing effects.

---

## 2. Twenty premium micro-interactions

| # | Trigger | Motion | Duration | Easing |
|---:|---|---|---:|---|
| 1 | Page load | Hero title rises 8px while fading from 0 to 1 | 420ms | `cubic-bezier(.22,1,.36,1)` |
| 2 | Card hover | Preview scales to `1.025` with a 2% crop pan | 180ms | `cubic-bezier(.22,1,.36,1)` |
| 3 | Card keyboard focus | Focus ring expands from 0 to 2px | 160ms | `ease-out` |
| 4 | Lane switch | Active underline travels between tabs | 220ms | `cubic-bezier(.65,0,.35,1)` |
| 5 | Filter selection | Chip fills, checkmark draws, label shifts 1px | 180ms | `ease-out` |
| 6 | Filter drawer open | Drawer slides 16px from the right with opacity change | 240ms | `cubic-bezier(.22,1,.36,1)` |
| 7 | Result count change | Old number fades down while new number fades up | 180ms | `ease-in-out` |
| 8 | Score enters viewport | Score bar fills from zero to its value | 500ms | `cubic-bezier(.16,1,.3,1)` |
| 9 | Tier reveal | S/A/B badge gets a single light sweep from left to right | 260ms | `ease-out` |
| 10 | Add to compare | Card compresses 2px and a copy appears in the bottom tray | 280ms | `cubic-bezier(.34,1.56,.64,1)` |
| 11 | Compare tray expand | Tray grows upward while columns fade into place | 320ms | `cubic-bezier(.22,1,.36,1)` |
| 12 | Gallery open | Selected image scales from thumbnail bounds into the lightbox | 320ms | `cubic-bezier(.22,1,.36,1)` |
| 13 | Gallery next | Current image crossfades while the next image shifts 12px | 220ms | `ease-in-out` |
| 14 | Copy trigger word | Copy icon flips into a checkmark, then returns | 260ms | `cubic-bezier(.34,1.56,.64,1)` |
| 15 | Import click | Button label changes to “JSON ready” with a checkmark stroke | 360ms | `cubic-bezier(.16,1,.3,1)` |
| 16 | Missing dependency | Missing row receives one coral pulse, then stays still | 420ms | `ease-out` |
| 17 | Original link hover | External-link arrow moves 4px up and right | 160ms | `ease-out` |
| 18 | Search open | Command palette scales from `.98` to `1` and fades in | 180ms | `cubic-bezier(.22,1,.36,1)` |
| 19 | Mature toggle | Toggle thumb glides, background changes only after confirmation | 220ms | `cubic-bezier(.65,0,.35,1)` |
| 20 | Save shortlist | Bookmark fills from bottom to top and emits no persistent sparkle | 240ms | `cubic-bezier(.16,1,.3,1)` |

Respect `prefers-reduced-motion`: replace movement with opacity and instant state changes.

## 3. One hundred organization, navigation, and presentation ideas

### Information architecture

1. Make the homepage promise an outcome: “Create a consistent AI persona,” not “Browse models.”

2. Name the three lanes by user intent: `Persona Studio`, `Campaign Lab`, and `Mature Lane`.

3. Put the lanes in the primary navigation, never inside a buried filter menu.

4. Add a small stage rail showing where each lane fits: identity, image, motion, voice, publish.

5. Let users enter through `I need a result`, not `I need a LoRA`.

6. Create a permanent `Start here` shelf with three safe, tested entry points.

7. Explain Civitai in one sentence: “The original source for many models and workflows in this library.”

8. Separate `Models` and `Workflows` as tabs inside every lane.

9. Add a `Stacks` view for complete combinations of models, workflows, and dependencies.

10. Preserve lane, filters, and sort state in the URL so every view is shareable.

### Ranks and editorial trust

11. Define S tier as “first pick for production.”

12. Define A tier as “reliable with one known caveat.”

13. Define B tier as “worth using when its niche matches the job.”

14. Show the editorial score as `8.7 / 10`, never as stars.

15. Put the named justification directly under the score.

16. Separate `Editor score` from `Community signal`.

17. Use a confidence label such as `High confidence`, `Tested once`, or `Needs more testing`.

18. Show what hardware and base model produced the editorial score.

19. Add a “Why this is not S tier” sentence to every A and B entry.

20. Display score changes when an entry moves after re-testing.

### Card anatomy

21. Give every card one dominant preview, not a collage of equal thumbnails.

22. Use custom English names that describe the result, such as “Soft-Window Persona Lock.”

23. Put the purpose line above technical metadata.

24. Add a `Best when` line that names the exact use case.

25. Put VRAM next to the title, not at the bottom of the card.

26. Use hardware labels such as `8 GB laptop`, `12 GB desktop`, or `Cloud recommended`.

27. Show whether the entry is a LoRA, checkpoint, workflow, voice model, or utility.

28. Show the compatible base model beside the type.

29. Display downloads, likes, and creator rating as dated community signals.

30. Keep `Open original on Civitai` visible on every detail page.

### Filters

31. Use a compact filter bar with only the four highest-value filters visible.

32. Make `VRAM` the first filter because it eliminates impossible options.

33. Add GPU presets: `6 GB`, `8 GB`, `12 GB`, `16 GB+`, and `Cloud`.

34. Filter by base model family.

35. Filter by input: text, image, pose, reference face, audio, or video.

36. Filter by output: portrait, product still, talking head, reel, or voice clip.

37. Filter image-to-video entries by target duration.

38. Filter ad pipelines by audio requirement: silent, narration, lip sync, or music.

39. Add a `Consistency` filter for identity lock, clothing lock, product lock, and scene lock.

40. Keep the mature filter separate from ordinary content filters.

### Search and discovery

41. Make search understand outcome synonyms such as `face consistency`, `identity lock`, and `same person`.

42. Add intent chips under the search field: `new persona`, `product ad`, `talking video`, and `voice`.

43. Use a command palette for keyboard-first navigation.

44. Scope search explicitly to `This lane`, `All lanes`, or `Saved`.

45. Show three example queries inside an empty search state.

46. Store recent searches locally without sending them anywhere.

47. When search returns nothing, suggest a nearby outcome instead of a generic error.

48. Support search by creator name and original Civitai model name.

49. Support search by freshness, such as `updated this month`.

50. Add a controlled `Surprise me` button that selects from the curated set, not the full source.

### Comparison views

51. Add a persistent compare tray at the bottom of the screen.

52. Compare two to four entries in aligned rows.

53. Compare editor score, tier, VRAM, base model, freshness, and dependencies.

54. Compare preview galleries using the same prompt or scenario label.

55. Highlight score deltas rather than coloring every value.

56. Show a mini workflow graph for each compared workflow.

57. Display dependency differences: missing nodes, models, extensions, and voice tools.

58. Add `Show only differences` to comparison mode.

59. Add `Use with my rig` to hide incompatible options inside comparison.

60. Export a shortlist as Markdown or a stable share URL.

### Onboarding

61. Start with three questions: desired output, hardware, and experience level.

62. Give newcomers one complete sample persona instead of an empty grid.

63. Define LoRA in a tooltip: “A small add-on that changes a base model’s behavior.”

64. Ask for VRAM in plain language: “What GPU are you using?”

65. Offer `Beginner` and `Technical` display modes.

66. Keep technical fields collapsed until the person asks for them.

67. Show a sample gallery before showing model names.

68. Put the first import action above the fold on the first recommended card.

69. Use a three-step breadcrumb: `Choose result → Pick stack → Import`.

70. Allow saving a shortlist without an account.

### Detail pages

71. Open with the editorial verdict, not the creator’s original title.

72. Use a two-column detail layout: output proof on the left, decision proof on the right.

73. Put the score, tier, VRAM, base model, and freshness in one compact proof block.

74. Add an `Editor’s note` explaining the tradeoff in plain English.

75. Show trigger words beside a copy button.

76. Give workflows a primary `Download ComfyUI JSON` action.

77. Explain import as: `Download JSON → drag onto ComfyUI, or use Workflows > Open`.

78. List missing models and custom nodes before the user downloads anything.

79. Pin the exact model version used for the editorial test.

80. Add a recovery panel: `Missing checkpoint? Put it in models/checkpoints, then refresh.`

### Workflow presentation

81. Present ad pipelines as a storyboard: still, motion, audio, voice, final export.

82. Show every stack as `Base model + LoRA + workflow + optional tools`.

83. Label audio and voice nodes by role: narration, lip sync, cleanup, or music.

84. Add explicit handoff buttons between lanes: `Use this persona in Campaign Lab`.

85. Let users switch between `Model view` and `Pipeline view`.

86. Offer `Proven` and `Latest` sorting, never mixing them silently.

87. Show estimated generation time as a range tied to the selected hardware.

88. Mark entries whose preview uses a different base model than the listed workflow.

89. Add a compact dependency graph with clickable explanations.

90. Distinguish “tested by us” from “linked because the community uses it.”

### Static-site resilience and content quality

91. Store each entry in a versioned static manifest with source IDs and checked dates.

92. Add a provenance line: creator, original model, version ID, and last verification date.

93. Show license or usage notes before the import button.

94. Show file format and safety scan status when available from the source metadata.

95. Mark removed or archived Civitai sources instead of leaving dead cards online.

96. Give every stale entry a visible `Needs re-test` state.

97. Add an editor changelog with score, version, and dependency changes.

98. Use lazy-loaded galleries with fixed aspect-ratio boxes to prevent layout jumps.

99. Add a `Suggest a test` link that points to a GitHub issue template with the exact entry prefilled.

100. Add a `One-minute route` bookmark that takes newcomers from outcome selection to their first import.

## 4. Ideal first 60 seconds for a newcomer

### 0–8 seconds

Hero copy:

> Build a consistent AI persona, then turn it into an ad.

Supporting copy:

> A hand-tested shortlist of LoRAs and ComfyUI workflows. Choose the result first. We explain the rest.

Primary actions:

- `Create a persona`
- `Make an ad`
- `Explore mature metadata`

The mature option remains visually secondary and locked by default.

### 8–18 seconds

The newcomer clicks `Create a persona`.

A three-card choice appears:

- `Realistic social persona`
- `Product-ready face`
- `Talking-head creator`

Each card shows an output gallery, not technical names.

A small explainer says:

> Civitai is where the original models live. This library narrows the choice to setups worth trying.

### 18–28 seconds

The newcomer selects `Realistic social persona`.

The site asks one hardware question:

> How much GPU memory do you have?

Choices:

- `6–8 GB`
- `10–12 GB`
- `16 GB+`
- `I use cloud generation`

No account, API key, or configuration file appears.

### 28–40 seconds

The library presents three recommendations:

1. `Soft-Window Persona Lock`, S tier, `8.9 / 10`
2. `Natural Portrait Anchor`, A tier, `8.2 / 10`
3. `Editorial Face Consistency`, A tier, `7.8 / 10`

The top card says:

> Best first pick for a recognizable face across changing outfits and locations.

Visible proof:

- Required VRAM
- Base model
- Tested resolution
- Freshness
- Community downloads
- One known caveat

### 40–50 seconds

The newcomer opens the top card.

The first detail panel shows:

- Three before/after preview pairs
- A short “why this ranked first” note
- The exact trigger word
- The selected model version
- A `Download ComfyUI JSON` button
- A `What you need` checklist

The import instruction is one sentence:

> Download the JSON, drag it onto the ComfyUI canvas, then install the two highlighted missing models.

This matches ComfyUI’s documented JSON and image-metadata loading paths. [ComfyUI getting started guide](https://docs.comfy.org/get_started/first_generation)

### 50–60 seconds

After clicking import, the page changes the button to `JSON ready`.

A next-step panel appears:

> Your persona setup is ready. Next: use this identity in a product ad.

Action:

- `Continue to Campaign Lab`

The newcomer understands the product’s core loop:

`choose an outcome → select a tested stack → import it → continue to the next lane`

## 5. Tasteful mature-content gating

### Public-build rule

The public build never ships explicit imagery, explicit image URLs, or hidden full-resolution previews.

Mature entries show:

- Custom editorial name
- Purpose line
- S/A/B tier
- Editorial score and justification
- VRAM and dependency metadata
- Freshness
- Safety and usage notes
- Link to the original Civitai page

The preview area uses an abstract neutral placeholder with the label:

> Mature reference hidden on this site. Open the original source to review it.

### Blur mechanics

If a private or future build ever includes mature previews:

- Load a low-resolution censored placeholder first.
- Apply `filter: blur(28px)` and `transform: scale(1.08)` to avoid sharp edges.
- Place a solid overlay above the image, not only text over the blur.
- Never reveal content on hover.
- Require an explicit click on `Show preview`.
- Keep the blur state as the default after every page load.
- Never use CSS blur as a substitute for removing explicit assets from the public build.
- Use descriptive but non-explicit alt text, such as `Mature workflow preview hidden`.

### Toggle UX

Place the control at the far right of the header:

`Mature lane  [locked toggle]`

On activation, open a calm confirmation panel:

> This lane contains workflows intended for adult content. This site shows metadata and links only. Explicit previews remain on the original source.

Actions:

- `Continue to mature metadata`
- `Keep SFW mode`

Use “Mature lane” in the interface. Reserve “NSFW” for metadata, filters, and accessibility labels.

Deep links such as `?lane=mature` still open in SFW mode and require confirmation.

### Memory persistence

Use a two-level persistence model:

- Default: remember the choice for the current browser session only.
- Optional checkbox: `Remember mature mode on this device for 30 days`.

Store only a boolean preference in `localStorage`:

```text
civitai-library.mature-mode = true
civitai-library.mature-expiry = timestamp
```

Additional rules:

- Expired preferences revert to SFW.
- Shared-device warning appears beside the checkbox.
- A visible `Reset to SFW` action remains in the header.
- Mature mode never changes the default for a new browser profile.
- Analytics do not record mature search terms or outbound page titles.
- The public build never prefetches mature preview assets.
- Outbound links open in a new tab and say: `Open original on Civitai`.
tokens used
43.178
# civitai-library

**Why:** Civitai has the supply; `civitai-library` becomes the decision layer that tells a newcomer what to use, why it ranks, what it needs, and how to import it. Civitai’s model data already exposes versions, types, tags, stats, images, files, and NSFW metadata, while ComfyUI supports loading workflows from JSON, templates, and image metadata. [Civitai model API](https://github.com/civitai/civitai-developer-docs/blob/main/site/reference/models.md), [ComfyUI workflow loading](https://docs.comfy.org/get_started/first_generation)

## 1. Three visual design directions

### Direction A: Pro-tool dark, “The Control Room”

**Philosophy:** Reduce decision fatigue. The site feels like a serious production instrument for people shipping content.

**Mood:** Focused, technical, quiet, high-trust.

**Typography:**

- Display: Archivo Semi Condensed, 600
- UI/body: IBM Plex Sans
- Metadata: IBM Plex Mono

**Color system:**

- Carbon: `#0B0D0F`
- Panel: `#14191D`
- Bone text: `#E9E6DC`
- Mint success: `#7DF5C6`
- Coral action: `#FF705C`
- Periwinkle lane: `#AEB8FF`

**Layout skeleton:**

```text
┌──────────────┬─────────────────────────────────────────────┐
│ logo         │ search models, workflows, outcomes      ●   │
│ lanes        ├─────────────────────────────────────────────┤
│ collections  │ “Ship a consistent AI persona”              │
│ saved        │ [Persona] [Ads] [Mature]                    │
│              ├─────────────────────────────────────────────┤
│              │ filters                                      │
│              │ [VRAM] [Base model] [Task] [Freshness]       │
│              ├─────────────────────────────────────────────┤
│              │ S-tier cards                                 │
│              │ [card] [card] [card] [card]                  │
└──────────────┴─────────────────────────────────────────────┘
```

**Signature element:** Every card includes a horizontal readiness strip:

`persona identity → image generation → motion → voice → publish`

Completed stages glow mint. Missing dependencies turn coral.

**Best use:** Dense browsing, comparisons, hardware filtering, repeat users.

**Risk:** It can feel like another AI dashboard. Keep the hero visual and editorial verdict large enough to preserve personality.

---

### Direction B: Editorial gallery, “The Field Guide”

**Philosophy:** Curation is the product. Every entry reads like a recommendation from an expert editor, not a marketplace listing.

**Mood:** Cult magazine, visual reference book, confident restraint.

**Typography:**

- Display: Bricolage Grotesque, 600
- Body: Literata
- Metadata: Azeret Mono

**Color system:**

- Paper: `#F0EEE7`
- Ink: `#171717`
- Cobalt: `#315BFF`
- Acid note: `#D9FF4D`
- Warm grey: `#C9C5BB`
- Muted lavender: `#DCD9FF`

**Layout skeleton:**

```text
┌────────────────────────────────────────────────────────────┐
│ civitai-library        Persona   Ads   Mature       Search │
├────────────────────────────────────────────────────────────┤
│ THE SHORTLIST                                               │
│ Models and workflows that survive actual production.        │
├───────────────────────────────┬────────────────────────────┤
│                               │ Editor’s note               │
│        lead preview           │ “Best identity lock under   │
│                               │ changing light.”             │
├───────────────────────────────┴────────────────────────────┤
│ S TIER                                                       │
│ [large card]       [small card]       [small card]           │
├────────────────────────────────────────────────────────────┤
│ A TIER                                                       │
│ [gallery rail] [gallery rail] [gallery rail]                │
└────────────────────────────────────────────────────────────┘
```

**Signature element:** Each entry has a blunt editorial verdict instead of a generic rating:

> “The safest first pick for a recognizable face.”

**Best use:** Brand differentiation, visual browsing, premium feel, public sharing.

**Risk:** Dense technical information can disappear. Put VRAM, version, dependencies, and import readiness in a fixed “proof rail” beside every detail page.

**My pick for launch:** Direction B. The product’s advantage is judgment, not inventory. Borrow Direction A’s technical proof rail for detail pages.

---

### Direction C: Arcade energy, “The Creator Loadout”

**Philosophy:** Turn model discovery into a confident game-like selection process without making the content childish.

**Mood:** Creative studio, synth console, campaign map.

**Typography:**

- Display: Chakra Petch, 700
- Body: Manrope
- Metadata: Space Mono

**Color system:**

- Deep violet: `#120B2E`
- Purple panel: `#25135C`
- Acid yellow: `#EFFF61`
- Electric cyan: `#57E7FF`
- Hot magenta: `#FF4FD8`
- White lavender: `#F6F2FF`

**Layout skeleton:**

```text
┌─────────────────────────────────────────────────────────────┐
│ CIVITAI-LIBRARY                 [A] [B] [MATURE]   [SEARCH] │
├─────────────────────────────────────────────────────────────┤
│ SELECT YOUR LOADOUT                                         │
│ [Consistent persona] [Product campaign] [Motion + voice]   │
├───────────────┬───────────────────────────────┬─────────────┤
│ rank ladder   │ featured workflow              │ rig check   │
│ S             │ large preview                  │ 8 GB VRAM   │
│ A             │ “Campaign Starter 04”         │ ready       │
│ B             │ [IMPORT JSON]                  │             │
├───────────────┴───────────────────────────────┴─────────────┤
│ [mission card] [mission card] [mission card]                 │
└─────────────────────────────────────────────────────────────┘
```

**Signature element:** A campaign map connects the three lanes:

`Persona seed → Ad still → Image-to-video → Voice pass`

**Best use:** Newcomer onboarding, discovery, experimentation, social sharing.

**Risk:** Too much glow creates visual fatigue. Use animation only for state changes, never as permanent decoration. No flashing effects.

---

## 2. Twenty premium micro-interactions

| # | Trigger | Motion | Duration | Easing |
|---:|---|---|---:|---|
| 1 | Page load | Hero title rises 8px while fading from 0 to 1 | 420ms | `cubic-bezier(.22,1,.36,1)` |
| 2 | Card hover | Preview scales to `1.025` with a 2% crop pan | 180ms | `cubic-bezier(.22,1,.36,1)` |
| 3 | Card keyboard focus | Focus ring expands from 0 to 2px | 160ms | `ease-out` |
| 4 | Lane switch | Active underline travels between tabs | 220ms | `cubic-bezier(.65,0,.35,1)` |
| 5 | Filter selection | Chip fills, checkmark draws, label shifts 1px | 180ms | `ease-out` |
| 6 | Filter drawer open | Drawer slides 16px from the right with opacity change | 240ms | `cubic-bezier(.22,1,.36,1)` |
| 7 | Result count change | Old number fades down while new number fades up | 180ms | `ease-in-out` |
| 8 | Score enters viewport | Score bar fills from zero to its value | 500ms | `cubic-bezier(.16,1,.3,1)` |
| 9 | Tier reveal | S/A/B badge gets a single light sweep from left to right | 260ms | `ease-out` |
| 10 | Add to compare | Card compresses 2px and a copy appears in the bottom tray | 280ms | `cubic-bezier(.34,1.56,.64,1)` |
| 11 | Compare tray expand | Tray grows upward while columns fade into place | 320ms | `cubic-bezier(.22,1,.36,1)` |
| 12 | Gallery open | Selected image scales from thumbnail bounds into the lightbox | 320ms | `cubic-bezier(.22,1,.36,1)` |
| 13 | Gallery next | Current image crossfades while the next image shifts 12px | 220ms | `ease-in-out` |
| 14 | Copy trigger word | Copy icon flips into a checkmark, then returns | 260ms | `cubic-bezier(.34,1.56,.64,1)` |
| 15 | Import click | Button label changes to “JSON ready” with a checkmark stroke | 360ms | `cubic-bezier(.16,1,.3,1)` |
| 16 | Missing dependency | Missing row receives one coral pulse, then stays still | 420ms | `ease-out` |
| 17 | Original link hover | External-link arrow moves 4px up and right | 160ms | `ease-out` |
| 18 | Search open | Command palette scales from `.98` to `1` and fades in | 180ms | `cubic-bezier(.22,1,.36,1)` |
| 19 | Mature toggle | Toggle thumb glides, background changes only after confirmation | 220ms | `cubic-bezier(.65,0,.35,1)` |
| 20 | Save shortlist | Bookmark fills from bottom to top and emits no persistent sparkle | 240ms | `cubic-bezier(.16,1,.3,1)` |

Respect `prefers-reduced-motion`: replace movement with opacity and instant state changes.

## 3. One hundred organization, navigation, and presentation ideas

### Information architecture

1. Make the homepage promise an outcome: “Create a consistent AI persona,” not “Browse models.”

2. Name the three lanes by user intent: `Persona Studio`, `Campaign Lab`, and `Mature Lane`.

3. Put the lanes in the primary navigation, never inside a buried filter menu.

4. Add a small stage rail showing where each lane fits: identity, image, motion, voice, publish.

5. Let users enter through `I need a result`, not `I need a LoRA`.

6. Create a permanent `Start here` shelf with three safe, tested entry points.

7. Explain Civitai in one sentence: “The original source for many models and workflows in this library.”

8. Separate `Models` and `Workflows` as tabs inside every lane.

9. Add a `Stacks` view for complete combinations of models, workflows, and dependencies.

10. Preserve lane, filters, and sort state in the URL so every view is shareable.

### Ranks and editorial trust

11. Define S tier as “first pick for production.”

12. Define A tier as “reliable with one known caveat.”

13. Define B tier as “worth using when its niche matches the job.”

14. Show the editorial score as `8.7 / 10`, never as stars.

15. Put the named justification directly under the score.

16. Separate `Editor score` from `Community signal`.

17. Use a confidence label such as `High confidence`, `Tested once`, or `Needs more testing`.

18. Show what hardware and base model produced the editorial score.

19. Add a “Why this is not S tier” sentence to every A and B entry.

20. Display score changes when an entry moves after re-testing.

### Card anatomy

21. Give every card one dominant preview, not a collage of equal thumbnails.

22. Use custom English names that describe the result, such as “Soft-Window Persona Lock.”

23. Put the purpose line above technical metadata.

24. Add a `Best when` line that names the exact use case.

25. Put VRAM next to the title, not at the bottom of the card.

26. Use hardware labels such as `8 GB laptop`, `12 GB desktop`, or `Cloud recommended`.

27. Show whether the entry is a LoRA, checkpoint, workflow, voice model, or utility.

28. Show the compatible base model beside the type.

29. Display downloads, likes, and creator rating as dated community signals.

30. Keep `Open original on Civitai` visible on every detail page.

### Filters

31. Use a compact filter bar with only the four highest-value filters visible.

32. Make `VRAM` the first filter because it eliminates impossible options.

33. Add GPU presets: `6 GB`, `8 GB`, `12 GB`, `16 GB+`, and `Cloud`.

34. Filter by base model family.

35. Filter by input: text, image, pose, reference face, audio, or video.

36. Filter by output: portrait, product still, talking head, reel, or voice clip.

37. Filter image-to-video entries by target duration.

38. Filter ad pipelines by audio requirement: silent, narration, lip sync, or music.

39. Add a `Consistency` filter for identity lock, clothing lock, product lock, and scene lock.

40. Keep the mature filter separate from ordinary content filters.

### Search and discovery

41. Make search understand outcome synonyms such as `face consistency`, `identity lock`, and `same person`.

42. Add intent chips under the search field: `new persona`, `product ad`, `talking video`, and `voice`.

43. Use a command palette for keyboard-first navigation.

44. Scope search explicitly to `This lane`, `All lanes`, or `Saved`.

45. Show three example queries inside an empty search state.

46. Store recent searches locally without sending them anywhere.

47. When search returns nothing, suggest a nearby outcome instead of a generic error.

48. Support search by creator name and original Civitai model name.

49. Support search by freshness, such as `updated this month`.

50. Add a controlled `Surprise me` button that selects from the curated set, not the full source.

### Comparison views

51. Add a persistent compare tray at the bottom of the screen.

52. Compare two to four entries in aligned rows.

53. Compare editor score, tier, VRAM, base model, freshness, and dependencies.

54. Compare preview galleries using the same prompt or scenario label.

55. Highlight score deltas rather than coloring every value.

56. Show a mini workflow graph for each compared workflow.

57. Display dependency differences: missing nodes, models, extensions, and voice tools.

58. Add `Show only differences` to comparison mode.

59. Add `Use with my rig` to hide incompatible options inside comparison.

60. Export a shortlist as Markdown or a stable share URL.

### Onboarding

61. Start with three questions: desired output, hardware, and experience level.

62. Give newcomers one complete sample persona instead of an empty grid.

63. Define LoRA in a tooltip: “A small add-on that changes a base model’s behavior.”

64. Ask for VRAM in plain language: “What GPU are you using?”

65. Offer `Beginner` and `Technical` display modes.

66. Keep technical fields collapsed until the person asks for them.

67. Show a sample gallery before showing model names.

68. Put the first import action above the fold on the first recommended card.

69. Use a three-step breadcrumb: `Choose result → Pick stack → Import`.

70. Allow saving a shortlist without an account.

### Detail pages

71. Open with the editorial verdict, not the creator’s original title.

72. Use a two-column detail layout: output proof on the left, decision proof on the right.

73. Put the score, tier, VRAM, base model, and freshness in one compact proof block.

74. Add an `Editor’s note` explaining the tradeoff in plain English.

75. Show trigger words beside a copy button.

76. Give workflows a primary `Download ComfyUI JSON` action.

77. Explain import as: `Download JSON → drag onto ComfyUI, or use Workflows > Open`.

78. List missing models and custom nodes before the user downloads anything.

79. Pin the exact model version used for the editorial test.

80. Add a recovery panel: `Missing checkpoint? Put it in models/checkpoints, then refresh.`

### Workflow presentation

81. Present ad pipelines as a storyboard: still, motion, audio, voice, final export.

82. Show every stack as `Base model + LoRA + workflow + optional tools`.

83. Label audio and voice nodes by role: narration, lip sync, cleanup, or music.

84. Add explicit handoff buttons between lanes: `Use this persona in Campaign Lab`.

85. Let users switch between `Model view` and `Pipeline view`.

86. Offer `Proven` and `Latest` sorting, never mixing them silently.

87. Show estimated generation time as a range tied to the selected hardware.

88. Mark entries whose preview uses a different base model than the listed workflow.

89. Add a compact dependency graph with clickable explanations.

90. Distinguish “tested by us” from “linked because the community uses it.”

### Static-site resilience and content quality

91. Store each entry in a versioned static manifest with source IDs and checked dates.

92. Add a provenance line: creator, original model, version ID, and last verification date.

93. Show license or usage notes before the import button.

94. Show file format and safety scan status when available from the source metadata.

95. Mark removed or archived Civitai sources instead of leaving dead cards online.

96. Give every stale entry a visible `Needs re-test` state.

97. Add an editor changelog with score, version, and dependency changes.

98. Use lazy-loaded galleries with fixed aspect-ratio boxes to prevent layout jumps.

99. Add a `Suggest a test` link that points to a GitHub issue template with the exact entry prefilled.

100. Add a `One-minute route` bookmark that takes newcomers from outcome selection to their first import.

## 4. Ideal first 60 seconds for a newcomer

### 0–8 seconds

Hero copy:

> Build a consistent AI persona, then turn it into an ad.

Supporting copy:

> A hand-tested shortlist of LoRAs and ComfyUI workflows. Choose the result first. We explain the rest.

Primary actions:

- `Create a persona`
- `Make an ad`
- `Explore mature metadata`

The mature option remains visually secondary and locked by default.

### 8–18 seconds

The newcomer clicks `Create a persona`.

A three-card choice appears:

- `Realistic social persona`
- `Product-ready face`
- `Talking-head creator`

Each card shows an output gallery, not technical names.

A small explainer says:

> Civitai is where the original models live. This library narrows the choice to setups worth trying.

### 18–28 seconds

The newcomer selects `Realistic social persona`.

The site asks one hardware question:

> How much GPU memory do you have?

Choices:

- `6–8 GB`
- `10–12 GB`
- `16 GB+`
- `I use cloud generation`

No account, API key, or configuration file appears.

### 28–40 seconds

The library presents three recommendations:

1. `Soft-Window Persona Lock`, S tier, `8.9 / 10`
2. `Natural Portrait Anchor`, A tier, `8.2 / 10`
3. `Editorial Face Consistency`, A tier, `7.8 / 10`

The top card says:

> Best first pick for a recognizable face across changing outfits and locations.

Visible proof:

- Required VRAM
- Base model
- Tested resolution
- Freshness
- Community downloads
- One known caveat

### 40–50 seconds

The newcomer opens the top card.

The first detail panel shows:

- Three before/after preview pairs
- A short “why this ranked first” note
- The exact trigger word
- The selected model version
- A `Download ComfyUI JSON` button
- A `What you need` checklist

The import instruction is one sentence:

> Download the JSON, drag it onto the ComfyUI canvas, then install the two highlighted missing models.

This matches ComfyUI’s documented JSON and image-metadata loading paths. [ComfyUI getting started guide](https://docs.comfy.org/get_started/first_generation)

### 50–60 seconds

After clicking import, the page changes the button to `JSON ready`.

A next-step panel appears:

> Your persona setup is ready. Next: use this identity in a product ad.

Action:

- `Continue to Campaign Lab`

The newcomer understands the product’s core loop:

`choose an outcome → select a tested stack → import it → continue to the next lane`

## 5. Tasteful mature-content gating

### Public-build rule

The public build never ships explicit imagery, explicit image URLs, or hidden full-resolution previews.

Mature entries show:

- Custom editorial name
- Purpose line
- S/A/B tier
- Editorial score and justification
- VRAM and dependency metadata
- Freshness
- Safety and usage notes
- Link to the original Civitai page

The preview area uses an abstract neutral placeholder with the label:

> Mature reference hidden on this site. Open the original source to review it.

### Blur mechanics

If a private or future build ever includes mature previews:

- Load a low-resolution censored placeholder first.
- Apply `filter: blur(28px)` and `transform: scale(1.08)` to avoid sharp edges.
- Place a solid overlay above the image, not only text over the blur.
- Never reveal content on hover.
- Require an explicit click on `Show preview`.
- Keep the blur state as the default after every page load.
- Never use CSS blur as a substitute for removing explicit assets from the public build.
- Use descriptive but non-explicit alt text, such as `Mature workflow preview hidden`.

### Toggle UX

Place the control at the far right of the header:

`Mature lane  [locked toggle]`

On activation, open a calm confirmation panel:

> This lane contains workflows intended for adult content. This site shows metadata and links only. Explicit previews remain on the original source.

Actions:

- `Continue to mature metadata`
- `Keep SFW mode`

Use “Mature lane” in the interface. Reserve “NSFW” for metadata, filters, and accessibility labels.

Deep links such as `?lane=mature` still open in SFW mode and require confirmation.

### Memory persistence

Use a two-level persistence model:

- Default: remember the choice for the current browser session only.
- Optional checkbox: `Remember mature mode on this device for 30 days`.

Store only a boolean preference in `localStorage`:

```text
civitai-library.mature-mode = true
civitai-library.mature-expiry = timestamp
```

Additional rules:

- Expired preferences revert to SFW.
- Shared-device warning appears beside the checkbox.
- A visible `Reset to SFW` action remains in the header.
- Mature mode never changes the default for a new browser profile.
- Analytics do not record mature search terms or outbound page titles.
- The public build never prefetches mature preview assets.
- Outbound links open in a new tab and say: `Open original on Civitai`.
