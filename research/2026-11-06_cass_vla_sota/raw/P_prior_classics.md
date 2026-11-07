## Summary
- No pre-2025-07 paper I found selects a perception query conditioned on a set of candidate trajectories. The close ancestors each cover one part: plan-conditioned relevance (PKL, planning-aware metrics, HOIST counterfactual importance), occlusion plus active perception (Zhang and Fisac RSS 2021), and expected-gain acquisition (adaptive submodularity, nonmyopic VoI, Covert 2023, Janisch 2017). So the novelty claim holds for this period, subject to the sweep being limited to what I searched.
- Frames "which query changes the decision" most directly: (1) Philion PKL 2004.08745 and Ivanovic 2110.03270 (value of perception = effect on the plan); (2) Golovin and Krause 1003.3967 plus Krause and Guestrin 1207.1394 (greedy selection by expected value of observation, budgeted; our budget-1 selector with expected-gain targets is the one-step instance); (3) Covert 2301.00557 (learned greedy mutual-information acquisition, a ready baseline for the MLP selector); (4) Gupta HOIST 2312.02467 (counterfactual effect on ego as importance label); (5) Bajcsy 1603.02729 (active perception framing).
- Closest classical driving paper: Zhang et al. 2105.08169, where occluded hazards drive planning that accounts for later observations. It is model-based and does not choose among tools.
- Trajectory-agnostic attention is a separate line (BDD-A 1711.06406, DR(eye)VE 1705.03854): gaze says what a human looks at, not what changes the plan. Good foil for the "scene-uncertainty" baseline.
- Selective prediction and deferral (Geifman 1705.08500, SelectiveNet, Madras 1711.06664, Mozannar 2006.01862, KnowNo 2307.01928) justify the abstain action and risk-coverage plots. Conformal Risk Control 2208.02814 and Learn then Test 2110.01052 cover the future calibration phase.
- Adaptive computation (ACT, BranchyNet, Dynamic Zoom-in 1711.05187, Glance and Focus) uses confidence-triggered compute, the compute-side analogue of scene-uncertainty triggering. Dynamic Zoom-in is the closest: it predicts accuracy gain per region to pick where to zoom.
- Pre-DriveAgent-R1 tool use: Agent-Driver 2311.10813 (tool library by function calls), plus ReAct, Toolformer, V* and Sketchpad outside driving. None budgets or conditions on candidate plans.
- Citation counts are OpenAlex values on the arXiv record and undercount (they omit the published version). Venues marked UNVERIFIED are from my memory and were not on the abs page; check before writing the bib.

## Papers
### Learning to Evaluate Perception Models Using Planner-Centric Metrics
- id: arXiv:2004.08745 | date: 2020-04 | venue: arXiv preprint (published venue UNVERIFIED)
- authors: Philion et al. | code: none checked
- relevance: HIGH - defines perception quality by the effect of its output on the downstream driving plan (PKL), the root of our 'decision-relevant' notion.
- what: Proposes a metric for 3D detection that isolates detection and measures the impact the detections have on the downstream driving task, instead of treating all errors equally. The abstract says it penalizes mistakes that other metrics miss without being hand-designed to. Already cited in raw/B; the 2026 occluded-agent paper in papers.csv builds on it.
- thesis use: Cite as the origin of plan-conditioned relevance. Borrow: a KL-on-plan score as an alternative oracle gain label for each tool. Contrast: PKL scores a fixed perception output, we choose which query to make.
- verified: abs meta fetched; citations: 73 (OpenAlex, arXiv record)

