# E_benchmarks

## Summary
- No close overlap found. No benchmark in this sub-area measures candidate-conditioned perception-query selection or per-query cost for a driving planner. The closest items are generic VLM tool-gating papers (ToolGate, CounterCredit) that are not driving.
- Closest benchmark to the project's hazard types: "What's Hidden Matters" (2607.00283) ranks occluded agents by their effect on the ego plan (Planning KL-divergence). This is the same decision-relevance idea as the project, but applied to occlusion identification by a VLM, not to tool choice.
- Robustness benchmarks (RoboDriveBench 2512.01300, Lost in Fog 2605.21446, DriveBench 2501.04003, Safety2Drive 2505.13872) give corruption recipes (fog, noise, lighting) to justify or parameterize the three tool-noise levels. DriveBench reports that VLMs only acknowledge a corruption when asked directly. (A Robust Agentic Utilization / RAU method I first reported is NOT in the arXiv HTML text I read; dropped.)
- Closed-loop VLM benchmarks (Bench2Drive-VL 2604.01259, Bench2ADVLM 2508.02028) and NAVSIM v2 pseudo-simulation (2506.04218) are the natural next step beyond open-loop MetaDrive. MetaVQA (2501.09167) is the only item already on MetaDrive/ScenarioNet with VLMs.
- Long-tail datasets with candidate-trajectory preference labels: WOD-E2E (2510.26125) has rater scores over several candidate trajectories per example. This matches the "K candidate trajectories, oracle best" setup better than any other real-data benchmark found.
- Traffic-light ambiguity is thinly covered: DriveAction and TaCarla touch traffic lights, nothing targets occluded or ambiguous lights for VLMs. This is a gap the project's injected-hazard design fills.
- Searches were web-snippet based; metadata verified with absfetch, full texts not read. Several paper dates are 2026 from arXiv ids, taken at face value.

## Papers

### What's Hidden Matters: Identifying Planning-Critical Occluded Agents using Vision-Language Models
- id: arXiv:2607.00283 | date: 2026-07 | venue: arXiv preprint (IEEE copyright notice in PDF)
- authors: Chahe, Amirhosein et al. | code: none seen
- relevance: HIGH — plan-conditioned decision relevance of hidden agents; closest in spirit to candidate-conditioned query value.
- what: Uses Planning KL-divergence to rank occluded agents by impact on the ego plan, has GPT-5 write structured annotations, and builds a nuScenes benchmark of high-impact scenarios. Fine-tuned smaller VLMs beat larger zero-shot ones; PKL-guided data selection improves about 30% over random sampling.
- thesis use: idea to borrow (PKL as a decision-relevance score for the oracle or features); related work for occlusion hazards.
- verified: abs meta fetched

### Lost in Fog: Sensor Perturbations Expose Reasoning Fragility in Driving VLAs
- id: arXiv:2605.21446 | date: 2026-05 | venue: CVPR 2026 Workshop SAIAD (per known list)
- authors: Priyadershi, Abhinaw et al. | code: none seen
- relevance: HIGH — known anchor; id now resolved.
- what: Alpamayo R1 (10B) over 1,996 scenarios and 8 perturbations (noise at 4 levels, 2 lighting extremes, 2 fog levels). When the Chain-of-Causation explanation changes, trajectory deviation rises 5.3x (21.8 m vs 4.1 m). Evaluation is open-loop.
- thesis use: motivation for tool-noise levels; reasoning-consistency as a possible trigger signal.
- verified: abs meta fetched

### Bench2Drive-VL: Benchmarks for Closed-Loop Autonomous Driving with Vision-Language Models
- id: arXiv:2604.01259 | date: 2026-04 | venue: arXiv preprint
- authors: Jia, Xiaosong et al. | code: https://github.com/Thinklab-SJTU/Bench2Drive-VL
- relevance: MED — closed-loop VLM driving in CARLA, plug-in interface and configurable graph-based CoT.
- what: Extends Bench2Drive with DriveCommenter (behavior-grounded QA generator, including off-route states) and a unified interface to plug VLMs into the closed loop.
- thesis use: future closed-loop validation target after the open-loop MetaDrive study.
- verified: abs meta fetched

