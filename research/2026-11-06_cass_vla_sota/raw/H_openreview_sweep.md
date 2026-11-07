# H_openreview_sweep

Source for every entry: OpenReview search API records (title, keywords, abstract) fetched 2026-11-06. Only abstracts were read (PDFs and direct note lookups return 403), so claims about methods are limited to what the abstract says. ICLR 2027 authors are anonymous (double-blind), so the authors field says so. The record `cdate` gives the month. verified = "openreview search record" for all entries.

## Summary

- NO CLOSE OVERLAP FOUND with candidate-conditioned perception query selection for driving. Across 36 ICLR 2027 queries (24 requested plus 12 targeted extras on plan-conditioned queries, VoI, candidate plans, etc.) no abstract says the query/tool is chosen from how the candidate trajectories diverge. This rests on abstracts only; the three nearest neighbours below should be full-text checked.
- NEAREST 1, most important: "The Decision Value of Perception Compute" (DEEP, id l9QJO8BIoE). Defines decision value = change in downstream loss from escalating cheap to expensive perception, scores allocators against a budget-constrained decision oracle on KITTI/nuScenes and open-loop nuPlan with PDM-Closed. Finds 34-54% of loss-changing escalations make it worse, perception gain disagrees in sign with decision value, learned allocators select nearly as much harm as random. It is the same framing (decision-aware, budget, oracle) but allocates perception compute, not tool choice, and does not condition on candidates. It is a strong citation and a possible benchmark protocol/competitor; it also supports the claim that scene-level triggers are weak.
- NEAREST 2: "Closed-Loop Agentic Reinforcement Learning for Vision-Language Driving Agents" (DynaChain, gJvWSNcUtw). Learns which questions to ask per frame, Bench2Drive-VL, Driving Score 58.93 to 79.15 with 2.52 questions vs 7. Argues value of a question is realised in the trajectory that follows. Selection is learned and closed-loop, but over VLM questions, not perception tools conditioned on candidate plans.
- NEAREST 3: "MosaicDrive" (9I96DzTfHb) argues confidence-triggered acquisition (the DriveAgent-R1 style) is structurally flawed because confidence is computed from evidence already held; supports the scene-uncertainty baseline critique. Also "Learning When to Search" (LlFRODPGr8) and "Foresight on Demand" (6pILFjKpgH): both train a lightweight gate on the realised planning-score gain, on nuPlan / NAVSIM, closest in training-target spirit to the "expected gain" targets.
- Trend 1: many 2026-09 submissions gate an expensive module (VLM call, RAG, search, foresight, replanning) by learned necessity: ETM, ARDrive, STAR-Drive, StreamSelect, Learning When to Search, Foresight on Demand, Learning When to Call. Targets are usually realised-gain pseudo labels, same as ours. None gates perception tools by candidate set.
- Trend 2: tool/zoom driving agents moved to RL with necessity terms (DriveScout) and to benchmarks of evidence sufficiency/abstention (DriveAnswer, DriveWHEN, RADIUS-Drive).
- Trend 3: generate-and-select driving planners with learned trajectory scorers are crowded (World4Scorer, CLOVER, CoFiDrive, PhyDrive, AttendingScorer, iDriveVLA). iDriveVLA names the "generation-evaluation asymmetry" (oracle best candidate exists but is not selected), which matches our oracle-best-candidate scoring.
- Calibration side: CoSA-Drive (calibrated bounds authorising candidate behaviours), TRIPWIRE (risk-calibrated commitment at matched escalation budget), "Risk Bounds for Physical AI" (MetaDrive runtime monitors) for the future conformal phase.
- Other groups: CoRL 2026 and ICML 2026 and ICLR 2026 return results (CoRL 2026 / ICML 2026 are public accepted records). ICRA 2027 (IEEE.org/ICRA/2027/Conference), CVPR 2027 (thecvf.com/CVPR/2027/Conference), AAAI 2027 (AAAI.org/2027/Conference) and NeurIPS 2026 (NeurIPS.cc/2026/Conference) returned zero notes (count 0) for a driving-tool query. DriveAgent-R1 itself is an ICLR 2026 Poster (id r2g8TV4nJy), which is useful for the citation venue.
- MetaDrive query in ICLR 2027: no tool-selection paper uses it; closest uses are BoundaryWorld (regret on MetaDrive) and Risk Bounds for Physical AI (MetaDrive monitors), COACH (MetaDrive interactive imitation).
- Group coverage (second pass): the full 24-term list was run on robot-learning.org/CoRL/2026/Conference, ICML.cc/2026/Conference and ICLR.cc/2026/Conference (about 70 calls, no 429s). Added 10 terms on thecvf.com/CVPR/2026/Conference and NeurIPS.cc/2025/Conference. Groups with results: CoRL 2026, ICML 2026, ICLR 2026, CVPR 2026, NeurIPS 2025, NeurIPS 2025 Datasets_and_Benchmarks_Track. Groups with count 0: IEEE.org/ICRA/2027/Conference, IEEE.org/ICRA/2026/Conference, thecvf.com/CVPR/2027/Conference, thecvf.com/ICCV/2025/Conference, AAAI.org/2027/Conference, AAAI.org/2026/Conference, NeurIPS.cc/2026/Conference, NeurIPS.cc/2026/Conference/Submission, NeurIPS.cc/2026/Datasets_and_Benchmarks_Track.
- Second pass found nothing that changes the overlap verdict: still no candidate-conditioned perception query selection for driving in any searched venue. New context only: OmniDrive-R1 (CVPR 2026 Findings, RL zoom-in), HybridDriveVLA (CVPR 2026, waypoint evaluation), CAPAgent (perception-model replacement shift).
- arXiv versions: only iDriveVLA has one (arXiv:2609.30818, confirmed via absfetch). The other HIGH items have no arXiv version found, so cite them as OpenReview submissions, and mark that reviews are not public in these records.