### Safe Occlusion-aware Autonomous Driving via Game-Theoretic Active Perception
- id: arXiv:2105.08169 | date: 2021-05 | venue: RSS 2021 (OpenAlex)
- authors: Zhang et al. | code: none checked
- relevance: HIGH - occlusion hazard plus planning that accounts for what future observations will reveal, i.e. active perception inside the planner.
- what: Poses safe planning under occlusion as a hybrid zero-sum game between the ego and a hidden agent; the plan accounts for the ability to react once the agent is detected. Gives worst-case safety guarantees while limiting conservativeness; demonstrated on challenging occluded driving scenarios.
- thesis use: Closest classical driving paper on 'looking changes the decision under occlusion'. Cite as the model-based counterpart: they plan for information, we select a query for a learned ranker. Not query selection.
- verified: abs meta fetched; citations: 68 (OpenAlex, RSS record)

### Injecting Planning-Awareness into Prediction and Detection Evaluation
- id: arXiv:2110.03270 | date: 2021-10 | venue: IEEE IV 2022 (OpenAlex)
- authors: Ivanovic et al. | code: none checked
- relevance: MED - argues task-agnostic metrics rate outputs equal that lead to different planning outcomes; proposes task-aware metrics.
- what: Critically assesses accuracy-based metrics (IoU, displacement error) and proposes task-aware, planning-informed metrics for prediction and detection evaluation.
- thesis use: Cite with PKL as 'planner-centric evaluation'. Supports our choice to score selectors by decision accuracy rather than detection accuracy.
- verified: abs meta fetched; citations: 27 (OpenAlex, arXiv record)

### Object Importance Estimation using Counterfactual Reasoning for Intelligent Driving
- id: arXiv:2312.02467 | date: 2023-12 | venue: arXiv preprint (published venue UNVERIFIED)
- authors: Gupta et al. | code: none checked
- relevance: HIGH - object importance defined by how perturbing an object's motion changes the ego's driving, a counterfactual decision-relevance label.
- what: Introduces HOIST (human-annotated object importance in simulated traffic) and a counterfactual method that modifies object motion and ascribes importance by the effect on ego driving; beats baselines on HOIST.
- thesis use: Idea to borrow: counterfactual-effect labels for which hidden or visible actor matters, close to our oracle-gain labels. Already in papers.csv and raw/B.
- verified: abs meta fetched; citations: 4 (OpenAlex)

### Rank2Tell: A Multimodal Driving Dataset for Joint Importance Ranking and Reasoning
- id: arXiv:2309.06597 | date: 2023-09 | venue: arXiv preprint (published venue UNVERIFIED)
- authors: Sachdeva et al. | code: none checked
- relevance: MED - dataset of ranked object importance with reasons in complex traffic scenes.
- what: Multi-modal ego-centric dataset with dense annotations of semantic, spatial, temporal and relational attributes of important objects, with closed and open VQA.
- thesis use: Related work for object importance; possible human-label sanity check. Not about cost or queries.
- verified: abs meta fetched; citations: 65 (OpenAlex)

### Revisiting Active Perception
- id: arXiv:1603.02729 | date: 2016-03 | venue: Autonomous Robots 2017 (OpenAlex)
- authors: Bajcsy et al. | code: none
- relevance: HIGH - the canonical active-perception reference; perception chosen for the task, not for fidelity.
- what: Reviews the history of active perception ideas and argues the seminal contributions are as relevant today as decades ago given modern compute. Pair with Bajcsy's original 1988 Proc. IEEE paper (not fetched).
- thesis use: Cite for the framing 'perception acts as a function of the decision', the lineage behind our selector.
- verified: abs meta fetched; citations: 339 (OpenAlex, journal record)

### Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization
- id: arXiv:1003.3967 | date: 2010-03 | venue: arXiv preprint (JAIR, not checked)
- authors: Golovin & Krause | code: none
- relevance: HIGH - adaptive greedy selection of observations with guarantees; sequential 'which observation next' under a budget.
- what: Introduces adaptive submodularity; adaptive greedy is competitive with the optimal policy; examples include sensor placement and active learning.
- thesis use: Theory frame for a greedy expected-gain selector at budget 1 (our case is the single-step instance). Cite when justifying expected-gain targets.
- verified: abs meta fetched; citations: 508 (OpenAlex)

