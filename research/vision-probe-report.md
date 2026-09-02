# Vision probe report

Date: 2026-09-02  
Source: `data/candidates-persona.json`  
Sample: every other entry, indices 0, 2, 4, …, 38 (20 of 40 total)

## Result

The probe is **GO for guarded triage** on 200+ finalists and **NO for unattended publish gating**.
The 450px previews made the coarse visual class fairly reliable, but name fit, subtle anatomy quality,
and NSFW status still need a review queue. The sample contained 14 anime-illustration entries, 5
realism-photoreal entries, and 1 other entry. That confirms an anime-heavy pull, but does not support
treating realism as a negligible tail.

The quality median was 8/10 (mean 7.4/10). Two sampled previews were MP4s; the first extracted frame
was used for the table, so video entries need a multi-frame rule at scale.

The `raw nsfwLevel` value below is copied from the candidate JSON for audit. The bucket is my
**preview-based estimate**, not a reinterpretation of the model-level value. A model with raw level
31 can still have a safe-looking thumbnail.

## Per-entry table

Bucket rubric: `safe` = no visible nudity or sexualized framing; `moderate` = suggestive framing,
revealing/skin-focused presentation, or lingerie-like styling without explicit nudity; `explicit` =
visible explicit anatomy, sexual act, or equivalent. `Q` is the visual quality read from the 450px
preview. Confidence is shown as `class / Q+bucket`.

