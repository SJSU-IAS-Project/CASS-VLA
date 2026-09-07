# CASS-VLA: Calibrated Active Safety Shielding for Vision-Language-Action Driving Planners

## Team

- Eshan Chawla
- Max Dokukin

## Selected Tracks

- Track 5 — Agentic Autonomy
- Track 6 — Safety and Evaluation

## Abstract

Vision-Language-Action (VLA) models combine visual perception, language-based reasoning, and action planning for autonomous driving. However, a driving planner may still propose unsafe trajectories when visual evidence is incomplete, ambiguous, occluded, or degraded by weather and sensor noise.

This project proposes CASS-VLA, a calibrated active safety supervisor for VLA driving planners. Operating at 1 Hz, CASS-VLA receives the current visual observation, recent scene history, route context, ego state, and a candidate trajectory proposed by a base planner. It estimates trajectory-specific risk and uncertainty, then selectively chooses to accept the trajectory, invoke a perception tool, request replanning, or trigger a conservative fallback. Initial tools include region-of-interest inspection, depth estimation, object tracking, and geometric trajectory collision checking.

Our research question is: under a fixed reasoning and tool-use budget, can calibrated active safety verification reduce unsafe trajectory acceptance compared with planner-only, always-on critic, and uncalibrated VLA-critic baselines? We will evaluate closed-loop driving safety, route completion, false intervention rate, tool cost, and uncertainty calibration under controlled hazards and perception perturbations in simulation.

## Motivation

Recent VLA-driving work has explored self-reflection, trajectory critics, active perception, and learning from failures. Yet these approaches generally do not provide a calibrated runtime mechanism for deciding whether a specific planner-proposed trajectory has enough reliable evidence to execute safely.

CASS-VLA studies the following decision:

> Should the system trust the proposed path, inspect the scene further, request a new plan, or fall back to a conservative controller?

## System Overview

```text
Camera frames + route + ego state
                ↓
         Main driving planner
                ↓
    Candidate trajectory / action plan
                ↓
      CASS-VLA safety supervisor
                ↓
 ┌──────────────┼──────────────┐
Accept      Inspect tool      Replan / fallback
                ↓
       Updated safety decision
                ↓
     Low-level driving controller
```

## Inputs and Outputs

### Inputs

- Current camera observation and short visual history
- Ego-vehicle state, including speed and heading
- Route or high-level navigation command
- Candidate trajectory proposed by the base planner
- Optional planner rationale or intended driving behavior
- Outputs from selectively invoked perception tools

### Outputs

- `ACCEPT` — execute the proposed trajectory
- `INSPECT(tool)` — gather more visual or geometric evidence
- `REPLAN` — reject the trajectory and request a new one
- `FALLBACK` — use a conservative safe controller

The supervisor also returns an estimated risk level, uncertainty score, identified hazard, and any safety constraints for replanning.

## Research Hypothesis

A trajectory-conditioned VLA safety supervisor with calibrated uncertainty and selective tool use will reduce unsafe trajectory acceptance while requiring fewer unnecessary interventions and tool calls than always-on verification.

## Evaluation

We plan to evaluate in simulation using CARLA and/or Bench2Drive-style scenarios.

Primary metrics:

- Unsafe trajectory acceptance rate
- Collision and near-collision rate
- Closed-loop route completion
- False-veto rate on safe trajectories
- Recovery success after intervention
- Tool calls and latency per episode
- Uncertainty calibration and empirical risk coverage

## Planned Baselines

1. Main planner only
2. Main planner with always-on VLA critic
3. Main planner with uncalibrated tool-using VLA critic
4. Main planner with calibrated critic but no tools
5. Full CASS-VLA system

## Initial References

- Counterfactual VLA: Self-Reflective Vision-Language-Action Model with Adaptive Reasoning, CVPR 2026
- Judge, Then Drive: A Critic-Centric Vision Language Action Framework for Autonomous Driving, 2026 preprint
- DriveAgent-R1: Advancing VLM-based Autonomous Driving with Active Perception and Hybrid Thinking, ICLR 2026

## Project Status

Proposal-stage repository. The initial milestone is to finalize the literature survey, simulator selection, base planner, and evaluation protocol.