### Near-optimal Nonmyopic Value of Information in Graphical Models
- id: arXiv:1207.1394 | date: 2012-07 | venue: UAI 2005 (arXiv listing 2012; UNVERIFIED)
- authors: Krause & Guestrin | code: none
- relevance: HIGH - classic value-of-information subset selection with a (1-1/e) guarantee.
- what: Gives a randomized algorithm with a constant-factor guarantee for selecting an observation subset in a graphical model, with a hardness result and experiments on two real datasets.
- thesis use: Classic VoI citation for 'select the observation with the highest expected value'. Our MLP regresses exactly such a per-tool expected gain.
- verified: abs meta fetched; citations: 358 (OpenAlex)

### Near-Optimal Sensor Placements in Gaussian Processes: Theory, Efficient Algorithms and Empirical Studies
- id: doi:10.5555/1390681.1390689 | date: 2008 | venue: JMLR (OpenAlex)
- authors: Krause et al. | code: none
- relevance: MED - submodular sensor selection by mutual information.
- what: Not fetched beyond the OpenAlex record: JMLR 2008, first author Krause, 1421 citations. Abstract not read.
- thesis use: Standard citation for submodular sensor selection; keep to one sentence.
- verified: page fetched (OpenAlex record only; abstract UNVERIFIED); citations: 1421

### Learning to Maximize Mutual Information for Dynamic Feature Selection
- id: arXiv:2301.00557 | date: 2023-01 | venue: arXiv preprint (ICML 2023, UNVERIFIED)
- authors: Covert et al. | code: none checked
- relevance: HIGH - greedy conditional-mutual-information acquisition learned by amortization; the closest ML analogue of an expected-gain selector.
- what: Selects features greedily by conditional mutual information; since that needs oracle access to the data distribution, learns it by amortized optimization; recovers the greedy policy at optimality and beats several feature selection methods.
- thesis use: Method to borrow or baseline: an information-gain selector with an abstain/stop option. Strong prior for the learned MLP selector.
- verified: abs meta fetched; citations: 16 (OpenAlex)

### Classification with Costly Features using Deep Reinforcement Learning
- id: arXiv:1711.07364 | date: 2017-11 | venue: AAAI 2019 (OpenAlex)
- authors: Janisch et al. | code: none checked
- relevance: MED - each action requests a feature or terminates with a decision; accuracy vs feature cost.
- what: Formulates classification with costly features as sequential decision-making solved by deep Q-learning; comparable to specialized state-of-the-art on eight problems.
- thesis use: Classic cost-sensitive acquisition baseline family (sequential RL), versus our one-step supervised expected-gain target.
- verified: abs meta fetched; citations: 79 (OpenAlex, AAAI record)

### Opportunistic Learning: Budgeted Cost-Sensitive Learning from Data Streams
- id: arXiv:1901.00243 | date: 2019-01 | venue: arXiv preprint (ICLR 2019, UNVERIFIED)
- authors: Kachuee et al. | code: none checked
- relevance: MED - feature value = expected change in model uncertainty (MC dropout), RL under a budget.
- what: RL formulation with a reward from the utility of each feature; MC dropout measures expected variation of model uncertainty as the feature-value function; evaluated on three datasets including MNIST.
- thesis use: Shows an uncertainty-based value function, the analogue of our scene-uncertainty baseline in acquisition literature.
- verified: abs meta fetched; citations: 27 (OpenAlex)

### Active Feature Acquisition with Generative Surrogate Models
- id: arXiv:2010.02433 | date: 2020-10 | venue: arXiv preprint (ICML 2021, UNVERIFIED)
- authors: Li & Oliva | code: none checked
- relevance: MED - model-based active feature acquisition; information gain estimated by a generative surrogate.
- what: Reformulates the AFA MDP as generative modeling and learns a surrogate that captures feature dependencies to estimate information gain from acquisitions.
- thesis use: Related work for learned gain estimators in acquisition.
- verified: abs meta fetched; citations: 13 (OpenAlex)

