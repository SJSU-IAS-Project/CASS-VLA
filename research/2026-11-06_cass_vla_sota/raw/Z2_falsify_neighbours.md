# Z2_falsify_neighbours: does a neighbouring field already do the core mechanism?

Search window: 2026-11-06 23:47 to about 00:20 PST. Every arXiv entry below had its abstract page fetched with absfetch.py. Five (CLARINET, ATAP, LA-CDM, ACTMED, BudgetVerify) also had the arxiv.org/html text read and grepped. Classic (pre-arXiv) items come from WebSearch result pages only and are marked.

## Summary

Core mechanism M = (a) conditioning on the set of K candidates, (b) choosing among several different costly sources or none, (c) selector learned from each source's expected decision gain, (d) accuracy-vs-budget curve against uncertainty, random and oracle choosers.

Verdict: the mechanism as a conjunction has no single exact precedent that I found, but every part exists in a neighbouring field, and two papers cover three of the four parts each. A reviewer can fairly say "this is CLARINET / BudgetVerify / Best-of-Evidence applied to driving". What remains new is the combination: a learned chooser over heterogeneous perception tools, conditioned on how K trajectories diverge, with an oracle-selector ceiling. The idea of conditioning a query on the candidate set and training it on counterfactual outcome is NOT new. This is an absence over what I searched, not over the field.

Closest precedents, with the parts each has:

| Precedent | (a) candidate set | (b) choice among sources or none | (c) learned from gain | (d) budget curve vs uncertainty / random / oracle |
|---|---|---|---|---|
| CLARINET 2405.15784 (recsys / retrieval, read in full) | YES: the model input is the top book candidates (those whose retrieval probabilities add up to 50%, at most 3), plus dialogue | Partly: chooses among generated clarification questions (one source type, many questions); no "none" option | YES: trained on the question that put the target's rank in the top 10 or raised it by 10 or more in simulation; this is a counterfactual rank-gain target | Partly: per-turn curve over 10 turns; random, EIG and KL (information-style, not scene-uncertainty) baselines; no oracle selector, user is oracle only |
| BudgetVerify 2609.33052 (LLM verification, read in full) | NO: one generated answer, not a pool | YES: none / mid verifier / high verifier | YES: cost-aware oracle labels from running all three tiers offline, classifiers imitate them | Partly: accuracy-cost Pareto frontiers against fixed-tier policies only; no uncertainty, random or oracle selector; features are pre-verification question and answer features |
| Best-of-Evidence 2607.20950 (best-of-N with evidence actions; read by others, not by me) | YES: fixed best-of-N pool, actions valued by whether they can change the choice | YES: several evidence actions | NO: plug-in expected value of sample information, no training | Partly: budget sweep, vs majority; others report gains of 0.26 to 0.58 points |
| Hutchinson and Kak 1989 (robot work cell; WebSearch snippets only) | YES: sensing chosen from current hypotheses about object identity and pose | YES: range, camera and force/torque sensing operations | NO: hand-built ambiguity-minimising rule | NO |
| Rao and Daume 1805.04655 (clarification questions, abstract only) | YES: scores each candidate question by expected utility over candidate answers | YES (many questions) | YES: neural EVPI, trained on StackExchange pairs | NO: ranking metrics vs expert judgement, no budget curve |
| ATAP 2609.23504 (grasp NBV, read in full) | YES: competing affordance-location hypotheses | YES: candidate viewpoints | NO: objective is expected entropy reduction plus verification gain | Partly: fewer NBV steps (57% fewer) vs reconstruction-based NBV; no selector baselines |
| Arnob and Stein 2403.03269 (navigation) | NO | YES: which unseen region to reveal | YES: GNN trained on computed value of information | NO: planner baselines, not selector curves |
| LA-CDM 2506.13474 and ACTMED 2510.18988 (medical test choice) | YES: hypothesis agent keeps candidate diagnoses; ACTMED scores tests by expected KL over diagnoses | YES: choose among tests or stop | LA-CDM: RL with efficiency reward, no gain labels; ACTMED: no training | Weak: no oracle selector found in the text greps |

