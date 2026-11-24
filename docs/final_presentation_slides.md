# Final presentation: slide draft

**Talk:** 10 minutes, in class Dec 1 or Dec 3, 2026. Upload the slides (.pptx or .pdf) to Canvas by Dec 3 (closes Dec 10).
**Team:** Max Dokukin, Eshan Chawla.
**Rubric (10 pts):** clear and easy to follow (5), project progress (5: ahead of schedule).
**Course guidance:** tell one visual story, keep text light, and give negative results room.

**Section owners (agreed):**

| Section | Owner | Slides | Time |
|---|---|---|---|
| 1. Intro: the problem | Max | 1-2 | 1:15 |
| 2. Background: setup, landscape, baselines | Eshan | 3-4 | 1:30 |
| 3. Contribution 1: learned selector | Max | 5-7 | 2:30 |
| 4. Contribution 2: counterfactual value-of-information selector | Eshan | 8-11 | 2:45 |
| 5. Limitations | Max | 12 | 0:45 |
| 6. Conclusion | Eshan | 13 | 0:45 |
| Buffer and questions | | | 0:30 |

**Number sources.**
- Max's numbers come from `research/2026-11-19_learned_selector/deliverables/report/report.md` (second final: seeds 1060-1159).
- Eshan's numbers come from `docs/voi_selector.md`, `docs/vlm_failure_analysis.md` and `research/2026-11-20_voi_selector/FINAL.md` (seeds 1160-1259).
- Before the talk, recheck every number against those files; do not edit numbers on the slides by hand.

**Figure sources.**
- Max: `research/2026-11-19_learned_selector/deliverables/figures/`.
- Eshan: `paper/figures/` (vector PDFs).
- His existing deck is in `research/2026-11-19_learned_selector/deliverables/deck/`; reuse its pipeline figure and style for consistency.

---

## 1. Intro (Max)

### Slide 1: Title

- **Title:** *Which perception tool should a driving planner call? Learned vs. counterfactual tool selection*
- Max Dokukin, Eshan Chawla. CMPE 249, Fall 2026.
- GitHub: https://github.com/SJSU-IAS-Project/CASS-VLA
- **Visual:** one front-camera frame from `occluded_pedestrian`: a parked car with a pedestrian half hidden behind it.

> **Speaker notes:** "A planner has several candidate maneuvers. Before it commits, it can afford one extra look. Which look?"

### Slide 2: The problem

- The planner proposes up to 6 candidate maneuvers over 5 s (keep, speed up, slow down, stop, change left or right).
- It may call **one** perception tool before choosing, or none:
  - **ROI** inspection (can see hidden objects and the light),
  - **depth** (precise range and speed),
  - **collision** check (tracked objects, front and rear).
- Calling every tool every step is expensive, and a noisy extra reading can also *flip a correct choice to a wrong one*.
- **Goal set by the instructor:** similar or better safety decisions with **substantially fewer** perception calls than always-on.
- **Visual:** a three-box diagram: candidates → selector (which tool?) → ranker picks one.

> **Speaker notes:** Mention the scope cut from the proposal feedback: one question, three tools, oracle labels, five baselines.

---

## 2. Background (Eshan)

### Slide 3: Setup: scenarios, oracle, metric

- **MetaDrive, 6 hazard families:** occluded pedestrian, occluded cross traffic, ambiguous light, lead brake or cut-in, lane blockage, merge closing speed.
- **Oracle:** re-simulates every candidate against the true actors and labels the best one, `c*`, plus a safe or unsafe flag.
- **Tools** are simulated at 3 noise levels (low / mid / high).
- **Metric:**
  - top-1 accuracy (did the ranker pick `c*`?) averaged over call budgets of 0 to 1 calls per decision;
  - unsafe rate of the chosen maneuver.
- **Data:** 14,786 decisions on seeds 100-399, plus extra training seeds. Fresh, never-seen seeds are used for each final test.
- **Visual:** Max's pipeline figure `f0_pipeline.svg`, plus one small table of the 6 families.

### Slide 4: Landscape and baselines

- **Prior work:**
  - plan-aware compute allocation exists (SIGMA, DEEP, Best-of-Evidence);
  - DriveAgent-R1 learns *when* to use tools from the image, but never sees the candidate trajectories;
  - an off-road robot paper (2611.06702) rescores rollouts under map hypotheses, rule-based, with no budget curve.
- **Gap we target:** choosing among perception tools *from how the planner's candidates differ*, scored on a budget curve against an oracle.
- **Baselines** (all share one ranker and the same tools):
  - no tool;
  - random tool;
  - **ranker margin**, the generic uncertainty trigger;
  - **always-on**, all 3 tools, 3 calls per decision;
  - an oracle selector as the ceiling.