## Papers

### The Decision Value of Perception Compute (DEEP: Decision Evaluation for Escalated Perception)
- id: https://openreview.net/forum?id=l9QJO8BIoE | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, decision-value of an extra perception step under a budget against a decision oracle, in driving (closest framing to the project)
- what: Defines decision value of perception compute as the change in downstream loss when escalating from cheap to expensive perception, and scores pre-escalation allocators against a budget-constrained decision oracle with their own compute charged. With monocular geometry on KITTI/nuScenes, 34-54% of escalations that change loss make it worse; on nuScenes perception-level gain often disagrees in sign with decision value; choosing signals by perception gain loses 7.4% of all-cheap loss. Learned allocators select nearly as much harm as random; at a 20% latency budget only routers at about 3.5% of a detector pass beat random. Also evaluated open-loop on nuPlan with PDM-Closed.
- thesis use: competitor/related work and evidence that perception-level uncertainty is a poor trigger; borrow the "charge the selector for its own compute" and oracle-budget protocol. Contrast: it routes whole-input perception modes, not tool choice conditioned on candidates.
- verified: openreview search record (abstract only)

### Closed-Loop Agentic Reinforcement Learning for Vision-Language Driving Agents (DynaChain)
- id: https://openreview.net/forum?id=gJvWSNcUtw | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: "will release" (no url)
- relevance: HIGH, learns which questions to ask per frame, value judged by the trajectory outcome
- what: Formalises reasoning-chain selection as a closed-loop MDP; DynaChain decides at each frame which questions to ask before acting, trained with closed-loop agentic RL on Bench2Drive-VL. Raises Driving Score from 58.93 to 79.15 while asking 2.52 questions per decision instead of seven; the gain comes from which questions are asked, and requires learned selection plus closed-loop training. A fixed chain of questions drives worse than answering nothing.
- thesis use: competitor/related work; supports "selection matters more than answer accuracy". Contrast: question set is VLM reasoning, not perception tools, and it is not conditioned on candidate trajectories.
- verified: openreview search record (abstract only)

