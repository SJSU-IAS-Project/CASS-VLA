# G_calibrated_risk: calibrated / conformal risk for planners and runtime monitors

## Summary
- Closest overlap with the project: **SIGMA (2610.09520)**. It decides *whether to invoke a costly information source* (cloud VLM) by simulating the planner under plausible scene realizations and computing "expected planning gain" (EPG, which it calls a task-specific approximation of value of information). That is planner-conditioned, decision-relevant query selection, against scene-uncertainty and fixed-period triggers. It is not candidate-set or tool-choice specific, and it uses CARLA with a cloud VLM, not perception tools. It is the best citation for "trajectory-agnostic uncertainty triggering is not enough".
- Closest on the conformal side: **Localized Conformal Safety Monitoring with VLMs (2610.02765)**. Post-hoc split-conformal layer over a frozen VLM that flags collision-causing *planned trajectories*, on CARLA with Qwen/Cosmos backbones. It is a direct template for the future calibration/accept-veto phase (frozen VLM plus calibrated per-trajectory safety set).
- **Barrier-function conformal clearance certificate for trajectory selection (2608.26533)** conformally certifies the chosen trajectory among planner candidates (nuPlan, PDM). Useful as the "accept" gate after the ranker.
- Since SafePath (2505.09427), conformal work moved to (a) abstention/escalation layers on K-sample action selection (BOKBO, SentryVLA) and (b) agent-level conformal risk control with accept/intervene/probe rules (ToolChain-CRC, SafeCommit, CURA, CCPO). These supply the accept/inspect/replan/fallback policy shape, but none in driving with perception tools.
- A strong conceptual warning for the thesis: "Calibration Is Not Control" (2606.21399) shows that routing on calibrated failure risk is worse than routing on *intervention value* (regret 0.51 vs 0.09, ALFWorld). This supports training the selector on expected-gain targets rather than uncertainty, and gives a framing for the scene-uncertainty baseline.
- Calibration under shift: robust/adversarial CP for planners (2602.12616, 2511.10586), severity-conditioned conformal margins under degraded sensing (KEPT 2610.37217), VLM confidence that stays high as visibility is lost (2610.22981). Supports "tool noise levels need noise-conditioned calibration".
- Context-Aware CP (ICML 2026) uses planner uncertainty and trajectory stability as extra calibration signals for VLM driving QA, an example of candidate/trajectory features helping calibration.
- No paper found that does candidate-conditioned *tool* selection in driving with conformal guarantees. The SafePath cited-by list in OpenAlex has only 2 entries (neither relevant). Cited-by coverage for newer papers is thin, so this is a gap in my snowball, not proof of absence.

## Papers

### Not All Uncertainty Matters: Simulation-in-the-Loop Fast-Slow Reasoning for Decision-Critical Autonomous Driving System
- id: arXiv:2610.09520 | date: 2026-10 | venue: arXiv preprint
- authors: Chen, Jiayi et al. | code: none seen
- relevance: HIGH — planner-conditioned decision on whether to request extra information (expected planning gain), measured against periodic/uncertainty triggers; closest overlap to the project's selector idea.
- what: Fast-slow collaboration where an onboard planner is embedded in uncertainty assessment; it simulates plausible scene realizations, estimates the expected reduction in planning cost if uncertainty is resolved (EPG), and uses EPG for cloud invocation, guidance integration and request prioritization under deadlines. In CARLA, vs fixed-period collaboration: 50% fewer unnecessary cloud interactions, over 6% higher navigation success, up to 26.2% shorter finish time (dynamic scenarios).
- thesis use: competitor / related work for "value-of-information style, plan-conditioned querying"; borrow EPG as a name/metric for expected-gain targets. Differs: cloud VLM guidance, not perception-tool choice, no candidate-set divergence.
- verified: abs meta fetched; html read (EPG described as task-specific approximation of VOI)

### Localized Conformal Safety Monitoring with Vision-Language Models for Autonomous Driving
- id: arXiv:2610.02765 | date: 2026-10 | venue: arXiv preprint
- authors: Marques, Luís et al. | code: none seen
- relevance: HIGH — frozen VLM plus split-conformal layer that labels planned trajectories safe/unsafe with finite-sample coverage; template for the calibration phase.
- what: SLLCP, label-conditional split conformal with localization that upweights relevant past scenes when computing thresholds. On 15k CARLA trajectories from unseen scenarios it flags 89.6% (Qwen) and 88.4% (Cosmos) of collision-causing trajectories, vs 4.6% and 39.1% for the base VLMs.
- thesis use: idea to borrow (localized, label-conditional calibration for accept/veto); baseline for future-phase monitor.
- verified: abs meta fetched

