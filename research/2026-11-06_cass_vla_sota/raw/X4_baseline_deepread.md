# X4_baseline_deepread

Method: full arXiv HTML text fetched with curl, tags stripped, math alttext kept. Quotes are verbatim from that text. Section numbers are the papers' own. Written 2026-11-06 (PST). Sections 3-5 are appended below as they are finished.

---

## 1. Best-of-Evidence (BoE), arXiv:2607.20950v1 (cs.LG, 23 Jul 2026), Zhang et al., IQuest Research / INSAIT / DTU

### Setting and the exact method
- Fixed pool of K candidates sampled from a VLM (Sec 2.1). A cheap prior f_0 gives each candidate a score (the ledger uses answer-frequency, whose argmax is raw majority). "With C=0, the transcript is empty and the objective reduces to ideal Bayesian BoN." (Sec 2.3).
- What an evidence action is (Sec 2.3, 5.1): a costed check of a claim ("factor") or of a whole response. "A view may be a crop, mask-guided region, metadata field, structured lookup, or human inspection of the same X." In the benchmark, each open-answer candidate has five slots (modality, anatomical region, view/plane, primary finding, one attribute) and claims are merged across candidates with stance in {-1,0,+1} (the signed candidate-factor matrix B, Eq 4). Costs: "Structured checks have cost 1, ordinary or grounded VLM factor judgments cost 4, and whole-response judgments cost 8. These are design costs rather than measured wall-clock or token costs." (Sec 5.1)
- Objective (Eq 7): maximise E[max_i E[U_i | F, T_pi]] over budget-feasible policies. Ideal value of an action is EVSI_sel(e|f,t) = E_{O_e}[V_sel(f, t+(e,O_e))] - V_sel(f,t) (Eq 9), "the expected change in final selection value rather than claim accuracy or graph degree alone."
- Implemented value (Sec 3.2, Eq 10-11): outcome o maps to a signed candidate effect alpha_ie(o) in {-1,0,+1}; each channel has a pooled outcome mass p_hat_e and a discrimination index kappa(e); update is logit s_i(t+(e,o)) = logit s_i(t) + alpha_ie(o) * logit kappa(e). Plug-in score: EVSI_hat = sum_o p_hat_e(o) max_i s_i(t+(e,o)) - max_i s_i(t). "Feasible actions are ranked by EVSI_hat(e|f,t)/c(e)." Greedy, myopic, stops when budget or estimated value runs out.
- Is it learned? No network is trained. kappa_g and outcome frequencies are fitted per dataset-channel group on the same ledger used for evaluation: "Fitted indices, outcome frequencies, and policy evaluation use the same ledger." (Sec 5.1). The authors' own caveat: "The pooled p_hat_e is not a history-conditioned predictive model" and "s_i is an evidence-updated selection score, not a calibrated posterior probability." (Sec 3.2). Limitations: "The current controller also uses a myopic plug-in EVSI-per-cost rule... Future work should explore learned or multi-step acquisition policies, stronger calibration and stopping rules" (Sec 7).
- Theory: (i) evidence-only gain bounded by sqrt((m/2) * I(U;T|F)) <= sqrt((m/2) Lambda_C) (Eq 15); (ii) factor-code query separation, Q_factor = log2 K vs Q_candidate >= ceil((1-eps)K)-1 (Sec 4.2); (iii) a local proxy D_factor = iota * R_eff / c(e) (Eq 13), which "is a local explanatory proxy... The replay controller does not estimate W_h, R_eff, or iota_e(h)."

