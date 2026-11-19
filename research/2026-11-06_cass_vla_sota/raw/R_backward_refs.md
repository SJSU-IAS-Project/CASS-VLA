# R_backward_refs: references and related-work themes of the six closest papers

Source texts: arxiv.org/html for 2610.09520, 2609.35910, 2611.06702, 2602.10719, 2604.14251, 2607.20950 (all read, bibliographies parsed: 57, 33, 32, 43, 24, 47 entries). Entries below were absent from papers.csv and raw/*.md at 23:35 PST on 2026-11-06 unless noted.

## Summary
- No new close overlap turned up in the reference lists. The closest papers are the six themselves, and all six are already recorded (SIGMA, When to Ask for Help, DualDriveVLA and CTD in papers.csv; DEEP and Best-of-Evidence in raw/X1, X4, Y, Z). What the lists add is the lineage they all share: value of information, planner-conditioned relevance, and cost-budgeted escalation.
- Most important pattern: three of the six define the value of a query by its effect on the downstream decision. SIGMA calls it expected planning gain (EPG) via simulation-in-the-loop. DEEP defines decision value as change in downstream loss and judges allocators against a budget-constrained oracle. 'When to Ask for Help' rescored the current MPPI rollouts under counterfactual map resolutions and calls the UAV request "an optimistic form of value of information" (its own words). Our expected-gain target belongs to this family; the differentiator that stays is conditioning on a discrete candidate set with a VLM/tool query in driving.
- Planner-centric perception metrics are the shared ancestor of that idea and were not recorded: Philion et al. (PKL, 2004.08745), Ivanovic and Pavone (2110.03270), Li and Yang (2306.07276, previously noted but not fetched), Antonante et al. (task-aware risk, 2305.01870). All fetched here as MED.
- For the future calibration phase: CTD stands on Learn then Test (2110.01052) and Pareto Testing (2210.07913); Kiyani et al. (2602.17633) give an accept/reject/defer policy with a two-threshold structure and online error control. That matches the planned accept/inspect/replan/fallback policy.
- For evaluation design: DEEP's closest structural neighbours are budget-adaptive routing (2606.30919) and ORIC edge offloading (2410.18919). Both pick inputs by predicted gain under a budget, but the gain is detection quality. DEEP states that perception gain and decision value disagree in sign on 25-51% of nuScenes frames where both are non-zero; useful as a motivation sentence for choosing decision accuracy.
- Best-of-Evidence's lineage (generate-rank-verify 2605.17609, active feature acquisition 2010.02433, epistemic throughput 2602.09127, TIM-PRM 2511.22998, LLM-as-a-Verifier 2607.05391) is about picking which costly check to run over a fixed candidate pool, outside driving. It is the nearest non-driving analogue of candidate-conditioned querying.
- Older and robotics-side foundations (Howard 1966, Russell and Wefald, Oliver and Horvitz, Bajcsy, Reece and Shafer on perceptual attention in robot driving) are cited by DEEP and are worth a one-line citation each; I could not verify abstracts for them.
- The DualDriveVLA, SIGMA (edge-cloud half) and CTD (LLM-routing half) bibliographies are mostly outside scope. About 60% of SIGMA's list is edge computing or mobile networking. No further driving tool-agents or trajectory critics appeared there beyond what the scan holds.

## How each source paper positions itself (related-work themes)
| Paper | Themes in its related work | Gap it claims |
|---|---|---|
| SIGMA 2610.09520 | (A) perception-level uncertainty estimation and calibration; (B) motion planning under perception uncertainty, including informative planning and forward-simulation exploration; (C) fast-slow / cloud-edge collaborative driving and LLM/VLM driving agents; (D) a positioning table against collaborative perception and edge-cloud scheduling | Uncertainty is treated by magnitude and invocation by heuristic triggers; nobody asks whether resolving it changes the planning outcome (EPG criterion) |
| DEEP 2609.35910 | (1) adaptive inference and task-aware computation; (2) selective offloading and routing (weak vs strong detector, LLM routing, selective prediction, deferral); (3) planning-aware perception evaluation; (4) value of information and computation (Howard, metareasoning, active perception, selective perception) | Existing allocators value perception gain; DEEP values the marginal change in downstream decision loss, acted on before escalation |
| When to Ask for Help 2611.06702 | Field autonomy (off-road); air-ground teaming; collaborative navigation and mapping; counterfactual navigation; value of information and asking for help | Prior work gathers aerial data beforehand or triggers on uncertainty; this one scores planner rollouts under counterfactual resolutions and calls the UAV only if the plan improves |
| DualDriveVLA 2602.10719 | VLMs for driving (dual-system vs single-system); diagnosing VLM/VLA stacks (interpretability, benchmarks) | Few mechanistic studies of why VLM and vision-only branches differ and how to select between them at trajectory level |
| Calibrate-Then-Delegate 2604.14251 | Latent probes for safety monitoring; calibrated cascades and risk-controlled delegation (LTT, Pareto testing, cascaded judges, weak-strong verification); LLM routing and model cascades | Value-based instance-level routing with finite-sample control of the expert-call budget instead of fixed top-k quotas |
| Best-of-Evidence 2607.20950 | Candidate-level test-time selection (BoN, PRMs, adaptive generate-rank-verify); grounded verification and budgeted acquisition (tools, VoI, active feature acquisition, submodularity, group testing); medical VQA benchmarks | Evidence is attached to candidates; BoE treats a shared claim as the verification unit and spends a budget by estimated selection value |

Theme overlap worth noting: DEEP, SIGMA and 'When to Ask' all include a "perception/uncertainty is not the same as decision relevance" paragraph; CTD and DEEP both include a routing/cascade paragraph; none of the six has a paragraph on tool-calling driving VLMs (DriveAgent-R1 and its kin), so that cluster is positioned only by the scan.

## Papers
### Learning to Evaluate Perception Models Using Planner-Centric Metrics (PKL)
- id: arXiv:2004.08745 | date: 2020-04 | venue: arXiv preprint (CVPR 2020 per DEEP bibliography)
- authors: Philion et al. | code: project page given in abstract
- relevance: MED — foundational: scores perception by its effect on a downstream planner (the origin of 'relevance defined by plan change').
- what: Proposes a detection metric that measures the impact of detections on the downstream driving task; the abstract says humans side with the metric 79% of the time on scenes where standard metrics disagree. It downweights detections by distance and speed.
- thesis use: Cite as the root of plan-conditioned relevance; the same idea as the Planning-KL ranking in 'What's Hidden Matters' (already in the scan) and as the expected-gain target.
- verified: abs meta fetched

### Injecting Planning-Awareness into Prediction and Detection Evaluation
- id: arXiv:2110.03270 | date: 2021-10 | venue: IEEE IV 2022 (per DEEP bibliography)
- authors: Ivanovic, Pavone | code: none seen
- relevance: MED — task-aware metrics for detection and prediction based on effect on planning.
- what: Argues accuracy metrics (IoU, displacement error) are task-agnostic and gives planning-aware metrics on simulation and real driving data.
- thesis use: Related-work anchor for 'relevance should be measured by the decision, not by perception accuracy'.
- verified: abs meta fetched

### Task-Aware Risk Estimation of Perception Failures for Autonomous Vehicles
- id: arXiv:2305.01870 | date: 2023-05 | venue: RSS 2023 (per DEEP bibliography)
- authors: Antonante et al. | code: NVlabs 'persevere' (from search, not checked)
- relevance: MED — risk of a perception failure measured by its effect on the motion plan; PAC bounds.
- what: Task-aware risk estimator: a failure that does not affect the plan has low risk, a benign-looking one that does has high risk. Evaluated on nuPlan (abstract wording only, I did not read the numbers).
- thesis use: Idea to borrow for the future calibrated accept/inspect phase (plan-conditioned risk with PAC bounds). Also the risk-side counterpart of candidate-conditioned querying.
- verified: abs meta fetched

### Transcendental Idealism of Planner: Evaluating Perception from Planning Perspective for Autonomous Driving
- id: arXiv:2306.07276 | date: 2023-06 | venue: ICML 2023 (per DEEP bibliography)
- authors: Li, Wei-Xin et al. | code: none seen
- relevance: MED — models the planner as expected-utility maximiser and measures how perception noise changes its objective.
- what: Principled framework for the impact of perceptual error on planning, using expected utility maximisation over a world-state description.
- thesis use: Theory framing for why tool noise should be judged through the ranker. Already named as 'not fetched' in raw/ notes; now fetched.
- verified: abs meta fetched

### Efficiently Controlling Multiple Risks with Pareto Testing
- id: arXiv:2210.07913 | date: 2022-10 | venue: ICLR 2023 (per CTD bibliography)
- authors: Laufer-Goldshtein et al. | code: none seen
- relevance: MED — conformal-style calibration of several risks at once, optimising cost; used by Calibrate-Then-Delegate.
- what: Two-stage method: find the Pareto frontier of settings, then run statistical testing only on that frontier to meet several risk constraints while optimising other objectives (run time vs error in the abstract).
- thesis use: Idea for the future phase: calibrate the query-budget threshold and the accuracy risk together. Pair with Learn then Test.
- verified: abs meta fetched

### Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control
- id: arXiv:2110.01052 | date: 2021-10 | venue: arXiv preprint (AoAS per general knowledge; UNVERIFIED venue)
- authors: Angelopoulos et al. | code: none seen
- relevance: MED — the risk-control framework that CTD builds on; foundation for the project's conformal risk control phase.
- what: Reframes risk control as multiple hypothesis testing and gives finite-sample guarantees without refitting; worked examples in vision and tabular data.
- thesis use: Cite for the calibration phase. Closer to our needs than plain conformal prediction because the risk is a task loss.
- verified: abs meta fetched

### When to Trust the Cheap Check: Weak and Strong Verification for Reasoning
- id: arXiv:2602.17633 | date: 2026-02 | venue: arXiv preprint
- authors: Kiyani et al. | code: none seen
- relevance: MED — optimal two-threshold accept/reject/defer policy for cheap vs costly verification, with online error control.
- what: Formalises weak-strong verification policies that accept or reject on the weak signal and defer to strong verification otherwise. Shows optimal policies have a two-threshold structure and gives an online algorithm controlling acceptance and rejection errors.
- thesis use: Matches the future accept/inspect/replan/fallback policy: two thresholds on a calibrated score, with the strong check as the tool call.
- verified: abs meta fetched

### Active Feature Acquisition with Generative Surrogate Models
- id: arXiv:2010.02433 | date: 2020-10 | venue: ICML 2021 (per BoE bibliography)
- authors: Li, Oliva | code: github lupalab/GSMRL (from search)
- relevance: MED — sequential acquisition of costly features as an MDP; classic reference for 'which observation to buy'.
- what: Treats active feature acquisition as an MDP and uses a generative surrogate model to estimate information gain from each acquisition as reward.
- thesis use: Background for the selector: a learned acquisition policy with expected-gain rewards. The raw/ files already hold newer AFA papers; this is the older anchor.
- verified: abs meta fetched

### Adaptive Generate-Rank-Verify: Inference-Time Search with Costly Verification
- id: arXiv:2605.17609 | date: 2026-05 | venue: ICML 2026 (per search result, not checked on the abs page)
- authors: Dughmi, Haghifam, Kalayci | code: none seen
- relevance: MED — cheap score then costly verifier, with an adaptive policy for how many candidates to verify; candidate set plus budget.
- what: Models cheap reward + expensive verifier as cost-sensitive first-positive search, characterises the optimal policy by dynamic programming when distributions are known, and gives an online policy (ADAP) when they are not. Tested on maths and code.
- thesis use: Structural analogue: choose which of K candidates to spend a costly check on. Best-of-Evidence cites it in the same cluster.
- verified: abs meta fetched

### AVIS: Adaptive Test-Time Scaling for Vision-Language Models
- id: arXiv:2606.11576 | date: 2026-06 | venue: arXiv preprint
- authors: Jeddi et al. | code: avis-vlm.github.io (from search)
- relevance: LOW/MED — per-query policy that sets visual context and reasoning compute for a VLM.
- what: Learns a lightweight policy that adapts both visual token pruning and number of reasoning rollouts per query, to improve the accuracy-compute trade-off.
- thesis use: Related work on adaptive VLM compute; not about perception tools or candidates.
- verified: abs meta fetched

### LLM-as-a-Verifier: A General-Purpose Verification Framework
- id: arXiv:2607.05391 | date: 2026-07 | venue: NeurIPS 2026 (per search listing, not checked)
- authors: Kwok et al. | code: none found
- relevance: LOW/MED — continuous verifier scores from token-logit expectation; includes a robotics reward benchmark.
- what: Computes expected score from logit distributions and scales verification by granularity, repetition and criteria. The search snippet cites RoboRewardBench; I did not read the table.
- thesis use: Possible cheap way to turn the frozen VLM into a candidate scorer instead of asking it to pick a tool (prompting currently says 'none').
- verified: abs meta fetched

### Budget-Adaptive Routing: Skipping the Weak When the Strong Answers Anyway
- id: arXiv:2606.30919 | date: 2026-06 | venue: Workshop on Networks for AI Computing (NAIC '26) per DEEP bibliography
- authors: Geng, Mohan, Ott | code: none seen
- relevance: MED — routing/offload estimator under a varying budget; closest structure to an equal-budget Pareto comparison.
- what: Weak-skipping estimator from raw pixels (0.153 GFLOPs, about 29x lighter than the weak detector, per abstract) and a router that chooses between weak-skipping and weak-conditioned placement by offload budget. Evaluated as an accuracy-compute frontier.
- thesis use: Evaluation template: compare allocators along the whole budget curve and charge the allocator for its own cost.
- verified: abs meta fetched

### Optimizing Edge Offloading Decisions for Object Detection (ORIC)
- id: arXiv:2410.18919 | date: 2024-10 | venue: IEEE/ACM SEC 2024
- authors: Qiu et al. | code: github qiujiaming315/edgeml-object-detection (from search)
- relevance: MED — per-image reward for offloading, estimated before offloading, selected under a budget.
- what: ORIC estimates the accuracy gain from offloading an image using only local detection results, then offloads images under a budget.
- thesis use: Same allocation structure as our selector (predicted gain, fixed budget) but the gain is perception accuracy, not a decision. DEEP uses it to make exactly this contrast.
- verified: abs meta fetched

### Inference Offloading for Cost-Sensitive Binary Classification at the Edge (H2T2)
- id: arXiv:2509.15674 | date: 2025-09 | venue: AAAI 2026
- authors: Moothedath et al. | code: github vnmo/H2T2-AAAI-2026 (from search)
- relevance: LOW/MED — two-threshold online offloading policy with sublinear regret.
- what: Adapts a pair of thresholds on local-model confidence online to decide when to offload at a cost, with regret bounds.
- thesis use: Scene-uncertainty-threshold baseline family with a theory behind it; supports the framing of the scene-uncertainty baseline.
- verified: abs meta fetched

### Consistent Estimators for Learning to Defer to an Expert
- id: arXiv:2006.01862 | date: 2020-06 | venue: ICML 2020
- authors: Mozannar, Sontag | code: none seen
- relevance: LOW/MED — classic learning-to-defer formulation: classifier plus rejector.
- what: Learns a predictor and a rejector from expert decisions via a consistent surrogate loss for cost-sensitive learning.
- thesis use: Foundational citation for 'selector learns when to defer'.
- verified: abs meta fetched

### Bridging Large-Model Reasoning and Real-Time Control via Agentic Fast-Slow Planning
- id: arXiv:2604.01681 | date: 2026-04 | venue: arXiv preprint
- authors: Chen, Jiayi et al. | code: none seen
- relevance: LOW/MED — SIGMA's own earlier fast-slow system; VLM detector on the vehicle and LLM in the cloud.
- what: Perception2Decision compresses scenes with an on-vehicle VLM and maps them to directives in the cloud; Decision2Trajectory converts directives into paths; MPC tracks. Tested in CARLA under perturbations.
- thesis use: Background for SIGMA's group. Already cited in raw/A; listed here for completeness.
- verified: abs meta fetched

### Learning-based Methods for Adaptive Informative Path Planning
- id: arXiv:2404.06940 | date: 2024-04 | venue: Robotics and Autonomous Systems 179 (2024) per search
- authors: Popovic, Ott, Rückin, Kochenderfer | code: none
- relevance: LOW/MED — survey of choosing where to sense next with learned policies (AIPP).
- what: Gives a unified mathematical framework for adaptive informative path planning and two taxonomies of learning-based methods.
- thesis use: Active-perception survey to cite instead of reinventing the framing. Cited by SIGMA.
- verified: abs meta fetched

### Epistemic Throughput: Fundamental Limits of Attention-Constrained Inference
- id: arXiv:2602.09127 | date: 2026-02 | venue: arXiv preprint
- authors: You, Lei | code: none
- relevance: LOW — theory of cheap screening of K records and expensive verification of at most B.
- what: Under Bayes log-loss, bounds the posterior uncertainty reduction per window with a sqrt(JKB) term.
- thesis use: Only for theory framing of a budget B over K candidates. Cited by Best-of-Evidence.
- verified: abs meta fetched

### Dynamic Test-Time Compute Scaling in Control Policy (DA-SIP / DASIP)
- id: arXiv:2511.20906 | date: 2025-11 | venue: NeurIPS 2025
- authors: Chun et al. | code: none seen
- relevance: LOW — difficulty classifier that sets the inference budget per control step.
- what: A classifier on the observation selects step budget, solver and ODE/SDE mode per control cycle. NeurIPS poster claims 2.6-4.4x less compute at similar success (from the poster page, not the abs page).
- thesis use: Trajectory-agnostic difficulty triggering, a robotics analogue of the scene-uncertainty baseline. Cited in DEEP.
- verified: abs meta fetched

### SP-VLA: A Joint Model Scheduling and Token Pruning Approach for VLA Model Acceleration
- id: arXiv:2506.12723 | date: 2025-06 | venue: ICLR 2026 (per search)
- authors: Li, Ye et al. | code: none seen
- relevance: LOW — action-aware scheduling between a VLA and a light generator.
- what: Switches between the full VLA and a lightweight generator by action state and prunes tokens.
- thesis use: Weak relevance: compute switching conditioned on actions. Cited in DEEP.
- verified: abs meta fetched

### Action-aware Dynamic Pruning for Efficient Vision-Language-Action Manipulation
- id: arXiv:2509.22093 | date: 2025-09 | venue: ICLR 2026 (per search)
- authors: Pei et al. | code: vla-adp.github.io (from search)
- relevance: LOW — gates visual token pruning by recent action trajectory.
- what: Conditions the pruning signal on recent motion; reports a 1.35x speedup on OpenVLA-OFT (search summary of the abstract).
- thesis use: Weak parallel to conditioning a perception decision on the action. Cited in DEEP.
- verified: abs meta fetched

### TIM-PRM: Verifying multimodal reasoning with Tool-Integrated PRM
- id: arXiv:2511.22998 | date: 2025-11 | venue: arXiv preprint
- authors: Kuang et al. | code: none seen
- relevance: LOW — verifier that plans and queries evidence tools about the image.
- what: Agentic process reward model that plans a verification strategy and asks independent questions through external tools; 8B model beats larger ones on VisualProcessBench (from the HF summary, not read).
- thesis use: Tool-querying verifier; shows the 'verify with a tool' pattern outside driving.
- verified: abs meta fetched

### CoINS: Counterfactual Interactive Navigation via Skill-Aware VLM
- id: arXiv:2601.03956 | date: 2026-01 | venue: arXiv preprint
- authors: Zhou, Kangjie et al. | code: none seen
- relevance: LOW — VLM reasons counterfactually about removing objects to decide whether to intervene.
- what: Fine-tuned InterNav-VLM judges how removal would change navigation connectivity. Cited in 'When to Ask for Help' as counterfactual reasoning.
- thesis use: Peripheral; counterfactual framing only.
- verified: abs meta fetched

### CREStE: Scalable Mapless Navigation with Internet Scale Priors and Counterfactual Guidance
- id: arXiv:2503.03921 | date: 2025-03 | venue: RSS 2025
- authors: Zhang, Arthur et al. | code: none seen
- relevance: LOW — counterfactual IRL for navigation costs.
- what: Distills visual foundation model features into BEV and learns costs from counterfactual trajectory demos.
- thesis use: Peripheral; frozen foundation features feeding a cost head.
- verified: abs meta fetched

### Traversing Mars: Cooperative Informative Path Planning to Efficiently Navigate Unknown Scenes
- id: arXiv:2406.05313 | date: 2024-06 | venue: arXiv preprint
- authors: Rockenbauer et al. | code: none seen
- relevance: LOW — a scout decides where to look so a follower finds the best path, with optimality guarantees.
- what: Cooperative IPP in which a scout explores until the follower's path is shown optimal or infeasible; reports 22.5% faster path finding than existing methods.
- thesis use: Early-stopping 'is the plan already optimal?' idea, loosely like abstaining when no tool can change the ranking.
- verified: abs meta fetched

### ColAG: A Collaborative Air-Ground Framework for Perception-Limited UGVs' Navigation
- id: arXiv:2310.13324 | date: 2023-10 | venue: arXiv preprint
- authors: Li, Zhehan et al. | code: none seen
- relevance: LOW — UAV assistance scheduled when predicted failures arise on the UGV plan.
- what: Cited by 'When to Ask for Help' as triggering aerial help from predicted risks along planned trajectories.
- thesis use: Peripheral precedent for plan-conditioned help requests.
- verified: abs meta fetched

### Devil is in Narrow Policy: Unleashing Exploration in Driving VLA Models (Curious-VLA)
- id: arXiv:2603.06049 | date: 2026-03 | venue: arXiv preprint
- authors: Chen, Canyu et al. | code: github Mashiroln/curious_vla
- relevance: LOW — multi-trajectory diversity for VLA training; Navsim PDMS 90.3, Best-of-N PDMS 94.8.
- what: Feasible Trajectory Expansion plus Adaptive Diversity-Aware Sampling for RL.
- thesis use: Source of diverse candidate sets; Best-of-N number shows headroom for a selector over candidates.
- verified: abs meta fetched

### Non-arXiv foundations cited by DEEP (Howard 1966 Information value theory; Russell and Wefald 1991 Principles of metareasoning; Lieder and Griffiths 2017 Strategy selection as rational metareasoning; Bajcsy 1988 Active perception; Reece and Shafer 1995 Control of perceptual attention in robot driving; Oliver and Horvitz 2005 Selective perception policies)
- id: none (journal papers) | date: 1966-2017 | venue: IEEE SMC / AIJ / Psych. Rev. / Proc. IEEE / CVIU
- authors: as listed | code: none
- relevance: MED — the classical value-of-information, metareasoning and active-perception references; Reece and Shafer is about driving.
- what: DEEP's related work cites these for pricing information or computation by its effect on decisions. Oliver and Horvitz is a selective-perception policy by expected value of information versus cost.
- thesis use: Cite as the theory root of 'expected gain per query'. Howard 1966 is also cited by 'When to Ask for Help'.
- verified: UNVERIFIED (names and venues taken from the DEEP reference list; no abstract fetched)

### LLM routing and cascade references cited by Calibrate-Then-Delegate (RouteLLM 2406.18665; FrugalGPT 2305.05176; Dekoninck et al. 2410.10347; AutoMix 2310.12963; Trust or Escalate 2407.18370)
- id: arXiv:2406.18665, 2305.05176, 2410.10347, 2310.12963, 2407.18370 | date: 2023-2025 | venue: ICLR/TMLR/ICML/NeurIPS per CTD bibliography
- authors: Ong; Chen; Dekoninck; Aggarwal; Jung | code: none checked
- relevance: LOW — cost-quality routing between models; Trust or Escalate gives provable agreement guarantees for cascaded judges.
- what: RouteLLM: routers choosing a strong or weak LLM (abstract says over 2x cost reduction in some cases). FrugalGPT: up to 98% cost reduction at GPT-4 level (abstract). AutoMix: POMDP router, over 50% cost reduction. Trust or Escalate: escalate only when judge confidence is low, with guarantee.
- thesis use: Literature for 'learned router at a cost budget' and for guarantee-bearing escalation. Use only as one-line citations.
- verified: abs meta fetched

## Leads not followed
- PACE (Jiao et al., RA-L 2026, DOI 10.1109/LRA.2026.3669805): proactive UAV-assisted planning, no arXiv page found by title search; cited by 'When to Ask for Help'.
- Tellex et al. 2014 "Asking for help using inverse semantics" (RSS; cited as the ask-for-help root) and Lauri and Ritala 2016 (planning for exploration by forward simulation): no abstract fetched.
- Other SIGMA references on conformal perception (Doula et al. CoRL 2025; Timans et al. ECCV 2024) and the cloud/edge driving works [4,5,6]; only '[6] Opportunistic Collaborative Planning' is already in papers.csv.
- DualDriveVLA's driving-VLA bibliography (ORION, iPad, Recogdrive, DiffusionDriveV2, WAM-diff, AutoVLA, Driving on Registers) was only checked by title against papers.csv; AutoVLA, Driving on Registers and AutoDriDM (as Drive-P2D, 2601.14702) are already there, the rest are general E2E driving and I judged them LOW.
- CTD's probe-monitoring references (Goldowsky-Dill, McKenzie, MacDiarmid) and BoE's medical VQA and PRM references were skipped as off-topic.
- Backward references of Kim and Park 'Think as Needed' (2605.10117, already in papers.csv) and of the DEEP companion X1 papers were not mined.
