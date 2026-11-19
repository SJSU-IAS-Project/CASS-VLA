# M6_listing_e3b (listing sweep e3_01, 413 titles, 32 shortlisted, all abstracts fetched)

## Summary
- No close overlap found. Nothing in this slice does candidate-conditioned perception-tool or query selection for driving.
- Closest in spirit: PRAM-R (LLM router picks which sensor modalities to run to save compute) and the situation-aware MPC switching paper (a classifier decides when to invoke the costly module). Both are trajectory-agnostic, scene-triggered gating, so they are useful as scene-uncertainty-style baselines/related work, not competitors.
- Trajectory scoring over candidate sets: SafeDrive (trajectory-conditioned collision-risk reasoning), CdDrive (jointly scores vocabulary plus diffusion candidates), KnowVal (value model for trajectory assessment), MTDrive (multi-turn MLLM refinement from feedback). All are NAVSIM/Bench2Drive and none acquires extra perception.
- "Trigger expensive step only when needed" pattern shows up in manipulation VLAs (VLA-ATTC uncertainty clutch plus pairwise action critic, Sentinel-VLA, SV-VLA verifier-triggered replanning, VLA UQ with spike pooling). Ideas transfer to the accept/replan phase; domain does not.
- LSRE converts sparse VLM judgments into a latent classifier so the VLM is not queried every frame; relevant to the frozen-VLM-features angle and the VLM-cost argument.
- Calibration/future phase: class-uncertainty propagation in nuPlan planning (miscalibration impact) and effort-based criticality metrics (which perception errors actually matter for braking/evasion) support a decision-relevant, rather than detection-accuracy, notion of error.
- The listing keywords mostly hit generic driving/VLA papers; yield for this slice is low (about 8% shortlisted, 17 kept).

## Papers

### PRAM-R: A Perception-Reasoning-Action-Memory Framework with LLM-Guided Modality Routing for Adaptive Autonomous Driving
- id: arXiv:2603.04222 | date: 2026-03 | venue: arXiv preprint
- authors: Zhang, Yi et al. | code: none seen
- relevance: MED — selects which sensor modalities to run to cut cost, a scene-context (trajectory-agnostic) query-selection baseline in driving.
- what: Asynchronous dual loop; an LLM router selects and weights modalities from environmental context and sensor diagnostics, with hysteresis stabilization. Abstract reports 87.2% fewer routing oscillations in synthetic stress tests, and on nuScenes 6.22% modality reduction with 20% memory recall at comparable trajectory accuracy to full-modality baselines.
- thesis use: related work for budgeted perception; contrast with candidate-conditioned selection (modest 6.22% saving shows little headroom for scene-only routing).
- verified: abs meta fetched

### Situation-Aware Interactive MPC Switching for Autonomous Driving
- id: arXiv:2512.06182 | date: 2025-12 | venue: arXiv preprint
- authors: Qi, Shuhao et al. | code: none seen
- relevance: MED — learned classifier decides when to invoke the expensive controller, a compute-vs-accuracy gating of the same shape as tool calling.
- what: Compares MPC formulations of different interaction fidelity, ranks them, and trains a neural classifier to switch among them. Invokes the advanced MPC only in rare critical situations; the abstract claims better overall performance with significantly lower compute (no numbers in abstract).
- thesis use: related work for "when to call the costly module"; scene-triggered baseline analogue.
- verified: abs meta fetched

### LSRE: Latent Semantic Rule Encoding for Real-Time Semantic Risk Detection in Autonomous Driving
- id: arXiv:2512.24712 | date: 2025-12 | venue: arXiv preprint
- authors: Cheng, Qian et al. | code: none seen
- relevance: MED — avoids per-frame VLM queries by distilling sparse VLM judgments into a latent classifier; VLM-cost and frozen-VLM-signal angle, CARLA.
- what: Converts sparsely sampled VLM judgments into decision boundaries in a recurrent world model's latent space, enabling 10 Hz semantic risk assessment. On six CARLA semantic-failure scenarios it reaches accuracy comparable to a large VLM baseline with earlier hazard anticipation.
- thesis use: idea to borrow (distill VLM into cheap head); related work for VLM-in-the-loop cost.
- verified: abs meta fetched

### SafeDrive: Fine-Grained Safety Reasoning for End-to-End Driving in a Sparse World
- id: arXiv:2602.18887 | date: 2026-02 | venue: arXiv preprint
- authors: Kim, Jungho et al. | code: none seen
- relevance: MED — trajectory-conditioned world model plus agent-specific collision-risk evaluation, close to the "collision check against tracked actors" tool and to scoring candidates.
- what: SWNet builds trajectory-conditioned sparse worlds of critical agents; FRNet scores agent-specific collision risk and drivable-area adherence. NAVSIM PDMS 91.6, EPDMS 87.5, 61 collisions out of 12,146 scenarios; Bench2Drive driving score 66.8%.
- thesis use: idea to borrow for the collision-check tool and ranker features.
- verified: abs meta fetched