### MosaicDrive: Task-Aware Multi-Camera Reasoning for Autonomous Driving
- id: https://openreview.net/forum?id=9I96DzTfHb | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, tool-using driving agent that decides which camera/tool to acquire; explicit critique of confidence-triggered retrieval
- what: Argues the confidence that triggers retrieval in tool-augmented driving agents is computed from evidence already held and says nothing about unobserved regions, and that extra evidence can override a correct prior judgement. Derives camera and tool requirements from the question, requires evidence before answering, and uses a source-aware verifier (Arbiter) with targeted re-queries. Evaluated on MOSICQA with executed tool traces under a protocol separating coverage from selectivity, and answer quality from acquisition cost. (Numbers not in abstract.)
- thesis use: related work / argument against scene-uncertainty triggering (the DriveAgent-R1 style baseline); tool-requirement is derived from the question, not from candidate plans.
- verified: openreview search record (abstract only)

### Learning When to Search: Adaptive Test-Time Computation for Generative Motion Planning
- id: https://openreview.net/forum?id=LlFRODPGr8 | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, decides whether to run candidate generation + scoring, trained from where search helps
- what: Shows the benefit of candidate search varies across planning steps; a lightweight history-aware model decides after the base trajectory is generated whether to search. On nuPlan closed loop: score 86.07 with search on 56.81% of steps versus Full Search 85.64 at 100%; beats fixed schedules at similar rates.
- thesis use: related work for budget-vs-accuracy Pareto of a gate; it gates search over candidates, not perception tools; the gate sees the base trajectory (partly candidate-aware).
- verified: openreview search record (abstract only)

### Foresight on Demand: Learning What and When to Predict for Autonomous Driving (FD-WAM)
- id: https://openreview.net/forum?id=6pILFjKpgH | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, router trained on realised planning-score difference with vs without an extra information source
- what: Utility-Aware Selective Foresight trains a router with the realised planning score difference between the planner's foresight and no-foresight paths, deciding from observed history alone; plus a decision-relevant foresight representation. Evaluated on NAVSIM v1/v2 and zero-shot HUGSIM. (Numbers not in abstract.)
- thesis use: closest training-target analogue to our "expected gain" labels; cite as precedent for gain-supervised gating.
- verified: openreview search record (abstract only)

### ETM: Event Trigger Module based VLM for Autonomous Driving
- id: https://openreview.net/forum?id=oa4EWvJlLC | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, information-gain-driven decision of when to invoke a VLM, with cost
- what: Lightweight trigger policy that activates the VLM only when refreshed semantic reasoning is expected to improve planning; trained with corner-case labels plus information-gain pseudo-labels. On nuScenes keeps planning accuracy comparable to always-triggered while cutting VLM invocation from 100% to 32%, latency by nearly 50% and compute by about 64%.
- thesis use: baseline-style competitor for "scene-level trigger" (when, not which); informs always-on vs budget comparison.
- verified: openreview search record (abstract only)

### DriveScout: Sharpening MLLM Perception in Autonomous Driving with Adaptive and Robust Visual Focusing
- id: https://openreview.net/forum?id=rXDM54aQdX | arXiv: none found (WebSearch by exact title, 2026-11-06; not confirmed absent) | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: HIGH, zoom/crop tool use as selective evidence acquisition with a necessity term (DriveAgent-R1 follow-up type)
- what: RL framework for Think-with-Images driving MLLMs; Target-Grounded Spatial Credit plus Necessity-Aware Focus Optimization and a progressive blur curriculum; introduces SCOUT, a paired nuScenes driving VQA benchmark with motion-blur variants. Improves blur robustness and reduces redundant visual operations (numbers not in abstract).
- thesis use: competitor for ROI tool; benchmark with degradation levels similar to our tool-noise levels.
- verified: openreview search record (abstract only)

