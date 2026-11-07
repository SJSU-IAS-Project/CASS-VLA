# Plan

Run: field_scan skill, 2026-11-06 22:30 to 2026-11-07 04:00 PST. Approved by the user ("run that untill 4am pst").
All agents are Sonnet. The run writes only to this folder and the session scratchpad.

| Time (PST) | Step | Agents |
|---|---|---|
| 22:35–00:30 | Wave 1, sub-areas A–G | 7 |
| 22:40–00:30 | Listing sweep fetch and filter (main thread): cs.RO cs.CV cs.AI cs.LG, 2026-07 to 2026-11 | 0 |
| 00:30–02:10 | Wave 2: deep-read of closest competitors, OpenReview ICLR 2027 sweep, follow-up of leads, thin areas | 3–4 |
| 00:30–02:10 | Listing triage, one agent per tier file of about 450 titles | 3–5 |
| 02:10–02:40 | ID check (verify.py), late deep-read, merge, references.bib | 1 |
| 02:40–03:10 | REPORT.md (main thread) | 0 |
| 03:10–03:50 | Audit, and related-work delta against docs/literature_survey.md | 2 |
| 03:50–04:00 | Fix the report from the audit, lint, reply | 0 |

## Wave 1 sub-areas

- A: VLM/VLA driving agents with active perception or tool calls (DriveAgent-R1 and its follow-ups)
- B: budgeted or selective perception and sensing, active perception, value of information, for driving and robotics
- C: VLM/LLM trajectory critics, scorers and selectors over candidate trajectories
- D: learning to defer, abstain, ask for help, or decide when to query more information (selective prediction, LLM tool-use decision, "when to call a tool")
- E: benchmarks and datasets with hazards, occlusion, sensor corruption, long-tail scenarios; MetaDrive, CARLA, Bench2Drive, nuPlan, NAVSIM
- F: frozen VLM/foundation-model features feeding planning or decision heads; prompted VLM vs. learned probe comparisons
- G: conformal and calibrated risk for planners and runtime monitors (future phase)

## Log

