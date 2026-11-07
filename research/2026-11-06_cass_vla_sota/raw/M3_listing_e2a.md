# M3_listing_e2a: listing sweep, slice e2_00

## Summary
- No close overlap found. Nothing in this slice does candidate-conditioned perception-query selection for driving, nor a driving VLM that calls tools. The slice (426 titles) is dominated by generic conformal prediction, LLM/MCP tool-calling, and zoom-in VLM papers.
- Nearest on 'which/when to query under a budget': Combining Cost-Constrained Runtime Monitors (2507.15886, when and which monitors, Pareto vs. cost), H-PRAP (2507.11920, risk-routed prediction effort in planning), CRSAIL (2512.00453, conformal threshold tied to query rate).
- Only driving-adjacent selectors: Learning Contextual Runtime Monitors (2601.20666, bandit chooses a controller by context, simulated driving) and LiDAS (dropped, active illumination, no decision-relevance).
- Active feature acquisition (2508.01957, 2508.18380, 2510.12624) and information pursuit (2507.03279) give the VOI vocabulary; all are tabular or language, none condition on candidate plans.
- For the calibration phase: LEC (2512.01556), Conformal Thinking (2602.03814), conformal alignment cascades (2510.17543), Learnable CP (2509.21955).
- 'When to look' VLM papers (2511.15613, 2512.17227, 2509.25699) trigger on language or model uncertainty, i.e. the trajectory-agnostic style the project compares against.
- Second, more generous pass over VOI / active acquisition / when-to-query titles previously marked LOW added the active feature acquisition, CPATTA, AIM-CoT and 2512.01188 entries; the robotic-manipulation active-perception ones stayed dropped. All 59 shortlisted abstracts were fetched.

## Papers

### Combining Cost-Constrained Runtime Monitors for AI Safety
- id: arXiv:2507.15886 | date: 2025-07 | venue: arXiv preprint
- authors: Hua, Tim Tian et al. | code: none
- relevance: MED — decides when and which monitor to call under an average-case budget; Pareto framing matches the query-budget curve, but domain is LLM code review, not driving.
- what: Searches exhaustively over when and which monitors to call, and allocates safety interventions by the Neyman-Pearson lemma using likelihood ratios. Under an average budget it more than doubles recall over a naive baseline in a code-review setting, and combining two monitors can Pareto dominate either alone.
- thesis use: Idea to borrow: cost-aware 'which monitor/tool, and when' formulation and likelihood-ratio allocation; cite as non-driving analogue of budgeted tool selection.
- verified: abs meta fetched

### Heterogeneous Predictor-based Risk-Aware Planning with Conformal Prediction in Dense, Uncertain Environments
- id: arXiv:2507.11920 | date: 2025-07 | venue: arXiv preprint
- authors: Yang, Jeongyong et al. | code: none
- relevance: MED — allocates prediction effort to high-risk obstacles under a compute budget and feeds conformal radii into a chance-constrained MPC; selection is per-obstacle, not per-candidate-trajectory.
- what: Introduces P-CRI, a horizon-level collision index calibrated with conformal prediction; a router sends high-risk obstacles to expensive predictors and low-risk ones to light predictors. Analyzes the safety-efficiency trade-off under a prediction compute budget in numerical simulations of dense environments.
- thesis use: Idea to borrow / related work: risk-routed spending of a limited compute budget with a collision-risk score; contrast with candidate-conditioned scoring.
- verified: abs meta fetched

### Sample-Efficient Expert Query Control in Active Imitation Learning via Conformal Prediction
- id: arXiv:2512.00453 | date: 2025-11 | venue: arXiv preprint
- authors: Firouzkouhi, Arad et al. | code: none
- relevance: MED — a calibrated rule for when to query an expert, with alpha tied to the expected query rate; matches the 'when to query' and calibration themes, but state-novelty based (trajectory-agnostic).
- what: CRSAIL queries the expert only when the visited state is under-represented in the expert dataset; novelty is the distance to the K-th nearest expert state and a global threshold is set by a conformal quantile. On MuJoCo tasks it matches or exceeds expert-level reward while cutting expert queries by up to 96% vs. DAgger and up to 65% vs. prior active IL methods.
- thesis use: Idea to borrow: conformal threshold giving direct control of query rate for the future calibration phase; example of a scene-uncertainty-style trigger baseline.
- verified: abs meta fetched

