# Final report: draft

**Submission:** Dec 15, 2026, 11:59 pm (hard cutoff Dec 16, 5 pm). A LaTeX PDF in a conference template, with the GitHub and video links at the top.
**Grading:** report 50, repository 30, video 20.

**This draft is Markdown.** The submission has to be LaTeX: copy each section into an IEEEtran conference template (`paper/main.tex`, `paper/sections/*.tex`). Every diagram and plot must be a vector PDF; `pdfimages -list paper/main.pdf` should list no raster images for plots or diagrams. Target length: 6-8 pages plus references.

**Section owners** follow the agreed split (intro, contribution 1, limitations: Max; background, contribution 2, conclusion: Eshan) and `work_plan.md` (Max also writes related work and the scenario and oracle method). Owners are marked in [brackets]. Before submission, recheck every number against its source file; do not copy numbers by hand into the LaTeX.

**Number sources.**
- **Max (C1):** `research/2026-11-19_learned_selector/deliverables/report/report.md` and `out/v4_eval/final_geom.json` / `final_vlm.json`, seeds 1060-1159, Max's data.
- **Eshan (C2):** `out/voi_eval/final.json`, `valtest.json`, `val_ablations.json`, `diagnosis.json` and `out/vlm_yesno/eval_val.json`, seeds 1160-1259 and 100-399, regenerated data, summarised in `docs/voi_selector.md` and `docs/vlm_failure_analysis.md`.
- The two finals use different fresh seeds and slightly different data builds (see Section V-C). Say so in the paper.

---

## Title, authors, links [Eshan]

**Which Perception Tool Should a Driving Planner Call? Learned and Counterfactual Value-of-Information Selection over Candidate Trajectories**

Max Dokukin, Eshan Chawla. San José State University, CMPE 249.

- Code: https://github.com/SJSU-IAS-Project/CASS-VLA
- Video: *TODO: YouTube (unlisted) link*

## Abstract [Eshan], about 230 words

A driving planner often holds several plausible trajectories whose safety hinges on something the scene alone does not show: a hidden pedestrian, an unread light, a misjudged closing speed. Before committing, it can afford one extra perception query, but calling every tool on every step is costly and a noisy reading can flip a correct choice. We ask which single tool to call (ROI inspection, depth or a geometric collision check), or none, given the planner's candidates. In MetaDrive, with six hazard families, simulated tools at three noise levels and a re-simulation oracle, we compare two selectors under pre-registered tests on fresh scenario seeds.

A learned selector, a small MLP over candidate-set features trained on the signed expected gain of each tool, calls only when it predicts a gain. At 0.6 calls per decision, 20% of always-on's three, it is non-inferior to always-on in accuracy and safer at every noise level (unsafe rate −0.013 to −0.034). It beats a ranker-margin trigger by 0.09 to 0.10.

A counterfactual value-of-information selector with no learned model, which simulates what each tool would reveal across world hypotheses, falls 0.08 to 0.10 below the learned selector and only ties the margin trigger. Our diagnosis traces this to its ranker-based world model, which agrees with the oracle on 24% of decisions.

An on-device 3B VLM cannot choose tools, but its token probabilities read traffic lights well (AUROC 0.97).

*(Check the length after editing: the target is 150-250 words.)*

---

## I. Introduction [Max]

**Motivation.**
- Runtime perception budgets in automated driving: latency and compute.
- Extra evidence can hurt (DEEP: 34-54% of loss-changing escalations make it worse; ToolGate: 9.9% of calls flip right to wrong).

**Problem.** Given K ≤ 6 candidate maneuvers and an ambiguous scene, choose one of {ROI, depth, collision, none} to maximise the chance that the ranker picks the oracle-best candidate `c*`, under a budget of calls per decision.

**The instructor's scoping.** One question, three tools, oracle labels from simulator state, five comparisons. The success criterion: similar or better safety decisions with substantially fewer perception calls than generic or always-on verification.