Other points that matter for the thesis:
- The training target "each source's outcome gain, averaged over noise" has a clear ancestor in BudgetVerify's offline-all-tiers labels and CLARINET's rank-gain labels. The project's "expected gain targets" are not a novel recipe; cite both.
- Candidate-conditioning is the weak point to defend. In neighbouring fields the candidate set enters either as a model input (CLARINET) or through an analytic hypothesis-split rule (Hutchinson and Kak, ATAP, ACTMED, Best-of-Evidence). BudgetVerify, ToolGate and SWE-Verifier show that routers without candidate features already give most of the Pareto gain, which fits the project's own 1 to 2 point margin.
- Disagreement-based single-question rules (query by committee, expected error reduction, Roy and McCallum 2001) and Chernoff-style active hypothesis testing (Chernoff 1959; Nitinawarat et al. 1205.0858; Kartik, Nayyar and Mitra, IEEE TAC 2022) are the theory ancestors of "pick the source that best separates the leading hypotheses". The search gave me abstracts and snippets only for these; I did not find one that is learned from outcome gain or compared against an oracle selector.
- Not found in any neighbour: an oracle-selector upper bound next to uncertainty and random choosers for source choice (only budget/Pareto vs fixed policies). That evaluation protocol is the project's clearest non-derivative piece.
- EQA and VLA active perception (VG-AVS 2512.13250, ActiveVLA, ActiveScale, EyeVLA) pick views from a single image or a policy, without a candidate-action set. They are not precedents for (a).
- Selective-deferral work (Budgeted Multiple-Expert Deferral 2510.26706, already in papers.csv) learns which expert to query, but conditions on the input, not a candidate set.

## Query log

| query (shortened) | source | closest result |
|---|---|---|
| which test to order given differential diagnosis, learned test selection | WebSearch std | ACTMED 2510.18988, SSRN 5367662 (sequential diagnostic testing, MDP) |
| active hypothesis testing choose sensor, Chernoff | WebSearch std | Chernoff 1959 lineage, Kartik/Nayyar/Mitra 2022, 1205.0858, 1403.1023 |
| best-of-N selective verification, which verifier, learned router | WebSearch std | 2602.03975, Best-of-Evidence 2607.20950 |
| clarifying question selection conditioned on candidate answers | WebSearch std | CLARINET 2405.15784, CLAIM 2608.11631 (UNVERIFIED id, not fetched) |
| next-best-view to disambiguate candidate grasps / pose hypotheses | WebSearch std | ATAP 2609.23504, ACE-NBV, Multi-View Picking 1809.08564 |
| EQA active perception, candidate answers disagree | WebSearch std | VG-AVS 2512.13250, SafeVantage (NeurIPS 2026 listing, not fetched) |
| learned sensor/tool query among several, expected decision improvement, uncertainty/random/oracle | WebSearch ext | decision-focused active learning (DEIG), no exact match |
| expected error reduction, query by committee | WebSearch std | Roy and McCallum 2001; Mussmann 2211.09283 |
| multi-hypothesis tracking sensor tasking, IDS | WebSearch std | Rybski and Veloso 2009 (EURASIP), Dagan/Becker/Sunberg hypothesis-driven tasking; no IDS hit |
| robot navigation sensor to disambiguate candidate paths, VOI | WebSearch std | Arnob and Stein 2403.03269; Hutchinson and Kak 1989 |
| LLM agent tool call by whether it changes candidate ranking | WebSearch std | ToolGate 2606.03054 (in csv), CAM-DF 2607.27083 |
| VLA active perception, disagreement among candidate action chunks | WebSearch ext | ActiveVLA 2601.08325, ActiveScale 2609.18514; none uses disagreement |
| learned VOI predictor on counterfactual decision gain | WebSearch ext | no match |
| Rao and Daume EVPI | WebSearch std | 1805.04655 |
| diagnostic test recommendation, supervised / RL, top-k differential | WebSearch std | LDTL 2604.05116, LA-CDM 2506.13474, DiagAgent 2510.24654, DiaLLM 2506.20059 |
| decision-focused active feature acquisition, top class flip | WebSearch std | AFABench 2508.14734 (in csv), AFA survey 2502.11067 |
| learned query selection among oracles, oracle selector | WebSearch std | Budgeted Multiple-Expert Deferral 2510.26706 (in csv) |
| plan-disagreement triggers ask/tool in robot LLM planners | WebSearch std | KnowNo 2307.01928, Introspective Planning (both already known) |
| multiple verifiers cost-aware routing | WebSearch ext | BudgetVerify 2609.33052, RouteAudit 2610.02808, SWE-Verifier 2610.30284 |
| active perception grasp, sensing action to discriminate top grasps | WebSearch std | Arruda 1708.04185, GraspView 2511.04199 |
| Roy McCallum 2001; Hutchinson Kak 1989 | WebSearch std | metadata confirmed from result pages |
| decision-aware sensing among planned trajectories | WebSearch ext | B-COD 2508.12166 (in csv), AS-DDTO 2606.22277 (in csv) |
| OpenAlex for classics (6 queries) | OpenAlex | responses had no "results" field (free daily budget notice); not used |

