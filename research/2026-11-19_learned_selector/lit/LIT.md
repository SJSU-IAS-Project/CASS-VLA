# Learned selector: training methods from the literature (2026-11-19)

Scope: how to train a better budgeted single-query tool selector. Scan done 18:05-18:45 PST with WebSearch and
`absfetch.py`. "verified: abs" means the title and date were read from the arXiv abstract page. The one-line methods
come from abstracts or search snippets only; no full text was read, so no result numbers are quoted. The previous scan
(`research/2026-11-06_cass_vla_sota/`) already covers driving tool VLMs and decision-value triggers; they are not repeated.

## (a) Papers

| # | Title | arXiv | Year | Method in one line | Why it matters for us | Verified |
|---|---|---|---|---|---|---|
| 1 | Estimating Conditional Mutual Information for Dynamic Feature Selection (DIME) | 2306.03301 | 2023 | Greedy AFA: a network predicts each feature's conditional mutual information with the label and acquires the argmax | Our selector is a one-step greedy AFA policy; DIME regresses a per-option value score then takes the argmax, as we do | abs (title/date; method from memory of the DIME paper, unchecked) |
| 2 | Distribution Guided Active Feature Acquisition | 2410.03915 | 2024 | AFA guided by distribution estimates of unacquired features | Same family; abstract not read, only title | abs (title only) |
| 3 | Active Feature Acquisition with Generative Surrogate Models (GSMRL) | 2010.02433 | 2020/ICML21 | RL for AFA with a generative surrogate giving intermediate rewards | The RL alternative; our setting has one step, so RL collapses to supervised value regression | abs |
| 4 | AFABench: Benchmarking Active Feature Acquisition | 2508.14734 | 2025 | Compares static, greedy and RL AFA under one protocol; adds AFAContext to expose greedy failures | Gives the comparison frame (static vs greedy vs RL) and a warning that greedy fails when features are only jointly informative; single-query makes us greedy-exact | abs |
| 5 | The Lagrangian Structure of Cost-Penalized AFA | 2610.21919 | 2026 | Greedy "gain minus lambda*cost" with a certificate for the gap to the hard-budget optimum | Supports score = predicted gain - lambda*cost, and thresholding at the budget quantile; shows hard-budget vs penalty gap | abs |
| 6 | Information Templates: Template-based AFA (TAFA) | 2508.18380 | 2025 | Non-greedy AFA that learns acquisition templates instead of RL | Only relevant if we ever allow two queries | abs |
| 7 | Stochastic Encodings for AFA | 2508.01957 | 2025 | Latent-variable model trained to avoid RL difficulty and myopic CMI | Low priority; shows the field's move to stable supervised training | abs |
| 8 | A Survey on Active Feature Acquisition Strategies | 2502.11067 | 2025 | POMDP view of AFA, greedy vs RL families | Citation for framing the selector as a one-step acquisition policy | abs |
| 9 | Consistent Estimators for Learning to Defer to an Expert | 2006.01862 | 2020 | Consistent softmax surrogate with an extra "defer" class | Basis for a "none" class as one more output (K+1 softmax) instead of K sigmoids | abs |
| 10 | Budgeted Multiple-Expert Deferral | 2510.26706 | 2025 | Trains a deferral policy without querying all experts on every training instance | Our labels need all tools swept per decision (we have them); relevant if sweeps get costly | abs |
| 11 | One-Stage Top-k Learning-to-Defer | 2505.10160 | 2025 | Score-based convex surrogate choosing the k most cost-effective entities per input | Cost-sensitive loss with a surrogate that does not depend on k, i.e. one model for all budgets | abs |
| 12 | Consistent Learning-to-Defer with Expert-Conditional Advice | 2603.14324 | 2026 | Learns which expert and which information to give it; losses = prediction loss + fees; warns that composing routing and advice losses can be inconsistent | Closest L2D analogue of "which tool" plus "whether"; warns that separate whether/which heads can be inconsistent, so test joint vs two-stage | abs |
| 13 | SelectiveNet | 1901.09192 | 2019 | Network with an integrated reject head trained at a target coverage | Train the abstain/"whether" head at the target coverage rather than at the class base rate | abs |
| 14 | Calibrated Selective Classification | 2208.12084 | 2022 | Coverage-constrained training so that retained predictions are calibrated | Argues the score used for ranking decisions should be calibrated; supports calibrating per-tool scores | abs |
| 15 | Revisiting Reweighted Risk for Calibration: AURC, Focal, Inverse Focal | 2505.23463 | 2025 | Differentiable AURC loss; links calibration error to selective classification | A loss that directly optimizes the risk-coverage curve, which is our accuracy-vs-budget curve | abs |
| 16 | On Calibration of Modern Neural Networks | 1706.04599 | 2017 | Temperature scaling on a held-out split | The cheap per-tool calibration fix (Platt/temperature) | abs |
| 17 | An Alternative Cross Entropy Loss for Learning-to-Rank | 1911.09798 | 2019 | Softmax cross-entropy as a bound on NDCG-type ranking metrics | Listwise loss across decisions; also the form for choosing among tools within a decision | abs |
| 18 | Why do tree-based models still outperform deep learning on tabular data? | 2207.08815 | 2022 | Benchmark where tuned trees beat MLPs on medium tabular data | Our ~39 hand features are tabular and extra data did not help the MLP: a GBDT is the obvious alternative learner | abs |
| 19 | Meta-learners for Estimating Heterogeneous Treatment Effects | 1706.03461 | 2017 | S/T/X-learners: regress outcomes or effects with any base learner | Our gain of tool over no tool is a treatment effect; S-learner (one net with tool input) vs T-learner (per-tool) vs direct-effect regression | abs |
| 20 | Policy Learning with Observational Data | 1702.02896 | 2017 | Learns treatment policies under a budget from doubly-robust effect scores | Justifies training on the 8-draw mean gain as a low-noise score and ranking by it under a budget | abs |
| 21 | Metalearners for Ranking Treatment Effects | 2405.02183 | 2024 | Meta-learners that rank individuals for budgeted treatment instead of estimating effects accurately | Direct precedent for ranking-oriented training under a budget; snippet notes that the KU Leuven top-k ranking study found limited gains (unchecked) | abs |
| 22 | Acting Less is Reasoning More (OTC) | 2504.14870 | 2025 | RL for LLM tool use with a reward penalising unnecessary calls | Cost penalty in the reward; analogue of subtracting lambda*cost and abstaining when net gain <= 0 | abs |
| 23 | SMART: Self-Aware Agent for Tool Overuse Mitigation | 2502.11435 | 2025 | Trains an agent to decide when to rely on parametric knowledge vs a tool | Overuse of tools is the same failure as our harmful calls | abs (title/date only) |
| 24 | Budget-Aware Agentic Routing via Boundary-Guided Training | 2602.21227 | 2026 | Routes between cheap and expensive models under hard per-task spend; uses always-cheap and always-expensive policies as reference points | Mirrors our no-tool and always-on anchors; one soft-penalty model does not fit every hard budget (search snippet), so test budget-conditioned scoring | abs |
| 25 | LLM Agents Already Know When to Call Tools (When2Tool) | 2605.09252 | 2026 | Benchmark plus a linear probe on hidden states predicting tool necessity | A linear/probe "whether" head on frozen features is competitive; supports a simple convex baseline next to the MLP | abs |