(updated as the run goes)
- 22:31 Wave 1 launched: A–G, 7 agents, stop 00:30. Listing fetch started for cs.RO cs.CV cs.AI cs.LG, 2026-07 to 2026-11.
- 22:35 F done early: 25 entries, abstract-level only, no close overlap. Nearest: 2602.10719, 2606.25509 (gate a VLM call, not a tool). Leads: OpenAlex, OpenReview not searched.
- 22:35 E done early: 26 papers. Closest idea 2607.00283 (plan-KL ranking of occluded agents). Lost in Fog = 2605.21446.
- 22:35 G done early: closest overlap SIGMA 2610.09520 (expected planning gain, VLM call trigger, CARLA). Sent back for full-text reads. Listing: 45 pages, 53,595 papers, 1,570 keyword hits; tiers t1 405, t2 468, t3_00/t3_01 ~350 each.
- 22:36 A done early (23 entries, no candidate-conditioned tool agent) and D done early (35 entries; closest ToolGate 2606.03054, VOILA 2602.03007, BCEA 2606.16667). All early finishers (A D E F G) sent back for full-text reads and snowballs until 00:30. Triage L1–L4 launched, stop 01:45.
- 22:37 G round 2 done: SIGMA deep read, novelty risk PARTIAL (binary cloud-VLM trigger by expected planning gain; no tool choice, no candidate set, no budget sweep). Calibration Is Not Control, 2610.02765, 2608.26533 read in full.
- 22:38 L3 done: 346 titles, 32 shortlisted, 14 blocks; HIGH 2608.14991 (risk-triggered cloud VLM, CARLA), 2608.29772 SAGE, 2609.01799. Note 2609.30557: latent probes add nothing over planner outputs.
- 22:38 L1 done: 405 titles, 14 blocks; closest 2611.02240 (belief-space MPC probe-then-act), 2610.21160 (value of intervention, LIBERO). Sent back for unfetched items and a second pass.
- 22:38 L2 done: 468 titles, 11 blocks. Close idea: 2611.06702 (robot picks the aerial query that most improves its MPPI rollouts), LAVOIR 2609.30706 (expected-gain regression per query). Sent back for full-text reads.
- 22:39 L4 done: 349 titles, 15 blocks; nearest 2610.23262, 2610.21434. Caveat paper 2610.28184. Starting second listing fetch for 2025-07 to 2026-06.
- 22:39 A round 2 done: full text of 2609.08217, 2512.14044, 2509.20843, 2610.05025 (TUD has a success-vs-calls curve). DriveAgent-R1 latency verified (Sec 3.7, Table 8). New near-precedent UDAV 2609.16368 (gate on K-trajectory spread, no tools).
- 22:39 F round 2 done (45 blocks). Key: 2602.10719 Sec 4.5 says representation-only gating does not beat the VLM baseline and selection needs trajectory-level signals (supports our claim). Layer/token studies: HALP 2603.05465, 2505.24840, ProbeAct 2606.09740. Note: our embed.npz already holds image_last and last_token.
- 22:39 E round 2 done. Correction: DriveBench has no agentic tool use (round-1 claim came from a search summary). No occluded-traffic-light benchmark found.
- 22:40 C round 2 done. DriveJudge Table 3: prompted VLM 50.06 AUC. New HIGH RRDrive 2609.21486 (candidate-conditioned queries to a risk field; oracle-best ranks 33.9th). Counterfactual VLA abstract +20.5% vs intro 14.7%.
- 22:40 L1 round 2 done: 19 blocks; adds 2610.10390 GeoCoTDrive, 2607.16938 CVAA, 2609.19681 VAST.
- 22:40 B done (38 entries). Close ICLR 2027 submissions: DEEP l9QJO8BIoE (decision value of perception compute; learned allocators near random on harm), MosaicDrive 9I96DzTfHb, ETM oa4EWvJlLC. Wave 2 deep-reads X1 (OpenReview set) and X2 (arXiv set: RRDrive, 2611.06702, 2508.12166, 2608.14991, 2611.02240, UDAV, 2609.30557, 2610.21160, 2609.22910) launched, stop 01:30. B sent back for leads.
- 22:41 L4 round 2 done: full text of 2610.28184 (hazard decodable AUC 0.998 but planner intrudes), 2610.23262, 2610.21434 (success vs queries). Added 2610.35448, 2610.41185.
- 22:41 L2 round 2 done: 2611.06702 deep read (risk partial at idea level: rescores fixed MPPI rollouts under map hypotheses, picks layer with max gain; no uncertainty/random baseline, no budget sweep). LAVOIR deep read (expected-gain regression, budget sweep, code).
- 22:41 D round 2 done (40 blocks). AdaTooler-V Tool Benefit Score = 8 runs with vs 8 without tool, closest to our noise-averaged expected gain. KnowNo set-size rule suggested as candidate-ambiguity baseline. UPS 2602.22474 still unread in full.
- 22:42 B round 2 done. Arnob & Stein 2403.03269 trains a GNN on privileged VoI targets (same recipe as ours). 2601.06407 VoI net-value rule as abstain baseline. Corrections to round-1 numbers recorded in file.
- 22:43 X2 done: 9 full texts. 2611.06702 novelty risk partial-to-high on the idea; suggests a counterfactual-rollout baseline in MetaDrive. Wording: 'candidate-set-conditioned choice among perception tools in driving, with a budget Pareto', not 'first plan-conditioned VoI'.
- 22:45 H done (35 entries). Adds DynaChain gJvWSNcUtw, Learning When to Search LlFRODPGr8, Foresight on Demand 6pILFjKpgH (sent to X1). DriveAgent-R1 = ICLR 2026 poster r2g8TV4nJy. H sent back for leads and 2026 venues.
- 22:45 X1 done: DEEP = arXiv 2609.35910, read in full (uncertainty no better than random at 20% budget; learned allocators select nearly as much harm as random; decision-value-trained routers beat random in 40/200). MosaicDrive, ETM, Certifying-IV, DriveScout abstract-only (no arXiv). X1 resumed for DynaChain, Learning When to Search, Foresight on Demand.
- 22:46 X1 addendum done: DynaChain, Learning When to Search, FD-WAM (all abstract-only). Novelty statement updated: gating by realized planning gain, uncertainty as poor trigger, harmful extra evidence are all prior work.
- 22:48 Early listing (2025-07 to 2026-06): 100 pages, 118,211 papers, 2,728 new keyword hits; tiers e1_00/01, e2_00/01, e3_00/01/02. Triage E1–E7 launched, stop 02:15.
- 22:52 M5 done: 407 titles, 16 blocks; nearest 2508.11488 Perception in Plan, 2511.06253 AdaDrive. Caveat 2510.08571 (offline metrics vs closed loop).
- 22:52 M6 done: 413 titles, 15 MED; nearest PRAM-R 2603.04222 (LLM router picks sensor modalities). Process note: triage agents shared one scratch abs.txt and overwrote each other; M5 and M6 re-fetched into private dirs. Skill fix: give each triage agent its own scratch dir.
- 22:53 M2 done: 315 titles, 21 blocks; HIGH idea 2606.22277 Active-Sensing DDTO (trajectory-dependent info-acquisition term with sensing budget, not driving).
- 22:54 M7 done: 423 rows, 15 MED. BA-GSAC 2605.26155: ensemble disagreement stays low under occlusion (weak evidence vs uncertainty triggers). Safe2Drive 2606.00191 occluded-VRU family. Also hit the shared-scratch collision and re-ran privately.
- 22:54 M1 done: 316 titles, 15 blocks; 2507.09822 active probing in MetaDrive (by action, not tools); DeeAD 2511.20720 gates compute by trajectory vs planning priors.
- 22:54 M3 done: 426 titles, 20 MED; 2507.15886 (which/when monitors under budget), 2601.20666 (bandit monitor in driving sim), AFA papers.
- 22:55 M4 done: 21 blocks; HIGH 2604.14251 Calibrate-Then-Delegate, 2605.00737, 2603.00324. All triage done. Launched X3 (late deep-read, 12 papers) and Y (UNVERIFIED and leads follow-up), stop 01:30.
- 22:55 H round 2 done (40 blocks): 2026 venues swept; iDriveVLA = 2609.30818. H says no arXiv for DEEP, X1 says 2609.35910: checking.
- 23:01 X3 done: 12 full texts. Partial overlaps: 2604.14251, 2605.00737 (utility estimation hard, our case), AdaDrive, Proof-of-Perception (tool choice by own uncertainty, budget sweep), 2606.03135, 2507.15886. AS-DDTO downgraded to LOW.
- 23:05 Merge: papers.csv 449 rows (51 HIGH), references.bib 44 entries; two rows fixed by hand (Z checks). REPORT.md written and linted. Audit and related-work delta launched, stop 02:30.
- 23:09 RELATED_WORK_DELTA.md written (21 claims at risk, 20 new rows, new gap section) before AUDIT.md existed; to be reconciled with the audit.
- 23:15 Y done: ~48 UNVERIFIED rows checked, 12 new blocks (Best-of-Evidence U1JptdfbDT nearest non-driving). DriveAgent-R1 training code exists (github.com/Zwc2003/DriveAgent-R1). Re-merged.
- 23:17 AUDIT.md: 75 claims, ~46 CONFIRMED, 8 WRONG, 18 OVERSTATED, 3 UNVERIFIABLE. Main thread re-checked RRDrive Table 5, BLUE abstract, family tables; REPORT.md revised, Corrections section filled. Launching a second audit of the revised sections, and the delta agent to reconcile with AUDIT.md.
- 23:19 RELATED_WORK_DELTA.md reconciled with AUDIT.md and revised REPORT.md.
- 23:29 AUDIT2.md: corrections mostly held; fixed Best-of-Evidence (arXiv 2607.20950), DriveJudge 77.95, tally, DEEP wording, ETM grouping and 12 leftover AUDIT items. Delta and papers.csv updated.