### Learning Contextual Runtime Monitors for Safe AI-Based Autonomy
- id: arXiv:2601.20666 | date: 2026-01 | venue: arXiv preprint
- authors: Luque-Cerpa, Alejandro et al. | code: none
- relevance: MED — a context-conditioned monitor that selects among controllers, learned with contextual bandits, with safety guarantees, validated in two simulated driving scenarios.
- what: Reformulates safe control ensembles as contextual monitoring: a monitor observes the context and selects the controller best suited to it, using contextual multi-armed bandit techniques. Reports significant safety and performance gains over non-contextual baselines in two simulated driving scenarios.
- thesis use: Related work for learned selectors in driving; bandit framing is an alternative to the MLP selector on expected-gain targets.
- verified: abs meta fetched

### LEC: Linear Expectation Constraints for Selection-Conditioned Risk Control in Selective Prediction and Routing Systems
- id: arXiv:2512.01556 | date: 2025-12 | venue: arXiv preprint
- authors: Wang, Zhiyuan et al. | code: none
- relevance: MED — finite-sample selection-conditioned error control for accept/defer decisions, extended to routing to a second model; relevant to the calibrated accept/reject phase.
- what: Controls the ratio of expected accepted errors to expected accepted predictions, giving a risk-constrained, retention-maximizing threshold from a held-out calibration set. Extends to two-model routing where the input is delegated if primary uncertainty exceeds its threshold; evaluated on QA and VQA.
- thesis use: Idea to borrow: accept-threshold calibration with error guarantee conditioned on acceptance, for the accept/inspect/replan/fallback policy.
- verified: abs meta fetched

### Conformal Thinking: Risk Control for Reasoning on a Compute Budget
- id: arXiv:2602.03814 | date: 2026-02 | venue: arXiv preprint
- authors: Wang, Xi et al. | code: none
- relevance: MED — turns budget setting into distribution-free risk control with an upper stop threshold and a lower threshold; a template for choosing the query-budget operating point.
- what: Reframes the token-budget problem as limiting error rate while minimizing compute, with an upper threshold (stop when confident) and a parametric lower threshold (stop unsolvable instances), set by distribution-free risk control from a validation set. Shows compute efficiency gains while meeting the user target risk across reasoning tasks.
- thesis use: Idea to borrow: choose the budget/threshold on the Pareto curve by risk control rather than by hand (future phase).
- verified: abs meta fetched

### Conformal Information Pursuit for Interactively Guiding Large Language Models
- id: arXiv:2507.03279 | date: 2025-07 | venue: arXiv preprint
- authors: Chan, Kwan Ho Ryan et al. | code: none
- relevance: MED — sequential choice of the next query by information gain, with conformal set size replacing entropy; query-selection analogue in language.
- what: Information Pursuit greedily picks the query maximizing information gain; C-IP estimates uncertainty from the average size of conformal prediction sets instead of unreliable LLM conditional entropy. On 20 Questions it gets better predictive performance and shorter query-answer chains than earlier IP and uncertainty-based chain-of-thought methods; also tested on MediQ.
- thesis use: Idea to borrow: conformal-set-size as a value-of-information proxy when model probabilities are miscalibrated.
- verified: abs meta fetched

### Stochastic Encodings for Active Feature Acquisition
- id: arXiv:2508.01957 | date: 2025-08 | venue: arXiv preprint
- authors: Norcliffe, Alexander et al. | code: none
- relevance: MED — instance-wise choice of which feature to measure; non-myopic, supervised latent-variable method that avoids RL.
- what: Addresses active feature acquisition with a latent variable model trained in a supervised manner; acquisitions reason over many possible unobserved realizations. Reports reliable gains over a diverse set of baselines on synthetic and real datasets.
- thesis use: Related work for 'which sensor/tool to query'; points out greedy mutual information is myopic, relevant to expected-gain targets.
- verified: abs meta fetched

