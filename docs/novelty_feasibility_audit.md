# AI Novelty and Feasibility Audit

## Proposed project

**CASS-VLA: Calibrated Active Safety Shielding for Vision-Language-Action Driving Planners**

## Summary judgment

The proposed domain is timely and technically meaningful, but it is a crowded area. VLA driving, critic-based trajectory refinement, counterfactual reasoning, and active perception are already active research topics. The project is novel only if it is framed as a calibrated runtime-assurance system rather than as a generic “VLA with prompts, skills, and tools.”

## Red-ocean risks

The following claims are not sufficiently novel on their own:

- “We use a VLA critic to evaluate driving plans.”
- “We use counterfactual reasoning before driving.”
- “We add visual tools such as depth estimation and object detection.”
- “We prompt a VLA to reason about driving safety.”
- “We improve driving performance with agentic planning.”

These directions overlap substantially with Counterfactual VLA, Judge, Then Drive, DriveAgent-R1, and other recent VLA-driving work.

## Required novelty claim

The project should make the following precise claim:

> We introduce a calibrated, trajectory-conditioned runtime safety shield that selectively decides whether to accept a planner-proposed trajectory, invoke an evidence-gathering tool, request replanning, or trigger fallback under a fixed 1-Hz compute budget.

The distinction is important:

- Existing work often improves the planner itself.
- CASS-VLA supervises an independently produced candidate trajectory.
- Existing work may use tools when uncertain.
- CASS-VLA uses tool calls to reduce uncertainty specifically enough to make a risk-calibrated accept/reject decision.
- Existing work may report safety improvements.
- CASS-VLA evaluates empirical risk coverage, unsafe acceptance, false vetoes, and tool cost.

## Potential research contributions

1. **Trajectory-conditioned calibrated risk**

   Predict and calibrate risk for the exact candidate trajectory proposed by the planner, not only for generic scene difficulty or object presence.

2. **Selective active perception**

   Invoke a visual or geometric tool only when the added evidence is likely to change the safety decision.

3. **Runtime intervention policy**

   Explicitly choose between accepting, inspecting, replanning, and falling back rather than generating only a revised trajectory.

4. **Safety-efficiency evaluation**

   Measure the tradeoff between fewer unsafe accepted trajectories and added tool/inference cost.

5. **Controlled benchmark protocol**

   Evaluate the same planner under visual perturbations, occlusions, and long-tail hazards to isolate whether safety supervision improves robustness.

## Feasibility assessment

| Dimension | Assessment | Notes |
|---|---|---|
| Technical novelty | Moderate to high | Strong only if calibration, selective intervention, and tool budget are all evaluated. |
| Course feasibility | High | Feasible with a frozen VLM/VLA and simulation; do not train a driving foundation model from scratch. |
| Compute requirements | Moderate | A 1-Hz VLA supervisor is much more realistic than direct high-frequency VLA control. |
| Data availability | Moderate to high | CARLA and Bench2Drive-style scenarios can support controlled evaluation. |
| Reproducibility | High | The system can log planner proposals, tool calls, risk scores, interventions, and outcomes. |
| Main-conference potential | Possible but uncertain | Requires strong closed-loop results, broad ablations, calibration evidence, and cross-scenario generalization. |

## Main risks

### Risk 1: Contribution becomes a systems combination

Combining an existing planner, VLA, prompts, and tools without a novel decision rule would likely be viewed as engineering integration rather than research.

**Mitigation:** make calibrated selective intervention the main algorithmic contribution.

### Risk 2: Calibration does not hold under visual shift

Conformal or held-out calibration guarantees do not automatically hold under arbitrary weather, sensor, or domain changes.

**Mitigation:** report results separately for in-distribution and shifted settings; do not claim real-world safety guarantees.

### Risk 3: VLA latency is too high

Large VLMs may be too slow or expensive for frequent driving decisions.

**Mitigation:** operate at 1 Hz, use a compact open model, cache scene state, and call tools selectively.

### Risk 4: Simulator results are not real-world deployment evidence

Simulation cannot establish real-vehicle safety.

**Mitigation:** frame all claims as simulation-based runtime-assurance evidence and clearly report limitations.

### Risk 5: Too much scope

A full driving planner, multi-agent system, VLA fine-tuning pipeline, tool suite, and benchmark is too large for one semester.

**Mitigation:** use an existing base planner, three initial tools, one simulator, and a restricted set of safety-critical scenarios.

## Recommendation

Proceed with this project if the team commits to the following scope:

- One simulator
- One base planner
- One frozen/lightly adapted VLM/VLA
- Three initial tools: ROI inspection, depth estimation, collision checking
- Four intervention outputs: accept, inspect, replan, fallback
- A controlled perturbation benchmark
- Strong planner-only and critic-based baselines

## Final AI critique

CASS-VLA is a credible research direction because it targets a practical and under-evaluated question: when should a VLA trust, inspect, or override a proposed driving trajectory? The project is not novel if presented as “a VLA critic with prompts and tools.” It becomes meaningfully novel if it demonstrates calibrated, trajectory-specific, compute-aware safety intervention with rigorous baselines and honest limitations.
