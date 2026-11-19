# B_budgeted_perception — budgeted / selective / task-driven perception and information acquisition

Scan date 2026-11-06. Sources: WebSearch, arXiv abs fetch (absfetch.py), OpenReview ICLR 2027 search records (abstracts only; OpenReview gives no authors/dates in the search record, so those fields are marked). No full texts read, so every number below is from an abstract.

## Summary

- **No paper found that does candidate-conditioned perception-tool selection for driving.** The closest by idea are (1) MosaicDrive (ICLR 2027 submission), which attacks exactly the DriveAgent-R1 weakness the project targets, namely that an uncertainty trigger is computed from evidence already held and says nothing about unseen regions, but conditions on the question, not on the candidate plans; (2) "The Decision Value of Perception Compute" (DEEP, ICLR 2027 submission), which defines the value of escalating perception by its effect on a downstream planner and scores allocators against a budget-constrained decision oracle (same evaluation logic as PlanDiscrim's Pareto + oracle selector); (3) "What's Hidden Matters" (2607.00283), which ranks occluded agents by planning impact (PKL).
- **DEEP is the most important find for the thesis framing.** It reports that 34-54% of escalations that change downstream loss make it worse, that perception-level gain often disagrees in sign with decision value, and that learned allocators pick nearly as much harm as random. Directly supports "scene/perception uncertainty is the wrong trigger" and warns that a learned selector may barely beat random. Read in full before writing the related-work section.
- **Dominant 2025-26 trend is "when to invoke the expensive thing" with a trigger or gate** (ETM, StreamSelect, ASSCG, DualDriveVLA, AdaThinkDrive, ToolGate, ElegantVLA, Act-Think-Abstain). These are all trajectory-agnostic, scene/temporal-feature triggers, i.e. the same family as the scene-uncertainty baseline. ETM explicitly uses information-gain pseudo-labels (close to the project's "expected gain" targets) but gates a whole VLM call, not a choice among tools, and is not conditioned on candidates.
- **Second trend: VLM agents that actively acquire evidence by zoom/crop/view tools, trained with RL and an efficiency reward** (DriveScout, OmniDrive-R1, AdaTurn, WATCH, Starve to Perceive, ACTIVE-o3, CropVLM, MTRDrive). Mostly VQA-style, not planner-in-the-loop.
- **Third: formal value-of-information / sensing-cost work outside driving** (VoI for LLM agents 2601.06407, Certifying Information Value of Adaptive Tool Use, Belief-Conditioned Diffusion for sensor subsets, Xu's "values of perception", learned VoI for navigation). Good for the theoretical definition of "expected gain" and for a certificate-style argument that adaptive selection can only help when the interface has positive information gap.
- **Classic "which object matters to the plan" line** (Agent Prioritization 1909.08792, HOIST counterfactual importance 2312.02467, Importance Filtering 2303.06935, PKL) labels importance by perturbing/removing an object and measuring plan change. This is the closest classic precedent for planning-derived (rather than perception-derived) relevance labels; the project's expected-gain targets are a tool-level analog.
- **Gap that remains open (as far as this scan shows):** conditioning the query choice on how the K candidate trajectories diverge. Nobody in this sub-area was found doing it. Treat this as a claim to re-check with agents A/C/D before asserting novelty.
- Caveat: several ICLR 2027 submissions are under double-blind review and may change; cite as submissions.

## Papers

### MosaicDrive: Task-Aware Multi-Camera Reasoning for Autonomous Driving
- id: OpenReview 9I96DzTfHb (ICLR 2027 submission) | date: UNVERIFIED (2026, submission cycle) | venue: ICLR 2027 submission
- authors: not shown in search record | code: none seen
- relevance: HIGH — close overlap in motivation: criticizes uncertainty-triggered acquisition in tool-augmented driving agents and replaces it with task-conditioned acquisition plus verification; conditions on the question, not on candidate plans.
- what: Argues the confidence that triggers retrieval of extra camera views is computed from evidence already held, so it carries no information about never-observed regions, and that extra evidence can overturn a correct prior answer. Derives camera and tool requirements from the question, uses a source-aware verifier (Arbiter) with targeted re-queries, and evaluates on MOSICQA (multi-camera driving QA with executed tool traces) with a protocol separating coverage from selectivity, correction from abstention, and answer quality from acquisition cost. No numbers in the abstract.
- thesis use: competitor / argument ally against scene-uncertainty triggering; borrow its protocol of separating coverage vs selectivity vs cost; note it is QA-based, not planner-conditioned.
- verified: OpenReview search record (abstract) read; not arXiv.

### The Decision Value of Perception Compute (DEEP: Decision Evaluation for Escalated Perception)
- id: OpenReview l9QJO8BIoE (ICLR 2027 submission) | date: UNVERIFIED (2026) | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: HIGH — defines decision value of spending extra perception compute on an input as downstream-loss change, and benchmarks pre-escalation allocators against a budget-constrained decision oracle with selection/latency/energy budgets and allocator self-cost charged.
- what: Uses monocular geometry on KITTI and nuScenes and the PDM-Closed planner open-loop on nuPlan. Reports that 34-54% of escalations that change downstream loss make it worse; perception gain often disagrees in sign with decision value; choosing signals by missed-object perception gain rather than decision value loses 7.4% of all-cheap loss on average; learned allocators recover part of the oracle value but select nearly as much harm as random, and once their own compute is charged at a 20% latency budget only the lightweight ones remain useful (abstract truncated in my fetch).
- thesis use: framing and baseline design (oracle selector, budget curves, charge the selector's own cost); evidence that uncertainty triggers can be harmful; risk that learned selectors give small gains over random.
- verified: OpenReview search record (abstract, truncated at ~1600 chars) read.

### What's Hidden Matters: Identifying Planning-Critical Occluded Agents using Vision-Language Models
- id: arXiv:2607.00283 | date: 2026-07 | venue: arXiv preprint
- authors: Chahe, Amirhosein et al. | code: none seen
- relevance: HIGH — ranks occluded agents by their impact on the ego plan (Planning KL-divergence), i.e. relevance defined by plan change, for occlusion hazards like the project's.
- what: Uses PKL to rank occluded agents on nuScenes, has GPT-5 annotate the top scenes, builds a benchmark and fine-tunes VLMs on it. Search-mirror summary: PKL-guided selection beats random sampling by roughly 30% (from a secondary source, not checked in the paper text).
- thesis use: benchmark / idea to borrow (PKL as planning-relevance label for the ROI/occlusion tool).
- verified: abs meta fetched.

### ETM: Event Trigger Module based VLM for Autonomous Driving
- id: OpenReview oa4EWvJlLC (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: HIGH — learned trigger deciding when to invoke an expensive VLM, framed as information-gain-driven and cost-balanced, trained with information-gain pseudo-labels plus corner-case labels; nuScenes.
- what: Lightweight event-driven policy activates the VLM only when refreshed reasoning is expected to improve planning. Abstract: comparable planning accuracy to always-triggered VLM systems while cutting invocation rate from 100% to 32%, latency by nearly 50%, compute by about 64%.
- thesis use: closest "expected-gain label" precedent in driving; competitor to the scene-uncertainty baseline; differs in that it gates one VLM, not which tool, and not candidate-conditioned.
- verified: OpenReview search record (abstract) read.

### DriveScout: Sharpening MLLM Perception in Autonomous Driving with Adaptive and Robust Visual Focusing
- id: OpenReview rXDM54aQdX (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: HIGH — a DriveAgent-R1-style follow-up: RL for "selective evidence acquisition" by cropping, with Necessity-Aware Focus Optimization to cut redundant visual operations; includes a paired clear/motion-blur nuScenes VQA benchmark (SCOUT).
- what: Target-Grounded Spatial Credit and a Progressive Blur Curriculum; claims better blur robustness and fewer redundant operations on SCOUT and two other driving benchmarks (no numbers in abstract).
- thesis use: competitor / related work for the learned-tool-use side; its necessity reward is an alternative to expected-gain targets; sensor-degradation benchmark idea.
- verified: OpenReview search record (abstract) read.

### Adaptive Inference for Streaming Multimodal Scene Understanding in Autonomous Driving (StreamSelect)
- id: OpenReview KQwcH95tnN (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: Chen, Yitao et al. (Toyota Motor North America, per record) | code: none seen
- relevance: MED — learned activation model decides when updated VLM reasoning is needed, using LiDAR BEV features as queries over camera tokens; includes a benchmark with per-frame alert labels (DriveStream) on nuScenes.
- what: Activation F1 66.0% on DriveStream-Alert, +2.2% over global multi-camera fusion with 43% fewer trainable parameters; invokes a pluggable VLM above a threshold, otherwise reuses the last response.
- thesis use: baseline family (scene-triggered gating); evaluate activation separately from downstream effect, as in its benchmark design.
- verified: OpenReview search record (abstract, truncated) read.

### Value of Information: A Framework for Human-Agent Communication
- id: arXiv:2601.06407 | date: 2026-01 | venue: ACL 2026 (per search result listing; not checked in proceedings)
- authors: Dong, Yijiang River et al. | code: none seen
- relevance: MED — decision-theoretic VoI chooses whether to ask a question by expected utility gain vs cost, with no tuned threshold; matched or exceeded the best manually tuned baselines on 20 Questions, medical diagnosis, flight booking, e-commerce.
- what: Inference-time method, reports up to 1.36 utility (abstract truncated in my fetch).
- thesis use: idea to borrow for the "accept/inspect/replan/fallback" phase: threshold-free VoI rule instead of tuned confidence thresholds.
- verified: abs meta fetched.

### ToolGate: Token-Efficient Pre-Call Control for Tool-Augmented Vision-Language Agents
- id: arXiv:2606.03054 | date: 2026-06 | venue: arXiv preprint
- authors: Liu, Anjie et al. | code: none seen
- relevance: HIGH — learned execute/skip controller for perceptual tool calls; finds most tool calls do not change the immediate answer (helpful 11.8% vs harmful 9.9% calls in the baseline).
- what: Lightweight controller on trajectory text and structural features cuts token cost to 64-69% of unrestricted ReAct on two Qwen3-VL backbones across five benchmarks while preserving average accuracy (abstract).
- thesis use: baseline / evidence that naive agents over-call tools; abstain-on-tool analog; not driving, not candidate-aware.
- verified: abs meta fetched.

### Certifying the Information Value of Adaptive Tool Use
- id: OpenReview JUWtWs4Tgb (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: MED — defines adaptive information value (gain from choosing queries after seeing responses vs fixing them in advance under the same budget) and gives a finite-budget upper-bound certificate with heterogeneous query costs.
- what: In network-diagnosis experiments, when models choose their own queries, adaptive querying underperforms pre-committed querying; externally optimized adaptive evidence gains 5.84 points on a positive-gap interface.
- thesis use: contradicts "LLM picks the tool" (consistent with the project's finding that the VLM says "none"); a way to argue an upper bound on selector gain given the tool interface.
- verified: OpenReview search record (abstract) read.

### Values of Perception, Prediction, Communication, and Common Sense in Decision Making
- id: arXiv:2601.06077 | date: 2025-12 | venue: arXiv preprint
- authors: Xu, Aolin | code: none
- relevance: MED — decision-theoretic definition of the value of perception; shows value of perception without prediction can be negative; asks "do we need to observe agent X, what order".
- what: Defines values with mutual-information-like properties; theory only.
- thesis use: formal definition of "expected gain" of a tool and a reason it can be negative (consistent with DEEP).
- verified: abs meta fetched.

### Belief-Conditioned One-Step Diffusion: Real-Time Trajectory Planning with Just-Enough Sensing
- id: arXiv:2508.12166 | date: 2025-08 | venue: CoRL 2025 (PMLR 305)
- authors: Puthumanaillam, Gokul et al. | code: project page bcod-diffusion.github.io (from search result, not opened)
- relevance: MED — chooses which minimal sensor subset to keep on, using the spread of a diffusion planner's trajectories as an uncertainty proxy, with an RL sensor selector and a calibrated CVaR risk scalar; about 10 ms.
- what: Marine robot, mapped environment; reduces sensing energy while matching always-on goal-reach (per search summary of abstract).
- thesis use: closest example of trajectory-spread (candidate divergence) driving a sensing decision; idea to borrow: trajectory dispersion as a selector feature.
- verified: abs meta fetched; method details from search summary.

### AdaThinkDrive: Adaptive Thinking via Reinforcement Learning for Autonomous Driving
- id: arXiv:2509.13769 | date: 2025-09 | venue: arXiv preprint
- authors: Luo, Yuechen et al. | code: none seen
- relevance: MED — learns when to apply CoT (fast answer vs slow think) with an Adaptive Think Reward comparing trajectory quality across modes; GRPO.
- what: Abstract: NAVSIM PDMS 90.3, +1.7 over the best vision-only baseline; beats never-think and always-think by 2.0 and 1.4 PDMS; 14% less inference time than always-think. (The 96%/84% CoT-usage figures in an earlier draft came from a search summary and are not in the abstract; UNVERIFIED.)
- thesis use: baseline family (trajectory-quality-based reward as the trigger signal, not scene features); related-work "think vs look".
- verified: abs meta fetched; numbers from search summary.

### AutoVLA: A VLA Model for End-to-End Autonomous Driving with Adaptive Reasoning and Reinforcement Fine-Tuning
- id: arXiv:2506.13757 | date: 2025-06 | venue: arXiv preprint
- authors: Zhou, Zewei et al. | code: none seen
- relevance: LOW — before the scan window; adaptive fast/slow reasoning via RFT.
- what: Unifies reasoning and action tokens; RFT reduces unnecessary reasoning.
- thesis use: background for adaptive-compute driving VLAs.
- verified: abs meta fetched.

### ASSCG: Just-Right Gating over Chattering for Fast-Slow LLM Planning in Autonomous Driving
- id: arXiv:2606.25509 | date: 2026-06 | venue: arXiv preprint
- authors: Ang, Sining et al. | code: project page williamxuanyu.github.io/asscg (from abstract)
- relevance: MED — Query/Cache/Drop gate for slow-system invocation, trained with SFT then compute-aware GRPO.
- what: AsyncDriver on nuPlan Hard20 closed loop: 67.28 (+2.28), latency -60%; RecogDrive-based dual system on NAVSIM: 91.4 PDMS (+0.6), speed +25%.
- thesis use: baseline family; budget-aware RL gate; the Cache action (reuse a previous answer) is a third option next to query/abstain.
- verified: abs meta fetched.

### From Representational Complementarity to Dual Systems (DualDriveVLA)
- id: arXiv:2602.10719 | date: 2026-02 | venue: arXiv preprint
- authors: Ang, Sining et al. | code: none seen
- relevance: MED — abstract: an oracle best-of-two VLM+ViT selector reaches 93.58 PDMS on NAVSIM; HybridDriveVLA selects from a compact cross-model candidate set with a learned trajectory scorer, PDMS 90.80 to 92.10; DualDriveVLA invokes the VLM in only 15% of scenarios, 91.00 PDMS with about 1.9x lower latency than the VLM baseline (CORRECTED: an earlier draft said 3.2x throughput, which came from a search summary and was wrong). Code: github.com/WilliamXuanYu/HybridDriveVLA (will be available, per abstract).
- what: Compares VLM vs vision-only backbones under a fixed diffusion planner; builds a confidence-based dual system.
- thesis use: baseline; the oracle-selector-vs-confidence-selector gap is the same shape as the project's Pareto story.
- verified: abs meta fetched.

### FASIONAD++ (Fast-Slow fusion with uncertainty-triggered slow system)
- id: arXiv:2503.08162 | date: 2025-03 | venue: arXiv preprint
- authors: Qian, Kangan et al. | code: none seen
- relevance: LOW — pre-window; slow VLM system activates through uncertainty estimation.
- what: Dynamic switching based on real-time uncertainty, with information-bottleneck feedback.
- thesis use: representative scene-uncertainty trigger.
- verified: abs meta fetched.

### MTRDrive: Memory-Tool Synergistic Reasoning for Robust Autonomous Driving in Corner Cases
- id: arXiv:2509.20843 | date: 2025-09 | venue: arXiv preprint
- authors: Luo, Ziang et al. | code: none seen
- relevance: MED — VLM with memory retrieval and dynamic toolkit (detection, open-vocab detection, cropping); Roadwork benchmark. Search summary: NAVSIM PDMS 88.3 for the 3B model.
- what: The VLM decides whether and how to invoke tools; new roadwork construction benchmark for zero-shot generalization.
- thesis use: DriveAgent-R1 competitor; Roadwork as a possible hazard benchmark.
- verified: abs meta fetched.

### Drive by Hindsight and Foresight: Tool-Grounded Synergistic Reasoning over Hierarchical Memory
- id: arXiv:2609.08217 | date: 2026-09 | venue: arXiv preprint
- authors: Chen, Baojie et al. | code: none seen
- relevance: MED — follow-up to the memory-tool line; model adaptively invokes tools guided by scene state and retrieved experience.
- what: Hierarchical driving memory plus proactive tool invocation in a closed loop (abstract; numbers not read).
- thesis use: competitor for tool-calling driving agents.
- verified: abs meta fetched.

### AgentThink: A Unified Framework for Tool-Augmented Chain-of-Thought Reasoning in VLMs for Autonomous Driving
- id: arXiv:2505.15298 | date: 2025-05 | venue: arXiv preprint (venue UNVERIFIED)
- authors: Qian, Kangan et al. | code: none seen
- relevance: MED — pre-window but essential to the tool-calling driving line; tool library, SFT then GRPO with tool-use rewards.
- what: Dynamic agent-style tool invocation within CoT for driving QA.
- thesis use: baseline for "VLM picks tool" prompting; likely also in agent A's file.
- verified: abs meta fetched.

### OmniDrive-R1: Reinforcement-driven Interleaved Multi-modal CoT for Trustworthy Vision-Language Autonomous Driving
- id: arXiv:2512.14044 | date: 2025-12 | venue: arXiv preprint
- authors: Zhang, Zhenguo et al. | code: none seen
- relevance: MED — RL-learned zoom-in on critical regions in an interleaved CoT, no dense localization labels.
- what: End-to-end joint perception-reasoning; aims at reducing object hallucination.
- thesis use: related work for learned ROI selection; competitor to a separate ROI tool.
- verified: abs meta fetched.

### ProActiveDrive: Future-Aware Adaptive Thinking for VLA Driving
- id: OpenReview Y6Pvaxv729 (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW — adaptive reasoning only when useful, plus cheap future prediction; Bench2Drive-220 driving score 86.08 to 88.20, success 67.27% to 71.30%.
- what: Built on a SimLingo-style policy; ablations show adaptive reasoning improves efficiency.
- thesis use: baseline family (adaptive think), closed-loop evidence for later phases.
- verified: OpenReview search record (abstract) read.

### VarioDrive: Adaptive and Diverse Reasoning for End-to-End Autonomous Driving
- id: OpenReview nxKu7c8r73 (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: MED — fast-slow inference: one plan for simple scenes, several preference-oriented plans (safety/efficiency/comfort) compared for complex scenes, then selects.
- what: Generates and compares multiple candidate plans only when the scene is complex.
- thesis use: related to candidate-set generation conditioned on difficulty; trajectory critic angle.
- verified: OpenReview search record (abstract, truncated) read.

### MindDrive: A Map-Informed Adaptive Decision Method for Efficient End-to-End Driving
- id: OpenReview EHiH6oQNZ8 (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW — model assesses scenario complexity and chooses direct action vs deliberative reasoning; RL contrasts decision modes within a scene; NAVSIM and nuScenes.
- what: Map retrieval gives decision-relevant priors; adaptive mode choice.
- thesis use: baseline family. (Name collides with other "MindDrive" submissions.)
- verified: OpenReview search record (abstract) read.

### Scene-Adaptive Readout and Decoding in Diffusion Driving VLAs
- id: OpenReview 3CHvYAsfDh (ICLR 2027 submission) | date: UNVERIFIED | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW — adaptive readout layer and decoding depth per scene; speedup up to 6.0x on Waymo E2E, validation RFS up to +0.56.
- what: Adaptive computation inside a diffusion driving VLA.
- thesis use: adaptive-computation background.
- verified: OpenReview search record read.

### FastDriveVLA, SToRM, MVPruner (token pruning for driving VLMs)
- id: arXiv:2507.23318 (FastDriveVLA, 2025-07, AAAI 2026), arXiv:2602.11656 (SToRM, 2026-02), arXiv:2606.27660 (MVPruner, 2026-06) | venue: as listed
- authors: Cao, Jiajun et al. / Kim, Seo Hyun et al. / Yang, Nan et al. | code: none seen
- relevance: LOW — attention/compute allocation over visual tokens and camera views; MVPruner reports 87.3% FLOPs reduction on DriveLM with 98.5% accuracy retained (search summary); SToRM keeps full-token performance with up to 30x less compute (search summary).
- what: Token importance prediction and per-view budget allocation; not tool selection.
- thesis use: related work on attention allocation; per-view budget is analogous to per-tool budget.
- verified: abs meta fetched for all three; numbers from search summary.

### Agent Prioritization for Autonomous Navigation
- id: arXiv:1909.08792 | date: 2019-09 | venue: arXiv preprint
- authors: Refaat, Khaled S. et al. | code: none
- relevance: MED (classic) — ranks agents by impact on the planner's decision so cheaper models can serve the rest; labels come from running the planner in simulation.
- what: Ranking dataset generated by logging what the planner reacted to.
- thesis use: classic precedent for planner-derived relevance labels under a compute budget.
- verified: abs meta fetched.

### Object Importance Estimation using Counterfactual Reasoning (HOIST)
- id: arXiv:2312.02467 | date: 2023-12 | venue: arXiv preprint
- authors: Gupta, Pranay et al. | code: none seen
- relevance: MED (classic) — importance by perturbing object motion and measuring change in ego behavior; human-labeled simulated traffic dataset.
- what: Counterfactual scenarios to score object importance.
- thesis use: idea to borrow for label construction (which hazard changes the chosen candidate).
- verified: abs meta fetched.

### Importance Filtering with Risk Models for Complex Driving Situations
- id: arXiv:2303.06935 | date: 2023-03 | venue: arXiv preprint
- authors: Puphal, Tim et al. | code: none
- relevance: LOW (classic) — filters agents that do not influence ego behavior using risk models, for planning efficiency.
- what: Overview and adaptation of risk models for filtering.
- thesis use: background.
- verified: abs meta fetched.

### Active Information Gathering for Long-Horizon Navigation by Learning the Value of Information
- id: arXiv:2403.03269 | date: 2024-03 | venue: IROS 2024 (per search result)
- authors: Arnob, Raihan Islam et al. | code: none seen
- relevance: MED (classic) — learned VoI of revealing unseen space, GNN trained on tractable training-time VoI; up to 63.76% and 36.68% cost improvements over non-learned and learned baselines.
- what: Learning over Subgoals; frontier-based exploratory actions.
- thesis use: precedent for training a selector on privileged-simulator VoI targets (same recipe as expected-gain labels).
- verified: abs meta fetched.

### Safe Occlusion-aware Autonomous Driving via Game-Theoretic Active Perception
- id: arXiv:2105.08169 | date: 2021-05 | venue: UNVERIFIED (not in abs meta)
- authors: Zhang, Zixu et al. (CORRECTED from abs meta) | code: none seen
- relevance: LOW (classic) — planning that adds a constraint on future field of view to actively reveal hidden road users in CARLA.
- what: Abstract: poses safe planning under occlusion as a hybrid zero-sum dynamic game between the AV (evader) and an initially hidden traffic participant (pursuer); gives worst-case safety guarantees while accounting for the vehicle's ability to avoid road users once detected; demonstrated in CARLA urban and highway scenarios.
- thesis use: classic active-perception-for-driving reference.
- verified: abs meta fetched (venue not in meta; left UNVERIFIED).

### Act, Think or Abstain: Complexity-Aware Adaptive Inference for VLA Models
- id: arXiv:2603.05147 | date: 2026-03 | venue: arXiv preprint
- authors: Izzo, Riccardo Andrea et al. | code: none seen
- relevance: MED — routes VLA execution into Act / Think / Abstain via embedding-based complexity estimators.
- what: Uses the backbone's latent embeddings as an active detection tool for state complexity.
- thesis use: three-way decision analog (act/reason/abstain); uses frozen backbone embeddings like the project's frozen-VLM features.
- verified: abs meta fetched.

### ElegantVLA, A1, Think Less Act Early (adaptive computation in VLAs)
- id: arXiv:2605.29438 (ElegantVLA, 2026-05), arXiv:2604.05672 (A1, 2026-04), arXiv:2606.15099 (AVA-VLA, 2026-06) | venue: arXiv preprints (2606.15099 also listed on an ICML 2026 poster page)
- authors: Li, Ye et al. / Zhang, Kaidong et al. / Lei, Dianqiao et al. | code: A1 states a full open-source release (abstract)
- relevance: LOW — manipulation VLAs; RL scheduler allocating compute per step (ElegantVLA), action-consistency early exit (A1), early-exit gate for latent reasoning (AVA-VLA).
- what: Adaptive compute allocation; the 98.3% at 145 ms vs 98.1% at 267 ms figure for AVA-VLA comes from a third-party summary, not checked.
- thesis use: background for adaptive computation.
- verified: abs meta fetched.

### VLA-Thinker / SCALE / UPS-type uncertainty-triggered looking in robotics
- id: arXiv:2603.14523 (VLA-Thinker, 2026-03), arXiv:2602.04208 (SCALE, 2026-02) | venue: arXiv preprints
- authors: Wang, Chaoyang et al. / Choi, Hyeonbeom et al. | code: none seen
- relevance: MED — VLA-Thinker makes perception a dynamically invocable reasoning action trained with GRPO on LIBERO and RoboTwin 2.0; SCALE modulates perception and action from self-uncertainty with one forward pass and no training.
- what: Both are scene/self-uncertainty-driven, not action-conditioned.
- thesis use: the SCALE-style trigger is another instance of the "trajectory-agnostic uncertainty" baseline.
- verified: abs meta fetched.

### VAP-TAMP: Robot Planning and Situation Handling with Active Perception
- id: arXiv:2604.26988 | date: 2026-04 | venue: arXiv preprint
- authors: Oloo, Austine et al. | code: none seen
- relevance: MED — uses action knowledge (the plan's actions) to prompt a VLM for active view selection and situation assessment inside a task-and-motion planner; this is plan-conditioned view selection, the nearest robotics analog to candidate-conditioned queries.
- what: Service tasks in simulation and on a mobile manipulator; no numbers in abstract.
- thesis use: closest plan-conditioned active-perception precedent outside driving.
- verified: abs meta fetched.

### The Perceptual Bandwidth Bottleneck in VLMs: Active Visual Reasoning via Sequential Experimental Design (FOVEA)
- id: arXiv:2605.01345 | date: 2026-05 | venue: arXiv preprint
- authors: Liu, Anjie et al. | code: none seen
- relevance: LOW — formalizes crop selection as sequential Bayesian optimal experimental design with a coverage-resolution proxy for information gain; training-free.
- what: High-resolution visual reasoning; not a decision/planning setting.
- thesis use: idea to borrow for a proxy information-gain objective for the ROI tool.
- verified: abs meta fetched.

### AdaTurn / WATCH / Starve to Perceive / ACTIVE-o3 / CropVLM (budgeted active perception for VLMs)
- id: OpenReview XMLvl4mopE (AdaTurn), OpenReview Xxb5y6mX7Y (WATCH), arXiv:2605.18603, arXiv:2505.21457, arXiv:2511.19820 | date: 2026 / 2026 / 2026-05 / 2025-05 / 2025-11 | venue: ICLR 2027 submissions for the first two, others arXiv (ACTIVE-o3 also on an ICML 2026 poster page)
- authors: Wu, Yuhuan et al. (Starve to Perceive); Zhu, Muzhi et al. (ACTIVE-o3); Carvalho, Miguel et al. (CropVLM) | code: WATCH has an anonymized repo
- relevance: LOW — all budget-conditioned or RL-trained zoom/crop acquisition for VQA; AdaTurn raises VisualProbe-Medium from 36.7% to 47.6% at four turns; WATCH frames acquisition as budgeted optimal stopping.
- what: Generic VLM active perception under turn or token budgets; none are driving planners.
- thesis use: budget-conditioning recipes; the optimal-stopping view for a multi-step version of the selector.
- verified: abs meta fetched for the three arXiv ones; OpenReview records read for the other two.

### Context-Aware Conformal Prediction for VLM-Based Driving Scene QA (CA-CP)
- id: ICML 2026 virtual page (icml.cc/virtual/2026/80373), OpenReview qCxRADChHQ; no arXiv id on the page | date: 2026 | venue: ICML 2026 workshop poster (Efficient Multimodal Question Answering, per WebFetch summary)
- authors: Joo, Yang-Jun; Kim, Younggun; Park, Sung-Yeon; Abdel-Aty, Mohamed (per WebFetch summary) | code: none seen
- relevance: LOW for this sub-area (calibration side) — uses planner uncertainty and temporal stability of planned trajectories as extra calibration signals; 16,655 WaymoQA pairs, six VLMs, improved worst-slab conditional coverage (per search summary).
- what: Planner features as conformal covariates.
- thesis use: for the conformal phase; candidate-spread as a conformal covariate is the same trick. Better covered by the calibration agent.
- verified: page fetched via WebFetch summary (title, authors, 16,655 WaymoQA pairs, six VLMs, planner uncertainty and trajectory temporal stability as features); abstract text not seen verbatim.

## Leads not followed

- Full-text reading of DEEP, MosaicDrive, ETM, DriveScout (only abstracts seen; OpenReview did not return author lists or dates). Check whether arXiv versions exist and whether DEEP releases code/benchmark.
- OpenAlex cited-by list for DriveAgent-R1 (OpenAlex did not index it under a direct DOI lookup); manual snowball via Google Scholar not done.
- Active perception in manipulation/navigation with VLAs beyond the few listed (e.g. CoMe-VLA 2602.04600, UPS "When to Act, Ask, or Learn" 2602.22474, Uncertainty-Informed Active Perception 2506.13367).
- Cost-aware tool routing for LLM agents (Calibrate-Then-Act 2602.16699, Inference-Time Budget Control 2605.05701, INTENT 2602.11541) — only abstracts seen for the first two; likely useful for the cost-model section.
- Older sensor gating (EcoFusion 2202.11330, HydraFusion 2201.06644, Adaptive LiDAR Scanning 2508.01562) and occlusion-aware planning with contingency (2502.06359) were seen only in search results.
- Planning-aware perception evaluation (Planner-centric metrics 2004.08745, Transcendental Idealism of Planner 2306.07276) not fetched.
- OpenReview ICLR 2027 queries not run: "occupancy/BEV query budget", "traffic light state tool", "conformal deferral driving".

## Deep-read addenda (full text via arxiv.org/html, 2026-11-06 late session)

Question asked of each: how is importance / value labeled, and does it condition on a set of candidate plans? Short answer for all five: none conditions on a candidate set. All score a single plan, a single predicted ego trajectory or a single action-knowledge step. Quotes are verbatim from the HTML text.

- **Agent Prioritization (arXiv:1909.08792, Refaat et al.)** — labels by running the planner. Quote: "We run the planner in simulation on real-world logged data, and log the causes of different planner decisions such as braking and nudging. These causes are then processed off-board to assign ground truth importance scores to agents." The expensive models run on all agents offline; the learned ranker (GBDT with pairwise loss over CNN + engineered features) runs online. Label = which agent caused a planner action, not a change in the plan's ranking. Not candidate-conditioned. Same "run the planner with privileged information to get labels" recipe as the project's oracle, but the label is attribution of an action, not the gain of a query.
- **HOIST (arXiv:2312.02467, Gupta et al.)** — counterfactual labels. Quote: "We modify the motion of objects in the scene and generate counterfactual scenarios. We gauge the change in the ego vehicle's driving under the counterfactual (estimated using an autonomous driving model) to estimate each object's importance." The Removal Score is the L2 distance between predicted ego waypoints with and without a vehicle; velocity perturbations (of other vehicles and of the ego) are scored by predicted collisions. Pedestrians use proximity instead. The dataset (HOIST) is human-annotated, simulated in CARLA. One predicted ego trajectory, not a candidate set. Closest label-construction analogue for a "does this hazard change the chosen action" target.
- **Arnob and Stein (arXiv:2403.03269)** — value of information as plan improvement, computed at training time with privileged knowledge. Quote: "allows us to compute the value of information for an exploratory action—the improvement to the robots plan if some part of the environment were revealed—at training time, that ... can estimate and use value of information at planning time". A GNN is trained on these targets and predicts expected VoI of each frontier action at deployment. This is the same recipe as the project's expected-gain targets (privileged labels, learned predictor), and its actions are the candidate exploratory moves, so it is the only one of the five where the choice set is a set of candidate actions; the VoI is per action, not per query given candidate plans. Venue (IROS 2024) is from a search result, not seen in the HTML.
- **Value of Information for human-agent communication (arXiv:2601.06407)** — decision rule: "At each turn, the agent evaluates the net utility gain for each candidate question ... The agent selects the question with the highest positive net value. If [it is not positive], the expected utility gain from further communication is not worth the cost. The agent terminates the dialogue and commits to the best action under its current belief." The LLM is prompted to output a belief distribution over latent factors and approximate the terms. Candidate questions yes, candidate plans no. Confirmed in the HTML: up to 1.36 utility points in high-cost settings, matching or exceeding the best tuned baselines in 18 of 20 cost conditions. ACL 2026 is only from a search listing. Good template for an abstain-by-net-value rule: query iff max over tools of (expected gain minus cost) is positive.
- **VAP-TAMP (arXiv:2604.26988)** — conditions on the current action's preconditions and effects, not on a candidate set. Quote: "VAP-TAMP actively prompts VLMs using the predicates of the current action's preconditions and effects in action knowledge ... At the motion level, VAP-TAMP prompts VLMs for active viewpoint selection towards maximizing information gain." Simulation in OmniGibson with injected failures at predefined probabilities (injection of situations resembles the project's hazard injection). Plan-conditioned but single-plan, and the VLM is prompted to choose, which the project found works poorly.

### Cost-aware tool routing and budget control (LLM agents, not driving)
All are text/LLM agents. Useful only for the cost model and for how to report Pareto curves.

### Beyond Tool-Call Count: Cost-Aware Tool-Use Routing for Black-Box LLM Agents
- id: NeurIPS 2026 virtual pages 170712 / 173045; no arXiv id found | date: 2026 | venue: NeurIPS 2026 (submission page, status UNVERIFIED)
- authors: not captured | code: none seen
- relevance: LOW — routing weighs predicted tool necessity against marginal tool cost with a user-set weight.
- what: Per search summary (not verbatim): 14.7% hypervolume gain on the accuracy-cost Pareto frontier over Probe & Prefill on the When2Tool benchmark; argues tool-call count is an incomplete cost proxy.
- thesis use: report hypervolume / area under the accuracy-cost curve, not just accuracy at one budget; tools in the project have different costs.
- verified: UNVERIFIED (search summary of the conference page only).

### Budget-Constrained Agentic LLMs: Intention-Based Planning for Costly Tool Use (INTENT)
- id: arXiv:2602.11541 | date: 2026-02 | venue: arXiv preprint
- authors: Liu, Hanbing et al. | code: none seen
- relevance: LOW — inference-time planner with a hierarchical world model enforcing a hard monetary budget; cost-augmented StableToolBench.
- what: Abstract: strictly enforces hard budget feasibility while improving task success; robust to tool price changes.
- thesis use: hard-budget formulation (at most one tool per step is a hard budget of 1).
- verified: abs meta fetched.

### Inference-Time Budget Control for LLM Search Agents
- id: arXiv:2605.05701 | date: 2026-05 | venue: arXiv preprint
- authors: Fang, Zhengru et al. | code: none seen
- relevance: LOW — controller assigns each feasible action a task-level VoI score, "an operational estimate of marginal task value per unit budget", under dual tool-call/token budgets; four multi-hop QA benchmarks, three backbones, four budget levels.
- what: Abstract: positive aggregate gains over four audited baselines; budget-dependent penalty gives the main gain.
- thesis use: budget-dependent penalty on the VoI score as a way to trace a Pareto curve from one selector.
- verified: abs meta fetched.

### Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents
- id: arXiv:2602.16699 | date: 2026-02 | venue: arXiv preprint
- authors: Ding, Wenxuan et al. | code: none seen
- relevance: LOW — passes the agent an inferred prior over latent environment state so it can trade exploration cost against uncertainty (QA, file reading, synthetic task).
- what: Abstract: explicit cost-benefit tradeoffs help agents find better strategies.
- thesis use: calibrated prior as input to the selector (cf. the project's calibration phase).
- verified: abs meta fetched.

### Budget-Aware Tool Use Enables Effective Agent Scaling (BATS)
- id: arXiv:2511.17006 | date: 2025-11 | venue: arXiv preprint
- authors: not captured in my fetch | code: github.com/google-research/budget-aware-agent (from abstract)
- relevance: LOW — finding that agents without "budget awareness" hit a ceiling when tool-call budgets grow; adds a Budget Tracker and a unified token+tool cost metric.
- what: Web search agents; cost-performance Pareto frontier.
- thesis use: unified cost metric idea.
- verified: abs meta fetched.

### Cited-by (OpenAlex, 2026-11-06)
- Agent Prioritization (OpenAlex W2973702581, 18 citations): newest citers are not VLM/tool work. Seen: "Priority Flicker in Risk-Based Pedestrian Prioritization" (2026-09, Future Transportation), "Importance is in your attention: agent importance prediction for autonomous driving" (CVPRW 2022), "Perceive, Attend, and Drive: Learning Spatial Attention for Safe Self-Driving" (ICRA 2021), "Dynamically Switching Human Prediction Models for Efficient Planning" (ICRA 2021), "CausalAgents: A Robustness Benchmark for Motion Forecasting" (ICRA 2024), "Risk Ranked Recall" (2021). Not fetched individually; the last-three-years ones worth a look for the planner-labeled-importance line are Dynamically Switching Human Prediction Models (switches model fidelity by need, a compute-allocation precedent) and Perceive, Attend, and Drive (spatial attention for planning).
- HOIST (OpenAlex W4391992291, 4 citations): "Global Interaction Modeling with Human Knowledge for Important Traffic Objects Identification" (2026-07), "See Something, Say Something: Layered Driver Situational Awareness from Language" (IV 2026), "Potential Fields as Scene Affordance for Behavior Change-Based Visual Risk Object Identification" (ICRA 2025), HumanSim (2025). None found that conditions on candidate plans. Titles only; no abstracts read.

## Update to Summary (end of session)

- Corrections: DualDriveVLA numbers (1.9x lower latency, not 3.2x throughput), Zhang & Fisac author (Zhang, Zixu), AdaThinkDrive CoT-usage percentages unverified. Applied above.
- None of the five deep-read papers (nor the cost-routing papers) conditions on a set of candidate plans. The plan-derived labels in Agent Prioritization, HOIST and Arnob & Stein are the lineage for the project's oracle and expected-gain targets, so the related work can say the label recipe is established while the candidate-set conditioning is the new part. Still to re-check against other agents' files.
- New candidate-selection neighbor: HybridDriveVLA (inside 2602.10719) selects from a compact cross-model candidate set with a learned trajectory scorer; relevant to agent C, not to tool selection.
- The net-value rule of 2601.06407 (query only if max over options of expected gain minus cost is positive) is a ready-made abstain rule and a way to get budget curves by sweeping the cost.