### Information Templates: A New Paradigm for Intelligent Active Feature Acquisition
- id: arXiv:2508.18380 | date: 2025-08 | venue: arXiv preprint
- authors: Huang, Hung-Tien et al. | code: none
- relevance: MED — cost-aware non-greedy acquisition with a small library of jointly informative feature sets; shrinks the action space.
- what: TAFA learns feature templates and uses them to guide next acquisitions, reducing the action space and avoiding estimating the data distribution. It outperforms state-of-the-art baselines with lower acquisition cost and computation on synthetic and real data.
- thesis use: Related work: cost-aware acquisition baselines.
- verified: abs meta fetched

### Learning-To-Measure: In-Context Active Feature Acquisition
- id: arXiv:2510.12624 | date: 2025-10 | venue: arXiv preprint
- authors: Kobayashi, Yuta et al. | code: none
- relevance: MED — acquisition policy via uncertainty-guided greedy conditional mutual information, with in-context generalization across tasks.
- what: Formalizes meta-AFA and proposes L2M: autoregressive pre-training for uncertainty quantification under arbitrary missingness plus a greedy CMI acquisition agent, operating in-context without per-task retraining. Matches or surpasses task-specific baselines on tabular benchmarks, especially with scarce labels and high missingness.
- thesis use: Related work only; tabular domain.
- verified: abs meta fetched

### Reliable Inference in Edge-Cloud Model Cascades via Conformal Alignment
- id: arXiv:2510.17543 | date: 2025-10 | venue: arXiv preprint
- authors: Huang, Jiayi et al. | code: none
- relevance: MED — calibrated escalation from a cheap to an expensive model with a tunable coverage/deferral-rate trade-off.
- what: Casts escalation from edge to cloud as multiple hypothesis testing, using conformal alignment to select inputs that can safely be handled at the edge, with guarantees on the fraction of edge decisions meeting cloud-level conditional coverage. Exposes a trade-off among coverage, deferral rate and set size.
- thesis use: Idea to borrow: calibrated 'call the expensive tool or not' guarantee.
- verified: abs meta fetched

### Learnable Conformal Prediction with Context-Aware Nonconformity Functions for Robotic Planning and Perception
- id: arXiv:2509.21955 | date: 2025-09 | venue: arXiv preprint
- authors: Kumar, Divake et al. | code: none
- relevance: MED — context-aware conformal sets for detection (BDD100K, Cityscapes) and path planning; relevant to calibrating planner accept/reject.
- what: LCP replaces fixed nonconformity scores with a lightweight neural function using geometric, semantic and task features. Reduces classification set sizes by 18%, gives 46-54% tighter boxes on COCO, BDD100K and Cityscapes, and raises path-planning success from 72% to 91.5% with 4.5% path inflation vs. 12.2% for standard CP.
- thesis use: Idea to borrow: learned nonconformity scores using geometric features, for the calibration phase.
- verified: abs meta fetched

### CPATTA: Conformal Supervision Allocation For Active Test-Time Adaptation
- id: arXiv:2509.25692 | date: 2025-09 | venue: arXiv preprint
- authors: Shi, Tingyu et al. | code: none
- relevance: MED — allocates a limited annotation-query budget using conformal scores; shows that conformal selection beats heuristic uncertainty triggering.
- what: Brings conformal uncertainty with coverage-aware online calibration into active test-time adaptation, with a domain-shift detector and staged updates. Outperforms state-of-the-art ATTA methods by around 5% accuracy.
- thesis use: Supporting evidence that principled scores beat heuristic scene-uncertainty at equal query budget (different domain).
- verified: abs meta fetched

