# Z1_falsify_direct: try to falsify the novelty claim

Run: 2026-11-06/07, about 00:00 to 00:30 PST. Claim tested: a selector for a driving planner picks which perception
query to make (one of several tools, or none) from features of how the K candidate trajectories diverge, is trained on
per-tool decision gain, and is evaluated as accuracy vs. query budget against uncertainty, random and oracle selectors.

## Summary

- **Counterexample found: NO.** About 60 differently worded queries over web search (standard and extended), patents,
  OpenReview (4 groups x 12 terms, then 3 groups x 10 terms), GitHub, arXiv listing titles (171,806 titles in the
  existing `listing_sweep`, re-filtered with new regexes) and abstract fetches turned up no paper, patent, thesis or repo that
  does all of: tool choice + candidate-trajectory-divergence features + gain-trained selector + budget curve vs
  uncertainty/random/oracle. REPORT.md section 1 stands. This is an absence over what I could search, not a proof.
- **Partial: three near-misses that are closer on one axis than something already in section 1, but none beats the five
  closest in section 1 overall.** Each differs on at least three of the four elements.
  1. **Ask the World** (OpenReview 4YOXy9OdU4, ICLR 2027 submission, already in papers.csv). A tentative correction to a
     nominal VLA action chunk is used as a "decision-directed visual query" to pick which viewpoint to acquire before
     accepting or rejecting the correction. Closest on "candidate plans define what to look at". Differs: robot
     manipulation, two candidates (nominal vs corrected) not K, a viewpoint rather than a choice among tool types, no
     learned selector on divergence features, no budget sweep or oracle/random baselines visible. Abstract only
     (openreview.net/pdf is blocked).
  2. **GM patent US12179756B2** ("Algorithm to generate planning-based attention signals", priority 2022-09-27). A DNN on a scene
     graph predicts a per-actor attention score. Claim 1 builds the training target from the planner itself: sample actor-state
     scenarios, plan with and without the actor ("removed actor"), take the maximum waypoint distance D_i between the two
     average trajectories. That is a decision-gain label learned by a network. Differs: chooses which actor to attend, not
     which tool; one planner trajectory per scenario sample, no candidate set and no ranker; no abstain action, no budget curve.
     New to the corpus. Read: abstract and claim 1 on Google Patents.
  3. **AnA: An Attentive Autonomous Driving System** (ASPLOS 2025, Choe, Wang, Lin; DOI 10.1145/3669940.3707261). Defines a
     query interface from planner to perception: the planner asks for focused tasks such as high-accuracy localisation of
     specific agents; standing queries give cheap awareness, ad-hoc queries give attention. Closest on "planner decides what
     perception to spend". Differs: a systems paper, query generation looks rule-based from driving context, a first-pass
     detector runs on every frame, baselines are perception-only heuristics (2P-All/Moving/Heuristic), no learned selector, no
     tool choice, no candidate set. New to the corpus. Read: the ACM abstract stub and a third-party review page only (no paper
     text), so details of query generation are UNVERIFIED.
- **Gain-trained binary gates are common and not new** (G-VLM, RISE, AdaDrive, SIGMA, DualDriveVLA). They answer "whether",
  not "which tool", and none uses candidate divergence. G-VLM (IEEE TITS 2026) trains the gate on the behavioural discrepancy
  between a lightweight controller and the VLM-assisted output; RISE (2608.20430) gates rollout on expected planning benefit.
  Both are new to papers.csv and worth a one-line cite as the "gain label" lineage.
- **Patents show the plan-to-perception feedback idea is old** (Baidu US10551840B2 / EP3633408, planner ROIs select which
  sensors perception processes; GM above; occlusion-aware planning patents that score candidate trajectories by collision
  probability plus information gain, e.g. US11834077). None selects among tools by learned gain. Cite as prior art for "plan
  tells perception where to look", not for the claim.
- **Where the claim is still safe:** the combination "K-candidate divergence features + choice among heterogeneous
  tools + abstain + gain targets + budget-vs-accuracy against uncertainty/random/oracle". The nearest on the budget-sweep
  and baseline design is not in driving (Proof-of-Perception 2603.00324, already in section 1).