### Pseudo-Simulation for Autonomous Driving (NAVSIM v2)
- id: arXiv:2506.04218 | date: 2025-06 (v3 2026-03) | venue: CoRL 2025
- authors: Cao, Wei et al. | code: https://github.com/autonomousvision/navsim
- relevance: MED — open-loop-cost evaluation that correlates with closed loop (R^2 = 0.8 vs 0.7 for best open-loop on nuPlan, per abstract). Pre-2025-07 but essential.
- what: Real logs plus pre-rendered 3D Gaussian Splatting observations, proximity-weighted. EPDMS metric adds traffic-light compliance and driving-direction compliance (from secondary summary, not checked in paper).
- thesis use: evaluation protocol to cite for justifying open-loop-plus-perturbation; EPDMS traffic-light term fits the light hazard.
- verified: abs meta fetched

### WOD-E2E: Waymo Open Dataset for End-to-End Driving in Challenging Long-tail Scenarios
- id: arXiv:2510.26125 | date: 2025-10 | venue: CVPR 2026 (per search result poster page, where it appears as Rare-E2E; not checked further)
- authors: Xu, Runsheng et al. | code: none seen
- relevance: MED — long-tail segments with rater preference scores over multiple candidate trajectories (Rater Feedback Score).
- what: 4,021 segments (about 12 hours), events under 0.03% frequency, 8 cameras, routing, ego state. Validation rater labels public.
- thesis use: real-data benchmark where the "candidate set + preference label" structure transfers; possible sim-to-real check.
- verified: abs meta fetched

### RoboDriveVLM: A Novel Benchmark and Baseline towards Robust Vision-Language Models for Autonomous Driving (RoboDriveBench)
- id: arXiv:2512.01300 | date: 2025-12 | venue: arXiv preprint
- authors: Liao, Dacheng et al. | code: "will be released"
- relevance: MED — robustness benchmark for VLM trajectory prediction.
- what: 11 corruption scenarios (6 sensor, 5 prompt), 250 scenarios and 5,689 frames each, 64,559 trajectory cases per evaluation, built on nuScenes. Proposes a unified-latent multimodal method and test-time adaptation.
- thesis use: corruption taxonomy for tool-noise design.
- verified: abs meta fetched

### Are VLMs Ready for Autonomous Driving? (DriveBench)
- id: arXiv:2501.04003 | date: 2025-01 | venue: ICCV 2025
- authors: Xie, Shaoyuan et al. | code: drive-bench.github.io (toolkit on GitHub)
- relevance: MED — pre-2025-07 but essential; reports VLMs answer from text priors under degraded images. CORRECTION: the RAU / agentic tool-use method claimed earlier came from a search summary and is absent from the arXiv HTML; do not cite it.
- what: 17 settings (clean, corrupted, text-only), 19,200 frames, 20,498 QA pairs, 12 VLMs.
- thesis use: see the full-text block appended below.
- verified: abs meta fetched

### Embodied Scene Understanding for Vision Language Models via MetaVQA
- id: arXiv:2501.09167 | date: 2025-01 | venue: CVPR (OpenAlex lists a CVPR proceedings location; year not checked)
- authors: Wang, Weizhen et al. | code: none checked
- relevance: MED — VLM benchmark with closed-loop runs in MetaDrive using ScenarioNet scenarios (nuScenes, Waymo).
- what: Set-of-Mark prompted VQA plus closed-loop simulation; fine-tuning on MetaVQA improves spatial reasoning (per abstract).
- thesis use: precedent and tooling for VLMs in MetaDrive; same simulator stack.
- verified: abs meta fetched

