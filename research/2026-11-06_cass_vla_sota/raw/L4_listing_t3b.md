# L4_listing_t3b: listing sweep, t3_01.tsv (349 titles, Jul-Nov 2026)

## Summary
- No close overlap found. None of the 349 titles describes candidate-conditioned perception-query selection for driving. Nearest in spirit: Expand-and-Prune (uncertainty in candidate scores drives a test-time budget) and PAV (success-vs-query trade-off for choosing how much of a VLA plan to trust), but both act on the planner's own compute, not on perception tools.
- Adaptive "think vs. don't think" driving VLAs keep appearing (CAR-VLA, STEER). Both route by scene complexity/risk or by learned reward, i.e. trajectory-agnostic triggers in the DriveAgent-R1 family. They are baselines/related work for the scene-uncertainty trigger, not competitors.
- Candidate scorers over multiple trajectories are now a crowded NAVSIM line (World4Scorer, RFWorld, ManeuverFlow). Useful for the ranker side (candidate-conditioned scoring, simulator outcome labels for unexecuted plans), not for query selection.
- Hazard benchmarks: ExceptionDrive (counterfactual hazard insertion into nuScenes, reference-free metrics) is the closest fit to the hazard-injection evaluation idea, though it edits real images instead of using MetaDrive.
- "Perceives but Doesn't Brake" shows hazard info is encoded but weakly used by the planner; argues perception evidence is not the bottleneck there, a useful caveat for the thesis.
- Calibrated abstention: RCDH (harvesting, occlusion) is a small-scale analogue of the future accept/reject phase.
- Occlusion for Free gives a label-free occlusion cue (two monocular distance cues disagree) that could be a cheap feature for the selector.
- The occlusion-keyword part of the file is almost all off-domain (medical, faces, gait, manipulation).

## Papers

### Expand-and-Prune: Test-Time Candidate-Space Adaptation for End-to-End Autonomous Driving
- id: arXiv:2610.23262 | date: 2026-10 | venue: arXiv preprint
- authors: Schmidt, Fabian et al. | code: https://github.com/iis-esslingen/Expand-and-Prune
- relevance: MED — candidate-set planners where uncertainty in trajectory scores sets a per-scene candidate budget.
- what: Test-time framework that expands the native candidate set with intent-guided and temporal candidates, then prunes adaptively using uncertainty in intermediate trajectory scores. Improves four candidate-based planners on four benchmarks; LangAuto Driving Score 68.2 to 75.9; 72.5% of selected trajectories come from the new candidates.
- thesis use: related work on candidate-set-level adaptation under a budget; contrast with query (tool) budget. Idea: candidate-score uncertainty as a selector feature.
- verified: abs meta fetched

### Policy-Aligned Predictive Verification for Adaptive VLA Action-Chunk Execution
- id: arXiv:2610.21434 | date: 2026-10 | venue: arXiv preprint
- authors: Kim, Minkyu et al. | code: none listed
- relevance: MED — learned verifier decides how much of a candidate plan to trust, reported as success-query trade-off (manipulation, not driving).
- what: A verifier scores candidate action prefixes for compatibility with successful continuation, trained from terminal outcomes with survival supervision; guides execution-horizon selection. Shows improved success-query trade-offs with pi_0 and pi_0.5 on LIBERO, RoboTwin 2.0 and real manipulation.
- thesis use: idea to borrow (evaluate candidates, plot accuracy vs. query cost); cite alongside TUD.
- verified: abs meta fetched

### CAR-VLA: Complexity-Aware and Risk-Adaptive Reasoning for Autonomous Driving
- id: arXiv:2609.34387 | date: 2026-09 | venue: arXiv preprint
- authors: Chen, Xiaolei et al. | code: promised on GitHub (link truncated in fetch)
- relevance: MED — driving VLA that chooses a reasoning mode from scene complexity and dynamic risk (whether/how to think).
- what: Maps four complexity-risk categories to three modes (Fast Intuition, Slow Thinking, Reflex Response) via supervised training then RL. NAVSIM v1 91.1 PDMS, NAVSIM v2 90.3 EPDMS, Navhard 35.0 EPDMS.
- thesis use: baseline family for trajectory-agnostic triggering (scene-uncertainty/risk), alongside DriveAgent-R1.
- verified: abs meta fetched