### ARDrive: Adaptive Retrieval-Augmented Generation for Autonomous Driving
- id: https://openreview.net/forum?id=uoY7qJgd6f | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, learns whether to retrieve with performance-gain pseudo-labels then RL on accuracy vs cost
- what: Learnable [RAG] token as a dynamic retrieval gate; SFT with pseudo labels from RAG vs No-RAG outcome comparison, then RL optimising accuracy-cost trade-off. Cuts reasoning latency 14% and RAG activation 34% while improving over always-RAG on public AD benchmarks.
- thesis use: related work on gain-labelled gating (same label recipe as ours).
- verified: openreview search record (abstract only)

### STAR-Drive: Selective Trajectory Adoption and Replanning for Autonomous Driving
- id: https://openreview.net/forum?id=LxrYLWBb3c | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, decides when to query and whether to adopt a new trajectory over the active one
- what: Training-free runtime: trajectory-guided scheduling of VLA calls plus world-aware selection comparing a new candidate with the remaining active trajectory. Evaluated on 913 closed-loop AlpaSim scenarios (results truncated in the record I read).
- thesis use: related work (trajectory-aware query timing, accept/replan policy for the future phase).
- verified: openreview search record (abstract only)

### Adaptive Inference for Streaming Multimodal Scene Understanding in Autonomous Driving (StreamSelect)
- id: https://openreview.net/forum?id=KQwcH95tnN | date: 2026-08 | venue: ICLR 2027 withdrawn submission
- authors: Yitao Chen et al. (Toyota Motor North America) | code: none
- relevance: MED, learned activation model decides when updated VLM reasoning is needed (LiDAR BEV queries over camera tokens)
- what: StreamSelect-Act scores when to invoke a pluggable VLM. Withdrawn, so cite with care. (Already in B_budgeted_perception.md.)
- thesis use: when-to-query baseline family.
- verified: openreview search record (abstract only)

### Learning When to Call: Predictive Opportunity Ranking for Embodied Agents
- id: https://openreview.net/forum?id=wTUAMalMEE | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, budgeted placement of expensive reasoning calls on CARLA
- what: Predictive Reasoning Scheduler scores from recent state history and BEV context, with a budget/cooldown selector; offline evaluation on frozen CARLA Town10HD trajectories, covering 23 of 63 event windows with 165 calls versus about 6 for Random-k (UWC@0.5s gain 26.71 points, 95% bootstrap interval 12.64-40.97).
- thesis use: budgeted call-placement baseline; random-k comparison and bootstrap reporting style.
- verified: openreview search record (abstract only)

### iDriveVLA / "Evaluation Is All You Need for Multi-Modal Autonomous Driving"
- id: https://openreview.net/forum?id=C3148YmmVH | arXiv:2609.30818 (absfetch confirmed: He, Zeyu et al., 2026-09-25; title "Evaluation Is All You Need for Multi-Modal Autonomous Driving"; NAVSIM v1 94.95 PDMS) | date: 2026-09 | venue: ICLR 2027 desk rejected submission; arXiv preprint
- authors: anonymous | code: none
- relevance: HIGH for the ranker side, names the generation-evaluation asymmetry: oracle best candidate is strong but planners fail to select it
- what: Unified trajectory evaluator (Safety-aware Scorer plus VLM-guided Modulator weighting criteria per scene) and an oracle-aligned objective. Desk rejected, so treat as a preprint-level claim.
- thesis use: motivates oracle-best-candidate scoring; ranker/critic baseline idea.
- verified: openreview search record (abstract only)

### World4Scorer: Outcome-Grounded World Modeling for Autonomous Driving
- id: https://openreview.net/forum?id=kx17FJ7sj6 | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, generate-and-select scorer with simulator outcome labels for every candidate (similar label idea to our privileged-simulator oracle)
- what: Trajectory-conditioned JEPA-style predictor produces a state per candidate and reads scores from it; simulator outcome labels supervise all candidates, executed future anchors it; inertial re-ranking for consistency; NAVSIM. (Already in L4_listing_t3b.md.)
- thesis use: ranker/critic baseline; label design.
- verified: openreview search record (abstract only)

