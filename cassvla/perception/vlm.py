"""Offline VLM pass (Phase 5): one scene embedding and one prompted answer per decision frame, cached to disk.

No VLM call happens inside the simulator loop. ``scripts/cache_vlm.py`` runs this over rendered frames
once; the selector and the evaluation only read the cache (``load_cache``).

Two outputs per frame:

* **embedding** - the vision tower's patch features, mean-pooled into one vector. It does not depend on the
  prompt, so it is a pure scene encoding.
* **prompted answer** - the VLM is shown the frame, the ego speed and the candidate maneuvers, and asked
  for visible hazards, occlusion, light state and the single query it would make. ``parse_answer`` turns the
  reply into a fixed schema and marks replies it could not parse instead of failing.

The prompt never contains oracle information (safety flags, c*, scores).
"""
import hashlib
import json
import os
import re
import time
from glob import glob

import numpy as np

DEFAULT_MODEL = "mlx-community/Qwen2.5-VL-3B-Instruct-4bit"
QUERIES = ("roi", "depth", "collision", "none")
LIGHTS = ("green", "yellow", "red", "none", "unknown")
MAX_HAZARDS = 5
SHARD_SIZE = 200

MANEUVERS = {
    "keep": "keep the lane at the current speed",
    "keep_fast": "keep the lane and speed up by 3 m/s",
    "decelerate": "keep the lane and slow to half speed",
    "stop": "brake to a stop in the lane",
    "change_left": "change to the left lane at the current speed",
    "change_right": "change to the right lane at the current speed",
}

PROMPT = """You are the perception module of a self-driving car. The image is its front camera.
The car is driving at {speed:.1f} m/s. The planner must choose one of these maneuvers for the next 5 seconds:
{candidates}
Before it chooses, it may make one extra perception query:
- roi: inspect a region for hidden or distant objects and the traffic-light state
- depth: measure the distance and closing speed of nearby objects
- collision: check each maneuver for geometric collision with tracked objects
- none: no query is needed to choose safely
Reply with JSON only, in this form:
{{"hazards": ["short phrase", ...], "occlusion": true or false, "light": "green|yellow|red|none|unknown", "query": "roi|depth|collision|none"}}"""


def describe_candidates(names):
    return "\n".join(f"- {n}: {MANEUVERS.get(n, n.replace('_', ' '))}" for n in names)


def build_prompt(speed, names):
    return PROMPT.format(speed=float(speed), candidates=describe_candidates(names))


def prompt_hash():
    return hashlib.sha256(PROMPT.encode()).hexdigest()[:12]


def _bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "yes", "1")
    return bool(v) if isinstance(v, (int, float)) else False


def parse_answer(text):
    """Reply text -> {hazards, occlusion, light, query, parse_error}. Never raises."""
    out = dict(hazards=[], occlusion=False, light="unknown", query="none", parse_error=False)
    start, end = text.find("{"), text.rfind("}")
    try:
        obj = json.loads(text[start:end + 1]) if 0 <= start < end else None
    except json.JSONDecodeError:
        obj = None
    if not isinstance(obj, dict):
        out["parse_error"] = True
        return out
    hazards = obj.get("hazards", [])
    if isinstance(hazards, str):
        hazards = [hazards]
    out["hazards"] = [str(h).strip() for h in hazards if str(h).strip()][:MAX_HAZARDS] if isinstance(hazards, list) else []
    out["occlusion"] = _bool(obj.get("occlusion", False))
    light = str(obj.get("light", "unknown")).strip().lower()
    out["light"] = light if light in LIGHTS else "unknown"
    query = re.sub(r"[^a-z]", "", str(obj.get("query", "")).lower())
    if query in QUERIES:
        out["query"] = query
    else:
        out["parse_error"] = True
    return out


class MLXBackend:
    """Qwen2.5-VL (or another mlx-vlm model) on Apple Silicon. Imports mlx lazily."""

    def __init__(self, model_id=DEFAULT_MODEL, revision=None, max_tokens=120):
        import mlx.core as mx
        from huggingface_hub import snapshot_download
        from mlx_vlm import load
        self.mx, self.model_id, self.max_tokens = mx, model_id, max_tokens
        path = snapshot_download(model_id, revision=revision)
        self.revision = os.path.basename(os.path.normpath(path))
        self.model, self.processor = load(path)
        # the 4-bit checkpoint keeps the vision tower in float16, which overflows to NaN on some frames (flat
        # intersection views): the reply became "!!!!" and the embedding NaN. float32 avoids it; mlx-vlm casts
        # pixel values to the vision tower's dtype, so generation uses it too.
        self.model.vision_tower.set_dtype(mx.float32)
        self.vision_dtype = "float32"

    def _chat(self, text):
        from mlx_vlm.prompt_utils import apply_chat_template
        return apply_chat_template(self.processor, self.model.config, text, num_images=1)

    def embed(self, image_path):
        from mlx_vlm.utils import prepare_inputs
        mx = self.mx
        t0 = time.time()
        inp = prepare_inputs(self.processor, images=[image_path], prompts=[self._chat("Describe the image.")],
                             image_token_index=getattr(self.model.config, "image_token_index", None))
        pv = inp["pixel_values"].astype(mx.float32)
        h = self.model.vision_tower(pv, inp["image_grid_thw"], output_hidden_states=False)
        e = mx.mean(h.astype(mx.float32), axis=0)
        mx.eval(e)
        return np.array(e, dtype=np.float32), dict(seconds=round(time.time() - t0, 3))

    def ask(self, image_path, text):
        from mlx_vlm import generate
        t0 = time.time()
        r = generate(self.model, self.processor, self._chat(text), image=[image_path], max_tokens=self.max_tokens, temperature=0.0)
        return r.text, dict(seconds=round(time.time() - t0, 3), prompt_tokens=int(r.prompt_tokens), generation_tokens=int(r.generation_tokens))

    def peak_memory_gb(self):
        return round(self.mx.get_peak_memory() / 1e9, 3)


