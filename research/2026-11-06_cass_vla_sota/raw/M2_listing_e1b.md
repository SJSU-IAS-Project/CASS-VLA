# M2_listing_e1b: triage of listing_sweep/e1_01.tsv (315 titles, 2603.05xxx to 2606.31xxx)

## Summary
- No close overlap with the project. Nothing in this slice does candidate-conditioned perception-query selection for driving. The slice is about 85% VLA titles (mostly manipulation, efficiency, attacks), so the driving/tool-use keywords matched mostly on "Vision-Language-Action".
- Closest in idea: AS-DDTO (2606.22277). It adds a trajectory-dependent information-acquisition term to a planner whose trajectories stay coincident then diverge toward candidate targets, with conformal candidate-set updates and a sensing budget. This is the same "how candidates diverge decides which observation is worth taking" intuition, but it is a target-identification trajectory optimizer, not a driving/tool selector. Idea to borrow, not a competitor.
- On-demand sensing as a tool call: MuseVLA (2606.17598) emits a sensor token plus a target description, like a tool call with arguments (manipulation, no budget analysis). ScoutVLA (2606.14772) does evidence-seeking viewpoint refinement (UAV).
- Candidate scoring/verification (manipulation, but same structure as the ranker): TokenPB (2603.18091), VeriSpace (2606.10568), Pre-VLA (2605.22446). TokenPB gives selection-regret bounds that separate candidate-set effects from calibration, which is directly quotable for the candidate-set framing.
- Calibrated confidence and deferral for the future phase: VLAConf (2605.29605, confidence-triggered handoff), TD calibration (2604.20472), VLA-FAIL (2606.21386), Navigation Heads (2603.13782), Assistron (2606.23147), mission-level runtime assurance for driving (2606.06996), GuardAD (2605.10386). All lack a conformal guarantee on a plan accept/reject decision.
- Driving robustness/diagnostics that bear on hazard design: the visual-perturbation study of driving VLAs (2605.31041), the faithfulness probe of Alpamayo-R1 (2605.17268, missed pedestrians), the view-selection benchmark (2606.09644), VENUSS input-configuration sensitivity (2604.06750).
- Occlusion benchmark: LIBERO-Occ (2606.10862) is manipulation only, so it is a design reference, not an eval fit.
- Titles that carried "tool" or "active perception" (2605.13119, 2605.13632, 2606.14772) turned out to be about VLA-as-tool execution or user guidance, not perception-tool choice.

## Papers

### Active Sensing and Deferred-Decision Trajectory Optimization for Robust Target Identification
- id: arXiv:2606.22277 | date: 2026-06 | venue: arXiv preprint
- authors: Siahkali, Farbod et al. | code: none seen
- relevance: HIGH (idea only) — trajectory-dependent information acquisition over a candidate set, with a sensing budget and conformal candidate sets; closest conceptual neighbour, but not driving and not a tool selector.
- what: Extends Deferred-Decision Trajectory Optimization, where trajectories to individual candidate targets stay coincident as long as possible, with a trajectory-dependent information-acquisition term that biases the shared segment toward regions enabling earlier target identification. Supports Bayesian and conformal candidate-set updates under distance-dependent sensing, with guarantees on recursive feasibility, belief concentration and fixed-time coverage of the raw conformal set. Simulations show better target identification than standard DDTO under limited sensing budget (no numbers in the abstract).
- thesis use: idea to borrow (value of a query depends on where candidate trajectories diverge); cite as related work for the candidate-conditioned premise and for conformal sets in the calibration phase.
- verified: abs meta fetched

### TokenPB: Enabling VLA Action Self-Verification via VLM Token Probability Bucketing
- id: arXiv:2603.18091 | date: 2026-03 | venue: arXiv preprint
- authors: Zhao, Chen et al. | code: https://github.com/RUCKBReasoning/TokenPB
- relevance: MED — scores M sampled candidate actions and picks the best; theory on selection regret that separates candidate-set effects from calibration.
- what: Co-trains a VLA with flow-matching loss and an auxiliary bucket-token loss; at inference samples M candidates, scores each by teacher-forced evaluation, selects the best, with KV-cache reuse. Reports success-rate gains over single-sample inference of +2.7 (simulation), +17.1 (real-world), +16.4 (out-of-distribution), and gains over external-verifier baselines under the same sampling budget.
- thesis use: related work for the ranker; the regret decomposition (candidate set vs calibration) supports the argument that candidate-set structure matters.
- verified: abs meta fetched