### Bench2ADVLM: A Closed-Loop Benchmark for Vision-language Models in Autonomous Driving
- id: arXiv:2508.02028 | date: 2025-08 | venue: arXiv preprint
- authors: Zhang, Tianyuan et al. | code: none checked
- relevance: MED — closed-loop VLM driving in CARLA (Bench2Drive routes) with self-reflective generation of 220 safety-critical scenarios from 220 standard routes (html read).
- what: Dual-system adaptation (fast ADVLM, slow general VLM mapping to control), plus a physical-vehicle control layer.
- thesis use: closed-loop and safety-critical evaluation reference.
- verified: abs meta fetched

### Safety2Drive: Safety-Critical Scenario Benchmark for the Evaluation of Autonomous Driving
- id: arXiv:2505.13872 | date: 2025-05 | venue: arXiv preprint
- authors: Li, Jingzheng et al. | code: none checked
- relevance: LOW-MED — 70 regulation-based test items in CARLA, with camera and LiDAR corruption and adversarial attack injection. Pre-2025-07.
- thesis use: scenario-library and corruption injection reference.
- verified: abs meta fetched

### D2-V2X: Depth-Driven Cooperative V2X Reasoning for Autonomous Driving
- id: arXiv:2605.24098 | date: 2026-05 | venue: arXiv preprint
- authors: Richard, Kevin et al. | code: none seen
- relevance: MED — QRA benchmark of 8,500 triplets targeting occluded hazards; the zero-shot VLM scores near zero on occluded hazards, the LiDAR-grounded model gets 24.4% recall.
- what: Cooperative V2X sensors; also reports a 77% cut in spatial estimation error for visible objects vs zero-shot.
- thesis use: evidence that zero-shot VLMs miss occluded hazards, supporting the need for an ROI/reveal tool.
- verified: abs meta fetched

### BeyondSight: Object Permanence for End-to-End Autonomous Driving
- id: arXiv:2607.09138 | date: 2026-07 | venue: arXiv preprint
- authors: Papais, Sandro et al. | code: none seen
- relevance: MED — nuScenes-Permanence adds supervision and observability-conditioned evaluation for fully occluded actors.
- what: Persistent actor hypotheses through occlusion; detection of unobservable actors goes from 0 to 0.249 (metric name cut off in my fetch; UNVERIFIED).
- thesis use: occlusion evaluation reference; contrast of memory vs. active query.
- verified: abs meta fetched

### nuReasoning: A Reasoning-Centric Dataset and Benchmark for Long-Tail Autonomous Driving
- id: arXiv:2605.31572 | date: 2026-05 | venue: arXiv preprint
- authors: Huang, Zhiyu et al. | code: none seen
- relevance: LOW-MED — 20,000 20-s clips, multi-camera, LiDAR, with spatial, decision and counterfactual reasoning annotations; evaluates both reasoning and planning.
- thesis use: counterfactual reasoning labels resemble the "which candidate is better" supervision.
- verified: abs meta fetched

### DriveAction: A Benchmark for Exploring Human-like Driving Decisions in VLA Models
- id: arXiv:2506.05667 | date: 2025-06 | venue: arXiv preprint
- authors: Hao, Yuhan et al. | code: none checked
- relevance: LOW-MED — 16,185 QA pairs from 2,610 scenarios with action-rooted tree evaluation; traffic-light tasks reported as a weak point for VLA models (per search summary, not read).
- thesis use: traffic-light weakness citation.
- verified: abs meta fetched

### Evaluating Small Vision-Language Models on Distance-Dependent Traffic Perception (DTPQA)
- id: arXiv:2510.08352 | date: 2025-10 | venue: arXiv preprint
- authors: Theodoridis, Nikos et al. | code: none checked
- relevance: LOW-MED — perception-only VQA with distance annotations (near up to 20 m vs far 30+ m).
- thesis use: supports the distance-ambiguity hazard and a depth tool.
- verified: abs meta fetched

### ToolGate: Token-Efficient Pre-Call Control for Tool-Augmented Vision-Language Agents
- id: arXiv:2606.03054 | date: 2026-06 | venue: arXiv preprint
- authors: Liu, Anjie et al. | code: none seen
- relevance: MED — not driving; learns execute/skip for perception tool calls. Baseline agent shows helpful and harmful calls at similar rates (11.8% vs 9.9%); token cost cut to 64-69% of ReAct.
- thesis use: related work on cost-aware tool gating; trajectory-text features, not candidate-conditioned.
- verified: abs meta fetched

