# Joint final deliverables

| File | What it is |
|---|---|
| `deck/joint_deck.pptx`, `deck/joint_deck.pdf` | Final talk: 23 main slides and 16 backups, with the speaker for each slide in the notes |
| `deck/SOURCES.md` | Speaker, section and number sources for every slide |
| `report/report.md`, `report/report.html`, `report/report.pdf` | Joint final report (Sections 1-6 and 8-9 are Max's, Section 7 is Contribution 2) |
| `figures/` | PNG renders of `paper/figures/*.pdf` and the pedestrian frame used by the VLM slide |
| `build_joint_deck.py`, `build_joint_report.py` | Build scripts |

## How Max's work is kept intact

Max's result files (`out/v4_eval`, `out/v3_eval`) exist only on his machine. If his numbers were rebuilt from the data
regenerated on the Mac, they would shift by the 0.010-0.016 reproduction gap (`research/2026-11-20_voi_selector/DATA.md`).
So both builds start from his published files and only add to them:

- **Deck.** The deck is his `deliverables/deck/deck.pptx`, with every slide and number unchanged. The only edit to his
  slides is the title-slide subtitle, which now names both contributions. Contribution 2, the conclusion and Eshan's
  backups are drawn with his own `build_pptx.py` renderer and `common.py` helpers, which are executed from his folder, not
  copied.
- **Report.** The report is his `deliverables/report/report.md`, word for word. Section 7, one abstract paragraph and one
  contributions paragraph are added, along with a related-work paragraph, Contribution 2 limits and next steps placed
  after his lists, and Appendices B and C. His Limitations and Next steps become Sections 8 and 9.
- **Fairness tests.** `tests/test_joint_deliverables.py` fails if any of his slide text or report paragraphs goes
  missing.

If Max updates his deck or report, rebuild. The deck needs `python-pptx` (`uv pip install --python .venv/bin/python python-pptx`):

```bash
.venv/bin/python docs/final/build_joint_deck.py      # needs LibreOffice for the PDF (--no-pdf to skip)
.venv/bin/python docs/final/build_joint_report.py    # needs Google Chrome for the PDF (--no-pdf to skip)
```

Each Contribution 2 number is read from `out/voi_eval`, `out/vlm_yesno` and `out/vlm_probe` at build time. Once
`out/voi_eval/final_v4_addendum.json` exists, the V4 addendum (VoI plus the VLM prior on the final seeds, exploratory)
appears on the VLM slide and in Section 7.6 automatically.

## Open items for the team

- **Talk length.** The talk is 10 minutes, and the deck has 23 main slides: 15 of Max's and 8 of Eshan's. Max should
  decide which of his slides move to backup. Candidates are the first final test, safety, "what drives it" and "where it
  goes wrong", which would bring the deck to the 13-slide outline in `docs/final_presentation_slides.md`.
- **Number in Max's report.** His report still says the harm rate is "at most 0.0117" in 6.4. His own audit
  (`AUDIT_deliverables.md`, item 1) says it should be 0.0133. The joint report keeps his text as it is, so the fix belongs
  in his `report.tmpl.md`.
- **IEEE LaTeX.** The course needs a LaTeX version of the report; the checklist is in `docs/final_report_draft.md`.
