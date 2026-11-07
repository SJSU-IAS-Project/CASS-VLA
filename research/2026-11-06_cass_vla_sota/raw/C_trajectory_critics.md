# C_trajectory_critics: scoring, selecting and verifying among candidate trajectories

Scanned 2026-11-06. Verification level is per entry. "abs meta fetched" means verbatim arXiv metadata and abstract via absfetch.py. Numbers are only those seen in the abstract or the html text.

## Summary
- **No close overlap found.** I found no paper in this sub-area that picks a perception query/tool conditioned on the candidate-trajectory set. Everything below either scores candidates (the "ranker" half of PlanDiscrim), or verifies/filters one proposal. The "selector" half (which query separates the candidates, under a budget) looks open. The searches that targeted this ("value of information", "planner-conditioned sensing", "which information disambiguates candidates") returned only classical active-perception and patent hits. This is a negative result from web search, not an exhaustive proof.
- **Closest conceptual neighbours** to the selector idea: (a) DiVeR (2610.04933, robotics) estimates "decision criticality" from the dispersion of sampled action candidates and reweights verifier learning toward states where candidates differ meaningfully. This is the same intuition as "how the candidates diverge", used for training weights, not for tool choice. (b) DriveReferee (2609.22762) runs an analytic collision/drivable-area check on a camera-predicted scene state; it is the nearest thing to the project's "geometric collision check" tool, and its finding that learned verdicts give no gain over the explicit rule supports using that tool as a deterministic oracle-like component. (c) DA-WAM (2608.19085) and DriveSuprim (2506.06659) target "distinguishing geometrically similar candidates with different safety outcomes", which is the information-separation problem the project studies.
- **Judge Then Drive and Counterfactual VLA are not candidate selectors.** Judge Then Drive (anchor) refines one rough trajectory with a critique; its 2604.27366 full text reports Bench2Drive closed-loop success 73.33%. Counterfactual VLA reasons about meta-actions of one plan. Neither chooses among K proposals, so the closest "VLM chooses among K" papers are SimpleVSF, MindDrive, DriveCritic/DriveJudge and (outside driving) Slow Brain Fast Planner.
- **Trend 1: VLM as trajectory judge.** DriveCritic (2510.13108), DriveJudge (2606.17362), DriveReward (2606.08525), SafeVL, VL-DPO all use a VLM to compare/score trajectories. Reported gains from VLM scoring over rule scorers are small or "comparable" (DriveReward: comparable to rule-based rewards; test-time selection gain 0.22% per a search snippet, UNVERIFIED in text). This matches the project's finding that a frozen VLM adds little (+0.3 to +0.7) and mostly says "none".
- **Trend 2: scorer families on NAVSIM keep scaling the vocabulary** (GTRS, DriveSuprim, ZTRS, SparseDriveV2, DrivoR). Cheap learned scorers (34M parameter DriveVer, DrivoR sub-scores) beat or match VLMs for selection. Useful as baselines or as a source of the "expected gain"-style per-candidate sub-scores.
- **Trend 3: scorer as reward / test-time optimization** (TOAD 2606.07170, RAD-2 generator-discriminator, DriveVer test-time verifier). Verifier-guided best-of-N is now a standard framing; DriveVer and DriveReferee give the "accept / replace with safer alternative" decision that matches the project's later accept/inspect/replan/fallback phase.
- **Trend 4: runtime monitors with calibration.** Chakraborty et al. 2507.22389 (conformal forward reachable sets for safety of a motion plan, nuScenes) is the best fit for the conformal accept/reject phase; SafePath (known) is the LLM-planner analogue.
- **Gap worth stating in the thesis:** none of these papers reports accuracy-vs-query-budget curves for acquisition decisions; they all assume the full perception is available and spend the budget on VLM or scorer compute, not on perception queries. Closest budget-aware paper outside driving: "When Should a VLM Look?" (2609.22910).
- **Update (round 2):** (1) RRDrive (2609.21486) is the closest new paper: it reports the oracle-best candidate ranks 33.9th on average under a learned scorer and uses candidate-conditioned queries into a risk-occupancy field, first with oracle occupancy and then with a predicted one. (2) Oracle best-of-K headroom is documented only for scorers: DriveSuprim 91.9 (K=1) to 98.7 (K=256) PDMS; AutoVLA oracle best-of-6 adds about 3 points; Metis +0.8 EPDMS. Nobody varies the information given to the scorer, which is the project's gap. (3) DriveJudge shows a prompted VLM at chance (50.06 AUC without tools, GPT-5 55.2% on pairs) and finetuning as what helps, matching the project's "VLM mostly says none". (4) DriveReferee gates extra sampling on a geometric clearance alarm, the nearest driving precedent for "pay for more only when the default plan is doubtful".

## Papers