- **Where the claim is weakest** (unchanged, found nothing to strengthen it): candidate-conditioning gain is small in the project's own
  results, and the literature increasingly frames this as value of information / decision value (DEEP, SIGMA, When to Ask for Help).
  Reviewers will ask for the comparison to a decision-value baseline with the same learner minus candidate features, which section 1
  already proposes.
- Search surface not covered: CVPR/ICRA/IROS 2027 submissions (no OpenReview group), patents beyond Google/USPTO snippets
  (no claim-level full-text search tool), Chinese-language venues, and anything after 2026-11-04.

## Query log

Format: query | source | hits checked | closest result. "Hits checked" = result titles read and compared to papers.csv; for
"extended" mode the engine returns about 10 links. Every ID named below was grepped in papers.csv; new ones were fetched with absfetch or the primary page.

Web search (WebSearch):

1. candidate trajectories which perception module to query AD planner learned selector query budget | web ext | 9 | patents on trajectory selection; MeanFuser; no match
2. plan-conditioned active perception driving: select sensing action by value of information over candidate plans | web ext | 10 | US 8781669 / 12187268 active sensing (info value of traffic light state, patent); IJCAI19 PBVI; DriveAgent-R1
3. decision-relevant perception AD tool call selection trajectory candidates disagreement | web | 10 | Gaffney patent US2024354462A1 (perception testing by decision change); 2609.03774 RIWM (perspective); 2605.25393 (not relevant)
4. patent selecting perception query based on divergence of candidate trajectories AV | web | 10 | US12005925 ambiguity resolution; US11975742 trajectory consistency; nothing on perception queries
5. "candidate trajectories" "perception tools" VLM driving agent chooses which tool zoom depth collision check | web ext | 9 | DriveAgent-R1, AgentThink, MTRDrive (all known)
6. test-time perception allocation planner candidates: which sensor to query to disambiguate top-ranked trajectories | web ext | 9 | TOAD 2606.07170, VeteranAD 2508.11488, 2602.16598 (all known)
7. learning to query perception: expected decision gain per tool, selector vs uncertainty vs random vs oracle... | web ext | 9 | general RL driving; nothing
8. multi-hypothesis planning active sensing occlusion information gathering disambiguate plans AV 2026 | web | 10 | Pad-AI-style, APRO, contingency planning; Ford occlusion patents
9. VLM driving "when to use tools" learned tool router gain-based labels perception tools budget | web ext | 9 | DriveAgent-R1 (gain-labelled data, tool reward); ToolVision, When Should a VLM Look (known)
10. "value of information" E2E driving planner invokes expensive perception module based on planner output | web | 7 | VeteranAD; Ego-MLP paper; nothing
11. github candidate trajectory scoring tool-augmented VLM driving perception tool selection MetaDrive occlusion hazard | web | 10 | HE-Drive, SimpleVSF, MetaVQA, VLM-SAFE
12. planner-aware adaptive perception: skip or run perception based on trajectory sensitivity | web ext | 9 | perception-aware planning (VIO), GFM-Planner; no match
13. github "candidate trajectories" "tool selection" AD agent perception "query budget" | web | 7 | Budget-constrained agentic LLMs 2602.11541 (known); patents
14. DriveAgent-R1 follow-up active perception tool-use driving VLM 2026 cost-aware gating which tool | web ext | 10 | OmniDrive-R1, 2609.08217 (known)
15. thesis master perception candidate plans next-best-view / sensor selection for planner decision occluded hazard | web | 10 | Cornell Han dissertation (NBV for multi-hypothesis planner), Michigan Zhong, Nagoya Narksri theses; none learned query selection
16. workshop paper 2026 "perception queries" planner candidate trajectories disagree "when to look" | web | 10 | VeteranAD, DriveSuprim, CLEAR; nothing
17. dynamic sensor gating multi-sensor driving planner picks sensor conditioned on predicted trajectories | web ext | 9 | EcoFusion, SEO (scene/risk gating, not plan)
18. robot navigation VLM chooses perception action (look, zoom, query) by disagreement among candidate actions | web ext | 9 | VAP-TAMP, ARNA, RoVLaP; none
19. "decision-aware"/"decision-relevant" perception "value of information" driving planner learned VoI estimator | web | 10 | 2505.06978 (VoI for V2X, new), 2601.06077 (known), 2604.01434 (known)
20. hypothesis-conditioned planning: perception query reduces ambiguity between ego trajectories ... | web | 10 | US11834077 (collision prob + info gain per candidate), CODEI 2503.10296 (new), Gilhuly ICRA22
21. arXiv 2026 driving agent "tool" "abstain" action space ROI inspection depth collision check ... | web ext | 9 | LLM-agent abstention/tool papers (2609.07395, 2607.10059, 2606.28733, 2607.27083 new but non-driving)
22. adaptive perception planning-aware trigger VLM invocation ... fast planner candidates triggers slow system | web ext | 9 | ASSCG 2606.25509, FASIONAD++, ThinkDrive (known); AdaDrive found (known)
23. patent "information gain" candidate trajectories select sensor "perception request" / "sensor tasking" | web | 10 | US11834077, US10754350
24. AdaDrive adaptive LLM activation | web | 10 | AdaDrive 2511.06253 (known)
25. "plan-conditioned"/"trajectory-conditioned" perception request VLM driving occluded pedestrian traffic light ... | web ext | 10 | DriveAgent-R1 failure case; FRENETIX-Occlusion; none
26. "learning to ask"/"learning to look" driving planner active sensing query policy RL occlusion | web | 10 | Pad-AI 2409.17618 (new), Zhang-Fisac RSS21 (known)
27. VLA/robot policy samples K action candidates, disagreement triggers sensing modality query | web ext | 9 | HiTac-WAM, RSS26 uncertainty-aware policy steering; none
28. AD "ask for more information"/"request perception" planner candidate trajectories "decision flip" tool gain oracle selector Pareto | web | 10 | DriveSuprim; Incremental Perception; PKL (known)
29. "perception-on-demand" AD planner queries perception module selectively | web | 10 | **AnA (ASPLOS25)**, VeteranAD, QuAD
30. trajectory-aware visual token selection / ROI selection conditioned on candidate ego trajectories | web | 10 | FastDriveVLA, ETA-VLA, LaTP; none conditioned on candidates
31. "Looking for Trouble"/planner-guided perception allocation, which agents to perceive accurately | web | 10 | **GM US12179756**, Baidu US10551840/EP3633408, Reece-Shafer 1993
32. planning-aware perception compute allocation 2026 E2E driving: selective high-res re-perception ... | web ext | 10 | VeteranAD, MomAD, StableDrive; none
33. sotaverified/alphaxiv "tool selection" driving "expected utility" ... cost-aware tool invocation | web | 10 | CostBench, 2306.07276; none
34. AnA: An Attentive Autonomous Driving System ASPLOS 2025 | web | 10 | NSF PAR record, review page
35. Choe Wang Lin "Attentive Autonomous Driving" AnA arXiv | web | 10 | no arXiv version found
36. verify planned trajectory with perception tools VLM driving "verification" tool call ... | web ext | 9 | DriveVer 2607.00399, SoTA Letters post "When to Wake a VLM" (new, blog), 2610.28184 (known)
37. active hypothesis testing AD which observation discriminates between candidate maneuvers EIG learned | web | 10 | 2110.04580 expected reward gain; active inference papers
38. "second look"/"targeted re-observation"/"probing" VLM driving candidate trajectories top-2 margin | web | 10 | SimpleVSF, DualDriveVLA, VL-DPO (known)
39. budgeted tool-use agents oracle/random/uncertainty selectors accuracy vs tool calls counterfactual tool gain labels | web ext | 9 | SURE-Act 2610.24194, ToolGate 2606.03054 (known), 2609.25678/2606.06976 (new, non-driving)
41. "dissertation value of information perception planning AD" | web | 10 | 2601.06077, 2306.07276, Padua VoI thesis (V2X)
42. patent AV planner "request" additional perception processing "for the candidate trajectories"... | web | 10 | Baidu US10551840, GM US12128924 (compute switching)
43. "decision-relevant" uncertainty AD perception planning selective refinement candidate trajectories ranking sensitivity | web | 10 | SUPER-AD, 2411.01639, 2602.16035, US11537127
44. CoRL/ICRA/IROS 2026 active perception for planning candidate query camera/sensor info-gain labels | web ext | 10 | APPLE, LEAP 2609.17628 (new, non-driving), 2603.23450 (sensor-query scheduling, new)
45. "trajectory divergence"/"plan divergence"/"candidate disagreement" feature selects when to invoke perception/VLM | web | 10 | **G-VLM (TITS 2026, new)**, 2602.10719, CAI-Gate 2507.20342, 2608.26074 (known)
46. learned gate trained on discrepancy with-help vs without-help planner decides when to call expensive module | web | 7 | nothing new
47. arXiv 2026 "tool" driving VLM "learned router"/"tool selector" from scene and trajectory features | web | 10 | MTRDrive, AgentThink, VisTA 2505.20289 (new, non-driving), 2602.15543 (known)
48. VLA planner proposes K candidates; verifier picks verification tool or camera view per candidate; budget | web ext | 10 | Pre-VLA, SEAL, VeGAS, VeriVLA 2610.21985 (new), SV-VLA; none pick tool
49. AD "hypothesis" occluded agent "should I look" learned policy chooses peek/wait/creep ... | web | 10 | Pad-AI 2409.17618, US12271204
50. "planning-aware" detector refinement "which objects to refine" learned importance from counterfactual | web | 10 | 2110.03270, HOIST 2312.02467 (known), NTNU 2024 relevance filter, RISE 2608.20430 (via hyper.ai)
51. Perception2Decision / "query timing" LLM driving remote model | web | 10 | 2604.01681, LVM-MPC 2504.18057 (collaboration timing; known family)
52. Tesla/Waymo/NVIDIA/Mobileye patent trajectory candidates selectively run additional perception when candidates differ in risk | web | 10 | US11851081, US11958503; none
53. "query" "perception" "planner" "counterfactual" "tool gain"/"decision gain" driving selector "query budget" | web ext | 9 | VeriDrive 2606.07338, BAS-OPD 2609.25891 (non-driving), 2608.22975 (known)
54. cooperative driving "which information to request" from planner candidates, bandwidth budget | web | 10 | 2305.04352, 2303.06080 (Glaser/Kira), COOPERNAUT; none
55. hazard-injection benchmark VLM driving tools ROI depth collision check tool-augmented planner | web | 10 | MovSafeBench/HazardForge, DSBench, CODA-LM; no tool+candidate benchmark
56. "To look or not to look" / "look before you leap" driving planner perception query cost | web | 10 | Ulysses 1993, VLMPlanner CAI-Gate, LVM-MPC
57. sufficient evidence driving VLM "evidence sufficiency" decide act or gather more | web | 10 | Q-Guide 2608.19739, EAFG 2608.20084, 2605.28160, 2409.17641 (non-driving)
58. closed-loop driving agent chooses among perception tools and abstain trained with tool-benefit labels CARLA Bench2Drive | web ext | 10 | Bench2Drive background only

