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

## Status on 2026-11-06

The venv imports on g17. g17 has no Xvfb but has the NVIDIA EGL library. Whether compute nodes have Xvfb is
unknown, and finding out needs a short `cpuqs` job. No job has been submitted.