### When Should a VLM Look? Paying Only for Visual Calls That Were Needed and Used
- id: arXiv:2609.22910 | date: 2026-09 | venue: arXiv preprint
- authors: Peng, Kunyu et al. | code: none seen
- relevance: MED — not driving; defines "needed and used" for crop/zoom calls. Only 10-12% of calls were both on its cold-start checkpoint; spurious-call rate 36-87% on benchmarks.
- thesis use: metric idea (decision value vs. answering immediately) analogous to the expected-gain target.
- verified: abs meta fetched

### Making Every Tool Call Count: Necessary Tool-Evidence Path Rewards for Agentic VLMs
- id: arXiv:2609.03493 | date: 2026-09 | venue: arXiv preprint
- authors: Long, Xingming et al. | code: none seen
- relevance: LOW-MED — not driving; reports Average Tool Calls as a cost metric next to accuracy.
- thesis use: cost reporting convention.
- verified: abs meta fetched

### Know Where You're Uncertain When Planning with Multimodal Foundation Models
- id: arXiv:2411.01639 | date: 2024-11 | venue: arXiv preprint
- authors: Bhatt, Neel P. et al. | code: none checked
- relevance: MED — conformal perception uncertainty plus an active sensing intervention for planning. Older but relevant to the conformal phase and to active sensing.
- thesis use: related work (the 35% decision-uncertainty reduction was from a search summary and is UNVERIFIED).
- verified: abs meta fetched

### SteerVLA: Steering Vision-Language-Action Models in Long-Tail Driving Scenarios
- id: arXiv:2602.08440 | date: 2026-02 | venue: arXiv preprint
- authors: Gao, Tian et al. | code: https://steervla.github.io/
- relevance: LOW-MED — long-tail closed-loop subset; +4.77 driving score overall and +8.04 on long-tail vs SOTA.
- verified: abs meta fetched

### Plug-and-Play Traffic Element Awareness for End-to-End Autonomous Driving
- id: arXiv:2608.18035 | date: 2026-08 | venue: arXiv preprint
- authors: Zhang, Zongzheng et al. | code: none seen
- relevance: LOW-MED — datasets augmented with traffic-light/sign annotations; quantifies their effect on E2E driving.
- thesis use: traffic-light hazard motivation.
- verified: abs meta fetched

### Task-Aligned Stability Analysis of VLMs for Autonomous Driving Hazard Detection
- id: arXiv:2606.11889 | date: 2026-06 | venue: arXiv preprint
- authors: Richards, Everett | code: none
- relevance: LOW-MED — on BDD100K with CLIP hazard scores, most corruptions cause false negatives, occlusion causes false alarms.
- thesis use: asymmetric failure modes for noisy tools.
- verified: abs meta fetched

### TaCarla: A comprehensive benchmarking dataset for end-to-end autonomous driving
- id: arXiv:2602.23499 | date: 2026-02 | venue: arXiv preprint
- authors: Gorgulu, Tugrul et al. | code: none checked
- relevance: LOW — CARLA Leaderboard 2.0 dataset with traffic-light labels.
- verified: abs meta fetched

### Adversarial Generation and Collaborative Evolution of Safety-Critical Scenarios (ScenGE)
- id: arXiv:2508.14527 | date: 2025-08 | venue: AAAI 2026 (per search result)
- authors: Liu, Jiangfan et al. | code: none checked
- relevance: LOW-MED — LLM-generated adversarial scenarios that create critical occlusions; transferable to MetaDrive per search summary.
- thesis use: automated hazard injection idea.
- verified: abs meta fetched

### SafeGen: Goal-Conditioned Video Diffusion of Safety-Critical Scenarios for VLM-Based Autonomous Driving
- id: arXiv:2607.19701 | date: 2026-07 | venue: arXiv preprint
- authors: Liu, Jiangfan et al. | code: none seen
- relevance: LOW — video-diffusion generation of vulnerable-road-user scenarios.
- verified: abs meta fetched

