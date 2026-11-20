from common import *
S = 'research/2026-11-19_learned_selector/'
FJ = 'out/v4_eval/final_geom.json'
P = H  # hypotheses
def cell(h, lv, key='mean_diff', c='ci95'):
    d = P[h]['cells'][lv]
    return f"{sg(d[key])} {ci(d[c])}"
import json as _j
VL = _j.load(open(os.path.join(ROOT, 'out/v4_eval/final_vlm.json')))
Q1 = VL['hypotheses']['final']['Q1']['cells']
VJ = 'out/v4_eval/final_vlm.json'
def rr(lv, m, k): return R['final/' + lv][m][k]
AO = {lv: R['final/' + lv]['always_on'] for lv in LV}
P4 = P['P4']['cells']

# 1 Title
slides.append(dict(title='Title', eyebrow='', backup=False, notes='', src='Title text: docs/refined_proposal.md (team, tracks).',
 els=[RECT(0, 0, 1920, 1080, INK),
      T(120, 150, 1500, 40, ['CMPE 249 · Agentic Autonomy and Safety and Evaluation'], size=30, color='AEB8C8'),
      T(120, 250, 1680, 300, ['Which perception tool should a driving planner call, and when?'], size=92, color='FFFFFF', bold=True),
      T(120, 590, 1600, 140, ['A learned selector that looks at the candidate trajectories, tested on fresh seeds'], size=44, color='D8E0EC'),
      T(120, 860, 1500, 50, ['Eshan Chawla and Max Dokukin'], size=38, color='FFFFFF'),
      T(120, 925, 1500, 50, ['Project CASS-VLA, Phase 1 (PlanDiscrim)'], size=30, color='AEB8C8')]))

# 2 Problem
slide('The question: cheaper perception checks, without losing safety', 'The problem', [
  T(100, 240, 1720, 260, [{'t': 'Our professor narrowed the project to one question:', 'size': 32, 'color': GREY, 'gap': 10},
     {'t': 'Given candidate trajectories and an ambiguous scene, can a selector choose the one perception query that matters most? It should match always-on checking at far lower cost, and beat uncertainty-based selection at the same budget.', 'size': 40, 'bold': True}], fill=PANEL, pad=36),
  T(100, 545, 1720, 460, bullets([
     'Calling every perception tool on every decision is costly. It can also hurt: extra evidence sometimes contradicts a correct judgment.',
     'Tool-using driving agents such as DriveAgent-R1 decide from the scene alone. Plan-value gates exist, but we found none that chooses among perception tools from how the candidates differ.',
     'Our bet: a scene can be uncertain in ways that do not matter for the choice at hand. The candidates show which uncertainty matters.',
     'Two rivals: always-on (the cost reference) and a generic uncertainty trigger (the equal-budget rival).'], size=36, gap=18))],
 'Question and motivation text: docs/refined_proposal.md, sections 0 and 1 (Research question; Domain problem).')

# 3 Setup
slide('Setup: three tools, a few candidates, a call budget', 'Setup', [
  T(100, 250, 540, 700, [{'t': 'Simulator', 'bold': True, 'color': TEAL, 'size': 34, 'gap': 12},
     {'t': 'MetaDrive, six scenario families: ambiguous light, lane blockage, lead brake or cut-in, merge, occluded cross traffic, occluded pedestrian.', 'gap': 14},
     {'t': 'Up to 6 candidate maneuvers per decision (K), over a 5 s horizon: keep, keep fast, decelerate, stop, change left, change right. A lane change exists only when the lane does.', 'gap': 14},
     {'t': 'Labels come from simulator ground truth (the oracle).'}], size=32, fill=PANEL, pad=32),
  T(690, 250, 540, 700, [{'t': 'Tools and noise', 'bold': True, 'color': TEAL, 'size': 34, 'gap': 12},
     {'t': 'Three simulated tools: ROI check, depth, geometric collision check.', 'gap': 14},
     {'t': 'Each tool is noisy. We test three noise levels: low, mid and high.', 'gap': 14},
     {'t': 'A tool result goes to the ranker, which picks the top candidate again.'}], size=32, fill=PANEL, pad=32),
  T(1280, 250, 540, 700, [{'t': 'Budget', 'bold': True, 'color': TEAL, 'size': 34, 'gap': 12},
     {'t': 'The selector makes at most one call per decision, or none.', 'gap': 14},
     {'t': 'Budget = calls per decision. A budget of 0.6 means 60% of decisions get one call.', 'gap': 14},
     {'t': '**Always-on** calls all 3 tools every time: 3 calls per decision.'}], size=32, fill=PANEL, pad=32),
  T(100, 975, 1720, 50, ['Accuracy: the ranker’s top candidate equals the oracle’s best candidate. Unsafe: the oracle labels the chosen candidate unsafe.'], size=26, color=GREY)],
 'Families, K, tools, noise (K up to 6 maneuvers over a 5 s horizon: cassvla/planning/features.py CANDIDATE_NAMES, docs/oracle.md): docs/refined_proposal.md (three tools; budget a=one query or none), docs/baseline_results.md (tool noise low/mid/high), REPORT.md section 3 (budget definition, always-on 3 calls), run2/PREREG2.md (metric). Family names: out/v4_eval/final_geom.json results.final/<level>.signed.by_family keys.')

