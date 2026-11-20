"""Offline VLM pass over rendered frames (Phase 5): cached embeddings, scene descriptions and a prompted tool choice.

    python scripts/vlm_encode.py embed    --frames out/v2_frames --model MODEL_DIR --out out/vlm
    python scripts/vlm_encode.py describe --frames out/v2_frames --model MODEL_DIR --out out/vlm
    python scripts/vlm_encode.py prompt   --frames out/v2_frames --model MODEL_DIR --out out/vlm --data out/v2_dataset --split val

Runs inside the vLLM Apptainer image, so it imports only torch, transformers, vllm, numpy and PIL. MODEL_DIR is a
local snapshot directory; nothing is downloaded.

embed writes <out>/embed.npz. Each row holds three float16 vectors of the language model: the mean over the image
tokens at the middle layer, the same at the last layer, and the last prompt token at the last layer.
describe writes <out>/describe.jsonl, and prompt writes <out>/prompt_<split>.jsonl. The prompt sees the frame and
the candidate names only, never the oracle's labels or ranking. --limit N keeps the first N frames for a smoke test.
"""
import argparse
import json
import os
import time

import numpy as np

EMBED_PROMPT = "You are the perception module of a self-driving car. Look at the road ahead and the objects that matter for choosing the next manoeuvre."
DESCRIBE_PROMPT = ("You are the perception module of a self-driving car. In at most three sentences, describe the road "
                   "ahead, the traffic light state if one is visible, and every object that could affect the next manoeuvre.")
TOOLS = ("roi", "depth", "collision", "none")
PROMPT_TEMPLATE = """You are the planner of a self-driving car, looking through the front camera.
The candidate manoeuvres are: {cands}. Without extra information, the planner would pick "{top1}".
You may make at most one extra perception query before deciding:
- roi: lists the objects in the corridor of the candidate paths, including ones hidden behind other objects, and the traffic light state.
- depth: gives accurate distance and speed for the objects already visible in the camera.
- collision: tracks every unoccluded object around the car, in front and behind, and checks each candidate path for collisions.
- none: make no query, because the planner's pick is already right or no query would change it.
Answer with exactly one word: roi, depth, collision or none."""


def load_frames(frames, limit):
    rows = [json.loads(line) for line in open(os.path.join(frames, "frames.jsonl"))]
    seen, out = set(), []
    for r in rows:
        k = (r["family"], r["seed"], r["t_dec"])
        if k not in seen and os.path.exists(os.path.join(frames, r["path"])):
            seen.add(k)
            out.append(r)
    out.sort(key=lambda r: (r["family"], r["seed"], r["t_dec"]))
    return out[:limit] if limit else out


