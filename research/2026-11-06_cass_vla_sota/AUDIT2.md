# AUDIT2: second fact-check of the revised REPORT.md

Run 2026-11-06 23:17 to 23:30 PST. Method: `diff` of `REPORT_preaudit.md` against `REPORT.md`, then each changed or added sentence checked against fresh arXiv html (own scratch folder, tags stripped, math alttext kept), absfetch.py, the OpenReview search API (5 s apart), arXiv title search, `docs/baseline_results.md`, `docs/phase5_vlm.md`, `papers.csv` (python csv) and `references.bib`. OpenReview PDFs were not opened (bot challenge).

Verdicts: CONFIRMED / WRONG / OVERSTATED / UNVERIFIABLE. Only changed or added claims are listed, plus the AUDIT.md items that were left unchanged.

## 1. Table of changed and added claims

| # | Claim | Section | Verdict | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | `papers.csv` holds 462 papers, 50 HIGH | header, 10 | CONFIRMED | python csv: 462 rows, HIGH 50, MED 278, LOW 133, blank 1 (2604.27366 Judge, Then Drive, "anchor"). No duplicate keys or arXiv ids. AS-DDTO 2606.22277 is LOW | none. Optionally say "50 HIGH, 1 unrated" |
| 2 | "the merge gave 51, and the AS-DDTO downgrade makes it 50" | 8 | CONFIRMED | PLAN.md 23:05: "449 rows (51 HIGH)"; raw/Z_main_thread_checks.md: "2606.22277 relevance HIGH -> LOW" after the merge | none. Note the csv grew from 449 to 462 rows after the merge (raw/Y finished 23:13); the report does not say so |
| 3 | `references.bib` is "BibTeX for the HIGH papers with arXiv ids" | 10 | CONFIRMED | 44 entries, 44 unique; equals the set of HIGH rows that have an arXiv id (50 HIGH minus 6 OpenReview-only). Titles and years match the csv (DEEP year in csv is "UNVERIFIED (2026)", bib says 2026) | none |
| 4 | Seven abstract-only OpenReview submissions are FD-WAM, Learning When to Search, ETM, DynaChain, MosaicDrive, DriveScout, Certifying the Information Value | 1, 9 | CONFIRMED (none are on arXiv) | arXiv title and abstract search (quoted distinctive phrases) returned no match for any of the seven; all seven appear in papers.csv as "OpenReview ... abstract" with no arXiv id | none |
| 5 | Best-of-Evidence, OpenReview U1JptdfbDT, "(abstract only)" | 2 | WRONG | It is on arXiv: **2607.20950**, "Best-of-Evidence: Best-of-N Selection under Partial Verification", Zhang et al., 2026/07/23 (absfetch and html fetched). papers.csv says "no arXiv version found". Full text exists, so it was not abstract-only | Cite arXiv:2607.20950, change papers.csv verified/arxiv cells, read the full text before calling it "the nearest idea" |
| 6 | Best-of-Evidence is not in the "seven abstract-only" list, yet section 2 calls it abstract only | 1, 2, 9 | WRONG (internal) | Section 2 names eight abstract-only papers (the seven plus BoE) while sections 1 and 9 say seven. Resolved by #5 (BoE has full text), but the report as written is inconsistent | Fix with #5 |
| 7 | BoE "spends a budget on evidence actions that can change the choice among a fixed pool of candidates"; nearest idea outside driving | 2 | CONFIRMED (abstract) | Abstract: "keeps the BoN candidate pool fixed ... allocates a limited budget to evidence actions that can change the final choice". Domain is medical VQA | Say "medical VQA" |
| 8 | Novelty text: "Averaged over query budgets, it beats the same learner without candidate features, ranker margin and random selection"; "decision gain" | 1 | CONFIRMED | baseline_results.md result table, last five columns "are averages over budgets 0 to 1": selector MLP beats scene-only, ranker margin and random in all four rows | none |
| 9 | Limit 1: leads scene-only MLP by only 1 to 2 points on average | 1 | CONFIRMED | "+0.016 / +0.011 / +0.017 / +0.016" (CIs not corrected for multiple comparisons) | none |
| 10 | Limit 2: behind at 0.95 and 1.00 at mid noise, and at 1.00 with high noise or blocked ROI | 1 | CONFIRMED | Verbatim in the success-criteria table | none |
| 11 | Limit 3a: behind on `occluded_cross_traffic` on the final split at half a call (0.330 vs 0.347) | 1 | CONFIRMED (omits mid noise) | Family table: "final split, mid noise and half a call"; scene-only 0.347, selector 0.330 | Add "at mid noise" |
| 12 | Limit 3b: "With 510 seeds on the test split, averaged over budgets, it leads there (0.297 against 0.272)" | 1 | CONFIRMED (omits two settings) | Second family table: `occluded_cross_traffic` scene-only 0.272, selector 0.297, "test-split averages over budgets", mid noise. The doc places it after "510 seeds with expected-gain targets" but never labels the table; the training also used expected-gain targets | Say "mid noise, 510 seeds and expected-gain targets" |
| 13 | Limit 4: "The features that describe how the candidates diverge changed the logistic selector by less than 0.01" | 1 | OVERSTATED | Source: "The features that describe **where the top two candidates part ways** changed the logistic selector by less than 0.01". That is one feature group (`_divergence` in features.py), not all candidate-geometry features. About ten other trajectory features follow the top scene features at 0.012 to 0.019 each in the MLP shuffle | "the features for where the top two candidates part ways" |
| 14 | Limit 5: with expected-gain targets and 510 seeds the lead grows in four of six cells | 1 | CONFIRMED | "grows in four of six cells and stays level at low noise" | none |
| 15 | 7.3: `occluded_pedestrian` lead 0.105 final split at half a call; 0.048 test split with 510 seeds averaged over budgets | 7 | CONFIRMED (same omissions as #12) | 0.545 - 0.440 = 0.105; 0.419 - 0.371 = 0.048 | Add "mid noise" |
| 16 | "Our existing results partly cover the core comparison" | 5 | CONFIRMED | consistent with the limits above | none |
| 17 | DEEP: learned allocators "select nearly as much harm as random", "even though they capture more benefit than random" | 1 | CONFIRMED | DEEP 2609.35910: "Learned allocators beat random by capturing more benefit but select nearly as much harm" | none |
| 18 | DEEP (section 6 heading): "Learned allocators pick harmful calls almost as often as random" | 6 | OVERSTATED (mild) | Source says "select nearly as much harm", an amount, not a frequency. "about a third of the oracle's beneficial value" holds only "at a 20% selection budget" | "carry nearly as much harm as random"; add "at a 20% selection budget" |
| 19 | DEEP: only lightweight routers still beat random at a 20% latency budget; detector resolution on KITTI, nuScenes, open-loop nuPlan | 6 | CONFIRMED | "only the lightweight routers, at about 3.5% of a full detector pass, still beat random" | none |
| 20 | DEEP: 34 to 54% "in DEEP's monocular-geometry settings" | 6 | CONFIRMED | "in every monocular-geometry setting, 34-54% of the escalations that change the downstream loss make it worse" | none |
| 21 | SIGMA baselines "local-only and fixed-period calls" | 1 | CONFIRMED | per AUDIT #14 (LOS, PCS); not re-read | none |
| 22 | DualDrive/HybridDriveVLA code: "announced; the GitHub link returned 404" | 1 | CONFIRMED | Paper says "Code will be available at https://github.com/WilliamXuanYu/HybridDriveVLA"; curl returned HTTP 404 at 23:20 | none |
| 23 | BLUE (2606.08684): scene complexity and kinematic features "struggle to predict" when language helps; hidden states "potentially already encode" it; gate trained on whether language will help | 3, 8 | CONFIRMED | Abstract: "pretrained VLA hidden states potentially already encode whether language will benefit a given frame, even though scene complexity and kinematic features alone struggle to predict this" | none |
| 24 | ASSCG (2606.25509) is a decision-value trigger | 3 | CONFIRMED | "frame-level gate trained with GRPO-style reinforcement fine-tuning to optimize closed-loop metrics under query costs"; reward is trajectory-score based, minus a call cost | none |
| 25 | "Eight papers score a query or a mode switch by its effect on the plan" | 3 | CONFIRMED (count), OVERSTATED (ETM) | Eight are listed. ETM's abstract: VLM called "only when refreshed semantic reasoning is expected to improve downstream planning", labels are corner-case labels plus information-gain pseudo-labels, so its target is information gain, not a measured plan change. Learning When to Search is unreadable beyond the abstract | Say "most score ... " or footnote ETM |
| 26 | AdaThinkDrive, AdaDrive, CAR-VLA, BLUE, ASSCG: "None of them chooses a perception query" | 3 | CONFIRMED (abstracts) | Abstracts of CAR-VLA, AdaDrive, AdaThinkDrive gate reasoning or LLM use; none selects a sensing tool | none |
| 27 | DriveAgent-R1: training code public; evaluation code and weights not | 3 | CONFIRMED | README (fetched now): training code ticked; "Evaluation Scripts", datasets, weights unticked, "pending company approval". 2609.08217 also says its "checkpoints and evaluation assets have not been fully released" | none |
| 28 | "Among the agents read in full, only DriveAgent-R1 has an explicit per-call cost" | 3 | CONFIRMED | AUDIT #43 (R_tool with C_tool = 0.125); scope now limited | none |
| 29 | Illusion of Visual Tool-Use (2608.06270) audits six models, two failure modes, one with no causal effect, "A calibrated minority of calls carries the gain" | 3 | CONFIRMED | Abstract: "two failure modes. In Calling Without Looking, returned observations have no causal effect ... the gain is concentrated in a Calibrated minority". The minority finding is general, not tied to one mode, which the report's wording implies loosely | none |
| 30 | ToolGate (2606.03054): 78.3% of calls leave the immediate answer unchanged, 9.9% change it from right to wrong | 3 | CONFIRMED | "only 11.8% ... incorrect to correct, ... 9.9% flip it from correct to incorrect. The remaining 78.3% leave the immediate forced-answer argmax unchanged" (measured on the baseline policy) | none |
| 31 | DriveSuprim (2506.06659, June 2025): 91.9 at K=1 to 98.7 at K=256 | 3 | CONFIRMED | AUDIT #46; the id 2506 matches June 2025 | none |
| 32 | RRDrive: oracle-best rank 33.9 under the baseline scorer to 27.7; risk profile added to each candidate; Table 5 compares geometry, risk or both | 3 | CONFIRMED | "the oracle rank from 33.9 to 27.7"; Table 5 "Geometry only 0.369, RiskOcc only 0.174, Geometry + RiskOcc 0.535". Table 5 is a cross-validated ranking probe on good candidates, not three deployed scorers | "a ranking probe" instead of "scorers" |
| 33 | "What we did not find is a per-decision choice of which information to acquire, under a budget" | 3 | UNVERIFIABLE | Absence claim; scoped as before | keep |
| 34 | DriveJudge Table 3: prompted VLM without tools 50.06 AUC; "Zero-shot tools raise it to 56.13, and fine-tuning to 77.95" | 4 | WRONG (the 77.95 clause) | Table 3: VLM-DirectScore 50.06; DriveJudge-ZeroShot (tools) 56.13; VLM-DirectScore-Ft (fine-tuning, no tools) **68.67**; DriveJudge (tools + fine-tuning) **77.95** | "tools raise it to 56.13; fine-tuning alone to 68.67; both to 77.95" |
| 35 | When2Tool (2605.09252) is a "text-only LLM study" | 4 | CONFIRMED | Title "LLM Agents Already Know When to Call Tools"; benchmarks are text tasks | none |
| 36 | Certifying (JUWtWs4Tgb): language models on network diagnosis; "in its tests" adaptive querying did worse when models chose their own queries | 4 | CONFIRMED | OpenReview abstract: "when the models select their own queries, adaptive querying underperforms pre-committed querying in our tests"; 63 topology lineages, three LM families | none |
| 37 | "Our VLM saying 'none' on 92% of decisions" | 4 | OVERSTATED (unfixed AUDIT #6) | phase5_vlm.md: 8% tool calls "on validation" (183 of 2,222); test "the same picture". Report omits the split | "92% on validation" |
| 38 | Black-image: DriveBench "for a significant portion of models" | 4 | CONFIRMED | "a significant portion of the models show minimal or no accuracy degradation, even in the absence of visual cues" | none |
| 39 | WOD-E2E: rater scores for 3 trajectories per example, picked from a filtered pool of fewer than 12; weak match | 5 | CONFIRMED | "we sample a set of diverse candidates (usually fewer than 12)"; "raters first select three diverse trajectories" | none |
| 40 | BOKBO: warning applies to noise-perturbed sampling, in manipulation | 6 | CONFIRMED | "K-sample disagreement tracks perturbation, not uncertainty"; "mechanism-specific"; token-level temperature sampling recovers partial safety information; VLA policies | none |
| 41 | Section 8: "AUDIT.md ... rated about 46 CONFIRMED, 8 WRONG, 18 OVERSTATED and 3 UNVERIFIABLE" | 8 | WRONG | The 75 rows of AUDIT.md count as 56 CONFIRMED (two of them mixed with OVERSTATED), 13 OVERSTATED, 5 WRONG, 1 UNVERIFIABLE by leading verdict. Counting mixed rows on both sides gives 15 OVERSTATED and 2 UNVERIFIABLE. No count gives 46/8/18/3 | "75 claims: 56 CONFIRMED, 13 OVERSTATED, 5 WRONG, 1 UNVERIFIABLE (leading verdict)" |
| 42 | "revised after the audit at about 23:25" | header | OVERSTATED (timestamp) | REPORT.md was saved at 23:17 and AUDIT.md at 23:13; the stated time was in the future when written | "about 23:15" |
| 43 | "The main thread re-checked the RRDrive, BLUE and family-table items against the sources before changing them" | 8 | UNVERIFIABLE | No log in PLAN.md or raw/Z records this. The three corrections themselves are right (#23, #32, #15) | Drop the sentence or log the check |
| 44 | Scan "started 22:30", "written at about 23:05" | header | CONFIRMED | PLAN.md log: 23:05 merge, report written and linted | none |
| 45 | "about 172,000 entries in all" | header | OVERSTATED (unfixed AUDIT #68) | Recount of listing_sweep html: 171,806 unique arXiv ids, 224,196 entries counting cross-lists | "about 172,000 unique papers" |
| 46 | Section 8 item list: DriveSuprim dated, HybridDriveVLA 404, WOD-E2E, tool audits, scope items | 8 | CONFIRMED | each matches the body text checked above | none |

## 2. AUDIT.md WRONG / OVERSTATED items: fixed or not

Fixed in REPORT.md: #5, #14, #20, #22, #25, #34, #35, #39, #44, #45, #47, #48, #49 (the DriveJudge figure is now framed correctly except the 77.95 clause, see table row 34), #50, #56, #60, #61, #62, #67, #69, #72 (partly), #73, #43.

Not fixed or only partly fixed:

1. **#68 (about 172,000 "entries")**: unchanged; the 171,806 figure is unique papers. Severity low.
2. **#72 (partly)**: the budget range, the MLP-only lead and the single-draw targets are now stated, but the "not corrected for multiple comparisons" caveat on the three intervals (AUDIT #1) is not in section 5. The "top shuffle drops are all scene features" point is also not in section 1.
3. **#6 (suggested fix)**: "92%" still has no "validation".
4. **#29**: FD-WAM quote is still clipped ("can even degrade planning"); the condition "when its predictions are inaccurate" is missing.
5. **#31**: ETM is still described as trained on "information-gain pseudo-labels"; the labels are hybrid with corner-case labels.
6. **#26**: Proof-of-Perception row still says "(document QA)"; its benchmarks include chart and multi-image QA.
7. **#41**: OmniDrive-R1 still "caps zoom calls at 5"; the source says tool calls.
8. **#51**: Auditing Latent-Space Monitors is still cited under "frozen embeddings"; its latents are VAD planner latents.
9. **#53**: the 21.5% and 58.1% to 14.5% figures still lack "K=6" and "seen CARLA sites"; "so no reranker can help there" is an inference not in the source.
10. **#24**: the DualDrive row does not say that gamma is swept (a model-gating accuracy-compute curve exists).
11. **#36**: Calibrate-Then-Delegate domain (LLM safety monitoring) is not stated.
12. **#32**: DynaChain's OpenReview title is not given (optional).

## 3. Counts

| Count | Report says | Files say | Verdict |
|---|---|---|---|
| `papers.csv` rows | 462 | 462 | CONFIRMED |
| HIGH rows | 50 | 50 (plus 1 unrated, 2604.27366) | CONFIRMED |
| `references.bib` entries | "HIGH papers with arXiv ids" (no number) | 44; HIGH with arXiv id = 44, sets equal | CONFIRMED |
| Abstract-only named submissions | 7 | the 7 are abstract-only and not on arXiv; BoE is named as abstract-only too (8th) and is on arXiv (2607.20950) | WRONG for BoE |
| AUDIT verdict totals | 46/8/18/3 | 56/5/13/1 | WRONG |
| listing entries | about 172,000 | 171,806 unique, 224,196 entries | OVERSTATED |

## 4. WRONG and OVERSTATED items, most serious first

1. **Best-of-Evidence is on arXiv (2607.20950), not abstract-only** (rows 5, 6). The report calls it "the nearest idea to candidate-conditioned query selection" while citing only the abstract, and papers.csv says "no arXiv version found". Read the full paper before keeping that sentence; the seven-versus-eight abstract-only count is also inconsistent.
2. **DriveJudge: "fine-tuning to 77.95" is wrong** (row 34). 77.95 needs tools and fine-tuning; fine-tuning without tools is 68.67. This sits inside the section that was just rewritten to be careful.
3. **Section 8 verdict tally 46/8/18/3 does not match AUDIT.md** (row 41). The table has 56/13/5/1.
4. **Limit 4 generalises** (row 13): the under-0.01 result is for the "where the top two candidates part ways" feature group, not for all candidate-divergence features.
5. **Section 6 DEEP heading says "as often"** (row 18); the source says "as much harm", and the one-third figure is at a 20% selection budget.
6. **Unfixed AUDIT items** (section 2 above): "multiple comparisons" caveat, "validation" on the 92%, clipped FD-WAM quote, 172,000 "entries", ETM labels, Proof-of-Perception benchmarks.
7. **ETM counted as a plan-effect trigger** (row 25), **timestamp 23:25 written at 23:17** (row 42), **unlogged "main thread re-checked" sentence** (row 43), **missing "mid noise / expected-gain" labels** on the two family numbers (rows 11, 12, 15).
