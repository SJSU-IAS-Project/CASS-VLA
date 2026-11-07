# State of the art: choosing perception queries for a driving planner

The scan started on 2026-11-06 at 22:30 PST. This report was written at about 23:05 and revised after two
audits by about 23:35. A third wave of agents and a third audit extended it by about 23:55, and two
falsification agents added to section 1 by about 00:10. It covers papers from 2025-07 to 2026-11, plus older papers that are clearly essential.
`papers.csv` holds 561 papers, and 63 of them are HIGH. arXiv listings for cs.RO, cs.CV, cs.AI
and cs.LG were filtered by title, 171,806 unique papers in all. The closest competitors were read in full.

## 1. Result

No paper we found chooses among several perception tools for a driving planner based on how its candidate
trajectories diverge. None evaluates that choice as top-1 accuracy against a query budget, next to
scene-uncertainty, random and oracle selectors. This is an absence over the papers we found, not over the
field. Seven close OpenReview submissions could be read only as abstracts: FD-WAM, Learning When to Search,
ETM, DynaChain, MosaicDrive, DriveScout and "Certifying the Information Value of Adaptive Tool Use".

Two agents then tried to falsify this. One ran about 60 web searches, including patents, plus GitHub and
OpenReview searches, and re-filtered all 171,806 listing titles; it found no counterexample. The other searched
neighbouring fields. It found most parts of the mechanism outside driving. No neighbour has the budget curve against an oracle
selector. Two examples show how far the neighbours get:

- **CLARINET** (arXiv:2405.15784, retrieval). It conditions on the retrieval distribution over candidates and
  is fine-tuned "to generate the question that would have maximized the rank of the true candidate". It
  chooses among generated questions, not among kinds of information source, and has no "ask nothing" option.
- **BudgetVerify** (arXiv:2609.33052, financial QA). It has no candidate set. It routes each answer to no verification, a light check or
  a costly check. Its router is "trained from offline correctness and token-cost outcomes", with Pareto
  frontiers against fixed policies.

So the mechanism of choosing a query from the candidate set, trained on its counterfactual gain, has
precedents. What the scan did not find is the combination. That is a learned choice among different perception tools
or none, conditioned on how K driving trajectories diverge. It is shown on one budget curve against
uncertainty, random and oracle selectors. Two near misses were found. Ask the World (OpenReview 4YOXy9OdU4, abstract only) is a manipulation paper. It
turns a proposed action correction into a viewpoint query. In driving, a GM patent, US12179756B2, comes close. The patent
trains an attention model on plan-change labels from planning with and without each actor.

The broader idea is no longer new. Several 2026 papers decide whether to acquire information by its effect on
the plan rather than by scene uncertainty. Several also show that extra evidence can hurt and that
uncertainty is a weak trigger. The project has to cite these as prior work.

A defensible novelty claim:

> We study which perception query a driving planner should make, given its candidate trajectories. A learned
> selector chooses among ROI inspection, depth and a collision check, or abstains. It uses features of how the
> candidates diverge and is trained on each tool's decision gain. Averaged over query budgets, it beats the
> same learner without candidate features, ranker margin and random selection. It is evaluated in
> hazard-injected MetaDrive at three tool-noise levels, against an oracle selector and a fair ceiling.

The biggest open risk is the size of the candidate-conditioning gain. Our own results show five limits:

- The selector leads the scene-only MLP by only 1 to 2 points on average.
- It falls behind that rival at 0.95 and 1.00 calls per decision at mid noise, and at 1.00 with high noise
  or blocked ROI.
- It falls behind on `occluded_cross_traffic` on the final split at mid noise and half a call per decision
  (0.330 against 0.347). With 510 seeds and expected-gain targets, on the test split at mid noise and averaged
  over budgets, it leads there (0.297 against 0.272).
- The features that describe where the top two candidates part ways changed the logistic selector by less than
  0.01. The four features whose shuffling hurts most are all scene features.
- The headline table uses single-draw targets. With expected-gain targets and 510 seeds, the lead grows in
  four of six cells.