## Papers

### CLARINET: Augmenting Language Models to Ask Clarification Questions for Retrieval
- id: arXiv:2405.15784 | date: 2024-04 | venue: arXiv preprint
- authors: Chi, Yizhou et al. | code: none seen
- relevance: HIGH — nearest neighbour-field precedent: a learned question chooser that takes the top candidates as input and is trained on a counterfactual rank-gain target.
- what: Picks which clarification question to ask so that the true item's rank rises. For each training query, candidate questions are answered by a GPT-3 user simulator; the model is trained on questions that put the target in the top 10 or raise its rank by 10. Input is the user query, past interactions and the top book candidates. It beats information gain by 17% and vanilla LLM prompting by 39% relative on retrieval success (abstract, book search). Appendix table has Random, EIG, KL and CLARINET rows.
- thesis use: must cite as prior art for candidate-conditioned query selection trained on counterfactual gain. Differences: one query type, no "none", no oracle selector, no uncertainty-trigger baseline, no hazard/noise levels.
- verified: abs meta fetched / html read

### BudgetVerify: Budget-Tiered Verification for Financial QA
- id: arXiv:2609.33052 | date: 2026-09 | venue: arXiv preprint
- authors: Jenq, Janet et al. | code: none seen
- relevance: HIGH — learned router over {no verification, cheap check, strong check}, trained on offline per-tier outcome labels, reported as accuracy-cost Pareto frontiers; the training recipe matches the project's.
- what: Runs all three tiers offline on the training split, derives cost-aware oracle labels per cost parameter, trains lightweight classifiers to imitate them. Features are question, context and generator-output cues, available before verification. Frontiers beat fixed-tier policies across six generator models.
- thesis use: precedent for gain-labelled routing and Pareto reporting. Contrast: single answer, no candidate set, no uncertainty/random/oracle selector baselines (only fixed tiers).
- verified: abs meta fetched / html read

### Best-of-Evidence: Best-of-N Selection under Partial Verification
- id: arXiv:2607.20950 | date: 2026-07 | venue: arXiv preprint (also OpenReview U1JptdfbDT)
- authors: not re-fetched | code: none seen
- relevance: HIGH — fixed candidate pool plus a budget over evidence actions that can change the choice; already in papers.csv and in report section 2.
- what: Only seen via a search summary this run (confirms: pool kept fixed, budget spent on evidence actions that can change the final choice, zero budget reduces to plain best-of-N). Not re-read.
- thesis use: the strongest "this is X applied to driving" candidate besides CLARINET; no training, so the learned-from-gain part differs.
- verified: UNVERIFIED in this run (search summary only); see Y_leads_followup.md

### Planning Sensing Strategies in a Robot Work Cell with Multi-Sensor Capabilities
- id: IEEE Trans. Robotics and Automation 5(6):765-783 | date: 1989 | venue: IEEE T-RA
- authors: Hutchinson, S. A. and Kak, A. C. | code: none
- relevance: MED — oldest hypothesis-conditioned sensor choice: proposes sensing operations, estimates the ambiguity left among current hypotheses, picks the one that reduces it most, across range, camera and force/torque sensing.
- what: Per web records: sensor and viewpoint chosen from hypotheses about object identity and position; equivalent operations grouped via an aspect-graph structure. No learning, no budget curve.
- thesis use: citable origin of mechanism parts (a) and (b); shows "which sensor given candidate hypotheses" is a 1980s idea.
- verified: page fetched (WebSearch snippets only, full text not read); pages at faculty.cc.gatech.edu/~seth/ResPages/pdfs/HutKak89.pdf