### VILTA: A VLM-in-the-Loop Adversary for Enhancing Driving Policy Robustness
- id: arXiv:2601.12672 | date: 2026-01 | venue: arXiv preprint
- authors: Chen, Qimao et al. | code: none seen
- relevance: LOW — VLM edits agent trajectories for closed-loop training curricula.
- verified: abs meta fetched

### ScenarioNet: Open-Source Platform for Large-Scale Traffic Scenario Simulation and Modeling
- id: arXiv:2306.12241 | date: 2023-06 | venue: NeurIPS 2023 Datasets and Benchmarks
- authors: Li, Quanyi et al. | code: none checked
- relevance: LOW-MED — scenario format and repository (Waymo, nuScenes, Lyft, nuPlan) replayable in MetaDrive; source for real-log scenarios.
- verified: abs meta fetched

## Full-text additions (round 2)
Texts read via arxiv.org/html, tags stripped. Numbers inside math were removed by the stripper, so those cells are described, not quoted.

### What's Hidden Matters (2607.00283) - full text read
- setup (Sec. IV-A): nuScenes plus Occ3D visibility. PKL computed with a planner trained on nuScenes (4 s horizon). Scenes sorted by PKL, "the top 1,000 from the nuScenes training set and top 250 from the nuScenes validation set", giving "1,250 scene windows(1,000 training, 250 validation), resulting in 22,500 camera frames", and "3,750 structured JSON annotations (3,000 training, 750 validation) generated by GPT-5". Each window: 3 frames at 1 s intervals across 6 cameras. Annotation fields (Sec. III-C3): visual cue, camera, agent class, action hypothesis, occluder class, occlusion type, priority level (High/Medium/Low), sector.
- numbers: Table III (Sec. IV-D2), 250-sample val set: Qwen-7B random selection avg. accuracy 0.405 vs PKL 0.543 (+34%); InternVL3.5-8B 0.429 vs 0.565 (+32%). Table II: fine-tuned Qwen-7B avg. acc 0.543, avg. F1 0.514, action 0.435; zero-shot Qwen-7B (Table I) avg. acc 0.301, F1 0.257 (read from the row ending 0.253 0.301 0.257 0.085; column order inferred, check before citing).
- how it serves us: (a) PKL = KL between plan distributions with and without the hidden agent is a ready definition of "decision relevance" and could define which injected MetaDrive hazards count as planning-critical; (b) shows annotation is per-agent, not per-candidate, so it does not condition on a candidate set: no overlap with candidate-conditioned tool selection; (c) it is open-loop and offline on nuScenes, no tool calls.

### DriveBench (2501.04003) - full text read, correction
- setup: Table 1/Appendix A.2: five corruption categories. Weather and lighting (Brightness, Dark, Snow, Fog, Rain); external disturbances (Water Splash, Lens Obstacle); sensor failures (Camera Crash, Frame Lost, Saturate); motion blur (Motion Blur, Zoom Blur); data transmission errors (Bit Error, ... H.265 listed in Table 4). Tasks: perception, prediction, planning, behavior (DriveLM-nuScenes and BDD-X sources). Abstract: 17 settings, 19,200 frames, 20,498 QA pairs, 12 VLMs.
- verbatim findings: Sec. 4.2.1 "even in the presence of image corruption, the model performance remains largely unaffected"; Table 3 caption "a large portion of models have no clear performance degradation even when the visual information is absent, suggesting the VLMs response might mainly be based on majority biases"; Sec. 4.2.2 "they only explicitly acknowledge these issues when directly prompted".
- correction: no "agentic tool use" or RAU section exists in this arXiv HTML version (searched for tool/agent/RAU); my earlier statement is withdrawn.
- how it serves us: a ready 15-type corruption list to map to the three tool-noise levels; the black-image result is an argument that accuracy-only VLM selector baselines can look fine without using the image, so the project's "VLM says none" result needs a no-image control.

