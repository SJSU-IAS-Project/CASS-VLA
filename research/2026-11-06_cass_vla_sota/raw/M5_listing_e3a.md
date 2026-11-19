# M5_listing_e3a — listing sweep e3_00 (Jul 2025 - Dec 2025 titles), early-triage pass

Input: 407 titles. 28 shortlisted, all 28 abstracts fetched with absfetch.py (meta tags). None was already in raw/*.md or known_papers.txt.

## Summary
- No close overlap found: nothing in this slice picks a perception query conditioned on the candidate-trajectory set. The nearest idea is Perception in Plan (2508.11488), which gathers traffic elements along multi-mode anchored trajectories, but it is an end-to-end network design, not a tool call under a budget.
- Closest on "whether to call the expensive model": AdaDrive (2511.06253) learns when to activate an LLM and how much to fuse its output. It is scene-driven (complexity and confidence), so it is a second scene-uncertainty-style baseline beside DriveAgent-R1.
- Closest on "which inputs to keep": RDAR (2509.19789) casts agent selection as an MDP with a binary mask and measures driving quality against agents processed. A different axis (agents, not tools) but the same relevance-under-budget framing.
- Closest on cost-vs-accuracy of perception: EneAD (2510.25205) switches perception models and framerate by a scene-difficulty classifier.
- Defer / ask for help: LAVQA (2511.11840), a shared-autonomy VQA loop where the car halts and queries a remote human; evaluated by collision rate in CARLA.
- Hazard and occlusion material for the benchmark side: Occluded nuScenes, the latent-risk safety certificate (2510.13114), PotentialRiskQA, NuRisk, WaymoQA. All are datasets or controllers, none has a tool-query budget.
- Collision-check tool and planner anchors: the collision-probability estimator (2510.05729) and the proposal/collision-check finding in 2510.15505 bear on the geometric collision-check tool and the oracle.
- Most of the rest of the slice is world models, Gaussian splatting, classical motion planning, manipulation VLAs and adversarial attacks, and was skipped on title.

## Papers

### AdaDrive: Self-Adaptive Slow-Fast System for Language-Grounded Autonomous Driving
- id: arXiv:2511.06253 | date: 2025-11 | venue: arXiv preprint
- authors: Zhang, Ruifei et al. | code: https://github.com/ReaFly/AdaDrive
- relevance: HIGH — learns when to invoke an LLM in a driving stack, a "whether to call" decision; scene-conditioned, so a baseline-style comparator.
- what: Slow-fast framework deciding when the LLM is activated (adaptive activation loss, comparative learning) and how strongly its output is fused with a conventional planner (continuous scaled influence from scene complexity and prediction confidence). The abstract reports state-of-the-art accuracy and efficiency on language-grounded driving benchmarks; no numbers given.
- thesis use: related work / baseline family for scene-uncertainty triggering; contrast: its trigger does not see the candidate set.
- verified: abs meta fetched

### Perception in Plan: Coupled Perception and Planning for End-to-End Autonomous Driving
- id: arXiv:2508.11488 | date: 2025-08 | venue: arXiv preprint
- authors: Zhang, Bozhou et al. | code: none in abstract
- relevance: HIGH — perception targeted by planning priors (multi-mode anchored trajectories); closest conceptual neighbour to candidate-conditioned querying, though not a budgeted tool choice.
- what: VeteranAD gathers traffic elements along anchored trajectories and predicts future trajectories autoregressively while focusing on relevant regions at each step. Reports state-of-the-art on NAVSIM and Bench2Drive (no numbers in abstract).
- thesis use: related work (trajectory-conditioned perception inside a network, versus an explicit tool selector); idea to borrow: ROI along each candidate.
- verified: abs meta fetched

### RDAR: Reward-Driven Agent Relevance Estimation for Autonomous Driving
- id: arXiv:2509.19789 | date: 2025-09 | venue: arXiv preprint
- authors: Bosio, Carlo et al. | code: none in abstract
- relevance: MED — learns per-agent relevance by choosing which agents to drop from a pre-trained behaviour model's input, with comparable driving performance at fewer agents.
- what: Masking is an MDP whose action is a binary agent mask. Evaluated on a large-scale driving dataset; comparable progress, safety and performance with significantly fewer agents (no numbers in abstract).
- thesis use: idea to borrow (value of an input measured by effect on the decision); related work for the "decision-relevant" argument.
- verified: abs meta fetched

### Energy-Efficient Autonomous Driving with Adaptive Perception and Robust Decision
- id: arXiv:2510.25205 | date: 2025-10 | venue: arXiv preprint
- authors: Xia, Yuyang et al. | code: none in abstract
- relevance: MED — compute-budgeted perception: selects perception model and framerate by a scene-difficulty classifier, plus an RL decision module robust to perturbed perception.
- what: EneAD tunes perception "knobs" with Bayesian optimisation and switches them per scenario; it reports perception consumption reduced by 1.9x to 3.5x (rest of the abstract is cut off in my fetch).
- thesis use: cost-axis related work; scene-difficulty switching is another trajectory-agnostic trigger.
- verified: abs meta fetched

### LAVQA: A Latency-Aware Visual Question Answering Framework for Shared Autonomy in Self-Driving Vehicles
- id: arXiv:2511.11840 | date: 2025-11 | venue: arXiv preprint
- authors: Xie, Shuangyu et al. | code: none in abstract
- relevance: MED — when uncertainty is high the vehicle halts and asks a remote human via VQA; a defer/ask-for-help setting with a latency-aware risk map.
- what: Adds a Latency-Induced Collision Map to visual queries. Closed-loop CARLA simulation: collision rates reduced by over 8x against latency-agnostic baselines.
- thesis use: related work for the future inspect/fallback phase.
- verified: abs meta fetched

### Enhancing LLM-based Autonomous Driving with Modular Traffic Light and Sign Recognition
- id: arXiv:2511.14391 | date: 2025-11 | venue: arXiv preprint
- authors: Schmidt, Fabian et al. | code: https://github.com/iis-esslingen/TLS-Assist
- relevance: MED — a dedicated traffic-light/sign recogniser feeds an LLM driver, i.e. a perception tool for small safety-critical objects; always-on rather than selected.
- what: TLS-Assist turns detections into structured text for the LLM input; closed loop on LangAuto in CARLA, up to 14% relative improvement over LMDrive and 7% over BEVDriver.
- thesis use: evidence that a light-state tool helps; an always-on baseline point for the Pareto curve.
- verified: abs meta fetched

### Occluded nuScenes: A Multi-Sensor Dataset for Evaluating Perception Robustness in Automated Driving
- id: arXiv:2510.18552 | date: 2025-10 | venue: arXiv preprint
- authors: Kumar, Sanjay et al. | code: none in abstract
- relevance: MED — parameterised, reproducible occlusions for camera (four types), radar and LiDAR (three degradations each).
- what: Extension of nuScenes for controlled sensor degradation; supports robustness evaluation of fusion models.
- thesis use: benchmark reference for occlusion injection design; not a decision benchmark.
- verified: abs meta fetched

### Safe Driving in Occluded Environments
- id: arXiv:2510.13114 | date: 2025-10 | venue: arXiv preprint
- authors: Wang, Zhuoyuan et al. | code: none in abstract
- relevance: MED — probabilistic safety certificate for latent risk from occluded objects, usable in MPC or learned policies; tested in CARLA.
- what: Probabilistic invariance gives linear action constraints that bound the latent risk probability, without needing the hidden objects observed.
- thesis use: related work for occlusion hazards and for the accept/fallback phase.
- verified: abs meta fetched

### Seeing before Observable: Potential Risk Reasoning in Autonomous Driving via Vision Language Models
- id: arXiv:2511.22928 | date: 2025-11 | venue: arXiv preprint
- authors: Liu, Jiaxin et al. | code: none in abstract
- relevance: MED — risks not yet observable, inferred from precursors; dataset PotentialRiskQA and a VLM framework PR-Reasoner.
- what: Fine-tuning on PotentialRiskQA improves potential-risk reasoning over baseline VLMs (no numbers in abstract).
- thesis use: hazard-type taxonomy for occlusion scenarios; VLM baseline.
- verified: abs meta fetched

### NuRisk: A Visual Question Answering Dataset for Agent-Level Risk Assessment in Autonomous Driving
- id: arXiv:2509.25944 | date: 2025-09 | venue: arXiv preprint
- authors: Gao, Yuan et al. | code: https://github.com/TUM-AVS/NuRisk
- relevance: MED — agent-level risk VQA on BEV sequences; 2.9K scenarios, 1.1M agent-level samples.
- what: Benchmarked VLMs peak at 33% accuracy at high latency; a fine-tuned 7B VLM agent reaches 41% with 75% lower latency.
- thesis use: evidence that frozen VLMs reason poorly about risk, matching the project's finding that the VLM mostly says "none".
- verified: abs meta fetched

### WaymoQA: A Multi-View Visual Question Answering Dataset for Safety-Critical Reasoning in Autonomous Driving
- id: arXiv:2511.20022 | date: 2025-11 | venue: arXiv preprint
- authors: Yu, Seungjun et al. | code: https://github.com/sjyu001/WaymoQA
- relevance: MED — 35,000 human-annotated QA pairs for safety-critical reasoning where avoiding one risk can create another; MLLMs underperform on these versus normal scenes.
- what: Two-stage task (resolve immediate risk, then downstream risk); fine-tuning on the dataset improves reasoning.
- thesis use: benchmark / VLM-weakness evidence.
- verified: abs meta fetched

### Precise and Efficient Collision Prediction under Uncertainty in Autonomous Driving
- id: arXiv:2510.05729 | date: 2025-10 | venue: arXiv preprint
- authors: Kaufeld, Marc et al. | code: https://github.com/TUM-AVS/Collision-Probability-Estimation
- relevance: MED — two semi-analytic collision probabilities for planned trajectories under pose/velocity uncertainty; a principled version of the geometric collision-check tool.
- what: Matches Monte Carlo results with large runtime savings (no numbers in abstract).
- thesis use: idea to borrow for the collision-check tool under noise.
- verified: abs meta fetched

### Perfect Prediction or Plenty of Proposals? What Matters Most in Planning for Autonomous Driving
- id: arXiv:2510.15505 | date: 2025-10 | venue: arXiv preprint
- authors: Distelzweig, Aron et al. | code: none in abstract
- relevance: MED — on Val14 and interPlan, perfect prediction does not improve planning; proposal quality matters, with predictions used mainly for collision checks.
- what: A PDM-based planner with better diverse proposals outperforms existing methods.
- thesis use: supports the candidate-set emphasis; a proposal generator for candidates.
- verified: abs meta fetched

### Scalable Offline Metrics for Autonomous Driving
- id: arXiv:2510.08571 | date: 2025-10 | venue: arXiv preprint
- authors: Aich, Animikh et al. | code: none in abstract
- relevance: MED — offline metrics correlate poorly with closed-loop outcomes; an epistemic-uncertainty offline metric improves correlation by over 13%.
- what: Simulation analysis plus real-world validation.
- thesis use: caveat for the open-loop evaluation; cite as limitation.
- verified: abs meta fetched

### Alpamayo-R1: Bridging Reasoning and Action Prediction for Generalizable Autonomous Driving in the Long Tail
- id: arXiv:2511.00088 | date: 2025-10 | venue: arXiv preprint
- authors: NVIDIA et al. | code: none in abstract
- relevance: MED — reasoning VLA with a diffusion trajectory decoder; up to 12% planning-accuracy gain on challenging cases and 35% fewer close encounters in closed-loop simulation.
- what: Chain of Causation dataset, Cosmos-Reason backbone, SFT then RL; RL improves reasoning quality by 45% and reasoning-action consistency by 37%.
- thesis use: VLM/VLA driving anchor; no tool use.
- verified: abs meta fetched

### Calibrating the Full Predictive Class Distribution of 3D Object Detectors for Autonomous Driving
- id: arXiv:2510.01829 | date: 2025-10 | venue: arXiv preprint
- authors: Schröder, Cornelius et al. | code: none in abstract
- relevance: MED — confidence calibration of detector class outputs; relevant to noisy-tool confidences and the future calibration phase.
- what: Auxiliary calibration losses plus isotonic regression give best calibration for CenterPoint and PillarNet; DSVT-Pillar cannot be jointly calibrated.
- thesis use: background for the calibration phase.
- verified: abs meta fetched

## Shortlisted but dropped
- 2511.13297 CorrectAD: data-generation loop for fixing failures, no query selection.
- 2511.14178 VLA-Pilot: manipulation policy steering at inference time.
- 2508.10511 KDPE: manipulation diffusion-policy trajectory filtering.
- 2509.01944 AutoDrive-R2: CoT with self-reflection, no tools or selection.
- 2512.01830 OpenREAD: LLM-as-critic is for reasoning rewards in training, not candidate scoring.
- 2510.07210 HyPlan: POMDP planner in CARLA, no perception queries.
- 2511.01334 Embodied Cognition Augmented End2End: EEG-based cognition features.
- 2509.07412 Attention and Risk-Aware Decision Framework: PPO with risk attention, not relevant.
- 2508.02919 Context-aware Risk Assessment (CRI): risk index modulating control, no query or calibration.
- 2511.19221 Percept-WAM: unified perception inside a VLM, no tool selection.
- 2510.21867 Addressing Corner Cases (WM-MoE): motion forecasting.
- 2508.21080 2COOOL: workshop summary, no method or numbers.

## Leads not followed
- Only titles in e3_00 were read; titles from Dec 2025 onward in this file are few (file ends at 2512.02417).
- Titles on trajectory scoring with VLM critics (for example DiffVLA++, ResAD) were skipped from titles alone; not checked.