| id | candidate name | curation draft name | your verdict | confidence | visual read / name fit |
|---:|---|---|---|---|---|
| 1318945 | One obsession | Silk 2.5D Core — Semi-Real Anime Anchor | anime-illustration · Q8 · safe · raw 31 | high / high | Clean anime linework, neon lighting, coherent gesture hand; name explicitly discloses anime. |
| 2220 | Babes | Gloss Pin-Up Core — Realistic Glamour Base | anime-illustration · Q7 · moderate · raw 31 | high / medium | Cartoon/anime face and proportions; clean enough hand and lighting. **Realistic Glamour** is a hard name/image mismatch. |
| 934764 | MiaoMiao Harem | Harem Spotlight — Anime Ensemble Base | anime-illustration · Q8 · safe · raw 31 | high / high | Highly graphic anime character with intentional glitch treatment; no visible NSFW content. |
| 2458426 | Anima | Anima Foundation — The New Anime Starting Point | anime-illustration (mecha) · Q8 · safe · raw 7 | high / high | Crisp cel-shaded mecha, strong sky light, no human-skin evidence; anime label fits. |
| 1377820 | Add Micro Details - Concept (Illustrious \| Pony \| NoobAI) | Micro-Thread — Texture Detail Amplifier | anime-illustration · Q8 · safe · raw 31 | high / high | Anime male character over a detailed bakery scene; face, arms, and lighting read cleanly. |
| 139131 | Sagging Breasts | Natural Gravity — Mature Anatomy Concept | anime-illustration · Q6 · moderate · raw 31 | high / medium | Flat anime rendering and soft background; reclining, body-focused pose is suggestive, not explicit. |
| 667086 | NSFW MASTER | Uncensor Key — NSFW Unlock Family | realism-photoreal · Q8 · moderate · raw 31 | high / medium | Photoreal close-up with smooth skin and controlled light; finger-to-lips framing is suggestive and the eyes are slightly uncanny. |
| 65423 | NijiMecha - Niji Journey - Artstyle  - SD1.5 LORA | Niji Tribute — Midjourney-Anime Look | anime-illustration (mecha fashion) · Q8 · moderate · raw 7 | high / medium | Inked armor and fashion pose are coherent; tight suit makes the framing mildly sexualized. |
| 2026594 | MiaoMiao RealSkin | Skin-True — Semi-Real Anime Base | anime-illustration · Q8 · moderate · raw 31 | high / medium | Anime eyes, hair, and rendering despite polished skin highlights; bare-back/corset framing is suggestive. Raw **RealSkin** is a soft realism promise. |
| 1133519 | Krekkov Style \| Goofy Ai | Krekkov Signature — Bold Ink Style | anime-illustration · Q7 · moderate · raw 31 | high / medium | Bold ink/color treatment, stylized fingers and large-bust framing; no explicit anatomy. |
| 633524 | Background Detail Enhancer✨ | Deep Stage — Background Detail Pump | other (environment illustration) · Q8 · safe · raw 3 | high / high | Strong gothic-room detail and candle/window lighting; no person, face, or skin to classify. |
| 29215 | BArtstyle \| Blue Archive Art Style LoRA \| Anime Flat Color \| 蔚蓝档案画风模型 \| ブルーアーカイブ画風モデル | Sensei's Flat Palette — Blue Archive Look | anime-illustration · Q7 · safe · raw 31 | high / high | Unambiguous flat-color anime, mostly coherent chairs and hand; no visible sexual content. |
| 1200733 | Iwao178 (いわお) - Artist Style | Iwao Ink — Delicate Illustrator Hand | anime-illustration (reference sheet) · Q5 · moderate · raw 31 | high / medium | Anime character samples, but tiny presentation, large white margins, and embedded text hurt quality. |
| 627178 | Cartoony Anime Style | Saturday-Morning Anime — Cartoon Push | anime-illustration (cartoon) · Q6 · safe · raw 15 | high / high | Intentionally simple cartoon with clean fills; not a realism failure, just a low-detail style. |
| 1609320 | IntoRealism | Reality Gateway — Turbo Photoreal Base | realism-photoreal (scene) · Q7 · safe · raw 31 | medium / medium | Camera-like dusk, depth of field, and city lighting; silhouetted subject gives little face/hand evidence. Name fits. |
| 1214846 | Illustrious Gehenna [Illustrious Checkpoint] | Gehenna Gloss — Dark Anime Base | anime-illustration · Q7 · safe · raw 15 | high / medium | Glossy anime face and plastic-smooth skin, with clean hair/rim light and distracting title text. |
| 2088956 | Famegrid (Krea 2 / Z-Image / Qwen) - Realism LoRA | Fame Look — Cross-Base Realism Finish | realism-photoreal · Q8 · safe · raw 15 | high / medium | Natural restaurant light and skin/face rendering; closed eyes and cropped hands limit artifact checking. Name fits. |
| 2218365 | CyberRealistic Z-Image Turbo | Proven-Real Turbo — Z-Image Heritage Port | realism-photoreal · Q8 · moderate · raw 31 | high / high | Freckles, skin texture, hands, straw, and ambient light read photographic; mild suggestive framing only. Name fits. |
| 228525 | ULTRA | Ultra Polish — High-Glam Photoreal Base | realism-photoreal · Q8 · safe · raw 31 | high / high | Clean portrait, plausible skin highlights and shadow, no hands; slight AI smoothness but no major artifact. Name fits. |
| 1240873 | Five Stars Illustrious ⭐⭐⭐⭐⭐ | Five-Star Finish — Premium Anime Base | anime-illustration · Q7 · safe · raw 31 | high / high | Clean fantasy-anime face and lighting; hands are simplified but symmetrical and readable. |

## Lane-fit liar detector

Hard flag:

- **2220 — “Gloss Pin-Up Core — Realistic Glamour Base”** (source name: “Babes”): the preview is
  unmistakably anime/cartoon illustration. The word “Realistic” promises the wrong lane.

Soft flag:

- **2026594 — “MiaoMiao RealSkin”** (curation name: “Skin-True — Semi-Real Anime Base”): the image
  is anime-illustration. The curation name is partly honest because it says “Semi-Real Anime,” but
  the source name can still make a realism-lane reader expect photographic skin.

Not flagged: 1318945 says “Semi-Real Anime Anchor” and the curation name makes the anime boundary
explicit; 1609320, 2088956, 2218365, and 228525 all make realism claims that their sampled previews
support.

## Calibrated prompt text

Use one preview at a time. Pass the source name and curation name as context, but make the image the
primary evidence and do not let either name override it.