### DriveReferee: Geometric Safety Verdicts Need Not Be Learned for Driving World-Action Models
- id: arXiv:2609.22762 | date: 2026-09 | venue: arXiv preprint
- authors: Yu, Fengcheng et al. | code: none seen
- relevance: HIGH — an analytic geometric collision/drivable-area check on a predicted scene state, used to verify candidate trajectories and select a safer one; mirrors the project's collision-check tool and the later accept/replan phase.
- what: A learned geometry readout predicts the scene representation from camera input, then an explicit rule evaluates collision and drivable area for each candidate. Under matched candidates and budgets it matches or beats learned-verifier and heuristic baselines, and learning the verdict gives no measurable downstream gain. 92.02 PDMS on NAVSIM navtest with single-camera input.
- thesis use: idea to borrow (deterministic collision check as the verifier; supports treating the tool as rule-based and noisy only through the state estimate); baseline-style comparison for learned vs analytic verification.
- verified: abs meta fetched; html read (candidate/verifier-baseline setup)

### DiVeR: Decision-Critical Verifier Learning for VLA Test-Time Scaling
- id: arXiv:2610.04933 | date: 2026-10 | venue: arXiv preprint
- authors: Park, Seongheon et al. | code: none seen
- relevance: HIGH (idea) — measures from the dispersion of sampled action candidates how decision-critical a state is. This is a candidate-divergence signal, the same family as the project's candidate-conditioned features, but in manipulation and used for verifier training.
- what: Verifier-guided test-time scaling samples multiple action candidates and picks the most likely to succeed. DiVeR estimates decision criticality from dispersion of sampled action representations and reweights verifier learning toward states where choice matters, with no step-level labels. Improves success on LIBERO, RoboCasa and a Franka robot.
- thesis use: idea to borrow (candidate dispersion as a feature or as justification for candidate-conditioned triggering); contrast: it reweights training, it does not choose a perception query.
- verified: abs meta fetched

### SimpleVSF: VLM-Scoring Fusion for Trajectory Prediction of End-to-End Autonomous Driving
- id: arXiv:2510.17191 | date: 2025-10 | venue: arXiv preprint (ICCV 2025 NAVSIM v2 challenge entry)
- authors: Zheng, Peiru et al. | code: none seen
- relevance: HIGH — a VLM picks the final trajectory from the per-scorer top-ranked candidates; direct example of a VLM trajectory selector.
- what: Combines conventional scorers and VLM-enhanced scorers with a weight fusioner (quantitative) and a VLM-based fusioner (qualitative). The VLM module is Qwen2-VL-2B fine-tuned on navtrain to generate cognitive directives (html text). Reported as leading approach in the ICCV 2025 NAVSIM v2 challenge.
- thesis use: baseline / competitor for "VLM as ranker"; evidence that VLM selection is used as a fusion layer on top of cheap scorers, not alone.
- verified: abs meta fetched; html read

### DriveVer: Lightweight Trajectory Evaluator as Test-Time Verifier for Autonomous Driving
- id: arXiv:2607.00399 | date: 2026-07 | venue: arXiv preprint
- authors: He, Chong et al. | code: none seen
- relevance: HIGH — a plug-and-play verifier that takes candidate trajectories, multi-view features and ego kinematics and outputs a safety confidence and a refinement vector; maps to the accept/replan phase and to the ranker.
- what: Dual-head 34M-parameter verifier trained on a NAVSIM trajectory set (16 trajectories per scene with scores from low to high). Improves base planners on NAVSIM v1/v2, e.g. DiffusionDrive +0.9 PDMS; ELF-VLA 91.0 to 91.5 (html table).
- thesis use: baseline for learned ranker/verifier; shows gains are around +0.5 to +0.9, comparable in size to the project's VLM-embedding gain.
- verified: abs meta fetched; html read (table numbers)

### MindDrive: An All-in-One Framework Bridging World Models and Vision-Language Model for End-to-End Autonomous Driving
- id: arXiv:2512.04441 | date: 2025-12 | venue: arXiv preprint
- authors: Sun, Bin et al. | code: none seen
- relevance: HIGH — generate candidates with a world-action model, then a VLM-oriented evaluator (VLoE) scores them on safety, comfort, efficiency.
- what: "context simulation, candidate generation, multi-objective trade-off". Claims SOTA on NAVSIM-v1 and v2 (abstract gives no numbers).
- thesis use: competitor / baseline for VLM-evaluator ranking; contrast with project's finding that prompting a VLM is weak.
- verified: abs meta fetched