### A Unified Candidate Set with Scene-Adaptive Refinement via Diffusion for End-to-End Autonomous Driving (CdDrive)
- id: arXiv:2602.03112 | date: 2026-02 | venue: arXiv preprint
- authors: Wu, Zhengfei et al. | code: https://github.com/WWW-TJ/CdDrive
- relevance: MED — multi-candidate generate-and-select with a shared scorer; candidate-set design matters for how candidates diverge.
- what: Keeps fixed-vocabulary candidates and adds vocabulary-conditioned diffusion candidates, jointly scored by one selection module; HATNA smooths diffusion candidates. Evaluated on NAVSIM v1 and v2 (abstract gives no numbers).
- thesis use: source of candidate sets/scorers for later real-data phase.
- verified: abs meta fetched

### KnowVal: A Knowledge-Augmented and Value-Guided Autonomous Driving System
- id: arXiv:2512.20299 | date: 2025-12 | venue: arXiv preprint
- authors: Xia, Zhongyu et al. | code: none seen
- relevance: MED — Value Model trained on human preferences for trajectory assessment, plus LLM knowledge retrieval (a retrieval "query" step).
- what: Builds a driving knowledge graph (laws, defensive driving, ethics) with LLM retrieval and trains a Value Model to guide value-aligned trajectory assessment. Lowest collision rate on nuScenes; state-of-the-art on Bench2Drive and NVISIM (per abstract).
- thesis use: trajectory critic related work.
- verified: abs meta fetched

### MTDrive: Multi-turn Interactive Reinforcement Learning for Autonomous Driving
- id: arXiv:2601.22930 | date: 2026-01 | venue: arXiv preprint
- authors: Li, Xidong et al. | code: promised, not yet released
- relevance: MED — MLLM iteratively refines trajectories from environmental feedback; multi-turn loop analogous to a look-then-decide agent (feedback is not a perception tool though).
- what: mtGRPO computes relative advantages across turns; interactive trajectory-understanding dataset from closed-loop simulation; NAVSIM results claimed superior; 2.5x training throughput from system optimizations.
- thesis use: competitor-adjacent related work for multi-turn driving agents.
- verified: abs meta fetched

### VLA-ATTC: Adaptive Test-Time Compute for VLA Models with Relative Action Critic Model
- id: arXiv:2605.01194 | date: 2026-05 | venue: arXiv preprint
- authors: Li, Wenhao et al. | code: promised
- relevance: MED — uncertainty-based gate decides when to deliberate, then a pairwise critic picks the best of generated candidates; same gate-plus-candidate-critic structure, manipulation domain.
- what: "Cognitive clutch" switches from reflexive execution to test-time compute; Relative Action Critic ranks candidates by pairwise comparison. On LIBERO-LONG it cuts the failure rate of PI0.5 by over 50%.
- thesis use: idea to borrow (pairwise relative ranker for the ranker stage).
- verified: abs meta fetched

### Sentinel-VLA: A Metacognitive VLA Model with Active Status Monitoring for Dynamic Reasoning and Error Recovery
- id: arXiv:2605.01191 | date: 2026-05 | venue: arXiv preprint
- authors: Li, Wenhao et al. | code: promised
- relevance: MED — reasons only when a monitor says so, minimizing compute; manipulation.
- what: A sentinel module monitors execution and triggers reasoning at initial planning or on error detection; data auto-generated (44 tasks, over 2.6 million transitions). Real-world success up over 30% versus PI0.
- thesis use: related work for on-demand reasoning triggers.
- verified: abs meta fetched

### Open-Loop Planning, Closed-Loop Verification: Speculative Verification for VLA (SV-VLA)
- id: arXiv:2604.02965 | date: 2026-04 | venue: arXiv preprint
- authors: Wang, Zihua et al. | code: https://github.com/edsad122/SV-VLA
- relevance: MED — lightweight verifier compares planned action to a closed-loop reference and triggers replanning only when needed; analogous to the future accept/replan policy.
- what: Heavy VLA as low-frequency planner, light verifier monitors latest observations. Abstract gives no numbers.
- thesis use: idea for accept/replan trigger.
- verified: abs meta fetched

### Shifting Uncertainty to Critical Moments: Towards Reliable Uncertainty Quantification for VLA Model
- id: arXiv:2603.18342 | date: 2026-03 | venue: arXiv preprint
- authors: Tang, Yanchuan et al. | code: none seen
- relevance: MED — failure prediction from uncertainty with max-pooling over windows so brief spikes are not diluted; relevant to calibrated accept/reject.
- what: Max-based sliding-window pooling, motion-aware stability weighting, DoF-adaptive calibration via Bayesian optimization; improves failure prediction on LIBERO (no numbers in abstract).
- thesis use: idea for the calibration phase.
- verified: abs meta fetched