DEEP (below) also reports that learned allocators "select nearly as much harm as random", even though they
capture more benefit than random.

The five closest papers:

| Paper | What it does | What it lacks next to the project | Code |
|---|---|---|---|
| When to Ask for Help, arXiv:2611.06702 (off-road robot) | Rescores its fixed MPPI rollouts under resolved map hypotheses, and requests the aerial map layer with the largest gain, or none. The paper calls this "an optimistic form of value of information". | Not driving. Rule-based argmax with a threshold, not learned. One operating point per policy: no budget sweep, and no scene-uncertainty, random or oracle baseline. | anonymous project page |
| SIGMA, arXiv:2610.09520 (CARLA) | Calls a cloud VLM when the "expected planning gain" (EPG, Eq. 17) is high. EPG averages the relative change in MPC cost over sampled scene realizations. | One binary decision. No choice among tools, and no candidate set (one MPC trajectory). Baselines are local-only and fixed-period calls. No budget sweep. | partial (uncertainty estimator only) |
| DEEP, "The Decision Value of Perception Compute", arXiv:2609.35910 (ICLR 2027 submission) | Defines the value of escalating perception as the signed change in downstream loss. Scores allocators against a budget-constrained decision oracle on KITTI, nuScenes and open-loop nuPlan. | One escalation type (detector resolution), not a choice among tools. No candidate conditioning. | none found |
| DualDriveVLA / HybridDriveVLA, arXiv:2602.10719 (NAVSIM) | Gates a VLM call with a trajectory-conditioned scorer on the fast path's trajectory. Calls the VLM in about 15% of scenarios for 91.00 PDMS. | Gates a model call, not a perception tool. No tool choice. | announced; the GitHub link returned 404 |
| Proof-of-Perception, arXiv:2603.00324 (document, chart and multi-image QA) | A learned controller chooses among OCR, detector and chart tools, using per-node conformal sets, and sweeps a budget of 8 to 24. | Not driving, and no plans: the trigger is the node's own uncertainty. No random or oracle baseline. | github.com/AryaFayyazi/PoP |

## 2. Close papers found late in the run

The OpenReview sweep found five more driving papers that gate an expensive step on its value to the plan. All
five are abstract-only.

- **Foresight on Demand (FD-WAM)**, OpenReview 6pILFjKpgH. Its router is trained on "the realized planning
  score difference between the same planner's foresight and no-foresight paths". This is the closest training
  target to our expected-gain labels. It is a binary gate that sees history only.
- **Learning When to Search**, OpenReview LlFRODPGr8. It decides when to run candidate generation and scoring.
  On closed-loop nuPlan it scores 86.07 with search on 56.81% of steps, against 85.64 for search at every step.
- **ETM**, OpenReview oa4EWvJlLC. It is a learned VLM-call trigger trained on information-gain pseudo-labels
  combined with corner-case labels. On nuScenes it calls the VLM on 32% of steps.
- **DynaChain**, OpenReview gJvWSNcUtw. It learns which of seven reasoning questions that a driving VLM should ask,
  with closed-loop RL on Bench2Drive-VL. Driving Score rises from 58.93 to 79.15 with 2.52 questions instead
  of 7.
- **MosaicDrive**, OpenReview 9I96DzTfHb. It argues that a confidence trigger "is computed from evidence the
  agent already holds, and so carries no information about regions it has never observed". The project's critique of DriveAgent-R1 is related but narrower: its
  trigger is a learned mode token that sees only the scene, not a confidence score.

Three papers outside driving are close in method:

- **Best-of-Evidence**, arXiv:2607.20950 (also OpenReview U1JptdfbDT; read in full in wave 3). It keeps a
  best-of-N candidate pool fixed and spends a limited budget on "evidence actions that can change the final
  choice", in four medical VQA settings. Outside driving, this is the nearest idea to candidate-conditioned
  query selection that the scan found. Each action is valued by a plug-in expected value of sample information
  per unit cost, and no model is trained. Its channel statistics are estimated on the same ledger it is evaluated on. Its gains are small. The paper
  says that "BoE is 0.26–0.58 percentage points above raw majority across the four cells", and only on
  VQA-Med does its interval against random acquisition exclude zero. The paper calls these analyses
  "exploratory and uncorrected".