### DriveCritic: Towards Context-Aware, Human-Aligned Evaluation for Autonomous Driving with Vision-Language Models
- id: arXiv:2510.13108 | date: 2025-10 | venue: arXiv preprint
- authors: Song, Jingyu et al. | code: project page https://song-jingyu.github.io/DriveCritic
- relevance: HIGH — a VLM trained (SFT then RL) to adjudicate between trajectory pairs using visual and symbolic context; a pairwise critic.
- what: Dataset of challenging NAVSIM-style scenarios with pairwise human preferences, where EPDMS lacks context. Outperforms EPDMS and baselines at matching human preferences.
- thesis use: baseline for pairwise ranking; the pairwise formulation could replace the project's top-1 ranker in analysis.
- verified: abs meta fetched

### DriveJudge: Rethinking Autonomous Driving Evaluation with Vision-Language Models
- id: arXiv:2606.17362 | date: 2026-06 | venue: arXiv preprint
- authors: Sun, Xinglong et al. | code: none seen
- relevance: HIGH — an evaluation agent that interprets context with a VLM and then selectively invokes deterministic rule functions. This is "VLM that calls tools" applied to judging trajectories.
- what: 33,577 human-annotated samples; tasks Driving Quality Classification and Trajectory Preference Selection. Beats EPDMS by 21.23 AUC on classification and DriveCritic by 6.5% on preference selection (abstract).
- thesis use: closest tool-calling-over-trajectories design; competitor in spirit (tools called after the VLM reads context, but no budget analysis).
- verified: abs meta fetched

### DriveReward: A Comprehensive Dataset and Generative Vision-Language Reward Model for Autonomous Driving
- id: arXiv:2606.08525 | date: 2026-06 | venue: arXiv preprint
- authors: Chen, Qimao et al. | code: none seen
- relevance: MED — 1B VLM reward model for RL and multi-modal trajectory scoring.
- what: Reasoning trajectory-evaluation dataset with counterfactual behaviours. Leading VLMs fail to excel across tasks; the 1B model outperforms larger VLMs on task reward alignment and matches rule-based rewards in RL finetuning and trajectory scoring (abstract).
- thesis use: evidence that general VLMs are weak trajectory judges; supports the project's observation.
- verified: abs meta fetched

### Judge, Then Drive (anchor, extra detail only)
- id: arXiv:2604.27366 | date: 2026-04 | venue: arXiv preprint
- relevance: anchor, not new. From the html text: 73.33% total success on Bench2Drive and about 30% improvement in challenging scenarios; trained on a synthetic CriticDrive dataset (12.9M trajectories per a review page). The critic refines one rough trajectory (deltas), it does not choose among K.
- verified: html read (success rate, Bench2Drive)