### Adaptive Classification for Prediction Under a Budget
- id: arXiv:1705.10194 | date: 2017-05 | venue: arXiv preprint (NeurIPS 2017, UNVERIFIED)
- authors: Nan & Saligrama | code: none checked
- relevance: MED - learned gating between cheap and expensive models under a cost constraint; accuracy vs cost.
- what: Trains a gating and prediction model by empirical loss minimization with cost constraints; the cheap path approximates the complex model where it is accurate.
- thesis use: Budget-accuracy Pareto framing; gating analogue of our selector.
- verified: abs meta fetched; citations: 51 (OpenAlex)

### Selective Classification for Deep Neural Networks
- id: arXiv:1705.08500 | date: 2017-05 | venue: arXiv preprint (NeurIPS 2017, UNVERIFIED)
- authors: Geifman & El-Yaniv | code: none checked
- relevance: HIGH - foundational risk-coverage selective prediction for deep nets.
- what: Builds a selective classifier from a trained network that rejects instances to meet a user-set risk with high probability; 2% top-5 ImageNet error guaranteed at 99.9% with about 60% coverage.
- thesis use: Foundational citation for abstain and for risk-coverage curves; our Pareto is the cost analogue. Link to the conformal risk phase.
- verified: abs meta fetched; citations: 324 (OpenAlex)

### SelectiveNet: A Deep Neural Network with an Integrated Reject Option
- id: arXiv:1901.09192 | date: 2019-01 | venue: arXiv preprint (ICML 2019, UNVERIFIED)
- authors: Geifman & El-Yaniv | code: none checked
- relevance: MED - jointly trains prediction and rejection end-to-end.
- what: Optimizes classification and rejection together over the covered domain, with a better risk-coverage trade-off on several datasets.
- thesis use: Idea to borrow if the selector's abstain action is trained jointly with the ranker.
- verified: abs meta fetched; citations: 173 (OpenAlex)

### Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer
- id: arXiv:1711.06664 | date: 2017-11 | venue: arXiv preprint (NeurIPS 2018, UNVERIFIED)
- authors: Madras et al. | code: none checked
- relevance: MED - origin of 'learning to defer' as a model option to pass the decision downstream.
- what: Generalizes rejection learning to account for the downstream decision-maker; shows systems become more accurate and less biased.
- thesis use: Cite for the defer/abstain lineage behind the 'none' and replan/fallback actions.
- verified: abs meta fetched; citations: 106 (OpenAlex)

### Consistent Estimators for Learning to Defer to an Expert
- id: arXiv:2006.01862 | date: 2020-06 | venue: arXiv preprint (ICML 2020, UNVERIFIED)
- authors: Mozannar & Sontag | code: none checked
- relevance: MED - consistent surrogate loss for deferral, reduction to cost-sensitive learning.
- what: Learns a classifier and a rejector from samples of the expert's decisions, via a consistent surrogate for cost-sensitive learning.
- thesis use: Theory citation for treating the selector as a cost-sensitive classifier with a defer class.
- verified: abs meta fetched; citations: 68 (OpenAlex)

### Deep Gamblers: Learning to Abstain with Portfolio Theory
- id: arXiv:1907.00208 | date: 2019-06 | venue: arXiv preprint (NeurIPS 2019, UNVERIFIED)
- authors: Liu et al. | code: none checked
- relevance: LOW - (m+1)-class abstention loss from portfolio theory.
- what: Turns selective classification into an (m+1)-class problem with a loss based on the doubling rate of gambling.
- thesis use: Optional citation for an explicit abstain class.
- verified: abs meta fetched; citations: 40 (OpenAlex)

### Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners
- id: arXiv:2307.01928 | date: 2023-07 | venue: arXiv preprint (CoRL 2023, UNVERIFIED)
- authors: Ren et al. | code: none checked
- relevance: HIGH - conformal prediction decides when an LLM planner asks for help, minimizing help calls; the closest older 'when to ask' method.
- what: KnowNo gives statistical guarantees on task completion while minimizing human help, across simulated and real robot setups. Already in papers.csv, raw/D, raw/Y.
- thesis use: Baseline family for the calibration phase; contrast: asks whether to ask, not which query.
- verified: abs meta fetched; citations: 109 (OpenAlex)

### Conformal Risk Control
- id: arXiv:2208.02814 | date: 2022-08 | venue: arXiv preprint (ICLR 2024, UNVERIFIED)
- authors: Angelopoulos et al. | code: none checked
- relevance: MED - method for the planned conformal risk phase.
- what: Extends conformal prediction to control the expected value of monotone losses; extensions to distribution shift; examples in vision and NLP.
- thesis use: Future-phase tool; cite as the calibration method.
- verified: abs meta fetched; citations: 84 (OpenAlex)

### Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control
- id: arXiv:2110.01052 | date: 2021-10 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Angelopoulos et al. | code: none checked
- relevance: MED - risk control as multiple hypothesis testing; no refitting.
- what: Calibrates predictive algorithms to control risks such as IoU or FDR via hypothesis testing.
- thesis use: Alternative calibration route for the accept/inspect/fallback thresholds.
- verified: abs meta fetched; citations: 103 (OpenAlex)

### Introspective Planning: Aligning Robots' Uncertainty with Inherent Task Ambiguity
- id: arXiv:2402.06529 | date: 2024-02 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Liang et al. | code: none checked
- relevance: LOW - LLM planner uncertainty alignment, with conformal prediction for asking.
- what: Builds a knowledge base of introspective reasoning examples retrieved at deployment; evaluated on three tasks including a safe mobile manipulation benchmark.
- thesis use: Optional pair with KnowNo.
- verified: abs meta fetched; citations: 9 (OpenAlex)

### Predicting Driver Attention in Critical Situations
- id: arXiv:1711.06406 | date: 2017-11 | venue: arXiv preprint (ACCV 2018, UNVERIFIED)
- authors: Xia et al. | code: none checked
- relevance: MED - BDD-A human gaze data on braking events; attention as a proxy for what matters in a scene.
- what: Introduces an in-lab driver-attention protocol and the BDD-A dataset, plus human weighted sampling of crucial frames and an attention model.
- thesis use: Classic 'attention allocation for driving'. Contrasts with plan-conditioned relevance: gaze is trajectory-agnostic.
- verified: abs meta fetched; citations: 170 (OpenAlex)

### Predicting the Driver's Focus of Attention: the DR(eye)VE Project
- id: arXiv:1705.03854 | date: 2017-05 | venue: arXiv preprint (TPAMI, UNVERIFIED)
- authors: Palazzi et al. | code: none checked
- relevance: LOW - driver gaze dataset and model; attention patterns shared across drivers.
- what: Multi-branch network over video, motion and semantics; DR(eye)VE has more than 500,000 frames with eye-tracking.
- thesis use: Cite together with BDD-A as the trajectory-agnostic attention line.
- verified: abs meta fetched; citations: 315 (OpenAlex)

### Important Object Identification with Semi-Supervised Learning for Autonomous Driving
- id: doi:10.1109/icra46639.2022.9812234 | date: 2022 | venue: ICRA 2022 (OpenAlex)
- authors: Li et al. | code: none checked
- relevance: MED - identifies driving-relevant objects; important-object line.
- what: Only the OpenAlex record was read (title, venue, 20 citations). Abstract not read.
- thesis use: Related work for importance estimation.
- verified: page fetched (OpenAlex record only; abstract UNVERIFIED); citations: 20

### DROID: Driver-Centric Risk Object IDentification
- id: doi:10.1109/tpami.2023.3294305 | date: 2023 | venue: TPAMI (OpenAlex)
- authors: Li et al. | code: none checked
- relevance: LOW - risk object identification (which object makes the driver stop); extends an IROS 2020 paper.
- what: Only the OpenAlex record was read (14 citations). Abstract not read.
- thesis use: Optional.
- verified: page fetched (OpenAlex record only; abstract UNVERIFIED); citations: 14

