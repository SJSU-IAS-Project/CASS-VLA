# L2_listing_t2: arXiv listing sweep, slice t2 (468 titles)

## Summary
- No close overlap found. Nothing in this slice is a driving paper that picks a perception query conditioned on candidate trajectories. The t2 keyword hits are mostly conformal-prediction theory, LLM tool-calling and generic safety filters, with no driving titles at all.
- Closest idea match (not driving): "When to Ask for Help" (2611.06702). A UGV scores its current MPPI rollouts under resolved map hypotheses, picks the map layer with the largest useful improvement, and requests only that aerial measurement. This is planner-conditioned, candidate-rollout-conditioned query selection. It supports the PlanDiscrim thesis in another domain and is a good citation for "uncertainty alone is not enough".
- Expected-gain labels have independent precedents. LAVOIR (2609.30706) trains a single pass encoder on regression of realized expected gain per candidate "slot" and matches a greedy oracle VOI policy. GapSight (2608.21762) builds labels from offline loss gap between global and crop views and distills them into a one-shot router. Both resemble the project's "expected gain" selector targets.
- Candidate-set scoring with calibrated risk and a fallback ladder: 2608.17496 (K candidate action chunks, risk/progress heads, shield, fallback ladder; manipulation, LIBERO-Long). Maps onto the accept/inspect/replan/fallback future phase.
- Online conformal probing (2609.25889) controls the "missed query error" (fraction of cases where probing would have helped) while minimizing probing rate. A usable formulation for the calibration phase.
- Visual-tool "when to call" work (ToolVision, GapSight, OPO) is VQA only, not driving. Useful as the learning recipe for deciding if a tool helps.
- OccludeBench (2610.13790) is a VLM occlusion benchmark of static images, relevant to the claim that VLM prompting mostly fails on hidden objects.

## Papers

### When to Ask for Help: Uncertainty-Triggered Aerial Refinement for Off-Road Navigation
- id: arXiv:2611.06702 | date: 2026-11 | venue: arXiv preprint
- authors: Samineni, Pranay et al. | code: none seen
- relevance: HIGH — planner-conditioned decision of whether and which measurement to request, by scoring the planner's own rollouts; closest conceptual match found in this slice.
- what: UGV evaluates how uncertain map information affects its current MPPI rollouts. If navigation is degraded, it scores the same rollouts under resolved map hypotheses, selects the map layer with largest useful improvement, requests that aerial measurement, fuses it and replans. 180 simulation trials on three routes: 98.9% goal attainment, 87.7% less mean UAV flight time than continuous greedy aerial mapping; each second of UAV flight saves 2.94 s of UGV navigation time.
- thesis use: competitor-in-spirit and supporting evidence that candidate-conditioned acquisition beats uncertainty-only triggering; cite as related work (off-road, not driving).
- verified: abs meta fetched

### LAVOIR: Teaching a Single-Pass Decision Encoder When and What to Ask with Amortized Value of Information
- id: arXiv:2609.30706 | date: 2026-09 | venue: arXiv preprint
- authors: Yilmaz, Furkan et al. | code: none seen
- relevance: MED — amortized expected-gain targets for which query to make, learned in one forward pass; text domain.
- what: Candidate missing-info slots are placed next to the answer options; one pass returns the decision distribution and, per slot, the expected gain in correct-decision probability. Labels come from realized gains averaged over profiles; a Gini cap bounds predicted value. Policy matches a greedy oracle VOI policy (AUC 0.799 vs 0.797); with at most 0.5 questions per conversation it is 14.1 points more accurate than never asking.
- thesis use: idea to borrow (expected-gain regression, oracle-VOI comparison, cap on predicted value); parallel to the MLP selector.
- verified: abs meta fetched

