from common import *
import slides as SL
out = ['# Deck sources', '', 'Each slide lists where its numbers come from. Paths are relative to `research/2026-11-19_learned_selector/` unless they start with `out/`, `docs/` or `deliverables/`.',
       'Numbers on slides 8, 9, 11 to 13 and the second-final backups are read from `out/v4_eval/final_geom.json` by `slides.py` when the deck is built. Other numbers are copied from the cited reports.', '',
       'Q1 (signed plus VLM on the second final test) passes at all three levels. Source: `out/v4_eval/final_vlm.json`, `hypotheses.final.Q1.cells.<level>` (mean_diff, ci95); signed_vlm mean accuracy 0.5163 / 0.4589 / 0.3851 is in `results.final/<level>.signed_vlm.mean_acc`.', '']
mi = bi = 0
for s in SL.slides:
    if s['backup']: bi += 1; n = f'Backup B{bi}'
    else: mi += 1; n = f'Slide {mi}'
    out += [f'## {n}: {s["title"]}', '', s['src'], '']
open('SOURCES.md', 'w').write('\n'.join(out)); print('ok')
