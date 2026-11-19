# L3_listing_t3a (listing sweep, t3_00.tsv, 346 titles)

## Summary
- No close overlap found. Nothing in this slice does candidate-conditioned perception-tool/query selection for a driving planner.
- Closest on "decide whether to query": Risk-Adaptive Edge-Cloud (2608.14991) uses an onboard risk trigger to decide when to call a cloud VLM. It is a trajectory-agnostic, scene-risk trigger, the same family as the scene-uncertainty baseline. SAGE (2608.29772) is a similar deferral trigger with an adaptive threshold, tested on CARLA occlusion hazards.
- Closest on "score K candidates": Versatile Samples for Learned Trajectory Scoring (2609.01799) and SVA (2607.03751, manipulation) train a separate scorer/critic over a frozen planner's candidate pool. PDT (2609.02688) analyses when proposal-ordering gains transfer to selected-trajectory utility. Useful as ranker/oracle-gap framing.
- Relevant to the frozen-VLM-feature result: Auditing Latent-Space Monitors (2609.30557) finds that latent probes add nothing over planner outputs plus ego state. Consistent with the small +0.3 to +0.7 gain seen from cached embeddings, and a warning to report an outputs-only control.
- Future calibration phase: SAFECAST (2608.04246, VLA failure detection with conformal calibration under shift) and Gating Before Commitment (2608.26074, abstention on uncertainty cuts false triggers).
- Benchmarks/hazards: DriveDegrade (2608.29005) and counterfactual pedestrian-removal diagnosis (2609.22582) are open-loop NAVSIM/nuScenes probes that could inspire hazard injection.
- Trend: many "adaptive reasoning/routing" papers (fast vs slow) decide how much to think, not which sensor query to make.
- Already in other raw files and skipped: 2607.00399 (DriveVer), 2609.22762 (DriveReferee).

## Papers

### Risk-Adaptive Edge--Cloud Visual Reasoning for Communication-Efficient Autonomous Driving
- id: arXiv:2608.14991 | date: 2026-08 | venue: arXiv preprint
- authors: Ma, Meng et al. | code: none seen
- relevance: HIGH — learns/decides when to call an expensive VLM under a cost (cloud request) budget in driving, trajectory-agnostic trigger.
- what: Onboard VLM plus lightweight detector assess traffic and path-relative hazards and decide when to request cloud VLM advice. In CARLA it matched the task success of periodic cloud access with 54.1% fewer cloud requests and fewer AEB activations.
- thesis use: competitor/baseline family for the scene-uncertainty trigger; supports the accuracy-vs-query-cost framing.
- verified: abs meta fetched

### Self-Aware Active Learning Enables Continual Improvement in Autonomous Driving (SAGE)
- id: arXiv:2608.29772 | date: 2026-08 | venue: arXiv preprint
- authors: Hu, Dong et al. | code: none seen
- relevance: HIGH — estimates when competence is insufficient and hands control to expert/fallback; evaluated incl. CARLA occlusion hazards.
- what: A world model yields "fear" (short-horizon predictive risk and uncertainty) and "curiosity" (prediction error) signals; curiosity adapts the fear threshold for takeover. Evaluated on route transfer, Waymo logs, CARLA occlusion hazards and a mobile robot.
- thesis use: baseline for scene-level deferral; idea for adaptive threshold; fallback-policy phase.
- verified: abs meta fetched

### Designing Versatile Samples for Learned Trajectory Scoring
- id: arXiv:2609.01799 | date: 2026-09 | venue: arXiv preprint
- authors: Li, Yaguang et al. | code: https://github.com/PurdueDigitalTwin/Versatile-Scoring
- relevance: HIGH — trained scorer that selects one trajectory from a candidate pool of a frozen planner.
- what: Notes that planners' proposals cluster around safe modes, so supervision near decision boundaries is thin. Builds lateral/longitudinal perturbation generators of the logged trajectory as extra training samples; a transformer scorer on frozen DiffusionDrive and MeanFuser reaches 90.1 and 90.4 EPDMS on NAVSIM navtrain (gains of 0.4 and 0.3).
- thesis use: idea to borrow (candidate-set construction so candidates diverge near decision boundaries); ranker design.
- verified: abs meta fetched