# 4 Method (flow)
flow = []
bx = [('Scene and candidates', 'ego state, hazards, K trajectories'), ('Candidate features', 'which candidate is on top, how it differs from the runner-up, safety and occlusion'),
      ('Small MLP', '32 hidden units, one output per tool'), ('Predicted gain per tool', 'ROI, depth, collision'), ('Call or abstain', 'call the best tool only if its gain is above 0')]
x0 = 100; w = 310; gapx = 42
for i, (a, b) in enumerate(bx):
    x = x0 + i * (w + gapx)
    flow.append(RECT(x, 250, w, 300, PANEL if i != 4 else 'D9EFEC'))
    flow.append(T(x + 22, 270, w - 44, 70, [a], size=32, bold=True, color=TEAL if i == 4 else INK))
    flow.append(T(x + 22, 355, w - 44, 190, [b], size=28, color=INK))
    if i < 4: flow.append(T(x + w, 360, gapx, 60, ['→'], size=42, color=GREY, align='c'))
slide('Method: pick the tool from the candidates', 'Method', flow + [
  T(100, 610, 840, 400, [{'t': 'Frozen MLP (first version)', 'bold': True, 'color': GREY, 'size': 34, 'gap': 12},
     {'t': 'Trained to predict the gain of each tool, clipped at 0. It never learns that a call can hurt.', 'gap': 12},
     {'t': 'Calls are ranked by score and spent up to the budget. It calls too much at high budgets.'}], size=32, fill=PANEL, pad=32),
  T(980, 610, 840, 400, [{'t': 'Signed-gain abstain (primary)', 'bold': True, 'color': TEAL, 'size': 34, 'gap': 12},
     {'t': 'Same network with a linear output. It is trained on the signed expected gain, so negative gains are visible.', 'gap': 12},
     {'t': 'It calls only when the best predicted gain is above 0, and it picks that tool. No extra threshold to tune.'}], size=32, fill='D9EFEC', pad=32)],
 'Model description: research/2026-11-19_learned_selector/run2/PREREG2.md (Methods: signed, frozen; 32 hidden units, MSE on unclipped expected gain, linear output, call only if largest predicted gain above 0), REPORT.md section 3 (Learner variants). Expected-gain labels: docs/baseline_results.md (8 extra noise draws per tool).')

# 5 Baselines
slide('Baselines: what the selector has to beat', 'Baselines', [
  TABLE(100, 240, 1720, [3.2, 8, 3], [['Policy', 'What it does', 'Calls per decision'],
     ['Always-on', 'Calls all three tools on every decision. The cost and accuracy reference.', '3'],
     ['Uncertainty margin', 'Calls where the ranker’s top-two margin is lowest. The generic uncertainty trigger.', 'budget'],
     ['Scene only (learned)', 'Same MLP, with scene features and the margin, but no candidate features.', 'budget'],
     ['Simple triggers', 'Ego speed, candidate spread, fixed schedule, random.', 'budget'],
     ['KnowNo-style', 'Calls on 99.8% to 100% of decisions at every setting, so it is not a budgeted trigger.', '(about 1)'],
     ['Signed, scene only', 'The signed model without candidate features. The fair rival for the signed model.', 'budget']], size=30, rowh=96, hl=[0]),
  T(100, 960, 1720, 60, ['The simple triggers land between 0.002 below and 0.03 above random, on the first final test.'], size=28, color=GREY)],
 'Policies: PREREG.md (Methods), PREREG2.md (Methods). KnowNo 99.76% to 100%: REPORT.md section 2 (Mean accuracy table note, knowno.<alpha>.call_rate). Simple triggers vs random: REPORT.md section 2 (same note).')

