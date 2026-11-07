# M7_listing_e3c: triage of listing_sweep/e3_02.tsv

## Summary
- No close overlap found. None of the 38 shortlisted abstracts describes candidate-conditioned perception-tool or query selection for driving. The titles in this slice are mostly generic driving, occlusion-in-other-domains and information-gain-for-RAG papers.
- Closest on the "trajectory critic over a candidate set" axis: CLOVER (generator-scorer over candidate trajectories, NAVSIM), RECTOR (rule-based reranking of a K=6 candidate set), and Reason-Imagine-Act (LLM proposes candidates, world-model rollouts, safety scorer selects). These are ranker-side references. None of them decides when to query a tool.
- Closest on the "when to look/compute" axis: Elastic Queries RL (EQRL, difficulty signal from critic-ensemble disagreement, manipulation) and Think as Needed (route frames to a shallow or deep path by geometric complexity). Both are trajectory-agnostic, scene-level triggers, so they fit the scene-uncertainty baseline family, not the proposed method.
- BA-GSAC (2605.26155) is useful evidence against scene-uncertainty triggers: ensemble disagreement stayed low under severe occlusion ("observability blindness"). Small Highway-Env RL study, so cite as a motivating observation only.
- Hazard/occlusion benchmarks: Safe2Drive (occluded VRU, work-zone and jaywalking families on Bench2Drive) and Bench2Drive-Robust (frame drop, partial observation, GPS/odometry noise, delay). Both are CARLA closed-loop, not MetaDrive.
- "Relevance modelling" (2606.10688) estimates which objects matter to the AV's decisions via counterfactuals. It is the nearest idea to decision-relevant query targets, though it works on object relevance, not tool choice.
- Nothing here on conformal or calibrated accept/reject for driving planners. 2606.03296 (CVaR tail-risk over diffusion samples) is the only risk-constrained planner, and it is not conformal.
- Titles with "occlusion" or "information gain" are overwhelmingly off-domain (person re-ID, RAG, medicine, gait). Rejected without fetching.

## Papers

### CLOVER: Closed-Loop Value Estimation and Ranking for End-to-End Autonomous Driving Planning
- id: arXiv:2605.15120 | date: 2026-05 | venue: arXiv preprint
- authors: Ang, Sining et al. | code: none seen in abstract
- relevance: MED. Generator-scorer planner that ranks candidate trajectories by predicted planning sub-scores, so it is a reference for the ranker stage.
- what: A generator proposes diverse candidate trajectories and a scorer predicts planning-metric sub-scores to rank them. Training uses evaluator-filtered pseudo-expert trajectories and closed-loop self-distillation toward teacher-selected top-k and Pareto targets. Reports 94.5 PDMS and 90.4 EPDMS on NAVSIM and 48.3 EPDMS on the NavHard split.
- thesis use: related work for the ranker and for "scorer quality limits proposal selection"; idea to borrow is the oracle-best-by-evaluator target.
- verified: abs meta fetched

### RECTOR: Priority-Aware Rule-Based Reranking for Compliance-Aware Autonomous Driving Trajectory Selection
- id: arXiv:2605.25095 | date: 2026-05 | venue: arXiv preprint
- authors: Hajieghrary, Hadi et al. | code: none seen in abstract
- relevance: MED. Selects one trajectory from a K=6 candidate set with a tiered rule scorer and tests against corrupted confidence.
- what: A post-generation reranker scores candidates against a Safety > Legal > Road > Comfort rulebook and selects lexicographically, without retraining the predictor. On Waymo Open Motion Dataset validation_interactive (43,219 augmented instances) it cuts Safety+Legal violations from 28.58% to 20.42% and Total from 40.32% to 32.41% versus confidence-only. Under adversarial confidence corruption, confidence-only fails in 100% of scenarios while the rule-aware selectors reject the injected mode in about 96%. Authors say results are proxy-evaluator, open-loop.
- thesis use: candidate-set selection baseline or ranker alternative; the rule tiers could define an oracle-best candidate; open-loop proxy caveat matches the project's setting.
- verified: abs meta fetched