### CLOVER: Closed-Loop Value Estimation and Ranking for End-to-End Autonomous Driving Planning
- id: https://openreview.net/forum?id=aEnMj4snBH | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, proposal-selection planner: scorer fitted to evaluator sub-scores, set-level candidate coverage
- what: Evaluator-filtered pseudo-expert trajectories for coverage, trajectory-level scorer fitted to true sub-scores, refinement toward teacher top-k and Pareto targets. Notes performance depends on candidate-set coverage and ranking quality.
- thesis use: ranker side; supports separating candidate coverage from ranking quality.
- verified: openreview search record (abstract only)

### CoFiDrive: Scene-Conditioned Registers and Coarse-to-Fine Trajectory Scoring for End-to-End Driving
- id: https://openreview.net/forum?id=Cw9PCXgOOd | date: 2026-08 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, candidate-dependent gated attention over scene features when scoring proposals
- what: 64-token scene memory from four cameras and a Cross-Compression Scorer where each proposal attends to coarse context and local patch features. Candidate-conditioned feature gathering, but inside the planner, not a tool query.
- thesis use: idea to borrow (candidate-conditioned feature access) for the selector features.
- verified: openreview search record (abstract only)

### PhyDrive: Planning-Oriented Physical Evidence Interaction for End-to-End Autonomous Driving
- id: https://openreview.net/forum?id=aahyqE80FX | date: 2026-08 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, Physical-Evidence-Guided Scorer on candidate-specific latents for safety-aware selection
- what: Extracts planning-oriented physical evidence to guide interaction between candidate latents and scene context; world-model auxiliary training. (No numbers in abstract excerpt.)
- thesis use: ranker/critic competitor.
- verified: openreview search record (abstract only)

### AttendingScorer: An End-to-End Driving Evaluator that Read Out Trajectory Evaluation Score from latent of Vision-Language-Model
- id: https://openreview.net/forum?id=1PXDojdzMH | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, VLM as a comparative evaluator between competing trajectories; reads a score out of frozen VLM latents via small query embeddings (TrajSteering)
- what: Trains only query embeddings, leaving VLM weights untouched, to obtain a quantitative trajectory score.
- thesis use: related to frozen-VLM-features-into-a-head (our +0.3 to +0.7 point embedding gain); candidate for a stronger VLM readout.
- verified: openreview search record (abstract only)

### CoSA-Drive: Counterfactual Safety Authorization for Vision-Language-Action Models in Autonomous Driving
- id: https://openreview.net/forum?id=dJM2YZT7VW | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED (future phase), calibrated confidence bounds authorise candidate behaviours that meet a risk constraint, with replanning on rejection
- what: Defence experts propose behavioural candidates; authorizer CERA predicts safety, intervention harm and utility; calibrated bounds authorise; a deterministic DriveContract checks rules and triggers replanning.
- thesis use: idea to borrow for the accept/inspect/replan/fallback phase.
- verified: openreview search record (abstract only)

### TRIPWIRE: Risk-Calibrated Commitment for Tool-Using Agents
- id: https://openreview.net/forum?id=lZTCitkTMi | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED (future phase), calibrate an escalation policy to residual harm among autonomously executed actions, reported at matched escalation budgets
- what: Commitment risk from failure likelihood and irreversibility, minus expected fallback risk, calibrated to a target; reduces realised harm vs uncertainty-based routing at matched budgets. Not driving (LLM tool agents).
- thesis use: framing for the calibration phase (matched-budget comparison).
- verified: openreview search record (abstract only)

### Risk Bounds for Physical AI: Decision Ambiguity and Model Incompleteness
- id: https://openreview.net/forum?id=ysYgzJzdpr | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED (future phase), runtime assurance risk bound with a MetaDrive study of detect-and-brake monitors
- what: A hidden fault scaling braking to 70% causes 21 failures in 120 drives selected for nominal success; none of twelve frozen monitors passes the intervention screen. The MetaDrive study does not estimate the bound itself.
- thesis use: MetaDrive precedent for monitor evaluation; cautionary on monitor claims.
- verified: openreview search record (abstract only)

