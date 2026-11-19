# AUDIT3: third-wave changes to REPORT.md

Checked on 2026-11-06, about 23:45 PST. Diff base: `REPORT_prewave3.md`. Sources: arXiv html and abstract pages (fetched), cached html in `scratchpad/html_X4`, the DriveAgent-R1 GitHub README, `papers.csv`, `references.bib`.

## Verdict table

| Claim | Section | Verdict | Evidence | Fix |
|---|---|---|---|---|
| DriveAgent-R1 has an explicit per-call cost, C_tool = 0.125 | 3.3 | CONFIRMED | v3 App. A.5: gain 0.25 amortised over a median of 2 calls, C_tool = 0.25/2 = 0.125. It is a heuristic, not a measured cost. | none |
| The VLM emits a learned mode token `<think_tool>` or `<think_text>` | 3.3 | CONFIRMED | Sec 2.1 ("generating either a <think_text> or <think_tool> token"); chosen by Stage 3 RL | none |
| Inputs are "first frame, speed and navigation command" | 3.3 | OVERSTATED | The paper says "initial visual context I_0 (front-view camera)" and "vehicle speed and navigation". The prompt says "front-view image ... from the current frame". "First-Frame" in the paper is an accuracy metric name, not an input. | Write "an initial front-view image, speed and navigation command" |
| It never sees candidate trajectories | 3.3, 7.5 | CONFIRMED | It outputs a 4-step meta-action sequence; there is no candidate set. | none |
| "Tool necessary" data comes from an accuracy gap between a large model with and without tools | 3.3 | CONFIRMED with nuance | App. A.4 Step 1: Qwen2.5-VL-3B first removes samples with text-mode accuracy above 0.9. Then a 72B "oracle" marks as tool-necessary the samples where tool mode gives a "significant performance gain" over text mode. The label is binary per sample, not per tool. | Add "after a 3B filter" and "per sample, not per tool" so "close to our expected-gain label" is not over-read |
| Its toolkit has no collision check | 3.3 | CONFIRMED | App. A.2 tools: Retrieve View, RoI Inspection, Depth Estimation, 3D Object Detection | none |
| Training code public; evaluation code and weights not | 3.3 | CONFIRMED | README fetched today: only "Training Code" ticked; evaluation scripts, datasets and weights are "pending company approval" | none |
| Training DriveAgent-R1 is out of scope because "its data is internal" | 5 | OVERSTATED | Training code is public and the paper also tests on nuScenes. Only Drive-Internal (35K clips) is internal, plus the weights. | "because its Drive-Internal data and weights are unreleased" |
| MosaicDrive's critique of confidence triggers is "the same critique" the project makes of DriveAgent-R1 | 2 | OVERSTATED | Wave 3 shows the trigger is a learned mode token, not a confidence score. The README still speaks of "uncertainty" and "scene complexity", so the critique holds only as "scene-only trigger". | "...makes a related critique of DriveAgent-R1, whose learned mode token sees only the scene" |
| Best-of-Evidence arXiv:2607.20950 id and title match; "read in full" | 2 | CONFIRMED | html title and body match. But `papers.csv` still says "no arXiv version found; not read in full". | Update the csv `verified` text for 2607.20950 |
| BoE values each action by plug-in EVSI per unit cost | 2 | CONFIRMED | Eq. 11 "plug-in score"; "ranked by EVSI-hat/c(e)"; Limitations: "myopic plug-in EVSI-per-cost rule" | none |
| "No model is trained" in BoE | 2 | CONFIRMED with nuance | Discrimination indices kappa and outcome frequencies are estimated from the same ledger used for evaluation ("same ledger"); the paper says this is "not a fitted joint observation model". The estimation is in-sample. | Optionally add "its channel statistics are estimated in-sample" |
| Quote "BoE is 0.26-0.58 percentage points above raw majority across the four cells" | 2 | CONFIRMED | Sec 5.2 "BoE is 0.26 – 0.58 percentage points above raw majority across the four cells" (en dash in the paper). Table 2: VQA-Med +0.26, PMC-VQA +0.58. | none (dash only) |
| BoE beats random acquisition significantly only on VQA-Med | 2 | CONFIRMED with nuance | Table 2: only VQA-Med excludes zero (+1.11 [0.43, 1.80], McNemar 0.0022). The paper calls all analyses "exploratory and uncorrected". Also, BoE vs raw is significant on PathVQA and PMC-VQA. | Add "exploratory, uncorrected" |
| "Among the agents read in full, only DriveAgent-R1 has an explicit per-call cost" | 3.3 | CONFIRMED | Scoped to driving agents. BoE has a cost c(e) per action but is not a driving agent. | none |
| Plug-in VOI selector "is the only baseline here that chooses among tools without learning" | 5 | WRONG | The next listed baseline, the counterfactual-rollout selector, also picks a tool with no learning ("picks the tool that changes the choice most"). The VOI selector also uses per-family average gains, which are fitted from training data. | "chooses among tools with no trained model" and drop "only", or say it uses tabulated gains |
| Pre-2025-07 papers in 3.6: ids match the names (all ten) | 3.6 | CONFIRMED | Abstract pages: 2004.08745 PKL; 2110.03270 Planning-Awareness; 2305.01870 Task-Aware Risk; 2312.02467 HOIST; 1909.08792 Agent Prioritization; 1003.3967 Adaptive Submodularity; 1207.1394 Nonmyopic VOI; 2301.00557 Covert et al.; 1711.05187 Dynamic Zoom-in; 2311.10813 Agent-Driver | none |
| PKL, 2110.03270 and 2305.01870 as "planner-centric perception metrics" | 3.6 | CONFIRMED | Abstracts measure perception by downstream planning impact. 2305.01870 is a risk estimator, not a metric, but the grouping is fair. | none |
| HOIST and Agent Prioritization as "counterfactual importance labels" | 3.6 | OVERSTATED | HOIST generates counterfactual scenarios. Agent Prioritization assigns ground truth from "the causes of various planner actions" logged from running the planner. That is not counterfactual. | "Importance labels from the planner's behaviour: counterfactual in HOIST, logged planner causes in Agent Prioritization" |
| Adaptive submodularity and nonmyopic VOI as "budgeted value of information" theory; "our one-call selector is the single-step case" | 3.6 | OVERSTATED | Abstracts: adaptive greedy with guarantees (1003.3967) and subset selection with a (1-1/e) approximation (1207.1394). Neither is explicitly budgeted VOI for tool choice. "Single-step case" is our own framing, taken from the P agent's note. | Mark the last sentence as our interpretation |
| Covert et al.: learned greedy acquisition of the most informative feature | 3.6 | CONFIRMED | Abstract: greedy conditional mutual information, amortised | none |
| Dynamic Zoom-in predicts the gain of zooming into each region | 3.6 | CONFIRMED | Abstract: R-net predicts the accuracy gain of a higher-resolution region. "Closest classic to our ROI tool" is a judgement. | none |
| Agent-Driver calls tools by function calls without a budget | 3.6 | CONFIRMED | Abstract: tool library via function calls. The full html has no budget or cost mechanism (its tools include a collision check on the trajectory). | none |
| "Reference lists of the six closest papers" | 3.6, 10 | OVERSTATED | Section 1 lists five closest papers (2611.06702, SIGMA, DEEP, DualDriveVLA, Proof-of-Perception). `raw/R_backward_refs.md` used six: those minus Proof-of-Perception, plus Calibrate-Then-Delegate and BoE. | "the six papers in `raw/R_backward_refs.md`" |
| Counts: 530 rows, 60 HIGH | header, 10 | CONFIRMED | csv: 530 rows, HIGH 60 (306 MED, 163 LOW, 1 blank). HIGH rows are the first 60. | none |
| One paper has no relevance rating | data | WRONG (csv defect) | Row 2604.27366 (Judge, Then Drive) has an empty `relevance`, so the tiers sum to 529 + 1. | Set it to MED or LOW |
| references.bib has 54 entries, "54 HIGH papers with arXiv ids" | 10 | CONFIRMED | 54 `@` entries. 54 of 60 HIGH rows have an arXiv id (56 rows overall have none), and the 54 bib ids equal those 54 exactly. | none |
| Files in section 10 exist | 10 | CONFIRMED except AUDIT3.md | Present: REPORT, AUDIT, AUDIT2, RELATED_WORK_DELTA, papers.csv, references.bib, BRIEF, PLAN, known_papers.txt, verify_cache/report json, raw/A..H, L1..L4, M1..M7, X1..X4, R_, P_, Y_, Z_, listing_sweep/. AUDIT3.md is this file. | none |
| "Five papers were checked only through OpenAlex records" | 9 | OVERSTATED | `raw/P_prior_classics.md` shows 4 entries marked "OpenAlex record only" plus 2 more named in its closing notes (6). | "about five or six" or "six" |
| Report finished "by about 00:05" | header | UNVERIFIABLE | At the time of this audit it is about 23:45. The time is in the future. | Put the real finish time |
| HIGH-count history in section 8 ("makes it 50") vs 60 now | 8 | OVERSTATED | Section 8 is still correct as history, but it has no note that wave 3 added 10 HIGH rows, and no entry on wave-3 corrections. | Add a line that wave 3 raised HIGH from 50 to 60 |
| `raw/Y_leads_followup.md` calls OCP "same family as DriveAgent-R1" (scene/confidence-threshold trigger) | raw, not report | OVERSTATED | Same issue as the MosaicDrive line: DriveAgent-R1's trigger is a learned mode token. Not in REPORT.md. | Note only |