### Look Before You Leap: Distilling Tree Search into Action Evaluation for Frozen VLA Models (SVA)
- id: arXiv:2607.03751 | date: 2026-07 | venue: arXiv preprint
- authors: Xie, Xinyi et al. | code: none seen
- relevance: MED — candidate-action evaluator over a frozen policy with uncertainty-regularized Q; manipulation, not driving.
- what: A frozen VLA proposes multiple candidates and a distilled lightweight Q-model picks the highest uncertainty-regularized one. Real-robot average success rises from 42.8% to 55.6%; pass@k on frozen VLAs goes from 33% (pass@1) to 92% (pass@32).
- thesis use: idea (propose-then-evaluate with frozen backbone; oracle-best-of-k as upper bound).
- verified: abs meta fetched

### From Proxy Learning to Driving Decisions: A Transfer-Based Framework for Evaluating Future-Aware Autonomous Driving Planners (PDT)
- id: arXiv:2609.02688 | date: 2026-09 | venue: arXiv preprint
- authors: Wu, Yikai | code: none seen
- relevance: MED — evaluation methodology for proposal-based planners; separates support (is the best candidate present) from selection regret.
- what: Decision-Transfer Decomposition (score margins, switch-conditioned utility, support-vs-selection regret) and a reliability-constrained validation. On NAVSIM-v1, component BCE falls from 0.705 to 0.530 while held selected PDM falls from 0.963 to 0.961.
- thesis use: evaluation idea (report regret vs oracle candidate, paired bootstrap for small gains).
- verified: abs meta fetched

### Auditing Latent-Space Monitors for Autonomous Driving
- id: arXiv:2609.30557 | date: 2026-09 | venue: arXiv preprint
- authors: Advani, Nikhil Kamalkumar et al. | code: per-frame labels released (url not seen)
- relevance: MED — failure monitors from model latents; relevant to frozen-feature gains and runtime failure prediction.
- what: On LaneSegNet and VAD, latent probes reach AUROC 0.780 (map) and 0.868 (VAD mean-ADE), but output-only monitors reach 0.825 and 0.924 (ego state, command and predicted trajectory for VAD); adding latents gives no statistically resolved gain.
- thesis use: contradicts/cautions the value of embeddings; add an outputs-only control; failure monitor for the future phase.
- verified: abs meta fetched

### SAFECAST: Robust Failure Detection for VLA Policies with Contrast-Set Training and Calibration
- id: arXiv:2608.04246 | date: 2026-08 | venue: arXiv preprint
- authors: Rajaprakash, Harshitha et al. | code: none seen
- relevance: MED — hidden-state risk probes with functional conformal prediction, calibration under deployment shift (manipulation).
- what: Contrast-set perturbations (visual and language) augment probe training and calibration; improves failure-detection ROC-AUC over the baseline on DROID (real) and LIBERO (sim). Sim-to-real calibration beat real-only rollouts.
- thesis use: idea for the conformal accept/reject phase; calibration under shift.
- verified: abs meta fetched

### Gating Before Commitment: Anticipating Intent Divergence to Prevent Post-Interaction Decision Failures in Autonomous Driving
- id: arXiv:2608.26074 | date: 2026-08 | venue: arXiv preprint
- authors: Xu, Cong et al. | code: none seen
- relevance: MED — gate on the planned maneuver before commitment, with uncertainty treated as abstention.
- what: Intent-geometry divergence score gates the plan; fires 72 ms after drift onset, 161 ms before corridor exit, in all ten replays. Treating uncertainty as abstention cut false triggers from nine in 5.9 min to 0.341 per minute. Very small evidence base (five clips).
- thesis use: weak idea for abstention/fallback phase.
- verified: abs meta fetched

### Cognitive Dual-Process Planning for Autonomous Driving with Structured Scene Knowledge and Verifiable Reasoning-Action Consistency
- id: arXiv:2607.19194 | date: 2026-07 | venue: arXiv preprint
- authors: Yang, Zhongyao et al. | code: none seen
- relevance: MED — a lightweight visual Arbiter from encoder features routes to fast vs slow reasoning (decides whether to spend compute).
- what: Arbiter estimates scene complexity before decoding. On 574 verified NAVSIM samples: 80.14% planning accuracy, 97.20% LCS, 17.39% lower average latency than always slow reasoning.
- thesis use: baseline family (trajectory-agnostic complexity trigger from frozen encoder features).
- verified: abs meta fetched

### When Does Corruption Break the Plan? A Degradation-Tolerance Benchmark for Camera-Only End-to-End Driving (DriveDegrade)
- id: arXiv:2608.29005 | date: 2026-08 | venue: arXiv preprint
- authors: Que, Haohua et al. | code: none seen
- relevance: MED — sensor-perturbation benchmark at the planning-output level.
- what: 16 corruption families at 5 severities, 15 policies, open-loop nuScenes/NAVSIM plus CARLA closed-loop anchor. Blur, JPEG and raindrop damage planning most; a released VLA planner loses only 11.5% when all six cameras are blinded.
- thesis use: benchmark idea for tool-noise levels; shows ego-status shortcut risk.
- verified: abs meta fetched