```text
You are a conservative visual QA classifier for an image-model curation funnel.

INPUTS
- One 450px preview image (or one representative video frame).
- source_name: {{candidate.name}}
- curation_name: {{draft.our_name}}
- raw_nsfwLevel: {{candidate.nsfwLevel}}  # audit context only; do not treat it as visual truth

TASK
Return exactly one JSON object with:
{
  "visual_class": "realism-photoreal" | "anime-illustration" | "other",
  "quality": 1-10,
  "nsfw_bucket": "safe" | "moderate" | "explicit",
  "name_fit": "fits" | "soft-mismatch" | "hard-mismatch" | "not-applicable",
  "confidence": "high" | "medium" | "low",
  "evidence": "one concise sentence"
}

CLASS RULES
1. realism-photoreal: photographic or convincingly camera-like humans/scenes with natural skin,
   proportions, lens behavior, and light. A polished render is not enough by itself.
2. anime-illustration: anime facial proportions, cel/ink linework, drawn or graphic shading,
   manga/cartoon conventions, or anime-style characters. Detailed or semi-real anime remains
   anime-illustration. Anime mecha and cartoon-anime samples stay in this class when the aesthetic
   is clearly anime.
3. other: environment/prop/mecha/artwork that is not clearly anime, an abstract image, a reference
   sheet whose visual identity cannot be judged, or any non-person preview that does not support
   either primary class.

QUALITY RULES
Score the visible preview, not the model's reputation. Check face/eyes, skin texture, hands/fingers,
limb anatomy, edges, lighting, perspective, and distracting text or cropping. For scene-only images,
score structure, light, and artifact cleanliness, and lower confidence because skin/face/hands cannot
be tested. Intentional stylization is not an artifact; obvious malformed anatomy is.

NSFW RULES
- safe: no visible nudity and no clearly sexualized framing.
- moderate: suggestive pose, lingerie-like/tight styling, exposed or emphasized intimate areas, or
  sexualized close-up without explicit nudity.
- explicit: visible explicit anatomy, sexual act, genital/nipple exposure, or sexual fluids.
Use the image only. Report raw_nsfwLevel separately in the caller's record; never upgrade the bucket
just because raw_nsfwLevel is high. When uncertain between buckets, choose the higher bucket and set
confidence to medium or low.

NAME-FIT RULES
Flag hard-mismatch when source_name or curation_name promises photo/photoreal/realism/real-skin but
visual_class is anime-illustration. Flag soft-mismatch when the promise is qualified (for example,
"semi-real") or only implied by a term such as "RealSkin." Names that explicitly say anime, toon,
illustration, or mecha fit anime/other results.
```

## Error modes found

1. **Semi-real anime masquerading as skin realism.** `MiaoMiao RealSkin` has polished skin shading,
   but the eyes, hair, and facial construction are anime. The class rule must prioritize rendering
   conventions over surface detail.
2. **Painterly or environment-real is not photoreal person realism.** `Background Detail Enhancer`
   is a high-quality illustrated room. It belongs in `other`, and its score cannot be used as a
   proxy for face/skin quality.
3. **Scene-only photoreal previews are under-observed.** `IntoRealism` looks camera-like, but the
   silhouetted subject has no inspectable face or hands. Keep the class, reduce confidence, and do
   not overclaim anatomy quality.
4. **Reference-sheet and text-heavy previews distort quality.** `Iwao178` is classifiable as anime,
   but the tiny samples, whitespace, and embedded text make the 450px card a poor quality read.
5. **Suggestive is not explicit.** The finger-to-lips and straw examples are moderate, not explicit;
   an automated pass needs a three-bucket rule so it does not collapse all mature-looking framing
   into either safe or explicit.
6. **Raw model NSFW level is not preview NSFW.** Several raw-31 entries show safe or moderate
   thumbnails. The site gate should retain raw metadata for policy decisions while this visual pass
   supplies a separate preview signal.
7. **Video needs temporal sampling.** The two sampled MP4s were reduced to a first frame for this
   probe. A production pass should inspect at least the first, middle, and last usable frames, or use
   a curator-approved representative frame.

## Go/no-go for 200+ finalists

**GO, with a review queue.** Run this pass as a coarse funnel filter because the anime/photoreal
separation was visually obvious on 19 of 20 samples and the prompt makes the key boundary explicit.

Do not let it autonomously publish or silently re-lane entries. Route to human review when any of the
following occurs: `other`, confidence below high, quality ≤5, `moderate` or `explicit`, a realism-name
mismatch, a video preview, or a text-heavy/reference-sheet preview. Also spot-check at least 10% of
high-confidence passes. This preserves the speed benefit while covering the exact failure modes found
here.
