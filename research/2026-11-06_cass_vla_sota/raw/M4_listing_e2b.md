# M4_listing_e2b: arXiv listing triage, e2_01.tsv (425 titles, Jul 2025 - Jun 2026)

## Summary
- No close overlap found. Nothing in this slice does candidate-trajectory-conditioned perception-query selection for driving. The slice is dominated by conformal-prediction theory papers, LLM tool-calling papers and generic "zoom" papers.
- Closest in method: Calibrate-Then-Delegate (2604.14251) and To Call or Not to Call (2605.00737). Both argue that uncertainty is a poor proxy for the benefit of a call and train a predictor of the benefit (a "delegation value" probe, a "latent need estimator") instead. That is the same argument as the project's expected-gain targets versus scene-uncertainty triggering. CTD also adds a conformal threshold with finite-sample cost or risk guarantees, which fits the future calibration phase.
- Budgeted tool allocation with conformal certificates: Proof-of-Perception (2603.00324) expands tool calls only when a conformal set is uncertain. It is a scene-uncertainty-style trigger with guarantees, so a possible baseline variant.
- Learned "when to call" results in LLM agents are consistent with the project's finding that a prompted VLM says "none": Model-Adaptive Tool Necessity (2605.14038) reports 26.5-54.0% and 30.8-41.8% mismatch between need and actual calls; Do Multimodal Agents Really Benefit from Tool Use (2606.02357) finds little consistent aggregate gain from tool access.
- Driving-specific items are few: conformal risk-object identification (2603.23919), Waymo conformal visual runtime monitoring (2605.13923), conformal spectral-risk MPC with vehicle obstacle avoidance (2606.04185). All are calibration-phase material, none are query selection.
- Value-of-information / active feature acquisition (2604.01434, 2605.05511, 2606.18933) is theory or tabular and gives formal vocabulary (non-myopic acquisition, stop-and-predict), not driving evidence.
- Second generous pass (VOI, active acquisition, when-to-query titles marked LOW in pass 1) added 2604.01434, 2605.05511, 2606.18933, 2603.07822, 2605.27788, 2606.11349 and 2605.16604; the rest were fetched and dropped (see end).
- All 58 shortlisted ids were fetched (abs meta). None was already in raw/*.md at grep time.

## Papers

### Calibrate-Then-Delegate: Safety Monitoring with Risk and Budget Guarantees via Model Cascades
- id: arXiv:2604.14251 | date: 2026-04 | venue: arXiv preprint
- authors: Pona, Edoardo et al. | code: none seen in abstract
- relevance: HIGH — a learned predictor of the benefit of an expensive call, calibrated to a budget or risk guarantee; direct analogue of expected-gain targets vs. uncertainty triggers
- what: A cheap latent-space probe screens every input and hard cases are escalated to an expert. Existing cascades delegate on probe uncertainty; CTD instead trains a "delegation value" probe that predicts the benefit of replacing the probe score with the expert score, then calibrates a threshold on it with held-out data and multiple hypothesis testing for finite-sample guarantees on cost or safety performance. On four safety datasets it improves over uncertainty-based delegation over much of the budget range and avoids unnecessary expert calls.
- thesis use: idea to borrow (benefit-prediction target plus conformal threshold on it, for the calibration phase); supports the claim that uncertainty is a weak proxy for query value
- verified: abs meta fetched

### To Call or Not to Call: A Framework to Assess and Optimize LLM Tool Calling
- id: arXiv:2605.00737 | date: 2026-05 | venue: arXiv preprint
- authors: Wu, Qinyuan et al. | code: https://github.com/QinyuanWu0710/ToCall_or_NotToCall
- relevance: HIGH — decision-theoretic framing of whether to call a tool (necessity, utility, affordability) and a learned estimator that improves budgeted allocation
- what: Evaluates six open models and one proprietary model across two tools and six tasks; perceived need and utility are misaligned with true values, especially under budget constraints, giving both overuse and harmful calls. Lightweight latent estimators of need (LNEs) trained on hidden states predict true need better than model self-reports and improve budgeted tool allocation.
- thesis use: idea to borrow (hidden-state need estimator, analogous to cached VLM embeddings feeding the selector); supports that prompting a model to choose tools is unreliable
- verified: abs meta fetched

### Proof-of-Perception: Certified Tool-Using Multimodal Reasoning with Compositional Conformal Guarantees
- id: arXiv:2603.00324 | date: 2026-02 | venue: arXiv preprint
- authors: Fayyazi, Arya et al. | code: none seen in abstract
- relevance: HIGH — a controller that allocates tool calls under a budget from per-node conformal sets, stopping early otherwise
- what: Multimodal reasoning is cast as an executable graph where each perception or logic node outputs a conformal set. A controller expands with extra tool calls only when the certificates say it is needed. Evaluated on document, chart and multi-image QA, where it improves over chain-of-thought, ReAct-style and program-of-thought baselines with more efficient compute (no numbers in abstract).
- thesis use: baseline variant (certificate-triggered scene-uncertainty selector) and a template for budget-aware calibrated stopping; not driving
- verified: abs meta fetched

### Model-Adaptive Tool Necessity Reveals the Knowing-Doing Gap in LLM Tool Use
- id: arXiv:2605.14038 | date: 2026-05 | venue: arXiv preprint
- authors: Cheng, Yize et al. | code: none seen in abstract
- relevance: MED — defines tool necessity empirically per model and measures the gap between need and calls
- what: Necessity is defined from each model's own performance; across four models on arithmetic and factual QA, necessity and observed tool-call behaviour mismatch by 26.5-54.0% and 30.8-41.8% respectively. Hidden-state probes show both "belief" and "action" signals are linearly decodable but nearly orthogonal in late-layer last-token directions.
- thesis use: supports the "VLM mostly says none" finding; the per-model-necessity definition parallels per-noise-level expected gain
- verified: abs meta fetched

### Utility-Guided Agent Orchestration for Efficient LLM Tool Use
- id: arXiv:2603.19896 | date: 2026-03 | venue: arXiv preprint
- authors: Liu, Boyan et al. | code: none seen in abstract
- relevance: MED — action selection among respond/retrieve/tool/verify/stop by estimated gain, step cost, uncertainty and redundancy
- what: Treats orchestration as an explicit decision problem with a utility policy; compared with direct answering, threshold control, fixed workflows, ReAct and policy variants. The abstract states the aim is a controllable quality-cost framework, not best accuracy, and gives no numbers.
- thesis use: idea to borrow (gain minus cost minus redundancy utility form for the selector); baseline pattern
- verified: abs meta fetched

### R2V Agent: Teaching SLMs When to Ask for Help
- id: arXiv:2605.16604 | date: 2026-05 | venue: arXiv preprint
- authors: Hemadri, Raghu Vamshi et al. | code: none seen in abstract
- relevance: MED — calibrated step-level router that escalates only when residual failure risk warrants it, reported as a reliability-cost frontier
- what: A distilled small-model policy, a teacher LLM, a process verifier scoring candidate actions each step and a router trained with Brier-calibrated probabilities and a CVaR-constrained objective. On HumanEval+ it reaches 94.3% success with 0.60% LLM escalation; on TextWorld it recovers from 64.6% to 98.2% at 41.7% escalation; on TerminalBench 93.3% at 33.9% LLM calls, about half the heuristic-router cost.
- thesis use: idea to borrow (accuracy vs. escalation-rate frontier; verifier scoring candidate actions resembles the ranker); not driving
- verified: abs meta fetched

### Knowing When to Ask: Segment-Level Credit Assignment for LLM Tool Use
- id: arXiv:2605.27788 | date: 2026-05 | venue: arXiv preprint
- authors: Kumar, Abhijit et al. | code: none seen in abstract
- relevance: MED — learns which individual tool call helped, penalising unnecessary calls
- what: CARL trains a critic on the model's own rollouts to learn where parametric knowledge suffices and where external help is needed, assigning independent credit per tool-use segment from a single binary outcome.
- thesis use: idea to borrow for per-call credit (the project's expected-gain label is a per-tool counterfactual of this kind)
- verified: abs meta fetched

### Uncertainty-Aware Vision-based Risk Object Identification via Conformal Risk Tube Prediction
- id: arXiv:2603.23919 | date: 2026-03 | venue: arXiv preprint
- authors: Fu, Kai-Yu et al. | code: project page https://hcis-lab.github.io/CRTP/
- relevance: MED — driving hazard identification with conformal coverage guarantees and a new multi-risk dataset
- what: Conformal Risk Tube Prediction models spatiotemporal risk uncertainty with coverage guarantees for true risks and calibrated risk scores. A new dataset and metrics cover multi-risk scenario configurations and perception error propagation; it reduces nuisance braking alerts (no numbers in abstract).
- thesis use: benchmark / calibration-phase reference for conformal accept/reject on driving hazards
- verified: abs meta fetched

### Vision-Based Runtime Monitoring under Varying Specifications using Semantic Latent Representations
- id: arXiv:2605.13923 | date: 2026-05 | venue: arXiv preprint
- authors: Hoxha, Bardh et al. | code: none seen in abstract
- relevance: MED — conformally certified monitor from images with finite-sample guarantees, checked on Waymo data
- what: A reusable monitor predicts atom robustness scores of past-time signal temporal logic from images under partial observability; one conformal calibration pass certifies a whole formula fragment. On a pedestrian-crossroad benchmark the semantic-basis monitor is up to 4 times tighter at long horizons; both monitors meet empirical coverage on Waymo driving data.
- thesis use: idea to borrow for the future accept/fallback phase (certified monitor on perceptual inputs)
- verified: abs meta fetched

### Distribution-Free Risk-Aware Planning and Control Under Uncertainty Using Conformal Spectral Risk Control
- id: arXiv:2606.04185 | date: 2026-06 | venue: arXiv preprint
- authors: Eom, Junsik et al. | code: none seen in abstract
- relevance: MED — conformal risk control extended to spectral risk measures inside an MPC planner, simulated vehicle obstacle avoidance
- what: Prediction sets guarantee spectral-risk constraint satisfaction without distributional assumptions and are used in risk-aware MPC; improved safety and reduced solve time versus a baseline RA-MPC in simulated vehicle obstacle avoidance (no numbers in abstract).
- thesis use: calibration phase (risk-controlled plan acceptance)
- verified: abs meta fetched

### Conformal Risk-Averse Decision Making with Action Conditional Guarantee
- id: arXiv:2606.05551 | date: 2026-06 | venue: arXiv preprint
- authors: Zhu, Zihan et al. | code: none seen in abstract
- relevance: MED — guarantees conditioned on the action taken, which fits per-candidate accept/reject
- what: Introduces action-conditional conformal prediction, shows the sets act as a proxy for the feasible decision space for risk-averse decision makers optimising action-conditional value-at-risk, and gives a finite-sample pinball-loss algorithm. Experiments on two real-world datasets improve action-conditional performance over conformal baselines.
- thesis use: calibration phase (guarantee per chosen candidate rather than marginal)
- verified: abs meta fetched

### Safe Probabilistic Planning for Human-Robot Interaction using Conformal Risk Control
- id: arXiv:2603.10392 | date: 2026-03 | venue: arXiv preprint
- authors: Gonzales, Jake et al. | code: project website https://jakeagonzales.github.io/crc-cbf-website/
- relevance: MED — conformal risk control on CBF safety values, margins adjusted by interaction context
- what: Combines control barrier functions with conformal risk control to bound constraint-violation probability around humans; on human-robot navigation it significantly reduces collision rates and safety violations versus baselines while keeping high success rates (no numbers in abstract).
- thesis use: calibration phase (context-adaptive safety margin)
- verified: abs meta fetched

### Co-GLANCE: Uncertainty-Aware Active Perception for Heterogeneous Robot Teaming
- id: arXiv:2606.09919 | date: 2026-06 | venue: arXiv preprint
- authors: Podolinsky, Michal P. et al. | code: none seen in abstract
- relevance: MED — calibrated (conformal) uncertainty with abstention directly triggers which robot acquires a new viewpoint to resolve occlusion
- what: Distils a VLM into an end-to-end model for occlusion segmentation and robot allocation; conformal prediction with selective abstention gives coverage guarantees for segmentation, allocation and detection, and these estimates trigger active perception. Outperforms cloud VLM baselines in occlusion segmentation (rest of the abstract truncated at fetch; UNVERIFIED beyond that).
- thesis use: related work for "calibrated uncertainty triggers acquisition" (scene-uncertainty-style trigger with guarantees); occlusion theme
- verified: abs meta fetched

### Leveraging the Value of Information in POMDP Planning
- id: arXiv:2604.01434 | date: 2026-04 | venue: arXiv preprint
- authors: Laouar, Zakariya et al. | code: none seen in abstract
- relevance: MED — formal value-of-information (expected performance gain from reasoning about observations) varying over the belief space
- what: A dynamic-programming framework processes observations conditionally on VOI per belief, and VOIMCP (an MCTS) skips observation branching when VOI is low. It has near-optimality guarantees and non-asymptotic convergence bounds; it outperforms baselines on several POMDP benchmarks.
- thesis use: theory citation for VOI as the quantity the selector should predict
- verified: abs meta fetched

### Non-Myopic Active Feature Acquisition via Pathwise Policy Gradients
- id: arXiv:2605.05511 | date: 2026-05 | venue: arXiv preprint
- authors: Aronsson, Linus et al. | code: none seen in abstract
- relevance: MED — active feature acquisition: choose which costly feature to acquire per instance and when to stop
- what: A continuous relaxation enables pathwise policy gradients through the full acquisition trajectory, with a straight-through rollout that matches discrete deployment and a variance bound motivating staged temperature sharpening. Better than state-of-the-art AFA baselines on synthetic and real datasets.
- thesis use: related-work framing (selector as an AFA policy); non-myopic extension if multi-step queries are ever allowed
- verified: abs meta fetched

### Zero-Shot Active Feature Acquisition via LLM-Elicitation
- id: arXiv:2606.18933 | date: 2026-06 | venue: arXiv preprint
- authors: Perets, Binyamin et al. | code: none seen in abstract
- relevance: MED — LLM supplies priors, a separate model decides acquisition
- what: The LLM is asked only for unary deviations and pairwise co-variations (sufficient statistics of a Markov random field) and acquisition is planned over that model, for binary classification and top-k identification.
- thesis use: contrast case: do not let the LLM decide, let it supply statistics (consistent with the frozen-VLM-as-feature-source result)
- verified: abs meta fetched

### Knowing When to Ask: Resolving Uncertainty in Human-Robot Joint Planning via Explicit Dialogue and Implicit Intent Cues
- id: arXiv:2603.07822 | date: 2026-03 | venue: arXiv preprint
- authors: Fang, Zeyu et al. | code: none seen in abstract
- relevance: MED — cost-optimal querying policy by dynamic programming so the robot asks only questions whose answers matter for the plan
- what: Hypothesis-augmented A* enumerates traversability hypotheses and a DP computes the querying policy; cost-optimal clarification cuts interaction cost by 51.9% at 100% task success, and implicit intent reading cuts execution time by 25.4%. Gazebo plus UAV deployments.
- thesis use: closest "query only if the answer changes the plan" precedent (plan-conditioned querying), outside driving
- verified: abs meta fetched

### Do Multimodal Agents Really Benefit from Tool Use? A Systematic Study of Capability Gains
- id: arXiv:2606.02357 | date: 2026-06 | venue: arXiv preprint
- authors: Guo, Jiawei et al. | code: none seen in abstract
- relevance: MED — evidence that tool access adds little beyond tool-free settings
- what: Studies Thyme and DeepEyesV2 against tool-free and pure-text counterparts; 93% of DeepEyesV2's tool-solved problems and 96% of Thyme's are also solved by a non-tool setting, and tool access does not reliably cut token cost.
- thesis use: caution and motivation for measuring counterfactual tool gain (the oracle-selector Pareto) rather than tool-call counts
- verified: abs meta fetched

### Probing Collision Grounding in Vision-Language Models for Safe Human-Robot Collaboration
- id: arXiv:2605.31196 | date: 2026-05 | venue: arXiv preprint
- authors: Wang, Jun et al. | code: benchmark page https://jun25336-bit.github.io/TouchSafeBench/
- relevance: MED — VLMs are weak at present and imminent collision judgement, relevant to the collision-check tool and to VLM-as-selector expectations
- what: TouchSafeBench has 2,940 simulated indoor episodes in Habitat 3.0 with multi-view RGB-D and simulator contact labels. Across three VLMs and nine visual representations the best average Macro-F1 stays below 50%; explicit depth does not automatically become collision evidence.
- thesis use: supports why geometric tools beat VLM judgement; indoor, not driving
- verified: abs meta fetched

### Q-Zoom: Query-Aware Adaptive Perception for Efficient Multimodal Large Language Models
- id: arXiv:2604.06912 | date: 2026-04 | venue: arXiv preprint
- authors: Shi, Yuheng et al. | code: none seen in abstract
- relevance: MED — a learned gate decides whether high-resolution processing is needed, then a RoI is localised
- what: A Dynamic Gating Network bypasses high-resolution processing when coarse features suffice; a Self-Distilled Region Proposal Network localises the RoI for demanding queries. Abstract is cut at fetch before the results; no numbers used.
- thesis use: analogue of the ROI tool plus gate; not driving
- verified: abs meta fetched

### CADS: Conformal Adaptive Decision System for Cost-Efficient Image Classification
- id: arXiv:2605.16401 | date: 2026-05 | venue: arXiv preprint
- authors: Turkoglu, Mikael et al. | code: none seen in abstract
- relevance: MED — conformal uncertainty routes samples through a model cascade, cost up to 12 times lower than heavy-model inference
- what: Sequential multi-model routing from lightweight "Scout" to high-capacity "Oracle" models, validated on two (clinical) datasets.
- thesis use: scene-uncertainty cascade baseline pattern
- verified: abs meta fetched

## Shortlisted but dropped
- 2604.14980 Hybrid Decision Making via Conformal VLM-generated Guidance: medical multi-label guidance for humans, not a planner.
- 2606.20491 Fast Human Attention Prediction for Fixation-guided Active Perception: gaze model on aerial robot, no candidate or tool choice.
- 2606.26529 The inattentional gap: radiology omission of co-present hazards; only a loose analogy.
- 2604.02226 When to ASK: uncertainty-gated LM queries on FrozenLake; toy and scene-uncertainty only.
- 2604.09408 HiL-Bench: coding-agent ask-for-help benchmark (Ask-F1); not perception.
- 2605.30152 Do Proactive Agents Need an LLM to Decide When to Act: assistant triggering from activity graphs.
- 2606.00096 Diversity Over Frequency: tool-use collapse in visual CoT, RL training analysis, no budget or driving.
- 2606.20728 VTOS: vision-tool orchestration search for detection programs; no query budget.
- 2604.11025 Test-time Scaling over Perception: zoom/crop trajectories for fine-grained VQA.
- 2603.22384 Learning When to Act (interval-aware RL): timing of cognitive ticks, no perception query.
- 2605.12561 Learning When to Act via Run-Time Assurance: control-update timing on pendulum/quadrotor.
- 2605.22988 Active Sensing Subserves Task-Level Control: biological theory.
- 2606.19808 Think Again or Think Longer: selective verification for text reasoning (76.3% vs 75.5% always-verify, 26.8% fewer tokens); reasoning-token allocation only, close to the query-budget idea but no perception.
- 2606.15594 Pixels to Proofs: conformal robust MPC in a latent world model; control, not query choice.
- 2605.16327 Differentiable Optimization Layered Control via Conformal Prediction: CBF layers, numerical simulation only.
- 2605.13028 Local Conformal Calibration of Dynamics Uncertainty (OCULAR): dynamics prediction regions.
- 2605.01195 TAIL-Safe: manipulation policy safety monitor.
- 2605.12651 Runtime Monitoring via Embedding Temporal Logic: monitoring language, no driving evidence in abstract.
- 2605.20566 Conflict-Aware Active Perception in 3DGS via CBFs: risk-aware EIG next-best-view for map uncertainty; mapping.
- 2604.17969 E3VS-Bench: 5-DoF viewpoint search in 3DGS indoor scenes.
- 2606.17630 FLAP: UAV FOV-constrained planning.
- 2604.23327 Beam Search for Active Perception in Mobile Robotics: graph informative-path planning.
- 2606.10986 Multi-UAV Active Sensing: terrain mapping.
- 2603.11072 OA-NBV: occlusion-aware next-best-view scoring candidate viewpoints for an occluded person (over 90% success); conceptually near (scoring candidates by visibility) but indoor viewpoint planning, not tool choice.
- 2605.07549 Probabilistic Object Detection with Conformal Prediction: box-corner CP for detection; no decision link.
- 2603.02196 Conformal Policy Control: regulating new policy against safe reference; RL deployment safety.
- 2605.20270 Conformal Selective Acting: anytime-valid risk control for RLVR LLMs.
- 2606.11349 Knowing When to Ask: Self-Gated Clarification (ACTION-RATING): taxonomy classification with LLMs.
- 2605.13050 Context Training with Active Information Seeking: LLM context optimisation with search.
- 2604.26649 When to Retrieve During Reasoning: RAG timing for text reasoning models.
- 2605.15864 Illusion of Visual Re-examination: VLM does not notice image swap; VQA reasoning, not driving.
- 2603.24974 Value of Information in Resource-Constrained Pricing: VOI in pricing regret theory.
- 2604.26169 Budget-Constrained Causal Bandits: ad treatment allocation.
- 2605.01346 CHASE: selective prediction on hidden-connectivity simulator.
- 2604.25855 SIEVES: selective prediction for VQA via visual evidence scoring; generic VQA, abstention only.
- 2606.21968 Look Before You Zoom (ViRGo): routing between retrieval and global perception for small objects in visual RAG; no driving.

## Leads not followed
- Full-text reading of 2604.14251 (CTD) and 2605.00737 (LNE) to check how the delegation value or need target is built and whether it can be conditioned on candidate set structure.
- Citing papers of 2604.14251 and 2603.00324 (conformal cascade / tool-budget lines), not looked up.
- 2606.09919 abstract was truncated in the fetch output past the occlusion-segmentation sentence; read the full abstract for its quantitative claims.
