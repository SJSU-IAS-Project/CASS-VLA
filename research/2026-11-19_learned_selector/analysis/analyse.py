import json, csv, numpy as np
R='out/v3_eval/triggers.json'
d=json.load(open(R))['results']
P=['random','uncertainty_margin','ego_speed','candidate_spread','fixed_schedule','scene_only','candidate_only','plandiscrim','fair_ceiling']
cells=[f'{s}/{l}' for s in('val','test') for l in('low','mid','high')]
simple=['uncertainty_margin','ego_speed','candidate_spread','fixed_schedule']
with open('research/2026-11-19_learned_selector/analysis/tables.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['table','cell','policy','metric','value','source'])
    for c in cells:
        for p in P: w.writerow(['headline',c,p,'mean_acc_over_budgets_0_to_1',d[c][p]['mean_acc'],f'{R}:results.{c}.{p}.mean_acc'])
    for c in cells:
        for p in P[:8]:
            if 'by_budget' in d[c][p]:
                for b,v in d[c][p]['by_budget'].items():
                    for m,x in v.items(): w.writerow(['budget_split',c,p,f'{m}@{b}',x,f'{R}:results.{c}.{p}.by_budget.{b}.{m}'])
    for c in cells:
        for a,v in d[c]['knowno'].items():
            for m,x in v.items(): w.writerow(['knowno',c,f'alpha{a}',m,x,f'{R}:results.{c}.knowno.{a}.{m}'])
print('GAP CLOSURE')
for c in cells:
    r=d[c]; bs=max(simple,key=lambda p:r[p]['mean_acc']); b=r[bs]['mean_acc']; ce=r['fair_ceiling']['mean_acc']
    print(c,bs,b,'plan',r['plandiscrim']['mean_acc'],'ceil',ce,'gap',round(ce-b,4),'closed',round((r['plandiscrim']['mean_acc']-b)/(ce-b),3),
     'scene closed',round((r['scene_only']['mean_acc']-b)/(ce-b),3),'cand closed',round((r['candidate_only']['mean_acc']-b)/(ce-b),3),
     'p-c',round(r['plandiscrim']['mean_acc']-r['candidate_only']['mean_acc'],4),'c-s',round(r['candidate_only']['mean_acc']-r['scene_only']['mean_acc'],4),'p-s',round(r['plandiscrim']['mean_acc']-r['scene_only']['mean_acc'],4))
print('SEEDS')
for c in cells: print(c,{p:d[c][p]['by_seed'] for p in('scene_only','candidate_only','plandiscrim')})
print('BUDGET')
for c in ('test/mid','test/high','val/mid'):
  for p in ['random','uncertainty_margin','ego_speed','fixed_schedule','scene_only','candidate_only','plandiscrim']:
    print(c,p,{b:(v['acc'],v['harm_rate'],v['benefit_captured']) for b,v in d[c][p]['by_budget'].items()})
print('FAMILY')
fams=sorted(d['test/mid']['plandiscrim']['by_family'])
for c in cells:
  for f in fams:
    r=d[c]; pl=r['plandiscrim']['by_family'][f]; sc=r['scene_only']['by_family'][f]
    bs=max(simple,key=lambda p:r[p]['by_family'][f]); bsv=r[bs]['by_family'][f]
    print(c,f,'pl',pl,'sc',sc,'best simple',bs,bsv,'pl-sc',round(pl-sc,4),'pl-simple',round(pl-bsv,4), 'FLAG' if pl<sc or pl<bsv else '')
print('KNOWNO')
for c in cells: print(c,json.dumps(d[c]['knowno']))
print('CURVE cross: first budget where plan<scene or plan<unc, test/mid, test/high, val/*')
for c in cells:
  r=d[c]; print(c,[round(b*0.05,2) for b in range(21) if r['plandiscrim']['curve'][b]<r['scene_only']['curve'][b]-1e-9], 'vs best simple',[round(i*0.05,2) for i in range(21) if r['plandiscrim']['curve'][i]<max(r[p]['curve'][i] for p in simple)-1e-9])