### Learning to Look Again: Loss-Gap Supervision for Free-form Crop Routing in Vision-Language Models
- id: arXiv:2608.21762 | date: 2026-08 | venue: arXiv preprint
- authors: Zhu, Jinchang et al. | code: none seen
- relevance: MED — learned router for whether to take an extra look, trained on offline "did the extra view help" labels.
- what: GapSight compares answer loss or option margin under a global view and crop-augmented views; helpful crops become labels, distilled into a one-shot router that predicts whether to review, expected utility and a crop box. On InternVL2.5-8B the six-benchmark average rises from 52.25 to 64.29, above CropVLM (57.16), ViCrop (55.84), ZoomRefine (54.43).
- thesis use: idea to borrow (label construction from counterfactual with/without-tool outcome); comparable to expected-gain targets.
- verified: abs meta fetched

### Calibrated Predictive Safety for Heterogeneous Robots: An Action-Conditioned JEPA Framework with Model-Based Safety Shields
- id: arXiv:2608.17496 | date: 2026-08 | venue: arXiv preprint
- authors: Zhong, Kaiming et al. | code: none seen
- relevance: MED — K candidate action chunks scored by calibrated risk and progress heads, with a shield and fallback ladder; manipulation, but same decision structure as the future phase.
- what: Proposer gives K candidates; an action-conditioned JEPA rolls each out in a frozen-encoder latent space; calibrated heads score them; a deterministic shield filters inadmissible candidates; a fallback ladder handles empty sets. In 600-episode LIBERO-Long configurations it improved success over a shield-only baseline and reduced collision false negatives at matched recall.
- thesis use: idea to borrow for the accept/replan/fallback phase and for frozen-encoder candidate scoring.
- verified: abs meta fetched

### Risk-Aware Online Conformal State Probing
- id: arXiv:2609.25889 | date: 2026-09 | venue: arXiv preprint
- authors: Talli, Pietro et al. | code: none seen
- relevance: MED — conformal guarantee on whether to probe, with cost (probing rate) minimized.
- what: Online conformal state probing (OCSP) is a joint action and probing policy that provably controls the missed query error (fraction of instances where probing would have been beneficial) while minimizing probing rate; works with pre-trained value-based policies without retraining. Validated in numerical simulation only.
- thesis use: idea to borrow for calibrated tool-call decisions in the future phase.
- verified: abs meta fetched

### ToolVision: Learning When and How to Use Visual Tools with Capability-Aligned Supervision
- id: arXiv:2608.08907 | date: 2026-08 | venue: arXiv preprint
- authors: Mao, Delin et al. | code: none seen
- relevance: MED — RL reward for tool use only on questions where tools give clear benefit (compares with and without tools).
- what: SFT trajectories are ranked by committee-scored stepwise evidence gain; before RL, the learner is compared with and without tools and tool use is rewarded only where it clearly helps. Image VQA, not driving.
- thesis use: idea to borrow (with/without-tool benefit as the training signal); abstract was truncated in my read, so no headline numbers recorded.
- verified: abs meta fetched

### Learning Where to Look: Observation Policy Optimization for Thinking with Images
- id: arXiv:2611.04943 | date: 2026-11 | venue: arXiv preprint
- authors: Wang, Junfeng et al. | code: none seen
- relevance: LOW-MED — credit assignment to zoom (observation) actions, branching at high-uncertainty tool calls.
- what: OPO branches at high-uncertainty, low-redundancy zoom-in events and credits the evidence obtained; notes bounding-box tokens have high generation entropy. Headline numbers were beyond my truncated read.
- thesis use: background on where-to-look learning for the ROI tool.
- verified: abs meta fetched

### OccludeBench: Can VLMs Find What's Missing?
- id: arXiv:2610.13790 | date: 2026-10 | venue: arXiv preprint
- authors: Cekinmez, Jasin et al. | code: none seen
- relevance: MED — occlusion benchmark for VLMs (not driving); VLMs recover hidden objects poorly.
- what: Manually curated benchmark of fully occluded objects, direct (shadow/reflection cue) vs inferential. Across five VLMs accuracy averages 42.7% direct vs 62.7% inferential (20.0-point gap); humans 63.4% vs 68.5%. Extended reasoning and tool use give inconsistent gains; an inpaint-then-confront prompt reduces the gap.
- thesis use: supporting evidence that VLM prompting alone is weak on occlusion; motivates tool calls.
- verified: abs meta fetched

