import json
r=json.load(open('results.json'))['cells']
cells=list(r)
def p(*a): print(*a)
p("## Q1 late vs early (rank >65%)")
for c in cells:
    q=r[c]['q1_by_rank']
    for row in q[3:5]+q[6:]:
        pass
    e,l=q[5],q[6]
    p(c,"early: score %.3f geC %.3f neg %.3f | late: n %d score %.3f geC %.3f geBest %.3f neg %.3f zero %.3f nohelp %.3f notool_ok %.3f tools %s perTool %s sh_totbest %.3f sh_chosen %.3f"%(e['mean_pred_score'],e['mean_ge_chosen'],e['frac_chosen_negative'],l['n'],l['mean_pred_score'],l['mean_ge_chosen'],l['mean_ge_best'],l['frac_chosen_negative'],l['frac_chosen_zero'],l['frac_no_tool_helps'],l['frac_notool_correct'],l['chosen_tool_share'],l['mean_ge_per_tool'],r[c]['q1_share_of_total_best_gain_in_late'],r[c]['q1_share_of_chosen_gain_in_late']))
p("## late by family")
for c in cells:
    p(c,{f:(v['n'],v['frac_neg'],v['mean_ge_chosen'],v['frac_no_tool_helps']) for f,v in r[c]['q1_late_by_family'].items()})
    p(c,'tool',r[c]['q1_late_by_tool'])
p("## Q2")
for c in cells:
    for nm in ('plandiscrim','scene_only'):
        for row in r[c]['q2'][nm]:
            if row['budget'] in (0.2,0.5): p(c,nm,row)
p("## Q5")
for c in cells: p(c,{a:(v['mean_diff'],v['ci95']) for a,v in r[c]['q5'].items() if isinstance(v,dict)})
