# Future Steps: From PlanDiscrim to CASS-VLA

## Purpose

[`refined_proposal.md`](refined_proposal.md) narrows the semester to one question: which single perception
query best separates a set of candidate trajectories. That narrowing deferred most of the original
[`proposal.md`](proposal.md) rather than discarding it.

This document records what was deferred, **why each piece was deferred rather than dropped**, and the
explicit entry criterion that must be met before starting it. The reviewer's instruction was that calibration,
repeated tool calls, and the full supervisor come *only after* the core evaluation works; the gates below make
that ordering concrete instead of aspirational.

The staging is deliberate: each stage is only meaningful if the previous one produced a positive result.
Starting Stage A before Stage 1 concludes would calibrate a signal not yet shown to carry information.

## Stage overview

| Stage | Adds | Entry criterion | Rough effort |
|---|---|---|---|
| A | Conformal risk calibration | PlanDiscrim beats uncertainty baseline on the Pareto sweep | 3–4 weeks |
| B | Sequential / budgeted multi-query | Stage A, or a clear single-query accuracy ceiling | 3–4 weeks |
| C | Full ACCEPT / INSPECT / REPLAN / FALLBACK supervisor | Stages A and B | 5–6 weeks |
| D | Closed-loop online VLA | Stage C, and latency budget measured | 4–6 weeks |
| E | CARLA / Bench2Drive transfer + perturbations | Stage D stable in MetaDrive | 4–6 weeks |
| F | Real-data offline validation | Stage E, and results worth external validation | 3–4 weeks |

Stages A and B are independent of each other and could run in parallel if a second semester or additional
people are available. C depends on both.

---

## Stage A — Conformal risk calibration

**What it adds.** Converts the selector's raw scores into a calibrated upper bound on risk via split
conformal prediction, so that "accept" becomes a decision with a distribution-dependent coverage statement
rather than a thresholded score. This was the original proposal's headline novelty claim and remains the
strongest path to a publishable contribution.

**Entry criterion.** PlanDiscrim demonstrably beats generic uncertainty-based selection across the Pareto
sweep. Calibrating a score that carries no more information than a scene-uncertainty heuristic would produce
a technically correct and scientifically empty result.

**Work.** Carve a calibration split by scenario seed; define the nonconformity score over candidate risk;
establish empirical coverage; measure expected calibration error; test coverage under held-out scenario
families.

**The interesting question.** Coverage almost certainly degrades under distribution shift — this is a known
weakness of conformal methods and was flagged as Risk 2 in
[`novelty_feasibility_audit.md`](novelty_feasibility_audit.md). Quantifying *how much* it degrades across
scenario families is more valuable than reporting in-distribution coverage that holds by construction.

**Prerequisite from Stage 1.** Split by scenario seed from the outset. Retrofitting a leakage-free
calibration split onto a frame-level dataset is painful, and the current plan already splits this way.

---

## Stage B — Sequential and budgeted multi-query

**What it adds.** Lifts the one-query-per-decision restriction. The selector allocates a budget across a
decision step (query, observe, decide whether to query again) and eventually across an episode, spending more
where ambiguity is genuinely costly.

**Entry criterion.** Either Stage A completes, or the Stage 1 results show single-query accuracy saturating
well below always-on — which would be direct evidence that one query is insufficient and would justify going
here first.

**Work.** Extend the labeling pipeline to tool *sequences* (note: the label space grows combinatorially, so
this likely needs greedy oracle sequences rather than exhaustive enumeration); formulate as a budgeted
information-gathering problem; compare against a myopic repeat of the Stage 1 selector.

**Main risk.** The oracle labeling cost grows sharply. Budget the pipeline extension, not just the modeling.

---

## Stage C — Full intervention supervisor

**What it adds.** Restores the original four-way output: `ACCEPT`, `INSPECT(tool)`, `REPLAN`, `FALLBACK`.
Ranking candidates and deciding whether *any* candidate is acceptable are different problems — the Stage 1
formulation always picks a top-1, even when every candidate is unsafe.

**Entry criterion.** Stages A and B. `ACCEPT` is only meaningful with a calibrated threshold (Stage A), and
`INSPECT` is only meaningful when repeated inspection is possible (Stage B).

