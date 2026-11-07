# D_when_to_query: learning when/which extra information to acquire (non-driving)

Scope note: no paper found here is in driving, and none conditions the query on a set of candidate actions. Search was web search plus arXiv abs metadata (absfetch); only ToolGate got a partial html read. Text-only descriptions of results come from abstracts unless stated.

## Summary (first pass; the updated summary is near the end of this file)
- No close overlap with candidate-conditioned query selection was found in this sub-area. The closest in spirit: ToolGate (2606.03054, execute/skip a proposed VLM tool call, trained on forced-answer proxy labels), BCEA (2606.16667, answer/abstain/acquire-more-visual-evidence under a budget), AdaTooler-V (2512.16918, per-sample "Tool Benefit Score"), VOILA (2602.03007, picks image fidelity by predicted correctness per option and expected utility).
- Strongest support for the project's "prompted VLM says none / is miscalibrated" finding: the Illusion of Visual Tool-Use audit (2608.06270: six models, policy miscalibration, "Calling Without Looking"), ToolGate (helpful vs harmful calls 11.8% vs 9.9%, 78.3% no change; prompting the agent to self-regulate is insufficient), and When2Tool (2605.09252: prompt-only suppresses necessary calls with unnecessary ones; linear probe AUROC 0.89-0.96 beats verbalized reasoning). Direction of error in the literature is mostly OVER-calling (blind tool use); the project's VLM under-calls ("none"). Both are mis-calibration; worth stating in the thesis.
- Learned small head beats prompting is a repeated pattern: When2Tool/Probe&Prefill, Probing-RAG, "Therefore I am. I Think" (2604.01202), ToolGate, Learning How Hard to Think (probe on hidden states). This supports the project's MLP-selector-on-features design. All are text LLMs except ToolGate/AdaTooler-V/BCEA/VOILA (VLM).
- Training targets that are expected gain: closest are AdaTooler-V's Tool Benefit Score (tool vs no-tool accuracy delta per sample), Damani et al. (predict reward distribution per budget), VOILA (predicted correctness per option, then utility rule), Consistent L2D with advice (2603.14324, routing plus which information, with acquisition fees). ToolGate explicitly states that true counterfactual VoI is unavailable from one rollout and uses a proxy; the project's averaging over noise draws is a cleaner estimate of exactly that quantity, which is a point of differentiation.
- "Which source" (not just whether): Consistent L2D with advice (2603.14324) learns which expert and what information, trained with only partial advice observed per record; ESearch-R1 (2512.18571) picks among Ask/GetMemory/Navigate with heterogeneous costs; AFABench (2508.14734) gives the standard benchmark/taxonomy (static, myopic, RL) for acquisition policies. Useful vocabulary: the project's selector is a myopic one-step active feature acquisition policy with abstain.
- Calibrated accept/abstain/acquire for the future phase: BCEA (conformal, three-way action), UPS (2602.22474, conformal choice of act/clarify/intervene), CORA (2604.09155, conformal risk control for execute/abstain), ToolChain-CRC (2606.18467). Good templates for the planned accept/inspect/replan/fallback policy.
- Robot ask-for-help: KnowNo-style conformal sets still the reference; newer work is RL-trained asking (Ask-to-Act 2504.00907, ESearch-R1) and abstention benchmarks (AbstainEQA 2512.04597).
- Tool-overuse RL literature (OTC-PO, EAPO, AutoTool, SMART, MeCo) penalizes call count in the reward; none uses a precomputed per-option expected-gain label. These are weaker baselines than they look for a fixed-budget Pareto setup but are the natural "learned adaptive-calling" competitors in text.

## Papers

### ToolGate: Token-Efficient Pre-Call Control for Tool-Augmented Vision-Language Agents
- id: arXiv:2606.03054 | date: 2026-06 | venue: arXiv preprint
- authors: Liu, Anjie et al. | code: not checked (no link in abstract)
- relevance: HIGH — learned execute/skip controller for VLM perception-tool calls, measured as accuracy vs token cost; closest VLM analogue of a learned query gate.
- what: A ReAct VLM agent proposes a perceptual tool call (OCR, detection, segmentation); a lightweight external controller on trajectory text and structural features (no pixels, no hidden states) predicts execute or skip. Across five benchmarks the baseline's helpful and harmful calls occur at similar rates (11.8% vs 9.9%) and 78.3% of calls leave the forced-answer argmax unchanged (Qwen3-VL-30B, 15,782 labeled calls). ToolGate cuts token cost to 64-69% of unrestricted ReAct at preserved cross-domain accuracy; executed calls fall 2.73 to 1.02 per episode. Labels are a proxy built from forced-answer probes before/after the call; the paper says it does not estimate true counterfactual VoI.
- thesis use: related work and idea to borrow (proxy label vs your noise-averaged expected gain; "prompting to self-regulate is insufficient" supports your prompted-VLM result). Does not choose among tools nor condition on candidate actions.
- verified: abs meta fetched / html partly read (grep of text)