- **Visual:** a 2x2 grid of what the selector sees (scene only vs. scene + candidates) against how it decides (learned vs. reasoned). Contribution 1 sits in the learned cell, Contribution 2 in the reasoned cell.

> **Speaker notes:** This slide sets up the two contributions as two answers to the same question: learn the selector from outcomes, or reason it out from what each tool could reveal.

---

## 3. Contribution 1: learned selector (Max)

### Slide 5: Method

- **Inputs:** 39 features. 11 describe the scene; 28 describe the candidate set: top candidate's clearance and time to collision, endpoint spread, occlusion of the top path, and where the top two candidates diverge.
- **Model:** a small MLP (32 hidden units) predicts the **signed expected gain** of each tool, averaged over 8 noise draws.
- **Decision rule ("signed abstain"):** call the best tool only if its predicted gain is above 0. It never spends calls that are predicted to hurt.
- **Visual:** a feature-group diagram and the abstain rule as a single line.

### Slide 6: Pre-registered result (seeds 1060-1159, 4,922 decisions)

| Mean accuracy over budgets | Low | Mid | High |
|---|---|---|---|
| Learned selector (`signed`) | 0.500 | 0.447 | 0.375 |
| Same model, scene features only | 0.483 | 0.424 | 0.349 |
| Ranker margin | 0.398 | 0.351 | 0.284 |
| Always-on (3 calls) | 0.585 | 0.490 | 0.357 |

- All four pre-registered hypotheses passed. It beats the ranker margin by +0.091 to +0.103, and the scene-only version by +0.017 to +0.026.
- **Visual:** `f1_pareto_mid.svg` (accuracy against calls per decision).

### Slide 7: The headline: 20% of the calls, no worse and safer

