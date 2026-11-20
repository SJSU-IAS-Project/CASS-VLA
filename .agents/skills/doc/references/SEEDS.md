# Seeds

Seeds below are already used. A new tuning or test run takes seeds from 1060 up.

| Seeds | Used for |
|---|---|
| 0-9 | choosing decision windows (`t_window`), twice |
| 10-29 | old window validation, before the speed fix |
| 30-49 | setting ROI noise and the tie rule in `labels.py` |
| 50-59 | window validation after the speed fix |
| 100-399 | main dataset; `build_dataset.py` splits them 70/15/15 by seed with `SPLIT_SEED` |
| 400-459 | final held-out test; method comparison once on 2026-11-06, then the pre-registered data-size check; treat it as seen |
| 460-759 | extra training seeds for the learning-curve check on 2026-11-06 |
| 760-859 | second final held-out test, now SEEN: used once on 2026-11-19 for the pre-registered test (`out/v3_final`, rules in `research/2026-11-19_learned_selector/PREREG.md`). Never use it to choose methods |
| 860-1059 | second set of extra training seeds (`out/v3_extra`). Swept, 9,682 decisions retained, no dataset or expected-gain labels built from it before 2026-11-19 |