### WOD-E2E (2510.26125) - full text read
- setup (Sec. 3.4.2-3.5): a model such as Wayformer produces up to 64 diverse trajectories per critical moment, bucketed by velocity, acceleration and lane changes, with "a set of diverse candidates (usually fewer than 12)". Human labelers "select three trajectories from these candidates for final ranking", each given a score; RFS compares the prediction to the three rated trajectories with trust regions, takes the max score over raters' trajectories, then averages and floors. Dataset: 4,021 segments, about 12 hours, frequency under 0.03%.
- verbatim: Sec. 4.4 Q2 "a better ADE does not guarantee a better RFS" (WayNet ADE 2.8 but RFS well below most; HMVLM the reverse).
- how it serves us: closest real-data analogue of K candidates with an oracle-best label (3 rated trajectories, ranks 1 to 3). A possible real-data check of the ranker/selector: treat the rated trajectories as the candidate set and RFS as the oracle score. Caveat: no hazard injection and no tool-noise.

### When Should a VLM Look? (2609.22910) - full text read
- setup: Qwen2.5-VL-7B cold-start then RL; evaluated on V*, HR-Bench-4K, HR-Bench-8K (perception) plus three general benchmarks; Table 2 reports calls per question, latency (s per question, batch size 1, one NVIDIA H20, vLLM) and spurious-call rate.
- verbatim numbers: "CounterCredit reaches 89.5% on V*, 80.2% on HR-Bench-4K, and 76.4% on HR-Bench-8K, 6.3 to 9.4 points above outcome-only GRPO at 1.78 against 1.84 calls per question, and lowers the spurious-call rate to 31% to 36%"; Table 3 text: "CounterCredit averages 76.1 against 68.9 at 1.78 calls per question against 1.84"; intro: "47% to 84% of the calls made by released visual agents are spurious". Qwen3-VL-8B base "from 75.4 to 80.8 on average".
- how it serves us: the "decision value" (answer-with-look vs answer-immediately) is the same quantity as the project's expected-gain target, and gives a metric (spurious-call rate) for the Pareto plot beyond accuracy-at-budget. Not driving, not candidate-conditioned, single-image crops.

## Additional papers (round 2)

### When and How Severely: Scenario-Specific Safety Envelopes for Driving VLAs
- id: arXiv:2606.14238 | date: 2026-06 | venue: arXiv preprint (OpenAlex also lists a Springer 2026 chapter)
- authors: Priyadershi, Abhinaw et al. | code: none seen
- relevance: MED — follow-up to Lost in Fog; safety envelope per scenario type under pixel noise.
- what: Alpamayo R1 on 15,968 (clip, attack) pairs; aggregate safe threshold sigma <= 50 under a 15% ADE budget hides scenarios tolerating sigma = 70; a Gaussian mixture finds six severity bands.
- thesis use: per-scenario-type noise tolerance supports hazard-specific tool-noise levels; relevant to the future calibration phase.
- verified: abs meta fetched

### Towards Safer Mobile Agents: Scalable Generation and Evaluation of Diverse Scenarios for VLMs (HazardForge / MovSafeBench)
- id: arXiv:2601.08470 | date: 2026-01 | venue: arXiv preprint (Springer chapter 2026 per OpenAlex); cites MetaVQA
- authors: Taniguchi, Takara et al. | code: none seen
- relevance: MED — hazard benchmark with distant and intruding objects.
- what: Image-editing pipeline to synthesize hazards; MovSafeBench is an MCQ benchmark with 7,254 images over 13 object categories, normal and anomalous objects. Built on DriveBench and SA-Bench (per search summary; four scenario types motion/intrusion/distance/static also from the summary, UNVERIFIED).
- thesis use: image-edited hazards for the VLM-feature part; the "distance" scenario type matches distance ambiguity.
- verified: abs meta fetched

### Budget-Constrained Embodied Perception (ASP)
- id: arXiv:2608.22975 | date: 2026-08 | venue: arXiv preprint
- authors: Lin, Defu et al. | code: none seen
- relevance: MED — query-conditioned budget allocation under a fixed per-decision token budget; not driving; synthetic SEW-Bench only (authors say natural-video benchmarks were not run).
- thesis use: related work on budget-allocated perception; accuracy-vs-budget framing.
- verified: abs meta fetched

