# Model Benchmarks — Live Research Snapshot

**Research date: 2026-09-01.** All rankings pulled from live leaderboards fetched this session (latest board snapshots dated 2026-08-25 arena.ai / Aug 2026 Artificial Analysis). Nothing ranked from training memory. Contested picks marked CONTESTED. OPEN items marked OPEN.

Source shorthand:
- **AR** = arena.ai (LMArena, crowdsourced blind-vote Elo): https://arena.ai/leaderboard/text-to-image
- **AA** = Artificial Analysis (blind-vote Elo + pricing): https://artificialanalysis.ai
- Snapshot dates quoted per board. Prices/positions move weekly — re-verify before publishing rankings on the curation site.

---

## OWNER VERIFICATION ITEMS (answered first)

### 1. "z-image" base/turbo — VERIFIED REAL, POSITION DROPPED
- **Z-Image-Turbo** is real: 6B-param distilled T2I from Alibaba Tongyi Lab (Tongyi-MAI), released 2025-11-27, **Apache 2.0**, 8 NFEs, sub-second inference on H800. Repo: https://github.com/Tongyi-MAI/Z-Image ; HF: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- **Historical peak:** Dec 2025 it was #1 open-weights on AA (Elo 1160, ahead of FLUX.2 dev 1147) — https://aigazine.com/benchmarks/alibabas-5-image-generator-beats-competition-with-1160-elo-score--v and GitHub README news entry (2025-12-08).
- **NOW (Aug 2026): NOT top anymore.** AA Elo **1133, rank ~72 overall** (https://artificialanalysis.ai/image/leaderboard/text-to-image — row: "Z-Image Turbo Open Weights | 1133 | Dec 2025 | $5.0/1k"). AR rank **53, Elo 1084** (https://arena.ai/leaderboard/text-to-image). Model page: https://artificialanalysis.ai/image/models/alibaba_z-image-turbo (Elo 1130.45).
- Among open weights it now sits BEHIND Ideogram 4.0 (AA 1219, #1 open), Ideogram 4.0 Quality (1214), FLUX.2 [dev] Turbo (1198) — AA FAQ text, fetched this session.
- **Z-Image-Base: still unreleased** per official HF README ("To be released" for Base and Edit) — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/blob/main/README.md . GitHub lists 4 variants (Turbo/Base/Edit/De-Turbo); only Turbo ships.
- **Why it still matters for us:** best speed/VRAM/price open model (8 steps, 16GB BF16 / 8GB FP8 / 5-6GB GGUF, $5/1k images), native ComfyUI (official tutorial: https://docs.comfy.org/tutorials/image/z-image/z-image ; templates: https://comfy.org/workflows/model/z-image/). Lane: fast local persona generation, not max quality.

### 2. "minimax is the best video model" — TRUE on image-to-video board, CONTESTED on text-to-video
- **TRUE (i2v):** `minimax-h3` is **#1 on arena.ai Image-to-Video** — Elo **1494±6**, 27,308 votes, snapshot 2026-08-25 (fetched live): https://arena.ai/leaderboard/image-to-video
- **CONTESTED (t2v):**
  - AR text-to-video (2026-08-25): gemini-omni-1.1-flash 1515 > gemini-omni-flash 1512 > flux-3-video 1495 (preliminary) > seedance-2.0 1479 > seedance-2.5 1476 > **minimax-h3 1460 (#6)** > muse-video 1457. https://arena.ai/leaderboard/text-to-video
  - AA text-to-video WITH audio (Aug 2026): **Wan 3.0 1242 #1** > Gemini Omni Flash 1237 > Minimax H3 Max (fal post-train) 1235 > **MiniMax H3 1227 (#4, #1 open weights)** > Seedance 2.0 1221. https://artificialanalysis.ai/video/leaderboard/text-to-video
- So: MiniMax H3 = best open-weights video model, #1 i2v overall, but "best video model, period" is contested by Gemini Omni / Wan 3.0 / Seedance 2.x / Flux 3 depending on board and lane.
- MiniMax H3 open-weights specifics: 33B dense omni-modal, released 2026-07-31 (open weights 2026-08-03), native stereo audio + 2K (hosted) / 768p (local), up to 15s. ComfyUI **native day-0 support** (v0.30.0+, nodes merged PR #15224) — https://blog.comfy.org/p/minimax-h3-day-0-support-in-comfyui and https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- **LICENSE WARNING (critical for a commercial curation site):** MiniMax H3 Community License **excludes EU, UK, South Korea, USA** — restriction covers the OUTPUT videos too, not just weights. Commercial license via Comfy (only official reseller) or platform.minimax.io/h3-license. Sources: https://smeltcore.com/recipes/minimax-h3-on-rtx-3060-12-gb-video-audio-in-comfyui-measured-on-this-card/ (quotes license §I.5, §V.4) and https://www.earngenix.com/workflows/minimax-h3-comfyui-workflow

---

## T1 — Photorealistic Image Generation (persona/portrait, skin realism, prompt adherence)

Board: AR photorealistic lane, snapshot **2026-08-25**: https://arena.ai/leaderboard/text-to-image/photorealistic ; cross-checked AA general+photorealistic (Aug 2026): https://artificialanalysis.ai/image/leaderboard/text-to-image?style=general-and-photorealistic

| # | Model | Benchmark position (date) | VRAM (local) | License | ComfyUI | Notes |
|---|-------|---------------------------|--------------|---------|---------|-------|
| 1 | **GPT Image 2** (OpenAI) | #1 AR photorealistic 1380±6 (2026-08-25); #1 AA "GPT Image 2 (high)" Elo 1369, Apr 2026 release | API only | Proprietary | Cloud only | Best prompt adherence + text-in-image per llm-stats (updated 2026-08-30): https://llm-stats.com/leaderboards/best-ai-for-image-generation . Expensive: $211/1k imgs (AA). |
| 2 | **Grok Imagine Image 2.0** (xAI/SpaceXAI) | #2 AR photorealistic 1327±20 (preliminary, 956 votes — low sample) | API only | Proprietary | Cloud only | CONTESTED: preliminary entry, few votes. |
| 3 | **MAI-Image-2.6-Preview** (Microsoft AI) | #3 AR photorealistic 1324; #2 AA 1351 (Aug 2026 release) | API only | Proprietary | Cloud only | New Aug 2026; AA API "coming soon". |
| 4 | **Reve 2.1** | #4 AR photorealistic 1302; #3 AA 1323 (Jul 2026) | API only | Proprietary | Cloud only | $200/1k imgs (AA). |
| 5 | **Seedream 5.0 Pro** (ByteDance) | #6 AR photorealistic 1281 (behind Meta muse-image 1293); #11 AA 1279 (Jul 2026) | API only | Proprietary | Cloud only | Strong photoreal skin; muse-image beats it on AR photorealistic lane. |

**Local/open lane (what a self-hosted curation site can actually ship):**
| Model | AA Elo open-weights position (Aug 2026) | VRAM | License | ComfyUI |
|-------|------------------------------------------|------|---------|---------|
| **Ideogram 4.0** | **#1 open weights, 1219** (Jun 2026) | OPEN (unverified) | "Ideogram Open Model" (check terms) | Native (weights on HF) |
| **FLUX.2 [dev] Turbo** | #2 open, 1198 | ~8GB class (fal-hosted 4.3s/img: https://magichour.ai/model-leaderboard/image-generation) | FLUX.2 dev = **non-commercial** | Native |
| **FLUX.2 [klein] 4B** | lower Elo (~1068 AA) but **Apache 2.0** | ~8GB (thundercompute table) | Apache 2.0 — commercial OK | Native |
| **Z-Image Turbo** | 1133 (see verification above) | 16GB BF16 / 8GB FP8 / 6GB GGUF | Apache 2.0 | Native, official templates |
| **HunyuanImage 3.0** (Tencent) | AR image-edit 1302; open | ~24GB class (OPEN exact) | tencent-hunyuan-community | Extension/native |

**CONTESTED:** AR vs AA disagree on #2-#5 ordering (grok-2.0 vs MAI-2.6 vs Reve). Meta muse-image ranks #5 AR-photorealistic but is absent from AA top — new entry, votes still accumulating. For skin realism specifically, no board isolates "skin" — closest is the photorealistic lane; community census (reddit/x, separate task) needed.

**OPEN:** Ideogram 4.0 local VRAM figure; HunyuanImage 3.0 exact VRAM; muse-image AA entry missing.

---

## T2 — Character Consistency (same face across shots)

No dedicated Elo board for identity fidelity exists — this lane is **consensus-based** (community guides, Jun/Apr 2026) + the image-edit arena as the closest benchmark proxy. Marking the whole task CONSENSUS-PROXY.

**Benchmark proxy: AR Image Edit (single-image), 29.1M votes, 2026-08-25:** https://arena.ai/leaderboard/image-edit
Top: 1. gpt-image-2 1462 · 2. grok-imagine-image-2.0 1439 · 3. mai-image-2.6-preview 1417 · 4. muse-image 1405 · 5. mai-image-2.5 1399. Nano Banana Pro 1390 (#7). **Open weights leaders: qwen-image-edit 1241 (#31, Apache 2.0)**, qwen-image-edit-2511 1235, flux-2-dev 1226, flux-2-klein-4b 1188 (Apache), bagel 1026.

**Identity tool stack (community consensus, mid-2026):**
| Method | Best on | Fidelity | Cost/effort | Source |
|--------|---------|----------|-------------|--------|
| **PuLID-FLUX** (ByteDance, training-free) | Flux pipelines — default 2026 choice | tightest Flux ID lock, face-only | 1 ref image, 0 training; stacks w/ LoRA+ControlNet | https://nowaythisisai.com/blog/character-consistency-fictional-characters-mid-2026 + https://github.com/ToTheBeginning/PuLID (v0.9.1) |
| **InstantID** | SDXL pipelines | highest identity fidelity in 2026 head-to-heads; over-anchors vs prompt | 1 ref, 0 training | same NWTIA source |
| **IP-Adapter FaceID v2** | Pony/Illustrious; fastest setup | below PuLID/InstantID | 1 ref | NWTIA + https://aiofm.info/en/guides/consistent-ai-character |
| **Character LoRA (trained)** | production personas, 50+ images, body+face | **highest ceiling** ("nuclear option") | Ostris/ai-toolkit 4-8h on 4090; Civitai Rapid <5min (quality tradeoff); Flux LoRA ~$0.30/45min rented A100; FLUX.2 LoRA trains on 8-12GB GGUF | NWTIA + aiofm + https://apatero.com/blog/flux-2-pro-lora-training-character-consistency-2026 |
| **FLUX.2 multi-reference** | up to 8 ref images at inference | LoRA@0.55 + 4 refs > FLUX.1 LoRA@1.0 full (author test, 95%+ consistency claim) | 0 training, needs FLUX.2 | apatero guide |
| **360° orbit trick** | harvest 24-96 consistent frames from video-model orbit (LTX 3/Kling 3/Sora 2) then train LoRA on them | free multi-angle ref set | 0 training | NWTIA |

Production stack per working studios: low-strength LoRA (0.6) + PuLID (0.8) + ControlNet OpenPose → highest stability short of full LoRA (NWTIA, Jun 2026). PuLID for FLUX.2 exists as ComfyUI extension: https://github.com/ifayens/comfyui-pulid-flux2 (Mar 2026, supports Klein 4B/9B + Dev).

**Video-side consistency (same face into i2v):** generate keyframe with PuLID/LoRA → feed to i2v (aiofm). Reference-to-video models: FLUX Kontext claims 92% identity retention over 45s clips (vendor benchmark, treat as marketing until reproduced: https://www.flixly.ai/blog/flux-kontext-review-character-consistency-2026 — CONTESTED, single-vendor numbers); Seedance 2.0 @-reference locks face to uploaded refs (https://aijourn.com/seedance-2-0-replaces-the-prompt-only-video-paradigm-with-multimodal-references/).

**CONTESTED:** InstantID vs PuLID ordering flips by test (identity fidelity vs prompt adherence). LoRA-vs-adapter ceiling claims come from practitioner blogs, not blind-vote boards.

**OPEN:** no quantitative cross-model identity benchmark (e.g., face-similarity score across 100-shot sets) found on live boards — gap; community census should cover r/StableDiffusion practice.

---

## T3 — Text-to-Video (quality, motion, duration)

Boards: AR t2v (645,773 votes, **2026-08-25**): https://arena.ai/leaderboard/text-to-video ; AA t2v with-audio (Aug 2026, "added last month" includes Wan 3.0/LTX-2.5 — confirms freshness): https://artificialanalysis.ai/video/leaderboard/text-to-video

| # | Model | Position (date) | Duration | VRAM (local) | License | ComfyUI | Notes |
|---|-------|------------------|----------|--------------|---------|---------|-------|
| 1 | **Gemini Omni 1.1 Flash** (Google) | #1 AR t2v 1515±16 (2026-08-25); #2 AA w/ audio 1237 | — | API | Proprietary | Cloud | CONTESTED vs AA #1. |
| 2 | **Wan 3.0** (Alibaba) | **#1 AA w/ audio 1242** (Aug 2026, $12/min) | — | API (no open-weights tag on AA) | Proprietary | Cloud | CONTESTED vs AR (not in AR top list yet — new). |
| 3 | **Flux 3 Video** (BFL) | #3 AR 1495±17 (preliminary, 1,287 votes) | **up to 20s/gen**, native audio, i2v+t2v+v2v | API | Proprietary (promised open dev checkpoint NOT shipped as of Aug 2026 — https://invideo.io/blog/ai-video-models-with-audio/) | Cloud | 5 API workflows: https://poyo.ai/hub/flux-3-video-native-audio-guide |
| 4 | **Dreamina Seedance 2.0** (ByteDance) | #4 AR 1479; #5 AA 1221; Pixazo judge-panel #1 (1212): https://www.pixazo.ai/models/leaderboard/ai-video-generation | 4-15s, 12 multimodal refs | API | Proprietary | Cloud | Seedance 2.5 already at #3 AR i2v (1483) — fast iteration. |
| 5 | **MiniMax H3** | #6 AR t2v 1460; #4 AA w/ audio 1227 (**#1 open weights both boards**) | ≤15s, 2K hosted / 768p local, stereo audio | 12GB floor w/ offload+64GB RAM → 24GB comfortable → 42.5GB footprint | **Community license, territorial exclusions (EU/UK/KR/US)** | **Native day-0** (see verification) | Open-weights king. |

Also notable: Meta muse-video #7 AR 1457; HappyHorse-1.0/1.1 (Alibaba-ATH) #8 AR / #2 AA-no-audio — public API access unclear (https://awesomeagents.ai/leaderboards/video-generation-benchmarks-leaderboard/, 2026-04-17); **Sora 2 is DEAD** — product shut down 2026-03-24, API sunsets 2026-09-24 (same source). Kling 3.0 Pro: #9 AA 1108, 4K/60fps claims via VisionStory (https://www.visionstory.ai/).

**Open-weights t2v ranking (AA, Aug 2026):** 1. MiniMax H3 1227 · 2. LTX-2.5 Pro 1060 · 3. LTX-2.5 Fast 1060 (both ltx-community license, single-pass audio) · then LTX-2.3, Wan 2.2 A14B (Apache 2.0).

**CONTESTED:** #1 overall splits three ways (Gemini Omni on AR vs Wan 3.0 on AA vs Seedance 2.0 on Pixazo judge-panel). Elo-with-audio vs no-audio boards reorder heavily (audio included biases preference — documented on awesomeagents).

**OPEN:** Wan 3.0 open-weights status unconfirmed; HappyHorse public access; Flux 3 open dev date.

---

## T4 — Image-to-Video, NATIVE AUDIO/DIALOGUE (HD still → animate with defined speech + voice)

Board: AR image-to-video (1.84M votes, **2026-08-25**, fetched live): https://arena.ai/leaderboard/image-to-video

| # | Model | i2v position (2026-08-25) | Native audio capability | Voice control | VRAM/license | ComfyUI |
|---|-------|---------------------------|--------------------------|---------------|--------------|---------|
| 1 | **MiniMax H3** | **#1, 1494±6** | Only model claiming **native stereo** audio, one pass, voice+SFX+music | Omni-Reference: up to 3 audio refs, billed free (invideo table) | see T3 — territorial license | Native |
| 2 | **Gemini Omni 1.1 Flash** | #2, 1488 | joint A/V (Gemini Omni family = audio-native) | own voices | API | Cloud |
| 3 | **Seedance 2.5 / 2.0** | #3 1483 / #4 1477 | single-pass joint A/V, dialect-aware lip-sync; **2.0 lip-syncs to UPLOADED audio** (@-refs: 3 audio ≤15s; 2.5 raises to 10 audio refs) | uploaded audio lip-sync — the "defined speech" workflow | API | Cloud |
| 4 | **Grok Imagine Video 1.5** | #6, 1459 | one-pass SFX/ambience/dialogue | **preset voices only, max 3/request, NO upload** | API ($0.05/s AR pricing col) | Cloud |
| 5 | **Veo 3.1 (audio)** | #11-15 cluster, 1398 | always-on dialogue+SFX+ambience, "short speech segments remain weak" (Google's own admission, invideo) | no audio input path | API, $0.50/s | Cloud |
| 6 | **Wan 2.7 i2v** | #9, 1427 | accepts **2-30s driving audio** that conditions motion | driving audio | API (open line ends at 2.2, Apache) | Cloud (2.2 open via WanVideoWrapper) |
| 7 | **Kling 3.0 / 2.6** | kling-v3-pro #17 1356; 2.6 lower | 2.6 = first native-audio Kling; quoted text in prompt triggers lip-sync; Omni binds voice from 5-30s sample (non-CN/EN auto-translated to EN — caveat) | voice binding + prompt dialogue | API | Cloud |
| 8 | **HappyHorse-1.0** | #8, 1442 | joint A/V, lip-synced dialogue in **7 languages** (EN/ZH/Cantonese/JA/KO/DE/FR) — language-coverage leader | — | API unclear | Cloud |

Audio-capability census source (table of every model, "native audio since" dates, published **2026-08-07**): https://invideo.io/blog/ai-video-models-with-audio/ — canonical for this lane. Quote: "if the job is a character speaking on camera, the shortlist as of August 2026 is HappyHorse, Kling 3.0, and Seedance."

**Open-weights i2v+audio (the local lane):**
| Model | Status | VRAM | Source |
|-------|--------|------|--------|
| **MiniMax H3 (FL2VA/Ref2VA)** | best local AV; stereo same-pass locally | 12GB floor (heavy offload) → 24GB comfortable | https://comfyui-wiki.com/en/news/2026-08-03-minimax-h3-open-weights-comfyui + smeltcore recipe |
| **LTX-2 / 2.5** | open weights, single-pass synchronized audio; Pro endpoint adds audio-to-video | OPEN (19B class, ~24GB typical — unverified) | invideo census + AA open list |
| **Ovi** (Character.AI) | open twin-backbone video+audio, 5B audio branch pretrained; 5s@24fps 720p-class; `<speech>` tags in prompt for dialogue | runs on **24GB with cpu_offload** | https://github.com/joshirishi/Ovi — ComfyUI via kijai WanVideoWrapper (WIP branch) |
| **DreamX-Creator 1.0** (Alibaba) | open 7B joint A/V generator + 2K refiner, first-frame+prompt → speech/Foley/ambience, arXiv Aug 2026 | OPEN (7B class) | https://arxiv.org/html/2608.31106 |
| **UniAVGen** | research framework, reference image + speech text → joint AV; CVPR 2026 | research | https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_UniAVGen_Unified_Audio_and_Video_Generation_with_Asymmetric_Cross-Modal_Interactions_CVPR_2026_paper.pdf |

**Workflow for "HD still → animate with defined speech + defined voice" (task spec):**
1. Still: T1 winner or local lane (GPT Image 2 / Ideogram 4.0 / Z-Image-Turbo for speed).
2. Animate+speech: (a) **Seedance 2.0** uploaded-audio lip-sync (voice from T5 model); (b) **Kling Omni** voice-binding from 5-30s sample; (c) **MiniMax H3** audio references (local, stereo); (d) **Wan 2.7** driving audio for performance-sync; (e) open/local: Ovi `<speech>` tags, LTX-2.3 Pro audio-to-video.
3. Voice: T5 model (Eleven v3 / Fish S2 Pro / F5-TTS local) → feed as the audio reference.

**CONTESTED:** "world's first native audio" claimed by both Kling 2.6 (Topview: https://www.topview.ai/make/kling-2-6) and others; actual first was Veo 3 May 2025 (invideo timeline). Audio-quality rankings differ from video-quality rankings — Kling 3.0's audio ranked below Veo 3.1's by reviewers (invideo).

**OPEN:** LTX-2.5 exact local VRAM; DreamX weights availability beyond paper; Wan 3.0 audio-input status.

---

## T5 — Voice/TTS (realistic speech, emotion, cloning)

Boards (AA, live Aug 2026 — both fetched):
- Provider-voice (native voices): https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice
- Controlled-voice (same 8 cloned voices — the CLONING board): https://artificialanalysis.ai/text-to-speech/leaderboard/controlled-voice

**Provider-voice top 5 (Aug 2026):** 1. Cartesia **Sonic 3.6** 1282 (Aug 2026) · 2. Inworld **Realtime TTS-2** 1250 · 3. SpeechifyAI **Simba 3.2** 1241 · 4. Alibaba **Qwen-Audio-3.0-TTS-Plus** 1240 · 5. VUI Labs **Luna TTS** 1224. Eleven v3 Conversational 1209 at #8; Gemini 3.1 Flash TTS 1206 #9. Best open: **Breeze TTS 2 (BreezeBlue) 1212** (#7 overall).

**Controlled-voice / cloning top 5 (Aug 2026):** 1. Inworld **Realtime TTS-2** 1123 · 2. Cartesia **Sonic 3.6** 1119 · 3. **Sonic 3.5** 1096 · 4. Realtime TTS-2 Flash 1075 · 5. **Eleven v3** 1062 (ElevenLabs, Feb 2026, $100/1M). Then StepAudio 2.5, SpaceXAI TTS, MiniMax Speech 2.8 HD 1028.

| Model | Position (board, date) | Cloning | License | Local VRAM | ComfyUI |
|-------|------------------------|---------|---------|------------|---------|
| Sonic 3.6 (Cartesia) | #1 provider 1282 / #2 cloning 1119 (AA, Aug 2026) | pro cloning | Proprietary, ~90ms TTFA (https://www.coval.ai/blog/best-text-to-speech-providers-in-2026-how-to-choose-(and-why-vendor-benchmarks-lie)/) | API | n/a |
| Realtime TTS-2 (Inworld) | #2 provider 1250 / **#1 cloning 1123** | instant 5-15s | Proprietary | API | n/a |
| Eleven v3 (ElevenLabs) | #8 provider 1209 / #5 cloning 1062 | best-in-class cloning per aimlapi tests | Proprietary $100/1M | API | n/a |
| Gemini 3.1 Flash TTS | #9 provider 1206; #2 VoiceArena 1071 (https://voicearena.com/tts-leaderboard/us-english) | no | Proprietary | API | n/a |
| **Breeze TTS 2** (BreezeBlue) | **#1 open weights** 1212 provider / 1007 cloning (AA) | yes | Open weights (license terms OPEN) | OPEN | OPEN |
| **Fish Audio S2 Pro** | #16 cloning 1003; best open on older Jul snapshot 1128 (offlinetts) | native, 80+ langs | open weights + API $15/1M | GPU for self-host | via API/extensions |
| **Kokoro 82M** | Elo ~1056, largest sample (5,368) | no cloning | Apache 2.0 | **CPU** | extension |
| **F5-TTS** | leading open zero-shot cloning per https://presenc.ai/research/best-open-weight-text-to-speech-models-2026 (3s ref, MOS ~4.3) | yes, 3s ref | **CC-BY-NC + commercial exception — check** | ~6GB | extension |
| **Orpheus 3B** | MOS ~4.4, emotion tags | yes | Apache 2.0 | ~8GB class | extension |
| **CosyVoice 3** | multilingual + cloning, 9 langs + 18 CN dialects (offlinetts Jul 2026) | zero-shot | Apache 2.0 | 8GB+ | extension |
| **Zonos2 8B** | "strongest open-weight" per offlinetts editorial (CONTESTED vs AA open ranking) | yes | Apache 2.0 | 16GB+ | extension |

**CONTESTED:** open-weights TTS king — AA says Breeze TTS 2 (1212); offlinetts editorial (Jul 2026) says Zonos2/CosyVoice3; presenc says F5-TTS for cloning. Different methodologies (blind Elo vs editorial). Churn is fast: Inworld RT 1.5 Max led in Apr 2026 (aimlapi), Sonic 3.6 by Aug — monthly re-rank needed. offlinetts itself flags its May 2026 numeric table as "mixed sources... treat as dated" — use AA as canonical.

**OPEN:** Breeze TTS 2 license text + VRAM + ComfyUI path; Voxtral TTS license (Mistral, open on AA); whether Chatterbox Turbo (MIT) still clones well vs S2 Pro (AA controlled-voice says S2 Pro 1003 > Chatterbox 931).

---

## LEADERBOARD / BENCHMARK SITE STATUS (live vs dead)

### LIVE & CURRENT (verified this session)
| Site | URL | Measures | Last-updated evidence |
|------|-----|----------|----------------------|
| Arena.ai (LMArena) — t2i, photorealistic, image-edit, t2v, i2v | https://arena.ai/leaderboard/text-to-image (+ /text-to-video, /image-to-video, /image-edit) | crowdsourced blind-vote Elo per modality/lane | boards stamped **Aug 25, 2026**; contains Aug 2026 models (MAI-2.6, flux-3-video-20260811, grok-video-1.5) |
| Artificial Analysis — image | https://artificialanalysis.ai/image/leaderboard/text-to-image | blind-vote Elo + price + speed | GPT Image 2 (Apr 2026), MAI-2.6-Preview (Aug 2026) ranked; Elo values match live FAQ text |
| Artificial Analysis — video | https://artificialanalysis.ai/video/leaderboard/text-to-video | Elo split with-audio / no-audio | "Added in last month: Minimax H3 Max (fal), LTX-2.5, Wan 3.0, Vidu Q3 Turbo" |
| Artificial Analysis — TTS (both boards) | https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice + /controlled-voice | speech Elo; cloning board uses 8 fixed cloned voices | Sonic 3.6 / RT TTS-2 (Aug 2026 releases) at top |
| VoiceArena | https://voicearena.com/tts-leaderboard/us-english | TTS Bradley-Terry Elo + latency, production-call sentences | Sonic-3.6 (Aug 2026) #1, Maya-2-Global (Jul 2026) on board |
| gptbased (mirror of AR) | https://gptbased.com/leaderboard/text_to_image/photorealistic | mirrors arena Elo + OpenRouter pricing | matches Aug 2026 AR numbers |
| awesomepapers.io (mirror) | https://awesomepapers.io/generative-models/leaderboards/Text-to-Video%20Arena%20(LMArena)/text-to-video-arena | LMArena mirror with per-score verification dates | score date **2026-08-04** marked "verified" |
| Pixazo video leaderboard | https://www.pixazo.ai/models/leaderboard/ai-video-generation | own judge-panel (Qwen2.5-VL + RAFT optical flow) Elo, 450 matches, calibrated to AA/AR | methodology page live; "Seedance 2.0 leads 1212" current; re-runs full board per new model |
| Lumenfall Arena | https://lumenfall.ai/arena/models/z-image-turbo | blind community votes + skill percentiles | has current Z-Image/GPT-Image-2 matchups; update cadence OPEN |
| llm-stats image guide | https://llm-stats.com/leaderboards/best-ai-for-image-generation | TrueSkill from blind votes, editorial overlay | "Updated August 30, 2026" |
| VidScore | https://vidscore.dev/leaderboard | quality×price blend, re-derives from AA weekly | derivative of AA (says so) — use AA directly |

### STALE / SNAPSHOT / DEAD
| Site | URL | Status | Evidence |
|------|-----|--------|----------|
| **Magic Hour image leaderboard** | https://magichour.ai/model-leaderboard/image-generation | **STALE SNAPSHOT 2026-04-06** — page itself says "figures are from our export, not live pages... may have moved on" | snapshot date printed on page; missing all May-Aug 2026 models from top |
| **Magic Hour video leaderboard** | https://magichour.ai/model-leaderboard/text-to-video | same — **STALE SNAPSHOT 2026-04-06** | same disclaimer; top-3 (Seedance 2.0/SkyReels V4/PixVerse V6) is 5 months old |
| awesomeagents video benchmarks article | https://awesomeagents.ai/leaderboards/video-generation-benchmarks-leaderboard/ | static article dated **2026-04-17**, not a live board — useful for methodology + Sora shutdown record, not for current ranks | "Rankings as of April 17, 2026" |
| offlinetts TTS tables | https://offlinetts.com/blog/tts-arena-leaderboard-2026/ + /tts-model-ranking-2026/ | **self-flagged editorial snapshots** ("original numeric table mixed sources... treat as dated comparison to verify"); May/Jul 2026 data predates Sonic 3.6 / RT TTS-2 | their own disclaimer |
| tts.ai arena | https://tts.ai/tts-arena/ | semi-static catalog w/ community votes; ranks Kokoro #1 by "official score" — contradicts every live blind-vote board (Kokoro is ~rank 30+ on AA) → **treat as DEAD for ranking purposes** | Kokoro-#1 ordering vs AA Elo 1056 |
| Coqui XTTS v2 / OpenVoice v2 / StyleTTS 2 / MetaVoice | (models, on AA board) | legacy 2023-2024 models still ranked bottom of live boards — not dead sites, dead-end models | AA controlled-voice ranks 36/37/… |
| VBench / VBench-2.0 | (academic) | NOT fetched this session — OPEN: verify vbench.org freshness before citing | — |

---

## OPEN ITEMS (queued, not blocking)
1. Ideogram 4.0 open-weights VRAM + "Ideogram Open Model" license commercial terms.
2. Wan 3.0 open-weights status (AA shows no open tag; Wan line historically open at ≤2.2).
3. Breeze TTS 2 (top open TTS on AA): license text, VRAM, ComfyUI path — nothing beyond Elo found.
4. LTX-2.5 Pro/Fast local VRAM figures.
5. Z-Image-Base / Z-Image-Edit release status — HF README still says "To be released"; recheck Tongyi-MAI repo before publishing.
6. VBench freshness check (academic board).
7. Community consensus census (reddit/x) for persona/NSFW lanes — separate task per context brief, NOT covered here.
8. NSFW-capability lane entirely absent from all boards above (arena policies exclude it) — needs its own census (Civitai-derived), by design of the curation site.
