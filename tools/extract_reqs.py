#!/usr/bin/env python3
"""extract_reqs v1 — the import moat (#78): models + custom nodes per kept workflow.

Parse PROVEN against real zips (diag at ~/.cache/req-diag): civitai workflow
zips carry ComfyUI UI-graph JSON {nodes: [{type, widgets_values}]}; API-format
{class_type, inputs} also supported. Model names live in widgets_values[0].

IN:  data/staged/{MOTION,SPEECH_VOICE,CAMERA_ANGLE,ADS}.json (kept entries),
     ~/.config/civitai/api.key
OUT: data/funnel/requirements.json {id: {models: [{name, folder}],
                                        nodes: [{class_type, manager_search}]}}
"""
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
STAGED = ROOT / "data" / "staged"
OUT = ROOT / "data" / "funnel" / "requirements.json"
ZIPS = Path("/home/eder/.cache/req-zips")
API = "https://civitai.com/api/v1"
CAP = 60

LOADERS = {
    "CheckpointLoaderSimple": "models/checkpoints/", "CheckpointLoader": "models/checkpoints/",
    "LoraLoader": "models/loras/", "LoraLoaderOnly": "models/loras/",
    "VAELoader": "models/vae/", "UNETLoader": "models/diffusion_models/",
    "DualCLIPLoader": "models/text_encoders/", "CLIPLoader": "models/text_encoders/",
    "UpscaleModelLoader": "models/upscale_models/", "ControlNetLoader": "models/controlnet/",
}
CORE = set(LOADERS) | {
    "KSampler", "KSamplerSelect", "KSamplerAdvanced", "CLIPTextEncode", "CLIPSetLastLayer",
    "VAEDecode", "VAEEncode", "VAEEncodeForInpaint", "LoadImage", "LoadImageMask", "SaveImage",
    "PreviewImage", "PreviewLatent", "EmptyLatentImage", "EmptySD3LatentImage", "EmptyHunyuanLatentVideo",
    "ConditioningCombine", "ConditioningConcat", "ConditioningAverage", "ConditioningZeroOut",
    "ConditioningSetMask", "ConditioningSetTimestepRange", "SetLatentNoiseMask", "LatentUpscale",
    "LatentComposite", "ImageScale", "ImageUpscaleWithModel", "ImageScaleBy", "ImageInvert",
    "ImageConcatMulti", "ImagePadForOutpaint", "LoadImageOutput", "MaskToImage", "ImageToMask",
    "ModelSamplingSD3", "ModelSamplingFlux", "ModelSamplingAuraFlow", "FluxGuidance", "BasicGuider",
    "BasicScheduler", "RandomNoise", "SamplerCustomAdvanced", "DisableNoise", "FlipSigmas",
    "SplitSigmas", "SplitSigmasDenoise", "PolyexponentialScheduler", "KarrasScheduler",
    "VPScheduler", "BetaSamplingScheduler", "CFGGuider", "DualCFGGuider", "PerpNegGuider",
    "Reroute", "Note", "PrimitiveNode", "MarkdownNote", "easy anything?", "Anything Everywhere?",
    "ImageBlend", "ImageCrop", "ImageBlur", "MaskBlur", "MaskComposite", "GrowMask", "InvertMask",
    "TextNode", "StringFunction", "ShowText|pysssss", "easy showAnything", "easy string",
    "ImpactWildcardProcessor", "ImpactWildcardEncode", "SeafoamProductPlacer",
    "CLIPVisionEncode", "CLIPVisionLoader", "StyleModelApply", "StyleModelLoader",
    "GLIGENLoader", "GLIGENTextBoxApply", "HyperTile", "PatchModelAddDownscale",
    "LoraLoaderModelOnly", "UNetSelfAttentionMultiply", "UNetCrossAttentionMultiply",
    "VAEDecodeTiled", "VAEEncodeTiled", "RepeatLatentBatch", "LatentAdd", "LatentSubtract",
    "LatentMultiply", "LatentInterpolate", "LatentBlend", "LatentFlip", "LatentRotate",
}