### STEER: Route-Aware Adaptive Reasoning for Autonomous Driving
- id: arXiv:2611.00718 | date: 2026-10 | venue: arXiv preprint
- authors: Zou, Yangang et al. | code: none listed
- relevance: MED — learns CoT vs. direct routing from environment reward without scene-difficulty labels.
- what: Routing-uncertainty-aware rollout plus cross-route advantage credit assignment, to reduce over-reasoning in driving VLAs (NAVSIM; numbers not seen in fetched text).
- thesis use: related work; reward-based (not label-based) trigger learning is an alternative to the "expected gain" targets.
- verified: abs meta fetched

### World4Scorer: Outcome-Grounded World Modeling for Autonomous Driving
- id: arXiv:2609.36438 | date: 2026-09 | venue: arXiv preprint
- authors: Pei, Jieyuan et al. | code: none listed
- relevance: MED — generate-and-select scorer that predicts a per-candidate state and uses simulator outcome labels for unexecuted candidates.
- what: Trajectory-conditioned JEPA-style predictor, supervised by simulator outcomes of every candidate and anchored on the executed future; scene-matched bank of low-scoring plans and inertial re-ranking. Reports state-of-the-art NAVSIM-v2 and a strong adapted result on closed-loop Bench2Drive.
- thesis use: parallels our oracle labels from privileged simulator state; candidate-conditioned ranker reference.
- verified: abs meta fetched

### Trajectory Evaluation via Rollout-Free World Model for End-to-end Autonomous Driving
- id: arXiv:2611.05072 | date: 2026-11 | venue: arXiv preprint
- authors: Wang, Junzhe et al. | code: none listed
- relevance: MED — candidate trajectories query a shared scene memory for scoring (RFWorld).
- what: Avoids per-candidate rollouts; claims compute reduced by about horizon times candidate count; state-of-the-art on NAVSIM and Bench2Drive.
- thesis use: candidate scoring baseline / ranker design.
- verified: abs meta fetched

### ExceptionDrive: A Planning-Oriented Counterfactual Corner-Case Benchmark for Autonomous Driving
- id: arXiv:2609.37871 | date: 2026-09 | venue: arXiv preprint
- authors: Luo, Ziyi et al. | code: none listed
- relevance: MED — hazard-insertion benchmark with reference-free planning metrics; plus a VLM Reminder Agent for hazard records.
- what: Inserts hazards into real nuScenes scenes (21 tasks, six safety families); metrics UR, HCC, HPR, CTS; seven planners often intrude into hazard regions. Reminder Agent improves strategy accuracy and reduces under-warning zero-shot.
- thesis use: benchmark reference for hazard-oriented evaluation; reference-free metric design.
- verified: abs meta fetched

### Perceives but Doesn't Brake: A Perception-Action Binding Gap in Reasoning Driving VLAs
- id: arXiv:2610.28184 | date: 2026-10 | venue: arXiv preprint
- authors: Cercola, Matteo et al. | code: none listed
- relevance: MED — shows hazards are encoded but weakly control the plan; hazard-conditioned guidance in a frozen sampler (Alpamayo-1.5).
- what: With exact obstacle geometry, guidance cuts footprint intrusion from 58.1% to 14.5% and eliminates collisions in the closed-loop braking battery.
- thesis use: caveat / motivation: exact geometry (like a collision-check tool) helps when the planner can use it.
- verified: abs meta fetched