### Benchmarking Evidence Sufficiency in Vision-Language Models for Autonomous Driving (DriveAnswer)
- id: https://openreview.net/forum?id=8ixTIlnnkc | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, benchmark where abstention is correct under weak evidence (20,151 questions, matched strong/weak evidence)
- what: Best zero-shot baseline reaches 64.69% strong-evidence accuracy but 41.96% matched-pair success; sufficiency supervision restores selective behaviour; DriveAnswer-Gemma reaches 81.58% matched-pair success.
- thesis use: benchmark/idea for "when is evidence insufficient" labels; supports our observation that VLMs say "none"/overanswer.
- verified: openreview search record (abstract only)

### When Should the Decision Change? Counterfactual Probing of Vision-Language Models for Autonomous Driving (DriveWHEN)
- id: https://openreview.net/forum?id=3f2j5QOg7N | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, paired counterfactual interventions on nuScenes; VLMs often fail to revise actions when a hazard is introduced
- what: Four atomic interventions (left/right lateral intrusions, forward departure, appearance control) with human-assigned required actions; five VLMs tested. Supports weak VLM decision sensitivity.
- thesis use: motivates why prompting the VLM to pick tools fails; paired-evaluation design.
- verified: openreview search record (abstract only)

### Seeing with Tools, Reasoning with Language: Recasting Vision as Structured Scene Text for Driving VQA (DriveTLM)
- id: https://openreview.net/forum?id=BsBw6uPTUQ | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, training-free delegation of visual extraction to tools with rule-based or agentic tool selection; DriveBench and LingoQA
- what: Tool outputs are organised into structured scene text so the answering model needs no visual tokens; compares rule-based and agentic tool selection. (Abstract excerpt truncated before numbers.)
- thesis use: baseline for rule-based vs agentic tool selection.
- verified: openreview search record (abstract only)

### ALERT: A Self-evolving Agent for Latent Risk Reasoning in Autonomous Driving
- id: https://openreview.net/forum?id=1SmxzSXO4o | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, tool-augmented risk agent with a skill pool; benchmark from real takeover data; +11.7% over best VLM-only baseline. (Already in B and F.)
- thesis use: context only.
- verified: openreview search record (abstract only)

### Not Every Tool Call Helps: Fine-Grained Credit Assignment for Efficient Tool-Integrated Reasoning (GAPO)
- id: https://openreview.net/forum?id=q2GHLB1Im7 | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, per-call "observable correctness gain" estimator; tool overuse is pervasive; many calls redundant or harmful (LLM maths, not driving)
- thesis use: idea to borrow: per-tool gain targets, same as our expected-gain labels; supports "some tool calls hurt".
- verified: openreview search record (abstract only)

### EviRover: Reinforcing Agentic Perception Beyond a Glance
- id: https://openreview.net/forum?id=lmBrAHq07w | date: 2026-08 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, agentic perception under insufficient evidence; 4B model, +30 points on EviLens (688 instances); not driving
- thesis use: related work for tool-based perception RL.
- verified: openreview search record (abstract only)

### AskStream: When and What to Ask Proactively under Uncertainty in Streaming Video Understanding
- id: https://openreview.net/forum?id=KtoceE7tyD | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, wait/ask/answer action space with frame-level windows (438 videos, 2,714 windows); ask-for-information framing
- thesis use: related work for abstain/ask.
- verified: openreview search record (abstract only)

### Wait or Take Over: Forecasting OOD Persistence and Recovery for Efficient Human-in-the-Loop Imitation Learning (ReGIL)
- id: https://openreview.net/forum?id=D6tiZjxnTx | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, robot-gated request-for-help decision; learned support-persistence value from Hamilton-Jacobi reachability; MetaDrive appears in the keyword search hit
- thesis use: related work on when-to-ask under a human-effort budget. Companion: COACH (id 38SDKqRg3g, "What to Learn and Who to Ask", MetaDrive and MetaWorld).
- verified: openreview search record (abstract only)