- **Calibrate-Then-Delegate**, arXiv:2604.14251, in LLM safety monitoring. A probe predicts the benefit of an expert call, and a
  Learn-then-Test threshold sets it under a budget.
- **To Call or Not to Call**, arXiv:2605.00737. It finds that "utility estimation remains substantially harder
  than need estimation". Utility is the case our candidate features are meant to help with.

## 3. What changed in the field, mostly since 2025-07

1. **Triggers are moving from uncertainty to decision value.** Seven papers score a query or a mode switch
   by its effect on the plan. They are SIGMA, DEEP, FD-WAM, Learning When to Search, 2611.06702, BLUE (2606.08684)
   and ASSCG (2606.25509). ETM is close, but its labels measure information gain rather than plan quality. BLUE says that scene complexity and kinematic features "struggle to predict" when
   language helps, while frozen VLA hidden states "potentially already encode" it. Calibration Is Not Control
   (arXiv:2606.21399) shows the same outside driving. Changing only the supervision target, from failure risk
   to intervention value, cuts regret from 0.513 to 0.094 on ALFWorld.
2. **Most adaptive driving systems choose how much to think, not what to look at.** Examples are AdaThinkDrive
   (2509.13769), AdaDrive (2511.06253), CAR-VLA (2609.34387), BLUE and ASSCG. None of them chooses a
   perception query.
3. **Tool-using driving agents multiplied, but none conditions on candidates or reports a budget curve.** Drive
   by Hindsight and Foresight (2609.08217) has 27 tools and calls at least one on 99.5% of queries. OmniDrive-R1
   (2512.14044) caps tool calls at 5. AgentThink (2505.15298) and MTRDrive (2509.20843) do not report call counts.
   Among the agents read in full, only DriveAgent-R1 has an explicit per-call cost (C_tool = 0.125). Its
   trigger is not a raw uncertainty score. The VLM emits a learned mode token, `<think_tool>` or `<think_text>`,
   from the initial front-view image, speed and navigation command. It never sees candidate trajectories. Its
   "tool necessary" training data keeps the samples on which a 72B model gains significantly from tools. That
   label is binary per sample, not a gain per tool like ours. Its toolkit has no collision check. Its training
   code is public, but the Drive-Internal data and the weights are not.
   DriveAgent-R1's training code is public, but its evaluation code and weights are not, so it has to be
   re-implemented as a trigger.
4. **Audits show that VLMs often call visual tools without using the result.** The Illusion of Visual Tool-Use
   (2608.06270) audits six models. It finds two failure modes. In one of them, the returned crop has no causal
   effect on the answer. A calibrated minority of calls carries the gain. In ToolGate (2606.03054), 78.3% of calls leave
   the immediate answer unchanged, and 9.9% change it from right to wrong.
5. **Candidate scorers keep improving, with a large oracle-best gap.** DriveSuprim (2506.06659, June 2025): the
   best candidate in the top-K rises from 91.9 PDMS at K=1 to 98.7 at K=256. RRDrive (2609.21486) moves the
   oracle-best candidate's average rank from 33.9 under the baseline scorer to 27.7. It does so by adding a
   risk profile to each candidate. Its Table 5 compares scorers that see geometry, risk or both. So adding
   information to a scorer is studied. What we did not find is a per-decision choice of which information to
   acquire, under a budget.

