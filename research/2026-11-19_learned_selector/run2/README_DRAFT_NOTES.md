# Facts in README.md that README_DRAFT.md drops

| Fact in current README.md | Where it lives instead |
|---|---|
| Team: Eshan Chawla, Max Dokukin | `docs/refined_proposal.md` (Team). Human decides whether the draft names authors. |
| Tracks 5 (Agentic Autonomy) and 6 (Safety and Evaluation) | `docs/refined_proposal.md` (Selected Tracks) |
| Abstract: calibrated active safety supervisor at 1 Hz with ACCEPT / INSPECT / REPLAN / FALLBACK | `docs/proposal.md` (original) and `docs/future_steps.md` (Stage A calibration, Stage C intervention policy). Draft Status links future_steps. |
| Research question vs planner-only, always-on critic, uncalibrated critic | Reframed in `docs/refined_proposal.md` section 0 and 1 as tool selection; the draft answers a narrower question (Why not table). |
| Motivation (self-reflection, trajectory critics, active perception prior work) | `docs/literature_survey.md`, `docs/novelty_feasibility_audit.md` |
| System overview diagram, inputs and outputs | `docs/refined_proposal.md` (pipeline diagram, formulation) |
| Research hypothesis (calibrated, fewer interventions than always-on) | Superseded by H1 to H3, S1 and S4 in `research/2026-11-19_learned_selector/PREREG.md` and `docs/baseline_results.md` (pre-registered final test) |
| Evaluation in CARLA / Bench2Drive, closed-loop metrics | Now MetaDrive and open loop, `docs/refined_proposal.md` section 0 table. Closed-loop metrics deferred in `docs/future_steps.md`. |
| Planned baselines 1 to 5 | `docs/refined_proposal.md` and `docs/baseline_results.md` |
| "Object tracking" as a fourth tool | Dropped in the refinement (3 tools). `docs/refined_proposal.md` section 0. |
| Pointers to docs and `out/` (git ignored) | Kept, in Layout |

Factual disagreement to settle: the current README still describes CARLA, four tools and a 1 Hz closed loop, which the refined proposal replaced.