### VeriSpace: Spatially Grounded Action Verification for Vision-Language-Action Models
- id: arXiv:2606.10568 | date: 2026-06 | venue: arXiv preprint
- authors: Zhao, Guiyu et al. | code: none seen
- relevance: MED — test-time verifier that discriminates between subtle candidate actions using 3D-injected scene encoding.
- what: A 3D-aware verifier with Dual-Path 3D-Injected Scene Encoding and Spatially-Grounded Action Reasoning that evaluates each candidate for spatial relations, geometric validity and goal progress. Reported to improve decision reliability over the base VLA policies and prior verification methods (no numbers in the abstract).
- thesis use: related work (candidate verifier); a possible ranker comparison if geometry features are added.
- verified: abs meta fetched

### Pre-VLA: Preemptive Runtime Verification for Reliable Vision-Language-Action and World-Model Rollouts
- id: arXiv:2605.22446 | date: 2026-05 | venue: arXiv preprint
- authors: Sun, Zhen et al. | code: none seen
- relevance: MED — predicts safety confidence and advantage for candidate action chunks before execution, with a resampling scheduler under a computation budget.
- what: A multimodal backbone with a dual-branch head predicts safety confidence and critic-derived advantage per candidate chunk; trained with Focal classification, advantage regression and soft-threshold calibration; a dual-mode scheduler filters low-quality actions and triggers adaptive resampling under a limited compute budget. On LIBERO, average closed-loop success rises from 30.79% to 37.62% over RynnVLA-002, with 183.9 ms average forward verification time per chunk.
- thesis use: related work for accept/reject of candidates and budgeted re-querying; a model for the accept/replan policy in the future phase.
- verified: abs meta fetched

### MuseVLA: An Adaptive Multimodal Sensing Vision-Language-Action Model for Robotic Manipulation
- id: arXiv:2606.17598 | date: 2026-06 | venue: arXiv preprint
- authors: Liu, Xingyuming et al. | code: https://github.com/microsoft/MuseVLA
- relevance: MED — selects which sensor to invoke and what to attend to, framed as a tool call with arguments.
- what: Generates a sensor token and target description from instruction and visual context, then converts the chosen sensor reading into a grounded sensor image for fusion and action generation. Real-robot dexterous tasks (temperature-guided pick-and-place, audio-driven search, radar-assisted retrieval) reach 80.6% average success, above RGB-only and multisensory VLA baselines.
- thesis use: related work for "which sensor/tool to call"; contrast: selection is conditioned on instruction and image, not on candidate actions, and has no budget or noise analysis.
- verified: abs meta fetched

### ScoutVLA: UAV-Centric Active Perception via a Dual-Expert VLA Model for Open-World Embodied Question Answering
- id: arXiv:2606.14772 | date: 2026-06 | venue: arXiv preprint
- authors: Lu, Wenhao et al. | code: none seen
- relevance: MED — an evidence-driven active perception policy that first infers which evidence is missing, then moves to get it.
- what: Introduces FG-EQA (over 40K simulated and 1K real-world trajectories) and a dual-expert VLA: a vision-language expert infers missing evidence, a flow-matching action expert generates viewpoint-refinement trajectories. Reports 10.48x higher average strict success rate and 7.72x higher average QA correctness than baselines.
- thesis use: related work on active perception; not a tool selector and no query budget.
- verified: abs meta fetched

### VLAConf: Calibrated Task-Success Confidence for Vision-Language-Action Models
- id: arXiv:2605.29605 | date: 2026-05 | venue: arXiv preprint
- authors: Huang, Dehao et al. | code: project page only
- relevance: MED — calibrated confidence from frozen VLA representations, used to trigger expert handoff.
- what: A step-conditioned Coin-Flip Network gives an uncalibrated score, and a low-capacity calibrator fitted on outcome-labelled rollouts maps it to task-success probability. Improves online confidence estimation on LIBERO, and confidence-triggered handoffs improve success over no intervention.
- thesis use: calibration-phase reference (frozen features plus a small calibrator; confidence-triggered deferral). No conformal guarantee.
- verified: abs meta fetched