### Reason-Imagine-Act: Closed-Loop LLM Decision Making with World Models for Autonomous Driving
- id: arXiv:2605.24004 | date: 2026-05 | venue: arXiv preprint
- authors: Sun, Zhengqi et al. | code: github.com/pku-smart-city/source_code (RIA directory, from abstract)
- relevance: MED. LLM proposes an action template and candidate sub-actions, a world model rolls them out, a safety scorer picks one: a candidate-then-verify loop.
- what: Per step the LLM proposes candidates, a world model does short-horizon rollouts and a safety scorer selects the safest executable action, with feedback to the next reasoning step. In a CARLA point-goal protocol (1000 episodes) RIA reaches 80.05% route completion, 51.10% arrival rate and 0.20% collision rate, ahead of training-free baselines CARLA TM and MADA.
- thesis use: related work for candidate verification with a learned model as the "tool"; no query-budget notion.
- verified: abs meta fetched

### Safe2Drive: Evaluating Safe Driving Behaviors of E2E Autonomous Driving Models
- id: arXiv:2606.00191 | date: 2026-05 | venue: arXiv preprint
- authors: Sahu, Nishad et al. | code: none seen in abstract
- relevance: MED. Hazard benchmark with an occluded-VRU family, which is one of the project's three hazard types.
- what: 100 Bench2Drive-aligned scenarios in three families (work zones, pedestrian jaywalking, occluded vulnerable road users) plus a SafeDriving Score. LEAD falls from 94.70 DS on Bench2Drive to 39.95 on S2D, and SimLingo from 85.07 to 41.00; SDS is 11.85 and 15.27.
- thesis use: citation for "occlusion hazards break current planners"; scenario-design reference for the MetaDrive hazards.
- verified: abs meta fetched

### Bench2Drive-Robust: Benchmarking Closed-Loop Autonomous Driving under Deployment Perturbations
- id: arXiv:2605.18059 | date: 2026-05 | venue: arXiv preprint
- authors: Zhang, Zhiyuan et al. | code: none seen in abstract
- relevance: MED. Perturbation benchmark for E2E driving that is analogous to the project's tool-noise levels, but perturbs the planner's inputs, not the tools.
- what: Closed-loop benchmark of camera-stream failures (frame drop, partial observation), ego-state errors (GPS noise, speed/odometry error) and model inference delay. Evaluates representative E2E methods at several severities and reports substantial closed-loop degradation (no numbers in the abstract).
- thesis use: related work for noise-severity design; contrasts with the open-loop protocol used here.
- verified: abs meta fetched

### Self-Supervised Relevance Modelling in Autonomous Driving via Counterfactual Analysis
- id: arXiv:2606.10688 | date: 2026-06 | venue: arXiv preprint
- authors: Lusvarghi, Luca et al. | code: abstract says the dataset and model are openly released (URL not in the fetched text)
- relevance: MED. Learns which objects matter for the AV's decisions via counterfactual removal, to focus perception compute.
- what: A relevance model is trained self-supervised on a synthetic causal dataset in one urban scenario and estimates object relevance with millisecond-level latency. Relevance heatmaps are proposed as proactive inputs to perception and planning.
- thesis use: idea to borrow for decision-relevance labels; complements the "expected gain" targets.
- verified: abs meta fetched

### Elastic Queries Reinforcement Learning: Self-Aware Policy Execution for VLA Models
- id: arXiv:2606.14375 | date: 2026-06 | venue: arXiv preprint
- authors: Wang, Ge et al. | code: none seen in abstract
- relevance: MED. Learns, per query, how much compute and how long an open-loop chunk to use, under an amortized NFE budget. It is manipulation, not driving.
- what: A latent-schedule adaptor picks latent input, denoising budget and chunk length without fine-tuning the VLA. A critic ensemble's disagreement gives a state difficulty signal. Reduces amortized inference cost while preserving or improving task success, across simulation and real-robot manipulation.
- thesis use: example of a disagreement-based scene-difficulty trigger under a budget; fits the scene-uncertainty baseline family.
- verified: abs meta fetched