### Scalable Decision Making with Sensor Occlusions for Autonomous Driving
- id: doi:10.1109/icra.2018.8460914 | date: 2018 | venue: ICRA 2018 (OpenAlex)
- authors: Bouton et al. | code: none checked
- relevance: MED - POMDP decision making under occlusion at intersections.
- what: Only the OpenAlex record was read (64 citations). Abstract not read.
- thesis use: POMDP/occlusion lineage; cite in one sentence.
- verified: page fetched (OpenAlex record only; abstract UNVERIFIED); citations: 64

### Towards Streaming Perception
- id: arXiv:2005.10420 | date: 2020-05 | venue: arXiv preprint (ECCV 2020, UNVERIFIED)
- authors: Li et al. | code: none checked
- relevance: MED - latency-accuracy Pareto for online perception.
- what: Introduces 'streaming accuracy', a single metric combining latency and accuracy evaluated at every time instant.
- thesis use: Pareto-curve precedent for evaluating perception budgets.
- verified: abs meta fetched; citations: 120 (OpenAlex)

### Anytime Stereo Image Depth Estimation on Mobile Devices
- id: arXiv:1810.11408 | date: 2018-10 | venue: arXiv preprint (ICRA 2019, UNVERIFIED)
- authors: Wang et al. | code: none checked
- relevance: LOW - anytime depth: query the model at any time for its current estimate.
- what: Staged disparity prediction that trades computation for accuracy at inference; 10-35 FPS at 1242x375 on an NVIDIA GPU.
- thesis use: Anytime-computation precedent for a depth tool.
- verified: abs meta fetched; citations: 222 (OpenAlex)

### Adaptive Computation Time for Recurrent Neural Networks
- id: arXiv:1603.08983 | date: 2016-03 | venue: arXiv preprint
- authors: Graves | code: none
- relevance: LOW - foundational adaptive computation (ponder time).
- what: Lets a recurrent net learn how many computation steps to take per input; strong gains on four synthetic problems.
- thesis use: Background for adaptive computation; one cite.
- verified: abs meta fetched; citations: 434 (OpenAlex)

### BranchyNet: Fast Inference via Early Exiting from Deep Neural Networks
- id: arXiv:1709.01686 | date: 2017-09 | venue: arXiv preprint (ICPR 2016, UNVERIFIED)
- authors: Teerapittayanon et al. | code: none checked
- relevance: LOW - early exit when confidence is high; confidence-triggered compute, the compute-side analogue of scene-uncertainty triggering.
- what: Adds side-branch classifiers so confident samples exit early.
- thesis use: Analogy for the uncertainty-trigger baseline.
- verified: abs meta fetched; citations: 79 (OpenAlex)

### Dynamic Zoom-in Network for Fast Object Detection in Large Images
- id: arXiv:1711.05187 | date: 2017-11 | venue: arXiv preprint (CVPR 2018, UNVERIFIED)
- authors: Gao et al. | code: none checked
- relevance: MED - RL selects which regions to inspect at higher resolution, based on predicted accuracy gain; a classic 'which crop to look at' with expected-gain prediction.
- what: R-net predicts the accuracy gain of analyzing a region at higher resolution and Q-net sequentially selects regions; on Caltech Pedestrians it cuts processed pixels by over 50% without a drop in detection accuracy.
- thesis use: Closest classic to our ROI tool selection; cite as expected-gain-driven region selection.
- verified: abs meta fetched; citations: 147 (OpenAlex)

### Glance and Focus: a Dynamic Approach to Reducing Spatial Redundancy in Image Classification
- id: arXiv:2010.05300 | date: 2020-10 | venue: arXiv preprint (NeurIPS 2020, UNVERIFIED)
- authors: Wang et al. | code: none checked
- relevance: LOW - RL-selected small inputs, terminate when confident.
- what: Processes a sequence of small patches chosen by RL and can stop early once confident.
- thesis use: Optional.
- verified: abs meta fetched; citations: 126 (OpenAlex)