### Certified World Models as Sensing Clocks: Drift-Aware Deadlines for Active Perception
- id: arXiv:2607.01537 | date: 2026-07 | venue: arXiv preprint
- authors: Wang, Hongbo | code: none seen
- relevance: LOW-MED — when to re-sense under a budget with calibrated validity guarantees; synthetic/world-model setting.
- what: Turns a world model's validity horizon into a deadline for no-sensing intervals; drift-aware envelopes carry the guarantee. Reduces eventful-tail violations vs expected-belief scheduling at matched sensing budget in a synthetic theorem-bed; authors report empirical conformal horizons match it in the short-horizon VN-JEPA regime.
- thesis use: theory background for budget-matched sensing schedules.
- verified: abs meta fetched

### Depth or Description? When a One-Step Latent Score Replaces Lookahead in Proactive Information Acquisition
- id: arXiv:2611.07155 | date: 2026-11 | venue: arXiv preprint
- authors: Sengupta, Biswa | code: none seen
- relevance: LOW-MED — one-step score vs lookahead for choosing what to ask; may justify a one-step selector.
- what: A one-step score on the label can miss interactions among answers; a score on a suitable latent that encodes the decision replaces most of the depth at a fraction of the search. No numbers in abstract.
- thesis use: argues for keeping the selector one-step (single tool call) with a decision-aware latent.
- verified: abs meta fetched

### Budget-Constrained Embodied Perception: Four Resource Walls and a Pre-Registered Evaluation of Access-Structured Perception on Open Models at less than 31B
- id: arXiv:2608.22975 | date: 2026-08 | venue: arXiv preprint
- authors: Lin, Defu et al. | code: none seen
- relevance: LOW-MED — query-conditioned budget allocation for frozen multimodal models under a fixed per-decision token budget; synthetic benchmark.
- what: ASP wrapper; under a 4,096-token budget it reaches 75 to 94% episodic retrieval accuracy vs 3 to 19% for equal-budget query-independent sampling on SEW-Bench (synthetic). The authors report the full three-component architecture does not validate.
- thesis use: evidence that query-conditioned allocation beats query-independent at equal budget (same shape as our claim).
- verified: abs meta fetched

## Shortlisted but dropped
- 2607.00218 EgoSafetyBench: egocentric home/factory safety-guard benchmark, not driving; LOW only.
- 2608.08077 Explore, Map, Remember, Decide: VLM spatial memory/evacuation choice, no tool or candidate selection.
- 2611.04006 Controlling Action-Head Co-Adaptation to VLM Representation Anisotropy: frozen-VLM features to action head, but manipulation VLA training trick (AdaIE); marginal.
- 2609.36520 Distilling Privileged CBFs into RGB-Only Safety Filters: privileged-teacher to RGB student, not a query/selection problem.
- 2611.06434 EviSeek: embodied QA evidence seeking, no budgeted candidate-conditioned choice.
- 2609.17296 Conformal Policy Learning, 2610.22930 Conformal Policy Selection: treatment-effect statistics, not planning.
- 2610.19189 Adaptive Computation with Conformal Certification: medical imaging compute savings.
- 2610.02487 Threshold-Aware Conformal Routing: surrogate-vs-simulator routing; interesting generic idea (decision-threshold-aware intervals) but no perception/driving link.
- 2608.20802 SPARC: human motion forecasting conformal tubes, not vehicles.
- 2610.23891 When to Make a Decision: conceptual framework, no results.
- 2610.27350 Refuses When Asked, Complies When Acting: LLM robot safety check, not relevant.
- 2609.26384 Learning to Defer with Guidance: medical imaging L2D.
- 2610.09313 Why VLMs Miss Small Objects, and When Zooming In Is Safe: zoom theory for small objects in documents/images.
- 2609.37345 When to Retrieve, When to Stay: streaming video evidence selection.
- 2610.01698 ActiveWAM: active camera for bimanual manipulation.
- Not fetched, judged from title: 2609.11899, 2609.00291 (video look-deeper routing), 2609.18514 ActiveScale, 2608.02305 and 2610.21919 (active feature acquisition, tabular), 2607.06570 VoI under imprecise probabilities (decision theory).