### Barrier Function Conformal Safety Clearance Certification with CVaR for Driving Trajectory Selection
- id: arXiv:2608.26533 | date: 2026-08 | venue: arXiv preprint
- authors: Chang, Pei Yu et al. | code: none seen
- relevance: HIGH — conformal certificate on the *selected* trajectory among planner candidates (post-selection calibration).
- what: Differentiable separating-axis barrier margin lower-bounds oriented-box clearance; plan-time margin (nominal or sampled lower-tail CVaR) is calibrated post selection over exchangeable drive sessions. On 300 frozen nuPlan sessions with PDM closed-loop proposals at 10% miscoverage, CVaR cuts the conformal correction from 1.43 m to 0.03 m and raises nonnegative-clearance certificates from 68.7% to 87.3%; coverage 93.3-96.7%.
- thesis use: idea to borrow for accept gate after ranker; note post-selection calibration issue.
- verified: abs meta fetched

### Context-Aware Conformal Prediction for VLM-Based Driving Scene QA
- id: https://icml.cc/virtual/2026/80373 (no arXiv id found after OpenAlex and web search) | date: 2026 | venue: ICML 2026 workshop (the page links to a workshop id; workshop name not captured)
- authors: not captured | code: none seen
- relevance: MED — uses planner uncertainty and temporal stability of planned trajectories as calibration signals for VLM answers.
- what: CA-CP adds planner features as external difficulty signals; on 16,655 WaymoQA pairs across six VLMs it improves worst-slab conditional coverage on all 6 VLMs, with KNN kernel-weighted quantiles best, at modest set-size increase.
- thesis use: idea to borrow (trajectory-derived features inform calibration, parallels candidate-divergence features).
- verified: page fetched (abstract text only; authors not rendered in page text, workshop name and arXiv id UNVERIFIED)

### Calibration Is Not Control: Intervention Value for LLM-Agent Oversight
- id: arXiv:2606.21399 | date: 2026-06 | venue: arXiv preprint
- authors: Zhang, Chubin et al. | code: https://github.com/bennidict23/calibration-is-not-control
- relevance: HIGH (conceptual) — argues intervention triggered by calibrated failure risk is the wrong target; train on intervention utility.
- what: On ALFWorld, changing the supervision target from failure to intervention utility lowers regret from 0.51 to 0.09 with features/estimator/router fixed; online on 300 unseen tasks a frozen prefix-feature controller hands off less often (35% vs 48%) and succeeds more (45% vs 37%). Gains small on two reasoning benchmarks.
- thesis use: supports expected-gain targets over scene-uncertainty triggering; cite for the contrast between risk and value.
- verified: abs meta fetched

### BOKBO (Best of K Bad Options): Calibrated Abstention for VLA Policies
- id: arXiv:2605.30660 | date: 2026-05 | venue: arXiv preprint
- authors: Singh, Anya et al. | code: none seen
- relevance: HIGH (method fit) — conformal abstention over K candidate actions when all may be unsafe; K-candidate structure like the project's.
- what: Conformal risk control layer on K-sample VLA inference with finite-sample guarantees on executed-violation rate; global and per-task (Mondrian). Finds policy-internal nonconformity scores correlate 0.98 with sampling noise and at noise floor with violations; a learned violation predictor on semantic visual features supports calibration (libero_object_temp_x0.1, OpenVLA-OFT, eps=0.05: conditional bound holds on 86% of bootstrap splits, 78% coverage, 70% net success). Manipulation, not driving.
- thesis use: idea to borrow for the abstain/fallback layer; cautions that candidate-disagreement scores can be uninformative.
- verified: abs meta fetched

### SentryVLA: Uncertainty-Guided Action Selection and State Monitoring for VLA Robotic Control
- id: arXiv:2604.16677 | date: 2026-04 | venue: arXiv preprint
- authors: Lyu, Zongyao et al. | code: none seen
- relevance: MED — runtime wrapper over frozen policy: conformalized quantile regression ranks stochastic candidates, plus a Mahalanobis anomaly monitor on latent state.
- what: Candidate re-ranking by calibrated upper bound on deviation from expert-like behavior, and an execution-state anomaly score; no retraining of the frozen VLA. Manipulation.
- thesis use: idea to borrow (frozen-model wrapper plus latent anomaly monitor).
- verified: abs meta fetched

### ToolChain-CRC: Conformal Risk Control for Agentic AI Under Retrieval and Tool-Use Drift
- id: arXiv:2606.18467 | date: 2026-06 | venue: arXiv preprint
- authors: Opoku, Jeffery et al. | code: none seen
- relevance: MED — trajectory-level conformal risk control over tool calls with accept-or-intervene rule and anytime alarm.
- what: Step-level risk scores combined into trajectory risk, calibrated accept/intervene rule, drift-aware extension, anytime escalation via supermartingale. Shows final-answer-only calibration can miss retrieval/tool failures. Text agents, not driving.
- thesis use: idea to borrow for the policy structure under tool noise/drift.
- verified: abs meta fetched

