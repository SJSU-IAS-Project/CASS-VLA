---
name: doc
description: >
  What an agent needs to know about CASS-VLA that the code does not show. Covers which seed
  ranges are already used for tuning, validation and held-out tests; running sweeps,
  evaluation and frame rendering on this 8 GB CPU machine (thread variables, memory per camera
  worker, Xvfb, stopping process pools safely); the SJSU HPC setup (course directory, venv build,
  offline assets, agreed GPU terms); and the decisions log for windows, speeds and
  tool variants. Use before choosing seeds, launching a sweep or render, touching the cluster, or changing scenario
  speeds, windows or tool models.
---

# doc

This is the index of the project's agent knowledge. Open only the file whose row matches the
task. Each row names one file under `references/`, and every file there has a row.

| File | Read it when |
|---|---|
| `references/SEEDS.md` | choosing seeds for a sweep, a tuning run or an evaluation |
| `references/RUNNING.md` | launching a sweep, an evaluation or frame rendering, or stopping one |
| `references/HPC.md` | touching the SJSU cluster: paths, the venv, jobs |
| `references/DECISIONS.md` | changing anything a past decision covers |
