# CURATION REVIEW — workflows + nsfw lanes (manager's personal pass, 2026-09-02)

## workflows (30) — verdict: 29/30 approved, 1 under-tagged family
names are outcome-first per plan ("Two Characters, One Frame — No Color Bleed", "Sound-On Video in One Pass"). quality bar met.
flags:
- 2498991 "Sound-On Video in One Pass — LTX-2.3": audio tag MISSING in draft (audio:[]) — must be audio:["narration","music"] or similar at merge; it is the flagship i2v-audio entry for the task axis (REQUIREMENTS:38). same for 1818841 + 1853617 (sound variants) — audio tagging pass required before sitegen.
- duration 0/30 coverage (codex build log caught it): workflows drafts under-tagged on duration — patch pass: video-capable entries get duration buckets (est from model family: wan 5s, ltx 10s+, hunyuan 5-10s).
- 4 low-confidence entries (339604, 2426853, 2498991, 1048302): verify at merge; until then confidence badge "low" shows.
- 1309369 vs 1824577 "Still to Moving Shot" family: intentional (old vs current-gen rebuild) — cross-reference in handoff_next.

## nsfw (30) — verdict: 29/30 approved, 1 rename
professional register achieved throughout ("wine guide" tone: Mythic Wardrobe, Silken Finish Booster, Kinetic Bounce — Chest Motion Physics). zero crudity in names.
flags:
- 57573 "Mystery Cellar — 'Mtu Virus' Concept (Unverified)": rename -> "Mystery Cellar — Signature Concept Layer" (unverified stays in notes/confidence, not the name).
- 1343431, 1269557, 645017, 347111: motion/video entries on nsfw lane — outputs must carry video tags at merge (task axis).

## STRUCTURAL DECISION — cross-lane duplicates (mine, binding at merge)
11 ids appear in BOTH persona and nsfw drafts with different our_names (599757 Myth-Mark/Mythic Wardrobe; 1145743 Fine-Grain/Silken Finish; 1377820 Micro-Thread/Micro-Texture; 667086 Uncensor Key/Master Key; 438059 Motion Dial/Action Pose; 65423 Niji Tribute/Niji Emulation; 1133519 Krekkov Signature/Krekkov Study; 1586542 Gallery Touch/Painterly Finish; 633524 Deep Stage/Set Dressing; 1979448 Anime Out of Place/Two Worlds; 29215 Sensei's Flat Palette/Gacha Flat).
RULE: one civitai id = ONE entry = ONE our_name (the persona/neutral name — it reads correctly in both contexts). lanes = array (["personas","mature"]). the adult framing text becomes lane_note shown only inside the mature lane. preview gating stays per-nsfwLevel regardless of lane. sitegen merge implements this; build_check counts unique ids.