### Do Not Cut When Uncertain: Rejectable and Calibrated Decision Heads for VLA Policies in Robotic Harvesting
- id: arXiv:2609.35039 | date: 2026-09 | venue: arXiv preprint
- authors: Zhang, Heng | code: none listed
- relevance: MED — rejectable, calibrated output head for risk-aware abstention under occlusion (manipulation).
- what: RCDH attaches to a frozen VLA and adds explicit rejection plus calibration; evaluated on a harvesting platform with controllable leaf occlusion; restores OOD usability without hurting in-distribution (no numbers in abstract).
- thesis use: idea for the future accept/inspect/replan/fallback phase.
- verified: abs meta fetched

### Jev with Foresight: Safe Language-Guided Autonomous Driving via a Language World Model
- id: arXiv:2611.05448 | date: 2026-11 | venue: arXiv preprint
- authors: Qu, Yansong et al. | code: project page ys-qu.github.io/jev-ad-website
- relevance: MED — predicts consequences for every candidate action, then a typed decision model compares them.
- what: Collision rate 26.0% to 2.4% in simulated highway merging (500 episodes) and 48.2% to 2.8% on 500 replayed NGSIM episodes.
- thesis use: candidate-conditioned evaluation idea; foreseen consequences as selector features.
- verified: abs meta fetched

### Occlusion for Free: Detecting Occlusion from the Disagreement Between Two Monocular Distance Cues
- id: arXiv:2611.06899 | date: 2026-11 | venue: arXiv preprint
- authors: Onyenweaku, Chibueze Praise et al. | code: none listed
- relevance: MED — label-free occlusion score a selector could use to decide whether an ROI inspection is worthwhile.
- what: Compares apparent-height distance with monocular-depth distance; AUC 0.909 on KITTI for heavy occlusion, 0.819 on synthetic CARLA scenes vs. 0.644 for distance alone.
- thesis use: cheap feature for the selector; comparison point for "occlusion" hazard detection.
- verified: abs meta fetched

### When and How Should an Agent Clarify? CIGAsk
- id: arXiv:2609.24290 | date: 2026-09 | venue: arXiv preprint
- authors: Li, Yunxiang et al. | code: none listed
- relevance: LOW-MED — learns when to ask vs. answer using counterfactual information gain (QA, not driving).
- what: GRPO recipe with Counterfactual Information Gain reward and an asymmetric ambiguity bonus; CIGAsk-7B beats the strongest external baseline on three clarification benchmarks.
- thesis use: idea to borrow (reward = information gain with vs. without the response, similar to expected-gain targets).
- verified: abs meta fetched

### FocusDrive: Reasoning with Visual Focus for Autonomous Driving
- id: arXiv:2609.33190 | date: 2026-09 | venue: arXiv preprint
- authors: Liu, Zhiyuan et al. | code: none listed
- relevance: LOW-MED — grounds planning reasoning in image-patch references to decision-relevant objects.
- what: Pairs object descriptions with patch references; competitive gaze prediction (W3DA) and NAVSIM planning, improves over text CoT.
- thesis use: related work to ROI-based inspection tools.
- verified: abs meta fetched

### Towards Safer Autonomous Driving in an Open World: A Dual-Process Approach
- id: arXiv:2610.04088 | date: 2026-10 | venue: arXiv preprint
- authors: Janssen, Simon et al. | code: none listed
- relevance: LOW-MED — meta-cognitive switch between a NN planner and MPC using risk fields.
- what: CARLA red-light-running emergency vehicle scenarios; collisions reduced by 89% vs. NN-only.
- thesis use: related work on deciding when to hand off to a deliberate planner.
- verified: abs meta fetched

### RCVLA: 4D Radar-Grounded Semantic Reasoning and Trajectory Arbitration for Autonomous Driving
- id: arXiv:2609.32681 | date: 2026-09 | venue: arXiv preprint
- authors: Zheng, Lianqing et al. | code: none listed
- relevance: LOW-MED — rescoring of trajectory candidates with radar time-to-collision risk.
- what: Candidates refined by truncated diffusion; scores calibrated with TTC risk. Average L2 0.348 to 0.259 m and open-loop collision rate 0.576% to 0.175% from RCVLA-Sem to RCVLA-Phys.
- thesis use: scorer reference using a geometric risk term similar to the collision-check tool.
- verified: abs meta fetched