6. **The idea has older roots that the related work should cite.**
   - **Planner-centric perception metrics** score perception by its effect on a planner. Examples are PKL
     (2004.08745), planning-aware metrics (2110.03270) and task-aware risk (2305.01870).
   - **Importance labels from the planner** come from HOIST (2312.02467), which uses counterfactuals, and Agent
     Prioritization (1909.08792), which logs the causes of planner decisions.
   - **Budgeted value of information** has theory in adaptive submodularity (1003.3967) and nonmyopic value of
     information (1207.1394). In our own framing, the one-call selector is a single-step case of these.
   - **Learned greedy acquisition** of the most informative feature is in Covert et al. (2301.00557).
   - **Predicting the gain of zooming** into each region is in Dynamic Zoom-in (1711.05187), the closest classic
     to our ROI tool.
   - **Earlier driving tool use** is in Agent-Driver (2311.10813), which calls tools by function calls without a
     budget.
   - These come from a sweep of pre-2025-07 work, and from the reference lists of six close papers: SIGMA,
     DEEP, 2611.06702, DualDriveVLA, Calibrate-Then-Delegate and Best-of-Evidence.
     Several venues in that sweep were not checked.

## 4. The Phase 5 VLM results against the literature

- **Related work points the same way as our weak prompting result, though none of it tests a VLM choosing a
  perception tool.**
  - In DriveJudge (2606.17362, Table 3), a prompted VLM without tools scores 50.06 AUC at judging trajectories.
    Zero-shot tools raise it to 56.13. Fine-tuning without tools gives 68.67, and tools with fine-tuning give
    77.95.
  - When2Tool (2605.09252), a text-only LLM study, finds that prompting suppresses needed tool calls along with
    unneeded ones. A linear probe on hidden states predicts tool necessity much better.
  - The "Certifying the Information Value" submission (OpenReview JUWtWs4Tgb) studies language models on
    network diagnosis. It reports that in its tests, adaptive querying did worse than pre-committed querying
    when the models chose their own queries.
  - Our VLM saying "none" on about 92% of validation decisions fits this pattern.
- **Small gains from frozen embeddings are expected.**
  - Auditing Latent-Space Monitors (2609.30557) finds that the VAD planner's latent features add nothing over ego
    state, command and the planned trajectory. Endpoint AUROC is 0.868 with latent features, 0.924 without and 0.917 with both.
  - Perceives but Doesn't Brake (2610.28184) decodes hazard presence at AUC 0.998 while the planner still
    intrudes.
  - Our +0.3 to +0.7 point gain should be reported with intervals and against the geometry baseline, as it is.
- **The layer and pooling choice is open.**
  - ProbeAct (2606.09740) finds spatial pooling at layer 8 beats the image-token mean and the last token.
  - HALP (2603.05465) finds that query-token states beat vision-token states on Qwen2.5-VL-7B.
  - `embed.npz` already holds `image_last` and `last_token`. Trying them needs fresh seeds, because the current
    choice was fixed before evaluation (DECISIONS.md).
- **A blank-image control is needed.** DriveBench (2501.04003) finds that for a significant portion of models,
  accuracy barely drops with a black image, and 2606.31257 warns that probes can overstate grounding.

## 5. What this means for the evaluation

Our existing results partly cover the core comparison, with the limits listed in section 1. The selector MLP leads the scene-only MLP, the same
learner without candidate features, by +0.016, +0.011 and +0.017 at low, mid and high noise. All three 95%
bootstrap intervals are above zero, though they are not corrected for multiple comparisons. It leads ranker margin by 6 to 10 points and random by at least 0.016 at
every budget above zero. These numbers come from `docs/baseline_results.md`.

Metrics to add, from DEEP:
- Harm selected and benefit captured, separately, because a tool call can move the ranker away from `c*`.
- Normalized decision gain, measured against the budget-constrained oracle.
- A paired bootstrap over scenes.

Baselines to add, in rough order of cost:
- Ego speed, which is cheap and a DEEP baseline.
- A fixed schedule at a matched call rate, from Learning When to Search.
- A binary gate trained on "any tool helps", with scene features only, in the style of ETM and AdaDrive.
- A KnowNo-style trigger that calls when the ranker's conformal set over the K candidates is not a singleton
  (KnowNo, 2307.01928).