Seen only as search snippets, not abs-fetched (do not cite without checking): 2602.11541, 2511.17006, 2605.00737, 2607.23332.

## (b) Ranked cheap experiments

All are exploratory, judged on val/test only, never on `out/v3_final`. Each should fit in under 20 CPU-minutes with
`OMP_NUM_THREADS=1`. Fit on the existing `out/v2_dataset/train.jsonl` and `out/v2_expgain.jsonl`. "Change" is stated in
terms of `fit_mlp` and the selection code in `scripts/eval_baselines.py` and `scripts/eval_triggers.py`; I did not read
those scripts line by line, so adapt names to what is there. Expected effects are my judgement, not measured.

1. **Signed-gain regression head plus abstain at predicted gain <= 0.**
   Motivation: #19, #20, #5, #22. Change: replace the sigmoid and class-balanced BCE by a linear output per tool trained with
   MSE or Huber on the unclipped signed expected gain (mean over 8 draws, no clipping at zero). Score of a decision =
   max over tools of predicted gain; the call is made only if that max is above 0 and the decision is in the top budget
   fraction; otherwise no tool. Expected: fewer harmful calls (the harm/benefit split in `out/v3_eval/triggers.json` is
   the metric to watch) and a small gain at high budgets, where harmful calls currently dilute accuracy. Risk: MSE on a
   mostly-zero target regresses toward 0; use Huber and compare.