# 6 How we tested
slide('How we tested: two pre-registered final tests on fresh seeds', 'Method of testing', [
  T(100, 230, 1720, 170, [{'t': '**Pre-registration here:** we wrote the methods, the metric, the hypotheses and the pass rule in a file before the test labels or results existed. The test ran once. Anything found later is marked exploratory.'}], size=36, fill=PANEL, pad=32),
  TABLE(100, 430, 1720, [3.2, 4, 4], [['', 'First final test', 'Second final test'],
      ['Seeds', '760 to 859', '1060 to 1159'],
      ['Decisions', '4,903', f"{G['n_test']['final']:,}"],
      ['Training rows', '34,718', f"{G['n_train']:,} (same data)"],
      ['Plan file', 'PREREG.md + 2 amendments', 'PREREG2.md, written before any test evaluation'],
      ['Primary tests', 'H1, H2 (H3 descriptive)', 'P1 to P4'],
      ['Error bars', 'Paired bootstrap over scenario seeds, 1,000 resamples, 95% CI', 'Same']], size=30, rowh=74, hl=[0]),
  T(100, 985, 1720, 50, ['No correction for multiple comparisons: 4 primary hypotheses, each at every level it names.'], size=26, color=GREY)],
 'First final: REPORT.md section 2 (seeds 760-859, 4,903 decisions, 34,718 training rows). Second final: ' + FJ + ' (n_train, n_test, seeds); run2/PREREG2.md (seeds 1060-1159, written before evaluation, no correction). Pre-registration meaning: PREREG.md and PREREG2.md headers.')

# 7 Result 1
slide('First final test: the candidate-based selector beats both rivals', 'Result 1 of 2 · seeds 760 to 859', [
  TABLE(100, 240, 1720, [4.3, 2.6, 2.6, 2.6, 2.2], [['Mean accuracy difference (95% CI)', 'Low noise', 'Mid noise', 'High noise', 'Verdict'],
    ['H1: learned minus uncertainty margin', '+0.093 [0.085, 0.101]', '+0.080 [0.071, 0.088]', '+0.071 [0.062, 0.079]', 'holds'],
    ['H2: learned minus scene only', '+0.020 [0.016, 0.025]', '+0.021 [0.018, 0.025]', '+0.021 [0.017, 0.025]', 'holds'],
    ['S1: flip features add', '+0.000 [−0.002, 0.002]', '+0.003 [0.001, 0.005]', '+0.001 [0.000, 0.002]', 'fails'],
    ['S4: signed minus frozen', '+0.004 [0.001, 0.007]', '+0.010 [0.006, 0.014]', '+0.018 [0.014, 0.021]', 'holds (mid, high)']], size=26, rowh=84, hl=[4]),
  T(100, 740, 1720, 260, bullets([
     'H1 and H2: every confidence interval is above 0 at all three noise levels.',
     'S1 failed: the counterfactual flip features added at most +0.003, so we recommend dropping them.',
     'S4 confirmed on fresh seeds: the signed-gain variant beats the frozen MLP at mid and high noise.'], size=32, gap=12))],
 'REPORT.md section 2, Verdicts table (source keys: results.final/<level>.comparisons in out/v3_eval/triggers_final.json; S4 from diff_vs_frozen in out/v3_eval/final/s4_signed.json). Values rounded to 3 decimals from the 4-decimal table.')

# 8 Result 2
slide('Second final test: all four pre-registered hypotheses pass', 'Result 2 of 2 · seeds 1060 to 1159', [
  TABLE(100, 240, 1720, [4.3, 2.6, 2.6, 2.6, 1.5], [['Mean accuracy difference (95% CI)', 'Low noise', 'Mid noise', 'High noise', 'Verdict'],
    ['P1: signed minus frozen', 'not tested', cell('P1', 'mid'), cell('P1', 'high'), 'pass'],
    ['P2: signed minus signed, scene only'] + [cell('P2', l) for l in LV] + ['pass'],
    ['P3: signed minus uncertainty margin'] + [cell('P3', l) for l in LV] + ['pass'],
    ['P4: non-inferior to always-on at 0.6 calls', 'see next slide', 'see next slide', 'see next slide', 'pass'],
    ['Q1: signed plus VLM minus signed'] + [f"{sg(Q1[l]['mean_diff'], 4)} {ci(Q1[l]['ci95'], 4)}" for l in LV] + ['pass']], size=24, rowh=76, hl=[4]),
  T(100, 715, 1720, 300, bullets([
     'P1 replicates S4 from the first test, on seeds that nobody had looked at.',
     'P2: the candidate features matter even when both models use the signed-gain rule.',
     'P3: the lead over the uncertainty trigger is about 9 to 10 points of accuracy (0.091 to 0.103), averaged over budgets.',
     'Q1 (secondary) passes at all three levels. The shuffle and family controls were not repeated on the signed model, so extra capacity (71 vs 39 inputs) is not ruled out.'], size=28, gap=10))],
 FJ + ' hypotheses.final.P1/P2/P3 cells (mean_diff, ci95); P4 status. Q1 row: ' + VJ + ' hypotheses.final.Q1.cells.<level> (mean_diff, ci95), status pass; n_train 34,718, n_test 4,922.')