- A trigger on disagreement among the candidates alone, which tests BOKBO's warning (2605.30660). This is
  trivial to build.
- A plug-in value-of-information selector, adapted from Best-of-Evidence. The adaptation is ours, not the
  paper's. It scores each tool by the average gain for the hazard family, times the chance that the call
  changes the ranker's choice. Like the counterfactual-rollout selector below, it chooses among
  tools without training a model, though its family averages are estimated from training data.
- A DriveAgent-R1 proxy: a scene-only learned trigger, labelled by whether the best tool's gain exceeds a margin.
  Retraining DriveAgent-R1 itself is out of scope for a course project. Its training code is public, but its
  evaluation data and weights are not, and it would need a VLM trained by reinforcement learning.
- A counterfactual-rollout selector in the style of 2611.06702. It sets each uncertain element to its
  alternatives and reruns the ranker on the same candidates. It then picks the tool that changes the choice
  most. This is about one day of work.

Benchmark caveats:
- Offline metrics correlate poorly with closed-loop results (2510.08571), so open-loop accuracy is a
  limitation to state.
- No benchmark we found covers occluded or ambiguous traffic lights, so the `ambiguous_light` family fills a gap.
- WOD-E2E (2510.26125) has rater scores for 3 trajectories per example, picked from a filtered pool of fewer
  than 12. It is a weak real-data match to "K candidates with an oracle best".

## 6. Evidence that cuts against the project

- **Learned allocators select nearly as much harm as random.** DEEP: learned allocators "beat random by
  capturing more benefit but select nearly as much harm". At a 20% selection budget they capture about a
  third of the oracle's beneficial value. When each allocator is charged for its own compute at a 20% latency budget, only the lightweight
  routers still beat random. Its setting is detector resolution on KITTI, nuScenes and open-loop nuPlan.
- **Extra perception often hurts.** In DEEP's monocular-geometry settings, 34–54% of escalations that change the
  downstream loss make it worse.
  FD-WAM says foresight "can even degrade planning when its predictions are inaccurate". Our own curves fall past about 0.7 calls per decision.
- **Candidate divergence may be uninformative.** BOKBO (2605.30660) warns that disagreement among candidates
  can be uninformative when the candidates come from noise-perturbed sampling, in manipulation. Our candidates
  are distinct manoeuvres, so the warning applies only loosely.
- **The planner may ignore what perception gives it.** In Perceives but Doesn't Brake (2610.28184), all K=6
  unguided samples intrude in 21.5% of scenes. Reranking those samples cannot help there, which is our
  inference. On seen CARLA sites, exact obstacle geometry cut intrusion from 58.1% to 14.5%. A tool helps only if its output can change the ranker's choice.
- **Reviewers may want closed-loop results.** DynaChain, AdaDrive and SIGMA are evaluated closed loop.

## 7. Suggested next steps

1. Add DEEP's harm and benefit split and nDG to `eval_baselines.py`, using the existing per-tool gain tables.
   No new simulation is needed.
2. Add the ego-speed, fixed-schedule, any-tool gate and KnowNo-style baselines to the Pareto plot.
3. Report how the selector's lead over the scene-only MLP varies by hazard family, on one split and budget
   setting. On `occluded_pedestrian` the lead is 0.105 on the final split at half a call per decision. It is
   0.048 on the test split with 510 seeds, averaged over budgets.
4. Add a blank-image control to the VLM feature experiment.
5. Rewrite the related-work gap in `docs/literature_survey.md` around tool choice and candidate divergence.
   Cite SIGMA, DEEP and 2611.06702 as the nearest prior work. Also reword the proposal's claim that DriveAgent-R1
   triggers tools on scene uncertainty. Its trigger is a learned mode token that sees only the scene. `RELATED_WORK_DELTA.md` has the suggested
   wording.
6. For the calibration phase, start from Localized Conformal Safety Monitoring (2610.02765) and BCEA
   (2606.16667). BCEA shows that calibration must use the scores after acquisition.

## 8. Corrections the checks made

