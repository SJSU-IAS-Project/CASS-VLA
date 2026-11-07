# A_driving_tool_agents (written 2026-11-06)

## Summary
- No close overlap found. After ~12 searches plus OpenAlex cited-by lists, I found no driving paper that conditions a perception-tool call on the candidate trajectory set or action set. All tool-calling driving agents I found (DriveAgent-R1, AgentThink, OmniDrive-R1, MTRDrive, Drive by Hindsight and Foresight) decide on tool use from the scene or question, in a VQA or high-level-behavior setting. This supports the project's novelty claim, but the search is not exhaustive (OpenAlex cited-by coverage is thin: DriveAgent-R1 shows only 4 citers, none of them follow-ups).
- The tool-using driving agents cluster on DriveLMM-o1 (a VQA/MCQ reasoning benchmark): AgentThink (EMNLP Findings 2025), OmniDrive-R1 (CVPR Workshops 2026 per OpenAlex), MTRDrive, Drive by Hindsight and Foresight (2609.08217, MCQ 79.09). None reports accuracy vs. query budget. DriveAgent-R1 is the only one with an explicit per-call cost (tool-usage reward, C_tool = 0.125, verified in the v3 HTML) and a latency comparison.
- Trend: a counter-current of "internalize the tools" (CritiqueDriveVLM 2607.04179 uses a tool-free teacher and distils away tool latency; OmniDrive-R1 replaces external tool calls with a self-grounding zoom reward). This is an argument that fixed tool-call overhead matters, and supports a budget-aware framing.
- Outside driving, the "when to look" RL literature is active and directly borrowable: CounterCredit (2609.22910: reward only calls that were needed AND used; spurious call rates 36-87%), NTEP-R (2609.03493), AdaptVision (2512.03794), VLM-R3 (2505.16192). Their "needed" test (compare the realized branch against answering immediately) is essentially an expected-gain label, close to the project's expected-gain targets. Idea to borrow for labels and for a "spurious call rate" metric.
- Closest on the candidate-set side: Slow Brain, Fast Planner (2606.20458; VLM picks a candidate index from a planner's proposal set; no tools), Deferred Exposure/AD-MCQ (2608.01755; planning as selection among explicit candidates), SimpleVSF (2510.17191; VLM scoring over candidates). These show candidate-conditioned VLM choice but do not choose a perception query.
- Occlusion angle: "What's Hidden Matters" (2607.00283) ranks occluded agents by Planning KL-divergence, i.e. effect on the plan. This is a plan-conditioned relevance measure and a natural source of hazard-relevance ground truth or a feature. Related to, but not, query selection.
- Budgeted-trigger analogues in other domains: TUD (2610.05025; uncertainty from action re-predictions decides when to call a generalist VLA module, accuracy vs. call budget curve), VLMPlanner CAI-Gate (2507.20342; scene-complexity gate), VOILA (2602.03007; value-of-information fidelity selection). All are trajectory-agnostic or question-only triggers, same family as the scene-uncertainty baseline.
- Counterfactual VLA (CF-VLA) and ELF-VLA were fetched only for metadata; neither calls perception tools. CF-VLA's counterfactual reasoning is conditioned on the model's own planned meta-actions, so is the nearest "action-conditioned look" idea, but it is internal reasoning, not a perception query.
- UPDATE (second pass, full-text read of 2609.08217, 2512.14044, 2509.20843, 2610.05025). In all four, the tool trigger is a learned policy decision from scene, question and (for two) retrieved memory; none of the driving ones sees a candidate trajectory set. Per-call cost or budget curves are reported only by DriveAgent-R1 (C_tool, latency table) and TUD (calls vs success curve); 2609.08217 reports usage statistics but no budget curve. Details in the "Second-pass details" blocks below.
- UPDATE: the closest mechanism to the project's idea is dispersion of sampled or re-predicted plans gating an expensive call: UDAV (2609.16368; spread of K stochastic VLM trajectories triggers a second planning pass, off-road UAV/UGV) and TUD (2610.05025; dispersion of action re-predictions, manipulation). Both gate on the model's own sampled action disagreement, not on a fixed candidate set and not on choosing which perception tool, so the project's "which tool, given how the candidates diverge" is still not covered. UPS (2602.22474) maps VLM-verifier uncertainty over sampled actions (conformal set size) to act/ask/intervene, a neighbouring accept/inspect/fallback policy.
- UPDATE: the survey 2609.01659 lists only AgentThink and Prompts2Pavement as "tool-mediated" in its taxonomy (MTRDrive is filed under retrieval/knowledge). Mining it yielded no further tool-using driving agents; it states "adaptive reasoning budget" and "trigger reliability" as open challenges, which supports the gap.

## Papers

### Drive by Hindsight and Foresight: Tool-Grounded Synergistic Reasoning over Hierarchical Memory for Autonomous Driving
- id: arXiv:2609.08217 | date: 2026-09 | venue: arXiv preprint
- authors: Chen, Baojie et al. | code: none seen
- relevance: HIGH — newest DriveAgent-R1-style competitor: proactive adaptive tool invocation driven by scene state plus retrieved experience.
- what: Couples a hierarchical driving memory (short-term scene state, long-term experience incl. tool strategies) with proactive tool calls in a closed reasoning loop; SFT then GRPO on multi-step teacher rollouts. Reports 80.03 overall reasoning score and 79.09% MCQ on DriveLMM-o1 for a 7B model (abstract).
- thesis use: competitor / related work; the trigger is scene-and-memory-conditioned, not candidate-conditioned. Not read beyond abstract.
- verified: abs meta fetched

### AgentThink: A Unified Framework for Tool-Augmented Chain-of-Thought Reasoning in Vision-Language Models for Autonomous Driving
- id: arXiv:2505.15298 | date: 2025-05 | venue: Findings of EMNLP 2025 (from search result; not checked on the abs page)
- authors: Qian, Kangan et al. | code: https://github.com/curryqka/AgentThink
- relevance: HIGH — the driving tool-library baseline (visual, detection, prediction, occupancy, mapping tools); older than the 2025-07 window but essential and not in known_papers.
- what: Builds a driving tool library, generates self-verified tool-using reasoning data, trains SFT then GRPO for autonomous tool invocation, and adds a multi-tool usage evaluation protocol. On DriveLMM-o1 it reports +53.91% reasoning score and +33.54% answer accuracy (abstract).
- thesis use: baseline family / tool-set reference; its tool-use evaluation protocol could be borrowed. Trajectory-agnostic.
- verified: abs meta fetched

### OmniDrive-R1: Reinforcement-driven Interleaved Multi-modal Chain-of-Thought for Trustworthy Vision-Language Autonomous Driving
- id: arXiv:2512.14044 | date: 2025-12 | venue: CVPR Workshops 2026 (OpenAlex DOI 10.1109/cvprf71909.2026.00111; not confirmed on a venue page)
- authors: Zhang, Zhenguo et al. | code: none seen
- relevance: HIGH — "thinking with images" for driving: the model chooses between text reasoning, zoom-in on a region, or answering.
- what: Interleaved multimodal CoT with a zoom action; two-stage RL with Clip-GRPO, an annotation-free grounding reward that avoids external tool-call instability. On DriveLMM-o1, Qwen2.5-VL-7B goes 51.77 -> 80.35 reasoning score and 37.81 -> 73.62 answer accuracy (abstract). Future work lists lane and depth tools (from a search summary, not verified).
- thesis use: competitor for the ROI tool; evidence that zoom helps VQA-style driving. No planning, no budget curve.
- verified: abs meta fetched

### MTRDrive: Memory-Tool Synergistic Reasoning for Robust Autonomous Driving in Corner Cases
- id: arXiv:2509.20843 | date: 2025-09 | venue: arXiv preprint
- authors: Luo, Ziang et al. | code: none seen
- relevance: HIGH — memory plus dynamic toolkit for a 3B driving VLM, evaluated on NAVSIM (planning) and a roadwork corner-case benchmark.
- what: Closed loop of experience retrieval and dynamic toolkits; reports PDMS 88.3 on NAVSIM without CoT, driving metric 79.8%, planning accuracy 82.6%, and 80.2% zero-shot on the new Roadwork-VLM benchmark (abstract).
- thesis use: competitor; the only tool-using driving VLM here with a planning benchmark (NAVSIM). Roadwork-VLM is a possible hazard benchmark. Cited by the 2609.08217 line of work (that paper is its successor by theme; not confirmed same authors).
- verified: abs meta fetched

### DriveAgent-R1 (anchor; v3 details)
- id: arXiv:2507.20879 | date: 2025-07 | venue: ICLR 2026 (per search results)
- authors: Zheng, Weicheng et al. | code: none seen
- relevance: HIGH — the anchor/baseline. Facts verified from the v3 HTML: the final RL stage adds a tool-usage reward with a per-call cost C_tool = 0.25/2 = 0.125 (a 0.25 accuracy gain amortized over an expected median of 2 calls); tool-mode trajectories are rewarded relative to the mean of text-only trajectories. Output is high-level behavior (meta-actions), not a candidate set.
- what: see the abstract (tools: RoI inspection, depth estimation, 3D detection; adaptive switch between text-only and tool reasoning on Drive-Internal and nuScenes).
- thesis use: baseline. Its trigger is scene complexity learned by RL and has no candidate-set input. A latency comparison of 7.91 s vs 6.74 s (always-tool vs adaptive) appeared only in a search summary: UNVERIFIED.
- verified: abs meta fetched, html read (partial)

### When Should a VLM Look? Paying Only for Visual Calls That Were Needed and Used
- id: arXiv:2609.22910 | date: 2026-09 | venue: arXiv preprint
- authors: Peng, Kunyu et al. | code: none seen
- relevance: HIGH (method) — decision value ("realized visual branch vs answering immediately") plus evidence value ("crop vs random same-size patches") per call, i.e. a counterfactual value-of-call label.
- what: CounterCredit pays only calls that were both needed and used. Only 10-12% of calls on the cold-start checkpoint were needed and used, and released agents make spurious calls 36-87% of the time. Reaches 89.5% V*, 80.2% HR-Bench-4K, 76.4% HR-Bench-8K, +6.3 to 9.4 over outcome GRPO at 1.78 vs 1.84 calls per question (abstract). Not driving.
- thesis use: idea to borrow (expected-gain label, spurious-call metric). Supports the project's finding that the VLM's tool choice is poor.
- verified: abs meta fetched

### Slow Brain, Fast Planner: Latency-Resilient VLM-Augmented Urban Navigation
- id: arXiv:2606.20458 | date: 2026-06 | venue: arXiv preprint
- authors: Peng, Zhenghao "Mark" et al. | code: none seen
- relevance: MED-HIGH — VLM selects an index from a planner's candidate-trajectory set (the "trajectory scoring gap"); same first author as Counterfactual VLA.
- what: Sidewalk robot navigation. A VLM picks a candidate and a latency-resilient score fusion turns the stale choice into real-time planner scoring. On about 2,000 hard real-world scenarios, VLM selection gives 30% ADE reduction vs. the planner's selection; in simulation success stays above 80% with up to 5 s delay (abstract).
- thesis use: related work for the candidate-set ranker side; no perception tools, so not an overlap on the selector.
- verified: abs meta fetched

### Deferred Exposure of Future Trajectories for Verifiable Reasoning in Autonomous Driving VLMs
- id: arXiv:2608.01755 | date: 2026-08 | venue: arXiv preprint
- authors: Huang, Zixuan et al. | code: none seen
- relevance: MED — AD-MCQ casts planning as multiple-choice over explicit trajectory candidates, with RLVR (DEFT-RLVR).
- what: Shows teacher CoT anchored on the revealed GT trajectory is less faithful; reveals candidates only after the first-turn plan commitment (details from the abstract and a search summary).
- thesis use: benchmark-format idea (candidate MCQ with verifiable answer) for the ranker or for prompting a VLM.
- verified: abs meta fetched

### What's Hidden Matters: Identifying Planning-Critical Occluded Agents using Vision-Language Models
- id: arXiv:2607.00283 | date: 2026-07 | venue: arXiv preprint
- authors: Chahe, Amirhosein et al. | code: none seen
- relevance: MED — ranks occluded agents by Planning KL-divergence (effect on the ego plan); builds a nuScenes benchmark.
- what: PKL-guided annotation with GPT-5, fine-tuning VLMs; PKL-guided data selection gives about +30% over random sampling (abstract).
- thesis use: idea to borrow (plan-conditioned relevance of hidden objects as ground truth or feature for the occlusion hazard). Not query selection.
- verified: abs meta fetched

### CritiqueDriveVLM: From Verifier-Guided Reinforcement Learning to Latent Thought Distillation for Autonomous Driving
- id: arXiv:2607.04179 | date: 2026-07 | venue: arXiv preprint (OpenAlex also lists a Springer chapter)
- authors: Liu, Zhaohong et al. | code: none seen
- relevance: MED — argues tool-augmented frameworks cost too many tokens and too much latency, and internalizes reasoning instead.
- what: Critique-driven multi-turn RL gives a tool-free teacher (MCQ 55.54 -> 76.54 on DriveLMM-o1), then latent-thought distillation to a fast student (abstract; latency figures not checked).
- thesis use: contrast (motivates why a call budget matters; tool-free alternative to the always-on baseline).
- verified: abs meta fetched

### Triggering Generalist Reasoning via Predictive Uncertainty for Dual-System VLA (TUD)
- id: arXiv:2610.05025 | date: 2026-10 | venue: arXiv preprint
- authors: Yang, Hyemin et al. | code: none seen
- relevance: MED — when to call a slow module, scored on success vs. call budget with an operating curve by threshold.
- what: Uses cross-step dispersion of action re-predictions as an uncertainty trigger; on VLA-Arena it beats uncertainty baselines at matched call budgets (abstract). Manipulation, not driving.
- thesis use: closest budget-curve evaluation precedent; note its trigger is derived from the action plan's variation, which is a form of action-conditioned trigger (a partial analogue of candidate divergence, worth reading).
- verified: abs meta fetched

### VLM-R3: Region Recognition, Reasoning, and Refinement for Enhanced Multimodal Chain-of-Thought
- id: arXiv:2505.16192 | date: 2025-05 | venue: arXiv preprint
- authors: Jiang, Chaoya et al. | code: none seen
- relevance: MED — general model that decides when and where to crop (R-GRPO).
- what: Rewards region selection, crop/zoom transformation, and use of the crop in later reasoning; gains on MathVista, ScienceQA (abstract). Not driving.
- thesis use: background for the ROI tool.
- verified: abs meta fetched

### AdaptVision: Efficient Vision-Language Models via Adaptive Visual Acquisition
- id: arXiv:2512.03794 | date: 2025-12 | venue: arXiv preprint
- authors: Lin, Zichuan et al. | code: none seen
- relevance: MED — low-resolution first, bounding-box crop tool only when needed; RL balances accuracy and efficiency (DTPO decouples tool learning and accuracy).
- thesis use: idea to borrow (accuracy-vs-visual-tokens trade-off as a budget curve).
- verified: abs meta fetched

### Making Every Tool Call Count: Necessary Tool-Evidence Path Rewards for Agentic Vision-Language Models
- id: arXiv:2609.03493 | date: 2026-09 | venue: arXiv preprint
- authors: Long, Xingming et al. | code: none seen
- relevance: LOW-MED — rewards that each tool call targets needed evidence; addresses redundant or off-target calls.
- thesis use: related work for "tool call quality" metrics.
- verified: abs meta fetched

### Reinforcing VLMs to Use Tools for Detailed Visual Reasoning Under Resource Constraints
- id: arXiv:2506.14821 | date: 2025-06 | venue: arXiv preprint
- authors: Kumar, Sunil et al. | code: none seen
- relevance: LOW — small VLMs trained with GRPO to use a zoom tool. General VQA.
- thesis use: background only.
- verified: abs meta fetched

### VLA-Thinker: Boosting Vision-Language-Action Models through Thinking-with-Image Reasoning
- id: arXiv:2603.14523 | date: 2026-03 | venue: arXiv preprint
- authors: Wang, Chaoyang et al. | code: https://cywang735.github.io/VLA-Thinker/
- relevance: LOW-MED — VLA where perception is an invocable reasoning action; SFT then GRPO; 97.5% on LIBERO (abstract). Manipulation.
- thesis use: robotics counterpart of DriveAgent-R1.
- verified: abs meta fetched

### Explicit Geometric Chain-of-Thought for Vision-Language-Action in Autonomous Driving (GeoCoTDrive)
- id: arXiv:2610.10390 | date: 2026-10 | venue: arXiv preprint
- authors: Gui, Xingtai et al. | code: none seen
- relevance: LOW-MED — grounds decision-critical 2D regions, then retrieves local 3D priors from a geometric foundation model interleaved into context; PlanningGrounding dataset. Always-on, not a selectable tool.
- thesis use: related (planning-relevant region grounding; a possible always-on baseline).
- verified: abs meta fetched

### DrivingAgent: Design and Scheduling Agents for Autonomous Driving Systems
- id: arXiv:2606.12236 | date: 2026-06 | venue: arXiv preprint
- authors: Xia, Zhongyu et al. | code: none seen
- relevance: MED — RL-trained lightweight LLM schedules perception modules in real time (reuse/refresh/skip per module, per the search summary, not abstract) under latency constraints.
- thesis use: related work on module-level scheduling under a budget; the scheduler sees system state, no candidate trajectories (not confirmed beyond the abstract).
- verified: abs meta fetched

### VLMPlanner: Integrating Visual Language Models with Motion Planning
- id: arXiv:2507.20342 | date: 2025-07 | venue: arXiv preprint
- authors: Tang, Zhipeng et al. | code: none seen
- relevance: MED — CAI-Gate adjusts how often the VLM runs by scene complexity (nuPlan).
- thesis use: another scene-complexity trigger baseline.
- verified: abs meta fetched

### SimpleVSF: VLM-Scoring Fusion for Trajectory Prediction of End-to-End Autonomous Driving
- id: arXiv:2510.17191 | date: 2025-10 | venue: arXiv preprint
- authors: Zheng, Peiru et al. | code: none seen
- relevance: MED — VLM-enhanced scorers and a VLM fusioner over candidate trajectories; NAVSIM v2 challenge entry.
- thesis use: ranker-side related work (VLM over a candidate set).
- verified: abs meta fetched

### Counterfactual VLA / ELF-VLA (anchors, metadata only)
- id: arXiv:2512.24426 (CF-VLA, Peng et al.) and arXiv:2603.01063 (ELF-VLA, Luo et al.) | date: 2025-12 / 2026-03 | venue: CVPR 2026 for both (per search results)
- relevance: MED — CF-VLA reasons only in challenging scenes (adaptive thinking) and counterfactually revises its own planned meta-actions; ELF-VLA uses a teacher's diagnostic reports in RL. Neither calls perception tools.
- thesis use: anchors; CF-VLA is the nearest "action-conditioned" gating idea.
- verified: abs meta fetched

### Semantic Misalignment in Vision-Language Models under Perceptual Degradation
- id: arXiv:2601.08355 | date: 2026-01 | venue: arXiv preprint
- authors: Cheng, Guo et al. | code: none seen
- relevance: LOW-MED — moderate segmentation degradation causes hallucination, omission of safety-critical entities and inconsistent safety judgments in VLMs (abstract). Supports the tool-noise levels.
- thesis use: motivation for noisy tools.
- verified: abs meta fetched

### Beyond Textual Chain-of-Thought: A Survey on Action-Grounded Reasoning in Autonomous Driving
- id: arXiv:2609.01659 | date: 2026-08 | venue: arXiv preprint
- authors: Tang, Zhengxu et al. | code: https://github.com/tangzhengxu/awesome-av-cot
- relevance: LOW-MED — survey of 171 papers with an "externalized reasoning" category; use it to find missed tool-using driving papers.
- verified: abs meta fetched

### Second-pass details (full text read)

#### 2609.08217 Drive by Hindsight and Foresight (html read)
- trigger: the policy "identifies the current evidence gap, invokes a driving tool, grounds the observation, and updates the scene belief, looping until it answers" (Sec. 3, Eq. 1: y ~ pi(q, I_t, M_s, E_K, T)). Inputs are question, six-view images, short-term scene memory, top-K retrieved experiences and the tool set. No candidate trajectories or action set in the input.
- tool set: 27 callable functions (visual grounding, metric geometry, object perception, ego state, trajectory forecasting, occupancy, map query); 20 core tools used in experiments (App. A.3).
- cost/budget: at most 7 tool turns plus 1 answer turn (App. implementation); no per-call penalty found. Sec. 4.4 "Online tool behavior" verbatim: "97.4% of queries use one to three tools, with an average of 2.10 calls, while no-tool answering occurs in only 0.5% of cases"; tool success 99.74%. App. E.1: end-to-end latency dominated by LLM decoding (median 34.96 s), tool execution 5.4 ms median.
- headline (Table 1, DriveLMM-o1): overall 80.03, MCQ 79.09 (AgentThink row in same table: 79.68 / 71.35).
- note for the project: almost every query calls tools (99.5%), so the trigger barely discriminates; opposite regime to a budgeted selector.

#### 2512.14044 OmniDrive-R1 (html read)
- trigger: "autonomously decide whether to invoke the tool ... based on the complexity of the scene and the query" (Sec. 3, stage 2); Fig. 2 loop: thought, then optionally Zoom-in tool, up to 5 tool calls per trajectory (Sec. 4.1). Input is image plus question; no action or trajectory input.
- tool set: a single zoom-in tool (bounding box plus class label, crop). The HTML also claims the capability is "purely driven by the base VLM's intrinsic grounding potential, eliminating reliance on any external tools", so the abstract and body disagree on whether the crop is an external tool.
- cost/budget: none beyond the 5-call cap; rewards are accuracy, format and the CLIP-based grounding reward, no per-call penalty found.
- headline (Table 1, DriveLMM-o1): overall 80.35, final answer 73.62 (Qwen2.5-VL-7B base 51.77 / 37.81; AgentThink 79.68 / 71.35). Ablation Table 2: GRPO* without the grounding reward 70.18 / 57.19.
- venue: the arXiv HTML and abs page show no venue or comment line. The only venue evidence is the OpenAlex record (CVPR Workshops 2026, DOI 10.1109/cvprf71909.2026.00111). Keep as OpenAlex-only.

#### 2509.20843 MTRDrive (html read)
- trigger: "experience-driven approach to tool interaction" (Sec. III-B 2): a format reward gives 1.0 if experience is correctly used, 0.5 if correctly omitted, 0 otherwise, so the model learns when to draw on retrieved experience; experience is retrieved with CLIP image embeddings. Input is image plus retrieved experience; no candidate set.
- tool set (Sec. III-B 1): object detection, open-world vocabulary detection and further vision tools (I read only the first two).
- cost/budget: no per-call cost or call-count statistic found.
- headline (Table I): NAVSIM (SFT) planning accuracy 82.6 (3B Qwen2.5-VL base 1.6, 72B 37.8); abstract: PDMS 88.3. Ablation text: base model 1.6% on NAVSIM, SFT 79.9%, GRPO lifts zero-shot ROADWork planning accuracy 13.3% to 17.3%.

#### 2610.05025 TUD (html read)
- trigger: the dispersion (standard deviation) of the specialist's re-predictions of the upcoming action chunk against the cached generalist context; the generalist call is deferred while the running mean dispersion stays below a threshold set by an online percentile p (Sec. 1, Sec. 3). The trigger does see the action plan (it is computed from it) but it is one policy's re-predictions over time, not several candidates.
- tool/module: one generalist VLM call (not perception tools).
- cost/budget: the contribution is the success-vs-VLM-call curve (Fig. 3 "operating curve" as p varies; Table 4 matched call budgets, about 17-18 calls/episode high budget on VLA-Arena L0). Real robot (Table 5): TUD p90 SR 0.833 with 12.1 calls vs single-system pi0 SR 0.433 with 49.0 calls; abstract claims 75% fewer generalist calls than the best fixed-interval baseline.
- baselines compared as triggers: GenUQ, MC-AleaUQ, Diff-DAgger, BayesDiff, AAC-entropy, Visual.
- use for the project: closest published evaluation protocol (accuracy vs call budget with multiple uncertainty triggers as baselines); the project's candidate-divergence features are a driving analogue of its dispersion signal.

### UDAV: Uncertainty-Driven Adaptive VLM Waypoint Planner
- id: arXiv:2609.16368 | date: 2026-09 | venue: arXiv preprint
- authors: Farhani, Ghazal et al. | code: none seen
- relevance: MED-HIGH (mechanism) — draws K stochastic VLM trajectory predictions, takes the medoid, and invokes a reconsideration stage only when the maximum waypoint-wise spatial dispersion exceeds a threshold. This is "gate an expensive call on disagreement among sampled trajectories".
- what: UAV-guided UGV off-road navigation, 400 held-out queries. Mean ADE 147.4 px (deterministic) to 115.9 px (medoid) to 110.4 px (full planner); lowest P90/P95 errors even vs a K=10 consensus baseline (abstract). Not on-road driving, no perception tools.
- thesis use: closest mechanism precedent for conditioning an extra call on trajectory disagreement; cite as related work, and as a possible "trajectory-dispersion trigger" baseline.
- verified: abs meta fetched

### When to Act, Ask, or Learn: Uncertainty-Aware Policy Steering (UPS)
- id: arXiv:2602.22474 | date: 2026-02 | venue: RSS 2026 (from the RSS proceedings listing in search results; not opened)
- authors: Yuan, Jessie et al. | code: none seen
- relevance: MED — a VLM verifier scores sampled low-level action candidates; conformal prediction calibrates a set of acceptable actions, and set size picks act / ask a clarifying question / ask for intervention.
- thesis use: related work for the future conformal accept/inspect/replan/fallback phase; candidate-set based decision with calibrated coverage. Manipulation, not driving.
- verified: abs meta fetched

### Retrieval-Based Interleaved Visual Chain-of-Thought in Real-World Driving Scenarios (RIV-CoT / DrivingVQA)
- id: arXiv:2501.04671 | date: 2025-01 | venue: Findings of EACL 2026 (from search results; UNVERIFIED on the abs page)
- authors: Corbiere, Charles et al. | code: vita-epfl.github.io/DrivingVQA (from search results)
- relevance: LOW-MED — crops of relevant entities interleaved into reasoning on DrivingVQA (3,931 driving-theory MCQs); +3.1% answer accuracy, +4.6% reasoning accuracy over vanilla CoT (abstract). Cited in the survey as a visual-spatial crop method. Predates the window.
- thesis use: background for the ROI tool.
- verified: abs meta fetched

### Resolutions of earlier UNVERIFIED items
- DriveAgent-R1 latency: VERIFIED in the v3 HTML, Sec. 3.7 and Table 8 (Drive-Internal test, single H20, vLLM, batch 1, 100 samples x 5 runs): Passive-SV 8.50 s / 210.77 tokens; tool-only mode 7.91 s / 314.45; adaptive mode 6.74 s / 265.57.
- OmniDrive-R1 venue: NOT resolved from a primary page (arXiv abs/HTML carry no venue). Remains OpenAlex-only (CVPR Workshops 2026).

## Leads not followed
- The awesome-av-cot GitHub list behind survey 2609.01659 (survey text itself mined; it names only AgentThink and Prompts2Pavement as tool-mediated). SenseRAG (2501.03535, proactive querying, Jan 2025) seen but not written up. 2604.01681 (agentic fast-slow planning) and 2601.03519 (OFF-EMMA visual prompt, COT self-consistency) seen in the survey, LOW relevance, not entered.
- OpenReview ICLR 2027 search for driving tool-use submissions (not run).
- The "A Survey on VLA Models for AD" (ICCVW 2025) and 2512.16760 survey lists.
- Google Scholar-style cited-by for AgentThink (OpenAlex gave only 21, mostly surveys); DriveAgent-R1 follow-ups probably not yet indexed.
- S-Agent (2606.20515; spatial tool-use agent with 2D/3D tools, not driving) and EyeVLA (2511.15279; active PTZ viewpoint under a budget) were fetched but not written up as entries; LOW relevance.
- Robotics/aerial "which sensor query under budget" and value-of-information literature (other agents' areas).