### AdaTurn: Budget-Aware Test-Time Scaling for Active Visual Perception Agents
- id: arXiv:2607.14547 | date: 2026-07 | venue: arXiv preprint
- authors: Liang, Susan et al. | code: none seen
- relevance: LOW-MED — conditions an active-perception agent on a turn budget; image tasks. Accuracy-vs-turn-budget curves.
- verified: abs meta fetched

### ESI-Bench: Towards Embodied Spatial Intelligence that Closes the Perception-Action Loop
- id: arXiv:2605.18746 | date: 2026-05 | venue: arXiv preprint
- authors: Hong, Yining et al. | code: none seen
- relevance: LOW-MED — OmniGibson benchmark where agents choose perception/locomotion/manipulation to uncover occluded structure; step-budget sweep reported in a search summary (5 to 50 steps), UNVERIFIED in the paper.
- thesis use: embodied example of accuracy vs. number of acting/perceiving steps.
- verified: abs meta fetched

### Budget-Aware Tool Use Enables Effective Agent Scaling
- id: arXiv:2511.17006 | date: 2025-11 | venue: arXiv preprint
- authors: Liu, Tengxiao et al. | code: none seen
- relevance: LOW — web-search agents; shows more tool-call budget alone does not help without budget awareness; unified cost metric of tokens plus tool calls.
- verified: abs meta fetched

### OmniTraffic: A Controllable Generation Pipeline and Benchmark for Spatio-Temporal Traffic Reasoning
- id: arXiv:2606.15749 | date: 2026-06 | venue: arXiv preprint
- authors: Wang, Maonan et al. | code: none seen
- relevance: LOW-MED — 12 real intersections as editable 3D environments, VQA including signal-phase semantics; controllable generation.
- thesis use: traffic-signal VQA source; infrastructure view, not ego camera.
- verified: abs meta fetched

### Reasoning models do not yet follow their reasoning in autonomous driving: The KITScenes LongTail Dataset
- id: arXiv:2603.23607 | date: 2026-03 | venue: arXiv preprint (CVPR 2026 workshop challenge per search summary)
- authors: Wagner, Royden et al. | code: https://hf.co/datasets/kit-mrt/kitscenes-longtail
- relevance: LOW-MED — rare scenarios with a reasoning-action coherence measure; extracting actions from the reasoning trace "typically improves motion planning".
- thesis use: a caution for the VLM-chooses-tool prompt: stated and executed choices may disagree.
- verified: abs meta fetched

### DrivingBench: Can Vision-Language Models Drive a Toyota Corolla?
- id: arXiv:2609.38948 | date: 2026-09 | venue: arXiv preprint
- authors: Ramabadran, Aditya et al. | code: none seen
- relevance: LOW — real car, three tools, inference latency part of the task. The lone driving benchmark I found where tool/latency cost matters, but it is a parking-lot cone course, not hazard evaluation.
- verified: abs meta fetched

### Mapillary Vistas Validation for Fine-Grained Traffic Signs
- id: arXiv:2508.02047 | date: 2025-08 | venue: arXiv preprint
- authors: Garg, Sparsh et al. | code: none seen
- relevance: LOW — traffic signs (not lights); DINOv2 beats the VLM baselines. Included only because no light-specific benchmark exists.
- verified: abs meta fetched

### CoReVLA / DriveFine / DriveVLA-M0 / HERMES
- ids: arXiv:2509.15968 (2025-09), 2602.14577 (2026-02), 2608.10413 (2026-08), 2602.00993 (2026-02) | relevance: LOW — planners reported on long-tail or NAVSIM v2; abstracts fetched, no tool or query selection. Not read further.
- verified: abs meta fetched

