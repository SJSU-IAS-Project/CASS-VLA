# Status of V4 (VoI + VLM prior) on the final seeds

The final evaluation (`FINAL.md`, `out/voi_eval/final.json`) was run on 2026-11-20 as soon as the final data for
seeds 1160-1259 were ready. At that time the VLM yes/no answers for the final frames did not exist (rendering and
the yes/no pass were several hours away on this Mac). PREREG3 runs V4 only when every final decision has a yes/no
answer, so V4 is "not run" in the confirmatory result.

Any later `voi_vlm` run on seeds 1160-1259 is an exploratory addendum, not a confirmatory test. Its settings are the
ones already written in PREREG3 and `FROZEN.json` (occl_static = occl_ped = P(hidden) / 2 on top of the fitted
priors). V1-V3 cannot change: the VoI scores and the harness are deterministic.