### Dynamic Neural Networks: A Survey
- id: arXiv:2102.04906 | date: 2021-02 | venue: arXiv preprint (TPAMI, UNVERIFIED)
- authors: Han et al. | code: none
- relevance: LOW - survey of instance-, spatial- and temporal-wise adaptive computation.
- what: Reviews dynamic networks in three categories.
- thesis use: Single survey cite for adaptive computation.
- verified: abs meta fetched; citations: 867 (OpenAlex)

### Selective Sensor Fusion for Neural Visual-Inertial Odometry
- id: arXiv:1903.01534 | date: 2019-03 | venue: arXiv preprint (CVPR 2019, UNVERIFIED)
- authors: Chen et al. | code: none checked
- relevance: LOW - learned selection among sensor modalities via soft/hard masking.
- what: Two fusion modes (deterministic soft, stochastic hard) let the network use the available modalities; evaluated on three public datasets.
- thesis use: Precedent for learned sensor gating.
- verified: abs meta fetched; citations: 178 (OpenAlex)

### Planning-oriented Autonomous Driving
- id: arXiv:2212.10156 | date: 2022-12 | venue: arXiv preprint (CVPR 2023, UNVERIFIED)
- authors: Hu et al. | code: none checked
- relevance: MED - prioritizes perception and prediction tasks by contribution to planning (UniAD).
- what: Unified framework where all tasks serve planning.
- thesis use: Cite as planning-aware perception in end-to-end driving.
- verified: abs meta fetched; citations: 991 (OpenAlex)

### A Language Agent for Autonomous Driving (Agent-Driver)
- id: arXiv:2311.10813 | date: 2023-11 | venue: arXiv preprint (COLM 2024, UNVERIFIED)
- authors: Mao et al. | code: none checked
- relevance: HIGH - earliest LLM driving agent with a tool library via function calls, before DriveAgent-R1.
- what: Replaces the pipeline with an LLM that uses a tool library, a memory and a reasoning engine with chain-of-thought and self-reflection. The model calls tools for perception and prediction results; it does not decide a per-step budget.
- thesis use: Pre-DriveAgent-R1 tool-use citation. Contrast: tool calls are fixed, not selected under budget.
- verified: abs meta fetched; citations: 66 (OpenAlex)

### DriveLM: Driving with Graph Visual Question Answering
- id: arXiv:2312.14150 | date: 2023-12 | venue: arXiv preprint (ECCV 2024, UNVERIFIED)
- authors: Sima et al. | code: none checked
- relevance: LOW - graph VQA through perception, prediction and planning.
- what: DriveLM-Data on nuScenes and CARLA; DriveLM-Agent baseline for Graph VQA and end-to-end driving.
- thesis use: Background for VLM driving with staged reasoning.
- verified: abs meta fetched; citations: 282 (OpenAlex)

### GPT-Driver: Learning to Drive with GPT
- id: arXiv:2310.01415 | date: 2023-10 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Mao et al. | code: none checked
- relevance: LOW - motion planning as language modeling.
- what: Represents planner inputs and outputs as language tokens.
- thesis use: Background only.
- verified: abs meta fetched; citations: 151 (OpenAlex)

### DriveVLM: The Convergence of Autonomous Driving and Large Vision-Language Models
- id: arXiv:2402.12289 | date: 2024-02 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Tian et al. | code: none checked
- relevance: LOW - VLM scene analysis plus planning, with a dual system.
- what: DriveVLM-Dual combines the VLM with a traditional pipeline; evaluated on nuScenes and SUP-AD.
- thesis use: Background.
- verified: abs meta fetched; citations: 114 (OpenAlex)