### Temporal Difference Calibration in Sequential Tasks: Application to Vision-Language-Action Models
- id: arXiv:2604.20472 | date: 2026-04 | venue: arXiv preprint
- authors: Francis-Meretzki, Shelly et al. | code: none seen
- relevance: MED — sequential calibration of task-success confidence along an episode.
- what: Defines a sequential Brier score whose risk minimizer equals the policy value function, so TD value estimation acts as a calibration mechanism. Improves on the prior state of the art on simulated and real-robot data; calibrated single-step action probabilities give competitive uncertainty estimates.
- thesis use: calibration-phase reference.
- verified: abs meta fetched

### VLA-FAIL: Efficient Task Failure Detection for Finetuned Vision-Language-Action Models
- id: arXiv:2606.21386 | date: 2026-06 | venue: arXiv preprint
- authors: Seligmann, Florian et al. | code: project page only
- relevance: MED — cheap runtime failure detection that needs no failure data; detection accuracy versus latency metric.
- what: Combines last-layer Mahalanobis distance (out-of-distribution states) with action chunk consistency across receding-horizon chunks, and introduces AUCPDT, which jointly scores precision, recall and detection time. The combination frequently beats more expensive baselines in real-world and simulation tests.
- thesis use: trigger signals for the fallback branch in the future phase; AUCPDT as a metric idea.
- verified: abs meta fetched

### Your Vision-Language-Action Model Already Has Attention Heads For Path Deviation Detection
- id: arXiv:2603.13782 | date: 2026-03 | venue: arXiv preprint
- authors: Jeong, Jaehwan et al. | code: promised, no URL
- relevance: MED — training-free monitor on a frozen VLA that triggers a cheap fallback policy.
- what: Three attention heads out of over a thousand give a 44.6% deviation detection rate at 11.7% false positives; on detection the heavy VLA is bypassed for a lightweight RL shortest-path rollback on a physical robot (navigation).
- thesis use: example of detect-then-fallback with a frozen model; modest detection numbers.
- verified: abs meta fetched

### Mission-Level Runtime Assurance Framework for Autonomous Driving
- id: arXiv:2606.06996 | date: 2026-06 | venue: arXiv preprint
- authors: Tsai, Chieh et al. | code: none seen
- relevance: MED — driving runtime monitor that rejects unsafe or mission-infeasible commands before execution.
- what: Extends highway-env with mission-level fault scenarios and a runtime monitor, compared with an adapted Simplex-Drive baseline. Platform-level runtime safety alone misses mission-level faults, while the proposed monitor rejects mission-infeasible commands and improves mission success.
- thesis use: related work for accept/reject-and-fallback in driving; no calibration guarantee.
- verified: abs meta fetched

### GuardAD: Safeguarding Autonomous Driving MLLMs via Markovian Safety Logic
- id: arXiv:2605.10386 | date: 2026-05 | venue: arXiv preprint
- authors: Zhang, Tianyuan et al. | code: none seen
- relevance: MED — model-agnostic safeguard that infers latent hazards and revises actions of a driving MLLM.
- what: Neuro-symbolic Markovian logic states infer emerging and latent hazards; Logic-Driven Action Revision refines actions without changing the MLLM. Accident rates fall by 32.07% and task performance rises 6.85%, with closed-loop and physical vehicle studies.
- thesis use: related work for the accept/replan stage.
- verified: abs meta fetched

### C-CoT: Counterfactual Chain-of-Thought with Vision-Language Models for Safe Autonomous Driving
- id: arXiv:2605.10744 | date: 2026-05 | venue: arXiv preprint
- authors: Tian, Kefei et al. | code: none seen
- relevance: MED — VLM evaluates consequences of alternative meta-action combinations in a tree before planning.
- what: Five-stage CoT (scene, critical objects, risk, counterfactual risk, plan) with a meta-action evaluation tree, fine-tuned on Qwen2.5-VL-7B with LoRA on DeepAccident-CCoT. Risk prediction recall 81.9%, collision rate 3.52%, L2 error 1.98 m.
- thesis use: competitor-style VLM-only candidate-action critic; contrast with tool-based inspection.
- verified: abs meta fetched

### LWDrive: Layer-Wise World-Model-Guided Vision-Language Model Planning for Autonomous Driving
- id: arXiv:2606.29879 | date: 2026-06 | venue: arXiv preprint
- authors: Yang, Chen et al. | code: promised, no URL
- relevance: MED — expands a diverse candidate set around a VLM plan, refines it, and a score head selects the best trajectory.
- what: Foresight Cascade Planner refines candidates with future-frame supervision, history, action queries and multi-view BEV features; a score head selects the final trajectory. Scores 92.0 on NAVSIM and 89.6 on NAVSIM-v2.
- thesis use: related work for trajectory scorer over candidate sets; no tool calls.
- verified: abs meta fetched