### Experiments (Sec 5, App B)
- Four medical-VQA cells, generator Qwen3-VL-30B-A3B, judge Qwen3-VL-235B-A22B, K=16 at temperature 1.1, budgets C in {1,2,4,8,16}, main comparison at C=16. Oracle@K: VQA-Med 82.1, PathVQA 61.5, PMC-VQA 65.1, MedXpertQA-MM 64.7 (Table 1).
- Baselines at C=16: raw BoN majority, random factor acquisition, whole-response judging, BoE, and a non-deployable label-guided myopic allocator.
- Verbatim results: "BoE is 0.26-0.58 percentage points above raw majority across the four cells." Table 2 (pp, 95% interval): VQA-Med BoE-raw +0.26 [-0.47,+0.99], BoE-random +1.11 [+0.43,+1.80], McNemar p=0.0022; PathVQA +0.43 [+0.05,+0.81] / +0.29 [-0.09,+0.68], p=0.16; PMC-VQA +0.58 [+0.19,+0.97] / +0.22 [-0.18,+0.61], p=0.30; MedXpertQA-MM +0.40 [-0.15,+0.95] / +0.35 [-0.20,+0.90], p=0.30. "Only the VQA-Med BoE-random interval excludes zero."
- Rescue on raw-majority failures: "BoE rescues 4.44% of raw failures, compared with 2.45% for random factor acquisition" (VQA-Med); PathVQA "effectively tied with random". MedXpertQA-MM: "only 627 of 1,333 raw failures contain a correct candidate."
- Budget sweep (App B.7, Table 10, MedXpertQA-MM, accuracy %): raw 33.35 constant; BoE 33.35 / 33.30 / 33.55 / 33.45 / 33.75 and random 33.30 / 33.20 / 33.20 / 33.05 / 33.40 at C = 1/2/4/8/16. "BoE-random remains at or below 0.40 points and does not grow monotonically... this does not support a stable MedXpertQA-MM allocation gain." Matched menus (Table 9): BoE factor-only 33.55 vs random 33.40 (+0.15, "three questions", no interval).
- Channel quality limits it: VLM kappa_g 0.502-0.539, grounded 0.505-0.534 (Table 3), i.e. near 0.5 means no update; PathVQA/PMC-VQA BoE "sharpening" is negative (-0.737, -0.276).

### Comparison with PlanDiscrim (our project)
| Aspect | BoE | PlanDiscrim |
|---|---|---|
| Fixed pool of candidates | yes, K=16 sampled answers | yes, K=3-5 candidate trajectories |
| Action | claim/whole-response check, cost 1/4/8 (design costs) | one of 3 perception tools or abstain, at most one call |
| Value of an action | plug-in EVSI/cost from a pooled outcome distribution and a per-channel scalar kappa, same for every instance in a dataset-channel group | learned MLP on geometry features, trained on per-tool expected gain over 8 noise draws, instance-specific |
| Does value depend on how candidates differ | yes, but only through the signed stance matrix B and the current scores (R_eff idea: "a claim can touch many candidates yet have little value if it moves them in a common direction") | yes, through candidate-divergence features |
| Learned | no (fitted scalars on the evaluation ledger) | yes |
| Domain | medical VQA, offline replay of cached outcomes | driving, MetaDrive, injected hazards, 3 noise levels |
| Budget sweep | C in {1,2,4,8,16}, gains <= 0.58 pp, not monotone | accuracy vs query budget Pareto |

### Novelty risk to our project: PARTIAL (conceptual, not empirical)
The claim "spend a budget on checks whose outcome can change which fixed-pool candidate wins, valued by EVSI" is exactly BoE's framing, so we cannot claim the objective is new in general. What BoE does not do: no driving or embodied setting, no learned instance-conditioned value predictor (the authors list it as future work), no trained selector from noise-averaged gain labels, no abstain-vs-tool decision with a safety cost, and its measured gains are small and mostly statistically indistinguishable from random (Table 2). Cite BoE as the closest non-driving analogue and position our selector as the learned, instance-conditioned version of its plug-in EVSI. Its own caution (kappa near 0.5 gives no update; evidence cannot create a missing answer, Oracle@K ceiling) maps directly to our tool-noise levels and to oracle-best-candidate-absent cases.