### SafeCommit: Certifying When Memory-Grounded Agents May Safely Act
- id: arXiv:2608.04289 | date: 2026-08 | venue: arXiv preprint
- authors: Akewar, Mayur et al. | code: none seen
- relevance: MED — conformal action certificate across plausible worlds; if not certified, picks a low-side-effect *probe* targeting the blocking worlds, or a conservative fallback. Accept / probe / fallback is the shape of the planned policy.
- what: Calibrated set of latent worlds from memory, observations, tool outputs; action allowed only if safe in every retained world. Text/memory agents.
- thesis use: idea to borrow (probe chosen by which hypotheses block certification, analogous to candidate-conditioned query).
- verified: abs meta fetched (abstract truncated at my cut; results not read)

### SafeVantage: Vantage-Aware Memory for Reliable Embodied Decisions
- id: arXiv:2609.36906 | date: 2026-09 | venue: arXiv preprint
- authors: Lewis, Sean Hardesty et al. | code: none seen
- relevance: MED — active acquisition chosen by expected reduction in terminal decision loss, with calibrated Yes/No/Abstain head.
- what: Learned candidate-observability model predicts visibility at reachable viewpoints; view selection by expected decision-loss reduction accounting for cost. Embodied navigation/search.
- thesis use: idea to borrow (decision-loss-based acquisition + abstain).
- verified: abs meta fetched

### What's Hidden Matters: Identifying Planning-Critical Occluded Agents using Vision-Language Models
- id: arXiv:2607.00283 | date: 2026-07 | venue: arXiv preprint
- authors: Chahe, Amirhosein et al. | code: none seen
- relevance: MED — ranks occluded agents by their effect on the ego plan (Planning KL-divergence), nuScenes benchmark; plan-conditioned relevance of hidden objects.
- what: PKL ranks occluded agents by plan impact; GPT-5 annotates; fine-tuning VLMs on this data gives large gains (numbers not read).
- thesis use: benchmark / idea (plan-conditioned relevance for the occlusion hazard); possible label source for ROI-tool value.
- verified: abs meta fetched (abstract truncated)

### AutoAgent0: An Agentic Runtime for Safe Closed-Loop Driving
- id: arXiv:2610.18866 | date: 2026-10 | venue: arXiv preprint
- authors: Liu, Jiageng et al. | code: none seen
- relevance: MED — runtime harness: independent detection skills, rule-based verifier checks proposed trajectories, recovery planning when nominal trajectory is unreliable. Shield/replan loop with perception skills.
- what: Evaluated on Fail2Drive and NavSafe-inf; improved closed-loop robustness over single-expert execution (no numbers read).
- thesis use: competitor for accept/replan/fallback phase; not selective on queries.
- verified: abs meta fetched

### CARVE: Certified Affordable Repair of Vetoed Maneuvers via Envelopes for Interactive Driving
- id: arXiv:2606.02641 | date: 2026-05 | venue: arXiv preprint
- authors: Wang, Yifan | code: none seen
- relevance: LOW/MED — what to do after a veto: certified repair set and fallback. Not statistical.
- what: Prediction-free certificate layer; on 589 INTERACTION replay episodes CARVE-Greedy accepts 98.64% of initially vetoed maneuvers.
- thesis use: idea for the replan/fallback stage.
- verified: abs meta fetched

### When Environments Shift: Safe Planning with Generative Priors and Robust Conformal Prediction
- id: arXiv:2602.12616 | date: 2026-02 | venue: arXiv preprint
- authors: Rahaman, Kaizer et al. | code: none seen
- relevance: MED — conformal-MPC safety guarantee that survives distribution shift (traffic density) using diffusion-generated data and robust CP; ORCA simulator.
- thesis use: idea for calibration under shift (noise level as nuisance parameter).
- verified: abs meta fetched

### Safe Planning in Interactive Environments via Iterative Policy Updates and Adversarially Robust Conformal Prediction
- id: arXiv:2511.10586 | date: 2025-11 | venue: arXiv preprint
- authors: Mirzaeedodangeh, Omid et al. | code: none seen
- relevance: LOW/MED — CP guarantees across policy updates that shift environment behavior (exchangeability broken).
- thesis use: caveat for calibrating a selector whose choices change downstream data.
- verified: abs meta fetched