### When Does Adaptive Guidance Help? Belief-Aware Privileged Distillation for Autonomous Driving Under Partial Observability
- id: arXiv:2605.26155 | date: 2026-05 | venue: arXiv preprint
- authors: Haklidir, Mehmet | code: none seen in abstract
- relevance: MED. Finds that ensemble disagreement does not detect missing information under occlusion.
- what: BA-GSAC modulates the privileged-distillation coefficient by ensemble disagreement; tested on Highway-Env at three POMDP levels. Under severe occlusion (3 seeds) the coefficient collapses to its minimum within about 3K steps, because the ensemble models only what is visible. A linear-decay schedule performed best in severe POMDP (mean 116.5, CV=8.9%). The authors mark their proposed fix as not validated.
- thesis use: supporting argument that scene-uncertainty triggers are blind to occluded hazards; weak evidence (RL, small seeds).
- verified: abs meta fetched

### Think as Needed: Geometry-Driven Adaptive Perception for Autonomous Driving
- id: arXiv:2605.10117 | date: 2026-05 | venue: arXiv preprint
- authors: Kim, Donghyun et al. | code: none seen in abstract
- relevance: MED. Scene-complexity-triggered shallow/deep perception routing, i.e. a trajectory-agnostic compute trigger.
- what: Enhanced HOPE measures the geometric complexity of each LiDAR frame without labels and routes it through a shallow or deep path, with a memory module for occluded objects. On nuScenes and CARLA it cuts latency 38% on simple scenes with no accuracy loss, adds 2.7 mAP on rare long-tail scenarios, and tracks objects through occlusions longer than 5 seconds.
- thesis use: example competitor for the "scene-uncertainty" baseline family (scene-level routing, no candidate conditioning).
- verified: abs meta fetched

### Intend, Reflect, Refine: An Adaptive Multimodal Reflection Framework for Autonomous Driving
- id: arXiv:2606.22913 | date: 2026-06 | venue: arXiv preprint
- authors: Chen, Zisheng et al. | code: none seen in abstract
- relevance: MED. VLA that picks its reasoning mode by scene complexity and reflects on a preliminary intent before the final trajectory.
- what: IRR-Drive writes a textual intention, predicts future semantic BEV, then refines the trajectory; an adaptive reflection reward lets the model choose its reasoning mode by scene complexity. The abstract claims state-of-the-art PDMS and EPDMS on NAVSIM (no numbers in the fetched text).
- thesis use: think-vs-look switching competitor in the DriveAgent-R1 family; trigger is scene-based.
- verified: abs meta fetched

### A Query-Driven Communication-Efficient Digital Twins Design for Autonomous Driving
- id: arXiv:2606.28384 | date: 2026-06 | venue: arXiv preprint
- authors: Yang, Nuocheng et al. | code: none seen in abstract
- relevance: MED. A digital twin actively requests environment data from the vehicle based on its own simulation result, under a communication constraint.
- what: Formulates minimizing planning position error under fidelity and communication limits, with a cross-time-step progressive query mechanism. Reports a 24% lower planning position error versus traditional methods and 40% lower communication overhead.
- thesis use: conceptually a budgeted, simulation-conditioned query; wireless setting, so only an analogy.
- verified: abs meta fetched

### Uncertainty-Aware Clarification in LLM Agents with Information Gain
- id: arXiv:2606.03135 | date: 2026-06 | venue: arXiv preprint
- authors: Deng, Mengyi et al. | code: none seen in abstract
- relevance: MED. Trains a clarifier with an Information Gain Reward (Bayesian belief update toward the true goal), which is a value-of-information target for deciding what to ask.
- what: Evaluated in a clarification-enhanced tau-Bench with five backbones; success improves 3.7% over the no-clarification baseline with 0.3 extra interaction steps on average.
- thesis use: idea to borrow for the expected-gain label; not driving.
- verified: abs meta fetched

### Uncertainty-Aware and Temporally Regulated Expert Advice in Reinforcement Learning for Autonomous Driving
- id: arXiv:2605.30576 | date: 2026-05 | venue: arXiv preprint
- authors: Abouelazm, Ahmed et al. | code: none seen in abstract
- relevance: MED. Requests expert help when epistemic or aleatoric uncertainty exceeds adaptive thresholds, within an advice budget.
- what: Commitment-cooldown and stochastic early-stop regulate duration and frequency of guidance; built on an IQN backbone in CARLA unsignalized intersections. Improves success by 5-7% over the IQN baseline.
- thesis use: defer/ask-for-help trigger example; trigger is uncertainty-only, like the scene-uncertainty baseline.
- verified: abs meta fetched