**Contributions** (bulleted, as the rubric asks):
1. A reproducible MetaDrive benchmark: six hazard families, a candidate generator, a re-simulation oracle, three simulated tools at three noise levels, and expected-gain labels. [Max]
2. A learned, candidate-conditioned selector with a signed-gain abstain rule. Pre-registered on fresh seeds, it reaches always-on decisions at 20% of the calls and is safer. [Max]
3. A counterfactual value-of-information selector with no learned model, built on world hypotheses from the base observation. Its pre-registered negative result on fresh seeds comes with a root-cause diagnosis and ablations. [Eshan]
4. An on-device VLM study (Qwen2.5-VL-3B, 4-bit, Apple Silicon): why a small VLM cannot choose tools (four causes, including a float16 overflow bug we fixed), and which narrow, probability-scored questions it does answer. [Eshan]

## II. Related Work [Max]

Condense §2 of Max's report into about 0.75 page, in four groups:

- **Plan-aware compute allocation:** SIGMA (2610.09520), DEEP (2609.35910), BLUE (2606.08684), ASSCG (2606.25509), DualDriveVLA (2602.10719).
- **When to call a tool or expert:** Calibrate-Then-Delegate (2604.14251), To Call or Not to Call (2605.00737), ToolGate (2606.03054), DriveAgent-R1 (2507.20879), Proof-of-Perception (2603.00324).
- **Value of information and counterfactual selection:** Best-of-Evidence (2607.20950, plug-in VoI with no trained model), the off-road map-layer paper (2611.06702, rule-based rescoring under hypotheses), active feature acquisition, adaptive submodularity (1003.3967), nonmyopic VoI (1207.1394). *[Eshan adds 2-3 sentences: our VoI selector is the driving, candidate-conditioned, multi-tool instance of this family, with a budget curve.]*
- **Driving VLMs and VLAs:** a short paragraph linking to the proposal's literature survey (`docs/literature_survey.md`).
- **The claim:** narrow. Candidate-conditioned tool choice, with counterfactual-gain targets, evaluated on a budget curve against an oracle.

Use the verified entries in `research/2026-11-06_cass_vla_sota/references.bib`.

## III. Method

**Figure 1 (vector, TikZ, `paper/figures/architecture.tex`):** scene → base observation → candidate generator → selector (learned | VoI | +VLM) → tool call → merged belief → ranker → chosen maneuver, with the oracle and labels on the side. *TODO: draw it. Max's `f0_pipeline.svg` can be the starting point; convert it to PDF.*

### A. Scenarios, candidates and oracle [Max]

- **Six families:** occluded pedestrian, occluded cross traffic, ambiguous light, lead brake or cut-in, lane blockage, merge closing speed. Scripted hazards on procedural maps.
- **Decision points:** a hazard-blind cruise prefix, then a decision. A decision is kept only if at least one candidate is safe and at least one is unsafe.
- **Candidates:** keep, keep fast, decelerate, stop, change left, change right, over a 5 s horizon.
- **Oracle:** re-simulates each candidate against the true actors. Safe means no collision, red-light or off-road event, clearance ≥ 0.5 m and TTC ≥ 1.0 s. `c*` is the best candidate under safety first, then progress minus penalties.
- **Ranker:** the same rules on a belief, with constant-velocity prediction and disc approximations.

### B. Tools, noise and labels [Max]

- **Base observation:** the front camera, with 15% range and 2 m/s velocity noise, no occluded actors, and the light readable within 20 m.
- **Tools:**
  - ROI: corridor actors, including occluded ones, plus the light;
  - depth: precise range and speed of visible actors;
  - collision: tracked unoccluded actors within 50 m, front or rear.
- **Noise levels:** low, mid and high.
- **Merge:** a tool response replaces the base estimate of the same actor.
- **Expected-gain label:** correctness after the call, averaged over 8 noise draws, minus no-tool correctness.
- **Metric:**
  - top-1 accuracy (pick == `c*`) averaged over 21 budgets from 0 to 1 call per decision;
  - unsafe rate of the pick;
  - always-on = all three tools, 3 calls per decision.

### C. Learned selector (`signed`) [Max]

