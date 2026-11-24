# Project progress report and questions for feedback

**CMPE 249, Fall 2026. Team: Max Dokukin, Eshan Chawla.**

**Project:** PlanDiscrim (CASS-VLA): which single perception tool should a driving planner call?

**GitHub:** https://github.com/SJSU-IAS-Project/CASS-VLA (branch `main` holds both contributions; pull request #2 merged on Nov 23, 2026)

**Date:** November 23, 2026 (progress report, submitted on Canvas as PDF)

## 1. Where we are

We followed the scope in your proposal feedback:
- given a few candidate trajectories and an ambiguous scene, choose which single extra perception query (ROI, depth, collision, or none) is most useful;
- use MetaDrive oracle labels;
- compare against no tool, random, generic uncertainty and always-on.

All planned experiments are finished. What remains is writing, the talk and the optional checks in Section 5.

| Part | Owner | Status |
|---|---|---|
| Scenario suite (6 hazard families), candidate generator, re-simulation oracle, 3 simulated tools at 3 noise levels, expected-gain labels | Max | Done |
| Contribution 1: learned candidate-conditioned selector with a signed-gain abstain rule | Max | Done; two pre-registered final tests on fresh seeds |
| Contribution 2: counterfactual value-of-information (VoI) selector, no learned model | Eshan | Done; one pre-registered final test on fresh seeds, ablations, diagnosis |
| VLM: Qwen3.5-9B image features (cluster A100); Qwen2.5-VL-3B on-device study (Mac, mlx) | Max / Eshan | Done, including the VoI + VLM prior run on the final seeds |
| Final slides (Dec 1/3) | Both | Joint deck built (`docs/final/deck/`); trimming to 10 minutes |
| Final report (IEEE LaTeX, due Dec 15) | Both | Joint draft built (`docs/final/report/`); LaTeX port next |
| README, contributions file, 2-minute video | Both | Not started |

## 2. Results

All headline numbers come from scenario seeds that did not exist when each pre-registration was written. Each final test was run once. Accuracy means the ranker's pick equals the oracle-best candidate, averaged over call budgets of 0 to 1 calls per decision. Intervals are 95% seed-bootstrap.

**Contribution 1: learned selector** (seeds 1060-1159, 4,922 decisions).
- Mean accuracy at low / mid / high noise: 0.500 / 0.447 / 0.375, against 0.398 / 0.351 / 0.284 for the ranker-margin uncertainty trigger. All four pre-registered hypotheses passed.
- At **0.6 calls per decision** (20% of always-on's 3 calls) it is non-inferior to always-on in accuracy (+0.006, +0.031, +0.066) and has a **lower unsafe rate** at every noise level (−0.013, −0.025, −0.034, all intervals below 0).
- This is our reading of your success criterion.

**Contribution 2: counterfactual VoI selector** (seeds 1160-1259, 4,557 decisions).
- **Method.** For each tool, VoI simulates what the tool would reveal across hypothetical worlds built only from what the car sees: measurement noise, a pedestrian or vehicle behind an occluder, an unread light, a car behind. It then reruns the ranker and calls the tool with the highest expected gain, if that gain is above 0.
- **Result: negative.**
  - VoI scores 0.397 / 0.345 / 0.288: 0.076 to 0.098 below the learned selector, and level with the ranker margin.
  - It beats the margin only when calls are scarce: at 0.1 calls per decision, 0.270 / 0.259 / 0.247 against 0.239 / 0.225 / 0.213.
  - All three pre-registered hypotheses (V1-V3) failed.
- **Diagnosis.**
  - VoI optimises the ranker's own utility, but the ranker agrees with the oracle on only 24% of decisions, so the world model inherits that error.
  - Its per-tool correlation with the true gain is 0.08-0.22.
  - At 0.3 calls per decision, 12.2% of its calls are harmful at mid noise, against 2.4% for the learned selector.
  - When some tool helps, it picks the best tool 38% of the time, against 50% for the learned selector.

**On-device VLM** (Qwen2.5-VL-3B, 4-bit, MacBook).
- Asked to choose the tool, it answered `none` on all 1,018 frames. We traced this to four causes:
  - template copying;
  - perceiving a pedestrian but not using it in the answer;
  - no ability to reason about the tools;
  - a float16 overflow bug, now fixed (11 NaN frames reduced to 0).
- Scored by token probability on the final frames:
  - it reads traffic lights well: red-light AUROC 0.999, and 0.97 within the light family;
  - "is a road user hidden?" is at chance (0.51).
- Using it as VoI's occlusion prior did not help: −0.006 / −0.007 / +0.001 on the final seeds. This is an exploratory run made after the confirmatory test.
- The 9B image features did help the learned selector (+0.010 to +0.016, a pre-registered secondary hypothesis that passed).

## 3. Blockers and caveats

- **No closed-loop evaluation yet.** Our "safety" is the oracle's unsafe label on the chosen candidate, not a collision rate.
- **The 0.6 budget** in the learned selector's non-inferiority test was chosen after seeing an earlier final split. The later final is fresh, but the budget value is post hoc.
- **Reproduction gap.**
  - Contribution 2 regenerated the data on a second machine, and the split sizes match exactly.
  - The learned selector reads 0.010-0.016 lower there, probably because of a code change made alongside the first data build.
  - Both contributions are internally consistent, but their numbers come from two data builds and two fresh seed sets.
- **Simulated tools.** The tools are ground truth plus an assumed noise model, in one simulator with six scripted families.
- **Shared tool-merge simplification.** Actors with the same name (the three cones in `lane_blockage`) are merged into one. This affects the labels of both selectors equally.

## 4. Questions for you

1. **Negative result as a contribution.** Contribution 2 (counterfactual VoI) is a pre-registered negative result with a root-cause diagnosis and ablations. Is that acceptable as one of the two main contributions, or would you rather we present it as a baseline next to the learned selector?
2. **Closed loop.** How important is a closed-loop check (collision rate when the chosen candidate is actually driven) for the final grade, compared with our open-loop decision-quality results? We can run a small sample at about 0.6 calls per decision against always-on, on new seeds (1260 and up).
3. **"Safety decisions."** Is "non-inferior accuracy and a lower oracle-unsafe rate at 20% of the calls" a fair reading of "similar or better safety decisions with substantially fewer perception/VLA calls"? Or should we report something else, such as unsafe rate at a matched budget across all methods?
4. **VLA requirement.** Our VLA usage is offline (cached image features from a 9B VLM) plus an on-device 3B VLM study, as your feedback allowed. Is that enough on the VLA side, or do you expect a VLA call inside the decision loop?
5. **Two data builds.** Should the report keep each contribution on its own pre-registered final and explain the difference? Or should we also report the learned selector on the second build? We already did that rerun, and the ordering holds (0.495 / 0.435 / 0.364 against 0.397 / 0.345 / 0.288 for VoI).
6. **Report format.** Is a pre-registered-hypothesis table acceptable in the experiments section, or do you prefer conventional results tables only?

## 5. Next steps (to Dec 15)

- **Talk (Dec 1/3).** Trim the joint deck (`docs/final/deck/joint_deck.pdf`) to 10 minutes, rehearse, and upload to Canvas.
- **Report.** Port the joint draft (`docs/final/report/report.pdf`) to the IEEE LaTeX template, with vector figures only.
- **Repository.** Write the README with the reproduction chain and `CONTRIBUTIONS.md`, and record the 2-minute demo video.
- **Depending on your answers.** A small closed-loop check, VLM shuffle and family controls on the learned selector, and VoI's score as an input feature to the learned selector.