# 9 Headline
def card(lv, x):
    c = P4[lv]
    return stat(x, 400, 550, 430, lv.capitalize() + ' noise', sg(c['unsafe_diff']),
      [{'t': 'unsafe rate minus always-on', 'size': 28, 'color': GREY, 'gap': 6}, {'t': f"CI {ci(c['unsafe_diff_ci95'])}", 'size': 30, 'gap': 20},
       {'t': f"Accuracy minus always-on: {sg(c['acc_diff'])}", 'size': 30, 'bold': True, 'gap': 6}, {'t': f"CI {ci(c['acc_diff_ci95'])}", 'size': 28, 'color': GREY}])
slide('At 0.6 calls per decision, signed is within the accuracy margin of always-on and safer', 'Headline · budget 0.6 fixed before this test, chosen from the first final test; 20% of always-on’s 3 calls', [
  T(100, 250, 1720, 120, [{'t': 'On the same task, one fifth of the calls. At all three noise levels the unsafe rate is lower than always-on. Accuracy is within the 0.01 margin, and higher at mid and high noise.'}], size=38),
  ] + card('low', 100) + card('mid', 685) + card('high', 1270) + [
  T(100, 870, 1720, 150, [f"{lv.capitalize()}: accuracy {f3(rr(lv,'signed','at_budget_0.6')['acc'])} vs {f3(AO[lv]['mean_acc'])} for always-on, unsafe rate {f3(rr(lv,'signed','at_budget_0.6')['unsafe'])} vs {f3(AO[lv]['mean_unsafe'])}." for lv in LV] + [{'t': 'At low noise the accuracy gain is not distinguishable from 0, so we claim "not worse", not "better".', 'color': RUST}], size=26, color=INK)],
 FJ + ' hypotheses.final.P4.cells.<level> (acc_diff, acc_diff_ci95, unsafe_diff, unsafe_diff_ci95); absolute values: results.final/<level>.signed.at_budget_0.6 {acc, unsafe} and results.final/<level>.always_on {mean_acc, mean_unsafe}. 0.6 budget: run2/PREREG2.md (P4, chosen post hoc from first final, fresh seeds here).')

# 10 Pareto figure
slide('Accuracy against calls: signed reaches always-on early', 'Accuracy per call budget · mid noise · second final test', [
  IMG(100, 240, 1240, 698, 'f1_pareto_mid.png'),
  T(1380, 250, 440, 720, bullets([
     'Calls per decision on the x axis. Always-on is the star at 3.',
     'Signed first reaches always-on accuracy at 0.60, 0.50 and 0.35 calls per decision (low, mid, high), on a 0.05 grid. This is a post hoc reading of the curves, not a pre-registered test.',
     'The frozen MLP peaks, then loses accuracy as it spends more calls. Signed does not.',
     'Low and high noise: backup slides.'], size=28, gap=16))],
 'Figure: deliverables/figures/f1_pareto_mid.png (see figures/INDEX.md; source ' + FJ + ' results.final/mid.<method>.curve and always_on.mean_acc). First-reach budgets 0.60/0.50/0.35: computed from ' + FJ + ' results.final/<level>.signed.curve (21 points, step 0.05) against always_on.mean_acc, first index at or above (post hoc, descriptive). Frozen peak/drop: results.final/<level>.frozen.drop_after_0.65.')

# 11 Safety figure
slide('Safety: always-on’s unsafe rate reached by 0.45 to 0.55 calls', 'Unsafe rate per call budget · second final test · post hoc reading', [
  IMG(100, 230, 850, 478, 'f2_unsafe_mid.png'), IMG(970, 230, 850, 478, 'f2_unsafe_high.png'),
  T(100, 750, 1720, 280, bullets([
     'Left: mid noise. Right: high noise. Lower is better, and always-on is the star at 3 calls.',
     'Signed first matches always-on’s unsafe rate at 0.55 (low), 0.50 (mid) and 0.45 (high) calls per decision, then stays below it (post hoc reading of the curves, not a pre-registered test). The frozen MLP turns back up at high budgets.',
     'Unsafe means the oracle labels the chosen candidate unsafe. It is not a closed-loop collision rate.'], size=30, gap=12))],
 'Figures: deliverables/figures/f2_unsafe_mid.png and f2_unsafe_high.png (see figures/INDEX.md; source ' + FJ + ' results.final/<level>.<method>.unsafe_curve and always_on.mean_unsafe; first-match budgets 0.55/0.50/0.45 (low/mid/high) computed from signed.unsafe_curve, 0.05 grid, first index at or below always_on.mean_unsafe; post hoc, descriptive).')

