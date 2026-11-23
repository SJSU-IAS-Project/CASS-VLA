# Status of V4 (VoI + VLM prior) on the final seeds

The final evaluation (`FINAL.md`, `out/voi_eval/final.json`) was run on 2026-11-20 as soon as the final data for
seeds 1160-1259 were ready. At that time the VLM yes/no answers for the final frames did not exist (rendering and
the yes/no pass were several hours away on this Mac). PREREG3 runs V4 only when every final decision has a yes/no
answer, so V4 is "not run" in the confirmatory result.

Any later `voi_vlm` run on seeds 1160-1259 is an exploratory addendum, not a confirmatory test. Its settings are the
ones already written in PREREG3 and `FROZEN.json` (occl_static = occl_ped = P(hidden) / 2 on top of the fitted
priors). V1-V3 cannot change: the VoI scores and the harness are deterministic.

## Exploratory addendum (run 2026-11-23)

The yes/no pass on all 4,557 final frames finished, and `voi_vlm` was scored with the PREREG3 / `FROZEN.json` settings
(`out/voi_eval/final_v4_addendum.json`, `out/vlm_yesno/eval_final.json`). VoI + VLM prior minus VoI, mean accuracy over
budgets 0-1 [95% seed-bootstrap CI]:

| Low | Mid | High |
|---|---|---|
| −0.0061 [−0.0104, −0.0022] | −0.0070 [−0.0105, −0.0036] | +0.0009 [−0.0030, +0.0046] |

The VLM prior does not help; at low and mid noise it hurts slightly. Final-frame detector AUROC: red light 0.999 (0.97
within `ambiguous_light`), pedestrian 0.862, hidden road user 0.513 [0.474, 0.553]. This is exploratory and does not
change the confirmatory result (V1-V3 fail, V4 not run).
