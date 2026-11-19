# M1_listing_e1a: early listing sweep, slice e1_00.tsv (316 titles, 2025-07 to 2026-03)

## Summary
- No close overlap found. Nothing in this slice does candidate-conditioned perception-query selection for driving, nor tool-calling driving agents. Titles were overwhelmingly manipulation VLAs (the slice is dominated by the "Vision-Language-Action" keyword).
- Nearest in spirit: Active Probing with Multimodal Predictions (2507.09822), a planner that chooses probing actions to reduce uncertainty about other agents, evaluated in MetaDrive (same simulator as the project). It is action-level probing, not perception-tool selection, so it is an idea source and a possible related-work cite.
- Candidate-set selection with a verifier/critic is the main transferable theme: Do What You Say (2510.16281, VLM picks among sampled action sequences by predicted outcome), VGAS (2602.07399, best-of-N critic), CoVer-VLA (2602.12281), MG-Select (2510.05681, confidence-based selection among candidates). All are manipulation, but they bear on the ranker side.
- When-to-act / when-to-ask: INSIGHT (2510.01389) learns help triggers from token-level uncertainty over time; DeeAD (2511.20720) is the only driving paper that gates compute on trajectory-vs-prior agreement (Bench2Drive). Both are scene/trajectory uncertainty triggers, i.e. closer to the scene-uncertainty baseline than to a candidate-divergence selector.
- Future calibration phase: two conformal-in-the-loop planners (2510.16376, 2511.18170) and a risk estimator over candidate action sequences that gates commands (CoFreeVLA, 2601.21712).
- Benchmarks/diagnostics: Drive-P2D (2601.14702) and the reasoning-planning disconnect study (2510.04532); the latter supports the project's observation that prompting a VLM works poorly.
- Second, more generous pass over LOW-marked driving titles (VLDrive, SpaceDrive, FLARE, HiST-VLA, LaST-VLA, NoRD, E3AD, TAD, ScenePilot, CARScenes, work zones, OGR, VLM-UDMC, VLAD, VLMs-guided decision, COVLM-RL, Nav-EE, MindDrive, VLA-R, doScenes/OpenEMMA): all abstracts fetched; only VLA-R, ReflectDrive, Nav-EE (dropped) and the benchmark/diagnostic papers above were kept or considered. None picks perception queries.
- 50 abstracts fetched in total; none were already in raw/*.md.

## Papers

### Active Probing with Multimodal Predictions for Motion Planning
- id: arXiv:2507.09822 | date: 2025-07 | venue: arXiv preprint
- authors: Gadginmath et al. | code: project page darshangm.github.io/papers/active-probing-multimodal-predictions/
- relevance: MED — information-gathering action choice under uncertainty in MetaDrive, but probes by acting, not by calling perception tools.
- what: Combines trajectory planning with multimodal predictions and a risk metric (closed form for Gaussian mixtures). An active probing mechanism selects actions that improve estimates of other agents' behavioral parameters. Evaluated in MetaDrive traffic scenarios; the abstract gives no numbers.
- thesis use: related work for value-of-information in driving; MetaDrive precedent; idea to borrow (risk metric over multimodal predictions).
- verified: abs meta fetched

### INSIGHT: INference-time Sequence Introspection for Generating Help Triggers in Vision-Language-Action Models
- id: arXiv:2510.01389 | date: 2025-10 | venue: arXiv preprint
- authors: Karli et al. | code: none seen
- relevance: MED — learns when to request help (an abstain/defer decision) but from the policy's own token uncertainty, manipulation setting.
- what: Extracts per-token entropy, log-probability and Dirichlet-based aleatoric/epistemic estimates from pi0-FAST and trains compact transformers to predict help triggers, under strong and weak supervision, in-distribution and OOD. Finds that modeling the temporal evolution of uncertainty beats static sequence-level scores.
- thesis use: baseline-style "uncertainty trigger" comparison; idea for the later abstain/fallback phase.
- verified: abs meta fetched

### Do What You Say: Steering Vision-Language-Action Models via Runtime Reasoning-Action Alignment Verification
- id: arXiv:2510.16281 | date: 2025-10 | venue: arXiv preprint
- authors: Wu et al. | code: project website yilin-wu98.github.io/steering-reasoning-vla/
- relevance: MED — samples multiple candidate action sequences, predicts outcomes by simulation, and has a VLM pick the best; a candidate-set selector with a VLM.
- what: Training-free runtime steering for reasoning VLAs: sample candidates from the same model, predict outcomes via simulation, a pre-trained VLM selects the one aligned with the textual plan. Reports up to 15% gain over prior work on behavior composition tasks (LIBERO-100 extension).
- thesis use: idea to borrow for the ranker; evidence for VLM-as-selector design.
- verified: abs meta fetched

### VGAS: Value-Guided Action-Chunk Selection for Few-Shot Vision-Language-Action Adaptation
- id: arXiv:2602.07399 | date: 2026-02 | venue: arXiv preprint
- authors: Xu et al. | code: github.com/Jyugo-15/VGAS
- relevance: MED — best-of-N critic that must rank near-miss candidates; relevant to ranking quality when candidates are close.
- what: Generation-selection framework: a fine-tuned VLA proposes, a geometric Transformer critic (Q-Chunk-Former) with Explicit Geometric Regularization selects, keeping action-ranking resolution among near-miss candidates. Claims consistent success and robustness gains; no numbers in the abstract.
- thesis use: idea for the ranker/critic; related work on near-tie candidates.
- verified: abs meta fetched

### Scaling Verification Can Be More Effective than Scaling Policy Learning for Vision-Language-Action Alignment
- id: arXiv:2602.12281 | date: 2026-02 | venue: arXiv preprint
- authors: Kwok et al. | code: none seen
- relevance: MED — test-time verification over generated candidates; accuracy-versus-compute scaling framing similar to the Pareto view.
- what: CoVer, a contrastive verifier, with CoVer-VLA: generate candidates over rephrased instructions, then select with the verifier. Reports 22% in-distribution and 13% OOD gains on SIMPLER, 45% in real-world, and on PolaRiS 14% task progress and 9% success rate.
- thesis use: related work on test-time selection; scaling-vs-budget argument.
- verified: abs meta fetched

### Verifier-free Test-Time Sampling for Vision-Language-Action Models
- id: arXiv:2510.05681 | date: 2025-10 | venue: arXiv preprint
- authors: Jang et al. | code: none seen
- relevance: MED — selects among multiple candidate actions with an internal confidence metric, no external verifier.
- what: MG-Select uses KL divergence from a reference action-token distribution (the same VLA with randomly masked state and language) as confidence for choosing among candidates, with joint training via dropout of conditions. Reports consistent improvements across simulation and real-world benchmarks (no numbers in abstract).
- thesis use: cheap verifier-free selection baseline idea.
- verified: abs meta fetched

### DeeAD: Dynamic Early Exit of Vision-Language Action for Efficient Autonomous Driving
- id: arXiv:2511.20720 | date: 2025-11 | venue: arXiv preprint
- authors: Hu et al. | code: none seen
- relevance: MED — driving VLA that decides when to stop computing by checking intermediate trajectories against planning priors; a when-to-compute decision tied to trajectories.
- what: Training-free early exit that terminates when predicted trajectories agree with lightweight planning priors within a deviation under 2 m, with a multi-hop layer-skipping controller. On Bench2Drive with ORION: up to 28% transformer-layer sparsity and 29% latency reduction while preserving planning quality and safety.
- thesis use: related work on trajectory-conditioned compute gating; shows the cost-vs-quality framing in driving.
- verified: abs meta fetched

### Conformal Prediction in The Loop: A Feedback-Based Uncertainty Model for Trajectory Optimization
- id: arXiv:2510.16376 | date: 2025-10 | venue: arXiv preprint
- authors: Wang et al. | code: none seen
- relevance: MED — conformal prediction regions fed back from realized trajectories into planning with a joint risk constraint; relevant to the calibrated-risk future phase.
- what: Feedback-Based CP (Fb-CP) for shrinking-horizon trajectory optimization, with CP-based posterior risk calculation, decision-focused iterative risk allocation, and an extension to distribution shift. Coverage guarantees proven; benchmark results not quantified in the abstract.
- thesis use: idea for conformal risk control in the accept/replan policy.
- verified: abs meta fetched

### Time-aware Motion Planning in Dynamic Environments with Conformal Prediction
- id: arXiv:2511.18170 | date: 2025-11 | venue: arXiv preprint
- authors: Liang et al. | code: project page time-aware-planning.github.io
- relevance: MED — conformal prediction in a planner with an adaptive quantile that tightens margins where uncertainty is high.
- what: Global planner (SIPP) with distribution-free safety guarantees and a local reactive planner using adaptive CP; the quantile is tuned automatically rather than fixed. Numerical experiments in dynamic cluttered environments; no numbers in abstract.
- thesis use: idea for adaptive conformal thresholds in the accept/inspect decision.
- verified: abs meta fetched

### CoFreeVLA: Short-Horizon Collision-Free Dual-Arm Manipulation via Vision-Language-Action Model and Risk Estimation
- id: arXiv:2601.21712 | date: 2026-01 | venue: arXiv preprint
- authors: Liu et al. | code: none seen
- relevance: MED — a calibrated risk estimator over candidate action sequences gates risky commands; structure similar to accept/reject of plans.
- what: Lightweight short-horizon self-collision risk estimator taking proprioception, visual embeddings and candidate action sequences; gates commands and synthesizes recovery. Across five bimanual tasks and six VLA backbones, collision rate falls from 0.54 to 0.23 and success rises from 0.45 to 0.61.
- thesis use: idea for the gate/fallback phase (manipulation, so only the pattern transfers).
- verified: abs meta fetched

### Drive-P2D: A Progressive Perception-to-Decision Benchmark for VLMs in Autonomous Driving
- id: arXiv:2601.14702 | date: 2026-01 | venue: arXiv preprint
- authors: Tang et al. | code: none seen
- relevance: MED — benchmark that separates perception from decision for driving VLMs and covers high-risk scenarios; useful for justifying where VLMs fail.
- what: 6,650 questions across Object, Scene and Decision levels with objective scoring of final answers and analysis of reasoning errors; evaluates mainstream VLMs on all and high-risk scenarios.
- thesis use: related work / motivation for tool-assisted perception.
- verified: abs meta fetched

### More Than Meets the Eye? Uncovering the Reasoning-Planning Disconnect in Training Vision-Language Driving Models
- id: arXiv:2510.04532 | date: 2025-10 | venue: arXiv preprint
- authors: Song et al. | code: none seen
- relevance: MED — shows driving VLM planning depends on ego/navigation priors rather than chain-of-thought; consistent with the project's finding that prompting the VLM to pick tools is weak.
- what: Builds DriveMind (plan-aligned CoT VQA from nuPlan), trains VLM agents with SFT and GRPO; removing priors causes large drops while removing CoT changes little. Proposes a training-free perturbation probe of prior reliance.
- thesis use: supports "contradicts the assumption that VLM reasoning drives decisions"; motivation for a learned geometry-feature selector.
- verified: abs meta fetched

### Discrete Diffusion for Reflective Vision-Language-Action Models in Autonomous Driving
- id: arXiv:2509.20109 | date: 2025-09 | venue: arXiv preprint
- authors: Li et al. | code: none seen
- relevance: MED — trajectory generation with a safety-aware reflection step that detects unsafe tokens and regenerates; a check-then-replan loop on NAVSIM.
- what: ReflectDrive discretizes the driving space into an action codebook, uses local search to find unsafe tokens and inpaint safe anchors without gradients. Evaluated on NAVSIM; abstract gives no numbers.
- thesis use: related work for the replan/fallback phase.
- verified: abs meta fetched

### Selective Perception for Robot: Task-Aware Attention in Multimodal VLA
- id: arXiv:2602.15543 | date: 2026-02 | venue: arXiv preprint
- authors: Son et al. | code: none seen
- relevance: MED — lightweight router decides which camera views to feed the policy based on predicted task relevance, with compute proportional to relevance; a budgeted input-selection decision (manipulation).
- what: Adaptive routing on the text prompt and wrist camera predicts view relevance, attenuating low-utility views; router labels come from an automated VLM labeling pipeline. Real-world manipulation gains in efficiency and control performance (no numbers in abstract).
- thesis use: idea for choosing which input to fetch under a budget; VLM-labelled supervision precedent.
- verified: abs meta fetched

### VLA-R: Vision-Language Action Retrieval toward Open-World End-to-End Autonomous Driving
- id: arXiv:2511.12405 | date: 2025-11 | venue: arXiv preprint
- authors: Seong et al. | code: none seen
- relevance: MED — uses a frozen VLM for open-world detection/segmentation features feeding an action retrieval head; frozen-VLM-features-to-planner pattern.
- what: Frozen VLM perception features, a Q-Former bottleneck, and vision-action contrastive learning for action retrieval; real-world robotic platform demos, no numbers in abstract.
- thesis use: related work for the frozen-VLM-embedding input to the selector.
- verified: abs meta fetched

## Shortlisted but dropped
- 2507.17049 Evaluating Uncertainty and Quality of VLA-enabled Robots: manipulation uncertainty metrics, no decision component.
- 2509.04018 FPC-VLA: manipulation failure supervisor, no budget or tool angle.
- 2511.18960 AVA-VLA: attention reweighting within a VLA, not a query decision.
- 2512.01715 Transport Discrepancy (DiG): manipulation reliability gate, no cost tradeoff.
- 2512.11891 VLSA/AEGIS: control-barrier safety layer for manipulation.
- 2512.02834 TACO: pseudo-count verifier for action chunks; weaker than the other selection papers.
- 2601.00969 V-VLAPS and 2508.12211 VLAPS, 2509.22643 VLA-Reasoner: MCTS with VLA priors, manipulation, not tool/query selection.
- 2512.05277 TAD (temporal understanding benchmark): video QA, no query decision.
- 2510.02803 Work zones challenge VLM planning: failure study and RAG, not relevant to tool choice.
- 2510.01795 Nav-EE: navigation-guided early exit, latency only.
- 2512.09349 COVLM-RL: critical-object reasoning for RL, no query budget.
- 2602.18020 AWARE: training-free VLA module, manipulation.
- 2601.02295 CycleVLA: manipulation failure prediction/backtracking.
- 2602.06339 Action Hallucination, 2602.04228 Reshaping action error: theory/training objectives.
- 2509.17042 OGR: VLM reward/curriculum generation.
- 2512.13636 MindDrive: online RL VLA, no query decision.
- 2511.13881 VLMs Guided Interpretable Decision Making, 2507.15266 VLM-UDMC, 2507.01284 VLAD: VLM as high-level driving advisor, no tool or candidate selection.
- 2602.04184 doScenes/OpenEMMA instructions: instruction-conditioned planning.
- 2510.04550 TRAJECT-Bench: LLM tool-use benchmark outside driving; only a naming overlap on tool selection.
- 2602.02459 TIC-VLA, 2510.18337 MoTVLA: latency-aware or fast-slow reasoning, no query decision.
- 2601.19582 ScenePilot-4K, 2511.10701 CARScenes: driving VLM datasets with risk labels but no hazard injection or perturbation protocol.
- 2601.05611 FLARE, 2512.10719 SpaceDrive, 2511.06256 VLDrive, 2512.04733 E3AD, 2602.13329 HiST-VLA, 2603.01928 LaST-VLA, 2602.21172 NoRD: driving VLM/VLA architectures or training recipes, no perception-query component.

## Leads not followed
- Drive-P2D and ScenePilot-Bench could be mined for hazard categories, not done.
- Cited-by lists for Active Probing (2507.09822) in MetaDrive were not checked.
