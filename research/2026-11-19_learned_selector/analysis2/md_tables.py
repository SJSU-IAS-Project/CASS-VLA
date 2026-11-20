import json
r=json.load(open('results.json'))['cells']
cells=list(r)
o=[]
def T(h,rows):
    o.append("| "+" | ".join(h)+" |"); o.append("|"+"---|"*len(h))
    for x in rows: o.append("| "+" | ".join(str(v) for v in x)+" |")
    o.append("")
o.append("### T1 ranks 0-65% against 65-100%, plandiscrim seed 0\n")
rows=[]
for c in cells:
    q=r[c]['q1_by_rank'];e,l=q[5],q[6]
    rows.append([c,e['mean_pred_score'],e['mean_ge_chosen'],e['frac_chosen_negative'],l['n'],l['mean_pred_score'],l['mean_ge_chosen'],l['mean_ge_best'],l['frac_chosen_negative'],l['frac_chosen_zero'],l['frac_chosen_positive'],l['frac_notool_correct'],r[c]['q1_share_of_total_best_gain_in_late']])
T(["cell","early score","early gain of chosen","early harm","late n","late score","late gain of chosen","late best-tool gain","late harm","late zero","late positive","late no-tool correct","share of best gain in late"],rows)
o.append("### T2 late decisions, mean expected gain per tool and chosen-tool mix\n")
rows=[]
for c in cells:
    l=r[c]['q1_by_rank'][6]
    rows.append([c]+[l['mean_ge_per_tool'][t] for t in ('roi','depth','collision')]+[l['chosen_tool_share'][t] for t in ('roi','depth','collision')])
T(["cell","gain if roi","gain if depth","gain if collision","chosen roi","chosen depth","chosen collision"],rows)
o.append("### T3 late decisions by family (harm share / mean expected gain of chosen / share where no tool has positive gain / n)\n")
fams=list(r['val/mid']['q1_late_by_family'])
rows=[]
for f in fams:
    rows.append([f]+[f"{r[c]['q1_late_by_family'][f]['frac_neg']:.2f} / {r[c]['q1_late_by_family'][f]['mean_ge_chosen']:+.2f} / {r[c]['q1_late_by_family'][f]['frac_no_tool_helps']:.2f} / {r[c]['q1_late_by_family'][f]['n']}" for c in ('val/mid','test/mid','val/high','test/high')])
T(["family","val/mid","test/mid","val/high","test/high"],rows)
o.append("### T4 gap to the fair ceiling in expected accuracy, split (plandiscrim seed 0; scene_only in brackets)\n")
rows=[]
for c in cells:
    for b in (0.2,0.5):
        x=[z for z in r[c]['q2']['plandiscrim'] if z['budget']==b][0]; y=[z for z in r[c]['q2']['scene_only'] if z['budget']==b][0]
        a=x['a_missed_positive_mass']+x['a_calls_where_no_tool_helps']; ay=y['a_missed_positive_mass']+y['a_calls_where_no_tool_helps']
        rows.append([c,b,x['gap_exp_acc'],f"{a:.4f} ({a/x['gap_exp_acc']:.0%})",f"{x['b_wrong_tool']:.4f} ({x['b_wrong_tool']/x['gap_exp_acc']:.0%})",x['frac_calls_in_ceiling_set'],x['frac_calls_wrong_tool'],x['frac_calls_neg_chosen'],
                     f"[{y['gap_exp_acc']:.4f}; a {ay/y['gap_exp_acc']:.0%}; b {y['b_wrong_tool']/y['gap_exp_acc']:.0%}]"])
T(["cell","budget","gap","(a) wrong decisions","(b) wrong tool","calls inside ceiling set","calls with a non-best tool","calls with negative gain","scene_only [gap; shares]"],rows)
o.append("### T5 bootstrap, mean difference over budgets and 95% interval over scenario seeds\n")
rows=[]
for c in cells:
    q=r[c]['q5']
    rows.append([c]+[f"{q[k]['mean_diff']:+.4f} [{q[k]['ci95'][0]:+.4f}, {q[k]['ci95'][1]:+.4f}]" for k in ('plandiscrim_minus_scene_only','plandiscrim_minus_uncertainty_margin')]+[q['n_scenario_seeds']])