### Judge, Then Act: A Critic-Centric Vision Language Action Framework for Autonomous Driving (CriticVLA)
- id: https://openreview.net/forum?id=CKVUqG4YQf | date: 2026-05 | venue: CoRL 2026 Poster (accepted)
- authors: Lijin Yang et al. | code: none seen in record
- relevance: MED, VLA-based critic refines a rough trajectory; 12.9M annotated synthetic trajectories (already in F_vlm_features.md)
- thesis use: critic/ranker baseline; accepted venue.
- verified: openreview search record (abstract only)

### Observe Before You Alert: Belief-State Driver Alerting with Vision-Language Models (VLAlert)
- id: https://openreview.net/forum?id=G6vrRbO3NE | date: 2026-05 | venue: CoRL 2026 Poster (accepted)
- authors: Yuhang Wang et al. | code: none seen in record
- relevance: MED, tri-action Silent/Observe/Alert policy; Observe defers to gather evidence; VLM hidden states pooled as belief (already in F)
- thesis use: abstain/defer-with-observation action design; frozen-VLM-hidden-state head.
- verified: openreview search record (abstract only)

### An Adaptive Slow-Fast Framework for Real-Time Anomaly Detection in Autonomous Driving (SOFA)
- id: https://openreview.net/forum?id=eGZ6YMFVzU | date: 2026-05 | venue: CoRL 2026 Poster (accepted)
- authors: Zhenyu Zong et al. | code: none seen in record
- relevance: LOW-MED, TTC-driven switch between fast LiDAR anomaly detector and slow VLM reasoning
- thesis use: a hand-set geometric trigger baseline comparable to our scene-uncertainty trigger.
- verified: openreview search record (abstract only)

### Deliberation Meets Reaction: A Dual-Expert VLA framework for Autonomous Driving (DE-Driver)
- id: https://openreview.net/forum?id=rHcWxVrDFV | date: 2025-09 | venue: ICLR 2026 submission (record says "Submitted to ICLR 2026"; outcome unknown)
- authors: Jialong Xie et al. | code: none
- relevance: LOW-MED, scene-aware router between reactive and deliberative experts
- thesis use: scene-level router baseline family.
- verified: openreview search record (abstract only)

### FocusDrive: Reasoning with Visual Focus for Autonomous Driving
- id: https://openreview.net/forum?id=8POknkNPgC | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, explicit visual focus patches in planning reasoning; W3DA and NAVSIM
- thesis use: ROI-focus idea.
- verified: openreview search record (abstract only)

### OmniDrive-R1: Reinforcement-Driven Interleaved Multi-Modal Chain-of-Thought for Trustworthy Vision-Language Autonomous Driving
- id: https://openreview.net/forum?id=dNKg4pJzWP | date: 2025-12 | venue: CVPR 2026 Findings (accepted)
- authors: Zhenguo Zhang et al. | code: none seen in record
- relevance: MED-HIGH, VLM learns by RL to "zoom in" on critical regions as part of interleaved CoT (end-to-end, no tool call separation); reduces object hallucination. May duplicate A_driving_tool_agents.md.
- thesis use: ROI-zoom competitor and an accepted-venue citation for the ROI tool; abstract excerpt has no numbers.
- verified: openreview search record (abstract only)

### HybridDriveVLA: Vision-Language-Action Model with Visual CoT reasoning and ToT Evaluation for Autonomous Driving
- id: https://openreview.net/forum?id=K3AX8S6KFw | date: 2025-12 | venue: CVPR 2026 (accepted)
- authors: Yipene Cedric Francois Bassole et al. | code: none seen in record
- relevance: MED, generates and scores several waypoint sequences per aspect (safety etc.) with a Tree-of-Thought style evaluation, i.e. a VLM candidate-trajectory evaluator
- thesis use: ranker/critic baseline; may duplicate C_trajectory_critics.md.
- verified: openreview search record (abstract only)

