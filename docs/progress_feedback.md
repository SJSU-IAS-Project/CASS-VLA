# Project progress and questions for feedback

**CMPE 249, Fall 2026. Team: Max Dokukin, Eshan Chawla.**
**Project:** PlanDiscrim (CASS-VLA): which single perception tool should a driving planner call?
**GitHub:** https://github.com/SJSU-IAS-Project/CASS-VLA
- branch `max`: benchmark and learned selector;
- branch `eshan/voi-selector`: VoI selector and on-device VLM study.

*Optional progress check-in (Canvas). Export to PDF before submitting.*

## 1. Where we are

We followed the scope in your proposal feedback:
- given a few candidate trajectories and an ambiguous scene, choose which single extra perception query (ROI, depth, collision, or none) is most useful;
- use MetaDrive oracle labels;
- compare against no tool, random, generic uncertainty and always-on.

| Part | Owner | Status |
|---|---|---|
| Scenario suite (6 hazard families), candidate generator, re-simulation oracle, 3 simulated tools at 3 noise levels, expected-gain labels | Max | Done |
| Contribution 1: learned candidate-conditioned selector with a signed-gain abstain rule | Max | Done; two pre-registered final tests on fresh seeds |
| Contribution 2: counterfactual value-of-information (VoI) selector, no learned model | Eshan | Done; one pre-registered final test on fresh seeds |
| VLM: Qwen3.5-9B image features (cluster A100), Qwen2.5-VL-3B on-device study (Mac, mlx) | Max / Eshan | Done |
| Slides (Dec 1/3), final report (LaTeX), README, 2-minute video | Both | Drafts started |

## 2. Preliminary results

All headline numbers are on scenario seeds that did not exist when each pre-registration was written, and each final was opened once. Accuracy means the ranker's pick equals the oracle-best candidate, averaged over call budgets of 0 to 1 calls per decision. Intervals are 95% seed-bootstrap.

**Contribution 1: learned selector** (seeds 1060-1159, 4,922 decisions).
- Mean accuracy at low / mid / high noise: 0.500 / 0.447 / 0.375, against 0.398 / 0.351 / 0.284 for the ranker-margin uncertainty trigger.
- At **0.6 calls per decision** (20% of always-on's 3 calls) it is non-inferior to always-on in accuracy (+0.006, +0.031, +0.066) and has a **lower unsafe rate** at every noise level (−0.013, −0.025, −0.034, all intervals below 0).
- This is our reading of your success criterion.

**Contribution 2: counterfactual VoI selector** (seeds 1160-1259, 4,557 decisions).
- **Method:** VoI simulates what each tool would reveal across world hypotheses built only from what the car sees (measurement noise, hidden pedestrians or vehicles behind occluders, unread lights), reruns the ranker, and calls the tool with the highest expected gain.
- **Result: negative.** VoI scores 0.397 / 0.345 / 0.288: 0.08-0.10 below the learned selector, and level with the ranker margin. It only beats the margin when calls are scarce (0.1-0.3 calls per decision).
- **Diagnosis:**
  - VoI optimises the ranker's own utility, but the ranker agrees with the oracle on only 24% of decisions, so the world model inherits that error;
  - its per-tool correlation with the true gain is 0.08-0.22;
  - 13% of its calls are harmful, against 1.5% for the learned selector.

**On-device VLM** (Qwen2.5-VL-3B, 4-bit, MacBook).
- Asked to choose the tool, it answered `none` on all 1,018 frames. We traced this to four causes:
  - template copying;
  - perceiving a pedestrian but not using it in the answer;
  - no ability to reason about the tools;
  - a float16 overflow bug, now fixed.
- Scored by token probability, it reads traffic lights well (AUROC 0.97 within the light family), but "is something hidden?" is near chance (0.58).
- Using it as VoI's prior did not help.
- The 9B image features did help the learned selector (+0.010 to +0.016).

## 3. Blockers and caveats

- **No closed-loop evaluation yet.** Our "safety" is the oracle's unsafe label on the chosen candidate, not a collision rate.
- **The 0.6 budget** in the learned selector's non-inferiority test was chosen after seeing an earlier final split. The later final is fresh, but the budget value is post hoc.
- **Reproduction gap.** Contribution 2 regenerated the data on a second machine. Split sizes match exactly, but the learned selector reads 0.010-0.016 lower there, probably a code-version difference. Both contributions are internally consistent, but their numbers come from two data builds and two fresh seed sets.
- **Simulated tools** (ground truth plus an assumed noise model), one simulator and six scripted families.

## 4. Questions for you

1. **Negative result as a contribution.** Contribution 2 (counterfactual VoI) is a clean, pre-registered negative result with a root-cause diagnosis and ablations. Is that acceptable as one of the two main contributions, or would you rather we present it as a baseline next to the learned selector?
2. **Closed loop.** How important is a closed-loop check (collision rate when the chosen candidate is actually driven) for the final grade, compared with the open-loop decision-quality results we have? We can run a small sample at about 0.6 calls per decision against always-on if you think it is needed.
3. **"Safety decisions."** Is "non-inferior accuracy and a lower oracle-unsafe rate at 20% of the calls" a fair reading of "similar or better safety decisions with substantially fewer perception/VLA calls"? Or should we report something else, such as unsafe rate at a matched budget across all methods?
4. **VLA requirement.** Our VLA usage is offline: cached image features from a 9B VLM, and an on-device 3B VLM study, as your feedback allowed. Is that enough on the VLA side, or do you expect a VLA call inside the decision loop?
5. **Two data builds.** For the report, should we rerun the learned selector on the second machine's data and fresh seeds (already done, and the ordering holds), or keep each contribution on its own pre-registered final and explain the difference?
6. **Report format.** Is a pre-registered-hypothesis table acceptable in the experiments section, or do you prefer conventional results tables only?

## 5. Next steps (to Dec 15)

- Slides for Dec 1/3 (`docs/final_presentation_slides.md`).
- Final report in the IEEE LaTeX template, vector figures only (`docs/final_report_draft.md`).
- README with the reproduction chain, `CONTRIBUTIONS.md`, and the 2-minute demo video.
- Depending on your answers: a small closed-loop check, and VLM controls.