# 12 What drives it
slide('What drives it: knowing which candidate is on top', 'Why it works', [
  T(100, 250, 1000, 760, bullets([
     '**Candidates beat scene.** A model with candidate features beats the scene-only model by 0.011 to 0.026 in every val and test cell.',
     f"**It holds on fresh seeds.** Signed minus signed scene-only: {sg(P['P2']['cells']['low']['mean_diff'])}, {sg(P['P2']['cells']['mid']['mean_diff'])}, {sg(P['P2']['cells']['high']['mean_diff'])} (low, mid, high), all CIs above 0.",
     '**The identity of the top candidate costs the most when shuffled.** Divergence features cost less (permutation importance, no ablation run).',
     'Divergence features (when and how the top two candidates part ways) add a smaller share. The time of divergence is the strongest one.',
     'Biggest gains over scene-only: lane blockage and occluded pedestrian.'], size=32, gap=18)),
  TABLE(1160, 250, 660, [3.4, 1.3, 1.3], [['Shuffled group', 'Mid', 'High'], ['Top candidate identity', '0.056', '0.046'], ['Scene and margin', '0.045', '0.036'], ['Occlusion', '0.027', '0.020'], ['Candidate divergence', '0.019', '0.014']], size=28, rowh=80, hl=[1, 2]),
  T(1160, 690, 660, 260, ['Drop in mean accuracy when a feature group is shuffled (val and test, frozen MLP).'], size=26, color=GREY)],
 'REPORT.md section 3 (Which features carry the lead: candidate_only vs scene_only 0.011-0.026; permutation drops 0.056/0.046, 0.045/0.036, 0.027/0.020 from analysis2/FAILURES.md section 3, 0.019/0.014 divergence). P2 values: ' + FJ + ' hypotheses.final.P2. Family gains: REPORT.md section 2 (S3, lane_blockage +0.052 to +0.058, occluded_pedestrian +0.040 to +0.048; first final).')

# 13 Where it goes wrong
slide('Where it goes wrong: late calls and wrong decisions', 'Failure analysis', [
  TABLE(100, 250, 960, [3, 1.5, 1.5], [['Harm rate at budget 0.1', 'Signed', 'Frozen']] + [[l.capitalize() + ' noise', f3(rr(l, 'signed', 'harm')['0.1']), f3(rr(l, 'frozen', 'harm')['0.1'])] for l in LV], size=30, rowh=84, hl=[1]),
  T(100, 700, 960, 300, [f"Harm rate: share of made calls whose tool has negative expected gain. Second final test. The uncertainty margin trigger at mid noise: {f3(rr('mid', 'uncertainty_margin', 'harm')['0.1'])}.", 'Drop in accuracy after budget 0.65, frozen vs signed: ' + ', '.join(f"{f3(rr(l,'frozen','drop_after_0.65'))} vs {f3(rr(l,'signed','drop_after_0.65'))}" for l in LV) + ' (low, mid, high).'], size=26, color=GREY),
  T(1120, 250, 700, 760, bullets([
     '**Late calls hurt.** On val and test, calls ranked past 65% are harmful 26% to 46% of the time, yet hold only 4% to 10% of the gain.',
     '**Wrong decision beats wrong tool.** 55% to 76% of the gap to the ceiling is calling the wrong decisions.',
     '**Depth collapse.** At mid noise the frozen model predicts depth on 1,514 of 2,222 val decisions. It predicts collision on 130, where collision is best on 272.'], size=30, gap=18))],
 'Harm and drop: ' + FJ + ' results.final/<level>.{signed,frozen,uncertainty_margin}.harm["0.1"] and .drop_after_0.65. Late calls, wrong decision vs wrong tool, depth collapse: REPORT.md section 3 (Failure modes), analysis2/FAILURES.md.')

# 14 VLM
slide('VLM features: a small gain, about half beyond scene family', 'Phase 5 · vision-language features', [
  T(100, 250, 1000, 760, bullets([
     '32 PCA dimensions of Qwen3.5-9B image features are added to the geometry features.',
     '**Frozen MLP:** +0.005 to +0.010 mean accuracy, positive for all three init seeds in every cell.',
     '**Signed model, val and test:** +0.008 to +0.015 over geometry-only on the same rows, all CIs above 0 (exploratory).',
     '**Controls (frozen MLP, one run per cell, no CIs):** shuffled features remove the gain. A scene-family code alone recovers 49% of it, so about half is information beyond family.'], size=32, gap=18)),
  RECT(1160, 250, 660, 420, 'D9EFEC'),
  T(1190, 275, 600, 380, [{'t': 'Q1: passes', 'size': 48, 'bold': True, 'color': TEAL, 'gap': 14}, {'t': 'Signed plus VLM minus signed, second final test, mean accuracy (95% CI):', 'size': 28, 'gap': 10}] + [{'t': f"{l.capitalize()}: {sg(Q1[l]['mean_diff'], 4)} {ci(Q1[l]['ci95'], 4)}", 'size': 28, 'gap': 6} for l in LV], size=30),
  T(1160, 700, 660, 300, ['The first final test had no frames, so it has no VLM result. The shuffle and family controls were not rerun on the signed model, so extra capacity (71 vs 39 inputs) is not ruled out.'], size=26, color=GREY)],
 'Frozen-MLP gain: REPORT.md section 3 (VLM features), docs/phase5_vlm.md Controls (shuffle at or below geometry in 5 of 6 cells; family recovers 20% to 77%, 49% overall). Signed + VLM +0.008 to +0.015: run2/experiments/EXPERIMENTS2.md section B table (cells +0.0084 to +0.0149). Q1 box: ' + VJ + ' hypotheses.final.Q1.cells.<level> (mean_diff, ci95), status pass.')