- **Features:** 39 in total. 11 scene features; 28 candidate-set features, including top-candidate clearance and TTC, endpoint and progress spread, occlusion of the top path, and the divergence of the top two candidates.
- **Model and training:** an MLP with 32 ReLU units and a linear output per tool, trained with squared loss on the unclipped expected gain. 300 full-batch Adam steps, lr 0.01, L2 1e-3, 3 init seeds averaged.
- **Decision rule:** rank decisions by the maximum predicted gain, call the argmax tool within the budget, and only if the predicted gain is above 0.
- **Equation:** $\hat g_t(x)$ for each tool $t$; call $\arg\max_t \hat g_t$ iff $\max_t \hat g_t > 0$.

### D. Counterfactual value-of-information selector (`voi`) [Eshan]

**World hypotheses** (`cassvla/planning/hypotheses.py`, shared with Max's flip features). Built from the base observation, the ego state and the map only:
- (i) 8 measurement-noise draws of the visible actors, using the base camera's noise model;
- (ii) a stopped vehicle or a crossing pedestrian at up to 6 occluded points on candidate paths;
- (iii) an unread light set to red or green;
- (iv) a fast car 12 m behind in each adjacent lane.

**Compositional world model.** Every world carries a noise draw; hidden events (ii-iv) are layered on top of one. A first design treated the noise-free base estimate as a world of its own; it is ruled out because the camera is always noisy, was replaced on validation, and is reported as an ablation.

**Weights.**
- Each component $c$ (no event, occluded vehicle, occluded pedestrian, light, rear) gets prior $\pi_c$, renormalised and split evenly over its worlds.
- Priors are event rates on the 10,329 training decisions: occluded vehicle 0.014, occluded pedestrian 0.102, unread light not green 0.415, car behind 0.0. They enter as relative weights against the no-event component.

**Value of a tool.** For worlds $w_k$ with weights $\omega_k$:

$$\mathrm{VoI}(t) = \sum_k \omega_k\, U\big(c_{t,k}, w_k\big) - \sum_k \omega_k\, U\big(c_0, w_k\big)$$

- $c_0$ is the ranker's pick from the base observation.
- $c_{t,k}$ is its pick after tool $t$ answers in world $w_k$. The answer is simulated by running the tool model on a pseudo-record in which $w_k$ is the truth, with its own noise stream.
- $U$ = ranker score − 200 · [unsafe], the ranker's own objective.

**Decision rule.** Call $\arg\max_t \mathrm{VoI}(t)$ only if it is above 0, inside the budget. VoI can be negative, which predicts a harmful call.

**What it never reads:** hidden actors, `c*`, oracle metrics or the true light. A unit test changes these fields and checks that VoI is unchanged.

**Settings frozen on validation** (`FROZEN.json`): fitted priors, 8 draws, all classes, tool answers simulated at the evaluated noise level, λ = 0.

### E. On-device VLM [Eshan]

- **Model and pass:** Qwen2.5-VL-3B-Instruct, 4-bit, run through mlx on Apple Silicon. One 640x360 front-camera frame per decision, rendered at the exact decision state (ego pose within 5 cm of the record).
- **Prompted tool choice:** frame + speed + candidate names → JSON {hazards, occlusion, light, query}. No oracle information.
- **Yes/no questions**, scored as P(Yes) / (P(Yes) + P(No)) on the first answer token:
  - pedestrian present;
  - road ahead hidden behind a stopped vehicle;
  - light red or yellow.
- **VLM prior for VoI (`voi_vlm`):** occluded-vehicle and occluded-pedestrian priors set to P(hidden)/2 per decision. This costs one VLM call per decision.

## IV. Experiments and Ablations

### A. Setup and protocol [Eshan]

- **Hardware:**
  - Max's runs: a 16-core Linux machine, plus an SJSU cluster A100 for the 9B VLM.
  - Eshan's runs: an Apple Silicon Mac, 10 cores, 64 GB; the VLM ran there through mlx.
- **Seeds and splits:**
  - 100-399 is the main dataset (70/15/15 train/val/test by seed);
  - 460-759 and 860-1059 are extra training seeds (34,718 training rows in total);
  - 1060-1159 was the final for C1;
  - 1160-1259 was the final for C2.
  - Each final was pre-registered before its seeds existed and opened once (`PREREG2.md`, `PREREG3.md`).
- **Statistics:** 95% paired bootstrap over scenario seeds, 1,000 resamples. No multiple-comparison correction; say so.
- **Baselines:** no tool, random, ranker margin, scene-only learned, always-on, and the fair ceiling.

### B. Contribution 1: learned selector (seeds 1060-1159, 4,922 decisions) [Max]

**Table I.** Mean accuracy over budgets (unsafe rate).

| Method | Low | Mid | High |
|---|---|---|---|
| signed | 0.500 (0.397) | 0.447 (0.443) | 0.375 (0.510) |
| frozen (clipped-gain MLP) | 0.498 (0.403) | 0.439 (0.457) | 0.356 (0.536) |
| signed, scene features only | 0.483 (0.409) | 0.424 (0.460) | 0.349 (0.527) |
| ranker margin | 0.398 (0.495) | 0.351 (0.537) | 0.284 (0.604) |
| always-on (3 calls) | 0.585 (0.315) | 0.490 (0.388) | 0.357 (0.491) |

**Pre-registered hypotheses.** All passed.
- P1, signed − frozen: +0.009 at mid, +0.019 at high.
- P2, signed − scene-only: +0.017 to +0.026.
- P3, signed − margin: +0.091 to +0.103.
- P4, at 0.6 calls per decision against always-on:
  - accuracy +0.006 [−0.002, 0.016], +0.031, +0.066;
  - unsafe rate −0.013, −0.025, −0.034, with all intervals below 0.

Caveat: the 0.6 budget was chosen post hoc from the first final.

**VLM features (Q1, secondary):** +0.016 / +0.012 / +0.010. Shuffle and family controls on the signed model are pending.

**Figures:** accuracy-budget curve at mid noise; P4 differences with intervals. *Convert Max's `f1_pareto_mid.svg` and `f3_p4.svg` to PDF.*

### C. Contribution 2: VoI selector (seeds 1160-1259, 4,557 decisions) [Eshan]

**Table II.** Mean accuracy over budgets (unsafe rate), final split.

| Method | Low | Mid | High |
|---|---|---|---|
| signed (retrained on regenerated data) | 0.495 (0.404) | 0.435 (0.458) | 0.364 (0.524) |
| VoI, abstains at VoI ≤ 0 | 0.397 (0.489) | 0.345 (0.532) | 0.288 (0.586) |
| VoI, budget only | 0.399 | 0.347 | 0.288 |
| ranker margin | 0.400 (0.495) | 0.345 (0.542) | 0.280 (0.610) |
| always-on (3 calls) | 0.577 (0.321) | 0.472 (0.404) | 0.346 (0.498) |

**Pre-registered hypotheses (PREREG3):**
- **V1:** VoI non-inferior to signed. **Failed:** −0.098 [−0.107, −0.088], −0.090 [−0.099, −0.081], −0.076 [−0.085, −0.066].
- **V2:** VoI beats margin. **Failed:** −0.003 [−0.014, 0.009], −0.000 [−0.010, 0.010], +0.008 [−0.003, 0.018].
- **V3:** VoI at its own call rate vs. always-on. **Failed.**
- **V4:** VoI + VLM. **Not run on the final seeds** (the yes/no answers were not ready; see `V4_STATUS.md`).

**Budget dependence.** VoI beats the margin when calls are scarce and loses when they are plentiful.

| Accuracy at budget | VoI (low / mid / high) | Margin (low / mid / high) |
|---|---|---|
| 0.1 calls/decision | 0.270 / 0.259 / 0.247 | 0.239 / 0.225 / 0.213 |
| 0.3 calls/decision | 0.344 / 0.307 / 0.270 | 0.325 / 0.290 / 0.248 |
| 1.0 call/decision | 0.509 / 0.415 / 0.318 | 0.557 / 0.454 / 0.332 |

**Validation and test (seeds 100-399)** show the same ordering. VoI with uniform priors (no training data at all) is 0.006-0.020 below VoI with fitted priors there; it was not run on the final seeds.

**Figure:** `paper/figures/voi_pareto_acc.pdf` (and `voi_pareto_unsafe.pdf`).

**Data note.** C2's data were regenerated on the Mac from the same code. Split sizes match Max's exactly, but the learned selector scores 0.010-0.016 lower on validation than in Max's run, probably because his data predate a feature and hazard fix (`research/2026-11-20_voi_selector/DATA.md`). All C2 comparisons use one dataset and one codebase for every method.

### D. Ablations (validation) [Eshan; Max adds C1 ablations]

**Table III.** VoI variant minus reference (uniform priors), mean accuracy [95% CI].

| Variant | Low | Mid | High |
|---|---|---|---|
| fitted priors | +0.018 [0.008, 0.027] | +0.006 [−0.004, 0.016] | +0.018 [0.006, 0.029] |
| no noise draws | −0.003 [−0.012, 0.005] | −0.012 [−0.022, −0.003] | −0.007 [−0.021, 0.007] |
| no light hypotheses | −0.006 [−0.012, −0.002] | −0.008 [−0.013, −0.003] | −0.008 [−0.014, −0.003] |
| no occluded pedestrian | +0.005 | −0.006 | +0.001 |
| no occluded vehicle | +0.005 | +0.004 | +0.003 |
| no rear car | +0.008 [0.003, 0.013] | +0.004 | +0.010 [0.002, 0.018] |
| 4 / 16 draws | within ±0.007 | | |
| noise-unaware simulation | +0.011 | 0.000 | +0.008 |
| first design (alternatives) | +0.005 | −0.007 | −0.003 |
| VLM prior (`voi_vlm`) − VoI | −0.005 [−0.011, 0.000] | −0.002 [−0.009, 0.004] | +0.000 [−0.006, 0.006] |

**Reading:**
- Fitted priors matter most.
- The light and noise hypotheses carry real value.
- The imaginary rear car hurts; it never occurs in the data, and fitted priors give it weight 0.
- The VLM prior adds nothing.

**Figure:** `paper/figures/voi_ablations.pdf`.

**C1 ablations [Max]:** candidate-only vs. scene-only (+0.011 to +0.026), permutation importance (the identity of the chosen candidate matters most), flip features (no gain, S1 failed), and the learner variants (calibration, softmax, pairwise: no gain).

### E. Latency and resources [Eshan]

| Step (Apple Silicon Mac) | Seconds |
|---|---|
| Learned selector, MLP forward pass | about 2e-6 |
| VoI selector, per decision per noise level (about 100 ranker calls) | 0.06-0.07 |
| VLM embedding, float32 vision tower | 0.40 |
| VLM prompted answer | 1.66 |
| VLM peak memory | 5.7 GB (3.8 GB in float16, which overflows) |

**Figure:** `paper/figures/latency.pdf`.

### F. VLM study [Eshan]

**Prompted tool choice** (1,018 frames, `out/vlm_probe/report.json`):
- 5 distinct replies; `query = none` on all 1,018; `occlusion = true` on 0;
- 4 verbatim template copies;
- light read correctly on 92.5% of frames with a light, but "green" on 737 of 737 frames without one.

**Prompt variants on the same frame:**
- "describe" finds the pedestrian;
- "is there a pedestrian?" answers no;
- "list hazards, then a query" lists the pedestrian, then picks none;
- with `none` removed, the answer becomes a constant `depth`.

**Yes/no AUROC on validation** (2,222 decisions):
- red light: 0.999 overall, 0.97 within its family;
- pedestrian: 0.89, but the score tracks the scenario family;
- hidden road user: 0.58.

**Comparison:** Max's Qwen3.5-9B prompted variant called a tool on 8% of decisions (0.261 vs. 0.250 for no tool).

**Figure:** `paper/figures/vlm_yesno_auroc.pdf`. A qualitative figure (the pedestrian frame with the four contradictory answers) is still *TODO* and must be vector-safe: embed the photo as an image, with the text as vector.

## V. Failure Analysis, Negative Results and Limitations

### A. Why the VoI selector fails [Eshan]

1. **World-model mismatch.**
   - VoI maximises the ranker's utility; the label is agreement with the oracle's `c*`, which re-simulates reactive hazards.
   - The base ranker agrees with the oracle on 24.1% of validation decisions.
   - A selector whose world model is the ranker cannot see when the ranker itself is wrong. The learned selector is trained on oracle outcomes and absorbs this.
2. **Weak score-gain coupling.**
   - Per-tool Spearman correlation between VoI and the true expected gain is 0.08-0.22.
   - Its max score separates "some tool helps" with AUROC 0.59-0.61 (margin: 0.56-0.57).
   - Tool choice is optimal on 38% of helped decisions, against 50% for the learned selector.
   - 13% of its calls are harmful at budget 0.3, against 1.5%.
3. **Prior mapping.** Event rates used as relative weights under-weight events: a red light gets an effective weight of about 0.14 against a fitted rate of 0.41.
4. **Design iteration on validation.** The first world model (the noise-free base as a world) was worse and was replaced before the final. This is disclosed, and kept as an ablation.

### B. Failure modes of the learned selector [Max]

- Late calls hurt the frozen model; the signed abstain fixes this.
- 55-76% of the gap to the ceiling is calling on the wrong decisions.
- The model collapses to depth.
- `lead_brake_cutin` and `occluded_cross_traffic` have low ceilings: the hazard starts after the decision.

### C. VLM negative results [Eshan]

The four causes (`docs/vlm_failure_analysis.md`):
- template copying;
- perceiving the pedestrian but not using it in the answer;
- tool choice beyond the model's reasoning;
- a float16 vision-tower overflow (11 NaN frames, `!!!!` replies, PCA failure), now fixed with float32 and a NaN guard.

### D. Limitations [Max]

- **Decision quality, not closed-loop driving:** no collision rate.
- **Simulated tools** with an assumed noise model.
- **One generator** with six scripted families and a non-reactive oracle.
- **Post hoc choices:** the 0.6 budget came from an earlier split, and there is no multiple-comparison correction.
- **Small candidate gain:** about 2 points over scene-only.
- **Missing controls:** for the VLM-feature gain.
- **Reproduction gap:** regenerated data read 0.010-0.016 lower.
- **Benchmark quirk:** `tools.merge` keys actors by name, so repeated names (cones) collapse. Labels and VoI share this.

## VI. Conclusion and Future Work [Eshan]

**Takeaways:**
- A learned, candidate-conditioned selector meets the instructor's criterion: always-on decisions at 20% of the calls, and safer.
- A principled counterfactual VoI selector with no learned model does not. It is only as good as its world model, and here it ties a simple uncertainty trigger.
- Small on-device VLMs help with narrow, probability-scored questions (light state), not tool choice.

**Future work:**
1. Closed-loop collision rates at about 0.6 calls per decision.
2. VoI on a better world model, for example one that learns the ranker-to-oracle gap. Alternatively, VoI as an input feature to the learned selector.
3. VLM controls (shuffle, family, blank image) and V4 on fresh seeds.
4. A learned perception model in place of a simulated tool.

## References

*TODO: export from `research/2026-11-06_cass_vla_sota/references.bib`.* Minimum set: MetaDrive; SIGMA; DEEP; BLUE; ASSCG; DualDriveVLA; Calibrate-Then-Delegate; To Call or Not to Call; ToolGate; Best-of-Evidence; 2611.06702; DriveAgent-R1; Proof-of-Perception; adaptive submodularity; nonmyopic VoI; Qwen2.5-VL; mlx-vlm; the literature-survey papers from the proposal.

---

## Checklist before submission

- [ ] Port to the IEEEtran template: `paper/main.tex`, `paper/sections/*.tex`, `refs.bib`, and a Makefile with `latexmk -pdf`.
- [ ] TikZ architecture diagram (Figure 1).
- [ ] Convert Max's SVG figures to PDF (`rsvg-convert -f pdf` or Inkscape). No PNG plots.
- [ ] Qualitative figure: the pedestrian frame and the VLM answers. Optionally, top-down plots of 2-3 decisions where VoI and the learned selector disagree.
- [ ] Abstract within 150-250 words; contributions as bullets; links clickable at the top.
- [ ] Every number traced to its JSON source. The data note on the two finals is in the paper.
- [ ] `pdfimages -list paper/main.pdf` shows no raster plots.
- [ ] README updated with the links and the reproduction chain (repository: 30 points).
