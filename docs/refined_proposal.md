# Refined Project Proposal: PlanDiscrim

## Title

**PlanDiscrim: Trajectory-Conditioned Perception Tool Selection for Driving Planners**

(Refinement of the earlier CASS-VLA proposal. The name *PlanDiscrim* is taken from the reviewer feedback in
[`proposal_feedback.md`](proposal_feedback.md); CASS-VLA is retained as the name of the long-term research
program, of which this proposal is Phase 1. See [`future_steps.md`](future_steps.md) for the deferred phases.)

## Team

- Eshan Chawla
- Max Dokukin

## Selected Tracks

- Track 5 — Agentic Autonomy
- Track 6 — Safety and Evaluation

## 0. Response to Feedback

The original proposal bundled seven contributions into one semester: a candidate planner, a VLA safety critic,
a multi-tool perception library, active tool selection, conformal risk calibration, replanning/fallback logic,
and closed-loop evaluation. Reviewer feedback identified this as over-scoped and recommended extracting
**planner-discriminative tool selection** as the single core question.

This refined proposal adopts that recommendation in full.

| Dimension | Original proposal | Refined proposal |
|---|---|---|
| Core question | Should this trajectory be executed? | Which single perception query best separates these candidate trajectories? |
| Simulator | CARLA + Bench2Drive | **MetaDrive** |
| Tools | 4 (ROI, depth, tracking, collision check) | **3** (ROI/object inspection, depth/distance, geometric collision check) |
| VLA role | In the loop at 1 Hz | **Offline / cached outputs** |
| Supervision signal | None specified | **Oracle labels from MetaDrive ground-truth state** |
| Calibration | Core contribution | **Deferred** (Stage A of future work) |
| Intervention policy | ACCEPT / INSPECT / REPLAN / FALLBACK | **Deferred** (Stage C of future work) |
| Evaluation | Closed-loop driving | **Open-loop decision quality vs. query cost** |