# ---- cache on disk -------------------------------------------------------------------------------------

def _write_shard(out_dir, keys, embs):
    n = len(glob(os.path.join(out_dir, "emb_*.npz")))
    path = os.path.join(out_dir, f"emb_{n:05d}.npz")
    np.savez(path + ".tmp.npz", keys=np.array(keys), emb=np.stack(embs).astype(np.float32))
    os.replace(path + ".tmp.npz", path)


def load_cache(out_dir):
    """-> dict(meta, keys, emb (N, D) float32, prompted {key: answer dict}). Missing parts come back empty."""
    meta_path = os.path.join(out_dir, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    keys, embs = [], []
    for path in sorted(glob(os.path.join(out_dir, "emb_*.npz"))):
        if path.endswith(".tmp.npz"):
            continue
        z = np.load(path)
        keys += [str(k) for k in z["keys"]]
        embs.append(z["emb"])
    prompted = {}
    pp = os.path.join(out_dir, "prompted.jsonl")
    if os.path.exists(pp):
        with open(pp) as f:
            for line in f:
                r = json.loads(line)
                prompted[r["key"]] = r
    emb = np.concatenate(embs) if embs else np.zeros((0, 0), np.float32)
    return dict(meta=meta, keys=keys, emb=emb, prompted=prompted)


def cache_frames(frames, frames_dir, backend, out_dir, mode="both", log=print):
    """Run ``backend`` over ``frames`` and append results to the cache in ``out_dir``. Resumable.

    ``frames``: iterable of dicts with ``key``, ``path`` (relative to ``frames_dir``), ``speed`` and
    ``candidates`` (maneuver names). ``mode``: ``embed``, ``ask`` or ``both``. Returns per-frame timings."""
    os.makedirs(out_dir, exist_ok=True)
    meta = dict(model=getattr(backend, "model_id", type(backend).__name__), revision=getattr(backend, "revision", None),
                prompt_hash=prompt_hash(), prompt=PROMPT, embedding="vision tower patch features, mean-pooled",
                vision_dtype=getattr(backend, "vision_dtype", None))
    meta_path = os.path.join(out_dir, "meta.json")
    if os.path.exists(meta_path):
        old = json.load(open(meta_path))
        for k in ("model", "revision", "prompt_hash", "vision_dtype"):
            if old.get(k) != meta[k]:
                raise ValueError(f"cache in {out_dir} was made with {k}={old.get(k)!r}, not {meta[k]!r}; use a new --out")
    else:
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=1)

    have = load_cache(out_dir)
    have_emb, have_ask = set(have["keys"]), set(have["prompted"])
    timings, keys, embs = [], [], []
    with open(os.path.join(out_dir, "prompted.jsonl"), "a") as fp:
        for i, fr in enumerate(frames):
            img = os.path.join(frames_dir, fr["path"])
            t = dict(key=fr["key"])
            if mode in ("embed", "both") and fr["key"] not in have_emb:
                e, s = backend.embed(img)
                if not np.isfinite(e).all():
                    if keys:
                        _write_shard(out_dir, keys, embs)
                    raise ValueError(f"non-finite embedding for {fr['key']} ({img})")
                keys.append(fr["key"])
                embs.append(e)
                t["embed"] = s
                if len(keys) >= SHARD_SIZE:
                    _write_shard(out_dir, keys, embs)
                    keys, embs = [], []
            if mode in ("ask", "both") and fr["key"] not in have_ask:
                text, s = backend.ask(img, build_prompt(fr["speed"], fr["candidates"]))
                fp.write(json.dumps(dict(key=fr["key"], raw=text, **parse_answer(text))) + "\n")
                fp.flush()
                t["ask"] = s
            if len(t) > 1:
                timings.append(t)
            if log and (i + 1) % 50 == 0:
                log(f"{i + 1} frames")
    if keys:
        _write_shard(out_dir, keys, embs)
    return timings


def summarize_timings(timings, peak_memory_gb=None):
    out = dict(frames=len(timings), peak_memory_gb=peak_memory_gb)
    for part in ("embed", "ask"):
        s = np.array([t[part]["seconds"] for t in timings if part in t], float)
        if len(s):
            out[part] = dict(n=int(len(s)), mean_s=round(float(s.mean()), 3), p50_s=round(float(np.median(s)), 3),
                             p95_s=round(float(np.percentile(s, 95)), 3))
    return out