OpenReview search API (api2.openreview.net/notes/search, 5 s spacing, limit 50, 0 errors):

- Batch 1: groups ICLR.cc/2027, ICLR.cc/2026, robot-learning.org/CoRL/2026, ICML.cc/2026 x 12 terms: "candidate trajectories perception query"; "which perception tool to call driving"; "tool selection autonomous driving planner budget"; "value of information planner candidate trajectories"; "active perception driving query budget"; "decision-relevant perception planning"; "when to look driving VLM tool"; "selective perception driving planner"; "trajectory-conditioned perception"; "perception allocation planner"; "query selection occlusion driving"; "expected gain tool selection". 1,460 unique notes; keyword-filtered to 74 driving-plus-query/tool/uncertainty hits; all titles read, 7 abstracts read. Closest: Ask the World (4YOXy9OdU4), StreamSelect (KQwcH95tnN), VLAlert (G6vrRbO3NE), DriveAgent-R1 (r2g8TV4nJy). All already in papers.csv or not relevant (FocusVLA is manipulation view routing from predicted intent).
- Batch 2: groups ICLR.cc/2027, CoRL/2026, ICLR.cc/2026 x 10 terms: "planner candidate set which tool to query"; "evidence acquisition for planning decisions"; "cost-aware perception querying vision-language driving"; "active perception autonomous driving vision-language tool"; "occluded hazards traffic light ambiguity driving benchmark tool"; "ranker margin query abstain driving"; "trajectory critic perception tools"; "information-seeking action autonomous vehicle VLM"; "counterfactual value of observation planner"; "sensing decision candidate actions disagreement". 1,120 notes, 47 unseen driving/candidate hits; abstracts read for X06N9Uuw7m, 899Uym6doj, SAVE k0GGfvnT5G, D-JEPA 7qpkedfwN3. None is candidate-conditioned query selection.