The shift from *verification* ("is this one trajectory safe?") to *discrimination* ("which query separates
these candidates?") is the substantive change. Discrimination is a sharper question, and — critically — it
admits ground-truth labels, which the original framing did not.

## 1. Problem Formulation

### Domain problem

A driving planner facing an ambiguous scene can produce several plausible candidate trajectories that differ
in safety, but the difference may be undecidable from the raw observation alone. An occluding vehicle, a
distant traffic light, or an ambiguous depth cue can each be the one fact that determines which candidate is
correct. Querying every perception tool at every step resolves this but is wasteful; querying none leaves the
ambiguity unresolved.

Existing active-perception systems (e.g. DriveAgent-R1) trigger tools on *scene* uncertainty — a
trajectory-agnostic signal. A scene can be visually uncertain in ways that are irrelevant to the choice at
hand, and visually clear in ways that hide the one detail that matters. This project asks whether conditioning
on the **candidate set** does better.

### Research question

> Given a set of candidate trajectories and an ambiguous scene, can a trajectory-conditioned selector choose
> the single most decision-relevant perception query, achieving comparable or better candidate-ranking
> accuracy than always-on verification at substantially lower query cost — and beating trajectory-agnostic
> uncertainty-based selection at an equal budget?

### Formal setup

At a decision step the system receives a scene `s` (front-facing camera frame, short visual history, ego
state, route command) and a candidate set `C = {c_1, ..., c_K}` of short-horizon trajectories, `K ≈ 3–5`.

A tool library `T = {t_ROI, t_depth, t_collision}` is available. The selector outputs an action
`a ∈ T ∪ {∅}` — at most **one** query per decision step, or abstention.

A ranker then scores `C` using the base observation plus the query result (if any) and returns a top-1
candidate `ĉ`.

The oracle best candidate `c*` is computed from privileged MetaDrive state. The selector is evaluated on
whether `ĉ = c*` and on how many queries it spent getting there.

### Inputs

- Front-facing camera frame and short visual history
- Ego state (speed, heading, position)
- Route command
- Candidate trajectory set `C`
- Cached VLA scene description / embedding for the frame
- Tool output, when one query is made

### Outputs

- Selected query `a ∈ {ROI, depth, collision, none}`
- Ranking over `C`, and top-1 candidate `ĉ`
- Per-tool predicted decision-change score (the selector's internal signal, logged for analysis)

## 2. Motivation

Every additional perception or VLA call costs latency and compute, and in a driving stack that budget is
strictly bounded. The interesting question is not whether more evidence helps — it obviously does — but
whether a system can predict *in advance* which single piece of evidence will change its mind, and skip the
rest.

Framing this over a candidate set makes the question answerable. "Was this tool call worth it?" is vague in
the abstract; "did this tool call flip the top-1 candidate to the oracle-correct one?" is a binary label a
simulator can produce at scale. That label is the methodological core of this proposal and is what makes the
reduced scope tractable in a semester.

## 3. Technical Approach

### System architecture

```text
Scene observation + ego state + route
                  ↓
       Candidate trajectory generator  ──────►  C = {c_1 ... c_K}
                  ↓                                    │
        Cached VLA scene encoding                      │
                  ↓                                    ↓
         ┌──── PlanDiscrim selector ◄─────────── candidate features
         │              ↓
         │   a ∈ {ROI, depth, collision, none}
         │              ↓
         │       Perception tool  (executed at most once)
         │              ↓
         └────────► Candidate ranker
                        ↓
                    top-1 ĉ
                        ↓
        compare against oracle c* from MetaDrive state
```

### Candidate trajectory generation

Candidates come from a deliberately simple generator, not a learned planner: a small bank of short-horizon
maneuvers (lane keep at several speeds, lane change left/right, decelerate, stop) fitted to the road geometry
MetaDrive exposes. This is a scope decision — the project studies *selection among candidates*, so the
candidate source is intentionally boring and reproducible. A learned planner would add variance without
changing the research question.

Scenes are retained for the dataset only when candidates genuinely disagree under the oracle, i.e. when at
least one candidate is unsafe and at least one is safe. Scenes where every candidate is equivalent carry no
signal about tool selection.

### Tool library

Three tools, each with a defined cost and a simulated-but-realistic response:

| Tool | Query | Resolves |
|---|---|---|
| `t_ROI` | Inspect a region of interest for objects / traffic-light state | Occlusion, distant or ambiguous signals, unnoticed actors |
| `t_depth` | Estimate distance to a specified object or region | Depth/distance ambiguity, closing-speed misjudgment |
| `t_collision` | Geometric collision check of a candidate against tracked actors | Whether a specific candidate intersects predicted occupancy |

Note that `t_collision` is inherently trajectory-conditioned while `t_ROI` and `t_depth` are scene-directed
with a trajectory-dependent argument (which region, which object). This asymmetry is deliberate: it gives the
selector something non-trivial to learn.

### Oracle label generation (the core mechanism)

This is the load-bearing piece of the proposal. MetaDrive exposes privileged ground-truth state — actor
poses, velocities, bounding boxes, occupancy, traffic-light phases, road geometry. For each retained scene:

1. **Oracle ranking.** Roll every candidate `c_k` forward against ground-truth actor futures and score it
   (collision, minimum clearance, time-to-collision, rule compliance). This yields `c*` and a full oracle
   ordering over `C`.
2. **Counterfactual tool responses.** For each tool `t`, construct the response it would return from ground
   truth, degraded by a realistic noise model so the tool is informative but not itself an oracle.
3. **Decision-change labels.** For each `t`, run the ranker with `t`'s response and record whether top-1
   becomes `c*`. Label `t` as **decision-changing** if the ranker is wrong without any tool and correct with
   `t`.
4. **Abstention labels.** Scenes where the ranker is already correct with no tool, or where no tool fixes it,
   are labeled `∅`. These are essential — they are precisely the scenes where a good selector saves a call,
   and a dataset that omits them would make every method look good.

The result is a supervised dataset of (scene, candidate set) → per-tool decision-change labels. It defines an
**oracle tool selector** as the upper bound and lets every method be scored as regret against it.

### The PlanDiscrim selector

Input features: cached VLA scene encoding, candidate-set geometry (divergence between candidates, where and
when they differ), ego state, and per-candidate risk proxies. Output: a predicted decision-change probability
per tool, plus abstention.

Two variants will be compared, budget permitting:

- **Learned head** — a light classifier over the cached features. Primary variant; cheap to train and to run.
- **Prompted VLA** — the cached VLA asked directly which query would most help distinguish the candidates.
  Secondary variant, evaluated offline on a subset.

The VLA is run **offline over the frame set and cached to disk**. No VLA call occurs inside the simulation
loop. This removes latency from the critical path of the semester and is the single largest feasibility win
from the reviewer's recommendation.

## 4. Evaluation Environment

**MetaDrive**, replacing CARLA/Bench2Drive. The reasons are scope-driven: MetaDrive is lightweight, installs
without a heavy binary dependency, runs headless on modest hardware, and — the deciding factor — exposes the
privileged state the oracle labeling pipeline requires through a clean API.

Scenario families, built as procedurally generated MetaDrive scenes with scripted hazards:

- Occluded pedestrian or cyclist emerging from behind a parked vehicle
- Occluded cross-traffic at an intersection
- Distant or ambiguous traffic-light state
- Sudden lead-vehicle braking and cut-ins
- Lane blockage requiring a commit-or-abort decision
- Depth/closing-speed ambiguity at merges

Target dataset size: on the order of a few thousand retained decision steps, stratified across scenario
families, with a held-out split by scenario seed (not by frame) to prevent leakage between near-identical
consecutive frames.

## 5. Baselines

All five methods share the same candidate generator, ranker, and tool implementations. Only the selection
policy differs.

1. **No tool** — rank from base observation only. Lower bound on both accuracy and cost.
2. **Random tool** — uniform over `T`. Controls for the benefit of *any* extra evidence.
3. **Generic uncertainty-based selection** — query when scene/ranker uncertainty exceeds a threshold, with
   the tool chosen trajectory-agnostically. **This is the real rival.** The entire claim of the project is
   that trajectory-conditioned selection beats trajectory-agnostic uncertainty at equal budget; without this
   baseline there is no result.
4. **Always-on** — query all three tools every step. Upper bound on accuracy, worst case on cost.
5. **PlanDiscrim** — trajectory-conditioned selection of at most one tool.

Reference point: the **oracle selector** from the labeling pipeline, which defines the achievable ceiling and
turns the comparison into a regret measurement rather than a bare accuracy table.

## 6. Metrics and Success Criteria

### Decision quality

- Top-1 candidate accuracy (`ĉ = c*`)
- Unsafe candidate selection rate (top-1 is a candidate the oracle marks unsafe)
- Full-ranking correlation with the oracle ordering
- Regret against the oracle selector

### Cost

- Tool calls per decision and per episode
- Abstention precision/recall — did the method skip a query exactly when no query would have helped?
- Wall-clock and estimated inference cost per decision

### Headline analysis

An **accuracy-versus-cost Pareto curve**, sweeping each method's operating threshold. The claim is supported
only if PlanDiscrim sits above and to the left of generic uncertainty-based selection across the budget range,
not merely at one hand-picked threshold.

### Breakdowns

- Per-scenario-family accuracy, to show *where* trajectory conditioning helps
- Per-tool selection precision, to show the selector learns tool-specific relevance rather than a single
  "query something" reflex

### Success criteria

1. PlanDiscrim reaches top-1 accuracy within a small margin of always-on while using substantially fewer
   queries.
2. PlanDiscrim beats generic uncertainty-based selection at equal query budget, across the Pareto sweep.
3. PlanDiscrim beats random selection at equal budget (sanity check; failing this invalidates the setup).
4. Abstention is meaningfully better than chance — the selector knows when no query helps.
5. Failure modes are characterized honestly, including scenario families where trajectory conditioning does
   not help.

A negative but well-measured result — that trajectory conditioning does *not* beat scene uncertainty — is a
reportable outcome and will be written up as such.

## 7. Plan

| Phase | Work | Primary owner |
|---|---|---|
| 1 | MetaDrive setup, headless runs, scenario scripting | Eshan |
| 2 | Candidate generator; oracle rollout scoring; `c*` | Eshan |
| 3 | Three tool implementations and counterfactual response models | Both |
| 4 | Label-generation pipeline and dataset release **(central artifact)** | Both |
| 5 | Offline VLA encoding pass and caching | Max |
| 6 | Four baselines | Max |
| 7 | PlanDiscrim selector, training, Pareto evaluation | Both |
| 8 | Ablations, breakdowns, report, presentation | Both |

Phase 4 is the critical path. If the labeling pipeline works, every later phase is straightforward; if it
does not, no amount of downstream modeling recovers the project. Phases 1–4 are therefore front-loaded, and
progress will be assessed against Phase 4 completion rather than against model results.

## 8. Resources

- No foundation-model training.
- Frozen open VLM in the 3B–7B range, run **offline in batch** over the frame set.
- MetaDrive is CPU-friendly; GPU is needed only for the one-time VLA encoding pass and for training the light
  selector head. A single ~24 GB GPU, or batched cloud inference, is sufficient. This is a substantially
  lower requirement than the original in-the-loop design.
- Repository and environment maintainer: Eshan.
- Literature and evaluation lead: Max.

## 9. Deliverables

- Reproducible MetaDrive scenario suite
- **Tool-discriminativeness dataset** with oracle labels — the main reusable artifact
- Three tool implementations with documented cost and noise models
- Four baselines plus the oracle selector
- PlanDiscrim selector and training code
- Accuracy-versus-cost Pareto evaluation with per-family breakdowns
- Experiment logs, ablations, and negative results
- Conference-style report and presentation
- Updated literature survey positioning against DriveAgent-R1 and related active-perception work

## 10. Assumptions and Known Limitations

- **Open-loop.** Decision quality is measured against oracle rankings, not driving outcomes. Closed-loop
  validation is Stage D of the future plan. A method that ranks well may still drive poorly.
- **Simulated tool responses.** Tools are ground-truth-derived plus a noise model, not real perception
  networks. The noise model is an assumption, and the sensitivity of results to it will be reported.
- **Single-step.** One query per decision, no sequential information gathering. Deferred to Stage B.
- **Oracle depends on privileged future state.** Actor futures are taken from the simulator, which assumes
  other agents do not react to the ego's candidate choice. This is a real limitation for interactive
  scenarios and will be stated explicitly rather than smoothed over.
- **MetaDrive is not CARLA.** Visual fidelity is lower, so conclusions about *visual* ambiguity transfer less
  readily than conclusions about *geometric* ambiguity. Transfer is Stage E.
- **No safety guarantee is claimed.** This phase produces no calibrated bound of any kind; calibration is
  Stage A.