## Leads not followed
- Active feature acquisition papers (2608.02305 BRiG-AFA, 2610.21919 Lagrangian structure of cost-penalized AFA) may supply cost-aware acquisition theory; titles only.
- 2607.26887 Conformalized Rate-Adaptive Sensing, 2609.25889 cited-by.

---
# Addendum (coordinator follow-up): deep reads, completed abstracts, leads, second pass
All quotes below are from arxiv.org/html text fetched on 2026-11-06 (equations read from MathML alttext). Section labels are the paper's.

## Deep read 1: When to Ask for Help (arXiv:2611.06702, v1, cs.RO, 04 Nov 2026)
- authors: Samineni, Thorpe, Chubick, Balakrishnan, Ellis, Chaudhuri, Topcu | code: project page only, https://anonymous.4open.science/w/when-to-ask-for-help/ (anonymous mirror; no repo link seen)
- How candidates condition the query (Sec. III): the planner (MPPI) emits a rollout population T_t = {tau^(1..K)}. "For each uncertainty source, it constructs a plausible resolved map, rescores the current rollouts under that counterfactual, and measures the resulting change in navigation score." Rollouts, state and goal are held fixed so only the map information changes ("Holding T_t fixed isolates the effect of the modified map information from changes caused by replanning"). So the query choice is conditioned on the candidate set. This is the same structure as ours: score the same K candidates under each possible tool outcome.
- Gain definition (Sec. III, Eq. 3, verbatim from alttext): `\Delta S_t^i = \max_{r\in R_i} \tilde S_t^{i,r} - S_t`, described as "the counterfactual navigation improvement ... the largest improvement in navigation score across the resolved hypotheses evaluated for map layer i". Selection (Eq. 4): among layers with Delta S >= threshold, take the argmax; "If no map layer satisfies [the threshold], no aerial request is issued." Navigation score (Sec. IV): `S_t = (1/K) sum_k 1_k^useful prod_j (1-q_{k,j})` (survival of rollouts against occupancy probability q). Implemented obstacle form (Eq. 6): `\Delta S_t^{obs} = max(S^free, S^occupied) - S^base`, plus a separation test D = |S^free - S^occupied|. The paper itself calls it "an optimistic form of value of information" (Sec. II): a max over hypotheses, not an expectation.
- Query set and cost model: A = {aerial occupancy map, aerial semantic/traversability map} plus the null action; a request names an ROI. Cost is UAV flight seconds (computed analytically from the maps a policy needs). There is no explicit cost term in the decision rule: it is a fixed intervention threshold plus a persistence trigger (score below S_min for N_p consecutive cycles). Only the obstacle layer uses true counterfactual hypotheses; semantic/geometric layers use "rollout-conditioned exposure" (fraction of rollout footprint touching uncertain cells), a heuristic.
- Baselines (Sec. V, Table I, 30 runs per direction per route, 180 total): Ground Only, UAV Counterfactual (ours), Greedy (continuous mapping), Explore then Drive (map first). There is NO scene-uncertainty-only trigger baseline and NO random-query baseline, even though the intro argues against uncertainty alone. There is no budget sweep (a single operating point; thresholds fixed).
- Headline numbers (Sec. V, verbatim): "UAV Counterfactual reaches the goal in 178/180 trials (98.9%), compared with 167 (92.8%) for Ground Only, 179 (99.4%) for Greedy, and 180 (100%) for Explore then Drive." "mean estimated UAV flight time is [..], an 87.7% reduction relative to Greedy and a 75.4% reduction relative to Explore then Drive." Aggregate savings ratios (Fig. 4 caption): "2.94 for Counterfactual, 0.95 for Explore then Drive, and 0.47 for Greedy". HARD route: "mean interventions decrease from 5.32 to 2.87 per trial and goal attainment increases from 48/60 to 60/60." Counterfactual is 10.4% faster than Ground Only in paired total mission time. Table I aggregate: mean UAV flight 31.5 s for counterfactual vs 256.1 s for Greedy.
- Caveats: simulation uses ground truth for localization and aerial maps and analytic UAV time; the field result is qualitative (about 2 km, 563 m route with 9/5/5 candidate requests across three trials).
- Novelty risk vs our project: PARTIAL (idea level), NONE (setting). Same core move (rescore the planner's own candidates under hypothesized tool outcomes, query only if the best-case improvement exceeds a threshold), so we must cite it and avoid claiming the principle as new. It differs in: off-road UGV with map-layer queries, not driving with a VLM and hazards; a max-over-hypotheses gain with fixed threshold rather than a learned selector trained on expected-gain targets over noise draws; no tool-noise levels; no Pareto accuracy-vs-budget evaluation; no uncertainty-only or random baseline. Our contribution stays defensible if we frame it as: learned amortized selector + budget-matched Pareto vs scene-uncertainty and random. Its Greedy-vs-selective result (2.94 vs 0.47 s saved per UAV second) is a useful framing for "cost-efficiency".

## Deep read 2: LAVOIR (arXiv:2609.30706, v1, cs.AI, 25 Sep 2026)
- authors: Yilmaz, Tasdemir, Gozay (independent/GH200 JUPITER compute) | code: https://github.com/moganai/lavoir (Apache-2.0); weights https://huggingface.co/moganai/lavoir (CC BY-NC 4.0) (Code and Data Availability section)
- How candidates condition the query: Sec. 4 (Input): the sequence is `[CLS] choice: ... [SEP] [MASK] opt1 [MASK] opt2 ... [SEP] missing information: [MASK] slot1 [MASK] slot2 ... [SEP] state`. Answer options (the candidate decisions) and the askable slots sit in the same encoder pass; the VOI head reads each slot marker and also gets features of the decision distribution f(p) (max prob, top-2 margin, entropy/log m, m/255). So per-slot value is conditioned on the option set and its current posterior, the analogue of "conditioned on how candidates diverge", but here options are text labels, not trajectories.
- Gain definition (Sec. 3, Eq. 2, verbatim): `VOI*(k|E) = E_{theta~P(.|E)} E_{a~A_k(.|theta)} [ P(g(theta) | E (+) a) ] - sum_y P(y|E)^2`, "the expected increase in the probability of the correct unit". Training target (Introduction): "least-squares regression on the realized gain p_k(y*) - p_0(y*) estimates the expected gain, an amortized value of information". Predicted value (Eq. 3): `v_k = G(softmax(z/T)) * sigmoid(h_k)`, G = Gini impurity of the model's posterior (Proposition 1: VOI* <= Gini). Policy (Sec. 3): ask about argmax_k v_k if v_k > c and fewer than Q questions asked; else hand off if 1-max p > c_h; else decide.
- Query set and cost model: slots of a schema (decisive and non-decisive), each asked at most once; cost is a scalar per-question threshold c, swept (c in {.02,.05,.1}); at most Q=2 questions; handoff threshold c_h. Answers come from a profile-based simulator.
- Baselines and sweeps (Sec. 6, Policies): "B2 never asks; B3 asks about a random unresolved slot when max_y p_y [is below a threshold]; B5 asks about the highest-VOI slot when the prediction set ... contains more than one unit" (uncalibrated conformal-style trigger); VOI (ours); ORACLE = greedy exact VOI*. So there IS an uncertainty-triggered random baseline (B3), an uncertainty-triggered-set baseline (B5), a never-ask baseline and an oracle. There IS a budget sweep: c, tau, c_h are swept and reported as accuracy vs mean questions (AUC over 0 to 2 questions, and b0.5 = best accuracy at <= 0.5 questions).
- Headline numbers (Sec. 7.1, verbatim): "With group temperatures the VOI policy reaches an AUC of 0.799-0.800 against 0.800-0.803 for ORACLE, with rho=0.82-0.83 and 88-92% top-1 agreement. With at most 0.5 questions per conversation it is 12.9-14.4 points more accurate than never asking (B2) and 7.2-9.5 points more accurate than asking at random when uncertain (B3)." "B5 ... AUC is 0.008-0.009 lower." Zero-shot schemas: VOI still beats baselines (AUC 0.02-0.05 above B5) but decisions weak: "0.51-0.52 accuracy against a ceiling of 0.667". Sec. 7.2 / abstract: ABCD real conversations +8.3 points where it asks; SGD asking rate 93% to 8.6% with the Gini cap. Abstract: 31 ms median latency on GH200.
- Caveats: text/dialogue domain; synthetic LLM-verbalized data; single seed; the oracle is greedy one-step and shares the model's own decision head so it is "a strong reference rather than an upper bound".
- Novelty risk vs our project: NONE for the claim (no perception, no trajectories, no driving), but PARTIAL for method novelty of two pieces: (a) amortized expected-gain regression for query selection with an oracle-VOI comparator and rank agreement (Spearman rho, top-1), (b) the Gini-style cap that makes predicted value vanish when the decision is already certain. We should cite it as the closest prior for "learn a per-query expected-gain head, compare to oracle VOI, report accuracy vs questions". Worth borrowing: report rho/top-1 agreement vs the oracle selector, and a posterior-based cap on predicted gain (ours could use the ranker's top-2 margin).

## Completed abstracts (full text read)
### ToolVision (arXiv:2608.08907; cs.CV; Aug 2026; code: promised, "We will publicly release the datasets and source code"; Sec. H.1 describes a code/data package with 4,057 SFT examples and 24,921 RL questions, no URL seen)
- Verbatim ending of the abstract: "ToolVision-8B improves over its base on all seven main benchmarks, surpasses Thyme-7B, CodeVision-8B, and CodeDance-7B on all three high-resolution benchmarks, and outperforms Qwen3-VL-32B-Thinking on V * and HRBench 8K."
- Sec. 4.3: largest gains over base Qwen3-VL-8B-Thinking are "MME-RealWorld-Lite (+12.7), MME-RealWorld-CN (+11.3), and HRBench 4K (+9.0)"; ArxivQA-2k +16.2; FSC-147-test MAE reduced 74%. The "necessity" signal (Sec. 3.3, "Measuring Tool Necessity") is a with/without-tool accuracy comparison per question, the closest analogue to our counterfactual "tool helps" label. Image VQA only. Relevance MED stands.

### OPO, Observation Policy Optimization (arXiv:2611.04943; cs.CV; 03 Nov 2026; code: https://github.com/Yann0122/Observation-Policy-Optimization)
- Verbatim remainder of the abstract: "Second, Evidence-Localized Advantage Attribution (ELAA) compares sibling branches using local evidence-sufficiency rewards and assigns credit only to the corresponding observation-action tokens. By decoupling observation-action optimization from trajectory-level outcome supervision, OPO improves visual evidence acquisition and further enhances visual reasoning performance. Experiments show that OPO consistently improves Qwen3-VL models across scales and achieves competitive performance against larger models and tool-augmented baselines. Code is publicly available."
- Sec. 5.2: OPO-2B gains +10.0 (V*), +12.4 (HR-Bench 4K), +15.8 (HR-Bench 8K); OPO-8B gains +4.7, +4.1, +4.3; OPO-8B reaches 92.7% on V* and 85.5% on HR-Bench 4K, 80.8% on HR-Bench 8K (from 76.5%). Zoom-in only, no query budget. Relevance LOW-MED stands.

## Leads fetched (abs meta fetched)

### BRiG-AFA: Bellman Risk-to-Go Learning for Non-Myopic Active Feature Acquisition
- id: arXiv:2608.02305 | date: 2026-08 | venue: arXiv preprint
- authors: Feng, Jiaorong et al. | code: none seen
- relevance: MED — "candidate-conditioned risk-to-go function for every remaining budget", supervised alternative to RL for budgeted acquisition.
- what: Learns a separate candidate-conditioned risk-to-go function per remaining budget, fitted backward with Bellman targets from the one-step terminal classification risk; inference greedily minimizes the learned risk. Fashion-MNIST with 20 candidate pixels: +10.20 +/- 0.74 points at four acquisitions; mean paired gain across budgets {2,4,8,12,16} is 3.50 +/- 0.37 points. Three-seed MiniBooNE mixed at small budgets. Tabular/pixel features, not perception tools.
- thesis use: idea to borrow if we move beyond one-step (we allow only one call, so non-myopic gains do not apply); cite as AFA context.
- verified: abs meta fetched

### The Lagrangian Structure of Cost-Penalized Active Feature Acquisition
- id: arXiv:2610.21919 | date: 2026-10 | venue: arXiv preprint
- authors: Bingham, Joseph | code: none seen
- relevance: LOW-MED — theory for "gain minus lambda*cost" greedy acquisition.
- what: Shows EIG-Cost (expected information gain minus cost penalty) is one-step greedy optimization of the Lagrangian relaxation of expected-cost AFA, lambda as dual multiplier; gives an a-posteriori certificate. Verified Del_lam near zero across 4,000 solved small instances; for equal costs proves Del_lam <= exp(-gamma * I(Y;X_[d])).
- thesis use: justification for a cost-penalized selector (select tool if gain - lambda*cost > 0) and for sweeping lambda to trace the Pareto curve.
- verified: abs meta fetched

### Conformalized Rate-Adaptive Sensing (CoRAS)
- id: arXiv:2607.26887 | date: 2026-07 | venue: arXiv preprint
- authors: Yang, Jiawei et al. | code: none seen
- relevance: LOW — conformal stopping-time bound for how many measurements to take; imaging.
- what: Calibrates an early estimate of the stopping time (first rate at which reconstruction error falls below a target) with marginal and approximate conditional coverage; uses fewer measurements than fixed-rate stopping and assigns more to harder images. No numbers in abstract.
- thesis use: weak analogue for a conformal "enough sensing" rule in the calibration phase.
- verified: abs meta fetched

## Second pass: additional VOI / acquisition / when-to-query papers (abs meta fetched)

### Agents' Last Doubt: Knowing When to Act and When to Step Back in Tool-Using Agents
- id: arXiv:2610.24194 | date: 2026-10 | venue: arXiv preprint
- authors: Liu, Qisai et al. | code: none seen
- relevance: MED — counterfactual outcome dataset over every legal action at each decision point (act, gather information, escalate), with a learned action-selection controller; accuracy vs interaction cost.
- what: Builds 3,115 action outcomes from 1,036 decision points in ToolSandbox by executing each legal action; trains SURE-Act to select actions for a frozen backbone agent. Learning to rank beats a regression-only baseline by 0.0309 offline utility; end-to-end gains of up to 0.0575 (abstract truncated in my read).
- thesis use: idea to borrow (execute every candidate query to build counterfactual labels, rank rather than regress); same labeling recipe as our noise-averaged expected-gain targets.
- verified: abs meta fetched

### Learning to Ask: Information Acquisition for SLM-LLM Collaboration, under a budget
- id: arXiv:2610.01236 | date: 2026-10 | venue: arXiv preprint
- authors: Kim, Yongjun et al. | code: none seen
- relevance: MED — learns whether to call an external advisor, how to formulate the query, under an API budget; performance-cost tradeoff vs routing baselines.
- what: Three-stage RLVR framework; improves the performance-cost tradeoff and in some settings matches or exceeds oracle problem-level routing on math and coding.
- thesis use: baseline pattern (oracle routing as reference); text domain.
- verified: abs meta fetched

### When Should Active RAG Retrieve? A Budget-Aware Evaluation of Utility, Calibration, and Cost
- id: arXiv:2607.24010 | date: 2026-07 | venue: arXiv preprint
- authors: Qian, Pin et al. | code: none seen
- relevance: MED — evaluation methodology: retrieval is valuable only through its marginal correctness change over no-retrieval; exact top-k utility frontiers, calibrated threshold frontiers, conservative budget frontiers.
- what: Argues single-point comparisons conflate a looser budget with a better policy; separates whether trigger scores rank useful decisions, whether thresholds calibrated on past data meet future budgets, and trigger-side cost.
- thesis use: evaluation protocol to borrow (report realized budget, not nominal; oracle top-k frontier as the upper bound on the Pareto plot).
- verified: abs meta fetched

### AdaTurn: Budget-Aware Test-Time Scaling for Active Visual Perception Agents
- id: arXiv:2607.14547 | date: 2026-07 | venue: arXiv preprint
- authors: Liang, Susan et al. | code: none seen
- relevance: LOW-MED — conditions an active-vision agent on a turn budget; accuracy at low budgets.
- what: FA-DAPO turns the over-budget event into a trainable forced-answer step; raises VisualProbe-Medium from 36.7% to 47.6% at four turns.
- thesis use: budget-conditioned policy and accuracy-vs-budget reporting precedent.
- verified: abs meta fetched

### StreamScout: Learning When to Look Deeper for Streaming Video Understanding
- id: arXiv:2609.00291 | date: 2026-08 | venue: arXiv preprint
- authors: Zhang, Ce et al. | code: none seen
- relevance: LOW-MED — stop-or-escalate cascade over three increasingly costly visual views; supervision distilled from a probe of the model's competence boundary.
- what: On OVO-Bench StreamScout-S improves Qwen3-VL-8B by 14.65 points while using 59% fewer tokens than uniform sampling.
- thesis use: label recipe (probe the cascade offline, distill into a router) parallel to GapSight and ours.
- verified: abs meta fetched

### Active feature acquisition set (low priority, abs read)
- 2609.32301 SynAFA (PID-based pair acquisition): strongest gains at low budgets on PhysioNet, significantly worse than nearly all baselines on MiniBooNE; cautionary: local information objectives poorly aligned with predictive utility. LOW.
- 2609.32325 AFA with incomplete training data: one-step acquisition values unchanged under MCAR, multi-step values can decrease; code github.com/Linusaronsson/AFA-Benchmark (missing-data branch). That benchmark repo could be a harness for acquisition baselines. LOW.
- 2608.24087 Knowing When to Ask for Help (Bayesian self-escalation, optimal stopping over a competence posterior; regret decays as 1/sqrt(n) with n calibration trajectories): LOW, LLM delegation.
- 2609.37687 WISE-ATTA and 2610.28409 (budget-aware multi-turn reward shaping, Qwen3.5 4B/9B on AppWorld and BabyAI): LOW, not perception.
- 2610.40030 Cheap Retrieval and Observation Credit Assignment: VoI lower bound on acquiring action's value, memory in RL; pilot only. LOW.

## Updated Summary
- Overlap with the project: no paper in t2 does candidate-conditioned perception-tool selection for driving. The nearest, 2611.06702 (UGV rescoring its own MPPI rollouts under resolved map hypotheses, query only if best-case score gain exceeds a threshold), shares the core mechanism; novelty risk is partial at the principle level and none at the setting level. It has no uncertainty-only or random baseline and no budget sweep, which is exactly the comparison PlanDiscrim reports. Cite it, and note its gain is a max over hypotheses with a fixed threshold rather than a learned expected-gain selector.
- LAVOIR (2609.30706) is the closest precedent for the learned-selector side: amortized expected-gain regression per candidate query, evaluated as accuracy vs mean questions against never-ask, random-when-uncertain, an uncalibrated prediction-set trigger and a greedy oracle (AUC 0.799 vs 0.797 oracle; +7.2 to 9.5 points over random at <= 0.5 questions). Text domain only. Borrow: rho/top-1 agreement with the oracle selector and a certainty cap on predicted gain.
- Label construction by "run each option and see what helped" recurs: ToolVision (with/without-tool necessity), GapSight (loss gap global vs crop), SURE-Act (execute every legal action), StreamScout (probe the cascade). Our noise-averaged expected-gain targets are in the same family, which makes them easy to defend.
- Evaluation hygiene: 2607.24010 argues for realized-budget and oracle top-k utility frontiers, not single-point accuracy; adopt for the Pareto plots. AFA theory (2610.21919) justifies sweeping a cost multiplier to trace the curve; non-myopic AFA (2608.02305) is moot with a single-call limit.
- Calibration phase: 2609.25889 (missed-query-error control while minimizing probing rate) and 2608.17496 (K candidates, calibrated risk heads, shield, fallback ladder) are the templates.
- Domain gap persists: all of these are text, VQA, manipulation or off-road navigation. A driving-specific candidate-conditioned query paper has not appeared in this slice of Jul-Nov 2026 listings, but the t2 keyword filter did not surface driving titles at all, so absence here is weak evidence.