### Slow Brain, Fast Planner: Latency-Resilient VLM-Augmented Urban Navigation
- id: arXiv:2606.20458 | date: 2026-06 | venue: arXiv preprint
- authors: Peng, Zhenghao "Mark" et al. | code: none seen
- relevance: MED — a VLM returns the index of one candidate from a planner proposal set (sidewalk robot, not road driving); same author as Counterfactual VLA.
- what: Defines a "trajectory scoring gap" between the planner's top choice and the best candidate. VLM selection gives 30% ADE reduction on about 2,000 real scenarios; a fusion layer turns a stale 1-3 s VLM choice into real-time scoring via geometric similarity with exponential decay. Score fusion keeps >80% success with delays up to 5 s (abstract).
- thesis use: idea to borrow (the "scoring gap" as an upper bound = the project's oracle best candidate; asynchronous VLM selection); competitor for VLM-selects-candidate.
- verified: abs meta fetched

### GTRS: Generalized Trajectory Scoring for End-to-end Multimodal Planning
- id: arXiv:2506.06664 | date: 2025-06 | venue: arXiv preprint (NAVSIM v2 challenge winner)
- authors: Li, Zhenxin et al. | code: https://github.com/NVlabs/GTRS (stated "will be available")
- relevance: MED — canonical learned scorer over a dense vocabulary plus diffusion proposals; includes "refinement training for critical trajectory discrimination" and robustness to sub-optimal sensor input. Just before the 2025-07 cutoff but essential.
- what: Vocabulary dropout trains a scorer on super-dense sets for inference on smaller subsets; sensor augmentation for OOD robustness. Approaches privileged-perception methods even with sub-optimal sensors.
- thesis use: baseline family for the learned scorer; its sensor-degradation framing is relevant to tool-noise levels.
- verified: abs meta fetched

### DriveSuprim: Towards Precise Trajectory Selection for End-to-End Planning
- id: arXiv:2506.06659 | date: 2025-06 | venue: AAAI 2026 (per search result)
- authors: Yao, Wenhao et al. | code: none seen
- relevance: MED — coarse-to-fine candidate filtering; targets "subtle but safety-critical differences" between candidates.
- what: 93.5% PDMS on NAVSIM v1, 87.1% EPDMS on v2, Bench2Drive DS 83.02, SR 60.00 (abstract).
- thesis use: baseline; cite for "what separates near-identical candidates is the hard part".
- verified: abs meta fetched

### SparseDriveV2: Scoring is All You Need for End-to-End Autonomous Driving
- id: arXiv:2603.29163 | date: 2026-03 | venue: arXiv preprint
- authors: Sun, Wenchao et al. | code: none seen
- relevance: MED — scaling study of Hydra-MDP: performance rises as anchors get denser without saturation; factorized path-times-velocity vocabulary.
- what: Verbatim abstract (html): "SparseDriveV2 scales the trajectory vocabulary to be 32 denser than prior methods ... With a lightweight ResNet-34 as backbone, SparseDriveV2 achieves 92.0 PDMS and 90.1 EPDMS on NAVSIM, with 89.15 Driving Score and 70.00 Success Rate on Bench2Drive."
- thesis use: baseline / background for scorer scaling.
- verified: abs meta fetched; html read (numbers confirmed)

### DA-WAM: Decision-Aligned Future Latents for Driving World Models
- id: arXiv:2608.19085 | date: 2026-08 | venue: arXiv preprint
- authors: Zhong, Ruiguo et al. | code: none seen (HF model card exists)
- relevance: MED-HIGH — an action-conditioned predictor generates a distinct future latent per candidate; a multi-head scorer estimates planning factors; hard-negative post-training for geometrically similar trajectories with different safety outcomes.
- what: SOTA among learned camera-based planners on NAVSIM-v1/v2 and Bench2Drive (abstract; no numbers in the abstract).
- thesis use: idea to borrow (candidate-conditioned representation so that the features reflect the distinction among candidates, which is the same motivation as a candidate-conditioned selector).
- verified: abs meta fetched

### Test-Time Trajectory Optimization for Autonomous Driving (TOAD)
- id: arXiv:2606.07170 | date: 2026-06 | venue: arXiv preprint
- authors: Xu, Yihong et al. | code: https://valeoai.github.io/TOAD/
- relevance: MED — treats the scorer as a trajectory-level reward and runs the Cross-Entropy Method at test time, warm-started from proposals.
- what: Across seven planners, NAVSIM-v1 reaches 94.7 PDMS, NAVSIM-v2 56.3 EPDMS, and HUGSIM closed-loop improves (abstract).
- thesis use: background for verifier-guided search; shows weak candidate sets cap scorer quality, relevant to K = 3-5 candidate design.
- verified: abs meta fetched

### RAD-2: Scaling Reinforcement Learning in a Generator-Discriminator Framework
- id: arXiv:2604.15308 | date: 2026-04 | venue: arXiv preprint
- authors: Gao, Hao et al. | code: none seen
- relevance: MED — diffusion generator plus RL-trained discriminator that reranks candidates by long-term driving quality.
- what: Collision rate reduced 56% versus strong diffusion-based planners (abstract); closed-loop BEV-Warp simulation.
- thesis use: baseline design for ranker; closed-loop extension reference.
- verified: abs meta fetched

### Driving on Registers (DrivoR)
- id: arXiv:2601.05083 | date: 2026-01 | venue: arXiv preprint (CVPR 2026 supplemental listed by search)
- authors: Kirby, Ellington et al. | code: promised via project page
- relevance: MED — scoring decoder mimics an oracle and predicts interpretable sub-scores (safety, comfort, efficiency).
- what: Competitive on NAVSIM-v1/v2 and HUGSIM with compact scene tokens.
- thesis use: the oracle-mimicking scorer with sub-scores is analogous to the project's oracle best-candidate labels and expected-gain targets.
- verified: abs meta fetched

### ZTRS: Zero-Human Demonstration End-to-end Autonomous Driving with Trajectory Scorer
- id: arXiv:2510.24108 | date: 2025-10 | venue: arXiv preprint
- authors: Li, Zhenxin et al. | code: none seen
- relevance: LOW-MED — RL-trained scorer over enumerable trajectories, with no human demonstrations; strong on Navhard and HUGSIM.
- thesis use: background; the oracle labels from simulator state resemble its rule-based rewards.
- verified: abs meta fetched

### Safety Evaluation of Motion Plans Using Trajectory Predictors as Forward Reachable Set Estimators
- id: arXiv:2507.22389 | date: 2025-07 | venue: arXiv preprint
- authors: Chakraborty, Kaustav et al. | code: none seen
- relevance: HIGH for the future phase — a runtime safety monitor for an end-to-end plan using conformal-calibrated forward reachable sets plus a Bayesian OOD filter.
- what: Complete (conformal coverage) and sound (Bayesian filter) monitor of ego-plan intersection with calibrated FRS of other agents; nuScenes (per search).
- thesis use: idea to borrow for conformal accept/reject; baseline for the calibrated monitor phase.
- verified: abs meta fetched

### VL-DPO: Vision-Language-Guided Finetuning for Preference-Aligned Autonomous Driving
- id: arXiv:2605.20082 | date: 2026-05 | venue: arXiv preprint
- authors: Xu, Zhefan et al. | code: none seen
- relevance: MED — frozen VLM zero-shot selects the preferred trajectory among model rollouts to build DPO pairs on WOD-E2E.
- what: VLM trajectory selection is a "high-quality proxy" for human preference; +11.94% RFS, -10.01% ADE over the pretrained model (abstract).
- thesis use: evidence that a frozen VLM can rank trajectories when used offline for labels, a different use from per-step prompting.
- verified: abs meta fetched

### SafeVL: Driving Safety Evaluation via Meticulous Reasoning in Vision Language Models
- id: no arXiv id found (NVIDIA research page; ICRA 2026 submission per project page) | date: 2025 | venue: UNVERIFIED
- authors: Ma, Yingzi; Cao et al. | code: https://safevl.github.io
- relevance: MED — VLM safety evaluator used as a planning trajectory filter in UniAD.
- what: 76% zero-shot accuracy on the Nexar collision dataset; as a UniAD trajectory filter reduces closed-loop collision rate by 8% on NeuroNCAP (from the NVIDIA page abstract, unit unspecified).
- thesis use: baseline for VLM accept/reject filter.
- verified: page fetched via search only (UNVERIFIED in text)

### Causal Scene Narration: Inference-Time Text Restructuring for Vision-Language-Action Driving
- id: arXiv:2604.01723 | date: 2026-04 | venue: arXiv preprint
- authors: Li, Yun et al. | code: none seen
- relevance: LOW-MED — runtime safety supervision layer with rule-based fallback controller between a VLA and control; CARLA with a perception-noise condition.
- what: Restructured text inputs give +31.1% relative CARLA DS on LMDrive; the controlled ablation attributes most of the gain to information content (+6.17 DS) rather than structure.
- thesis use: fallback-policy precedent; "information content matters" parallels the project's information-needed question.
- verified: abs meta fetched

### BeyondDrive (Beyond Imitation: Learning Safe End-to-End Autonomous Driving from Hard Negatives)
- id: arXiv:2605.19771 | date: 2026-05 | venue: arXiv preprint
- authors: Wang, Junli et al. | code: none seen
- relevance: LOW-MED — hard negatives that are expert-proximate but unsafe; same phenomenon as geometrically similar candidates with different outcomes.
- what: 89.7 PDMS on NAVSIM v1 with Latent TransFuser (abstract).
- thesis use: motivation for why candidate geometry alone cannot separate good from bad, so extra information is needed.
- verified: abs meta fetched

### DriveDPO: Policy Learning via Safety DPO For End-to-End Autonomous Driving
- id: arXiv:2509.17940 | date: 2025-09 | venue: arXiv preprint
- authors: Shang, Shuyao et al. | code: none seen
- relevance: LOW — trajectory-level safety preference alignment; 90.0 PDMS on NAVSIM (abstract).
- thesis use: background.
- verified: abs meta fetched

### Using Ensemble Diffusion to Estimate Uncertainty for End-to-End Autonomous Driving (EnDfuser)
- id: arXiv:2506.00560 | date: 2025-05 | venue: arXiv preprint (PMLR v307 per search)
- authors: Wintel, Florian et al. | code: none seen
- relevance: MED — 128 candidates from one frame, with the spread of the candidate set used as uncertainty and a simple safety rule (+1.7% driving score on LAV).
- thesis use: idea to borrow (candidate-set spread as an uncertainty feature; the closest to "how the candidates diverge" in driving); baseline for scene-uncertainty vs candidate-spread.
- verified: abs meta fetched

### SUPER-AD: Semantic Uncertainty-aware Planning for End-to-End Robust Autonomous Driving
- id: arXiv:2511.22865 | date: 2025-11 | venue: arXiv preprint
- authors: Ryu, Wonjeong et al. | code: none seen
- relevance: LOW-MED — BEV aleatoric uncertainty folded into a drivability map; gains on NAVHARD and NAVSAFE subsets.
- thesis use: scene-uncertainty baseline comparable to the project's trajectory-agnostic trigger.
- verified: abs meta fetched

### When Should a VLM Look? Paying Only for Visual Calls That Were Needed and Used
- id: arXiv:2609.22910 | date: 2026-09 | venue: arXiv preprint
- authors: Peng, Kunyu et al. | code: none seen
- relevance: MED-HIGH (outside driving; likely covered by another scan) — rewards visual crop/zoom calls only when needed and used; only 10-12% of visual calls were both needed and used on the cold-start checkpoint.
- what: CounterCredit gives 89.5% on V*, 80.2% on HR-Bench-4K, 76.4% on HR-Bench-8K at 1.78 vs 1.84 calls per question (abstract).
- thesis use: "decision value" (answer with vs without the call) is the same as the project's expected-gain targets; idea to borrow for labels.
- verified: abs meta fetched

### OmniDrive-R1: Reinforcement-driven Interleaved Multi-modal Chain-of-Thought for Trustworthy Vision-Language Autonomous Driving
- id: arXiv:2512.14044 | date: 2025-12 | venue: arXiv preprint
- authors: Zhang, Zhenguo et al. | code: none seen
- relevance: MED (probably another agent's area) — RL-trained "zoom in" grounding for driving VLMs, a DriveAgent-R1 competitor.
- thesis use: competitor to trajectory-agnostic zoom triggering.
- verified: abs meta fetched

### Update-Free On-Policy Steering via Verifiers (UF-OPS)
- id: arXiv:2603.10282 | date: 2026-03 | venue: arXiv preprint
- authors: Attarian, Maria et al. | code: none seen
- relevance: LOW — robotics verifier steering of a frozen diffusion policy; 49% average success improvement on 5 real tasks (abstract).
- thesis use: background for verifier-guided best-of-N.
- verified: abs meta fetched

### Counterfactual VLA (anchor, id resolved)
- id: arXiv:2512.24426 | date: 2025-12 | venue: CVPR 2026
- authors: Peng, Zhenghao "Mark" et al.
- relevance: anchor, not new. Abstract: improves trajectory accuracy by up to 17.6%, safety metrics by 20.5%; reasons counterfactually only in challenging scenarios. Resolved from the paper html: the abstract and conclusion say safety +20.5% (conclusion: "20.5% lower collisions than non-reasoning baselines"), while the Introduction says "increases the safety metric by 14.7%". Both are in the same version (v1); the paper is internally inconsistent, so quote the abstract (20.5%) and flag the 14.7% intro figure.
- verified: abs meta fetched

## Addendum, round 2 (full-text reads, cited-by, oracle gap)

### Deep read: DiVeR (2610.04933, html v2 of 2026-10-25)
- candidates: sampled from a frozen VLA policy (flow-based models: independent initial Gaussian noise with fixed conditioning, VLM computation reused through KV caching). The candidate count N is a Best-of-N setting varied in the LIBERO-Long experiment; I did not extract the default N (math was stripped from the html), so UNVERIFIED.
- separating signal: a learned binary verifier on the action-expert representation, trained with decision-weighted BCE. The weight is the dispersion of the sampled candidates' action-expert representations at that state, standardized within each trajectory. Low dispersion marks routine states, high dispersion marks states where "plausible actions diverge and candidate selection can substantially affect downstream outcomes".
- extra perception acquired: none. All candidates share the same observation; the paper does not query extra sensing.
- baselines (same candidate sets, Best-of-N): KDPE (kernel-density), MG-Select (verifier-free), TACO and SVM (learned verifiers), plus a VLM-based verifier.
- headline (Intro): "DiVeR improves task success by up to +13.6% over single sample inference and +3.4% over the strongest baseline", and "surpasses the VLM-based verifier by +4.6% success rate". Benchmarks: LIBERO-Long, RoboCasa (18 atomic tasks), Franka real robot, three seeds.
- thesis: the only paper found where candidate dispersion decides where verification effort matters. It is a training-time weighting, not a per-step query policy, so it supports but does not pre-empt the project.

### Deep read: DriveReferee (2609.22762)
- candidates: one default sample from the world-action policy; "additional sampling is triggered only when" the referee's clearance on the default plan falls below a threshold. On an alarm the policy draws additional candidates and all are evaluated on the same predicted map. The number of extra candidates is not extracted (math stripped), UNVERIFIED. Candidates are ranked by fewer violating poses, then larger clearance, then a tie-break score.
- separating signal: an analytic referee implementing two checks, Drivable Area Compliance and No At-Fault Collision, on a rasterized scene state predicted from camera features by a learned geometry readout (depth distribution lifted to BEV, LSS/Simple-BEV style).
- extra perception acquired: none per candidate. The scene state is predicted once from the same frames. The paper does adapt compute (extra samples only on alarm), which is an acquire-more-only-when-needed policy, but for candidate generation, not for sensing.
- baselines: three map-blind controls (random, smoother, more conservative) and learned verifiers with the same base policy, candidate set and budget; the learned verifier is trained on up to 66,385 labelled candidates with 5/10/25/50/100% data ablation.
- headline (Abstract / Sec. IV): "learning the verdict provides no measurable downstream gain despite requiring tens of thousands of evaluator-labeled training examples"; "92.02/91.56 PDMS/EPDMS on the full NAVSIM navtest" (full, 16B backbone, 1 camera). Related-work text notes that verification "has largely been studied through oracle best-of-N evaluation rather than as a deployable mechanism" and that Metis follows AutoVLA's best-of-N protocol with an oracle scorer.
- thesis: the gate-then-sample structure is the nearest driving analogue to "spend extra only when the default is uncertain" and gives a template for the project's inspect/replan phase.

### Deep read: DriveJudge (2606.17362)
- candidates: pairs, not K. Task 2 uses the DriveCritic validation set for NAVSIM: "Given two trajectories ... with human preference label". Ambiguous-preference pairs were removed from DriveCritic's set (Appendix B.3).
- separating signal: a Qwen-based VLM (2B and 8B variants) reads the scene, then selectively invokes deterministic rule functions (collision checks, lane deviation); SFT then RL.
- extra perception: this is tool acquisition by a VLM, but the tools are rule evaluators on provided state, not perception sensors, and no query-budget analysis is given.
- baselines (Table 2, trajectory preference accuracy): Random 50.00, ADE/FDE 70.53, EPDMS 56.50, GPT-5 55.20, Gemini3.1 55.45, Supervised Classifier 64.80, DriveCritic 76.33, DriveJudge-2B 80.63, DriveJudge-8B 82.83.
- Table 3 (AUC, driving-quality classification): VLM-DirectScore (no tools, no finetune) 50.06; DriveJudge zero-shot with tools 56.13; Non-VLM finetuned 58.39; Non-VLM-Agent 55.11; VLM-DirectScore-Ft 68.67; DriveJudge full 77.95. Text: "Tool invocation improves zero-shot performance (50.06 to 56.13 AUC)".
- thesis: strongest published parallel to the project's finding that a prompted VLM at chance picks tools/candidates poorly (50.06 AUC and GPT-5/Gemini near 55% on pairs), and that finetuning is what produces the gain.

### Deep read: EnDfuser (2506.00560, v2 of 2026-05, PMLR 307)
- candidates: 128 trajectories from one perception frame via ensemble diffusion in a CARLA closed-loop planner.
- separating signal: the variance of predicted speed across the candidates is the uncertainty indicator. A rule overrides the target speed with a braking value when it exceeds a threshold. Abstract: the rule "improves the system's driving score by 1.7% on the LAV benchmark" (the math was stripped from the html so I confirmed only the abstract figure). The paper also tests naive speed reduction and concludes the rule's gain on LAV is partly explained by lower speed (Sec. 4.2: larger naive reduction gives "a similar increase in DS ... it coincides with increased route timeouts").
- extra perception: none. Baselines: TF++ (and variants with and without the rule); evaluation on LAV and Longest6.
- thesis: precedent for candidate-set spread as the trigger signal in driving, but the action is braking, not acquiring information, and the gain is small and confounded by speed.

### Deep read: DA-WAM (2608.19085)
- candidates: a trajectory generator emits the candidate set (default candidate count not extracted; the latency appendix scales 1 to 64 candidates in 36.52-39.00 ms and 128 in 42.57 ms; default takes 37.24 ms, 12.56 ms slower than DiffusionDrive and 258.32 ms faster than DrivoR). Training adds retrieved expert-proximate alternatives with different collision and TTC outcomes (hard negatives).
- separating signal: an action-conditioned predictor builds a distinct future-latent token set per candidate (V-JEPA 2.1 encoder, LoRA rank 32) and a shared scorer predicts planning factors and utility.
- extra perception: none at inference.
- baselines: DiffusionDrive, DrivoR, UniVLA and others (Table 1).
- headline: "DA-WAM achieves 93.7 PDMS on NAVSIM-v1 using its learned candidate scores directly" (text); SOTA among learned camera planners on NAVSIM-v1/v2 and Bench2Drive.
- thesis: argues candidate-specific future latents are needed to separate candidates, i.e. candidate-conditioning matters for the scorer. The project's selector is conditioned on candidate geometry only.

### Driving on Registers, Reasoning on Risk: Risk-Aware Occupancy for Register-Based End-to-End Autonomous Driving (RRDrive)
- id: arXiv:2609.21486 | date: 2026-09 | venue: arXiv preprint
- authors: Chen, Jiaxing et al. | code: none seen
- relevance: HIGH — measures an oracle-best-of-K gap directly and uses "candidate-conditioned risk queries" for selection.
- what: Abstract: "On a register-based baseline, bad and poor candidates constitute 19.74% of the candidate set, while the oracle-best candidate ranks only 33.9th on average." Candidate-conditioned risk queries on a risk-aware occupancy representation lift selected-trajectory PDMS to 0.951 vs 0.937 baseline (+1.5% relative), average candidate PDMS by 7.7%, and Spearman correlation among good candidates from 0.26 to 0.67. They first use an oracle RiskOcc (their dataset RiskOcc4D-NAVSIM) and then "move beyond this oracle setting" with an external RiskOcc predictor from sensors, described as competitive.
- thesis use: direct evidence for the fair-ceiling framing (oracle vs predicted perception, as the project does with privileged state vs noisy tools); competitor-in-spirit for "candidate-conditioned queries", though it queries a learned occupancy field rather than choosing among tools under a budget.
- verified: abs meta fetched; html read (abstract-level numbers)

### Oracle best-of-K headroom evidence (for the "fair ceiling")
- DriveSuprim (2506.06659), Table 1 (html): "PDM score of the best trajectory in the top-K candidates on ranked predicted scores": PDMS 91.9 at K=1, 94.5 at K=4, 96.1 at K=16, 98.7 at K=256, versus Human 94.8. Oracle selection over a 256-candidate set therefore sits 4.9 points above the human demonstration (98.7 vs 94.8) and 5.2 above the paper's own 93.5 PDMS top-1 result (abstract). verified: html read.
- AutoVLA (2506.13757): "In best-of-N planning, we use an oracle scorer to select the optimal trajectory from six generated candidates" (html). First-column values in its table: One-shot 80.54, Post-RFT 89.11, Best-of-N 92.12 (column header not recoverable from the text; presumably PDMS, UNVERIFIED). Oracle best-of-6 adds about 3.0 over Post-RFT. verified: abs meta fetched; html read.
- Metis (2606.15869), NAVSIM-v2 navtest Table 2 (html): EPDMS 89.5 for the single-pass model and 90.3 in the best-of-N (N=6, following AutoVLA) row, a gain of 0.8 with an oracle scorer. verified: html read (table row; dagger marker not visible in text).
- RRDrive (2609.21486): oracle-best candidate ranks 33.9th on average among the baseline's ranked candidates (abstract).
- Take-away: the oracle headroom is large for big vocabularies (K=256) and a few points for K=6 (0.8 to 3.0), and gaps vary a lot with how the candidate set was built. The project's K=3-5 with privileged-state oracle fits the "small K, modest headroom" regime. No paper found reports oracle-vs-learned-scorer gap as a function of information given to the scorer, which is the project's contribution.

### Risk-aware World Model Predictive Control (RaWMPC)
- id: arXiv:2602.23259 | date: 2026-02 | venue: arXiv preprint
- authors: Sun, Jiangxin et al. | code: none seen
- relevance: MED — a world model predicts consequences of multiple candidate actions and picks low-risk ones with explicit risk evaluation, with no expert supervision.
- thesis use: baseline concept for risk-evaluated selection; generalization claim to long-tail.
- verified: abs meta fetched

### Cited-by results (OpenAlex)
- Judge Then Drive (W7159598366): 0 citing works as of 2026-11-06 in OpenAlex; DriveCritic (W4415274616): 0. DriveJudge cites DriveCritic and is the only direct follow-up found.
- GTRS (W4417119532, 9 citing since 2025-07) and Hydra-MDP (W4399598145, about 40): mostly scorer-family papers already listed (SparseDriveV2, DriveSuprim, BeyondDrive). New titles seen but not read: DriveFine (masked diffusion VLA), RASA-Drive (robustness diagnosis of scoring-based planners, Appl. Intell. 2026), RiSE-Drive (risk-sensitive long-horizon candidate evaluation, ACM 2026-11-05, no arXiv page found), AnchDrive, HAD, Drive-JEPA, "Teaching Vision-Language-Action Models What to See and Where to Look" (not read). These were found only by title in OpenAlex; treat as UNVERIFIED leads.

### Resolutions of earlier UNVERIFIED items
- Counterfactual VLA: resolved above (20.5% in abstract/conclusion, 14.7% in intro, same paper).
- SparseDriveV2 numbers: confirmed from html (92.0 PDMS, 90.1 EPDMS, 89.15 DS and 70.00 SR on Bench2Drive, ResNet-34).
- SafeVL: still no arXiv id; numbers (76% zero-shot on Nexar, 8% closed-loop collision reduction as a UniAD trajectory filter on NeuroNCAP) remain from the NVIDIA page via search only. Kept UNVERIFIED.

## Leads not followed
- Cited-by lists (OpenAlex) for Judge Then Drive, GTRS, Hydra-MDP, DriveCritic; a web search found no citing papers for Judge Then Drive, but a proper OpenAlex query was not run.
- Other 2026 follow-ups that surfaced but were not fetched: WoTE and RFWorld (NeurIPS 2026, rollout-free world model trajectory evaluation), IRL-VLA (CVPR 2026), MTDrive (multi-turn RL with PDM agent for trajectory refinement), DiffRefiner, VDRive, ReCogDrive, AgentThink (2505.15298), ColaVLA (2512.22939).
- SafeVL arXiv id: not found; check NVIDIA/Google Scholar.
- Robotics VLA verifiers (RoboMonkey, RoVer 2510.10975, ADVLA) and RoboSafe (2512.21220) as guardrail precedents; only noted from search snippets.
- Targeted OpenReview ICLR 2027 search for "trajectory verifier", "best-of-N driving", "active perception driving" was not run.
