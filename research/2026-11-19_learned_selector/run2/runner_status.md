# Runner status
- 2026-11-19 22:45:37 job1 sweep v4_final started (12 procs)
- 2026-11-20 01:32:05 job1 sweep done: 120 chunks, 7346 decisions, 4922 retained, exit ok
- 2026-11-20 01:32:05 job2 started: build_dataset(6), label_expected_gain(6), flip_features(4)
- 2026-11-20 01:37:00 job2 done, all exit ok. rows: dataset final.jsonl 4922, expgain 4922, flip 4923 (incl. header = 4922 rows). Expected 4922 retained. Nothing evaluated, no labels inspected.
- 2026-11-20 01:51:19 geometry final started (final.py, 5 methods)
- 2026-11-20 01:55:13 geometry final done, exit ok. n_train 34718, n_test(final) 4922. Output /home/user/CASS-VLA/out/v4_eval/final_geom.json. Hypotheses: P1 pass, P2 pass, P3 pass, Q1 not run, P4 pass.
- 2026-11-20 02:35:57 Q1 final (signed, signed_vlm) started
- 2026-11-20 02:39:53 Q1 final done, exit ok. n_train 34718, n_test 4922. Q1 pass: diffs low +0.0163 [0.0129,0.0196], mid +0.0115 [0.0084,0.0149], high +0.0099 [0.0073,0.0125]. Output out/v4_eval/final_vlm.json