# 15 Limits
slide('Limits: what these numbers do and do not show', 'Limits', [
  T(100, 240, 1720, 780, bullets([
     '**Open loop, not driving.** Accuracy is top-1 agreement with the oracle’s best candidate. We never ran the chosen candidate in the simulator.',
     '**"Unsafe" is a label, not a collision.** It is the oracle’s unsafe label on the chosen candidate. No closed-loop collision rate exists.',
     '**Simulated tools.** A call is a noisy simulated tool, not a real perception model. Always-on merges all three outputs and is not a VLM verifier.',
     '**One simulator and one generator.** MetaDrive, six families, one noise model. Seeds differ across splits, but the generator does not.',
     '**Multiple comparisons.** Four primary hypotheses, no correction. About a dozen variants were tried on val and test before one was pre-registered.',
     '**The 0.6 budget was chosen post hoc** from the first final test. The second test used fresh seeds, but the budget was not blind to the first.',
     '**VLM controls have no CIs** and were not repeated on the signed model.'], size=32, gap=16))],
 'REPORT.md section 4 (Limits); run2/PREREG2.md (P4 note on 0.6 budget; multiple comparisons paragraph); run2/experiments/EXPERIMENTS2.md (header: about a dozen variants, multiple-comparisons caveat). Nine variants in run 1: REPORT.md section 3 (Learner variants).')

# 16 Next steps
slide('Next steps', 'What we would do next', [
  T(100, 250, 1720, 760, bullets([
     '**Closed loop.** Run the selected candidate in MetaDrive and count collisions at about 0.6 calls per decision, against always-on. This is the main gap.',
     '**Control the VLM gain.** Q1 passed, but repeat the shuffle and family controls on the signed model, since capacity is not ruled out.',
     '**Choose the tool better.** The signed model stops calling at the right places, but picks the best tool less often. Offsets and thresholds gave nothing, so try a two-stage model.',
     '**Put CIs on unsafe-rate differences** at a budget fixed in advance. Only accuracy has CIs in the first test.',
     '**Look at lead_brake_cutin.** It is the largest family, has the lowest ceiling and is where simple triggers can win.',
     '**Test with real tools** and a second simulator.'], size=34, gap=20))],
 'REPORT.md section 5 (next steps 1, 2, 3, 4, 6, 7). Offsets and thresholds null: run2/experiments/EXPERIMENTS2.md sections A and D. Real tools / second simulator: our addition from the limits (no file source).')

# 17 Summary
slide('Summary', 'Take-away', [
  T(100, 250, 1720, 760, bullets([
     'A selector that sees the candidate trajectories beats the generic uncertainty trigger by about 0.07 to 0.10 mean accuracy, and beats a scene-only selector.',
     'The signed-gain version stops calling when no tool is predicted to help, so the curve no longer falls at high budgets. It confirmed on fresh seeds at mid and high noise.',
     f"At 0.6 calls per decision, 20% of always-on’s cost, it is within the 0.01 accuracy margin of always-on and safer at all three noise levels. Unsafe rate is {sg(P4['low']['unsafe_diff'])}, {sg(P4['mid']['unsafe_diff'])} and {sg(P4['high']['unsafe_diff'])} relative to always-on.",
     'Adding VLM image features to the signed model helps at all three noise levels (Q1, +0.010 to +0.016), though capacity is not ruled out.',
     'The evidence is open loop with simulated tools. Closed-loop collisions are the next test.'], size=38, gap=28))],
 'Slide 7 (H1 range +0.071 to +0.093) and slide 8 (P3 +0.091 to +0.103), see their sources; P4 unsafe differences: ' + FJ + ' hypotheses.final.P4.cells.<level>.unsafe_diff.')