### Baseline recipe for our MetaDrive setup: "BoE-EVSI plug-in selector"
Inputs we have: K candidate scores s_i from the ranker, per-tool expected gains, tool outcome model.
1. Convert ranker scores to a softmax/logit score s_i^(0) (BoE's cheap prior).
2. For each tool e, define a small outcome set O_e (for the collision check: collision flag per candidate = alpha_ie in {-1,0,+1}; for ROI: hidden-actor revealed yes/no; for depth: near/far). Estimate pooled p_hat_e(o) as the empirical outcome frequency per tool on the TRAIN split only (not test; BoE's reuse of the same ledger is a leak we should avoid).
3. Estimate kappa(e) per tool and noise level on train as the rate at which the outcome agrees with the oracle-best-candidate direction; wt = logit kappa.
4. EVSI_hat(e) = sum_o p_hat(o) max_i s_i(+alpha_ie(o) wt) - max_i s_i; call the tool with the largest EVSI_hat/c(e) if above a threshold tau, else abstain. Sweep tau (or c(e)) for the Pareto curve.
5. Variants: "BoE-pooled" uses dataset-level p_hat and kappa (faithful). "BoE-margin" uses only the ranker margin top1-top2 (degenerate case, equals scene-agnostic uncertainty). This baseline needs no training, only a train-split pass over the existing cached outcomes.
Implementation cost: low-medium (a day, mostly defining alpha_ie per tool).

---

## 2. DriveAgent-R1, arXiv:2507.20879v3 (cs.CV, 20 Apr 2026), Zheng et al. (Tsinghua / Li Auto)

### How it decides to call a tool
- It is not a scene-uncertainty score and not an explicit threshold. The decision is a learned discrete mode token emitted by the VLM: "It first selects a reasoning path by generating either a <think_text> or <think_tool> token." (Sec 2.1). For common scenarios it uses text; "For complex or uncertain scenarios where the initial visual context is insufficient, DriveAgent-R1 generates the <think_tool> token". Input to the decision: only the first frame I_0 (front camera) and T_0 (speed, navigation). It does NOT see candidate trajectories (the output is a 4-step meta-action sequence A=(a_1..a_4), each a=(velocity token, trajectory token), 2 s apart, 8 s total; Sec 2.1). So the trigger is trajectory-agnostic by construction, which is what our project's comparison relies on.
- Once in tool mode: multi-turn loop H_k = H_{k-1} + T_k + I_k, ends on the final action or at the limit K; "limit the maximum number of tool calls to 3" in RL (Sec 3.1.3).
- Training (three stages): (1) Dual-Mode SFT on 4K CoT samples, 2K D_text and 2K D_tool. The label for "tool necessary" is an oracle gap: D_text = scenes where Qwen2.5-VL-3B already gets high accuracy ("e.g., >0.9") without tools; D_tool = of the rest, those where Qwen2.5-VL-72B "yields a significant performance gain over the M_text mode" with tools (App A.4 Step 1). (2) FCM-RL with Mode-Partitioned GRPO: G/2 responses forced to each mode per query, advantages normalised over the pooled group (Sec 2.3.2). (3) AMS-RL: plain GRPO where the model produces the mode token itself.
- Reward (Sec 2.3.3, App A.5): R = R_acc + R_fmt + 1(mode=tool) * R_tool, with R_tool = (R_acc,i - Rbar_acc^text) - N_i * C_tool; "C_tool=0.25/2=0.125" derived as "Minimum Effective Gain": a tool use is justified if it corrects at least one of the 4 meta-actions (accuracy gain 0.25) amortised over a median of 2 calls (range 1-3). Reward "clipped to a fixed range, for instance [-0.2,0.2]". R_acc is a position-weighted Levenshtein score (deletion/insertion cost 0.6); relaxed speed matching gives 0.5 / 0.2 partial credit.
- Tool set (Sec 2.1, App A.2): Retrieve View (any camera, history from a 5-second pool), RoI Inspection (zoom crop of a region), Depth Estimation (depth map), 3D Object Detection (open-vocabulary). All return images/maps that are re-encoded into the VLM context; there is no collision-check tool.

### Verbatim numbers
- Table 1 (Drive-Internal_test, first-frame joint acc / sequence avg joint acc, w/o tools -> w/ tools): DriveAgent-R1 45.27 -> 51.34 (+6.07) and 43.29 -> 45.42 (+2.13); nuScenes_test first-frame 52.58 -> 52.96 (+0.38), sequence 44.43 -> 47.10 (+2.67). Human 49.59 / 49.29 (Drive-Internal), 50.48 / 48.24 (nuScenes). GPT-5 56.30 -> 56.48, 47.19 -> 47.97 on Drive-Internal. Qwen2.5-VL-3B with tools: 24.06 -> 23.64 (-0.42), 24.98 -> 22.63 (-2.35), i.e. tools often hurt untrained models.
- Table 6 (Drive-Internal_test, MSA = mode-selection accuracy, "optimal mode m*_i is defined as whichever mode (M_tool or M_text) achieves higher accuracy for a given sample"): SFT only MSA 45.00; +FCM 56.64; +AMS 57.55; +AMS x2 61.61; full FCM->AMS 68.52. Final forced-mode accuracy 44.97 (tool) / 43.29 (text) / 45.42 (adaptive). So adaptive beats forcing either mode by only +0.45 to +2.13 points and MSA tops out at 68.52% (MSA is a two-class match, tool vs text, so a coin flip would be about 50%; that last comparison is my inference, not a paper statement).
- Table 8 efficiency (single H20, vLLM, batch 1): Passive-SV 8.50 s, 210.77 tokens; M_tool 7.91 s, 314.45 tokens; M_adaptive 6.74 s, 265.57 tokens. Table 7: Retrieve-View-only variant beats Passive-FV by +1.69 and Passive-SV by +1.29.
- Real tool-call frequency or fraction of scenes using tools is not reported in the text I read; I found no number for it. UNVERIFIED if a figure shows it.
- Code: the paper v3 text gives only "Project: https://tsinghua-mars-lab.github.io/DriveAgent-R1/". It says nothing about github.com/Zwc2003/DriveAgent-R1 and nothing about released weights or data (no match for "release" or "open-source" other than a citation). I could not confirm the repo's contents from the paper; the training data (Drive-Internal, 35K clips, 530K VQA pairs) is internal.

### Novelty risk to our project: PARTIAL (low on the core claim)
It is the motivating baseline: trajectory-agnostic, learned from outcome reward, decides tool vs no-tool from the first frame only, never sees candidate plans. It cannot choose which of several tools via a value estimate (the model writes the tool and arguments in text), and it has no budget curve. The "tool necessity by oracle accuracy gap" label (D_tool) is the same idea as our expected-gain label, so reviewers could say our label is a per-tool version of theirs; state that explicitly. Its C_tool shows cost is a fixed per-call penalty, not a sweep.

### Baseline recipe: what a faithful trigger in MetaDrive needs
A true re-implementation (train a VLM with MP-GRPO on MetaDrive) is out of scope. A faithful proxy of its decision rule, which depends only on scene information and not on candidates:
1. Label: for each training decision, "tool needed" = best-tool oracle accuracy minus no-tool accuracy >= margin (their margin idea, with C_tool-style threshold 0.125 in their accuracy units; ours is 1/K-ish decision accuracy, so set the margin by sweep).
2. Features: scene-only (front-frame embedding from the frozen Qwen3.5 cache, ego speed, route command, count/proximity of visible actors, light-state ambiguity flag); explicitly exclude candidate-set features (divergence, ranker margin).
3. Model: logistic regression or small MLP on these, outputting P(tool needed). Trigger = P > tau; sweep tau for the Pareto curve; if triggered call the default tool (or a fixed priority) since DriveAgent-R1 does not rank tools by value. Optionally add a "scene-uncertainty entropy" variant using the ranker's top-1 softmax entropy.
4. Also give it the ablation "VLM asked to emit think_tool vs think_text" (we already have this: Qwen3.5-9B mostly says "none") and cite as zero-shot version.
Implementation cost: low (features exist).

---

## 3. KnowNo ("Robots That Ask For Help"), arXiv:2307.01928, Ren et al.

### Exact conformal construction (Sec 2, 3.1, 3.2)
- Candidates: the LLM generates a set of semantically different next steps; the choice is "formatted as multiple-choice Q&A", labels A-D plus a post-hoc E "an option not listed here". Score: the next-token probability of each letter, f_hat(x~)_y (Sec 2). Rationale: raw sequence probability p(y) "remains highly sensitive to variable-length k", and their Sec A9 shows using p(y) directly "leads to poor performance".
- Calibration set Z = {(x~_i, y_i)}, N pairs, with exactly one correct label each (extension to several acceptable options in their Sec A3). Nonconformity score kappa_i = 1 - f_hat(x~_i)_{y_i} (one minus the confidence given to the TRUE option). q_hat = the ceil((N+1)(1-eps))/N empirical quantile of kappa_1..kappa_N.
- Prediction set: C(x~_test) = {y in Y | f_hat(x~_test)_y >= 1 - q_hat}. Marginal guarantee P(y_test in C) >= 1-eps (Eq 1). They use the dataset-conditional version (Eq 2, Beta inverse CDF): "we use a modest-sized calibration dataset (N=400) and delta=0.01, and adjust eps_hat to achieve the desired 1-eps coverage (with probability 1-delta=0.99 over the sampling of the calibration set)."
- Help rule (Sec 3.2): "If C(x~_test) is a singleton, the robot executes the corresponding plan. Otherwise, we deem the LLM uncertain over possible actions and trigger human help." The human picks from the set or halts if the truth is not in it. Proposition 1: task completion >= 1-eps with prob 1-delta, and (if f_hat models true conditional probabilities) minimal average set size. Multi-step version (Sec 3.3) splits the budget across steps.
- Important for our use: the trigger is a function of the score vector alone (set size > 1). It has no action-value or cost term; "help" is a human and always resolves the ambiguity. In our setting a tool does not resolve it deterministically, and tools have noise.

### Verbatim numbers
- Abstract/contributions: "reducing the amount of help required by 10-24% as compared to baseline approaches."
- Simulation (Sec 4.1): 200 trials per method/setting; eps = 0.15 target (1-eps = 0.85) in Fig 3; eps varied 0.25 to 0.01 for KnowNo and 0.6 to 0.01 for Simple Set/Ensemble Set (Fig 4). "As the scenarios become more ambiguous KnowNo shows a greater reduction of human help compared to Simple Set - as much as 24% at certain success levels." Baselines: Simple Set (cumulative thresholding on the same f_hat), Ensemble Set (frequency over 20 randomised prompts; "requires 20x inference time"), Prompt Set, Binary, No Help. Prompt Set "only achieves 35% task success" in the Spatial setting (Fig A10 caption).
- Hardware multi-step (Table 1, eps=0.25 for KnowNo, Simple Set eps=0.42 tuned to match plan success 0.76): KnowNo set size 1.72, help-step 0.58, help-trial 0.92, task success 0.74; Simple Set 2.04 / 0.72 / 1.00 / 0.72; No Help plan 0.41, task 0.38. Text: "KnowNo reduces the human help rate by 14% step-wise and 8% trial-wise." And "if we set eps=0.25 for Simple Set... step-wise help rate of 87%".
- Mobile manipulation (Table 2, PaLM-2L, 1-eps=0.85, Simple Set eps=0.24): KnowNo plan 0.87, task 0.76, set size 2.22, help 0.67; Simple Set 0.87 / 0.75 / 2.38 / 0.81; No Help 0.62 / 0.51. "KnowNo reduces the human help rate by 14%". GPT-3.5 gives set size 2.50, help 0.86 and "significant MCQA bias towards options D and E".

### Novelty risk: NONE to low
KnowNo decides whether to ask, not which query; it has no cost-aware action choice and no sensing tools. Cite it as the origin of "set size > 1 => ask" and as the template for the future conformal phase.

### Baseline recipe: KnowNo trigger over our K candidates
Per decision i with ranker scores r_1..r_K:
1. Normalise: f_hat_k = softmax(r_k / T) (T fitted on a train fold to minimise NLL; KnowNo uses LLM letter probabilities, we use the ranker). Note the ranker is a trained model, so calibrate on a held-out fold the ranker did not train on.
2. Label y_i = oracle best candidate index (privileged state). If several candidates tie as best, use the multi-correct extension (Sec A3): count a set as covering if it contains any acceptable candidate.
3. Nonconformity kappa_i = 1 - f_hat_{y_i}. q_hat = ceil((N+1)(1-eps))/N quantile on a calibration split (N=400 is enough in their paper; we have more). Set C = {k : f_hat_k >= 1 - q_hat}.
4. Trigger: call a tool iff |C| > 1; abstain (execute the argmax) iff |C| = 1. Sweep eps over (0.01, 0.6) for the budget axis; the realised query rate is the x coordinate.
5. Which tool when triggered: KnowNo has no rule. Use the fixed-priority default, the tool with the highest train-set average gain, or (stronger variant, mention as KnowNo+) the tool with the highest learned gain. Label it clearly as an extension.
6. Variants: Simple Set (cumulative softmax mass >= 1-eps, no calibration) as KnowNo's own ablation.
Cost: low (about 40 lines; needs one calibration split). It is a function of the candidate score distribution only, so it is "candidate-aware but tool-agnostic", the exact middle point between scene-uncertainty and our selector.

---

## 4. UPS, "When to Act, Ask, or Learn: Uncertainty-Aware Policy Steering", arXiv:2602.22474v2 (cs.RO, 12 May 2026), Yuan, Wu, Bajcsy (CMU)

### Exact mechanism (Sec IV)
- Candidates: K action samples from a diffusion policy are rolled out in a latent world model (Dreamer-v3) in an interleaved action/imagination loop, then narrated to text by a VLM (Gemini-3-flash-preview). A (K+1)-th option "none of the above samples are correct" is appended "to ensure the system can detect incapability." The verifier (Gemini-2.0-flash) answers multiple-choice over the narrations; y_t = argmax P_VLM(y | narrations, task) (Sec IV-A). K=10 in calibration (Sec V-A).
- Score shaping before CP (Sec IV-B, Eq 5): P_VLM(y|.) = sum_theta P(y | narrations, theta) P(theta | L), i.e. the VLM first hypothesises hidden user intents with probabilities, then scores options given each intent; marginalised. Reason given: raw likelihoods are "significantly overconfident".
- Nonconformity (Eq 3), sequence-level for sequential decisions: kappa(x_bar, y_bar) = 1 - min_{x_i in x_bar} min_{y in Y*_i} P_VLM(y|x_i), i.e. the minimum probability over the whole sequence and over ALL acceptable labels (conservative: penalises leaving out any suitable option). q_hat = ceil((N+1)(1-eps))/N quantile. Prediction set (Eq 4): C(x) = {y in {1..K+1} : 1 - P_VLM(y|x) <= q_hat}. Theorem 1: P(Y*_i subset of C(x_i)) >= 1-eps.
- Three-way decision (Sec IV-C), verbatim logic:
  - "|C(x)|=1 and K+1 not in C(x)" -> execute the chosen action sample ("confident and capable").
  - "|C(x)|>1" -> "textual clarification question" to the user; the answer replaces the instruction and the loop repeats "until |C(x)|=1".
  - "C(x)={K+1}" (set contains only 'none') -> request a low-level intervention: "the robot randomly selects a trajectory and explicitly asks human supervision to correct potential failures"; corrections train a residual policy with a gating classifier, then the verifier is recalibrated.
  - Not specified in the text I read: a set that contains 'none' plus other options. The three cases above are the only ones given.
- Setup: calibration set of 80 (observation, instruction) pairs, half ambiguous, half straightforward, 1-eps = 0.85; test set 40 samples (Sec V-A). Metrics: coverage, clarification rate, set size.

### Verbatim numbers
- Score comparison (Sec V-A1): the Bayesian-intent score "achieve strong coverage (>=85%) while minimizing the clarification rate" vs Vanilla and CoT; CoT "overestimate ambiguity (leading to near 100% clarification rates)". Numbers are in Figs 3-5 only; not given in text.
- Steering (Sec V-A2, PnP Cup): Forewarn (uncalibrated) improvement "straightforward = 45%, ambiguous = 15%"; UPS with clarification adds "further increasing success rate by 15%".
- Intervention rate (Sec V-B1): PnP Cup UPS 0.06 vs HG-DAgger 0.1 vs EnsembleDAgger 0.16; Insert Block UPS 0.05 vs 0.06 vs 0.26; simulation UPS 0.058 vs 0.20 vs 0.27. EnsembleDAgger = ensemble disagreement above a threshold, so this is an in-paper data point that low-level disagreement triggers over-ask (same direction as BOKBO's warning).
- Re-deployment (Sec V-B2): "15% increase in success rate in ambiguous settings for both hardware tasks"; final success "85%" (sentence truncated in my extract; UNVERIFIED beyond this).
- Evaluation is tiny: 40 test samples per task, 20 trials per condition (Fig 6 caption). Treat all its percentages as high-variance.

### Novelty risk: NONE to low
Same machinery as KnowNo extended with an incapability option and an escalation ladder; the "actions" are human interactions (clarify, intervene), not perception tools, and nothing is chosen by value or cost. The relevant overlap is the three-way outcome from set structure, which prefigures the project's later accept/inspect/replan/fallback policy. Cite for that future phase.

### Baseline recipe (mapping to our K candidates and tools)
1. Same softmax-over-ranker scores as KnowNo, plus a (K+1)-th "none of the candidates is acceptable" score. Obtain it as a learned logit: train a small head on the train fold to predict "oracle-best candidate is unsafe/below threshold" from geometry features; or set it to 1 - max_k p_k renormalised (cheap, uncalibrated).
2. Nonconformity: kappa = 1 - min over acceptable labels of P(y). With ties among near-best candidates (tolerance delta on oracle regret) use all of them as Y*; this is the conservative score and gives bigger sets, i.e. more queries.
3. Decision map (ours): |C|=1, none not in C -> accept top-1, no tool. |C|>1 among real candidates -> call a tool (the "clarify" analogue: the tool is the thing that disambiguates). C={none} -> replan/fallback (not scored in the current open-loop metric; count it as a query or as abstain, state which).
4. Budget axis: sweep eps. Because the tool is chosen by a rule it does not define, use the same "which tool" rule as in KnowNo's recipe.
Cost: low if KnowNo is already built (add one logit and the min-over-acceptable score); the none head adds a small training step.

---

## 5. BOKBO, "Best of K Bad Options: K-Sample Disagreement Tracks Perturbation, Not Uncertainty", arXiv:2605.30660v1 (cs.LG, 28 May 2026), Singh, Happi, Relan, Nair, Baradwaj (Relling Systems; CC BY 4.0)

### The exact warning and its setting
- Setting (Sec 3): VLA test-time scaling for OpenVLA-OFT (primary) and pi0-FAST on LIBERO (libero_object_temp_x0.1 and libero_spatial_temp_x0.1), K=8 candidates made by action-space Gaussian noise a_k = a_0 + sigma*xi_k with sigma in {0.02, 0.05, 0.10, 0.15, 0.20}. Candidate "violation" v(a,o) is an expert-calibrated force threshold (Sec 4.4). Base violation rate 8.6%.
- Warning (Abstract): "the base-policy confidence proxy and K-sample disagreement correlate at 0.98 with the action-noise hyperparameter sigma but at the noise floor with safety violations - they measure the perturbation, not the policy's uncertainty." Sec 5.3 Table 4 (median Spearman, 5 seeds): VLA confidence proxy vs violation -0.053 [-0.071,-0.029], vs sigma 0.981; K-sample disagreement vs violation -0.007 [-0.024, 0.011], vs sigma 0.984; learned violation predictor -0.380 [-0.421,-0.339], vs sigma 0.143.
- Definition of the disagreement score (Sec 4.3): "maximum pairwise L2 distance among candidates, summed across timesteps". Confidence proxy: base-policy log-probability of the chosen chunk, normalised across the K candidates.
- Scope limit, stated by the authors (Sec 4.6, 5.4, Table 5): "The failure is mechanism-specific." Under token-level temperature sampling (diversity from the policy's own stochasticity) free-signal vs violation correlations are -0.247 (confidence proxy) and -0.198 (disagreement), with correlation to the sampling hyperparameter dropping from 0.981 to 0.412 and 0.984 to 0.396. "free signals are partially informative"; the confidence proxy holds the conditional bound on 0.49 of splits "usable, but well below the learned predictor's 0.86". The authors conclude "The learned predictor remains the right choice across both mechanisms."
- Learned predictor (Sec 4.5): MLP 965 -> 128 -> 32 -> 1 on DINOv2 ViT-S/14 features (768 dims), proprio (8), candidate chunk (56), base chunk (56), their difference (56), 5 scalars, 16-dim task embedding; BCE with class-balanced positive weighting (~12:1), retrained per bootstrap split.
- Headline CRC numbers: abstract says "At eps=0.05 on libero_object_temp_x0.1 ... the conditional CRC bound holds on 86% of bootstrap splits with 78% coverage and 70% net task success"; Table 1 (250 cells) lists BOKBO executed violation 0.031, coverage 0.80, net success 0.71 vs no abstention 0.086 / 1.00 / 0.68; Table 6 (50 cells): coverage 0.78, net success 0.70, median executed violation 0.027. These two aggregations differ slightly in the paper itself. Free signals "hold the conditional bound on 15% (VLA proxy) and 12% (K-disagreement) of splits at eps=0.05". Mondrian per-task: min conditional hold 0.71 -> 0.93 (abstract). Splits 500/375/375 (train/cal/test), 5 seeds x 100 bootstraps.

### Implication for us (my reading, not the paper's claim)
Our K candidates are not injected-noise samples; they are short-horizon trajectories from a planner/ranker, so BOKBO's measured failure (correlation 0.98 with sigma) does not transfer automatically. The relevant caution is general: candidate-disagreement (spread of candidates) may track how the candidate set was generated rather than decision difficulty. We should (a) report the correlation of our divergence features with the generator's diversity setting (e.g. lateral-offset or speed-scale grid used to make K candidates) and with oracle regret, and (b) include a "disagreement-only" selector as an ablation. This is also exactly the point where a learned selector on geometry features beats a free disagreement score, which is BOKBO's own conclusion. Paper is from a small industry lab, one benchmark family (LIBERO force-based safety labels), not peer-reviewed as far as the text shows (arXiv preprint).

### Novelty risk: PARTIAL (positioning, not overlap)
It is an execute-or-abstain layer over K candidates with a learned MLP score and conformal risk control. Does not choose among tools. It overlaps with our future calibration phase (CRC on candidate sets) and supports our design choice of a learned predictor over disagreement. Cite for both.

### Baseline recipe: "candidate-disagreement trigger" and "BOKBO-learned trigger"
1. Disagreement trigger: score d = max pairwise L2 distance between candidate trajectories (sum over timesteps), call a tool iff d > tau; sweep tau. Cost: trivial, features exist.
2. BOKBO-style learned trigger: MLP (one hidden layer 128) on [frozen-VLM embedding, ego state, candidate-set features] predicting "top-1 candidate is not the oracle best" (BCE with positive weighting); trigger = predicted risk > tau; if CRC desired, tau = inf{tau : (1/|C|) sum 1[s<=tau and wrong] <= eps - 1/(|C|+1)} on a calibration fold (Eq 2), giving an execute-or-query rule with a finite-sample bound. Note it decides whether to query, not which tool (ours does both).
3. The correlation diagnostic from Table 4 (Spearman vs violation, vs generator parameter) is cheap to replicate.

---

## 6. Ranking of baselines by implementation cost (cheapest first)

| Rank | Baseline | Source | What it needs from us | Cost | Decides which tool? |
|---|---|---|---|---|---|
| 1 | Candidate-disagreement trigger | BOKBO Sec 4.3 | max pairwise L2 between K candidates, threshold sweep | trivial (minutes) | no |
| 2 | Ranker-margin / entropy trigger (scene-uncertainty proxy) | DriveAgent-R1 spirit | softmax margin or entropy of ranker, threshold sweep | trivial | no |
| 3 | KnowNo conformal set (|C|>1) | KnowNo Sec 3.1-3.2 | calibrated softmax on ranker, one calibration split, eps sweep | low (about 40 lines) | no (needs a separate tool rule) |
| 4 | Scene-only learned trigger (DriveAgent-R1 faithful proxy) | DriveAgent-R1 Sec 2.3.3, App A.4/A.5 | train logistic/MLP on scene features only, label = best-tool gain over no-tool above margin; no candidate features | low | no (default tool) |
| 5 | UPS three-way set | UPS Sec IV-B/C | KnowNo plus a (K+1) 'none' logit and min-over-acceptable score | low-medium | no (clarify = tool call) |
| 6 | BOKBO learned risk MLP with CRC threshold | BOKBO Sec 4.1, 4.5 | MLP on embedding plus candidate features, calibration fold | medium | no |
| 7 | BoE plug-in EVSI/cost | BoE Sec 3.2, Eq 10-11 | per-tool outcome sets, train-split outcome frequencies, kappa per tool, signed effect per candidate | medium | yes |
| 8 | Full DriveAgent-R1 (VLM trained with MP-GRPO and R_tool) | DriveAgent-R1 Sec 2.3 | VLM RL training in MetaDrive | very high, not recommended | yes (VLM writes call) |

Recommended minimum set for the Pareto figure: 1 or 2, 3, 4, 7, plus our selector and oracle. Items 3 and 4 bracket our contribution (candidate-aware but tool-agnostic vs tool-aware but candidate-agnostic); item 7 is the strongest non-learned tool-aware competitor and the one reviewers will most likely ask about.

## Caveats
- DriveAgent-R1: text gives only the project page URL (tsinghua-mars-lab.github.io/DriveAgent-R1/); I could not confirm what github.com/Zwc2003/DriveAgent-R1 contains from the paper. I did not fetch the repo (outside this task's text-only brief).
- UPS Fig. 3-6 values are only in figures; I quote only text numbers.
- All arXiv HTML pages were fetched once each; text saved under the scratchpad html_X4 directory.