def api_get(path, key):
    req = Request(f"{API}{path}", headers={"Authorization": f"Bearer {key}", "User-Agent": "garimpo/0"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def parse_workflow(data):
    models, nodes = {}, {}
    entries = []
    if isinstance(data, dict) and isinstance(data.get("nodes"), list):
        entries = [{"type": n.get("type"), "widgets": n.get("widgets_values") or []} for n in data["nodes"]]
    elif isinstance(data, dict):
        entries = [{"type": v.get("class_type"), "widgets": list((v.get("inputs") or {}).values())}
                   for v in data.values() if isinstance(v, dict)]
    elif isinstance(data, list):
        entries = [{"type": v.get("class_type"), "widgets": list((v.get("inputs") or {}).values())}
                   for v in data if isinstance(v, dict)]
    for e in entries:
        ntype = str(e["type"] or "")
        if not ntype:
            continue
        if ntype in LOADERS:
            flat = []
            for w in e["widgets"]:
                if isinstance(w, str):
                    flat.append(w)
                elif isinstance(w, list):
                    flat.extend(x for x in w if isinstance(x, str))
            names = [w for w in flat if "." in w] or flat[:1]
            for name in names:
                models[name] = LOADERS[ntype]
        if ntype not in CORE and not ntype.startswith("__"):
            nodes[ntype] = True
    return ({"name": n, "folder": f} for n, f in models.items()), list(nodes)


def main():
    key = Path("~/.config/civitai/api.key").expanduser().read_text().strip()
    targets = []
    for stage in ("MOTION", "SPEECH_VOICE", "CAMERA_ANGLE", "ADS"):
        f = STAGED / f"{stage}.json"
        if not f.exists():
            continue
        for e in json.loads(f.read_text())["entries"]:
            if e.get("review_flag") is False and (e.get("preview") or {}).get("url_width450") and str(e.get("id", "")).isdigit():
                targets.append(e)
    targets.sort(key=lambda e: -(e.get("composite") or 0))
    targets = targets[:CAP]
    print(f"targets: {len(targets)} kept workflows", file=sys.stderr)
    ZIPS.mkdir(parents=True, exist_ok=True)
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    for i, e in enumerate(targets):
        mid = e["id"]
        if str(mid) in out and (out[str(mid)].get("models") or out[str(mid)].get("nodes")):
            continue
        try:
            m = api_get(f"/models/{mid}", key)
            ver = (m.get("modelVersions") or [{}])[0]
            arc = next((f for f in ver.get("files", []) if f.get("type") == "Archive"), None)
            if not arc:
                out[str(mid)] = {"models": [], "nodes": [], "note": "no archive file"}
                continue
            req = Request(arc["downloadUrl"], headers={"Authorization": f"Bearer {key}", "User-Agent": "garimpo/0"})
            zpath = ZIPS / f"{mid}.zip"
            with urlopen(req, timeout=60) as r, open(zpath, "wb") as w:
                w.write(r.read())
            models, nodes = {}, []
            with zipfile.ZipFile(zpath) as z:
                for name in z.namelist():
                    if not name.lower().endswith(".json"):
                        continue
                    try:
                        wf = json.loads(z.read(name))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    mg, ng = parse_workflow(wf)
                    for g in mg:
                        models[g["name"]] = g["folder"]
                    nodes = sorted(set(nodes) | set(ng))
            out[str(mid)] = {"models": [{"name": n, "folder": f} for n, f in sorted(models.items())],
                             "nodes": [{"class_type": n, "manager_search": n} for n in nodes]}
        except Exception as ex:
            out[str(mid)] = {"models": [], "nodes": [], "error": str(ex)[:80]}
        time.sleep(0.5)
        if (i + 1) % 10 == 0:
            OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
            print(f"  early write: {len(out)} ids", file=sys.stderr)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    filled = sum(1 for v in out.values() if v.get("models") or v.get("nodes"))
    print(f"done: {len(out)} ids, {filled} with models/nodes", file=sys.stderr)


if __name__ == "__main__":
    main()