`AUDIT.md` checked 75 claims in the first draft. By leading verdict it rated 56 CONFIRMED, 13 OVERSTATED,
5 WRONG and 1 UNVERIFIABLE. Before changing them, the main thread re-checked the RRDrive, BLUE and
family-table items against the sources (`raw/Z_main_thread_checks.md`). These are the changes:

- **RRDrive.** The draft said that no paper varies the information given to the scorer. RRDrive's Table 5 does,
  so the claim now says that no paper chooses per decision which information to acquire. The 33.9 rank belongs
  to the baseline scorer; RRDrive reaches 27.7.
- **BLUE and ASSCG.** They moved from the "how much to think" group to the decision-value group. BLUE trains its
  gate on whether language will help.
- **WOD-E2E.** Raters score 3 trajectories per example, not up to 64.
- **Our own results.** "Already cover the core comparison" became "partly cover". Section 1 now lists five
  limits. They are the 1 to 2 point lead, the top-budget losses, `occluded_cross_traffic`, the small effect of
  the divergence features, and the single-draw targets.
- **Family-level numbers.** The `occluded_pedestrian` lead now names its split and budget. It is 0.105 on the
  final split at half a call, and 0.048 on the test split with 510 seeds.
- **DEEP.** "May barely beat random" became "pick harmful calls almost as often as random". The 34–54% figure
  is now limited to DEEP's monocular-geometry settings.
- **Prompting evidence.** Section 4 no longer says that prompting is "known to work poorly". None of the three
  sources tests a VLM choosing a perception tool. The quote from the "Certifying" submission was paraphrased,
  because the draft had dropped "in our tests".
- **Tool audits.** The Illusion and ToolGate findings were narrowed to what each paper measured.
- **Scope of other claims.** BOKBO's warning applies to noise-perturbed sampling. The Value-of-Intervention link
  to hazard families was removed, because that paper's heterogeneity is temporal. SIGMA also has a local-only
  baseline. DriveBench's black-image finding covers "a significant portion of models", not all.
- **Internal errors:**
  - Section 2 wrongly said "all except DEEP". The seven abstract-only submissions are now named in section 1.
  - The HIGH count was corrected: the merge gave 51, and the AS-DDTO downgrade makes it 50.
  - The scan-time line was corrected.
  - DriveSuprim (June 2025) is now dated.
  - The HybridDriveVLA code cell now says the link returned 404.

`AUDIT2.md` checked the revised draft. Most corrections held. It found these, all now fixed:

- **Best-of-Evidence.** It is on arXiv as 2607.20950, confirmed from the abstract page. The draft called it
  OpenReview-only.
- **DriveJudge.** 77.95 needs tools and fine-tuning together. Fine-tuning alone gives 68.67.
- **The audit tally.** The first revision miscounted AUDIT.md's verdicts.
- **Divergence features.** The under-0.01 result covers only the feature group for where the top two
  candidates part ways.
- **DEEP.** The heading now uses the paper's words ("nearly as much harm"), and the one-third figure is tied to
  the 20% budget.
- **ETM.** It is no longer counted among the plan-effect triggers, because its labels measure information gain.
- **Leftover AUDIT.md items.** These were the listing count, the multiple-comparisons caveat, "validation" on
  the 92%, the FD-WAM quote, ETM's labels, Proof-of-Perception's domain, OmniDrive-R1's tool cap, the VAD
  latents, and the K=6 and CARLA-site scope.

The third wave of agents raised the HIGH count from 50 to 60, mostly with pre-2025-07 foundations. `AUDIT3.md`
checked the additions. It found these, all now fixed:

- **DriveAgent-R1's inputs.** They are the initial front-view image, not "the first frame".
- **DriveAgent-R1's label.** It is binary per sample, so it is not close to our per-tool gain.
- **DriveAgent-R1's openness.** Its training code is public, so "its data is internal" was too broad.
- **Best-of-Evidence.** It now notes the in-sample statistics and the "exploratory and uncorrected" caveat.
- **Agent Prioritization.** It logs planner causes rather than counterfactuals.
- **Our framing.** The single-step value-of-information remark is now marked as our own.
- **The plug-in baseline.** It is not the only untrained tool chooser.
- **The MosaicDrive critique.** It fits DriveAgent-R1 only in part.
- **Counts.** The OpenAlex-only count is six, not five.