- At **0.6 calls per decision** (20% of always-on's 3 calls):
  - accuracy is non-inferior to always-on at every noise level (+0.006, +0.031, +0.066);
  - the unsafe rate is **lower** at every level (−0.013, −0.025, −0.034), with all intervals below 0.
- It matches always-on's accuracy and safety together at 0.60 / 0.50 / 0.45 calls per decision.
- Adding VLM image features gave +0.010 to +0.016 more (secondary hypothesis, passed; controls are still pending).
- **Visual:** `f3_p4.svg` (difference from always-on, with intervals).

> **Speaker notes:** Be explicit that the 0.6 budget was chosen after the first final split, and that the second final's seeds were fresh.

---

## 4. Contribution 2: counterfactual value-of-information selector (Eshan)

### Slide 8: The question and the method

- **Question:** can we *reason out* the best tool instead of learning it? No learned model, just counterfactuals.
- **For one decision:**
  1. Imagine possible worlds from what the car sees: measurement-noise redraws of visible objects, plus at most one hidden event (a pedestrian or stopped car behind an occluder, an unread light that is red or green, a car behind).
  2. In each world, simulate what each tool would report, then rerun the ranker.
  3. VoI(tool) = expected gain in the ranker's utility from calling it. Call only if VoI > 0.
- **Privacy of the label:** reads nothing privileged (no hidden actors, no oracle labels, no true light); a test enforces this.
- **Visual:** a small flow of 3 worlds → tool answers → reranked choices → expected gain.

> **Speaker notes:** This is the value-of-information idea from the literature (Best-of-Evidence, the off-road paper), applied to the planner's own candidates.

### Slide 9: Pre-registered result: a clear negative (seeds 1160-1259, 4,557 decisions)

| Mean accuracy over budgets | Low | Mid | High |
|---|---|---|---|
| Learned selector (Max) | **0.495** | **0.435** | **0.364** |
| VoI (Eshan) | 0.397 | 0.345 | 0.288 |
| Ranker margin | 0.400 | 0.345 | 0.280 |
| Always-on (3 calls) | 0.577 | 0.472 | 0.346 |

- VoI is **0.076 to 0.098 below** the learned selector, and level with the ranker margin. V1 to V3 failed.
- It does beat the margin when calls are scarce: at 0.1 calls, 0.259 vs. 0.225 at mid noise.
- **Visual:** `paper/figures/voi_pareto_acc.pdf`.

> **Speaker notes:**
> - The pre-registration (`PREREG3.md`) was committed before these seeds were generated.
> - A design fix (noise draws in every world) was made on validation only, and disclosed.
> - The learned selector here is retrained on our regenerated data, which reads 0.010-0.016 lower than Max's own numbers.

### Slide 10: Why it fails (diagnosis and ablations)

- **Root cause.** VoI optimises the *ranker's* utility, but the label is the *oracle's* `c*`, which re-simulates reactive hazards.
  - The base ranker is right on only **24%** of decisions, so a world model built on the ranker inherits that mismatch.
  - The learned selector is trained on real outcomes and absorbs it.
- **Evidence:**
  - VoI's scores track the true gain weakly (per-tool rank correlation 0.08 to 0.22);
  - it picks the best tool on 38% of decisions, against 50% for the learned selector;
  - 13% of its calls hurt, against 1.5%.
- **Ablations (validation):**
  - priors fitted on training data: +0.018 / +0.006 / +0.018;
  - removing the light hypotheses: about −0.007;
  - removing the noise draws: −0.012 at mid;
  - the imaginary car behind never happens, and removing it helps.
- **Cost:** about 0.07 s per decision for about 100 ranker calls, against microseconds for the learned MLP.
- **Visual:** `paper/figures/voi_ablations.pdf`.

### Slide 11: The on-device VLM: what a 3B model can and cannot do

- Qwen2.5-VL-3B (4-bit, mlx) on a MacBook: 0.40 s per embedding, 1.66 s per answer, 5.7 GB peak memory.
- **Asked to choose the tool, it carries no information:**
  - 1,018 of 1,018 answers were `none`, with 5 distinct replies;
  - it copies the answer template (every no-light frame was answered "green");
  - it describes the pedestrian when asked, then says "no pedestrian" and picks `none`.
- **Bug found and fixed:** the float16 vision tower overflowed to NaN on intersection frames.
- **Yes/no answers scored by token probability:** red light reaches AUROC 0.97 within its scenario family, but "is something hidden?" is near chance (0.58). Using it as the VoI prior changed nothing (−0.005 / −0.002 / 0.000).
- **Visual:** a side-by-side of the pedestrian frame and the model's contradictory answers, plus `paper/figures/vlm_yesno_auroc.pdf`.

> **Speaker notes:** Max's 9B model on an A100 called a tool on only 8% of decisions, so size alone doesn't fix this. Use small VLMs for narrow perception questions, not for tool choice.

---

## 5. Limitations (Max)

### Slide 12: Limitations

- **Decision quality, not driving:** no closed-loop runs, so there is no collision rate yet.
- **Simulated tools:** ground truth plus an assumed noise model, not real perception networks.
- **One generator:** 6 scripted families in one simulator, with a non-reactive oracle.
- **Post hoc choices:** the 0.6 budget came from the first final split, and no multiple-comparison correction was applied.
- **Small candidate gain:** the learned selector leads its scene-only version by only about 2 points.
- **Missing controls:** the VLM-feature gain still needs shuffle and family controls on the learned selector.
- **Reproduction gap:** regenerated data give 0.010-0.016 lower learned-selector accuracy; this is unresolved.

---

## 6. Conclusion (Eshan)

### Slide 13: Takeaways

1. **Learning wins.** A small learned selector conditioned on the candidates reaches always-on's decisions with 20% of the calls, and is safer.
2. **Reasoning alone does not, here.** A counterfactual VoI selector is only as good as its world model. Built on a ranker that agrees with the oracle 24% of the time, it ties a simple uncertainty trigger. That is a pre-registered negative result.
3. **Small on-device VLMs** are useful for narrow, probability-scored questions (light state), not for choosing tools.
- **Next steps:**
  - closed-loop collision rates;
  - VLM controls;
  - VoI built on a better world model, or as a feature inside the learned selector.
- **Links:** GitHub, demo video (to be added), report.

---

## Backup slides (only if asked)

- **B1.** Pre-registration timeline for both finals (`PREREG2.md`, `PREREG3.md`) and the seed table.
- **B2.** Harm rate vs. benefit captured at budgets 0.1 to 0.5 (Max's `f5_harm.svg`).
- **B3.** VoI unsafe-rate curves (`paper/figures/voi_pareto_unsafe.pdf`).
- **B4.** Latency bar chart (`paper/figures/latency.pdf`).
- **B5.** The `tools.merge` duplicate-name issue (three cones collapse into one), and why labels and VoI share it.

## To do before the talk

- [ ] Max: confirm his slides 1-2, 5-7 and 12, and the 0.6-budget wording.
- [x] Build the actual deck: `docs/final/deck/joint_deck.pptx` (built on Max's deck by `docs/final/build_joint_deck.py`; see `docs/final/README.md`).
- [ ] Max: choose which of his slides move to backup so the talk fits 10 minutes.
- [ ] Prepare the pedestrian-frame image for slide 11 (`out/frames_dev/occluded_pedestrian/100_2.0.png`).
- [ ] Rehearse to 10:00 with a timer, keeping each section to its time.
- [ ] After the talk, upload to Canvas by Dec 3.