**Work.** Add a "reject the whole candidate set" branch; define replanning constraints passed back to the
generator; implement a conservative fallback controller; measure recovery success after intervention.

**The metric that matters.** **False-veto rate.** A supervisor can win every safety metric by vetoing
everything. This was already the pressure valve in the original proposal and becomes the primary guard here.
Any result in this stage must report false vetoes alongside safety gains, or it means nothing.

---

## Stage D — Closed-loop online VLA

**What it adds.** Moves from cached offline VLA outputs to live in-the-loop inference at 1 Hz, and from
open-loop decision accuracy to closed-loop driving outcomes: route completion, collision rate, near-collision
rate, minimum clearance.

**Entry criterion.** Stage C works offline, and the per-decision latency budget has been measured rather than
assumed.

**Why this is its own stage.** Open-loop decision accuracy and closed-loop driving performance can diverge —
compounding errors, distribution shift from the system's own actions, and the fact that a single bad decision
early in an episode dominates the outcome. Treating "it ranks correctly" as equivalent to "it drives well"
would be the most likely way to overclaim, so the two are measured separately and on purpose.

**Work.** Real-time inference path, scene-state caching between steps, latency instrumentation, closed-loop
episode metrics, recovery-after-intervention measurement.

---

## Stage E — CARLA / Bench2Drive transfer and perturbation robustness

**What it adds.** The original evaluation environment, plus the sensor-perturbation study from the first
proposal: night, rain, fog, sensor noise.

**Entry criterion.** Stage D stable in MetaDrive.

**Why it belongs here.** MetaDrive's lower visual fidelity is a real limitation for claims about *visual*
ambiguity — geometric ambiguity transfers more readily than visual ambiguity. A CARLA result would materially
strengthen the visual claims, and the perturbation study connects directly to the fragility findings in
*Lost in Fog* ([`literature_survey.md`](literature_survey.md)).

**Work.** Port scenarios and the oracle pipeline to CARLA/Bench2Drive; re-derive labels from CARLA ground
truth; run the perturbation sweep; report in-distribution and shifted results separately.

**Honest expectation.** The port is mostly engineering, and the oracle pipeline is the part that will resist
it. Worth doing only if the underlying result is strong enough to be worth defending in a second environment.

---

## Stage F — Real-data offline validation

**What it adds.** Checks whether trajectory-conditioned tool selection holds on real logged driving data
(nuScenes or similar) rather than simulation alone.

**Entry criterion.** Stage E, and a result strong enough to justify the effort.

**Fundamental obstacle.** Real data has no counterfactual oracle. There is no way to observe what would have
happened under a candidate the vehicle did not take. Any real-data evaluation is therefore a weaker,
proxy-based validation — comparison against human-driven trajectories, or annotation of hazard visibility —
not a replication of the simulated result. This stage should be scoped as a sanity check, never as the main
evidence.

---

## Things deliberately dropped, not deferred

These were in the original proposal and are not planned for any stage:

- **Object tracking as a separate fourth tool.** Folded into `t_collision`, which needs predicted occupancy
  anyway. Three tools keep the selection problem legible.
- **A learned or SOTA base planner.** The candidate generator stays deliberately simple. A stronger planner
  would add variance without changing the research question — and a *weak* planner inflates the apparent
  benefit of supervision, which is a reason to keep the generator fixed and simple rather than to improve it.
- **Fine-tuning the VLA.** Frozen throughout. Training a driving foundation model was ruled out in the
  original proposal and stays ruled out.
- **Any real-vehicle claim.** All results are simulation-based runtime-assurance evidence. This does not
  change at any stage.

## Carrying this forward

Two things from Stage 1 determine whether the later stages are cheap or expensive:

1. **Split by scenario seed from day one.** Every calibration and generalization claim downstream depends on
   a leakage-free split, and retrofitting one is worse than doing it correctly now.
2. **Log everything per decision** — candidate set, per-tool predicted scores, the query made, the tool
   response, the resulting ranking, the oracle labels, and cost. Stages A through C are largely re-analyses
   of this log. If the log is complete, each stage is a new analysis; if it is not, each stage is a new data
   collection.