# ---------- backups ----------
slide('Backup: first final test, mean accuracy by policy', 'Backup · seeds 760 to 859', [
  TABLE(100, 240, 1720, [3.5, 1.5, 1.5, 1.5], [['Policy', 'Low', 'Mid', 'High']] + [list(r) for r in [
    ['random', '0.3835', '0.3265', '0.2719'], ['uncertainty_margin', '0.4058', '0.3543', '0.2881'], ['scene_only', '0.4788', '0.4123', '0.3376'],
    ['candidate_only', '0.4901', '0.4287', '0.3541'], ['plandiscrim (frozen)', '0.4990', '0.4338', '0.3588'], ['plandiscrim_flip', '0.4990', '0.4367', '0.3599'],
    ['signed_mse_abstain', '0.5028', '0.4437', '0.3763'], ['fair_ceiling', '0.5413', '0.4726', '0.3867']]], size=30, rowh=76, hl=[], bold_rows=[7])],
 'REPORT.md section 2, "Mean accuracy over budgets" table (results.final/<level>.<policy>.mean_acc in out/v3_eval/triggers_final.json; signed_mse_abstain from s4_signed.json).', backup=True)

slide('Backup: second final test, all methods', 'Backup · seeds 1060 to 1159', [
  TABLE(100, 240, 1720, [3.4, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4], [['Method', 'Acc low', 'Acc mid', 'Acc high', 'Unsafe low', 'Unsafe mid', 'Unsafe high']] +
    [[n] + [f4(rr(l, m, 'mean_acc')) for l in LV] + [f4(rr(l, m, 'mean_unsafe')) for l in LV] for n, m in [('signed', 'signed'), ('frozen', 'frozen'), ('signed, scene only', 'signed_scene'), ('uncertainty margin', 'uncertainty_margin')]] +
    [['always-on (3 calls)'] + [f4(AO[l]['mean_acc']) for l in LV] + [f4(AO[l]['mean_unsafe']) for l in LV]], size=30, rowh=84, hl=[], bold_rows=[1]),
  T(100, 760, 1720, 200, ['Mean over 21 budgets for the budgeted methods. Always-on has no budget, so its value is a single number.'], size=28, color=GREY)],
 FJ + ' results.final/<level>.<method>.mean_acc and mean_unsafe; always_on.mean_acc and mean_unsafe.', backup=True)

slide('Backup: second final test, harm rate and benefit captured', 'Backup · seeds 1060 to 1159', [
  TABLE(100, 240, 1720, [2.2, 2.6, 1.5, 1.5, 1.5, 1.5], [['Level', 'Method', '0.1', '0.2', '0.3', '0.5']] +
    [[l.capitalize(), m, *[f"{f3(rr(l, k, 'harm')[b])} / {f3(rr(l, k, 'benefit')[b])}" for b in ['0.1', '0.2', '0.3', '0.5']]] for l in LV for m, k in [('signed', 'signed'), ('frozen', 'frozen'), ('margin', 'uncertainty_margin')]], size=26, rowh=68, hl=[]),
  T(100, 940, 1720, 60, ['Each cell: harm rate / benefit captured, at budgets 0.1, 0.2, 0.3 and 0.5.'], size=26, color=GREY)],
 FJ + ' results.final/<level>.<method>.harm and .benefit (keys "0.1", "0.2", "0.3", "0.5").', backup=True)

fam = ['ambiguous_light', 'lane_blockage', 'lead_brake_cutin', 'merge_closing_speed', 'occluded_cross_traffic', 'occluded_pedestrian']
slide('Backup: second final test, accuracy by scenario family', 'Backup · seeds 1060 to 1159', [
  TABLE(100, 240, 1720, [3.6, 2.2, 2.2, 2.2], [['Family (signed / scene-only)', 'Low', '', 'Mid', '', 'High', '']] if False else [['Family: signed / signed scene-only', 'Low', 'Mid', 'High']] +
    [[fm] + [f"{f3(rr(l,'signed','by_family')[fm])} / {f3(rr(l,'signed_scene','by_family')[fm])}" for l in LV] for fm in fam], size=30, rowh=84, hl=[]),
  T(100, 880, 1720, 120, ['Mean accuracy over budgets. No family-level CIs were computed.'], size=28, color=GREY)],
 FJ + ' results.final/<level>.{signed,signed_scene}.by_family.<family>.', backup=True)

slide('Backup: first final test, post hoc unsafe rate against always-on', 'Backup · post hoc, not pre-registered', [
  TABLE(100, 240, 1720, [3.4, 2, 2, 2], [['Unsafe minus always-on (95% CI)', 'Low', 'Mid', 'High'],
    ['Frozen, at its accuracy-match budget (0.60 / 0.50 / 0.35)', '−0.005 [−0.012, 0.003]', '0.000 [−0.010, 0.010]', '+0.043 [0.030, 0.056]'],
    ['Signed, at the same budgets', '−0.014 [−0.022, −0.006]', '−0.013 [−0.024, −0.002]', '+0.032 [0.019, 0.045]'],
    ['Signed, at 0.5 calls', '+0.011 [0.001, 0.020]', '−0.013 [−0.024, −0.002]', '−0.017 [−0.029, −0.004]'],
    ['Signed, at 0.7 calls', '−0.018 [−0.025, −0.010]', '−0.030 [−0.040, −0.021]', '−0.035 [−0.045, −0.024]']], size=28, rowh=104, hl=[]),
  T(100, 800, 1720, 200, ['This analysis led us to fix the 0.6 budget for the second test. The CIs are for chosen budgets and are not corrected for the number of budgets looked at.'], size=28, color=GREY)],
 'run2/analysis4/H3_POSTHOC.md sections 1 and 2 (values rounded to 3 decimals; data in run2/analysis4/h3_posthoc.json).', backup=True)