### Collision-Aware Vision-Language Learning for End-to-End Driving with Multimodal Infraction Datasets
- id: arXiv:2603.25946 | date: 2026-03 | venue: arXiv preprint
- authors: Koran, Alex et al. | code: none seen
- relevance: MED — collision prediction plug-in and a CARLA collision dataset; relates to the collision-check tool and hazard data.
- what: VLAAD (MIL-based video-language anomaly detector) integrated into TransFuser++ gives a 14.12% relative driving-score increase on CARLA; on the new Real-Collide dashcam set a 0.6B VLAAD beats a multi-billion VLM by 23.3% AUC. Releases CARLA-Collide.
- thesis use: possible dataset/benchmark source and learned collision-risk baseline.
- verified: abs meta fetched

### Does Visual Information Play a Decisive Role in Vision-Language-Action Model Driving Behavior?
- id: arXiv:2605.31041 | date: 2026-05 | venue: arXiv preprint
- authors: He, Jingtao et al. | code: none seen
- relevance: MED — structured visual perturbations (channel, information, structure level) on driving VLAs, open-loop and closed-loop.
- what: Finds evaluation-dependent dependency patterns and uneven visual grounding across abstraction levels (no numbers in the abstract).
- thesis use: guidance for the sensor-perturbation and noise-level design.
- verified: abs meta fetched

### Is VLA Reasoning Faithful? Probing Safety of Chain-of-Causation in Autonomous Driving Models
- id: arXiv:2605.17268 | date: 2026-05 | venue: arXiv preprint
- authors: Mayumu, Nicanor et al. | code: none seen
- relevance: MED — shows a driving VLA misses pedestrians and is fragile, which motivates tool checks.
- what: 300 Alpamayo-R1-10B inferences over 100 PhysicalAI-AV scenarios: reasoning fidelity 42.5%, 94 missed pedestrians in one third of pedestrian-relevant scenes, 97.7% trajectory fragility under mild perturbations, 48.3% mean reasoning-action consistency.
- thesis use: motivation citation for why perception tools are needed.
- verified: abs meta fetched

### Where Does the Answer Come From? Benchmarking View-Level Visual Evidence Identification in Multi-View MLLMs for Autonomous Driving
- id: arXiv:2606.09644 | date: 2026-06 | venue: arXiv preprint
- authors: Wang, Yimu et al. | code: none seen
- relevance: MED — a small benchmark where the model must pick which camera view supports the answer; a query-selection analogue.
- what: 122 conflict-centric QA pairs from 73 nuScenes scenes, evaluated for camera-view selection, oracle-view QA and joint prediction (no results in the abstract).
- thesis use: related benchmark for "where to look"; tiny.
- verified: abs meta fetched

### How Well Do Vision-Language Models Understand Sequential Driving Scenes? A Sensitivity Study
- id: arXiv:2604.06750 | date: 2026-04 | venue: arXiv preprint
- authors: Brusnicki, Roberto et al. | code: project page only
- relevance: MED — measures how resolution, frame count, intervals and layout affect VLMs on driving scenes; informs zoom/crop value.
- what: VENUSS compares 25+ VLMs over 2,600+ scenarios; top models reach 57% accuracy versus 65% for humans; VLMs do well on static object detection but poorly on vehicle dynamics and temporal relations.
- thesis use: supports why speed/distance tools help; a source for VLM-prompt design caveats.
- verified: abs meta fetched

### LIBERO-Occ: Evaluating and Improving Vision-Language-Action Models under Scene-Induced Occlusion via Viewpoint Imagination
- id: arXiv:2606.10862 | date: 2026-06 | venue: arXiv preprint
- authors: Li, Taishan et al. | code: https://github.com/litsh/Libero-Occ
- relevance: MED — occlusion benchmark with types and severity levels (manipulation, not driving).
- what: State-of-the-art VLAs degrade substantially under occlusion; Viewpoint Imagination generates a complementary view and conditions action on observed plus imagined evidence.
- thesis use: design reference for occlusion types and severities.
- verified: abs meta fetched

