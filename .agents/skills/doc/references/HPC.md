# SJSU HPC

CASS-VLA runs on the cluster as course work for CMPE 249 (Fall 2026), apart from the master's research in
`~/sjsu-hpc`. Connecting, the VPN rules and Slurm limits are in `~/sjsu-hpc/.agents/skills/doc/references/`.
Resource terms agreed with the `ctxeval` side are in
`~/sjsu-hpc/communication/resources_sharing/CASS_VLA_RESOURCES_response_2026-11-06-14-28.md`.

## Where things are

`D=/data/cmpe249-fa26/students/017025164`. Write only there (course rule). Never write in `/data/cmpe295-suresh`
or `~/sjsu_hpc` on the cluster.

| Path | What |
|---|---|
| `$D/CASS-VLA` | code, copied with rsync, without `.venv`, `out` or `.git` |
| `$D/venv` | Python 3.11.18 virtualenv with the packages pinned in `$D/wheels/lock.txt` |
| `$D/python` | the uv-managed CPython that the venv uses |
| `$D/tools/uv` | uv 0.13.7, copied from the research container |
| `$D/assets/metadrive` | MetaDrive assets; `venv/.../site-packages/metadrive/assets` links here, because compute nodes are offline |
| `$D/wheels` | the MetaDrive wheel built from commit 85e5dad, and the lock file |

## Building the venv

- hpc1 has git 1.8.3, too old for uv's git dependencies. Build the MetaDrive wheel on the research container
  with `uv build --wheel` from a shallow fetch of the pinned commit, then copy it.
- hpc1 has glibc 2.17 and the compute nodes glibc 2.34. Install on hpc1 with
  `uv pip install --python-platform x86_64-manylinux_2_34`, and set `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR`
  under `$D`, so nothing lands in the full `/home`.
- The venv does not import on hpc1. Check it on g17 with imports only, because heavy work never runs there.
- `uv python install` adds `~/.local/bin/python3.11` on the cluster home; remove it. The `python3.12` link
  there belongs to the master's tools.
- matplotlib writes a font cache to `~/.cache/matplotlib`. Set `MPLCONFIGDIR=$D/cache/mpl` in jobs.

## Rendering

- Compute nodes have no Xvfb. Without DISPLAY, Panda3D falls back to headless EGL with Mesa llvmpipe, which cannot
  create MetaDrive's 16x multisample buffers. Pass `--max-msaa 4` to `scripts/render_frames.py`. The frames are
  pixel-identical to Xvfb frames on the research container (9-frame check, 2026-11-06).
- One worker peaks at 5.5 GB. `scripts/hpc/render.sbatch` runs 16 workers in 100 GB on `cpuqs` and renders about
  230-260 frames per minute.

## Jobs

- Job scripts are in `scripts/hpc/`; copies live in `$D/jobs/`. Submit from g17 with full paths, because a `$VAR`
  inside the hpc1-to-g17 ssh string expands on hpc1.
- `scripts/hpc/vlm.sbatch` runs `scripts/vlm_encode.py` in the ctxeval vLLM image on one A100, with the image and the
  Qwen3.5-9B snapshot bound read-only from `/data/cmpe295-suresh`. Log every GPU job in
  `~/sjsu-hpc/communication/resources_sharing/CASS_VLA_GPU_JOBS.md`, and keep at most one queued or running.
- Smoke test 107999 (64 frames): embed 6 frames/s, describe and prompt about 20 frames/s, plus about 2 min per
  vLLM start-up.
