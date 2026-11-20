# Runner status
- 18:03 job1 v3_final sweep resumed (10 procs, 105 chunks left), log out/v3_final.log
- 18:05 job2 VLM controls chain (shuffle, shuffle_family, family sequential), /tmp/vlm_chain.log
- 18:09 VLM control eval peaked at 3.7 GB RSS (not 1.2 GB) next to the sweep; killed at 1.5 GB available. Deferred until sweep ends.
- 18:10 job3 flip chain started (v2_sweep, v2_extra, v3_extra; 4 procs), /tmp/flip_chain.log
- 18:17 flip v2_sweep done exit 0 (out/v3_flip/v2_sweep.jsonl). v2_extra, v3_extra running.
- 18:19 sweep at 19/105 chunks, ~532 s per chunk under load (ETA ~19:25). Available mem >=2.9 GB.
- 18:33 flip jobs all done exit 0 (rows: see wc below). 18:34 job4 v3_extra label+dataset chain started (/tmp/lab_chain.log)
  14708 out/v3_flip/v2_extra.jsonl
  14787 out/v3_flip/v2_sweep.jsonl
   9683 out/v3_flip/v3_extra.jsonl
  39178 total
- 20:32 (manager resumed) v3_final ds, expgain, flip started in parallel
- 20:36 v3_final ds/expgain/flip done: 4903/4903/4904 rows. Final run launched (3 eval_triggers levels + s4_signed).
- 20:41 final run done, merged to out/v3_eval/triggers_final.json: {final: H1 true, H2 true, S1 false}; n_train 34718. s4_signed done. Next: VLM controls one at a time.
- 20:41 VLM control chain started (sequential, waits for >4.5 GB avail), results in /tmp/vlm_chain2.log