### Real-World Reinforcement Learning of Active Perception Behaviors
- id: arXiv:2512.01188 | date: 2025-12 | venue: arXiv preprint
- authors: Hu, Edward S. et al. | code: none
- relevance: MED — trains active perception policies using privileged sensors only at training time, analogous to oracle labels from privileged simulator state.
- what: AAWR (asymmetric advantage weighted regression) uses privileged extra sensors during training to learn high-quality value functions that estimate the advantage of the target policy, bootstrapping from few suboptimal demonstrations and a coarse policy.
- thesis use: Idea to borrow: privileged-information value targets for learning the selector.
- verified: abs meta fetched

### When to Think and When to Look: Uncertainty-Guided Lookback
- id: arXiv:2511.15613 | date: 2025-11 | venue: arXiv preprint
- authors: Bi, Jing et al. | code: none
- relevance: MED — uncertainty-triggered look-back to the image in VLM reasoning; an uncertainty-triggered 'look' baseline in the style of scene-uncertainty triggering.
- what: Evaluates ten InternVL3.5 and Qwen3-VL variants on MMMU-val, shows more thinking is not always better, and proposes a training-free decoding strategy combining an uncertainty signal with adaptive lookback prompts and breadth search, improving MMMU under fixed token budgets.
- thesis use: Baseline-style trigger; not driving.
- verified: abs meta fetched

### Learning When to Look: A Disentangled Curriculum for Strategic Perception in Multimodal Reasoning
- id: arXiv:2512.17227 | date: 2025-12 | venue: arXiv preprint
- authors: Yang, Siqi et al. | code: none
- relevance: MED — RL policy for when to perceive, with a reward coupling perceptual actions to uncertainty markers.
- what: Separates 'how-to-think' from 'when-to-look' with a text-only SFT curriculum then Perception-Grounded CoT, and trains timing by RL with a Pivotal Perception Reward linking looks to markers of cognitive uncertainty.
- thesis use: Related work for 'when to look' policies; trigger is language-uncertainty, not candidate-conditioned.
- verified: abs meta fetched

### AIM-CoT: Active Information-driven Multimodal Chain-of-Thought for Vision-Language Reasoning
- id: arXiv:2509.25699 | date: 2025-09 | venue: arXiv preprint
- authors: Li, Xiping et al. | code: none
- relevance: MED — addresses 'what to see' (evidence selection) and 'when to see' (triggering) with information-driven rather than attention-based signals.
- what: Argues interleaved-modal CoT depends on selecting visual evidence and on when to insert it, and that attention signals and existing triggers fall short; proposes an active information-driven framework (abstract truncated before results).
- thesis use: Related work for evidence selection and triggering in VLMs.
- verified: abs meta fetched

### Who Moved My Distribution? Conformal Prediction for Interactive Multi-Agent Systems
- id: arXiv:2511.11567 | date: 2025-11 | venue: arXiv preprint
- authors: Binny, Allen Emmanuel et al. | code: none
- relevance: MED — conformal prediction regions for other agents' trajectories used by the ego controller; names the endogenous distribution shift that closed-loop evaluation would face.
- what: Iterative conformal framework adapting an uncertainty-aware ego controller to the endogenous shift caused by reactive agents, with convergence conditions; in 2- and 3-agent simulations it improves success rates by up to 9.6% over CP baselines.
- thesis use: Caveat for moving from open-loop to closed-loop calibration.
- verified: abs meta fetched

### No Need for Learning to Defer? A Training Free Deferral Framework to Multiple Experts through Conformal Prediction
- id: arXiv:2509.12573 | date: 2025-09 | venue: arXiv preprint
- authors: Bary, Tim et al. | code: none
- relevance: MED (borderline) — training-free choice among experts via conformal sets; a tool-selection-by-set analogue.
- what: Uses conformal prediction sets to quantify label-specific uncertainty and selects the expert with a segregativity criterion; on CIFAR10-H and HAM10000 it reduces training labels needed (abstract truncated).
- thesis use: Related work for deferral without training.
- verified: abs meta fetched