### Learning to Ask Good Questions: Ranking Clarification Questions using Neural Expected Value of Perfect Information
- id: arXiv:1805.04655 | date: 2018-05 | venue: ACL 2018
- authors: Rao, Sudha et al. | code: github.com/raosudha89/ranking_clarification_questions (per search result)
- relevance: MED — neural expected-value-of-perfect-information ranker over candidate questions, trained on about 77K StackExchange posts.
- what: Each candidate question is scored by expected utility over a set of candidate answers. Evaluated on 500 samples against expert judgements.
- thesis use: classic VOI-learned-from-data precedent; no budget curve.
- verified: abs meta fetched

### Imagine then Verify: Affordance-Targeted Active Perception for Task-Oriented Grasping in Cluttered Scenes (ATAP)
- id: arXiv:2609.23504 | date: 2026-09 | venue: arXiv preprint
- authors: Cui, Jingzhi et al. | code: none seen
- relevance: MED — viewpoint planner that maximises expected entropy reduction over competing occlusion hypotheses plus expected verification gain; stops on a viewpoint budget.
- what: Hypothesises hidden geometry with a shape prior, predicts an affordance distribution, scores views. 57% fewer NBV steps than reconstruction-based active perception. Not learned from gain targets.
- thesis use: robot-manipulation analogue of (a)+(b) for occlusion; analytic rule, no selector baselines.
- verified: abs meta fetched / html read

### Active Information Gathering for Long-Horizon Navigation Under Uncertainty by Learning the Value of Information
- id: arXiv:2403.03269 | date: 2024-03 | venue: arXiv preprint
- authors: Arnob, Raihan Islam et al. | code: none seen
- relevance: MED — GNN trained on computed value of information to pick which unseen region to reveal (up to 63.76% and 36.68% improvement over baselines in two office-like environments, per abstract).
- what: Training-time VOI computation supplies labels; the learned predictor chooses exploratory actions. Already in papers.csv.
- thesis use: learned-from-VOI-labels precedent in navigation; no candidate plans, no selector budget curve.
- verified: abs meta fetched

### Language Agents for Hypothesis-driven Clinical Decision Making with Reinforcement Learning (LA-CDM)
- id: arXiv:2506.13474 | date: 2025-06 | venue: arXiv preprint (a search result lists ICLR 2026, UNVERIFIED)
- authors: Bani-Harouni, David et al. | code: none seen
- relevance: MED — an agent keeps diagnostic hypotheses and uncertainty and chooses the next test or commits, trained with SL plus RL including an efficiency objective; MIMIC-CDM.
- what: Test choice conditioned on hypotheses, trained by reward, with no gain labels. The paper itself notes there is no ground truth on optimal test sequences.
- thesis use: medical precedent for hypothesis-conditioned test choice learned from outcome.
- verified: abs meta fetched / html read

### Timely Clinical Diagnosis through Active Test Selection (ACTMED)
- id: arXiv:2510.18988 | date: 2025-10 | venue: arXiv preprint
- authors: Estevez, Silas Ruhrberg et al. | code: none seen
- relevance: MED — selects the test with the largest expected diagnostic-uncertainty reduction (Bayesian experimental design with an LLM simulator, cost-penalised).
- what: Training-free; test chosen by expected KL gain over diagnoses.
- thesis use: medical analogue of the analytic VOI selector; contrasts with the learned selector.
- verified: abs meta fetched / html read

### Uncertainty-Guided Latent Diagnostic Trajectory Learning for Sequential Clinical Diagnosis (LDTL)
- id: arXiv:2604.05116 | date: 2026-04 | venue: arXiv preprint
- authors: Shen, Xuyang et al. | code: none seen
- relevance: LOW — planner LLM trained toward trajectories that carry more diagnostic information; better accuracy with fewer tests on MIMIC-CDM.
- thesis use: medical related work for learned acquisition.
- verified: abs meta fetched

### ROUTEAUDIT: Interaction-Aware Identification for Budgeted Multi-Verifier Routing
- id: arXiv:2610.02808 | date: 2026-10 | venue: arXiv preprint
- authors: Hu, Miaobo et al. | code: none seen
- relevance: LOW — evaluation-protocol paper for multi-verifier routers; holds the verifier catalog, accounting and scorer fixed and attributes gains to routes. On 1,319 held-out requests, learned and RLVR routers score 0.9522 and 0.9553 against 0.9484 for matched static.
- thesis use: idea to borrow for a fair matched-baseline comparison; shows tiny router gains over a matched static policy are the norm.
- verified: abs meta fetched