GitHub (api.github.com/search/repositories, 4 to 8 s apart; the unauthenticated limit of 10/min was hit once and waited out):

- "active perception autonomous driving vlm", "driveagent-r1", "tool selection driving agent", "agentic autonomous driving tool in:description", "active perception autonomous driving in:description": DriveAgent-R1 (wczheng, Tsinghua-MARS-Lab mirror), Ishita-29/nuScenes-Agent, qq1018408006/Agentic-autonomous-driving-toolkit (README 404), Safe_Occlusion_Aware_Planning (RSS21), kostasoiko4 anomaly-detection repo (not relevant). READMEs read for nuScenes-Agent and the anomaly repo.
- Multiword queries ("candidate trajectories vlm selector", "metadrive vlm tool", "query selection planner driving budget", "information gathering AD occlusion", "value of information perception driving", "which sensor to query planner", "metadrive hazard occlusion", "perception query planner", "conformal planner vlm driving", "trajectory scorer vlm driving") returned 0 or irrelevant spam repos.

arXiv listing re-filter: `/home/user/CASS-VLA/research/2026-11-06_cass_vla_sota/listing_sweep/html*` (171,806 unique ids), my own title regexes (which sensor/tool/view, where to look, decision/plan-aware perception, value of information, information seeking, active perception/sensing, perception/sensing budget/allocation/on-demand, selective/adaptive perception, query selection/policy/budget, tool selection/routing/gating, decision-focused, when to look/query/call) AND (driving|vehicle|planner|trajectory|robot|embodied|VLA|agent), minus ids in papers.csv: 99 titles, all read. Abstracts read for 2608.13605, 2610.23891, 2609.03142, 2603.08128, 2611.06434, 2602.01266: robotics/embodied, none candidate-conditioned tool choice. Script: `/tmp/claude-1000/-home-user-CASS-VLA/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/Z1/sweep2.py`.