def messages(text):
    return [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": text}]}]


def embed(args, rows):
    import torch
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    proc = AutoProcessor.from_pretrained(args.model)
    proc.tokenizer.padding_side = "left"
    model = AutoModelForImageTextToText.from_pretrained(args.model, dtype=torch.bfloat16, device_map="cuda").eval()
    image_id = model.config.image_token_id
    text = proc.apply_chat_template(messages(EMBED_PROMPT), add_generation_prompt=True, tokenize=False, enable_thinking=False)
    mid, last, tok = [], [], []
    t0 = time.time()
    for i in range(0, len(rows), args.batch):
        batch = rows[i:i + args.batch]
        images = [Image.open(os.path.join(args.frames, r["path"])).convert("RGB") for r in batch]
        inputs = proc(images=images, text=[text] * len(batch), return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            hs = model(**inputs, output_hidden_states=True).hidden_states
        mask = (inputs["input_ids"] == image_id).unsqueeze(-1).to(hs[0].dtype)
        n = mask.sum(dim=1).clamp(min=1)
        mid.append(((hs[len(hs) // 2] * mask).sum(dim=1) / n).float().cpu().numpy().astype(np.float16))
        last.append(((hs[-1] * mask).sum(dim=1) / n).float().cpu().numpy().astype(np.float16))
        tok.append(hs[-1][:, -1].float().cpu().numpy().astype(np.float16))
        if i == 0:
            print(f"image tokens per frame {int(n[0])}, sequence {inputs['input_ids'].shape[1]}", flush=True)
        if (i // args.batch) % 20 == 0:
            print(f"{i + len(batch)}/{len(rows)} frames, {time.time() - t0:.0f}s", flush=True)
    np.savez(os.path.join(args.out, "embed.npz"), family=np.array([r["family"] for r in rows]), seed=np.array([r["seed"] for r in rows]),
             t_dec=np.array([r["t_dec"] for r in rows]), image_mid=np.concatenate(mid), image_last=np.concatenate(last), last_token=np.concatenate(tok),
             model=args.model, prompt=EMBED_PROMPT)
    print(f"embed done: {len(rows)} frames in {time.time() - t0:.0f}s", flush=True)


def vllm_chat(args, rows, texts, max_tokens):
    from PIL import Image
    from vllm import LLM, SamplingParams
    llm = LLM(model=args.model, max_model_len=4096, max_num_seqs=args.max_num_seqs, limit_mm_per_prompt={"image": 1, "video": 0},
              gpu_memory_utilization=0.85, seed=0, generation_config="vllm", enable_prefix_caching=False)
    params = SamplingParams(temperature=0.0, max_tokens=max_tokens, seed=0)
    convs = []
    for r, text in zip(rows, texts):
        img = Image.open(os.path.join(args.frames, r["path"])).convert("RGB")
        convs.append([{"role": "user", "content": [{"type": "image_pil", "image_pil": img}, {"type": "text", "text": text}]}])
    t0 = time.time()
    outs = llm.chat(convs, params, chat_template_kwargs=dict(enable_thinking=False))
    print(f"{len(rows)} frames generated in {time.time() - t0:.0f}s", flush=True)
    return [o.outputs[0].text.strip() for o in outs]


def describe(args, rows):
    texts = vllm_chat(args, rows, [DESCRIBE_PROMPT] * len(rows), 160)
    with open(os.path.join(args.out, "describe.jsonl"), "w") as f:
        for r, t in zip(rows, texts):
            f.write(json.dumps(dict(family=r["family"], seed=r["seed"], t_dec=r["t_dec"], text=t)) + "\n")


def prompt(args, rows):
    data = {(d["family"], d["seed"], d["t_dec"]): d for d in map(json.loads, open(os.path.join(args.data, f"{args.split}.jsonl")))}
    rows = [r for r in rows if (r["family"], r["seed"], r["t_dec"]) in data]
    texts = []
    for r in rows:
        d = data[r["family"], r["seed"], r["t_dec"]]
        texts.append(PROMPT_TEMPLATE.format(cands=", ".join(sorted(d["safe"])), top1=d["no_tool"]["top1"]))
    answers = vllm_chat(args, rows, texts, 8)
    with open(os.path.join(args.out, f"prompt_{args.split}.jsonl"), "w") as f:
        for r, a in zip(rows, answers):
            words = [w.strip(".,:;\"'*").lower() for w in a.split()]
            tool = next((w for w in words if w in TOOLS), None)
            f.write(json.dumps(dict(family=r["family"], seed=r["seed"], t_dec=r["t_dec"], tool=tool, raw=a)) + "\n")
    print(f"prompt done: {len(rows)} decisions", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=("embed", "describe", "prompt"))
    p.add_argument("--frames", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--data", default=None, help="dataset dir, for the prompt stage")
    p.add_argument("--split", default="val")
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--max-num-seqs", type=int, default=64)
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = load_frames(args.frames, args.limit)
    print(f"{len(rows)} frames", flush=True)
    dict(embed=embed, describe=describe, prompt=prompt)[args.stage](args, rows)


if __name__ == "__main__":
    main()
