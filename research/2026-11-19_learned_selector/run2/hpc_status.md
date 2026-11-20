# HPC status
- 22:50 rsync done: code to $D/CASS-VLA (no .venv/out/.git/research/.agents); out/v3_extra (241 files) and out/v3_extra_ds (train.jsonl 9,682 rows) to $D/CASS-VLA/out; job scripts copied to $D/jobs.
- 22:52 submitted render job 158982 (cpuqs, 1:15:00): out/v3_extra_ds:train -> out/frames_v3 (9,682 frames, expect ~42 min).
- 2026-11-20 01:32 job 158982 COMPLETED (ran 32:35, exit 0): out/frames_v3/frames.jsonl 9,682 rows = v3_extra_ds train rows. Waiting for out/v4_final_ds (not present yet) and runner_status 'dataset done'.
- 2026-11-20 01:40 out/v4_final (121 files) and out/v4_final_ds (final.jsonl 4,922 rows) rsynced (build_dataset done; expgain/flip still running locally, not needed for render). Submitted second render job (see next line).
- 01:37 submitted render job 159757 (cpuqs, 45 min): out/v4_final_ds:final -> out/frames_v3 (4,922 frames; expect total 14,604).
- 01:57 job 159757 COMPLETED (20:11, exit 0): out/frames_v3/frames.jsonl 14,604 rows (9,682 + 4,922). 
- 01:58 submitted GPU job 159857 (gpuqs a100:1, 1:30:00): vlm.sbatch out/frames_v3 -> out/vlm_v3, LIMIT 0, embed+describe. Logged in CASS_VLA_GPU_JOBS.md.
- 02:29 GPU job 159857 COMPLETED (32 min, exit 0, cs001): embed 14,604 frames, describe 14,604 lines. Pulled to out/vlm_v3 (embed.npz 360 MB, describe.jsonl). Local check: embed.npz family/seed/t_dec (14604,), image_mid/image_last/last_token (14604,4096) f16 = frames.jsonl 14,604. GPU jobs row updated. Frames stay on cluster only.