### LLM Agents Already Know When to Call Tools -- Even Without Reasoning (When2Tool, Probe&Prefill)
- id: arXiv:2605.09252 | date: 2026-05 | venue: arXiv preprint (NeurIPS 2026 poster page seen in search, not on arXiv abs)
- authors: Sun, Chung-En et al. | code: github.com/Trustworthy-ML-Lab/when2tool (link in the paper text, Sec. 1)
- relevance: HIGH — direct evidence that a linear probe beats prompted/verbalized tool decisions.
- what: Benchmark of 18 environments with controlled tool-necessity boundaries. Prompt-only baselines suppress necessary calls along with unnecessary ones; Reason-then-Act costs accuracy on hard tasks. Tool necessity is linearly decodable from pre-generation hidden states with AUROC 0.89-0.96 across six models; Probe&Prefill reduces tool calls by 38% with 1.7% accuracy loss (abstract and Sec. 1; a 48% figure in a search snippet was wrong; Sec. 1 also reports up to 56% fewer API calls on Search-o1 without accuracy loss).
- thesis use: supports learned head over prompting; text-only, so cite as the LLM analogue of the project's VLM result.
- verified: abs meta fetched

### The Illusion of Visual Tool-Use: A Causal Audit of Thinking with Images
- id: arXiv:2608.06270 | date: 2026-08 | venue: EMNLP 2026 Findings (venue from a search listing only; not on the arXiv abs page)
- authors: Wang, Zhiheng et al. | code: github.com/OpenCausaLab/CauAudit
- relevance: HIGH — evidence that VLM visual-tool policies are mis-called, plus a step-level "Visual Evidence Gain" estimand (counterfactual replacement of one observation).
- what: Audits six models on five fine-grained perception benchmarks at policy, trajectory, and step level. Finds "Calling Without Looking" (observations have no causal effect) and "Looking Without Planning" (informative observations, incoherent call schedule); accuracy gain concentrated in a calibrated minority.
- thesis use: motivates learned selection; Visual Evidence Gain is a per-observation counterfactual gain similar in spirit to your expected-gain target.
- verified: abs meta fetched

### Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Model (BCEA)
- id: arXiv:2606.16667 | date: 2026-06 | venue: arXiv preprint
- authors: Xu, Jian et al. | code: not checked (no link in abstract)
- relevance: HIGH — three-way answer/abstain/acquire-more-visual-evidence (zoom, crop) with conformal risk control under a bounded budget.
- what: A conformal claim filter must abstain on over 80% of claims to hold hallucination below 5% on a balanced object-existence benchmark; BCEA lets the model instead re-examine the image under a bounded budget. The abstract I could retrieve cut off before the headline result.
- thesis use: template for the future accept/inspect/fallback phase; competitor for the "calibrated query" story.
- verified: abs meta fetched (abstract truncated by the fetch)

### AdaTooler-V: Adaptive Tool-Use for Images and Videos
- id: arXiv:2512.16918 | date: 2025-12 | venue: ACL Findings 2026 (venue from a search listing only; not on the arXiv abs page)
- authors: Wang, Chaoyang et al. | code: released (URL not checked)
- relevance: MED-HIGH — per-sample Tool Benefit Score as an RL reward scale: closest published "gain of using the tool" training signal in a VLM.
- what: Argues open MLLMs call vision tools even when unnecessary, hurting efficiency and accuracy. AT-GRPO scales rewards by each sample's Tool Benefit Score; AdaTooler-V-7B reaches 89.8% on V*.
- thesis use: related work; contrast with a supervised, noise-averaged expected-gain label.
- verified: abs meta fetched

### Are Tools Always Beneficial? Learning to Invoke Tools Adaptively for Dual-Mode Multimodal LLM Reasoning (AutoTool)
- id: arXiv:2605.19852 | date: 2026-05 | venue: ICML 2026 (venue from a search listing only)
- authors: Ma, Qinghe et al. | code: github.com/MQinghe/AutoTool (per search page)
- relevance: MED — RL for tool-on/tool-off modes in a MLLM; reports the policy drifts toward tool-off.
- what: Dual-mode reasoning with mode-specific rewards (MSPO) and mode balancing; 21.8% accuracy gain on V* over base and 44.9% efficiency gain on POPE vs tool-augmented methods.
- thesis use: related work on whether-to-call; the tool-off bias is parallel to the project's VLM saying "none".
- verified: abs meta fetched

### VOILA: Value-of-Information Guided Fidelity Selection for Cost-Aware Multimodal Question Answering
- id: arXiv:2602.03007 | date: 2026-02 | venue: arXiv preprint
- authors: Bhope, Rahul Atul et al. | code: not checked (no link in abstract)
- relevance: MED-HIGH — learned predictor of correctness per option plus a VoI utility rule selecting which option to buy.
- what: Gradient-boosted regressor predicts correctness at each fidelity from question features, isotonic calibration, then picks the minimum-cost fidelity maximizing expected utility. Five datasets, six VLMs: 50-60% cost reduction at 90-95% of full-resolution accuracy.
- thesis use: very close in recipe to the MLP selector on expected-gain targets (predict per-option correctness, select under cost); cite as precedent.
- verified: abs meta fetched

### Consistent Learning-to-Defer with Expert-Conditional Advice
- id: arXiv:2603.14324 | date: 2026-03 | venue: arXiv preprint
- authors: Montreuil, Yannis et al. | code: not checked (no link in abstract)
- relevance: MED-HIGH — learns both which expert handles an input and which information they receive, with acquisition fees; handles training data where only a subset of advice is observed.
- what: Proposes reference conditional classification with consistency bounds; on FEVER and Sensitive, full training has lowest dev loss at every fee and limited training helps at most matched budgets.
- thesis use: theory for "which query + cost" selectors and for training with partially observed tool outcomes.
- verified: abs meta fetched

