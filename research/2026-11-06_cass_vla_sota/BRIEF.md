# Brief for every scraping agent

Today is 2026-11-06. The user is an MS student (SJSU, CMPE 249 course project, team of two) working on
**trajectory-conditioned perception tool selection for driving planners** (project name PlanDiscrim,
part of a longer program called CASS-VLA). The last survey was done in mid-2026 and covered only the 7
papers in `known_papers.txt`. Your job: find what is new or what they missed, with the emphasis on
**2025-07 onward**, plus any older paper that is clearly essential and not in `known_papers.txt`.

## The project (what "relevant" means)
At each decision step a driving planner has a scene (front camera frame, ego state, route) and a set of
K = 3–5 candidate short-horizon trajectories. A selector may call at most one perception tool (ROI/object
inspection that reveals occluded objects and the light state, depth/distance-and-speed for visible objects,
or a geometric collision check against tracked actors) or abstain. A ranker then picks the top-1 candidate,
scored against an oracle best candidate computed from privileged simulator state. The question is whether
a selector conditioned on the candidate set (how the candidates diverge) picks the decision-relevant query
better than trajectory-agnostic scene-uncertainty triggering (as in DriveAgent-R1) at an equal query budget.
Evaluation is open-loop decision accuracy vs. query budget (a Pareto curve) in MetaDrive scenarios with
injected hazards (occlusion, ambiguous traffic lights, distance ambiguity) and three tool-noise levels.
Baselines: no tool, always-on, random, scene-uncertainty, an oracle selector. A learned MLP selector on
geometry features is trained on "expected gain" targets (each tool's correctness averaged over noise draws).
A frozen VLM (Qwen3.5-9B) is used offline: its cached image embeddings add a small gain (+0.3 to +0.7
points) to the selector, and prompting it to choose the tool works poorly (it mostly says "none").
Calibration (conformal risk control) and an accept/inspect/replan/fallback policy are future phases.

A paper is HIGH relevance if it:
- decides **which** perception/tool/sensor query to make, or **whether** to make one, under a budget, in
  driving or robotics, especially conditioned on the candidate actions/plans (decision-relevant or
  value-of-information style acquisition);
- is a VLM/VLA driving agent that calls perception tools (zoom, crop, depth, detection, collision check) or
  switches between "think" and "look", e.g. DriveAgent-R1 follow-ups and competitors;
- learns when to defer, abstain, ask for help or request more information, measured as accuracy vs. cost;
- is a trajectory critic/scorer/selector over multiple candidate trajectories with a VLM or with tools;
- offers a benchmark or dataset with hazards, occlusion or sensor perturbation that fits the evaluation, or
  uses frozen VLM features as input to a planning/decision head;
- adds calibrated/conformal risk to a planner's accept/reject decision (for the future phase).

Note any paper that **overlaps the project closely** (candidate-conditioned query selection for driving).
That is the most important thing to report.

## Already known — read first
`/home/user/CASS-VLA/research/2026-11-06_cass_vla_sota/known_papers.txt`. Do not report these as new.
You may cite them as anchors. Before adding a paper, grep the other `raw/*.md` files for its title so you
don't duplicate another agent's entry (duplicates are tolerated, but skip them if you notice).

## Tools
- arXiv abs pages for verbatim metadata and abstracts:
  `python3 -I /home/user/research/.agents/skills/field_scan/scripts/absfetch.py <id>`, 2 s apart.
- arXiv full text: `curl -sL -A 'research-verify/0.1' https://arxiv.org/html/<id>`, then strip the tags
  (see `/home/user/research/.agents/skills/field_scan/references/ENDPOINTS.md`).
- OpenReview search: `curl -s 'https://api2.openreview.net/notes/search?term=<terms>&content=all&source=all&group=ICLR.cc/2027/Conference&limit=50'`, 4 s apart.
- WebSearch and WebFetch for blogs, GitHub, CVF open access and cited-by lists. WebFetch returns a summary,
  not the page, so never take a number from it without checking the verbatim text.
- Do not use export.arxiv.org or Semantic Scholar's API. Both return 429 once several agents share the IP.
  OpenAlex works for cited-by lists.
- Snowball: for 2–3 anchor papers in your area, look at who cites them.

## Rules
- Never invent a paper, id, author, venue or number. Every entry must come from a fetched record or page.
  Mark anything you could not verify as UNVERIFIED.
- Do not download PDFs, and do not write anywhere except your own output file in
  `/home/user/CASS-VLA/research/2026-11-06_cass_vla_sota/raw/` (plus temporary files under the scratch
  directory you are given). No git commands that write. No sbatch, no ssh, no VPN.
- Stop by the time in your prompt (check `TZ=America/Los_Angeles date`). The whole run ends at 04:00 PST.
  Write your file every ~10 papers, so partial work survives.

## Output: `raw/<your_slug>.md`
1. `## Summary`: 5–10 bullets on what changed in this sub-area, the main trends, and which papers matter
   most for the project and why. Close overlaps go first.
2. `## Papers`: one block per paper, most relevant first, 15–40 papers:
   ```
   ### <Title>
   - id: arXiv:XXXX.XXXXX (or DOI / URL) | date: YYYY-MM | venue: <venue or "arXiv preprint">
   - authors: <first author et al.> | code: <url or none>
   - relevance: HIGH / MED / LOW — <one line why, measured against the project>
   - what: <2–3 sentences: problem, method, headline result with dataset (only numbers you saw)>
   - thesis use: <baseline / benchmark / idea to borrow / competitor / contradicts X>
   - verified: abs meta fetched / html read / page fetched / UNVERIFIED
   ```
3. `## Leads not followed`: queries or threads you ran out of time for.