### KEPT: Conformal Keepouts Kept in Planning for Enclosed-Space Navigation in Degraded Sensing
- id: arXiv:2610.37217 | date: 2026-10 | venue: arXiv preprint
- authors: Kim, Eric Minwoo et al. | code: none seen
- relevance: MED — conformal margin conditioned on a label-free severity estimate under smoke/dust/fog so per-class coverage holds as degradation varies.
- thesis use: idea to borrow for severity-conditioned calibration across the three tool-noise levels.
- verified: abs meta fetched

### How Murky Before a VLM Knows It Cannot See? Accuracy, Confidence and Abstention on a Physical Visibility Axis
- id: arXiv:2610.22981 | date: 2026-10 | venue: arXiv preprint
- authors: Fauzan, Mochamad Rizal et al. | code: none seen
- relevance: MED — five small VLMs keep high confidence (internal 0.68-0.84, verbalized 0.61-1.00) after accuracy falls to chance in fog at V=1.95 m (1000 COCO scenes).
- thesis use: supports not trusting VLM verbalized confidence (consistent with VLM prompting saying "none"); related to Lost in Fog.
- verified: abs meta fetched

### Confidence Calibration in Vision-Language-Action Models
- id: arXiv:2507.17383 | date: 2025-07 | venue: arXiv preprint
- authors: Zollo, Thomas P et al. | code: none seen
- relevance: MED — first study of VLA confidence calibration; prompt ensembles and action-wise Platt scaling.
- thesis use: baseline calibration methods for a VLM/VLA component.
- verified: abs meta fetched

### CovNav: Conformal Prediction-Guided Adaptive Inference for Object Goal Navigation
- id: arXiv:2610.27677 | date: 2026-10 | venue: arXiv preprint
- authors: Wu, Pengying et al. | code: none seen
- relevance: MED — CP prediction set decides when to escalate from fast to slow reasoning (only ambiguous queries escalate). A cost-vs-accuracy "when to think more" gate with CP.
- thesis use: idea (CP-gated escalation, budget curve).
- verified: abs meta fetched

### CLOSER: Evidence-Aware Active Visual Verification for Embodied Object-Goal Navigation
- id: arXiv:2610.28476 | date: 2026-10 | venue: arXiv preprint
- authors: Wu, Pengying et al. | code: none seen
- relevance: LOW/MED — VLM labels views target/non-target/uncertain; keeps acquiring views until decisive.
- thesis use: related active verification; not driving.
- verified: abs meta fetched

### Conformal Constrained Policy Optimization for Cost-Effective LLM Agents
- id: arXiv:2511.11828 | date: 2025-11 | venue: AAAI 2026 (per OpenAlex record)
- authors: Si, Wenwen et al. | code: none seen
- relevance: MED — orchestrator chooses models/tools in sequence to minimize cost subject to a conformal reliability constraint; up to 30% cost reduction on two multi-hop QA benchmarks.
- thesis use: idea to borrow (cost-minimizing tool policy with a conformal constraint) for the budget Pareto framing.
- verified: abs meta fetched

### Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents
- id: arXiv:2602.16699 | date: 2026-02 | venue: arXiv preprint
- authors: Ding, Wenxuan et al. | code: none seen
- relevance: LOW/MED — agents given a calibrated prior reason about cost-uncertainty tradeoffs to decide when to stop acquiring information.
- thesis use: idea (explicit prior passed to decision-maker).
- verified: abs meta fetched

### ReDAct: Uncertainty-Aware Deferral for LLM Agents
- id: arXiv:2604.07036 | date: 2026-04 | venue: arXiv preprint
- authors: Piatrashyn, Dzianis et al. | code: none seen
- relevance: LOW/MED — defer to large model when small model's uncertainty exceeds a calibrated threshold; deferring about 15% of decisions matches the large model (ALFWorld, MiniGrid). Scene-uncertainty-style trigger, a baseline analogue.
- thesis use: baseline analogue to scene-uncertainty triggering.
- verified: abs meta fetched

### CoFineLLM: Conformal Finetuning of LLMs for Language-Instructed Robot Planning
- id: arXiv:2511.06575 | date: 2025-11 | venue: arXiv preprint
- authors: Wang, Jun et al. | code: none seen
- relevance: LOW/MED — direct KnowNo/SafePath follow-up: CP-aware finetuning shrinks prediction sets so fewer help requests.
- thesis use: related work for "ask for help" with conformal sets.
- verified: abs meta fetched

### Judge, Retrieve, or Abstain: Uncertainty-Guarded LLM Judging with Provable Risk Guarantees
- id: arXiv:2608.17994 | date: 2026-08 | venue: arXiv preprint
- authors: Badshah, Sher et al. | code: none seen
- relevance: LOW/MED — accept if confident, else route to a tool-augmented mode, else abstain; false-discovery rate among accepted verdicts controlled (Clopper-Pearson).
- thesis use: idea (accept/tool/abstain cascade with risk guarantee).
- verified: abs meta fetched