2. **Per-tool calibration before the max.**
   Motivation: #16, #14. Change: hold out about 20% of train rows, fit isotonic or Platt per tool on the held-out
   predictions against the binary "gain > 0" (or against the gain value), then rank decisions by the max calibrated score.
   Cost: seconds. Expected: removes cross-tool scale mismatch so the argmax and the top-budget cut stop favouring the
   tool with the most inflated sigmoid; effect likely small, 0 to 1 point, but it is almost free. Run as a post-hoc wrapper
   on the existing fitted MLP.
3. **Listwise or pairwise ranking loss across decisions.**
   Motivation: #17, #21, #15, #11. Change: keep the tool outputs, but add (or swap in) a loss on decision-level score
   s_i = max_t f_t(x_i): pairwise logistic on pairs (i, j) with a different best-tool gain, or a softmax cross-entropy
   over a mini-batch of decisions with the max-over-tools gain as the relevance. Weight pairs by the gain difference.
   Expected: the best candidate for the part of the curve at low and mid budgets, since only the ranking matters
   there. Literature caution: #21's snippet says top-k ranking gains can be limited, so expect 0 to 1 point.
4. **K+1 softmax with a "none" class and a cost term.**
   Motivation: #9, #12, #13, #22. Change: one softmax over {none, roi, depth, collision}; target the argmax of the mean
   gain (none if all gains <= 0), or use a soft target proportional to positive gain. Rank decisions by 1 - p(none) or
   by p(best tool). Also try a lambda*cost subtraction. Expected: makes "which" and "whether" compete in one loss,
   which removes inconsistency of independent sigmoids; may cut harmful calls. Compare against experiment 5.
5. **Two-stage "whether" then "which".**
   Motivation: #12, #13. Change: stage 1 a binary head for "best tool gain > 0 (or > eps)", stage 2 a tool-choice
   head trained only on rows with positive gain. Rank by stage 1, pick the tool with stage 2. #12 warns composing the
   two can be inconsistent; the test is whether it still beats experiment 4. Expected: better tool choice at low
   budgets because stage 2 no longer trains on rows where every tool is useless.
6. **Gradient-boosted trees (sklearn HistGradientBoosting or LightGBM if installed) on the same ~39 features.**
   Motivation: #18, #19 (T-learner). Change: one regressor per tool on the signed gain (or one classifier on gain > 0),
   `max_iter` about 200, depth 3-4, single thread. Then use the same selection code. Expected: on tabular geometry
   features trees often match or beat the MLP, and trees are monotone-friendly; the CASS lead over the scene-only
   learner may widen or shrink, which is itself informative for the attribution claim. Run the scene-only twin for a
   fair comparison. About 3-5 CPU-minutes.
7. **Cost-sensitive weights on harmful calls.**
   Motivation: #22, #23, #5. Change: keep BCE but weight each (row, tool) example by |gain| (positive class) and by
   a factor of 2-5 for rows where the tool has negative gain (negative class), instead of class-balanced weights.
   Expected: moves the score away from harmful calls; likely overlaps with experiment 1, so run only if 1 shows
   promise, or as the cheap variant of it.
8. **Budget-conditioned or lambda-sweep scoring.**
   Motivation: #24, #5, #11. Change: instead of only taking the top budget fraction by max score, sweep lambda in
   score = pred_gain - lambda*cost and report the realised call rate; compare its accuracy-vs-calls curve with the
   quantile cut. Expected: identical ordering if cost is uniform per tool, so mostly a check of whether per-tool cost
   terms help; low priority.

Suggested order given the time: 1, 2 and 6 first (each under 5 minutes), then 3 and 4, then 5, then 7, then 8.
Report them all with the harm/benefit split and 95% bootstrap CIs, not only mean accuracy, because the expected lead is
a 1-2 point change and the noise on 2,235 test rows is of that order.

## Caveats
- Nothing here was run. Effect sizes are guesses from the literature's direction, not measurements.
- #1 and #23 have title and date verified only; the method text for #1 is from memory.
- Evidence that ranking or tree learners beat a tuned MLP in a setting like ours was not found; #18 is general tabular evidence.
