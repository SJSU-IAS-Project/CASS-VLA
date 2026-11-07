# L1_listing_t1 (arXiv listing sweep, slice t1: 405 titles, 2607-2611)

## Summary
- No close overlap found. None of the 405 titles is a candidate-conditioned perception-query selector for driving. The slice is dominated by manipulation VLA papers.
- Closest conceptual match to the selector question: "When to Probe and When to Act" (2611.02240), a classical belief-space MPC that plans information-seeking and switches to execution as clarity grows. It is not learned and has no VLM or tools, but it is the only driving paper here that frames probe-versus-act under diminishing returns.
- Best framing paper for the "whether to query" side: "When to Ask for Help" (2610.21160) defines a Value of Intervention (VoI) and measures it against cost ratio. It is on VLA slow-module calls (LIBERO), not driving, but it gives language for the equal-budget Pareto comparison and shows trigger gains vanish when failures are homogeneous.
- Uncertainty-gated acquisition: AtVLA (2608.02197) crops and re-encodes a region only on uncertain steps (~30% of steps, 1.4-1.6x compute). This is a scene-uncertainty trigger like the DriveAgent-R1 baseline, in manipulation.
- Monitor and calibration side (future phase): SRP (2610.37299, Bench2Drive), RESCUE (2610.13516), CalVLA (2611.00394), VLA-Tug (2611.08425, bounded miss/false-alarm rates), post-hoc epistemic heads with referral (2610.29730). RESCUE's point that an accurate alarm can still be not worth acting on is a useful caution for accept/inspect/replan.
- VLM-feature caveats: 2609.37046 finds speed is decodable from hidden states (probes 4.7-5.8 km/h MAE) far better than verbalized (10.2-16.8), which supports using frozen embeddings with a head instead of prompting. 2610.01531 evaluates Qwen3.5-9B (the project's VLM) under visual corruption.
- Benchmarks: CausalDriveBench (2609.32157) and BD-HazardVLM (2610.20627) are VQA-style, not tool or candidate-selection benchmarks. Low fit.
- Second pass (coordinator request) fetched every previously unfetched shortlist item plus a further 12 driving titles. Added GeoCoTDrive (2610.10390, the nearest ROI-then-geometry chain, but always on), CVAA (2607.16938, object-removal causal influence with traffic lights over-weighted), attention steering (2608.17095), OGAM (2610.05878) and VAST (2609.19681, occluded intersections). Still no paper does candidate-conditioned query selection.
- Already in other raw files and skipped: 2607.04179, 2609.08217, 2608.01755 (A_driving_tool_agents.md).

## Papers

### When to Probe and When to Act: Clarity-Aware Risk-Adaptive Control for Interactive Driving
- id: arXiv:2611.02240 | date: 2026-11 | venue: arXiv preprint
- authors: Wang, Youran et al. | code: none
- relevance: MED — information-seeking versus execution in driving under ambiguity, but classical MPC with no tools or VLM.
- what: Belief-space MPC that treats a scalar "clarity" as a planning variable, couples multistep information planning with a clarity-adaptive CVaR barrier, so it probes when ambiguous and relaxes once confident. Over 5,000 simulations in lane-merging and unsignalized intersections, it reports the highest success rates (94.6% and 93.2%) and lowest collision rates (1.2% and 1.4%) among compared methods.
- thesis use: related work for value-of-information in driving; idea to borrow (diminishing returns of queries, clarity-dependent risk); not a baseline.
- verified: abs meta fetched

### When to Ask for Help: A Decision-Theoretic Account and Measurement Standard for Slow-Module Scheduling in Dual-System Vision-Language-Action Models
- id: arXiv:2610.21160 | date: 2026-10 | venue: arXiv preprint
- authors: Zhang, Shilin | code: none
- relevance: MED — formal "whether to invoke an expensive module" objective with cost ratio, but manipulation (LIBERO).
- what: Casts slow-module invocation as a calibrated decision problem with a Value of Intervention (VoI) quantity that covers fixed-ratio, fixed-budget and history-gated schedules as special cases. Measured systems span three orders of magnitude in cost ratio rho. Calibrated gains vanish under homogeneous collapse and grow with heterogeneity. A leak-free protocol cuts apparent early-warning AUC from 0.93 to 0.62 on 929 deployment traces.
- thesis use: framing and citation for "query value vs. budget"; idea to borrow (report cost ratio, leak-free evaluation of triggers).
- verified: abs meta fetched

### Look Where It Matters: Adaptive Visual Refinement for Vision-Language-Action Models
- id: arXiv:2608.02197 | date: 2026-08 | venue: arXiv preprint
- authors: Cui, Jin et al. | code: none
- relevance: MED — uncertainty-gated crop-and-re-encode, the same pattern as a scene-uncertainty ROI trigger, in manipulation.
- what: AtVLA adds register tokens and uncertainty-gated local refinement. The action expert samples multiple action chunks and uses their disagreement as uncertainty. Only for uncertain steps, a region chosen by action-conditioned attention rollout is cropped and re-encoded at high resolution. LIBERO success rises from 94.2% to 98.4% and real-world success from 46.5% to 69.0%. Cropping triggers on about 30% of replanning steps at 1.4-1.6x compute.
- thesis use: baseline-style precedent for uncertainty-triggered ROI inspection; note its trigger uses disagreement among sampled action chunks, which is a weak form of candidate-set dependence.
- verified: abs meta fetched

### Towards Reliable Vision-Language Models for Autonomous Driving
- id: arXiv:2610.01531 | date: 2026-10 | venue: arXiv preprint
- authors: Mammen, Manasa Mariam et al. | code: none
- relevance: MED — evaluates Qwen3.5-9B (the project's frozen VLM) for accuracy and confidence reliability under visual corruption.
- what: Evaluates five VLMs (Qwen3.5-9B, Gemma4-E4B, LLaVA-OneVision-7B, DriveFusionQA-4B, Alpamayo-1.5-10B) on four driving QA datasets under degraded inputs. Effects of corruption vary across models, datasets and input settings. Applies Visual Evidence Augmentation, which helps for some model and dataset pairs but not consistently.
- thesis use: supports the noise-level design and VLM-confidence caveats; citation for why prompting the VLM to choose tools is unreliable.
- verified: abs meta fetched

### Speed in the Blind Spot: An Interpretability Analysis of Dynamic Perception in VLMs for Autonomous Driving
- id: arXiv:2609.37046 | date: 2026-09 | venue: arXiv preprint
- authors: Winter, Katharina et al. | code: none
- relevance: MED — explains why a depth/speed tool is needed and why frozen hidden states beat verbal output.
- what: Tests surrounding-agent speed, ego speed and future ego speed on nuScenes with open-weight VLMs and Alpamayo-1.5. For ego speed, continuous probes reach 4.7-5.8 km/h MAE versus 10.2-16.8 km/h for verbal outputs. Surrounding-agent speed is weakly encoded, and multiple frames give inconsistent verbal gains.
- thesis use: motivation for the distance/speed tool and for probing embeddings with a head rather than prompting.
- verified: abs meta fetched

### Structured Representation Probing for Risk Anticipation in End-to-End Autonomous Driving
- id: arXiv:2610.37299 | date: 2026-10 | venue: arXiv preprint
- authors: Liang, Jiawei et al. | code: none
- relevance: MED — learned runtime risk monitor on frozen driving policies; a signal that could feed an accept/inspect/replan policy.
- what: Structured Representation Probe reads actor, ego and map representations from a frozen policy with linear risk directions and pooled scores. On Bench2Drive with DriveTransformer, UniAD and VAD it beats runtime baselines. On DriveTransformer at a 2 s horizon, ROC-AUC is 0.833 versus 0.715 for temporal consistency, with 2.67% readout overhead.
- thesis use: future-phase trigger or risk signal; baseline for "scene-level risk" selectors.
- verified: abs meta fetched

### RESCUE: Is This Alarm Worth Acting On? Counterfactual Evaluation of VLA Runtime Monitors
- id: arXiv:2610.13516 | date: 2026-10 | venue: arXiv preprint
- authors: Ahmedt-Aristizabal, David et al. | code: none
- relevance: MED — evaluates monitors by the value of the intervention, not detection accuracy (manipulation).
- what: Restores simulator and policy states at checkpoints and compares alternative actions across 128,340 counterfactual branches with OpenVLA-OFT and pi_0.5 on LIBERO. Under the stop-and-reset model, even an idealised detector can afford only a 2.0-3.3% false-alarm rate before resets outweigh savings.
- thesis use: evaluation idea for the inspect/replan phase (judge a trigger by downstream cost, as the oracle-gain labels already do).
- verified: abs meta fetched

### Failure Prediction and Classification in Vision-Language-Action Models Via Calibrated Latent Probing
- id: arXiv:2611.08425 | date: 2026-11 | venue: arXiv preprint
- authors: Podolinsky, Michal P. et al. | code: https://vla-tug.github.io
- relevance: MED — calibrated probe on VLA latents with bounds on missed-detection and false-alarm rates; future calibration phase.
- what: VLA-Tug probes latent layers and bounds missed-detection and false-alarm rates. Bounds remain valid in up to 86% of runs under shift to unseen tasks versus at most 21% for baselines. Early detection at matched false-positive rate improves by up to 30% over the strongest learned baseline. Releases 3,180 annotated manipulation episodes.
- thesis use: method precedent for guarantee-style accept/reject on frozen-backbone features.
- verified: abs meta fetched

### Post-hoc Epistemic Uncertainty for Vision-Language-Action Policies
- id: arXiv:2610.29730 | date: 2026-10 | venue: arXiv preprint
- authors: Keller, Johannes et al. | code: none
- relevance: MED — uncertainty from embeddings of one policy, used to decide referral to a stronger supervisor (accuracy-vs-assistance).
- what: Kernel-variance heads compute Gaussian-process conditional variance on policy embeddings. With SmolVLA on LIBERO-10 they match two-policy ensembles on task-level correlation, active-learning demonstration acquisition and supervisor referral, with up to about 50x faster uncertainty scoring.
- thesis use: baseline-style uncertainty trigger computed from frozen embeddings; fits the "scene-uncertainty" selector family.
- verified: abs meta fetched

### OpenVisTool: An Open Recipe for Synthesizing Instructive Visual Tool-Use Trajectories
- id: arXiv:2608.08557 | date: 2026-08 | venue: arXiv preprint
- authors: Xiang, Changhao et al. | code: none
- relevance: MED — argues tool-call supervision should be kept only if the tool observation causally contributes to the answer; generic multimodal, not driving.
- what: Framework retains a trajectory only if the answer is correct and the tool observations causally contribute. Builds OpenVisTool-42K and OpenVisTool-Bench over five visual reasoning domains. Fine-tuning four backbones (4B-27B) improves visual tool use and two out-of-distribution benchmarks.
- thesis use: supports the expected-gain labeling idea (label a tool call by its counterfactual contribution rather than by final correctness).
- verified: abs meta fetched

### CausalDriveBench: Evaluating Causal Reasoning in Vision-Language-Action Models for Autonomous Driving
- id: arXiv:2609.32157 | date: 2026-09 | venue: arXiv preprint
- authors: Chembu, Narendiran et al. | code: none
- relevance: MED/LOW — distinguishes causally active, dormant and distractor entities; includes alternative-trajectory evaluation.
- what: 7,285 verified causal QA pairs and 1,000 counterfactual trajectories on nuScenes. Evaluates 10 driving VLAs and 3 VLMs. Best QA accuracy is 70.6%, and QA accuracy and trajectory accuracy are statistically uncorrelated across models.
- thesis use: related benchmark; the active/dormant/distractor split parallels decision-relevant versus merely salient objects.
- verified: abs meta fetched

### Measuring the Reasoning-Action Coupling in Driving Vision-Language-Action Models through Counterfactuals
- id: arXiv:2610.30953 | date: 2026-10 | venue: arXiv preprint
- authors: Manalu, Gabriel et al. | code: none
- relevance: LOW/MED — evidence that driving VLA text reasoning is weakly coupled to the trajectory, relevant to prompting a VLM to pick tools.
- what: Counterfactual interventions on four driving VLAs: altering the meaning of the reasoning changes trajectories less than blanking the camera input. Object-removal counterfactuals test whether reasoning and trajectories track scene changes.
- thesis use: citation for why verbal VLM choices are unreliable.
- verified: abs meta fetched

### Evidence-Gated Task and Motion Planning with Vision-Language Models
- id: arXiv:2608.20084 | date: 2026-08 | venue: arXiv preprint
- authors: Tanaka, Tsunehiko et al. | code: none
- relevance: LOW/MED — decides to proceed, acquire more evidence, or halt (manipulation, cooking).
- what: EAFG acquires visual evidence, then gates between proceeding, acquiring more evidence, or halting. Improves task completion over a VLM-TAMP baseline in the explicit and underspecified scenarios and halts correctly when a required object is absent.
- thesis use: pattern for proceed/inspect/halt policy in the future phase.
- verified: abs meta fetched

### From Scene Graphs to Answers: Selective Neuro-Symbolic Reasoning for Autonomous Driving
- id: arXiv:2609.32645 | date: 2026-09 | venue: arXiv preprint
- authors: Wang, Yiyao et al. | code: none
- relevance: LOW/MED — cheap symbolic path first, LLM only when the symbolic executor abstains.
- what: Spatiotemporal scene graph with a symbolic executor, LLM called only on abstention. On 5,916 NuScenes-QA questions under oracle perception, 80.63% accuracy with GPT-5.4-mini, +5.48 points over LLM-only.
- thesis use: analogy for cost-aware tool escalation; minor.
- verified: abs meta fetched

### Explicit Geometric Chain-of-Thought for Vision-Language-Action in Autonomous Driving (GeoCoTDrive)
- id: arXiv:2610.10390 | date: 2026-10 | venue: arXiv preprint
- authors: Gui, Xingtai et al. | code: none
- relevance: MED — "think with 2D first, drive with 3D priors": grounds decision-critical 2D regions, then pulls localized geometry from a foundation model inside those regions only. Closest in this slice to an ROI-then-depth tool chain, but always on, with no budget or selector.
- what: Introduces a planning-relevant grounding task and the PlanningGrounding dataset; localized 3D features are interleaved into the autoregressive context before trajectory generation. Abstract reports consistent gains in safety-critical planning across benchmarks, with no numbers given.
- thesis use: competitor or always-on upper-bound analogue; idea to borrow (grounding labels defined by planning relevance).
- verified: abs meta fetched

### What Do They See? Interpreting Complex Road Scenarios Through the Eyes of Vision-Language-Action Models (CVAA / Counter-nuScenes)
- id: arXiv:2607.16938 | date: 2026-07 | venue: arXiv preprint
- authors: Panda, Kalpana et al. | code: none
- relevance: MED — measures each object's causal effect on the planned trajectory by inpainting it out; the same notion as decision-relevance of a query target.
- what: Counterfactual ablation on Alpamayo 1 over 210 nuScenes scenes builds Counter-nuScenes. Vehicles and pedestrians on the path dominate. Traffic lights exert disproportionate effect relative to image footprint. Some irrelevant objects still move the plan.
- thesis use: evidence that the traffic-light and in-path actor hazards are the decision-relevant ones; possible recipe for oracle labels from real data.
- verified: abs meta fetched

### Inference-Time Attention Steering for Vision-Language-Action Driving Models
- id: arXiv:2608.17095 | date: 2026-08 | venue: arXiv preprint
- authors: Prasad, Darshan Nagendra et al. | code: none
- relevance: LOW/MED — redirects attention to detector-localized actors on Alpamayo-R1 at inference time, a soft ROI query.
- what: Additive pre-softmax attention bias on visual tokens of detected actors, 50 lane-change scenarios. Trajectory shift grows monotonically with bias magnitude (about 17 cm mean displacement, lateral up to about 140 cm at the clamp). The Chain-of-Causation text never changes, so the effect is on where the model looks.
- thesis use: shows an ROI "tool" can be applied to a frozen VLA without retraining; cautions that reasoning text may not respond.
- verified: abs meta fetched

### OGAM: Object-Grounded Attention Monitoring for VLA Policies
- id: arXiv:2610.05878 | date: 2026-10 | venue: arXiv preprint
- authors: Darwish, Haki et al. | code: none
- relevance: LOW/MED — conformal early-stop threshold calibrated on successful episodes only, nominal false-stop target alpha = 0.05 (manipulation).
- what: Stops 87-100% of failed episodes at median 5-12 s with observed false-stop rates of 3-5% across four policies.
- thesis use: calibration-phase precedent.
- verified: abs meta fetched

### VAST: V2X/Dynamic Map-Aware Autonomous Driving Systems Validation Toolchain
- id: arXiv:2609.19681 | date: 2026-09 | venue: arXiv preprint
- authors: Ito, Shunsuke et al. | code: none
- relevance: LOW/MED — occluded-intersection scenario generation with an extra information channel (Dynamic Map).
- what: Constrained sampling raises edge-case discovery from 40.0% to 80.0%. Dynamic Map availability cuts collision rate from 78.0% to 40.0% in the same scenario distribution (Autoware/AWSIM, not MetaDrive).
- thesis use: related work for occlusion scenario generation; shows extra information helps in occluded intersections.
- verified: abs meta fetched

## Shortlisted but dropped
- 2607.01658 Teaching VLA What to See and Where to Look: training recipe with trajectory-guided prompts (NAVSIM, nuScenes); no query selection.
- 2608.23224 Think Only When Needed: prompt gating for retrieved text in manipulation; not perception queries.
- 2608.14047 ART tool-use VLA: manipulation tool injection, no budget or selection.
- 2610.23378 Look Before You Act (ActiveAlign): active camera motion for manipulation occlusion; domain mismatch.
- 2609.25831 Run-then-Walk: RL reward schedule for VLM planners; no tools.
- 2609.38641 AD-Memo: language memory for driving VLA; not query selection.
- 2609.35078 RefineDrive: failure-guided post-training; no tools.
- 2610.20627 BD-HazardVLM: 500-image hazard VQA diagnostic; no tools or trajectories.
- 2611.00394 CalVLA: failure-confidence shaping on OpenVLA, manipulation, AUROC 0.7392; not driving.
- 2607.00776 Conformalized distance fields: conformal safe MPC for pedestrians/quadrotors; no perception queries, possible far-future reference only.
- 2608.08631 Budgeted querying for digital twin calibration: pendulum/Waterworld; off-domain.
- 2608.08575 title matched a VLA-conformal pattern in the listing but the abstract is a 3D medical segmentation paper (CDGC-Net); id/title in the TSV was inconsistent with the fetch, ignore.
- 2607.05180 VLM-CASE: fetched; a VLM reports road surface and visibility to set an MPC safety envelope (CARLA). Always-on, no query selection.
- 2608.01998 TALSC: fetched; Lyapunov scheduling of large vs small VLM calls under latency (up to 12.6% Micro-F1 gain). Cloud offload scheduling, not perception queries over trajectories.
- 2609.40007 Multi-link safety filter: fetched; manipulation barrier shield.
- 2610.05719 When to Switch (RACE): fetched; action-chunk transition timing in manipulation.
- 2610.34108 RoboDuo: fetched; coding agent picks full-task or atomic VLA after a completion check, LIBERO.
- 2609.34061 Quantile Head: fetched; action-head quantiles, no uncertainty-driven decisions.
- 2608.07361 Depth-wise probing of planning token (ORION): fetched; layer pruning, 97.7% command-probe accuracy after layer 1; not query selection.
- 2608.09202 CRUISE: fetched; VLM-guided pixel-level uncertainty for sensor fusion, no trajectory or query selection.
- 2608.13395 FIRE-VLA, 2608.07621 CMU-Drive, 2611.06204 CoSafe, 2610.16634 Language2Drive, 2610.34689 RSKD, 2607.29169 ActFovea, 2611.06160 DSRS, 2607.20988 HyWorldVLA, 2608.10976 XCoT-VLA, 2607.08375 WCog-VLA, 2608.15573 StableDrive: fetched in second pass; training recipes, cooperative driving, or instruction-following benchmarks with no tool/query selection or hazard evaluation.

## Leads not followed
- Second pass not exhaustive: remaining driving titles in t1.tsv were judged from the title only (for example 2609.00111 Qwen-Drive-1.0, 2607.04637 PixelPilot, 2608.12932 FlashDrive, 2608.21440 Geo-VLA, 2609.30709/2609.36934 VLALight traffic-signal control, 2610.25734 Think Densely Act Sparsely).