### Beyond the Leaderboard: Counterfactual Diagnosis of End-to-End and VLA Driving Policies Under Domain Shift
- id: arXiv:2609.22582 | date: 2026-09 | venue: arXiv preprint
- authors: Yang, Ruolin et al. | code: promised, not seen
- relevance: MED — counterfactual edits (pedestrian removed, relit) test whether plans respond to hazards.
- what: Six released policies, 246 NAVSIM near-pedestrian scenes; when the pedestrian lies on the planned path only 1.9% of responses are genuine avoidance, with median clearance change at most 0.03 m.
- thesis use: benchmark idea; evidence that planners ignore hazards, motivating perception queries.
- verified: abs meta fetched

### Variance-Guided Spatial Attention Fusion for Robust End-to-End Driving under Asymmetric Sensor Degradation (VG-SAF)
- id: arXiv:2608.24366 | date: 2026-08 | venue: arXiv preprint
- authors: Tao, Weizhi et al. | code: none seen
- relevance: MED — calibrated per-pixel reliability and a waypoint uncertainty scale that flags severe degradation.
- what: Physically grounded augmentor, heteroscedastic reliability maps, cross-modal trust softmax; improves closed-loop driving score, route completion and infraction score on CARLA Longest6 (no numbers in abstract).
- thesis use: noise-model idea for tool-noise levels; uncertainty signal for a trigger baseline.
- verified: abs meta fetched

### Worst-Case Hidden-Vehicle Trajectory Search in Spatiotemporal Occlusion Regions (HC-MTS)
- id: arXiv:2609.20480 | date: 2026-09 | venue: arXiv preprint
- authors: Tan, Ruichen et al. | code: none seen
- relevance: MED — occlusion hazard generation: worst-case legal hidden-vehicle trajectories against the ego plan.
- what: Bilevel minimax search over certified hidden-state modes; on eight Waymo Open Motion Dataset scenarios, identifies six avoidable counterexamples; visibility-memory horizon K=1 to K=20 cuts retained hidden seeds by 18.45% (total).
- thesis use: idea for adversarial occlusion hazards in MetaDrive.
- verified: abs meta fetched

### VLA-ULAP: Interleaving Cloud VLA Calls with Ultra-Lightweight Local Action Prediction at the Edge
- id: arXiv:2609.18663 | date: 2026-09 | venue: arXiv preprint
- authors: Cao, Deyu et al. | code: none seen
- relevance: LOW-MED — reduces expensive model calls (45.3-77.3%) while retaining 95.0-98.5% of baseline success; manipulation.
- what: Partitions inference across decision times between remote VLA and a ~7.4M-parameter local predictor. Success-vs-call-count trade-off, as a Pareto-style result.
- thesis use: framing precedent for accuracy-vs-call-budget curves.
- verified: abs meta fetched

## Shortlisted but dropped
- 2607.00399 DriveVer: already in raw/C_trajectory_critics.md.
- 2609.22762 DriveReferee: already in raw/C_trajectory_critics.md.
- 2607.04953 Real-World Perturbation Testing of ADS: perturbation robustness study, no decision/query angle.
- 2608.09591 FactorDrive: adaptive reasoning composition, not tool/query selection.
- 2609.14219 FRAME active metrological inspection: manufacturing manipulation, evidence gating only loosely related.
- 2609.14637 DynSTEER: LLM-agent trajectory evaluation, not driving.
- 2609.01260 Dual Process Motion Planning: generic nonlinear planning, no perception.
- 2608.12051 RISC: risk-slice audit budgeting for pedestrian perception, not planner-level.
- 2608.16885 tau0-VLA: manipulation test-time compute.
- 2609.21470 Risk-Aware Occupancy (ROIDrive): representation, not query selection.
- 2607.14727 WorkDrive: roadwork CoT training only.
- 2609.22587 Event-Triggered Async Inference for VLA: manipulation, timing of inference only.
- 2609.26618 NavSafe-inf: closed-loop photorealistic benchmark, off the open-loop MetaDrive setup.
- 2608.16697 (MAE self-evaluation of VLA) and 2607.27933 (flow-matching uncertainty failure detection): manipulation failure detection, abstracts not fetched.

## Leads not followed
- Remaining titles in this slice (pure manipulation VLA, motion planning, world models, detection) skipped by title.
