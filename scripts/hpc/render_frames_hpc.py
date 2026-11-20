"""Render one front-camera frame per decision in a dataset split, for the offline VLA pass (Phase 5).

Cluster renderer (Xvfb or headless EGL, many processes), used by scripts/hpc/*.sbatch. On a Mac, use
scripts/render_frames.py, which feeds the on-device mlx VLM cache (scripts/cache_vlm.py).

    DISPLAY=:99 python scripts/hpc/render_frames_hpc.py --data out/v2_final_ds --split final --out out/frames --procs 4

Needs an X server such as ``Xvfb :99``. Without one, Panda3D falls back to headless EGL, which accepts at most
4x multisampling, so pass ``--max-msaa 4`` there. Each worker replays the decision's prefix with every graphics output
switched off, then renders a single frame. Frames are PNG files in normal RGB colour order, at
<out>/<family>/<seed>_<t_dec>.png. <out>/frames.jsonl lists each frame with the ego position error against the
label record. A frame whose ego position is more than 5 cm from the record is replayed on its own, and dropped
if it still disagrees. Existing frames are skipped, so a rerun resumes.
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, ROOT)
W, H = 640, 360
MAX_EGO_ERR = 0.05


def render_chunk(task):
    family, seeds, items, out, max_msaa = task
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    if max_msaa is not None:
        from direct.filter.FilterManager import FilterManager
        scene_into = FilterManager.render_scene_into

        # MetaDrive asks for 16x multisampling in its post-processing buffers, which headless EGL cannot create
        def capped(self, *a, fbprops=None, **k):
            if fbprops is not None and fbprops.get_multisamples() > max_msaa:
                fbprops.set_multisamples(max_msaa)
            return scene_into(self, *a, fbprops=fbprops, **k)
        FilterManager.render_scene_into = capped
    import cv2
    import numpy as np
    from metadrive import constants
    from metadrive.component.sensors.rgb_camera import RGBCamera
    from cassvla.planning import Oracle
    from cassvla.planning.candidates import cruise_candidate
    from cassvla.planning.control import Tracker
    o = Oracle(family, start_seed=min(seeds), num_scenarios=max(seeds) - min(seeds) + 1, image_observation=True,
               sensors=dict(rgb_camera=(RGBCamera, W, H)), vehicle_config=dict(image_source="rgb_camera"), norm_pixel=False)
    env = o.env
    env.reset(seed=min(seeds))
    # the image observation would render every step; frames are taken by hand below instead
    for obs in env.observations.values():
        type(obs).observe = lambda self, *a, **k: None
    outputs = list(env.engine.graphicsEngine.getWindows())
    cam = env.engine.get_sensor("rgb_camera")

    def active(flag):
        for w in outputs:
            w.setActive(flag)

    def capture(seed, t_dec, ego_xy, path, n_frames):
        t0 = time.time()
        active(True)
        cam.track(env.agent.origin, constants.DEFAULT_SENSOR_OFFSET, constants.DEFAULT_SENSOR_HPR)
        env.engine.taskMgr.step()
        img = cam.get_rgb_array_cpu()
        active(False)
        err = float(np.linalg.norm(np.asarray(env.agent.position[:2]) - np.asarray(ego_xy[:2])))
        if err > MAX_EGO_ERR:
            return None
        cv2.imwrite(path + ".tmp.png", img)
        os.replace(path + ".tmp.png", path)
        row = dict(family=family, seed=seed, t_dec=t_dec, path=os.path.relpath(path, out), ego_err=round(err, 3),
                   render_s=round(time.time() - t0, 2), replays_for_seed=n_frames)
        with open(os.path.join(out, "frames.jsonl"), "a") as log:
            log.write(json.dumps(row) + "\n")
        return row

    by_seed = collections.defaultdict(list)
    for seed, t_dec, ego_xy in items:
        path = os.path.join(out, family, f"{seed}_{t_dec:.1f}.png")
        if not os.path.exists(path):
            by_seed[seed].append((t_dec, ego_xy, path))
    rows = []
    try:
        for seed, todo in sorted(by_seed.items()):
            # one replay to the last decision of the seed, capturing each earlier decision on the way
            todo.sort()
            active(False)
            env.reset(seed=seed)
            tracker = Tracker(cruise_candidate(env, o.cruise, todo[-1][0] + 1.0), env.agent)
            missed, step = [], 0
            for t_dec, ego_xy, path in todo:
                while step < int(round(t_dec / 0.1)):
                    env.step(tracker.act(env.agent))
                    step += 1
                row = capture(seed, t_dec, ego_xy, path, 1)
                (rows.append(row) if row else missed.append((t_dec, ego_xy, path)))
            for t_dec, ego_xy, path in missed:
                active(False)
                o._prefix(seed, t_dec)
                row = capture(seed, t_dec, ego_xy, path, 2)
                if row:
                    rows.append(row)
    finally:
        o.close()
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--split", required=True)
    p.add_argument("--sweep", default=None, help="sweep dir with the raw records; default from the dataset manifest")
    p.add_argument("--out", required=True)
    p.add_argument("--procs", type=int, default=4)
    p.add_argument("--seeds-per-task", type=int, default=5)
    p.add_argument("--max-msaa", type=int, default=None, help="cap multisampling; use 4 under headless EGL")
    args = p.parse_args()
    with open(os.path.join(args.data, f"{args.split}.jsonl")) as f:
        keys = {(r["family"], r["seed"], r["t_dec"]) for r in map(json.loads, f)}
    sweep = args.sweep or json.load(open(os.path.join(args.data, "manifest.json")))["sweep"]
    ego = {}
    for name in os.listdir(sweep):
        if name.endswith(".jsonl"):
            for line in open(os.path.join(sweep, name)):
                r = json.loads(line)
                k = (r["family"], r["seed"], r["t_dec"])
                if k in keys:
                    ego[k] = r["ego"]["position"]
    by = collections.defaultdict(list)
    for fam, seed, t in sorted(keys):
        by[fam, seed].append((seed, t, ego[fam, seed, t]))
    tasks, groups = [], collections.defaultdict(list)
    for (fam, seed), items in sorted(by.items()):
        groups[fam].append((seed, items))
    for fam, lst in groups.items():
        os.makedirs(os.path.join(args.out, fam), exist_ok=True)
        for i in range(0, len(lst), args.seeds_per_task):
            part = lst[i:i + args.seeds_per_task]
            tasks.append((fam, [s for s, _ in part], [it for _, its in part for it in its], args.out, args.max_msaa))
    print(f"{len(keys)} frames in {len(tasks)} tasks, {args.procs} processes", flush=True)
    t0 = time.time()
    done = 0
    with mp.get_context("spawn").Pool(args.procs) as pool:
        for rows in pool.imap_unordered(render_chunk, tasks):
            done += len(rows)
            worst = max((r["ego_err"] for r in rows), default=0.0)
            print(f"{done} frames, {time.time() - t0:.0f}s, worst ego error in task {worst:.3f} m", flush=True)


if __name__ == "__main__":
    main()