### ManeuverFlow: Maneuver Hypothesis Generation with Future Evidence for Trajectory Evaluation and Refinement
- id: arXiv:2610.13409 | date: 2026-10 | venue: arXiv preprint
- authors: Wei, Yuhao et al. | code: github.com/wyh-autonomy (truncated)
- relevance: LOW-MED — small candidate set per intention, evaluated with trajectory-specific future evidence.
- what: 90.6 PDMS / 90.1 EPDMS on NAVSIM v1/v2; WorldEngine 3DGS closed-loop PDMS* 75.19 (logged) and 74.58 (IDM).
- thesis use: candidate generator reference.
- verified: abs meta fetched

### Safety-Oriented Trajectory Ranking from BEV Perception Outputs
- id: arXiv:2610.14066 | date: 2026-10 | venue: arXiv preprint
- authors: Pohl, Leon et al. | code: none listed
- relevance: LOW-MED — rule-based ranking of candidate trajectories on BEV detections.
- what: Rule ranking matches 124 of 146 pairwise human votes (84.9%) across seven BEV scenarios.
- thesis use: simple geometric ranker baseline, similar to a collision-check-based ranker.
- verified: abs meta fetched

## Shortlisted but dropped
- 2610.04933 DiVeR: already in raw/C_trajectory_critics.md.
- 2610.05025 TUD (Triggering Generalist Reasoning): already in raw/A_driving_tool_agents.md.
- 2610.08123 Query-Based Cost Learning: planner cost learning, no query/tool selection.
- 2610.07521 GroundAct: grounding of reasoning into plan, no selection under budget.
- 2610.24590 Scene-Adaptive VLA: layer routing for compute, not perception queries.
- 2610.36079 CLAP-AD: speed scoring head, not about perception queries.
- 2610.40002 CoC-CFG: guidance weight over reasoning, manipulation of VLA internals.
- 2607.03155 Occlusion-Aware Contingency Planning: formal reachability planner, no learned selection.
- 2609.06342 OcclusionCBF: safety filter, no query selection.
- 2610.19082 RH-NBV: tabletop manipulation active view planning.
- 2611.01600 SCOUT: manipulation under occlusion.
- 2609.40297 Path-dependent marginal information gain: exploration/mapping.
- Remaining occlusion/information-gain titles (faces, gait, medical, Gaussian splatting, tracking): off-domain by title, not fetched.

## Leads not followed
- Titles not fetched: 2610.41185 Mechanistic Interpretability for End-to-End Self-Driving; 2609.34440 and 2610.21741 (metric/protocol pitfalls in NAVSIM/Bench2Drive, possibly relevant to evaluation caveats); 2609.20103 Safety-Critical Scenarios Emerge from Initial Scenes; 2610.35448 Model-Aware Generation of Safety-Critical Scenes.
- First 42 lines of the TSV beyond the first 21 (ids 2609.34085 to 2609.37772) were only skimmed; no further candidates stood out.

---
# Addendum (coordinator follow-up): full-text reads and leads

## Full-text reads (arxiv.org/html, tags stripped; numbers verbatim from the text)