## Wave 3 (added at 23:30, because waves 1–2 finished hours early)

| Time (PST) | Step | Agents |
|---|---|---|
| 23:30–01:30 | R: backward references of SIGMA, DEEP, 2611.06702, 2602.10719, 2604.14251, Best-of-Evidence | 1 |
| 23:30–01:30 | X4: full text of Best-of-Evidence, UPS 2602.22474, BOKBO 2605.30660, DriveAgent-R1 2507.20879 (trigger definition), KnowNo 2307.01928 | 1 |
| 23:30–01:30 | P: pre-2025-07 essential work on planning-aware perception, VoI sensing, AV attention allocation | 1 |
| then | merge, verify, update REPORT.md, third audit of the changes | 1 |
- 23:33 X4 done: full text of BoE (plug-in EVSI/c, not learned; gains +0.26 to +0.58 pp; beats random only on VQA-Med), DriveAgent-R1 (learned mode token from first frame, speed, nav; never sees candidates; tool-necessity label = oracle accuracy gap, close to our expected gain; no collision tool), KnowNo, UPS, BOKBO. Baseline cost ranking in file.
- 23:35 R done: 29 blocks from 6 bibliographies; planner-centric metrics lineage (PKL 2004.08745, 2110.03270, 2305.01870), LTT 2110.01052, 2602.17633. Removed the agent's stray /tmp/p.txt (copy of its blocks, all in raw/R_backward_refs.md).
- 23:38 P done: 47 classics (41 abs fetched). Ancestors: PKL, Ivanovic 2110.03270, HOIST, adaptive submodularity 1003.3967, nonmyopic VoI 1207.1394, Covert 2301.00557, Dynamic Zoom-in 1711.05187, Agent-Driver 2311.10813.
- 23:43 Re-merged: papers.csv 530 rows (60 HIGH), references.bib 54. verify run 3: OK 496, NO_ARXIV 119, MISMATCH 30 (new ones are section headings in X4/Y, no junk rows in csv). REPORT.md extended with wave 3; launching AUDIT3 on the diff.
- 23:46 AUDIT3.md: DriveAgent-R1 and BoE claims mostly held; fixed inputs, label, openness, BoE caveats, Agent Prioritization, framing, plug-in baseline, MosaicDrive critique, OpenAlex count. papers.csv: BoE note, Judge Then Drive relevance KNOWN. Delta P2 rewording updated for DriveAgent-R1.