### LMDrive: Closed-Loop End-to-End Driving with Large Language Models
- id: arXiv:2312.07488 | date: 2023-12 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Shao et al. | code: none checked
- relevance: LOW - closed-loop LLM driving.
- what: Language-guided end-to-end driving from multi-modal sensors and instructions.
- thesis use: Background.
- verified: abs meta fetched; citations: 186 (OpenAlex)

### ReAct: Synergizing Reasoning and Acting in Language Models
- id: arXiv:2210.03629 | date: 2022-10 | venue: arXiv preprint (ICLR 2023, UNVERIFIED)
- authors: Yao et al. | code: none checked
- relevance: MED - interleaves reasoning and actions that query external sources.
- what: Reasoning traces and task actions generated in an interleaved fashion to gather information.
- thesis use: Root of the think/act pattern DriveAgent-R1 uses.
- verified: abs meta fetched; citations: 2183 (OpenAlex)

### Toolformer: Language Models Can Teach Themselves to Use Tools
- id: arXiv:2302.04761 | date: 2023-02 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Schick et al. | code: none checked
- relevance: MED - a model trained to decide which API to call and when.
- what: Self-supervised training on API call decisions with a calculator, QA, search, translation and calendar tools.
- thesis use: Cite as the learned 'which tool and when' precedent in LMs.
- verified: abs meta fetched; citations: 1704 (OpenAlex)

### V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs
- id: arXiv:2312.14135 | date: 2023-12 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Wu & Xie | code: none checked
- relevance: MED - LLM-guided visual search for small details in high-resolution images; the visual-query analogue of ROI inspection.
- what: SEAL uses an LLM-guided search to find and focus on target visual elements; V*Bench tests high-resolution detail handling.
- thesis use: Idea to borrow for the ROI tool: zoom on a target. Not driving.
- verified: abs meta fetched; citations: 107 (OpenAlex)

### Visual Sketchpad: Sketching as a Visual Chain of Thought for Multimodal Language Models
- id: arXiv:2406.09403 | date: 2024-06 | venue: arXiv preprint (UNVERIFIED venue)
- authors: Hu et al. | code: none checked
- relevance: LOW - multimodal LM with drawing tools and specialist vision models.
- what: Gives a multimodal LM a visual sketchpad and tools; can call specialist vision models.
- thesis use: Background for tool-using VLMs.
- verified: abs meta fetched; citations: 49 (OpenAlex)

### MLLMs Know Where to Look: Training-free Perception of Small Visual Details with Multimodal LLMs
- id: arXiv:2502.17422 | date: 2025-02 | venue: arXiv preprint (ICLR 2025, UNVERIFIED)
- authors: Zhang et al. | code: none checked
- relevance: MED - VLM attention already points to the right region even when the answer is wrong, enabling training-free crops.
- what: Shows accuracy is causally sensitive to subject size and proposes training-free attention-based cropping interventions.
- thesis use: Idea to borrow: VLM attention as a cheap feature to decide whether a crop will help.
- verified: abs meta fetched; citations: 13 (OpenAlex)

## Leads not followed
- Bajcsy 1988 "Active perception" (Proc. IEEE) and Howard 1966 "Information value theory": OpenAlex search did not return them; classic non-arXiv citations to add by hand.
- Chow 1970 and Cortes et al. "Learning with rejection": no arXiv record; not looked up.
- Active classification based on value of classifier (Gao and Koller, NIPS 2011): OpenAlex record exists (65 cites), abstract not read.
- Shim et al. NeurIPS 2018 joint active feature acquisition: OpenAlex record only (42 cites).
- Krause et al. 2007 "Near-optimal observation selection using submodular functions" (303 cites) and Jayaraman and Grauman "Learning to look around" (CVPR 2018): OpenAlex record only.
- Occlusion-aware POMDP planners (Brechtel and others), perception-aware planning for quadrotors, and Deng et al. 2112.07787 (egocentric detection metric, 9 cites): found titles, not read.
- Embodied Question Answering 1711.11543 (fetched, LOW relevance, not written up).