### Why Ask One When You Can Ask k? Learning-to-Defer to the Top-k Experts
- id: arXiv:2504.12988 | date: 2025-04 | venue: arXiv preprint (v4 Oct 2025)
- authors: Montreuil, Yannis et al. | code: not checked (no link in abstract)
- relevance: MED — consistent surrogate for deferral to k cost-effective experts, adaptive k(x).
- what: Unifies one/two-stage L2D, selective prediction, cascades; accuracy-cost improvements on classification and regression.
- thesis use: formal framing of the budget Pareto curve; the adaptive k(x) is a per-input budget.
- verified: abs meta fetched

### Budgeted Multiple-Expert Deferral
- id: arXiv:2510.26706 | date: 2025-10 | venue: arXiv preprint
- authors: DeSalvo, Giulia et al. | code: not checked (no link in abstract)
- relevance: MED — deciding which experts to query during training to cut label cost; relevant if tool-outcome labels (your simulator calls) become expensive.
- what: Two-stage and single-stage algorithms query a subset of experts per training example, with generalization bounds.
- thesis use: idea for cheaper label generation (query only some tools per scenario).
- verified: abs meta fetched

### AFABench: A Generic Framework for Benchmarking Active Feature Acquisition
- id: arXiv:2508.14734 | date: 2025-08 | venue: arXiv preprint (a listing says 2026 proceedings)
- authors: Schütz, Valter et al. | code: GitHub AFA-Benchmark (from a search result)
- relevance: MED — benchmark and taxonomy (static, myopic, RL) for cost-sensitive acquisition; includes CUBE-NM to expose myopic failures.
- what: Standard evaluation of AFA policies on synthetic and real datasets.
- thesis use: vocabulary and baselines (the project's one-step selector is myopic AFA); note the lookahead limitation for multi-tool phases.
- verified: abs meta fetched

### Towards Cost Sensitive Decision Making (Active-Acquisition POMDP)
- id: arXiv:2410.03892 | date: 2024-10 | venue: AISTATS 2025
- authors: Li, Yang et al. | code: not checked (no link in abstract)
- relevance: MED — RL agent decides whether to acquire features at a cost; older but essential and with AISTATS 2025 publication.
- what: AA-POMDP with a deep generative model imputing unobserved features as belief.
- thesis use: formal model of "acquire vs act".
- verified: abs meta fetched

### When to Act, Ask, or Learn: Uncertainty-Aware Policy Steering (UPS)
- id: arXiv:2602.22474 | date: 2026-02 | venue: arXiv preprint
- authors: Yuan, Jessie et al. | code: not checked (no link in abstract)
- relevance: MED-HIGH — a VLM verifier scores low-level action candidates sampled from a base policy; conformal prediction selects execute / clarify / ask for intervention. Candidate-set verification plus calibrated routing.
- what: Calibrates VLM and policy jointly with statistical assurances; residual learning from collected interventions.
- thesis use: closest robotics analogue of "candidate set + conformal + choose resolution action"; template for the future phase.
- verified: abs meta fetched

### CORA: Conformal Risk-Controlled Agents for Safeguarded Mobile GUI Automation
- id: arXiv:2604.09155 | date: 2026-04 | venue: arXiv preprint
- authors: Feng, Yushi et al. | code: not checked (no link in abstract)
- relevance: MED — Guardian model estimates action-conditional risk per proposed step; conformal risk control sets execute/abstain boundary; rejected actions routed to a Diagnostician (confirm, reflect, abort).
- what: VLM GUI agent safeguard with user-specified risk budget.
- thesis use: pattern for accept/inspect/fallback with CRC.
- verified: abs meta fetched

### ToolChain-CRC: Conformal Risk Control for Agentic AI Under Retrieval and Tool-Use Drift
- id: arXiv:2606.18467 | date: 2026-06 | venue: arXiv preprint
- authors: Opoku, Jeffery et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — trajectory-level accept-or-intervene rule with anytime alarm; text agents.
- what: Step-level risk scores combined into trajectory risk; coverage proofs under exchangeability with a drift extension.
- thesis use: CRC citation for multi-step extension.
- verified: abs meta fetched

### Therefore I am. I Think
- id: arXiv:2604.01202 | date: 2026-04 | venue: arXiv preprint
- authors: Esakkiraja, Esakkivel et al. | code: not checked (no link in abstract)
- relevance: MED — linear probe decodes tool-calling decisions from pre-generation activations; steering flips behavior in 7-79% of examples depending on model/benchmark.
- what: Argues the decision is encoded before reasoning; CoT often rationalizes.
- thesis use: supports probing over prompting.
- verified: abs meta fetched

### Probing-RAG: Self-Probing to Guide Language Models in Selective Document Retrieval
- id: arXiv:2410.13339 | date: 2024-10 | venue: arXiv preprint (v2 in 2025)
- authors: Baek, Ingeol et al. | code: not checked (no link in abstract)
- relevance: MED — hidden-state prober decides whether another retrieval is needed; fewer redundant retrieval steps on five QA datasets.
- what: Pre-trained prober on intermediate-layer states.
- thesis use: canonical probe-for-retrieval-gating citation.
- verified: abs meta fetched

### Skill-RAG: Failure-State-Aware Retrieval Augmentation via Hidden-State Probing and Skill Routing
- id: arXiv:2604.15771 | date: 2026-04 | venue: arXiv preprint
- authors: Wei, Kai et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — prober gates retrieval; prompt-based router chooses among four retrieval skills including an exit skill.
- what: Strong gains on out-of-distribution datasets over prober-only baselines.
- thesis use: probe gating + typed query choice.
- verified: abs meta fetched

### Learning How Hard to Think: Input-Adaptive Allocation of LM Computation
- id: arXiv:2410.04707 | date: 2024-10 | venue: ICLR 2025 (proceedings.iclr.cc page seen in search)
- authors: Damani, Mehul et al. | code: not checked (no link in abstract)
- relevance: MED — predicts the reward distribution per input and budget with a probe on hidden states, then allocates compute; a direct "expected gain from extra compute" target.
- what: Adaptive best-of-k and routing; up to 50% compute reduction at no quality loss (ICLR abstract per search; not checked in the paper).
- thesis use: closest budgeted-compute analogue to expected-gain targets.
- verified: abs meta fetched (abstract: "reduce computation by up to 50% at no cost to response quality, or improve quality by up to 10% at a fixed computational budget")

### Learning When to Think: Adaptive Reasoning for Test-Time Compute Allocation
- id: arXiv:2608.20256 | date: 2026-08 | venue: arXiv preprint
- authors: Kassenaar, Gijs et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — model picks NoThink/Short/Long as the first token via GRPO; MATH500 0.782 vs 0.796 base, length 4,796 to 2,811 tokens.
- what: Router-free adaptive compute.
- thesis use: related work on budgeted compute.
- verified: abs meta fetched

### Acting Less is Reasoning More! Teaching Model to Act Efficiently (OTC-PO)
- id: arXiv:2504.14870 | date: 2025-04 | venue: arXiv preprint
- authors: Wang, Hongru et al. | code: not checked (no link in abstract)
- relevance: MED — RL reward favoring fewest tool calls among correct trajectories; "tool productivity" metric.
- what: Addresses excessive tool calling ("cognitive offloading").
- thesis use: tool-productivity (correct per call) is an easy extra metric for the Pareto plot.
- verified: abs meta fetched

### Learning When Not to Act: Mitigating Tool Abuse in Agentic Reinforcement Learning (EAPO)
- id: arXiv:2606.02132 | date: 2026-06 | venue: arXiv preprint
- authors: Chen, Liuji et al. | code: not checked (no link in abstract)
- relevance: MED — selective tool use with difficulty-aware shaping; vs GRPO +10.45%/+7.27%/+9.69% average performance and -18.33%/-18.33%/-24.59% tool calls on three models.
- what: Tool-free trajectories in each rollout group.
- thesis use: related work on uniform penalty vs selective use.
- verified: abs meta fetched

### SMART: Self-Aware Agent for Tool Overuse Mitigation
- id: arXiv:2502.11435 | date: 2025-02 | venue: arXiv preprint (venue not on abs page)
- authors: Qian, Cheng et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — SMARTAgent reduces tool use by 24% while improving performance by over 37%.
- what: SMART-ER dataset with step-wise rationales for when tools are needed.
- thesis use: tool-overuse citation.
- verified: abs meta fetched

### Adaptive Tool Use in Large Language Models with Meta-Cognition Trigger (MeCo)
- id: arXiv:2502.12961 | date: 2025-02 | venue: ACL 2025 (per search listing)
- authors: Li, Wenjun et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — training-free metacognitive score from representation space to decide tool calls.
- what: Works across backbones and benchmarks.
- thesis use: representation-based gating precedent.
- verified: abs meta fetched

### DeepEyes: Incentivizing "Thinking with Images" via Reinforcement Learning
- id: arXiv:2505.14362 | date: 2025-05 | venue: arXiv preprint
- authors: Zheng, Ziwei et al. | code: github.com/Visual-Agent/DeepEyes
- relevance: LOW-MED — origin of RL zoom-tool VLM; a search summary said early models were reluctant to zoom; not checked, dropped.
- what: Active perception via grounding as an intrinsic tool.
- thesis use: baseline family for VLM tool calling.
- verified: abs meta fetched

### Adaptive Chain-of-Focus Reasoning via Dynamic Visual Search and Zooming for Efficient VLMs
- id: arXiv:2505.15436 | date: 2025-05 | venue: arXiv preprint
- authors: Zhang, Xintong et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — SFT + RL for adaptive zoom; +5% over existing VLMs on V*. (A search summary's claim of up to 77.8% fewer zoom-ins than DeepEyes was not checked in the paper and is dropped.)
- what: MM-CoF dataset, Qwen2.5-VL fine-tuning.
- thesis use: related work.
- verified: abs meta fetched

### ESearch-R1: Learning Cost-Aware MLLM Agents for Interactive Embodied Search via Reinforcement Learning
- id: arXiv:2512.18571 | date: 2025-12 | venue: arXiv preprint
- authors: Zhou, Weijie et al. | code: not checked (no link in abstract)
- relevance: MED — MLLM learns among Ask / GetMemory / Navigate with heterogeneous costs (HC-GRPO), trading information gain against cost; a "which of several information sources" policy.
- what: Abstract text I retrieved was truncated before the results; the ~50% lower cost figure from a search summary is dropped as unchecked.
- thesis use: idea to borrow for multi-tool cost heterogeneity.
- verified: abs meta fetched (truncated)

### Grounding Multimodal LLMs to Embodied Agents that Ask for Help with Reinforcement Learning (Ask-to-Act)
- id: arXiv:2504.00907 | date: 2025-04 | venue: arXiv preprint
- authors: Ramrakhya, Ram et al. | code: not checked (no link in abstract)
- relevance: MED — RL-trained MLLM that asks minimal clarifying questions under partial observability; compared to GPT-4o zero-shot and SFT.
- what: Online RL with LLM-generated rewards.
- thesis use: evidence that prompted frontier VLMs are weak at when-to-ask.
- verified: abs meta fetched (truncated)

### When Robots Should Say "I Don't Know": Benchmarking Abstention in Embodied Question Answering (AbstainEQA)
- id: arXiv:2512.04597 | date: 2025-12 | venue: arXiv preprint
- authors: Wu, Tao et al. | code: not checked (no link in abstract)
- relevance: LOW-MED — abstention benchmark, 1,636 abstention cases plus 1,636 originals.
- what: Five abstention categories; abstract is cut before the headline model result.
- thesis use: abstain-evaluation precedent.
- verified: abs meta fetched (truncated)

### Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners (KnowNo)
- id: arXiv:2307.01928 | date: 2023-07 | venue: CoRL 2023 (PMLR v229, ren23a; from search listing)
- authors: Ren, Allen Z. et al. | code: https://robot-help.github.io (project page from abstract)
- relevance: MED (older, essential) — conformal prediction set over candidate plans; ask a human when the set is not a singleton.
- what: Verified in the html: the LLM planner is cast as multiple-choice QA over generated candidate options; conformal prediction on next-token likelihoods from a calibration set yields a reduced prediction set; "The LLM is certain if this prediction set is a singleton, and triggers help from a human otherwise." Intro/conclusion: "reducing human help by 10-24% compared to baseline approaches that lack formal assurances". Guarantee assumes the true option is in the set when help is accurate (task-completion level 1-epsilon, with 1-delta=0.99 over calibration sampling). Stated limitation: it does not yet model perception-module uncertainty.
- thesis use: comparison. KnowNo's trigger is candidate-conditioned, like the project's, but it measures the planner's confidence over WHICH candidate is right (output-likelihood ambiguity), asks a human who resolves everything, and has one action ("ask"). The project's selector instead reads how the candidates DIVERGE geometrically, chooses WHICH of several tools to call, and is trained on the measured gain of each tool (noisy outcome), so it can learn that ambiguity is not resolvable by any available tool and abstain. KnowNo's set-size rule is the natural "candidate-ambiguity trigger" baseline for the Pareto plot (call if the ranker's conformal set over K candidates has size > 1), and its coverage guarantee is the template for the future CRC phase.
- verified: abs meta fetched / html read (grep of key sentences)

### Seeing with Partial Certainty: Conformal Prediction for Robotic Scene Recognition
- id: arXiv:2501.04947 | date: 2025-01 | venue: arXiv preprint
- authors: Xu, Yifan et al. | code: not checked (no link in abstract)
- relevance: LOW — KnowNo-style conformal help requests for VLM place recognition (Matterport3D).
- thesis use: minor.
- verified: abs meta fetched

### ActiveVLA: Injecting Active Perception into Vision-Language-Action Models for Precise 3D Robotic Manipulation
- id: arXiv:2601.08325 | date: 2026-01 | venue: CVPR 2026 (venue from a search listing only)
- authors: Liu, Zhenyang et al. | code: none found
- relevance: LOW — active viewpoint/resolution selection in a VLA, coarse-to-fine.
- thesis use: robotics active perception context; no budgeted decision.
- verified: abs meta fetched

### Explicit Abstention Knobs for Predictable Reliability in Video Question Answering
- id: arXiv:2601.00138 | date: 2025-12 | venue: arXiv preprint
- authors: Ortiz, Jorge | code: not checked
- relevance: MED — direct evidence against confidence-triggered ("scene uncertainty") gating: self-reported confidence does not track how much evidence the model has.
- what: NExT-QA with Gemini 2.0 Flash. Thresholding gives smooth control in-distribution: "reducing error rates from 23.6% to 9.4% at 63.7% coverage with well-calibrated predictions (ECE = 0.018)" (html). But "this control is not epistemic": with evidence cut from 18 frames to 6, "median self-reported confidence remains 0.9 in both regimes despite a 3x reduction in visual information".
- thesis use: supports the claim that trajectory-agnostic uncertainty triggers are weak predictors of when a query helps.
- verified: html read (abstract sentences)

## Addendum A: full-text comparison of the six closest papers (html read, text stripped and grepped)

Column key: target = how "the query helps" is labeled; stochastic = whether it is averaged over repeated stochastic runs; input = what the gate sees.

| Paper | Target (verbatim where quoted) | Averaged over stochastic draws? | Gate/selector input | Baselines | Headline |
|---|---|---|---|---|---|
| ToolGate 2606.03054 | Default "execute-positive": call has c_b=0, c_a=1 (forced-answer argmax wrong before, right after) and the episode ends correct. Alternative "tool-useful": same flip, or c_b=c_a=1 and the probability on the ground truth rises by more than 0.1. Paper: "This is a practical proxy ... not a measurement of true counterfactual value of information." | No. One logged rollout per call; Eq. 1 VoI = Pr(correct\|execute) - Pr(correct\|skip) is called "not directly observed in a logged trajectory". | Serialized trajectory text (question, choices, past reasoning, past calls and outputs, pending call) embedded by a frozen sentence encoder plus structural features, then logistic regression. "It does not see image pixels, hidden states ..." | Unrestricted ReAct baseline, "VoI self-report" prompt, "Sparse prompt" (Sec. 6.2, Table 3). | Table 3, Qwen3-VL-30B: Baseline 70.8 acc, 100% tokens, 2.73 calls; VoI self-report 60.0, 126%, 5.88; Sparse prompt 69.8, 99%, 2.40; ToolGate 72.5, 67%, 1.02 (Sec. 6.2). Sec. 1: 11.8% of calls flip wrong to right, 9.9% right to wrong, 78.3% unchanged. |
| BCEA 2606.16667 | No learned target. Gate = pre-fixed borderline band [tau-, tau+] on the base grounding score: "runs the B acquisition views only when the base grounding s falls in the pre-fixed borderline band ... (a label-free, calibration-independent test)". Threshold calibrated by Bonferroni-corrected Clopper-Pearson. | Not applicable (claim-level binary labels; 300 random 50/50 splits for validity). | Base grounding score (likelihood drop when the image is blanked) of one claim. | Abstain-only (No-Acq), naive acquisition, ReCoVERR-style empirical-threshold acquirer, practical (uncertified) BCEA (Sec. 5.3, Table 1). | Abstract: to keep hallucination <5% a conformal filter "must abstain on over 80%"; certified gated BCEA coverage 0.32 vs 0.23 at alpha=0.10 and 0.42 vs 0.28 at alpha>=0.10 (Sec. 5.3, ~2 extra passes per claim); on free-form captions (20.6% hallucinated) certifies 34% of claims at <=10% vs 24% for abstention; zero violations over 300 splits. Naive acquisition "violates on every split". Key lesson: calibrate on post-acquisition scores. |
| VOILA 2602.03007 | y_f in {0,1}: whether the VLM's answer at fidelity f is correct; "we construct training data by executing the VLM at each fidelity f on labeled examples and recording whether the produced answer is correct". Decision: argmax_f Pr(correct\|q) - lambda*c(f) (Sec. 3.1). | No explicit averaging; one recorded run per (question, fidelity). Gradient-boosted regressor plus isotonic calibration. | Question-only features (TF-IDF, lexical stats, coarse question type); no image at decision time. | Fixed-fidelity baselines, accuracy-only selection, fixed-threshold heuristics (App. F.3). | Abstract/Sec. 5: "50-60% cost reductions while retaining 90-95% of full-resolution accuracy" across 5 datasets and 6 VLMs; VOILA "lies on or near the frontier" (Fig. 4). |
| AdaTooler-V 2512.16918 | Tool Benefit Score, Sec. 3.3 Eq. 1: DeltaS_i = S+(q_i) - S-(q_i), "the average accuracy of the model when reasoning with and without tool-use", reward R_t = DeltaS_i * exp(-gamma((n_tool - n_max)/n_max)^2), gamma=2. | YES. "Each query is evaluated eight times using Qwen2.5-VL-72B-Instruct (i.e., eight runs with tool-use and eight runs without tool-use) and the averaged accuracy gap is used". | The MLLM itself (image and question) during RL; the score is only an offline reward scale. | Qwen2.5-VL-7B base (V* 78.5), GPT-4o (65.2), Gemini 1.5 Pro (71.7), open models in Table 1; ablations on the reward (Table 3). | AdaTooler-V-7B 89.8 on V*, 12 benchmarks. |
| When2Tool 2605.09252 | "we force the model to answer without tool access, and label tasks where it succeeds as tool-unnecessary (y=0) and tasks where it fails as tool-necessary (y=1)". | No, one no-tool outcome per task (Sec. 4). Appendix J compares with an easy-vs-hard difficulty label. | Last-token hidden state, all layers concatenated, pre-generation; L2-regularized logistic regression, 900 train and 2,250 test tasks. | Prompt-only variants, Reason-then-Act, (App.) SFT. | Table 3: AUROC 0.894 (Qwen3-1.7B) to 0.957 (Qwen3-14B). Sec. 1: Probe&Prefill "reduces tool calls by 38% with only 1.7% accuracy loss, while the best baseline at comparable accuracy only reduces 4.2% of tool calls"; up to 56% fewer API calls on Search-o1. |
| Illusion of Visual Tool-Use 2608.06270 | Not a training target; an audit estimand. Eq. 4: VEG_i = DeltaM_real_i - DeltaM_cf_i, where the cf observation is a same-shape crop from a different location; "the action-induced shortcut T_i -> Y cancels". M is an option-restricted softmax probability gap on a forced answer. | Counterfactual replacement of one observation under a fixed prefix; repeated-seed runs reported in App. C.1. | Not a gate. Rollouts of six open MLLMs (DeepEyes, Mini-o3, Qwen3-VL-4B/8B, Pixel Reasoner, Thyme) on five fine-grained perception benchmarks. | Direct inference vs tool-use (policy level), corrupted observations (trajectory level). | Policy-level gain "essentially null on DeepEyes", modest on others, largest on Mini-o3 and Qwen3-VL-8B (+21.3 pp on VisualProbe) (Sec. 3.3.1). Gain concentrated in a Calibrated minority; two failure modes CWL and LWP (Sec. 4). |

Observations for the thesis:
- Nobody in this table averages the "call helps" label over environment noise at the decision-instance level except AdaTooler-V (8 runs with and 8 without the tool). ToolGate states it cannot get the counterfactual; When2Tool and VOILA use a single outcome. The project's per-tool expected gain over noise draws is therefore a cleaner version of AdaTooler-V's DeltaS, and it is computed per tool, which none of these do (all are binary call/skip or fidelity choice).
- No gate in the table conditions on the set of alternatives being chosen between. VOILA is the only one that scores several options per query (fidelities), from question features alone.
- Prompted self-regulation failures are quantified in ToolGate Table 3 (self-report: more calls, -10.8 accuracy points) and When2Tool (prompt-only suppresses necessary calls).

## Addendum B: new papers from the second pass

### Act Wisely: Cultivating Meta-Cognitive Tool Use in Agentic Multimodal Models (Metis, HDPO)
- id: arXiv:2604.08545 | date: 2026-04 | venue: arXiv preprint
- authors: Yan, Shilin et al. | code: https://github.com/Accio-Lab/Metis (link in the HuggingFace page)
- relevance: MED-HIGH — names "blind tool invocation" in a VLM and fixes it with a conditional efficiency reward; closest VLM competitor for learned when-to-call.
- what: Argues a scalarized tool penalty either suppresses essential tool use or is swamped by accuracy-reward variance. HDPO keeps an accuracy channel and an efficiency channel that applies "exclusively within accurate trajectories via conditional advantage estimation". Abstract: Metis "reduces tool invocations by orders of magnitude (e.g., from 98% to 2%) while simultaneously elevating reasoning accuracy" (Qwen3-VL-8B base).
- thesis use: related work and a baseline family (RL-trained caller); contrast with the supervised expected-gain selector. The 98% vs 2% number supports "base VLMs call blindly", opposite to the project's "none" behavior for a prompted Qwen3.5-9B, so state the two failure modes explicitly.
- verified: abs meta fetched / html partly read

### Look Where It Matters: High-Resolution Crops Retrieval for Efficient VLMs (AwaRes)
- id: arXiv:2603.16932 | date: 2026-03 | venue: arXiv preprint (v2 Sep 2026)
- authors: Shabtay, Nimrod et al. | code: project page https://nimrodshabtay.github.io/AwaRes
- relevance: MED — learned whether-and-where crop request, with an explicit label for "is the cheap view insufficient".
- what: Stage 1 label (Sec. 3): run a base VLM on low- and full-resolution inputs; an LLM judge compares both to ground truth; "If it judges a_low as correct (or ties it with a_full), we label the example as no crop needed LR; otherwise ... HR". Then a grounding model gives crop boxes, SFT then multi-turn GRPO with composite reward including crop-cost penalties. Abstract: "matches full-resolution accuracy while retaining only 36% of visual tokens"; Fig. 1: 80.3% with 36% of tokens across six benchmarks.
- thesis use: precedent for deriving a binary "query needed" label by comparing outcomes with and without the extra information (single run, no averaging).
- verified: abs meta fetched / html read (label stage)

### Starve to Perceive: Taming Lazy Perception in VLMs with Constrained Visual Bandwidth
- id: arXiv:2605.18603 | date: 2026-05 | venue: arXiv preprint (v2 Jul 2026)
- authors: Wu, Yuhuan et al. | code: not checked
- relevance: MED — evidence of "lazy perception": models imitate zoom/crop calls without depending on the outputs, because coarse views plus priors give moderate accuracy; fix by capping the token budget per view. Reports 5% average relative improvement.
- thesis use: explains why prompted VLMs mis-call tools (no incentive to look); supports training the selector on measured gains rather than on model behavior.
- verified: abs meta fetched

### Zoom Consistency: A Free Confidence Signal in Multi-Step Visual Grounding Pipelines
- id: arXiv:2604.15376 | date: 2026-04 | venue: arXiv preprint
- authors: Kim, Keon et al. | code: https://github.com/omxyz/zoom-consistency-routing
- relevance: LOW — geometric confidence from zoom agreement routes between a specialist and generalist VLM; AUC 0.60, captures 16.5% of oracle headroom (+0.8%, McNemar p = 0.19).
- thesis use: an example of a weak, cheap geometric uncertainty signal; small effects.
- verified: abs meta fetched

### SaPaVe: Towards Active Perception and Manipulation in Vision-Language-Action Models for Robotics
- id: arXiv:2603.12193 | date: 2026-03 | venue: arXiv preprint
- authors: Liu, Mengzhen et al. | code: not checked
- relevance: LOW — semantic camera control for a VLA with ActiveViewPose-200K and ActiveManip-Bench; up to 31.25% higher real-world success than GR00T N1 and pi_0. No cost-budgeted query decision.
- thesis use: robotics active-perception context only.
- verified: abs meta fetched

### Learning to See and Act: Task-Aware Virtual View Exploration for Robotic Manipulation (TVVE / TAVP)
- id: arXiv:2508.05186 | date: 2025-08 | venue: arXiv preprint
- authors: Bai, Yongjie et al. | code: https://hcplab-sysu.github.io/TAVP
- relevance: LOW — learns an exploration policy (in a pseudo-environment) to select task-relevant virtual viewpoints; RLBench-OG tests visual perturbations. No budget.
- thesis use: robotics view selection context. (Earlier in this file the title was given from a search listing; this is the abs-page title.)
- verified: abs meta fetched

### Act, Sense, Act: Learning Active Perception from Large-Scale Egocentric Human Data (CoMe-VLA)
- id: arXiv:2602.04600 | date: 2026-02 | venue: arXiv preprint
- authors: Li, Jialiang et al. | code: not checked
- relevance: LOW — formalizes active perception as a history-dependent loop of information-seeking actions and decision branching; VLA with a cognitive auxiliary head and dual-track memory.
- thesis use: vocabulary for "information-seeking action"; no cost trade-off.
- verified: abs meta fetched

## Addendum C: snowball results

- OpenAlex has no citing works yet for ToolGate (W7163349247, 0), When2Tool (W7160906306, 0), AdaTooler-V (2) or AutoTool (0); BCEA was not found by title. Cited-by lists for the 2026 papers are therefore empty and not informative; "similar work" came from web search (Metis, AwaRes, Starve to Perceive, Zoom Consistency).
- KnowNo (W4383472635, 109 citations) has 24 citing works dated 2025-07 onward in OpenAlex. Mostly surveys and HRI papers. The relevant ones: Value of Information: A Framework for Human-Agent Communication (already listed as arXiv:2601.06407, now seen as ACL 2026 long, doi 10.18653/v1/2026.acl-long.1987); "A Human-in-the-Loop Confidence-Aware Failure Recovery Framework for Modular Robot Policies" (HRI 2026, doi 10.1145/3757279.3788668, not read); "Perceive with confidence: Statistical safety assurances for navigation with learning-based perception" (IJRR, doi 10.1177/02783649251378151, not read; conformal perception for navigation, possibly relevant to the calibration phase). I did not open these.
- Not found: any follow-up that conditions a KnowNo-style trigger on the divergence of candidate plans together with a choice among perception tools.

## Summary (updated after full-text pass)
- No paper found here, in driving or elsewhere, selects among several perception tools conditioned on the divergence of a candidate set under a budget. The nearest are ToolGate (execute/skip for one proposed VLM call), VOILA (pick one of several fidelities per query, question-only features), AwaRes (whether and where to crop), BCEA (answer/abstain/acquire with a conformal certificate), and KnowNo/UPS (candidate-set ambiguity triggers a help or clarification action).
- Label definitions differ from the project's. ToolGate: single-rollout forced-answer flip plus episode success; it says true counterfactual VoI is unobservable. When2Tool: one no-tool outcome. VOILA and AwaRes: one run per option. Only AdaTooler-V averages ("eight runs with tool-use and eight runs without") to get a tool benefit score DeltaS. The project's per-tool expected gain over noise draws is the only per-tool, noise-averaged target seen; say so, and cite AdaTooler-V as the closest precedent.
- Prompted VLM and LLM tool decisions are shown to be poor from both directions: over-calling (ToolGate 2.73 calls per episode at baseline and 5.88 when asked to self-report value; Metis 98% redundant calls; AdaTooler-V "blind tool-use"; Illusion audit "Calling Without Looking") and suppression (When2Tool: prompt-only baselines suppress necessary calls). The project's "mostly says none" is the suppression side; frame both as mis-calibration.
- Small learned heads on cheap inputs beat prompting repeatedly: ToolGate (text features, logistic regression, +1.65 accuracy points in-domain at 67% tokens), When2Tool (linear probe AUROC 0.89 to 0.96), VOILA (question-only features, 50-60% cost cut at 90-95% accuracy). This supports the MLP selector design; it does not support a claim that candidate conditioning matters, which none of them test.
- Confidence-style triggers are weak: Ortiz (2601.00138) shows self-reported confidence stays at 0.9 when evidence is cut 3x; Zoom Consistency gets AUC 0.60. Useful backing against the scene-uncertainty baseline, in addition to DriveAgent-R1.
- Calibration for the future phase: BCEA shows that gating acquisition on a borderline band and calibrating on post-acquisition scores keeps the conformal guarantee, whereas naive acquisition breaks it ("violates on every split"). That applies directly to a CRC wrapper around the selector plus ranker pipeline. UPS (2602.22474), CORA (2604.09155) and ToolChain-CRC (2606.18467) give execute/abstain/escalate templates.
- KnowNo's trigger (non-singleton conformal set over candidate plans, 10-24% less help than baselines) is the natural candidate-ambiguity baseline to add to the Pareto plot; the project's difference is choosing which tool and learning from measured gain.
- Metrics worth adopting: tool productivity (correct answers per call, OTC-PO 2504.14870), and Visual Evidence Gain-style counterfactual checks that a returned observation actually changed the ranker's decision (2608.06270).

## Leads not followed
- Full text of AutoTool 2605.19852, Metis 2604.08545 (HDPO details), UPS 2602.22474 (how the conformal candidate set is built over action samples; likely the closest to candidate-conditioned triggering) and the three KnowNo-citing papers named in Addendum C.
- BCEA not found in OpenAlex; its code link was not looked for.
- Cost-sensitive selective prediction with a learned reject option in VLMs: not found in two searches.
- Skipped: learned deferral for LLM routing (2604.27723), When2Call/BFCL tool-necessity benchmarks, Adaptive-RAG and SeaKR-style triggers, "Reading the Plan" (NeurIPS 2026).