slide('Backup: signed plus VLM features, val and test (exploratory)', 'Backup · exploratory', [
  TABLE(100, 240, 1720, [3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5], [['Difference in mean accuracy', 'val low', 'test low', 'val mid', 'test mid', 'val high', 'test high'],
    ['Signed + VLM minus signed', '+0.0110', '+0.0149', '+0.0113', '+0.0116', '+0.0088', '+0.0084'],
    ['Signed scene-only minus signed', '−0.0227', '−0.0250', '−0.0250', '−0.0361', '−0.0286', '−0.0347']], size=28, rowh=100, hl=[]),
  T(100, 620, 1720, 380, ['All CIs for the VLM row are above 0 (for example val low [+0.0070, +0.0152]). The comparator was trained on the same 25,036 rows. The VLM model has 71 inputs against 39, so extra capacity is not ruled out for the signed model.'], size=30)],
 'run2/experiments/EXPERIMENTS2.md results table, rows B and C (CIs in the same table).', backup=True)

def bfig(title, names, src, cap=''):
    if len(names) == 1:
        els = [IMG(100, 230, 1500 if False else 1280, 720, names[0])]
    slide(title, 'Backup', els, src, backup=True)
slide('Backup: accuracy against calls at low and high noise', 'Backup · second final test', [IMG(100, 230, 850, 478, 'f1_pareto_low.png'), IMG(970, 230, 850, 478, 'f1_pareto_high.png'),
  T(100, 770, 1720, 120, ['Left: low noise. Right: high noise. Calls per decision on the x axis, always-on at 3.'], size=30)],
  'Figures: figures/f1_pareto_low.png, f1_pareto_high.png (source ' + FJ + ' results.final/<level>.<method>.curve).', backup=True)
slide('Backup: the 0.6-call test against its pass margins', 'Backup · P4', [IMG(100, 230, 1400, 735, 'f3_p4.png'),
  T(1540, 260, 300, 600, ['Shaded zones fail the test: more than 0.01 less accurate, or more than 0.01 more unsafe.'], size=26, color=GREY)],
  'Figure: figures/f3_p4.png (source ' + FJ + ' hypotheses.final.P4.cells).', backup=True)
slide('Backup: every pre-registered difference, both final tests', 'Backup · forest plot', [IMG(500, 220, 960, 792, 'f4_hypotheses.png')],
  'Figure: figures/f4_hypotheses.png (sources in figures/INDEX.md: triggers_final.json comparisons, s4_signed.json diff_vs_frozen, ' + FJ + ' hypotheses).', backup=True)
slide('Backup: harm rate by budget at mid noise', 'Backup · second final test', [IMG(100, 230, 1240, 698, 'f5_harm.png'),
  T(1380, 250, 440, 700, ['Harm rate: share of made calls whose tool has negative expected gain.', 'The uncertainty margin spends its first calls where a tool hurts.'], size=30)],
  'Figure: figures/f5_harm.png (source ' + FJ + ' results.final/mid.<method>.harm).', backup=True)
slide('Backup: wrong decision against wrong tool', 'Backup · exploratory, val and test', [IMG(100, 230, 1130, 720, 'f6_gap_split.png'),
  T(1270, 250, 550, 700, ['Share of the gap to the ceiling that comes from calling the wrong decisions (a) and from choosing the wrong tool (b). Frozen MLP, one init seed.'], size=30)],
  'Figure: figures/f6_gap_split.png (source analysis2/results.json cells.<split>/<level>.q2.plandiscrim; table T4 of analysis2/FAILURES.md).', backup=True)
slide('Backup: VLM controls', 'Backup · exploratory, one run per cell, no CIs', [IMG(100, 230, 1150, 690, 'f7_vlm_controls.png'),
  T(1290, 250, 530, 700, ['Real features help. Shuffled features remove the gain. A scene-family code recovers part of it. Frozen MLP, 25,036 training rows.'], size=30)],
  'Figure: figures/f7_vlm_controls.png (source out/v2_eval/vlm_extra_train.json and vlm_control_*.json; table in docs/phase5_vlm.md Controls).', backup=True)