### WOD-E2E: Waymo Open Dataset for End-to-End Driving in Challenging Long-tail Scenarios
- id: https://openreview.net/forum?id=9IYYm8abSy | date: 2025-12 | venue: CVPR 2026 (accepted)
- authors: Runsheng Xu et al. | code: none seen in record
- relevance: MED, 4,021 long-tail segments (about 12 h, 8 cameras), Rater Feedback Score open-loop metric that scores trajectories against rated alternatives
- thesis use: real-data open-loop benchmark with a multi-candidate-aware metric for a later transfer test. May duplicate E_benchmarks.md.
- verified: openreview search record (abstract only)

### CAPAgent: Keeping Spatial Agents Reliable When Their Perception Models Change
- id: https://openreview.net/forum?id=BP4U7GABJ8 | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: MED, agent decides how far to trust external perception tools (depth, pose, grounding) from quality cues; trained on one tool model, breaks when the model changes; CapSwap-Bench replays model replacements
- thesis use: matches our tool-noise levels: a selector learned at one noise level may under-react to another; borrow the replacement/noise-shift test.
- verified: openreview search record (abstract only)

### Switch-Reasoner: Learn When to Think in Multitask Mixtures via Reinforcement Learning
- id: https://openreview.net/forum?id=wpp6QPc1ln | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW-MED, treats thinking as a virtual tool call; sample-level supervision from the relative benefit of the two choices; 11 multimodal tasks, not driving
- thesis use: gain-based supervision precedent for tool vs no-tool.
- verified: openreview search record (abstract only)

### Spatial Tool Forests for Structured Spatial Reasoning
- id: https://openreview.net/forum?id=bHkx233O78 | date: 2026-09 | venue: ICLR 2027 submission (under review)
- authors: anonymous (under review) | code: none
- relevance: LOW, query-driven tool-chain planning with MCTS over a spatial tool library; tool-selection ambiguity as the motivation
- verified: openreview search record (abstract only)

### Planner-Breaker, CornerBench, Bench2Drive-Plan, RegAD, HazardArena (checked, not added as full blocks)
- ids: JlkIX1gcs0 (adversarial traffic producing avoidable collisions, about 3x more than gradient adversaries across five planners), MiNv8dHfC7 (CornerFactory/CornerBench corner-case benchmark from real logs with severity-aware metrics), 1smcK59muV (privileged planners under Bench2Drive; ground-truth inputs give no inherent advantage), SxhwcceBih (regressive planner with soft-label scorer on NAVSIM/nuPlan), 6nfZRQG4KQ (safe/unsafe twin scenarios for VLA semantic safety, manipulation).
- relevance: LOW; Planner-Breaker and CornerBench could serve as hazard-generation ideas.
- verified: openreview search record (abstract only)

## Leads not followed

- Full text is unavailable via OpenReview (403). arXiv search by exact title found no versions of DEEP, DynaChain, MosaicDrive, Learning When to Search, Foresight on Demand, ETM or DriveScout (WebSearch is not exhaustive); only iDriveVLA has arXiv:2609.30818. Re-check these in a few weeks and read the full text of DEEP, DynaChain, MosaicDrive before claiming novelty.
- OpenReview searches only see title/keywords/abstract; a paper that has no driving word in these can be missed. For CoRL 2026 / ICML 2026 / ICLR 2026 I filtered titles and keywords by driving terms and read abstracts of the likely ones only.
- Not read: CVPR 2026 papers Spatial Retrieval Augmented Autonomous Driving (96syuYXH30), ActiveAD (ir3oDh3ZFI, active learning, not perception queries), LiDAS (DRx3yJSYyz, active sensing at night), SearchAD; NeurIPS 2025 AutoVLA is the fast/slow adaptive reasoning one (already known to other agents).