Two falsification agents then searched for a counterexample to section 1 (`raw/Z1_falsify_direct.md`,
`raw/Z2_falsify_neighbours.md`). `AUDIT4.md` checked the text that this added. It found that Ask the World is
a manipulation paper, not a driving one. It also found that BudgetVerify lacks the candidate-set part
entirely, and that no neighbour has the oracle-selector budget curve. All three are now fixed.


Checks made before the audit:
- **DEEP's arXiv version.** The OpenReview sweep reported no arXiv version of DEEP. The main thread confirmed
  arXiv:2609.35910 from the abstract page.
- **DriveBench.** A round-1 claim that DriveBench (2501.04003) proposes agentic tool use came from a search
  summary. The full text has no such method, and the claim was removed.
- **Counterfactual VLA (2512.24426).** The paper contradicts itself: the abstract and conclusion say safety
  +20.5%, while the introduction says 14.7%.
- **Two grouped blocks.** One is the CA-CP entry and the other groups five OpenReview titles. The ID checker
  attached a neighbour's arXiv ID to each, and papers.csv carries no ID for them.
- **AS-DDTO (2606.22277).** It was downgraded from HIGH to LOW after a full-text read.

## 9. How far to trust this

- **Abstract-only items.** Seven close OpenReview submissions could be read only as abstracts, because
  OpenReview PDFs return a bot challenge. Their numbers come from abstracts.
- **The title filter misses papers.** The listing sweep matched titles by keyword. A paper whose title avoids
  driving, tool or perception words was missed unless a topic search found it.
- **Venue fields.** Many papers have "arXiv preprint" because venues were not checked.
- **Cited-by coverage was thin.** OpenAlex had 0 citing works for most 2026 papers.
- **Older papers.** In the pre-2025-07 sweep, some venues came from the agent's memory and are marked
  UNVERIFIED, and six papers were checked only through OpenAlex records.
- **Numbers in math.** Some numbers inside equations were lost when tags were stripped. Agents marked those.
- **Scratch file collisions.** The triage agents shared one scratch file at first and overwrote each other's
  fetches. Each one re-fetched into its own folder, so the entries come from their own fetches.

## 10. Files

| File | What it holds |
|---|---|
| `REPORT.md` | this report |
| `AUDIT.md` to `AUDIT4.md` | the independent claim checks of each revision |
| `RELATED_WORK_DELTA.md` | changes to `docs/literature_survey.md` |
| `papers.csv` | 561 papers, HIGH first |
| `references.bib` | BibTeX for the 57 HIGH papers with arXiv ids |
| `BRIEF.md`, `PLAN.md` | the agents' brief, and the schedule with a log of what ran |
| `known_papers.txt` | the baseline papers, which the agents skipped |
| `verify_cache.json`, `verify_report.json` | arXiv id checks |
| `raw/A_*` to `raw/H_*` | topic agents and the OpenReview sweep |
| `raw/L*`, `raw/M*` | listing triage, for Jul to Nov 2026 and Jul 2025 to Jun 2026 |
| `raw/X1` to `raw/X4` | full-text reads of the closest papers and of the papers behind the baselines |
| `raw/R_backward_refs.md` | references mined from the six closest papers |
| `raw/P_prior_classics.md` | pre-2025-07 foundations |
| `raw/Y_leads_followup.md` | follow-up of unverified entries |
| `raw/Z1_falsify_direct.md`, `raw/Z2_falsify_neighbours.md` | the two attempts to find a counterexample |
| `raw/Z_main_thread_checks.md` | checks made in the main thread |
| `listing_sweep/` | listing pages, keyword file, candidates and tier files, triage briefs |