## Search results (round 2)
- Occluded/ambiguous traffic lights: still no dataset or benchmark targeting occluded or ambiguous lights for VLMs after two extended searches. Adjacent: DriveAction (2506.05667), 2608.18035, OmniTraffic, signs only (2508.02047). The injected light hazard is therefore a gap rather than a reuse.
- MetaDrive/ScenarioNet from 2025-07: no new 2025-07+ VLM or planning evaluation in MetaDrive found by search. OpenAlex cited-by for MetaVQA since 2025-07 returned only 7 works, none a MetaDrive planner (nearest: HazardForge 2601.08470, FAST-EQA, SceneReasoner, a Springer object-centric prompting chapter). Bench2ADVLM and Bench2Drive-VL use CARLA.
- Accuracy vs. number of calls in embodied settings: AdaTurn (turn budgets), ASP (token budget), ESI-Bench (step budget), 2511.17006 (tool-call budget, web). None driving, none candidate-conditioned.
- OpenAlex cited-by for DriveBench since 2025-07: 37 works; relevant titles: "Evaluating the Perceptual Robustness of VLMs for Autonomous Driving in Corner Cases" (IV 2026), "RADBench: Evaluating Foundation VLMs for Corner Case Description" (IV 2026), "Are Vision LLMs Road-Ready?" (KDD 2025), "How well do video-language models understand traffic risk?" (2026-11). The first two I could not find on arXiv and have not entered (UNVERIFIED, dropped).

## Summary (updated, replaces the first Summary)
- No close overlap found after a second pass. No benchmark or paper in this sub-area conditions a perception-query choice on a candidate trajectory set for driving.
- Nearest idea: "What's Hidden Matters" (2607.00283). Full text read: PKL ranks which hidden agent matters to the plan, 1,250 nuScenes windows, PKL selection beats random by about 30% (Qwen-7B 0.405 to 0.543). It is per-agent and offline, not per-candidate and not tool-based. PKL is borrowable as a decision-relevance definition.
- Cost-aware tool calls exist only outside driving: ToolGate (2606.03054), CounterCredit (2609.22910, spurious-call rate 31-36% best vs 47-84% for released agents), AdaTurn, ASP, ESI-Bench. CounterCredit's "decision value" equals the project's expected-gain target in spirit.
- Correction: DriveBench (2501.04003) contains no agentic tool-use method in its arXiv HTML; my earlier RAU claim is withdrawn. Its useful content is the 15-type corruption list and the finding that VLM accuracy barely drops even with no image, which argues for a no-image control in the VLM-feature experiment.
- Real-data evaluation with candidates: WOD-E2E (2510.26125) gives up to 12 sampled candidates, 3 human-rated, scored by RFS. It is the best analogue of K candidates plus oracle best, usable as a sim-to-real check.
- Corruption recipes for the three tool-noise levels: DriveBench, RoboDriveBench (2512.01300), Lost in Fog (2605.21446) and its follow-up (2606.14238, per-scenario noise tolerance).
- Closed-loop options after MetaDrive: Bench2Drive-VL (2604.01259) and Bench2ADVLM (2508.02028), both CARLA; NAVSIM v2 pseudo-simulation (2506.04218). No 2025-07+ VLM work found in MetaDrive besides the MetaVQA line (2501.09167).
- Occluded or ambiguous traffic-light benchmarks: none found. The project's hazard injection fills a real gap.

## Leads not followed (updated)
- Not found on arXiv, dropped: IV 2026 papers "Evaluating the Perceptual Robustness of VLMs ... Corner Cases" and "RADBench"; NeurIPS 2026 "Evaluating the Readiness of VLMs for Real-World Autonomous Driving Tasks" (neurips.cc page only, no id); a "VLM driving RAU" claim.
- Not read in full: Bench2Drive-VL, Bench2ADVLM numbers, NAVSIM v2 EPDMS definitions (only abstract and search summary), RoboDriveBench tables, nuReasoning, DriveAction.
- WOD-E2E challenge top entries (HMVLM, Poutine, AutoVLA are named in Sec. 4.4) not looked up.
- Not run: OpenAlex cited-by for Lost in Fog, WOD-E2E, Bench2Drive-VL, DriveAgent-R1.
