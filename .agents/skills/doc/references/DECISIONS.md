# Decisions

Each line records one decision that a later change could undo by accident. Write it as a date,
the decision, and the reason, with the newest line last.

2026-11-05 Windows come from a fixed rule on tuning seeds (smallest 0.5 s span holding 95% of retained decisions) and are never changed after validation, because hand-picked windows inflate retained rates.
2026-11-06 Family speed and acceleration ranges were scaled by 0.8 when the substep fix landed, so vehicles drive as fast as in the validated scenarios. Unscaled, the lead in `lead_brake_cutin` is as fast as the ego and no hazard happens.
2026-11-06 The MLP selector settings (32 hidden units, 300 Adam steps, lr 0.01, l2 1e-3) were fixed before evaluation. Tuning them now would need fresh test seeds.
2026-11-06 Train selectors on expected-gain targets from `scripts/label_expected_gain.py` (mean over 8 noise draws), and compare against the fair ceiling, not the noise-seeing oracle selector. A pre-registered check beat single-draw targets in all 6 val/test cells, and the oracle's lead is mostly noise luck that no selector can foresee.
2026-11-06 Phase 5 VLM features are the PCA-32 of the middle-layer image-token mean from Qwen3.5-9B. They were chosen before evaluation and are not tuned on val or test; tuning them needs fresh seeds.
2026-11-07 Seeds 760-859 (`out/v3_final`) are reserved for one pre-registered run, with the rules in `research/2026-11-19_learned_selector/PREREG.md`, so nobody opens its labels to choose methods.
2026-11-19 The `knowno` trigger is degenerate here, because only the top-two margin is stored: its calibrated threshold calls 99.7 to 100% of decisions. Report it as degenerate, not as a budgeted baseline.
2026-11-19 The pre-registered final test on seeds 760-859 passed H1 and H2, so those seeds are now used up. The signed-gain abstain selector (S4, `signed_mse_abstain`) is the candidate for the next pre-registered test, which needs fresh seeds from 1060, because its method was chosen on val and test.
2026-11-20 The signed-gain abstain selector (`signed_mse_abstain`, with the VLM features when frames exist) is now the main method, because the second pre-registered test on seeds 1060-1159 passed P1 to P4 and Q1. The frozen selector stays as the baseline, and any new method needs fresh seeds from 1160.