### Perceives but Doesn't Brake (arXiv:2610.28184), full text read
- setup: Alpamayo-1.5 (frozen, zero-shot, flow-matching trajectory expert, 6.4 s horizon). Critical state = approaching ego with a stationary in-path obstacle. Instruments: (a) logged PhysicalAI-AV clips (ego speed >= 4 m/s, stationary object 8-45 m ahead; 185 clips; nominal set, plans enter footprint on only 2.50% of samples); (b) CARLA via Fail2Drive, matched-despawn pairs (hazard vs. identical empty scene), six object kinds at 8-30 m, seen sites and new sites held out in geometry and appearance; (c) AlpaSim/NuRec closed loop, static stimulus (24 paired reconstructions) and dynamic stimulus (38 scenes, 24 "must-brake"). Also cross-model checks on Senna and VaVAM (Sec. VI).
- headline numbers (verbatim):
  - Sec. IV-A: "contact rate, defined as footprint intrusion, is 58.1% (56.1, 60.5) at seen sites and 65.0% (58.6, 71.1) at new sites"; closed loop, "front-collision rate rises from about one in four rollouts to about four in five, a paired increase of 54.2 points (+33.3, +75.0)"; must-brake scenes: "it still contacts the stopped vehicle in 13 of the 24".
  - Sec. IV-B: hazard presence decodable from the frozen visual cache at "AUC of 0.998, yet every evaluated scene at 8-12 m intrudes" (Fig. 2).
  - Sec. IV-C: removing ego history gives a longitudinal shift "roughly an order of magnitude larger than blanking vision"; on long-tail clips ego history dominates "by roughly the same order of magnitude, about 12x". Swapping the reasoning trace has the smallest longitudinal effect.
  - Sec. IV-D: rotating a stopped vehicle changes the fraction of traces demanding a stop "from 10.4% to 99.0%", yet planned reach barely moves.
  - Sec. V-B (oracle geometry): intrusion "from 58.1% to 14.5% on seen sites and from 65.0% to 6.0% on new ones"; near-stop rate "from 20.1% to 76.4% on seen sites and 5.5% to 89.0% on new ones"; closed-loop collisions "from 13 of 24 to zero"; guidance adds "3.8 ms, 0.2% of the 2.30 s base replan".
  - Sec. V-B, reranking vs. steering: "21.5% of real scenes have all six unguided samples intruding, so no reranking selector could have rescued them"; guidance takes sample-level intrusion "from 98.5% to 4.8%".
  - Sec. V-C: fully model-derived arm cuts intrusion "from 65.0% to 28.6% on unseen sites"; attention readout over the frozen tokens gives 11.7% intrusion with range MAE 2.21 m (pooled: 28.6%, 3.28 m) (Table II). Presence readout does not transfer from CARLA to NuRec frames.
  - Table III: gating recall vision detector 71%, reasoning trace 55%, union 87%; "the trace adds only 0.9 recall points for 16.7 points of false flags" against the stronger presence readout.
  - Sec. VI: Senna decelerate+stop rate is "12% in both conditions" (hazard vs. clear).
  - Sec. VII/VIII: the critical state is rare in logs; every hazard measured is synthetic.
- implication for us (selector over ROI/depth/collision tools, ranker over K candidates):
  1. The strongest relevance is to the collision-check tool. When the oracle supplied exact obstacle geometry, a frozen generator went from 58.1% to 14.5% intrusion. In our setting the analogue is: a tool that returns exact actor geometry only helps if the ranker actually lets it change the choice. Our ranker must be constructed so that tool output has authority over candidate scores; otherwise "always-on" will show no gain and the Pareto curve will be flat for a ranker reason, not a selector reason.
  2. Their "reranking cannot rescue" result (21.5% of scenes have all six samples intruding) corresponds to our oracle: a scene where all K candidates are bad has no benefit from any query. Our expected-gain labels should be reported separately for scenes where the candidates differ in outcome; the selector can only win where candidates diverge (supports the candidate-conditioned thesis).
  3. Decodable is not used: AUC 0.998 for hazard presence with no behavioural change. This is a caution for our frozen-VLM-embedding feature result (+0.3 to +0.7): features may carry hazard info that a small head cannot exploit, and a spatially aware readout mattered (28.6% to 11.7%) over pooled statistics. Suggests trying a patch/attention readout over the cached embeddings instead of pooled vectors.
  4. Gating: the vision-based gate and the reasoning-based gate fire on different evidence (union recall 87%) but the extra evidence costs false flags; analogous to a scene-uncertainty trigger plus a candidate-divergence trigger, and a way to describe the false-trigger cost on our budget axis.
  5. Their model-derived gate failed to separate stopped from moving vehicles under rendering shift, which is a warning for our distance-ambiguity hazard: a tool-trigger that sees "a vehicle" cannot tell whether braking is needed; the candidate set (do some candidates brake and some not?) is the discriminating signal we use.
  6. Limits: single model (Alpamayo-1.5), longitudinal stopping only, synthetic hazards, no tool-choice or budget axis. It is not a competitor.