## Papers

Only items new to papers.csv (grep by id or title, 2026-11-07). Closest first.

### Algorithm to generate planning-based attention signals (US12179756B2, GM)
- id: US12179756B2 (application US20240101107A1) | date: 2024-12 (granted; priority 2022-09-27) | venue: US patent, GM Global Technology Operations LLC
- authors: Jafari Tafti, S. R.; Bacchus, B. N. R. | code: none
- relevance: MED — a learned per-actor attention score whose target is how much the planner's trajectory changes when the actor is removed. Same family of label as "decision gain", for which actor rather than which tool.
- what: A DNN on a scene graph outputs an attention score per actor. Claim 1 builds the training signal by sampling actor-state scenarios from their uncertainty distributions, generating a sample trajectory per scenario with all actors and again with a removed actor, averaging each set, and taking the maximum waypoint distance D_i between the two average trajectories. The vehicle drives the trajectory computed with the attention scores.
- thesis use: prior art for plan-change labels (cite next to What's Hidden Matters 2607.00283). Does not touch tool choice, candidate sets, abstain, or a budget curve.
- verified: page fetched (Google Patents abstract and claim 1 read)

### AnA: An Attentive Autonomous Driving System
- id: DOI 10.1145/3669940.3707261 | date: 2025 | venue: ASPLOS 2025 (ACM, pp. 33 to 46)
- authors: Choe, W.; Wang, R.; Lin, F. X. | code: none seen
- relevance: MED — planner-to-perception query interface with standing and ad-hoc queries; the closest systems-side statement of "the planner decides what perception to buy".
- what: Refactors an ADS so the planner requests focused perception tasks (e.g. high-accuracy localisation of specific agents) and perception allocates compute accordingly. Per a third-party review (not the authors), headline claims are 3x fewer collisions and 44% less compute, against open-loop perception-only heuristic baselines, with a first-pass detector on every frame.
- thesis use: related work for "planner-driven perception"; cite as a systems precedent that is rule-based and has no learned selector or tool choice.
- verified: page fetched (NSF PAR record: title, authors, DOI, no abstract) plus review page text. Numbers are from the reviewer's quotation of the paper and are UNVERIFIED against the paper itself.

### An Adaptive Multimodal End-to-End Autonomous Driving Framework Based on Behavior Discrepancy (G-VLM)
- id: DOI 10.1109/TITS.2026.3706626 | date: 2026-10 | venue: IEEE Transactions on Intelligent Transportation Systems 27(10), pp. 13113 to 13124
- authors: not captured from the page (Beijing Institute of Technology repository record) | code: none seen
- relevance: MED — a learned gate trained from the discrepancy between a lightweight controller and the VLM-assisted output (a gain-style label), decides when to run the expensive semantic module. Binary, no candidate set.
- what: G-VLM gates the expensive VLM on scene context and confidence estimates. CARLA closed-loop: 96.8% of the always-invoked VLM driving score at 12.2% of its compute, and up to 9.8 driving-score points over compute-matched alternatives (abstract).
- thesis use: baseline family for "when to call" gates with gain labels; supports the argument that "which tool" is the unaddressed part.
- verified: page fetched (abstract read verbatim)

### RISE: Adaptive Imagination for World Action Models
- id: arXiv:2608.20430 | date: 2026-08 | venue: arXiv preprint
- authors: Lu, Hongbo et al. | code: none seen
- relevance: MED — sequential Roll/Stop decision on the expected planning benefit of more computation, trained with counterfactual supervision. Driving (NAVSIM, nuScenes). Whether, not which.
- what: A Latent Evaluator estimates risk and the possible planning improvement, a Rollout Gate trades benefit against compute. Introduces CounterDrive, a counterfactual dataset with expert annotation. Reports best overall planning with less unnecessary rollout (no numbers in abstract).
- thesis use: related work for expected-benefit gating; counterfactual data construction idea.
- verified: abs meta fetched

### Planning driven perception system for autonomous driving vehicles (US10551840B2 / EP3633408)
- id: US10551840B2, EP3633408A1 | date: filed about 2018 | venue: patent (Baidu, per search result snippets; assignee not checked on the primary page)
- authors: not captured | code: none
- relevance: LOW — planner trajectory yields a driving intent and regions of interest, fed back so perception processes only selected sensors.
- what: Plan to perception feedback with sensor selection, rule-based; no gain labels, no candidate set, no budget evaluation.
- thesis use: prior-art citation for "plan tells perception what to process".
- verified: UNVERIFIED (search-result snippets only)

### Occlusion-aware motion planning with information gain (US11834077)
- id: US11834077B2 | date: UNVERIFIED (one snippet said granted November 2022) | venue: US patent; assignee UNVERIFIED (one snippet said Symbol Technologies, which looks wrong)
- authors: inventors listed as Jen, Singh, Smith (snippet) | code: none
- relevance: LOW — scores candidate trajectories by collision probability and by information gain, then selects one.
- what: The information gain is a property of the trajectory (it reveals occluded space), not a choice of perception query.
- thesis use: prior art for scoring candidate trajectories by information gain.
- verified: UNVERIFIED (snippet only)

### Perception testing (US2024354462A1, Gaffney, Meister, Barreto)
- id: US2024354462A1 | date: 2024 | venue: patent application
- authors: Gaffney et al. | code: none
- relevance: LOW — measures how often a decision-making component changes decisions when perception is ablated vs ground truth.
- what: Decision-change as the measure of perception importance, an offline test method, not a runtime selector.
- thesis use: prior art for decision-change as value of perception.
- verified: UNVERIFIED (snippet only)

### nuScenes-Agent: A Multi-Camera Tool-Calling Benchmark for Agentic Autonomous Driving
- id: github.com/Ishita-29/nuScenes-Agent | date: 2026 (repo pushed 2026-08) | venue: anonymous NeurIPS 2026 Datasets and Benchmarks submission (per README)
- authors: anonymous | code: github.com/Ishita-29/nuScenes-Agent
- relevance: LOW — 5,000 QA pairs, 9 perception tools, scores camera selection and tool orchestration; an LLM picks tools, no candidate trajectories.
- what: ReAct-style agent with get_camera_view, detect_objects, estimate_depth, estimate_velocity and others; process-level evaluation of tool calls.
- thesis use: possible benchmark for the tool-selection half; not decision-conditioned.
- verified: page fetched (README read); no paper found

### Learning Value of Information towards Joint Communication and Control in 6G V2X
- id: arXiv:2505.06978 | date: 2025-05 | venue: arXiv preprint
- authors: not captured | code: none seen
- relevance: LOW — DRL estimate of utility-based VoI for driving decisions, used to decide which V2X information to share.
- what: VoI as the benefit of extra information for sequential driving decisions, trained offline with missing vs full information.
- thesis use: citation for learned VoI in driving (communication side).
- verified: UNVERIFIED (search snippet only)

### CODEI: Resource-Efficient Task-Driven Co-Design of Perception and Decision Making
- id: arXiv:2503.10296 | date: 2025-03 | venue: arXiv preprint
- authors: Milojevic, D. et al. | code: none seen
- relevance: LOW — "occupancy queries" quantify what a sampling-based planner needs from perception; ILP picks sensors and algorithms at design time.
- what: Design-time sensor and algorithm selection from planner-derived perception requirements; not a runtime selector.
- thesis use: related work for planner-derived perception requirements.
- verified: abs meta fetched

### Information-Driven Active Perception for k-step Predictive Safety Monitoring
- id: arXiv:2603.23450 | date: 2026-03 | venue: arXiv preprint
- authors: Udupa, S. et al. | code: none seen
- relevance: LOW — schedules sensor queries under a strict query budget to maximise information gain about future safety; HMM/DFA setting, not driving.
- what: Minimises k-step conditional entropy of future safety under a sensor query budget; validated on a congestion game.
- thesis use: classical-theory contrast (information gain about state vs gain on the decision).
- verified: abs meta fetched

### When to Wake a Vision-Language Model (SoTA Letters blog post)
- id: sotaletters.substack.com/p/when-to-wake-a-vision-language-model | date: 2026-06-16 | venue: blog
- authors: Kyuhwan Yeon (Oxford Robotics Institute), per the post | code: none checked
- relevance: LOW — anomaly gate on frame embeddings wakes a VLM; the VLM flags a risky region and candidate trajectories passing through it are penalised, then the planner re-picks.
- what: Frozen planner proposes candidates; VLM woken on about 11% of routine vs 37% of long-tail frames (as quoted in the fetched summary; the PDMS figures are only in an image).
- thesis use: another scene-anomaly trigger baseline; the candidate set is used after the VLM call, not to decide it.
- verified: page fetched (summary; numbers UNVERIFIED against raw text)

### Learning Occlusion-aware Decision-making from Agent Interaction via Active Perception (Pad-AI)
- id: arXiv:2409.17618 | date: 2024-09 | venue: arXiv preprint
- authors: Jia et al. (per snippet) | code: none checked
- relevance: LOW — RL over semantic motion primitives including probing motions to reduce occlusion uncertainty; the sensing action is a manoeuvre, not a tool query.
- what: Learned active-perception behaviours for occluded intersections.
- thesis use: related work, vehicle-motion active perception vs tool-query active perception.
- verified: UNVERIFIED (search snippet only)

### Rethinking World Models for Safety-Critical Embodied Systems
- id: arXiv:2609.03774 | date: 2026-09 | venue: arXiv preprint (perspective)
- authors: Ma, Kailang et al. | code: none
- relevance: LOW — argues for decision-relevant representation and for recognising "when to act, revise, sense, defer, or abstain".
- what: Position paper proposing the Risk-Informed World Model; no experiments.
- thesis use: motivation citation for the accept/inspect/replan/fallback policy phase.
- verified: abs meta fetched

## Leads not followed

- Full text of AnA (ACM DL is paywalled; no arXiv found): check whether its planner-side query generation uses candidate plans.
- Claim-level read of US11834077, US10551840 and US2024354462A1 on Google Patents (only snippets seen).
- Kasra Rezaee patent family (Justia): a snippet mentioned scoring candidates by collision probability plus information gain; number and assignee not confirmed.
- OpenReview abstracts only for Ask the World; if it gains a public PDF, check whether its viewpoint selection is learned and whether a budget sweep exists.
- Non-English venues and CNKI; ICRA/IROS 2027 and CVPR 2027 submissions (no OpenReview group).
- Semantic Scholar cited-by lists for DriveAgent-R1 beyond the OpenAlex pass others did (not used here to respect the shared-IP rule).