T(["cell","minus scene_only","minus uncertainty_margin","seeds"],rows)
o.append("### T6 plandiscrim minus scene_only by family, interval over seeds (intervals that include 0 marked *)\n")
rows=[]
for f in fams:
    row=[f]
    for c in cells:
        v=r[c]['q5']['plandiscrim_minus_scene_only']['by_family'][f]; row.append(f"{v['mean_diff']:+.3f}{'*' if v['ci95'][0]<=0 else ''}")
    rows.append(row)
T(["family"]+cells,rows)
o.append("### T7 permutation importance, drop in mean accuracy over budgets (val / test)\n")
for nm in ('plandiscrim','scene_only'):
    for lv in ('mid','high'):
        imp={s:r[f'{s}/{lv}']['q3'][nm]['importance'] for s in ('val','test')}
        ks=sorted(imp['val'],key=lambda k:-(imp['val'][k]['drop']+imp['test'][k]['drop']))
        gs=[k for k in ks if k.startswith('GROUP')]; fs=[k for k in ks if not k.startswith('GROUP')][:10]
        o.append(f"**{nm}, {lv} noise** (base {r['val/'+lv]['q3'][nm]['base_mean_acc']} val, {r['test/'+lv]['q3'][nm]['base_mean_acc']} test)\n")
        T(["unit","val","test"],[[k.replace('GROUP:','group: '),imp['val'][k]['drop'],imp['test'][k]['drop']] for k in gs+fs])
o.append("### T8 divergence features singly, mean of val and test, plandiscrim\n")
div=["div_time","div_occl","div_actor_near","div_lateral","div_progress","runner_safe","runner_clearance","runner_ttc","runner_is_change","light_splits_top2"]
T(["feature","mid","high"],[[k]+[round((r[f'val/{lv}']['q3']['plandiscrim']['importance'][k]['drop']+r[f'test/{lv}']['q3']['plandiscrim']['importance'][k]['drop'])/2,4) for lv in ('mid','high')] for k in div])
o.append("### T9 per-family tool choice, mid noise, val and test pooled (counts)\n")
import numpy as np
rows=[]
for f in fams:
    M=np.zeros((4,3),int);n=0;opt=[];reg=[]
    for s in('val','test'):
        d=r[f'{s}/mid']['q4'][f];M+=np.array(d['matrix_rows_best_roi_depth_collision_none_cols_pred_roi_depth_collision']);n+=d['n']
        opt.append((d['tool_optimal_rate_among_positive'],d['n']));reg.append(d['mean_regret_among_positive'])
    pos=M[:3].sum()
    rows.append([f,n,f"{M[3].sum()/n:.2f}",f"roi {M[:,0].sum()}, depth {M[:,1].sum()}, coll {M[:,2].sum()}",f"roi {M[0].sum()}, depth {M[1].sum()}, coll {M[2].sum()}",f"{(M[0,0]+M[1,1]+M[2,2])/pos:.2f}",f"{np.mean([x[0] for x in opt]):.2f}",f"{np.mean(reg):.3f}"])
T(["family","n","share where no tool helps","predicted tool counts","best tool counts (argmax, ties to roi first)","exact-argmax agreement","tool-optimal rate (ties count)","mean regret"],rows)
rows=[]
for c in ('val/mid','test/mid','val/high','test/high'):
    d=r[c]['q4_by_tool']
    for t in d: rows.append([c,t,d[t]['n_best'],d[t]['pred_when_best'],d[t]['n_pred'],d[t]['precision_tool_optimal']])
o.append("### T10 per tool\n")
T(["cell","tool","decisions where it is the unique-or-first best","predicted tool when it is best (roi, depth, collision)","times predicted","share of predictions that are tool-optimal"],rows)
open('tables.md','w').write("\n".join(o))