### SWE-Verifier: Selective Verification for Cost-Efficient Coding Agents
- id: arXiv:2610.30284 | date: 2026-10 | venue: arXiv preprint
- authors: Zou, Kaijian et al. | code: github.com/zkjzou/SWE-Verifier
- relevance: LOW — scores the proposed action to decide when to sample and rank alternatives; verifies fewer than 4% of steps, 75.47 to 77.20% resolution at 1.09x cost.
- thesis use: binary candidate-generation gate, sibling of the "whether" decision.
- verified: abs meta fetched

### Adaptive Test-Time Compute Allocation via Learned Heuristics over Categorical Structure
- id: arXiv:2602.03975 | date: 2026-02 | venue: arXiv preprint
- authors: Qu, Shuhui | code: none seen
- relevance: LOW — allocates verifier calls across intermediate states by local uncertainty; 44% fewer verifier calls on MATH with higher accuracy than best-of-N.
- thesis use: uncertainty-triggered verification baseline analogue.
- verified: abs meta fetched

### Scores Are Not Decisions: Cost-Aware Stopping for Tool Acquisition in LLM Agents (CAM-DF)
- id: arXiv:2607.27083 | date: 2026-07 | venue: arXiv preprint
- authors: Feng, Yicheng et al. | code: none seen
- relevance: LOW — trained on the offline gap between stopping now and the best continuation; 37% fewer tools at comparable task success.
- thesis use: another instance of decision-gap training targets; supports not using ranking scores as the trigger.
- verified: abs meta fetched

### Human-AI-Powered Hypothesis Testing: Cost-Aware Selective AI Scoring and Sequential Human Escalation (SCALE)
- id: arXiv:2609.28859 | date: 2026-09 | venue: arXiv preprint
- authors: Ham, Dae Woong et al. | code: none seen
- relevance: LOW — sequential choice between AI scoring and human verification with a lower bound; a modern active-hypothesis-testing analogue with a theoretical cost bound.
- thesis use: citable for the active-testing lineage (Chernoff).
- verified: abs meta fetched

### Toward Ambulatory Vision: Learning Visually-Grounded Active View Selection (VG-AVS)
- id: arXiv:2512.13250 | date: 2025-12 | venue: arXiv preprint (a search result lists ICML 2026, UNVERIFIED)
- authors: Koo, Juil et al. | code: none seen
- relevance: LOW — picks the next viewpoint from the current image only; SFT then RL; improves EQA accuracy when added to scene-exploration systems.
- thesis use: EQA neighbour that lacks a candidate set; marks the boundary of what EQA does.
- verified: abs meta fetched

### Toward Optimal Active Learning through Sampling Estimation of Error Reduction
- id: ICML 2001, pp. 441-448 | date: 2001 | venue: ICML
- authors: Roy, Nicholas and McCallum, Andrew | code: none
- relevance: LOW — expected-error-reduction query selection, the classic "pick what most lowers expected future error".
- thesis use: classic citation for decision-gain-based selection.
- verified: page fetched (search result only)

### Controlled Sensing for Multihypothesis Testing (Nitinawarat et al.)
- id: arXiv:1205.0858 | date: 2012 | venue: arXiv preprint (per search result)
- authors: Nitinawarat et al. (full list not fetched) | code: none
- relevance: LOW — Chernoff-type policies for choosing experiments among several hypotheses; error exponents.
- thesis use: theory citation for active hypothesis testing; no learned selector.
- verified: UNVERIFIED (search result snippet only)

## Leads not followed
- Best-of-Evidence full text re-read (other agents did it); only a search summary used here.
- CLAIM 2608.11631 (information-gain clarification, arXiv id looked unusual in the search result) not fetched.
- SafeVantage (NeurIPS 2026 listing), DiagAgent 2510.24654, DiaLLM 2506.20059, Mussmann 2211.09283, AFA survey 2502.11067: seen in search only.
- Classics checked by search snippet only: Chernoff 1959, Seung et al. query by committee 1992, information-directed sampling (Russo and Van Roy), Hager and Mintz sensor-decision work. Not tied to a fetched record.
- OpenAlex gave no results this run (free-budget notice); a retry with an API key could verify the classics and run cited-by lists for CLARINET and BudgetVerify.
- Not searched: medical imaging "which modality" triage papers, sensor tasking in radar management, and active learning with multiple annotators (proactive learning, Donmez and Carbonell 2008) beyond one snippet.