### Safe Planning in Unknown Environments Using Conformalized Semantic Maps
- id: arXiv:2509.25124 | date: 2025-09 | venue: arXiv preprint
- authors: Sundarsingh, David Smith et al. | code: none
- relevance: MED (borderline) — conformal uncertainty on perception feeding a planner with a user-specified mission completion rate.
- what: Quantifies uncertainty in on-the-fly semantic maps with conformal prediction, model- and distribution-free, and plans paths achieving user-specified completion rates without sensor-model knowledge.
- thesis use: Related work for conformal perception-to-planner guarantees.
- verified: abs meta fetched

## Shortlisted but dropped
- 2508.12916 RoboRetriever: manipulation active perception with scene graph; no query-budget or decision link.
- 2509.14787 COMPASS: confined-space manipulation viewpoint planning.
- 2511.04199 GraspView: grasping best-view; manipulation.
- 2601.13639 One-shot optimal viewpoint prediction for manipulation.
- 2511.14037 BIM-discrepancy active sensing UAV-UGV: re-scan when corridor risk exceeds a threshold, but construction-site mapping/occupancy.
- 2602.01266 RL for active perception in aerial navigation: camera control with a voxel information reward, depth-based, no candidate plans or budget.
- 2512.08912 LiDAS: active headlight illumination for nighttime perception (+18.7% mAP50 at equal power); sensing hardware, not tool selection.
- 2509.04243 LASER: GUI grounding zoom; not driving.
- 2512.23646 OmniAgent: audio-video tool orchestration; not driving.
- 2512.08952 Learning When to Ask (humanoid mental-health interviews): unrelated domain.
- 2509.05663 DQS: label query strategy for time-series anomaly detection.
- 2511.05610 CP-driven adaptive sampling for water twins: conformal sensing allocation, but water networks; idea only (33-34% lower error than uniform sampling).
- 2511.05889 Language-conditioned safety filtering for navigation: not about queries.
- 2507.13835 Conformal data contamination tests: data buying.
- 2511.02969 Value of Information in Bootstrapped DQN: RL exploration.
- 2602.13215 AMOR: entropy-gated attention in language models; architecture.
- 2508.16636 Cognitive Decision Routing: LLM reasoning-depth routing, no calibration.
- 2510.19351 Learning to defer to a population: human-expert deferral, data scarcity.
- 2602.13554 Observability engineering: theory of active sensing, no experiments relevant.
- 2601.18442 SG-CADVLM: safety-critical scenario generation from crash reports; scenario generation, not a hazard/occlusion benchmark.
- 2508.05634 Crowd navigation with conformal uncertainty: RL with CP observations; not a selector.
- 2509.11520 SPEED early-exit selective prediction: DNN depth.
- 2509.12132 Reflection-V: VLM visual reflection training.
- 2601.11633 ViEBench: thinking-with-images evaluation, not driving.
- 2512.09907 VisualActBench: VLM action reasoning benchmark, not driving hazards.
- 2511.05982 Survey of runtime safety monitoring for perception DNNs: background reading only.
- 2509.19419 Probabilistic runtime verification of visual DL: OOD-based risk assessment, generic.
- 2509.14758 Latent safety filters with pre-trained vision models: control, manipulation.
- 2601.22570 Memory-augmented selective prediction for VLMs: reject option, no cost or budget.
- 2602.01334 Vision tool-use RL (crop-and-zoom) MED analysis: finds gains dominated by intrinsic learning, tool-use RL mainly reduces tool-induced harm; useful caution but not driving or budgeted, kept as footnote only.
- 2602.02873 ViThinker: query tokens for internal expert features, no external tool calls; not driving.
- 2509.01338 Conformal predictive monitoring multi-modal: temporal-logic monitoring.
- 2602.04821 STREAM-RL: urban traffic management, not vehicle planning.
- 2510.18485 COPPOL: conformal segmentation for RL on satellite hazard maps, not driving.
- 2510.07750 Inverse conformal risk control: robust optimization, generic.
- 2510.08748 Conformal Risk Training: OCE risk, generic.
- 2512.12844 Selective Conformal Risk Control: generic set-size reduction, redundant with LEC.

## Leads not followed
- Titles in this slice without driving/tool keywords were not examined beyond their titles; no full-text reads were done (abstract meta only).