### CURA: Certified Runtime Alarms for Computer-Use Agents
- id: arXiv:2608.27808 | date: 2026-08 | venue: arXiv preprint
- authors: Kumar, Divake et al. | code: none seen
- relevance: LOW — external sequential-test monitor with certified false-alarm control (alpha=0.10, detects 42.3% of failures at realized false alarm 0.066).
- thesis use: monitor design reference only.
- verified: abs meta fetched

### G-CARB: Graph-Localized Conformal Agent Risk Budget for Compositional Harm
- id: arXiv:2610.05563 | date: 2026-10 | venue: arXiv preprint
- authors: Yu, Zijun et al. | code: none seen
- relevance: LOW — conformal risk control for when to stop an agent across tool calls.
- verified: abs meta fetched

### Beyond Aggregate Risk: Role-Stratified Conformal Risk Control for LLM Tool Calls
- id: arXiv:2607.24343 | date: 2026-07 | venue: arXiv preprint
- authors: Rahman, Md Ashikur et al. | code: none seen
- relevance: LOW — per-field CRC on tool-call arguments; stratified calibration idea (per-tool or per-hazard thresholds).
- verified: abs meta fetched

### CoCoNav: Conformal Control for Safe Robot Navigation in Crowds
- id: arXiv:2608.07751 | date: 2026-08 | venue: arXiv preprint
- authors: Guo, Cheng et al. | code: none seen
- relevance: LOW/MED — online conformal PI-controller keeps coverage under shifting prediction error; relax-then-verify planner certifies nominal and contingency trajectories.
- thesis use: online calibration under shift, fallback/contingency idea.
- verified: abs meta fetched

