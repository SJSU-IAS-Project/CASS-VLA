# Main-thread checks

## verify.py, run 1 (about 22:50 PST)

Counter: OK 298, NO_ARXIV 37, MISMATCH 23. Each MISMATCH was read by hand:

- 21 are headings that paraphrase, shorten or group the arXiv title (e.g. "Judge, Then Drive (anchor, extra detail only)", "FastDriveVLA, SToRM, MVPruner", "Anchors fetched (older ...)"). The id matches the first named paper. No fix needed; grouped headings give one row per group in papers.csv.
- 2606.06219: the block heading uses the v1 title "CLEAR"; arXiv v2 is retitled "Vault". Same paper (F agent confirmed). No fix.
- 1909.08792 under "Context-Aware Conformal Prediction (CA-CP)" in raw/B_budgeted_perception.md: parser artifact. The CA-CP block has no arXiv id (ICML 2026 workshop page, OpenReview qCxRADChHQ); the parser picked up an id from later text. The CA-CP row in papers.csv must not carry 1909.08792.

## DEEP arXiv version

raw/H_openreview_sweep.md says no arXiv version of DEEP was found. raw/X1_competitor_deepread.md says it is arXiv:2609.35910. Checked with absfetch: arXiv:2609.35910, "The Decision Value of Perception Compute", Cong, Hoang Pham et al., 2026/09/28. The abstract matches the OpenReview submission l9QJO8BIoE (34–54% harmful escalations, sign disagreement on nuScenes, "select nearly as much harm as random"). X1 is right; H's "none found" is wrong for DEEP.

## Our own results against the scan (docs/baseline_results.md)

- Matched ablation that X1 asks for already exists: selector MLP vs scene-only MLP (same learner, agnostic features + ranker margin only). Lead +0.016 / +0.011 / +0.017 at low/mid/high noise, 95% bootstrap intervals above zero.
- Ranker-margin baseline (entropy-like trigger, as in Expand-and-Prune) is in the table; the selector leads it by 6–10 points.
- Random baseline in table; selector leads at every budget above 0 by at least 0.016.
- Not in our evaluation yet: harm selected / benefit captured / nDG (DEEP), ego-speed baseline (DEEP), KnowNo-style set-size trigger, fixed-schedule baseline at matched rate (Learning When to Search), blank-image control for VLM features (2606.31257, DriveBench), counterfactual-rollout baseline (2611.06702).

## verify.py, run 2

Counter: OK 423, NO_ARXIV 80, MISMATCH 24. One new mismatch: 2609.30818 under the grouped heading "Planner-Breaker, CornerBench, Bench2Drive-Plan, RegAD, HazardArena" in raw/H_openreview_sweep.md. Same parser artifact as CA-CP: the grouped block has no arXiv id and the parser took the next one (iDriveVLA, which is 2609.30818). The grouped row in papers.csv must not carry that id.

## papers.csv fixes after merge.py

- DEEP row: arxiv set to 2609.35910 (see above).
- 2606.22277 AS-DDTO: relevance HIGH -> LOW, following X3's full-text read.

## Checks of AUDIT.md before revising REPORT.md (about 23:15)

- RRDrive 2609.21486 html (fs_C cache): Table 5 caption "Within-good-candidate ranking ... the risk profile adds ranking information beyond trajectory geometry"; text "the oracle rank from 33.9 to 27.7". AUDIT right.
- BLUE 2606.08684 abstract: "pretrained VLA hidden states potentially already encode whether language will benefit a given frame, even though scene complexity and kinematic features alone struggle to predict this". AUDIT right: a benefit gate.
- docs/baseline_results.md: occluded_cross_traffic 0.347 scene-only vs 0.330 selector (final split, mid noise, half a call); 0.272 vs 0.297 in the 510-seed test table. occluded_pedestrian 0.440 vs 0.545 (+0.105) and 0.371 vs 0.419 (+0.048).

## Checks of AUDIT2.md (about 23:30)

- Best-of-Evidence: absfetch arXiv:2607.20950, "Best-of-Evidence: Best-of-N Selection under Partial Verification", Zhang, Cenwei et al., 2026/07/23. Abstract: "keeps the BoN candidate pool fixed ... allocates a limited budget to evidence actions that can change the final choice"; four medical VQA settings. papers.csv row given the id.
- DriveJudge 2606.17362 Table 3 (fs_C cache): VLM-DirectScore 50.06, DriveJudge-ZeroShot 56.13, VLM-DirectScore-Ft 68.67, DriveJudge 77.95. AUDIT2 right.
- AUDIT.md verdict tally by leading verdict, counted with python: CONFIRMED 56, OVERSTATED 13, WRONG 5, UNVERIFIABLE 1 (75).

## Checks of Z2 (about 00:20)

- CLARINET arXiv:2405.15784, Chi, Yizhou et al., 2024/04/28. Abstract: "conditions on a retrieval distribution, finetuning end-to-end to generate the question that would have maximized the rank of the true candidate at each turn"; beats information gain by 17% relative on retrieval success. Candidate-conditioned and trained on counterfactual gain: confirmed. Choice is among generated questions, not among source types.
- BudgetVerify arXiv:2609.33052, Jenq, Janet et al., 2026/09/27. Abstract: routes each answer to no verification, a light check or a costly check; router "trained from offline correctness and token-cost outcomes"; Pareto frontiers against fixed verification policies. One answer, not a candidate set: confirmed.