### Expand-and-Prune (arXiv:2610.23262), full text read (main text; appendix not read)
- setup: test-time wrapper, planner frozen. (1) Intent-guided candidate expansion: from LAD-Drive's belief over six meta-actions, candidates are sampled from per-action k-means prototype banks in proportion to belief mass. (2) Entropy-adaptive temporal memory: previous-frame top candidates are carried over, the count interpolated between a minimum and maximum by the normalized entropy of the previous scores. (3) Confidence-aware pruning: at the earliest stage with meaningful scores, the number of retained candidates is interpolated between a minimum and maximum by normalized entropy of the temperature-scaled score distribution (Eq. 5). Planners: LAD-Drive on LangAuto, BridgeDrive on Bench2Drive and Fail2Drive, DriveSuprim and SparseDriveV2 on NAVSIMv2 (pruning only on the last two).
- headline numbers (verbatim from tables/text):
  - Table 2 (LangAuto mean): LAD-Drive DS 68.2, RC 74.5, IS 0.90; "+ Expand-and-Prune" DS 75.9, RC 81.1, IS 0.93. Short routes DS 71.3 to 83.4; Long routes DS 49.8 to 58.9; Tiny 83.5 to 85.4. LMGenDrive for reference: DS 74.5.
  - Table 3(a) intent expansion (20 native candidates): +30 intent candidates gives DS 72.1 (from 68.2); "Further increasing the budget yields no additional gains"; replacing native anchors with 30 or 50 intent candidates only gives DS 62.8 and 64.4.
  - Table 3(c) pruning: no pruning DS 73.4; fixed Top-5 73.9; Top-10 73.1; best entropy setting 75.9, RC 81.1, IS 0.93. Text: "pruning not only reduces the number of hypotheses forwarded to subsequent refinement, but can also improve planning quality."
  - Table 4(a) BridgeDrive: Bench2Drive DS 95.9 to 96.5, SR 88.2 to 88.7; Fail2Drive generalization DS 80.2 to 83.1, SR 73.0 to 78.0, HM 76.4 to 80.5 (temporal + pruning).
  - Table 4(b) NAVSIMv2 EPDMS, pruning only: DriveSuprim R34 83.07 to 83.67; ViT-L 87.03 to 87.27; SparseDriveV2 87.04 to 87.37.
  - Abstract (also Sec. 1): "72.5% of selected trajectories originate from the newly introduced intent-guided or temporal candidates".
- implication for us:
  1. It is the closest published instance of a budget that depends on score uncertainty over candidates: entropy of the candidate score distribution decides how many candidates to keep. That is the natural trajectory-conditioned (but not tool-aware) trigger and a stronger baseline than raw scene uncertainty: add "entropy / margin of the ranker's no-tool candidate scores" as a baseline selector and as an MLP feature. If our learned selector does not beat it, the thesis claim narrows.
  2. Its gains are largest where candidates are ambiguous or out of distribution (Fail2Drive generalization, long routes), consistent with our expectation that query value concentrates in a minority of decision steps.
  3. Fixed Top-k pruning did worse than entropy-adaptive pruning (Table 3(c)): supports reporting adaptive vs. fixed budgets on our Pareto plot.
  4. Limits: the unit being budgeted is planner compute (candidates kept), not perception queries; no tool, no occlusion hazard; gains are reported on driving score, not decision accuracy against an oracle. No overlap with tool selection.