### CoSMO: Conformal Semantic Mapping for Open-World Safe Robot Navigation
- id: arXiv:2610.18321 | date: 2026-10 | venue: arXiv preprint
- authors: Wang, Shuqi et al. | code: none seen
- relevance: LOW/MED — calibrates VLM embeddings online into coverage sets under distribution shift; 61.6% fewer semantic collisions vs geometry-only on Matterport3D.
- thesis use: idea for calibrating on frozen VLM embeddings (matches project's frozen-embedding use).
- verified: abs meta fetched

### Adaptive Safety Filtering for Frozen ACC Policies via Conformal Residual Calibration
- id: arXiv:2609.35415 | date: 2026-09 | venue: arXiv preprint
- authors: Zhou, Zhiruo et al. | code: none seen
- relevance: LOW — conformal residual margin for filtering a frozen policy's actions; Adaptive RACF 94.3% episode safety, +19.9 points over nominal CBF-QP baseline.
- verified: abs meta fetched

### Forecasting the Past: Gradient-Based Distribution Shift Detection in Trajectory Prediction
- id: arXiv:2604.12425 | date: 2026-04 | venue: arXiv preprint
- authors: De Vita, Michele et al. | code: link in abstract (not recorded)
- relevance: LOW/MED — post-hoc shift score for trajectory predictors (Shifts, Argoverse); also early-detects collisions of a DQN planner in Highway sim.
- thesis use: shift detector for runtime monitor phase.
- verified: abs meta fetched

### Confidence-Modulated Safety Filtering for End-to-End Policies
- id: arXiv:2610.40922 | date: 2026-10 | venue: arXiv preprint
- authors: Borquez, Javier et al. | code: none seen
- relevance: LOW — policy confidence sets filter conservativeness at runtime (F1TENTH, preliminary).
- verified: abs meta fetched

## Leads not followed
- Cited-by for SafePath only returned 2 irrelevant OpenAlex hits; Google Scholar-style cited-by not available. Try arXiv full-text search for "SafePath" and for "KnowNo" driving follow-ups.
- Context-Aware CP (ICML 2026 workshop): searched OpenAlex and web, no arXiv id or authors found; leave UNVERIFIED.
- Read bodies (not just abstracts) of 2610.02765 and 2608.26533 for whether candidate sets and exchangeability handling transfer to MetaDrive.
- Not searched: conformal prediction for traffic-light state/occlusion inference, CRC for detection-driven planners (e.g. perception-error calibration papers 2025-07+), human-handover/takeover timing in driving, OpenReview ICLR 2027 submissions on conformal/abstention.

## Added papers (round 2)

### Opportunistic Collaborative Planning with Large Vision Model Guided Control and Joint Query-Service Optimization
- id: DOI 10.1109/iros60139.2025.11245999 | date: 2025-10 | venue: IROS 2025
- authors: not captured (SIGMA's footnote says it is the IROS 2025 precursor; first author presumably Chen, Jiayi: UNVERIFIED) | code: none seen
- relevance: MED — SIGMA's own earlier version of query-timing for cloud LVM guidance with MPC.
- what: Per SIGMA's footnote, "Part of this work has been presented at ... IROS ... in the paper entitled 'Opportunistic Collaborative Planning with Large Vision Model Guided Control and Joint Query-Service Optimization.'" Abstract not read.
- thesis use: related work to cite alongside SIGMA.
- verified: OpenAlex record only (title/date/DOI); content UNVERIFIED

### Bridging Large-Model Reasoning and Real-Time Control via Agentic Fast-Slow Planning
- id: DOI 10.1109/icra57385.2026.11695925 | date: 2026-06 | venue: ICRA 2026
- authors: Chen, Jiayi; Wang, Shuai; Zhu, Guangxu; Xu, Chengzhong (OpenAlex) | code: none seen
- relevance: LOW/MED — same group as SIGMA; hierarchical VLM detector, cloud LLM decision maker, MPC. No query-selection criterion in the abstract text I saw.
- thesis use: background for SIGMA lineage.
- verified: OpenAlex abstract read (arXiv id not found)

### Event-Adaptive Motion Planning with Distilled Vision-Language Model in Safety-Critical Situations
- id: arXiv:2606.25629 | date: 2026-06 | venue: arXiv preprint
- authors: Huang, Zhenwei et al. | code: none seen
- relevance: LOW/MED — prompt-configurable event trigger decides when to invoke a distilled VLM in the control loop (robot navigation, logistics scenarios). Trigger on temporal anomalies, not plan-conditioned.
- thesis use: baseline analogue to scene-triggered invocation.
- verified: abs meta fetched

### Explore until Confident: Efficient Exploration for Embodied Question Answering
- id: arXiv:2403.15941 | date: 2024-03 | venue: arXiv preprint (RSS 2024 per my memory: UNVERIFIED)
- authors: Ren, Allen Z. et al. | code: none seen
- relevance: MED — older essential: conformal prediction on VLM answer confidence decides when to stop gathering information.
- thesis use: canonical reference for "CP decides when to stop acquiring information".
- verified: abs meta fetched

## SIGMA deep read (arXiv:2610.09520v1, cs.RO, 07 Oct 2026; full html read)
Authors: Jiayi Chen, Shuai Wang, Guangxu Zhu, Derrick Wing Kwan Ng, Chengzhong Xu, Kaibin Huang. Code: only the 3D bounding-box uncertainty estimator, https://github.com/cjychenjiayi/3D_Bbox_uncertainty (the abstract says "The implementation of our prediction-time 3D bounding-box-level uncertainty estimator is publicly available"). No planner/EPG code link seen.

**EPG definition (Sec. V-C, Eq. 17a-b; Sec. V-B Eq. 16 gives the pairwise gain).**
- Eq. 16: normalized planning gain between two scene configurations = (J_t(C1) - J_t(C2)) / J_t(C1), where J_t is the optimal MPC cost (tracking error + control effort + smoothness, with collision-avoidance constraints).
- Eq. 17: delta J_t(xi_t) = (J_t(C_base) - J_t(C_t(xi_t))) / J_t(C_base); EPG_t = E over xi_t ~ p_t(xi | o_t) of [delta J_t(xi_t)].
- Verbatim gloss: "the expectation is taken over the uncertainty distribution induced by the current observation." Estimated by "importance-sampling-based Monte Carlo rollout" (budget-aware). Verbatim: "A negligible Delta_pg means that resolving the uncertainty does not materially change the planner, whereas a large value indicates decision-relevant uncertainty."
- Intro: "EPG can be interpreted as a task-specific approximation of the value of information".

**What it chooses between.** One binary decision per request: query the cloud or not (alpha_i in {0,1}, Eq. 25: indicator[benefit g_i > theta_g] times indicator[slack > predicted response time]), with benefit g_i = EPG_i - lambda*kappa_lm - rho*D(latency) (Eq. 24). Second binary: whether returned guidance is integrated (beta_i, Eq. 27). When several vehicles compete for cloud capacity, requests are ranked by psi_i = g_i / (latency + eps) (Eq. 26). Source = one cloud LVM/VLM pipeline ("object detection, segmentation, scene-graph construction, and traffic reasoning" bundled). It never selects among several tools or sensors.

**Candidate set.** There is no set of candidate trajectories. The planner is a single MPC that returns one optimal trajectory tau*(C) per scene configuration (Eq. 15). The "candidates" are sampled *scene realizations* (obstacle position perturbations), not plans. Divergence is measured in MPC cost, not among K plans.

**Baselines.** LOS (local-only, treats unknown objects conservatively as obstacles), PCS (fixed 5 s cloud-interaction period), PCS-2 (fixed 5.5 s). Verbatim in Sec. VII-B: "the SIGMA scheme dynamically triggers cloud interaction based on ODCT-based semantic screening (Section IV-A) and the EPG-guided collaboration strategy". No scene-uncertainty-threshold trigger baseline, no random trigger, no oracle, no budget sweep.

**Headline numbers (verbatim, with section).**
- Abstract: "Compared with fixed-period collaboration, SIGMA reduces unnecessary cloud interactions by 50%, improves navigation success rate by more than 6%, and achieves up to 26.2% reduction in finish time in dynamic scenarios."
- Sec. VII-B1: "SIGMA reduces the number of cloud interactions by 50% compared with PCS (2 vs. 4 times)" (a single scenario, Town06, about 110 m, 7 known and 4 unknown objects). Table IV (10 repeats): FTime LOS 25.94 s, PCS 24.09, PCS-2 23.53, SIGMA 22.35 s.
- Sec. VII-C (30 runs per setting, 3 m/s): Table V finish time with U=2 unknown objects: LOS 55.36 s, PCS 47.60, SIGMA 45.44; with U=1, PCS 44.02 beats SIGMA 44.86; with U=0, PCS 42.31 beats SIGMA 43.00. Verbatim: "we do not claim that SIGMA is always the fastest". "Compared with the second-best scheme, SIGMA improves the success rate by over 6%" (read from Fig. 16, no table).
- Sec. VII-D (Town03 crossroad, one dynamic scenario): Table VI FTime PCS 23.40 s vs SIGMA 17.28 s ("more than 26.2% reduction"; 23.40 to 17.28 is a 26.15% drop, so the 26.2% is rounded up from my arithmetic).
- Sec. VII-A: uncertainty head, localization error rises from 0.129 to 0.488 across uncertainty bins, Pearson 0.405, Spearman 0.536 (KITTI).
- Evidence base is thin: 10 to 30 runs on hand-built CARLA scenes, no variance reported in the text I read.

**Quotes that collide with, or sit close to, our claim.**
- Abstract: "Existing approaches typically rely on perception uncertainty, heuristic triggers, or resource-driven policies, which fail to explicitly evaluate whether resolving a particular uncertainty will actually improve the downstream planning outcome."
- Sec. VII-B2: "These results highlight that the impact of uncertainty should be evaluated in the planning space rather than the perception space. Only uncertainty that leads to divergent planning outcomes is decision-relevant."
- Sec. VII-D: "cloud reasoning is invoked when it can change the driving strategy, rather than merely refine perception."
- Abstract: "perception ambiguity [matters] when it substantially alters the feasible trajectory set or significantly affects the associated planning cost."
- Sec. II-D: "What remains underexplored is a unified decision-oriented perspective, where both uncertainty resolution and external reasoning are governed by their expected impact on downstream planning."
These are the same principle as ours (query value defined by effect on the decision, not by scene uncertainty).

**Novelty risk to our project: PARTIAL (medium).**
- Collides: the core argument "trigger by decision impact, not scene uncertainty", an EPG-like expected-gain quantity, and an invocation cost term in the trigger. We must cite SIGMA and not claim the principle as new.
- Does not collide: (1) a single binary query, no choice among tools, no abstain-vs-which-tool decision; (2) no candidate set of K trajectories and no use of how candidates diverge (their variability is over scene realizations pushed through one MPC); (3) no equal-budget Pareto comparison and no scene-uncertainty-threshold, random, or oracle baselines, only fixed-period and local-only; (4) it is a hand-set threshold on a Monte Carlo estimate, with no learned selector; (5) sensor/tool noise levels are not varied; (6) closed-loop CARLA with a physical MPC, not open-loop decision accuracy; (7) the cloud VLM supplies guidance, not a perception-tool readout.
- Suggested positioning: SIGMA is the nearest prior art for expected-gain-as-trigger; our contribution is the tool-choice and candidate-conditioned version plus the budget-matched comparison against uncertainty triggering. Their future-work paragraph lists RL policies and world-model-in-the-loop, not tool choice or candidate sets.
- Lineage to also cite: the IROS 2025 and ICRA 2026 papers above. OpenAlex shows 0 citations to SIGMA so far.

## Short deep reads

### Calibration Is Not Control (arXiv:2606.21399; full html read)
- Setting: LLM-agent oversight on ALFWorld (plus ScienceWorld, GSM8K, HotpotQA); not driving. Decision: intervene (handoff/repair) vs continue vs quit at a prefix, not which tool.
- Core claim (abstract): "states with the same failure risk can differ in whether intervention helps"; strictly increasing recalibration "preserves the threshold policy class and cannot recover this distinction".
- Numbers verbatim: regret 0.51 to 0.09 when changing only the label from failure to intervention utility (body: 0.513 to 0.094); deployable intervention-trained scalar 0.275 vs 0.229 on utility vs the failure-score rule; online on 300 unseen tasks with GPT-5.4 handoff, 35% vs 48% handoffs and 45% vs 37% success; Platt scaling cuts calibration error from 0.463 to 0.006 and leaves the problem intact.
- Limits stated: gains small on the two reasoning benchmarks; "The budget result is confined to the four-action suite".
- Code: https://github.com/bennidict23/calibration-is-not-control
- Novelty risk to us: none as competitor (different domain, binary-ish intervention), but strong support: it is an independent demonstration that training on intervention value beats risk-score triggering, which is our expected-gain-vs-scene-uncertainty argument.

### Localized Conformal Safety Monitoring with VLMs (arXiv:2610.02765; full html read)
- Task: binary safe/unsafe label for a planned trajectory given the scene, from a frozen VLM; SLLCP returns a prediction set per label with label-conditional coverage (error for unsafe, false-alarm rate for safe).
- Assumption stated: iid/exchangeable calibration set ("Assumption 1 ... iid with the test pair"); calibration set "uncorrupted". They test whether empirical coverage falls within a 90% interval of nominal under non-exchangeable test scenes.
- Baselines: raw VLM (binary), raw VLM with alpha-aware two-label sets (0.1/0.9), and four ablations (no locality, no linear probe, no UMAP projection, no per-label correction).
- Numbers: unchanged from abstract (89.6% Qwen, 88.4% Cosmos vs 4.6% and 39.1%; 15k CARLA trajectories from unseen scenarios). No code link found.
- Novelty risk to us: none for tool selection (monitor on single trajectories, no tool, no query). Useful for the future accept/veto phase and for frozen-VLM-embedding calibration.

### Barrier Function Conformal Safety Clearance Certification (arXiv:2608.26533; full html read)
- Setting: nuPlan, PDM-Closed candidate proposals; certifies the *selected* trajectory's clearance; calibration is over whole drive sessions (post-selection), 300 frozen sessions, 10% target miscoverage.
- Numbers: unchanged from abstract (correction 1.43 m to 0.03 m with sampled lower CVaR; nonnegative certificates 68.7% to 87.3%; coverage 93.3-96.7%).
- Does not choose among candidates; the selector is the existing PDM. No tools or queries. Code link not found in text.
- Novelty risk to us: none; direct template for an "accept" certificate after our ranker.

## Cited-by and related work notes (round 2)
- OpenAlex lists 0 works citing SIGMA (2610.09520) as of today, so the cited-by snowball is empty.
- SIGMA's own related work (Sec. II) covers perception uncertainty, planning under perception uncertainty, and fast-slow cloud-edge driving; its closest systems are the group's own IROS 2025 and ICRA 2026 papers listed above. No candidate-conditioned or multi-tool work cited in the sections I read.
- Reference list of SIGMA was not mined beyond Sec. II.

## Updated Summary (supersedes the first Summary where they differ)
- Most important change: SIGMA (2610.09520) is real prior art for "trigger the costly query by expected downstream planning gain, not scene uncertainty". Novelty risk to our project is PARTIAL. The principle collides; the candidate-set conditioning, choice among several tools plus abstain, equal-budget Pareto vs uncertainty/random/oracle baselines, and tool-noise levels do not appear in it. Cite it and reframe the claim around tool choice and candidate divergence.
- "Calibration Is Not Control" (2606.21399) independently supports learning from intervention value over failure-risk thresholds; no novelty risk.
- Calibration phase templates: SLLCP (2610.02765) for a frozen-VLM conformal veto on planned trajectories, 2608.26533 for a post-selection certificate on the chosen candidate, BOKBO (2605.30660) and SentryVLA (2604.16677) for abstention over K candidates (manipulation).
- Agent-level conformal accept/probe/fallback rules (ToolChain-CRC, SafeCommit, CCPO, Judge-Retrieve-Abstain) give policy shapes but none are in driving with perception tools.
- Shift calibration: KEPT (severity-conditioned conformal margin), robust CP planning (2602.12616, 2511.10586), VLM overconfidence under fog (2610.22981).
- Context-Aware CP stays an ICML 2026 workshop page with no arXiv id or authors found.
- Searches found no paper combining candidate-set-conditioned perception-tool selection with a budget curve in driving.
