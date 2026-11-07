# Triage brief (arXiv listing sweep)

Read ../BRIEF.md first (project, relevance rules, output block format). Then:

Your input is a TSV of `arxiv_id<TAB>categories<TAB>title`: arXiv listing entries from Jul–Nov 2026
(cs.RO, cs.CV, cs.AI, cs.LG). The titles matched driving / tool-use / active-perception / calibration
keywords and are NOT yet in any raw/*.md file or in known_papers.txt.

1. Read every title. Shortlist the ones that could be HIGH or MED against the project (typically 10–20%).
   Skip pure manipulation VLA papers, pure 3D detection/segmentation, mapping and sim-to-real papers unless they
   bear on choosing perception queries, scoring candidate trajectories, deciding when to call a tool or
   model, hazard/occlusion benchmarks, or calibrated accept/reject of plans.
2. For each shortlisted id, first grep ../raw/*.md for it (another agent may have added it since). Then
   fetch the verbatim abstract (one at a time, sleep 2 s between calls):
   ```
   python3 -I /home/user/research/.agents/skills/field_scan/scripts/absfetch.py <id>
   ```
   It prints title, first author, date and the abstract, taken from arxiv.org/abs meta tags.
3. Write a paper block (format in ../BRIEF.md, `verified: abs meta fetched`) for each paper that is
   really HIGH or MED after reading the abstract. Use only numbers that are in the abstract.
4. Output: ../raw/<your slug>.md with `## Summary` (what this slice adds, anything that overlaps
   the project closely, listed first), `## Papers`, then `## Shortlisted but dropped` (one line each: id,
   title, why dropped).
Write incrementally. Stop by 01:45 PST (`TZ=America/Los_Angeles date`). No other writes, no git.