### The Impact of Class Uncertainty Propagation in Perception-Based Motion Planning
- id: arXiv:2602.16035 | date: 2026-02 | venue: arXiv preprint
- authors: Shah, Jibran Iqbal et al. | code: none seen
- relevance: MED — measures how upstream perception-uncertainty calibration affects closed-loop planning on nuPlan; supports the tool-noise-to-plan-quality link.
- what: Compares two prediction-planning pipelines with different uncertainty propagation on nuPlan challenge scenarios; propagation generalizes better in complex closed-loop scenarios.
- thesis use: related work for noisy perception and calibration.
- verified: abs meta fetched

### Effort-Based Criticality Metrics for Evaluating 3D Perception Errors in Autonomous Driving
- id: arXiv:2603.28029 | date: 2026-03 | venue: arXiv preprint
- authors: Kaul, Sharang et al. | code: none seen
- relevance: MED — scores perception errors by the braking/evasion effort they cause (decision-relevant error), which parallels deriving an oracle from consequences rather than detection accuracy.
- what: False Speed Reduction, Maximum Deceleration Rate, Lateral Evasion Acceleration with reachability gate. On nuScenes and Argoverse 2, 65% to 93% of errors fall below the chosen criticality thresholds.
- thesis use: idea for "decision-relevant error" framing and tool-noise analysis.
- verified: abs meta fetched

### Risk-Aware Rulebooks for Multi-Objective Trajectory Evaluation under Uncertainty
- id: arXiv:2603.04603 | date: 2026-03 | venue: arXiv preprint
- authors: Wongpiromsarn, Tichakorn | code: none
- relevance: MED — formalism to rank trajectories under uncertain environment responses, with a preorder guaranteeing consistent preferences; relevant to defining the oracle best candidate.
- what: Evaluates trajectories under the distribution of environment responses; proves a preorder; illustrated with a driving example (no empirical numbers).
- thesis use: oracle/ranking definition reference.
- verified: abs meta fetched

### Sensor Query Schedule and Sensor Noise Covariances for Accuracy-constrained Trajectory Estimation
- id: arXiv:2602.16598 | date: 2026-02 | venue: arXiv preprint
- authors: Goudar, Abhishek et al. | code: none seen
- relevance: MED (LOW for method) — formal sensor-query-rate versus accuracy trade-off via semidefinite programs; vocabulary of query budget for state estimation, not planning.
- what: Computes the sensor schedule or noise covariance needed for a target estimation accuracy, validated in simulation and real experiments; flags infeasible accuracy targets.
- thesis use: citation for query-budget framing only.
- verified: abs meta fetched

## Shortlisted but dropped
- 2601.10707 See Less, Drive Better (SPS) — random patch masking for OOD robustness, not query selection.
- 2601.07092 Efficient VQA via Scene Region Compression — token compression for latency, no decision on what to query.
- 2603.15364 CRASH — LLM crash-report analysis from NHTSA reports, off-topic.
- 2512.16055 Driving in Corner Case — adversarial closed-loop eval on UniAD/VAD with generated images; no hazard/occlusion fit to MetaDrive setup.
- 2512.23215 AVOID — obstacle-detection dataset (CARLA); perception benchmark, no planning decision.
- 2604.20895 Systematic Risk Assessment of DNN Limitations — ISO HARA/TARA workflow, no experiments.
- 2603.02772 SERP — planner parameter adaptation, not perception queries.
- 2603.03704 CoCo-TAMP — manipulation TAMP with LLM belief priors.
- 2604.00401 Task and kinodynamic planning under semantic uncertainty — LTLf POSHS, not driving perception.
- 2604.01337 SECURE — accident-anticipation robustness, no query selection.
- 2601.05806 Modular Autonomy with Conversational Interaction — passenger LLM commands, off-topic.
- 2603.03514 MOPS-PRM — perception-constrained manipulation planning.
- 2512.07130 Mimir — goal-point uncertainty for diffusion planning, not tool use.
- 2512.15195 EPSM — perception safety metric; superseded by effort-based metrics entry.
- 2604.15291 AD4AD — anomaly-detection benchmark, no planner coupling.
- 2602.21445 AutoHorizon — adaptive execution horizon for manipulation VLAs.
- 2604.23513 LLM Interactive Decision-Making — LLM intent parsing and eHMI; candidate evaluation by MC sampling but no perception acquisition.

## Leads not followed
- Rest of the 413 titles were screened by title only; titles such as 2603.15185 (What Matters for Scalable and Robust Learning in E2E Planners) and 2604.10856 BridgeSim (OL-CL gap) may bear on open-loop evaluation validity but were not fetched.