### Policy-Aligned Predictive Verification, PAV (arXiv:2610.21434), full text read (main text; appendices not read)
- setup: manipulation. A predictor maps the VLA's task-conditioned representation plus a proposed action prefix to the future representation; a verifier outputs local validity per extension, trained only from terminal success/failure with a localization prior (to avoid lowering all scores in a failed rollout). Accumulated, length-normalized validity chooses the execution horizon: prefixes are checked in ascending order and extension stops at the first score below a threshold. pi_0 and pi_0.5 on LIBERO (4 suites), RoboTwin 2.0 (50 tasks), and a Franka with three real tasks. Cost axis = VLA queries per episode.
- headline numbers (verbatim):
  - Sec. 4.2.1: "improves success by 7.50 percentage points over [the best fixed horizon, name lost in HTML] while reducing queries by 63.3%"; "raises success from 97.50% to 98.10% with similar query counts".
  - Sec. 4.2.2 / Table 2: RoboTwin 2.0 selected 16 tasks 54.13% vs. best fixed 47.88% and DVAC 41.6%; all 50 tasks 58.64% vs. 55.76% with 58.5 vs. 54.5 queries.
  - Table 3 ablation (LIBERO, 10 candidate horizons): Direct (no future prediction) 84.55% success, 22.3 queries; DINOv2-space prediction 87.00%, 22.2; PAV 94.65%, 14.0.
  - Table 4: predicted-vs-observed future latent cosine 0.9401 with executed actions vs. 0.5304 for same-task swapped actions.
  - Table 5: verifier compute 0.90-2.49 ms, "0.45-1.24% of action-generation time".
  - Table 6 (real robot, 3 tasks): avg. success 74.4% vs. 41.1% for the strongest fixed horizon; replans 12.87 vs. 36.54 per episode.
- implication for us:
  1. A learned, outcome-supervised validity score used for a "how much to spend" decision, reported on a success-vs-queries plane, is the same evaluation geometry as our Pareto curve; its baselines (generation stability, prediction agreement) are the manipulation counterparts of our scene-uncertainty trigger. The claim that signals which do not look at the consequences of the proposed action miss failures (Fig. 1 example) is the manipulation form of our hypothesis.
  2. Ablation Table 3: using the policy's own representation space beat generic DINOv2 features (94.65% vs. 87.00%), a small supporting point for using VLM-aligned features instead of generic ones as selector inputs.
  3. Training from terminal outcomes only (no step labels) is an alternative to our expected-gain targets when the oracle is unavailable.
  4. Limits: the decision is a continuous horizon for one policy, not a choice among heterogeneous tools; no driving; candidates are prefixes of a single chunk, not K alternatives.

## Additional papers from the previously unfetched leads (abstract meta fetched)

### Model-Aware Generation of Safety-Critical Scenes for Robust End-to-End Driving via Distilled Planner Surrogates
- id: arXiv:2610.35448 | date: 2026-10 | venue: arXiv preprint
- authors: Seyam, Khaled M. et al. | code: none listed
- relevance: MED — evidence that the planner, not perception, is the collision bottleneck, plus planner-specific hazard scene generation.
- what: On NeuroNCAP "95.9% of DiffusionDrive's collisions are planning failures despite reliable detection". Generates 50 attack scenes per planner via a distilled BEV surrogate; fine-tuning on them lowers closed-loop collision rate for SparseDrive 28.0% to 12.2% and DiffusionDrive 37.5% to 19.2%.
- thesis use: motivation caveat (perception tools only help if planning can use them; same message as 2610.28184) and a hazard-scene generator idea for the benchmark. Not about tool selection.
- verified: abs meta fetched (full text not read)

### Mechanistic Interpretability for End-to-End Self-Driving
- id: arXiv:2610.41185 | date: 2026-10 | venue: arXiv preprint
- authors: Gagvani, Manav et al. | code: project page mgagvani.github.io/mechanistic-interpretability-for-e2e-driving
- relevance: LOW-MED — sparse-autoencoder latents of a driving planner respond to traffic-light state and stop signs; a lightweight adapter on SAE latents "reduces trajectory selection error by 3.44%".
- what: SAEs on a single-camera E2E path planner; unsupervised clustering recovers route intent with 98.3% accuracy; steering latents changes lateral displacement, curvature and braking monotonically.
- thesis use: related to frozen-feature heads for candidate selection (small gain, same order as our +0.3 to +0.7 VLM-embedding gain); possible feature source for light-state ambiguity.
- verified: abs meta fetched

