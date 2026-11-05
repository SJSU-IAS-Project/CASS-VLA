Updated 2026-11-05 10:30:46 UTC by xewe_handoff write. Read and written only by the xewe_handoff skill (R-14).

# HANDOFF

Head node of the handoff directory. It points at the newest entry and states the directory's
status. It holds no session content; that lives in the entry files.

## Head

- **HEAD:** handoffs/2026-11-05-10-30-46.md
- **HEAD timestamp:** 2026-11-05 10:30:46 UTC
- **Entries:** 2
- **Last writer:** xewe_handoff write — Claude Code, Opus 5.5
- **Resume:** claude --resume 14d0e54d-be2c-4176-989d-069698752c83
- **Integrity:** consistent — HEAD is the newest entry file; entry count equals file count; every index row exists on disk. Validated at last write.
- **Status:** closed — resume with the read procedure of xewe_handoff.

## Index (newest first)

- **2026-11-05-10-30-46** — Built the environment, fixed the hazards, built tools and labels, ran the first PlanDiscrim baseline — partial — next: Review `docs/baseline_results.md`, then commit the work with the commands printed at the end of the session.
- **2026-11-05-07-02-22** — Moved work off the Mac, baselined on Linux, found hazard sign bugs, planned an overnight run — partial — next: Run `./scripts/setup.sh` on the container that holds the repo, then confirm that the tests pass.

## Template

- `handoffs/yyyy-mm-dd-hh-mm-ss.md` — blank entry; copy it, never edit it.