### Bridging Predictive Uncertainty and Safe Action: Sample-Conditioned Differentiable Planning for Autonomous Driving
- id: arXiv:2606.03296 | date: 2026-06 | venue: arXiv preprint
- authors: Meng, Chengzhen et al. | code: none seen in abstract
- relevance: MED. Diffusion-sampled futures feed a differentiable planner with an empirical CVaR tail-risk constraint.
- what: Not conformal, but a risk-constrained planner over sampled scenarios, plus a directed-graph scene representation. Validation numbers were cut off in the fetched abstract view, so none are quoted.
- thesis use: related work for the future risk-control phase.
- verified: abs meta fetched

### Beyond the Visible: Benchmarking Occlusion Perception in Multimodal Large Language Models
- id: arXiv:2508.04059 | date: 2025-08 | venue: arXiv preprint
- authors: Liu, Zhaochen et al. | code: none seen in abstract
- relevance: MED. Supports the frozen-VLM finding: 22 MLLMs lag humans on occlusion perception, and scale or thinking does not close the gap.
- what: O-Bench has 1,365 images and 4,588 QA pairs across five tasks, built from SA-1B. Failure patterns include an overly conservative bias.
- thesis use: citation for why prompting the VLM to pick a tool says "none"; not driving.
- verified: abs meta fetched

## Shortlisted but dropped
- 2605.25393 Decision-Making with Lightweight Confidence-Aware Language Model: high-level decision LM on nuPlan, no perception queries or candidate set.
- 2606.08470 LUNA-AD: same group and design, no query or selection.
- 2605.22189 Learning A Unified Risk Map ... Partially Observable Environments: occlusion risk map for planning, no query selection. LOW.
- 2605.09774 DRIVE-C: camera-corruption video dataset (10 clean clips), perception robustness only.
- 2606.17541 Offline Preference-Based Trajectory Evaluation: "trajectory" means agent rollouts, not driving.
- 2606.19998 Tri-Info: VLA failure prediction from information signals, manipulation.
- 2601.21504 Don't double it (MatchInformer): occluded agent occupancy prediction, no query decision.
- 2606.15046 APRO: exact occlusion-aware planning for valet parking with reachability; no learned query or candidate set.
- 2602.23051 Cooperative perception for occlusion risk: V2X deployment analysis.
- 2602.23109 Active inference for occluded pedestrians: belief-driven controller, no tool or candidate-selection angle.
- 2606.30807 Derail: adversarial attack on candidate scoring heads (score drops of 39-80%); relevant as a ranker-fragility note only.
- 2606.20641 MAGNIFIED: RL fine-tuning of MLLM planner, no query.
- 2605.31256 Before Parc Ferme: pruning embodied LLMs.
- 2605.29138 Multi-Resolution E2E DNN: resolution selection under a latency budget, scene-agnostic image-level choice.
- 2606.14438 CADET causal auditing of planners: shortcut audit, not query selection.
- 2606.12706 VLADriveBench: CoT-action consistency metrics.
- 2605.30983 Grace-BEV: sensor-failure fusion robustness.
- 2511.08640 Predict and Resist: accident anticipation under sensor noise; alert-timing actor-critic, not tool selection.
- 2606.28758 X-Mind: visual CoT world model for VLA.
- 2605.16892 DriveSafe: caption-based risk assessment.
- 2605.06264 Can Attribution Predict Risk: attribution statistics as planning risk signals; interesting but no query selection.
- 2511.18353 UAV next-best-view under occlusion: forest search, not driving; viewpoint-selection analogy only.
- 2606.20274 Lagrange: open-vocabulary sparse E2E driving, no query.

## Leads not followed
- Titles about occlusion/information gain from other fields (re-ID, RAG, medicine) were skipped as off-domain.
- Full-text reads of Bench2Drive-Robust and Safe2Drive for scenario definitions were not done.