### Safety-Critical Scenarios Emerge from Initial Scenes (AdvScene)
- id: arXiv:2609.20103 | date: 2026-09 | venue: arXiv preprint
- authors: Wu, Yin et al. | code: none listed
- relevance: LOW — scenario generation by learning adversarial initial scenes with RL from closed-loop rollouts (Waymo; ego-fault collisions and TTC<3s events increase).
- thesis use: hazard-scenario generation idea only.
- verified: abs meta fetched

### Evaluation-protocol papers (context for evaluation caveats, LOW)
- 2609.34440 "When the Score Becomes the Target: Rethinking Metric Validity in Autonomous Driving" (Zhu, Morui et al., 2026-09): benchmark score changes can fail to reflect behavioural changes; optimized gains can reverse when the execution interface changes. Caveat for using any aggregate driving score as the decision-accuracy proxy; supports our choice of oracle-relative decision accuracy. verified: abs meta fetched.
- 2610.21741 "Comfortably Stuck: Evaluation Pitfalls in Bench2Drive's Closed-Loop Protocol" (Aghajanzadeh, Emad et al., 2026-10): Bench2Drive comfort metric correlates with stationary time at r = 0.97 across eight models; corrected metric cuts that to r = 0.06; also navigation-signal pitfalls. Relevant only if we cite Bench2Drive numbers. verified: abs meta fetched.

## Updated Summary (supersedes the one at the top)
- No paper in this slice does candidate-conditioned perception-tool selection for driving. Closest in spirit: Expand-and-Prune (2610.23262), which sets how many candidates to keep from the entropy of candidate scores; and PAV (2610.21434), a learned outcome-trained validity score that decides how far to trust a VLA's proposal and is evaluated on a success-vs-queries plane (manipulation).
- Concrete baseline to add: the entropy/margin of the no-tool ranker's candidate score distribution as a selector (from Expand-and-Prune). It is candidate-conditioned but not tool-aware; beating it is the cleaner test of the thesis than beating raw scene uncertainty alone.
- Two independent papers (2610.28184, 2610.35448) report that driving planners fail on hazards despite having the evidence: 58.1% footprint intrusion with 0.998-AUC hazard decodability; 95.9% of DiffusionDrive collisions are planning failures despite reliable detection. For our project this means tool output must have authority over the ranker, or the Pareto curve will be flat for ranker reasons.
- 2610.28184 also shows that when all samples are bad (21.5% of scenes) no reranker can help; our oracle-gain analysis should separate scenes where candidates actually diverge in outcome.
- Frozen-feature readouts: a spatially aware attention readout beat pooled statistics (28.6% to 11.7% intrusion), and PAV found policy-space features beat generic DINOv2 (94.65% vs. 87.00%); both suggest improving how the cached VLM embeddings are read before concluding the VLM adds little.
- Adaptive reasoning for driving VLAs (CAR-VLA, STEER) keeps growing; these are trajectory-agnostic triggers and belong in related work for the scene-uncertainty baseline.
- Scorer line (World4Scorer, RFWorld, ManeuverFlow) is crowded on NAVSIM; useful for the ranker design, with World4Scorer's simulator-outcome labels for unexecuted candidates paralleling our privileged-state oracle.
- Benchmarks: ExceptionDrive (hazard insertion into nuScenes, reference-free metrics) is the nearest hazard benchmark; two evaluation-pitfall papers (2609.34440, 2610.21741) are caveats if we quote aggregate driving scores.
- Calibration phase: RCDH (2609.35039) is a small-scale reference for rejectable, calibrated heads on a frozen policy under occlusion.

## Leads not followed (addendum)
- Appendices of 2610.23262 and 2610.21434 were not read; PAV's Table 1 (LIBERO main results) lost its row labels in the HTML strip, so only the text-quoted numbers are given.
- The 2609.34085-2609.37772 block of the TSV was only skimmed by title.