## WRONG / OVERSTATED, most serious first

1. **Section 5, "the only baseline here that chooses among tools without learning" (WRONG).** The counterfactual-rollout baseline two bullets below also chooses a tool with no learning. The VOI baseline also relies on average gains fitted from training data. Drop "only" and say "no trained model".
2. **papers.csv row 2604.27366 has no relevance tier (WRONG).** Fix before anyone filters by tier. The tier counts only add up to 530 with this blank row.
3. **Section 2, MosaicDrive line (OVERSTATED).** After wave 3 the DriveAgent-R1 trigger is a learned mode token, not a confidence trigger. State the critique as "scene-only trigger".
4. **Section 3.6, Agent Prioritization as "counterfactual" (OVERSTATED).** Its labels are logged planner causes.
5. **Section 3.6, "single-step case" and "budgeted VOI" (OVERSTATED).** These are our framing. The abstracts do not say it.
6. **Section 3.3, "first frame" (OVERSTATED).** Use "initial front-view image". Add the 3B pre-filter and that the label is per sample, not per tool.
7. **Section 5, "its data is internal" (OVERSTATED).** Only Drive-Internal and the weights are unreleased.
8. **"Six closest papers" vs "five closest papers" (OVERSTATED).** Name the set.
9. **Section 9, "five papers" OpenAlex-only (OVERSTATED).** The raw file shows six.
10. **Header time "00:05" (UNVERIFIABLE).** Use the real time.
11. **Section 8 does not record the wave-3 change from 50 to 60 HIGH (OVERSTATED, minor).**
12. **papers.csv BoE row still says "no arXiv version found; not read in full"** (stale versus REPORT.md; the row text is in the `verified` field).

## Section 1 and section 5 re-read

- Section 1 novelty claim holds. DriveAgent-R1's trigger sees only the scene and BoE works outside driving, so neither removes the claim. Wave 3 does show that DriveAgent-R1's training labels are an oracle-gain contrast, which weakens "trained on decision gain" as a novelty point if stated alone. The claim is still safe because ours is per tool and candidate-conditioned.
- Section 1 "Averaged over query budgets, it beats ... ranker margin and random selection" and the five limits are unchanged by wave 3. I did not recheck the numbers in `docs/baseline_results.md`, which is modified in the working tree.
- Section 5 "scene-uncertainty ... baselines" fits: the DriveAgent-R1 proxy is correctly labelled a scene-only learned trigger.
- Section 7.5 "Its trigger is a learned mode token that sees only the scene" is correct, but `RELATED_WORK_DELTA.md` P2 line 58 still has the old "scene uncertainty" wording as the text to be replaced. Check that the delta file offers the new wording.