## Wave 4 (added at 23:47): try to falsify the novelty claim

| Time (PST) | Step | Agents |
|---|---|---|
| 23:50–01:45 | Z1: adversarial web, GitHub and OpenReview search for a paper that already does REPORT.md's claim | 1 |
| 23:50–01:45 | Z2: adversarial search in neighbouring fields and wordings (robotics, embodied QA, medical, active classification, sensor scheduling) | 1 |
| then | update REPORT.md section 1 with the outcome; audit any change | 0–1 |
- 23:52 Z2 done: mechanism parts exist outside driving; CLARINET 2405.15784 (candidate-conditioned, counterfactual-gain trained, budget curve) and BudgetVerify 2609.33052 (tiered sources incl none, offline outcome labels, Pareto) each cover three of four parts. Abstracts checked in main thread.
- 00:07 Z1 done: no counterexample (~60 queries incl. patents, GitHub, OpenReview, listing re-filter); near misses Ask the World 4YOXy9OdU4, GM patent US12179756B2, AnA (ASPLOS 2025). Re-merged: 561 rows, 63 HIGH, 57 bib. REPORT.md section 1 updated with falsification results; launching AUDIT4 on the change.
- 00:09 AUDIT4.md: fixed Ask the World (manipulation, not driving), BudgetVerify (no candidate set), oracle-curve caveat, timestamp, search count. Run finished; further searches were returning the same papers.
