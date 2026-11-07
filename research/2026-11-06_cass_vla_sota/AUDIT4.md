# AUDIT4: changed sentences in REPORT.md since the pre-wave-4 version

Checked 2026-11-07 about 00:10 PST against arXiv html (curl, tags stripped), the OpenReview search API, Google Patents, python csv, and the two raw agent files.

## Claim table

| # | claim | verdict | evidence | fix |
|---|---|---|---|---|
| 1 | "two falsification agents added to section 1 at about 00:40" | WRONG | REPORT.md mtime is 00:07:22 on 2026-11-07; `date` at audit start read 00:07. Z1 mtime 00:04, Z2 mtime 23:51. 00:40 had not happened. (Z1 and Z2 headers also say "to 00:30" and "to about 00:20", which their own mtimes contradict.) | Write "about 00:05" or drop the time. |
| 2 | "There are two near misses in driving. Ask the World ..." | WRONG | OpenReview 4YOXy9OdU4 abstract: "Correction-guided active perception for VLAs", frozen LingBot VLA, "Bimanual Manipulation" keyword, "Task-Guided Viewpoint Selection". It is robot manipulation, not driving. Z1 itself says "robot manipulation". Only the GM patent is in driving. | "There are two near misses. Ask the World is robot manipulation; the other is a driving patent." |
| 3 | Ask the World "turns a proposed action correction into a viewpoint query", abstract only | CONFIRMED | Abstract: "treat the correction as a decision-directed visual query ... selects a viewpoint that exposes this relation". Abstract-only is right (pdf blocked). | Optional: add that it has two candidates (nominal and corrected), not K. |
| 4 | CLARINET: arXiv:2405.15784, retrieval | CONFIRMED | Title/abstract: clarification questions for retrieval (books). | none |
| 5 | CLARINET "conditions on the retrieval distribution over candidates" | CONFIRMED | Abstract: "condition on a retrieval distribution". Body: input is top candidates whose probabilities add to 50%, at most 3. | none |
| 6 | Quote "to generate the question that would have maximized the rank of the true candidate" | CONFIRMED | Verbatim in html abstract: "finetuning end-to-end to generate the question that would have maximized the rank of the true candidate at each turn". | none |
| 7 | CLARINET "chooses among generated questions, not among kinds of information source" | CONFIRMED | It generates a free-text question; single source (the user). | none |
| 8 | CLARINET "has no 'ask nothing' option" | CONFIRMED (absence in text) | Greps of the full html for stop/terminate/skip/abstain/whether-to-ask found nothing. Protocol is fixed: 9 questions over 10 turns ("allowed to ask 9 clarification questions"). Cannot prove absence beyond the text, but the design always asks. | none; could say "always asks (fixed 9 questions)". |
| 9 | BudgetVerify arXiv:2609.33052, financial QA | CONFIRMED | FinQA; "Budget-Tiered Verification for Financial QA". | none |
| 10 | BudgetVerify "routes each answer to no verification, a light check or a costly check" | CONFIRMED | "no verification, lightweight check-and-revise, or higher-cost solve-first-then-compare verification". | none |
| 11 | Quote "trained from offline correctness and token-cost outcomes" | CONFIRMED | Verbatim: "The router is trained from offline correctness and token-cost outcomes". | none |
| 12 | "Pareto frontiers against fixed policies" | CONFIRMED | Fixed baselines Generator Only, Always Mid, Always High; frontier over 26 cost values. No uncertainty/random/oracle selector baseline found. (Oracle labels exist for training only.) | none |
| 13 | "It sees one answer, not a candidate set" | CONFIRMED | "budgeted verification depth for a single generated financial answer". | none |
| 14 | "two papers cover three of the four parts each" | OVERSTATED | Z2's own table: CLARINET = YES, partly, YES, partly; BudgetVerify = NO, YES, YES, partly. Counting "partly" as covered, Best-of-Evidence (YES, YES, NO, partly) scores the same, so "two papers" is arbitrary. For BudgetVerify, (a) is NO. Under strict counting each has 2 full parts. | "each part exists in some neighbouring paper; CLARINET and BudgetVerify each cover two fully and one partly." |
| 15 | "found that each part of the mechanism exists outside driving" | OVERSTATED | Z2 states part (a) for BudgetVerify is absent and the full oracle-selector baseline (d) was "not found in any neighbour". Part (d) exists only partly. | "each part, at least in weaker form". |
| 16 | "One ran about 60 searches across the web, patents, GitHub and OpenReview" | CONFIRMED (understated) | Z1 log: 57 numbered web queries (number 40 is missing, so 57 not 58), plus 22 OpenReview term-group batches (each over 4 or 3 groups), plus about 15 GitHub queries. Total is nearer 100 requests; "about 60" fits the web queries alone. | Say "about 60 web searches plus OpenReview and GitHub queries". |
| 17 | "re-filtered all 171,806 listing titles" | CONFIRMED | Z1: "171,806 unique ids" re-filtered with new regexes, 99 titles left after removing csv ids. Number matches line 7 of the report. | none |
| 18 | "it found no counterexample" | CONFIRMED | Z1 summary: "Counterexample found: NO", caveated as absence over what was searched. | none |
| 19 | "The other searched neighbouring fields" | CONFIRMED | Z2 log: 24 queries over medical, retrieval, robotics, verification. | none |
| 20 | "mechanism of choosing a query from the candidate set, trained on its counterfactual gain, has precedents" | CONFIRMED | CLARINET (candidate input, rank-gain target) matches. Z2 states this explicitly. | none |
| 21 | Combination "shown on one budget curve against uncertainty, random and oracle selectors" not found | CONFIRMED (Z2/Z1 scope) | Z2: "Not found in any neighbour". Caveat as in the report. | none |
| 22 | GM patent US12179756B2 "trains an attention model on plan-change labels from planning with and without each actor" | CONFIRMED | Google Patents: Original/Current Assignee GM Global Technology Operations LLC; DNN on scene graph gives per-actor attention score; description: "automated data labeling procedure", method 200 "used to label data set for training DNN"; claim 1 computes D_i = max waypoint distance between average trajectory with all actors and with a removed actor. The claim text itself does not recite training; training is in the description. "Each actor" is a mild gloss (claim recites "a removed actor"). | none; optional: "removing an actor". |
| 23 | Patent is in driving | CONFIRMED | Host-vehicle planning. | none |
| 24 | `papers.csv` holds 561 papers, 63 HIGH | CONFIRMED | python csv: 561 rows; relevance counts MED 315, LOW 182, HIGH 63, KNOWN 1. | none |
| 25 | `references.bib` has 57 entries, "for the 57 HIGH papers with arXiv ids" | CONFIRMED | 57 `@` entries, 57 unique keys. HIGH rows with an arXiv id: 57 unique ids (6 HIGH rows have none: ETM, DriveScout, MosaicDrive, Closed-loop agentic RL, Learning When to Search, Foresight on Demand). All 57 ids are in the bib. | none |
| 26 | New file rows for `raw/Z1`, `raw/Z2` | CONFIRMED | Both files exist. | none |
| 27 | Implicit: Ask the World is covered by the corpus | UNVERIFIABLE/inconsistent | Z1 says it is "already in papers.csv", but no csv row has that title or id 4YOXy9OdU4 (the GM patent and AnA are in csv; Ask the World is not). Not stated in REPORT.md, so no report error, but the csv count 561 omits it. | Add a csv row or drop the Z1 claim. |
| 28 | Z2's Best-of-Evidence figures (not in the diff) | UNVERIFIABLE | Z2 never read it ("search summary only"). Not in the changed text. | none |

## WRONG / OVERSTATED, most serious first

1. WRONG (#2): Ask the World is a manipulation VLA paper, not driving. The report calls it one of "two near misses in driving". Fix the sentence.
2. WRONG (#1): "about 00:40" is in the future; the file was written at 00:07. Use about 00:05.
3. OVERSTATED (#14): "two papers cover three of the four parts each" counts "partly" as a cover and picks two of at least three papers that score the same. BudgetVerify lacks part (a) outright.
4. OVERSTATED (#15): "each part ... exists outside driving" is true only in weaker form for the budget-curve-with-oracle-selector part, which Z2 says no neighbour has.
5. Minor (#16): "about 60 searches" undercounts the real request total; harmless.
6. Minor (#27): Ask the World is not in papers.csv despite Z1's note.