### Assistron: Bayesian Shared Autonomy with Off-the-shelf Vision-Language-Action Models
- id: arXiv:2606.23147 | date: 2026-06 | venue: arXiv preprint
- authors: Song, Pinhao et al. | code: https://github.com/mousecpn/Assistron.git
- relevance: MED — decides when to ask the human to intervene (phase-aware detection), without fine-tuning the VLA.
- what: Prioritizes human intervention at critical failure points and adjusts VLA actions through flow-matching guidance; improves success over pure autonomous baselines on a multi-task scene recovery benchmark (no numbers in the abstract).
- thesis use: weak related work on deferral.
- verified: abs meta fetched

### RouterVLA: Budgeted Commissioning and Expert Onboarding for Growing VLA Pools
- id: arXiv:2606.27355 | date: 2026-06 | venue: arXiv preprint
- authors: Ren, Xingyu et al. | code: none seen
- relevance: MED (weak) — chooses which expert to deploy under an exactly cost-matched probe budget.
- what: Reaches 60.53% held-out success, +1.64 points over a semantic shortlist, at a matched probe budget.
- thesis use: tangential example of budget-matched selection.
- verified: abs meta fetched

## Shortlisted but dropped
- 2603.07901 NaviDriveVLM: decoupled navigator/driver on nuScenes planning; no tools or candidates.
- 2603.09512 Probing the Reliability of Driving VLMs: FutureVQA consistency study; not about decisions or tools.
- 2603.10330 PC-Diffuser: CBF safety filter inside diffusion planning; no perception queries.
- 2603.11219 Senna-2: VLM/E2E consistency alignment; no candidates or queries.
- 2603.18178 VLM-AutoDrive: collision detection post-training on dashcam video; no decision link.
- 2603.18315 DriveVLM-RL: VLM reward for RL; training-time only.
- 2603.20232 Fusing Driver Perceived and Physical Risk: scenario screening for testing; not a planner.
- 2603.20668 ROI-Driven Foveated Attention: ROI for data representation in manipulation.
- 2603.25740 Drive My Way: preference personalization.
- 2603.28565 StreamingVLA: adaptive observation for latency, manipulation.
- 2604.04161 Adaptive Action Chunking: entropy-based chunk size, manipulation.
- 2604.09059 VLA-World: imagined next frame from a trajectory; no query selection or budget (borderline).
- 2604.12447 HazardArena: semantic-safety benchmark for manipulation VLAs.
- 2604.17915 OneDrive, 2605.08830 VECTOR-Drive, 2606.12396 VLGA, 2605.27038 TPS-Drive, 2605.08133 VLADriver-RAG, 2605.31271 DriveMA: driving VLA architectures without tools, queries or calibration.
- 2605.09948 LoopVLA: learned sufficiency for early exit (compute, not perception).
- 2605.11817 See What Matters: token pruning.
- 2605.13119 VLAs-as-Tools: VLA skills as tools for a VLM planner (manipulation execution, not perception tools).
- 2605.13632 Guide, Think, Act: user spatial guidance for manipulation.
- 2605.22283 SOMA: spatial memory for out-of-view manipulation.
- 2605.22896 Agentic-VLA: online adaptation via reward synthesis.
- 2605.23176 DriveSpatial: spatiotemporal QA benchmark, no hazard/occlusion injection.
- 2605.29114 ReasonBreak: text-corruption attacks on reasoning driving VLAs (adversarial, not sensor noise).
- 2606.01624 What to Test Next: coverage-gap selection for VLM verification; "acquisition" is of test slices, not perception queries.
- 2606.10495 SALSA: social navigation post-training.
- 2606.20092 EventVLA: keyframe memory for manipulation.
- 2606.20980 Robusto-2: human vs VLM VQA study of OOD dashcam footage.
- 2606.24759 UniDrive: risk understanding with a high-resolution branch; perception model, no selection (borderline).
- 2606.29892 T^2VLA: test-time RL from confidence.
- 2606.31106 What Probing Reveals about Autonomous Driving: probing of internal prediction; no decision tie.

## Leads not followed
- Second pass over the titles marked LOW added only 2603.20232, 2604.04161, 2605.09948, 2605.11817, 2606.10495 and 2606.29892 to the fetch list; all were dropped.
- 2606.27079 ForesightSafety-VLA, 2606.00773 SafeVLA-Bench and 2606.23686 LIBERO-Safety are manipulation safety benchmarks, not fetched.
- Cited-by lists for AS-DDTO (2606.22277) and TokenPB (2603.18091) were not checked.
