import json
d=json.load(open('/home/user/CASS-VLA/out/v3_eval/dev/triggers_v2.json'))['results']
P=['plandiscrim','scene_only','candidate_only','uncertainty_margin']
B=[round(i*.05,2) for i in range(21)]
def first(r,p,t,key):
    c=r[p][key]
    for b,v in zip(B,c):
        if (key=='curve' and v>=t) or (key=='unsafe_curve' and v<=t): return b
def both(r,p,ta,tu):
    for i,b in enumerate(B):
        if r[p]['curve'][i]>=ta and r[p]['unsafe_curve'][i]<=tu: return b
out={}
for cell,r in d.items():
    ao=r['always_on']; out[cell]=dict(ao=ao)
    o={}
    for p in P:
        o[p]=dict(acc=first(r,p,ao['acc'],'curve'),uns=first(r,p,ao['unsafe'],'unsafe_curve'),both=both(r,p,ao['acc'],ao['unsafe']),
          c0=(r[p]['curve'][0],r[p]['unsafe_curve'][0]),c1=(r[p]['curve'][-1],r[p]['unsafe_curve'][-1]),
          ub={b:r[p]['unsafe_curve'][int(round(b/.05))] for b in (.1,.2,.3,.5)},
          best_unsafe=min(r[p]['unsafe_curve']),argbest=B[r[p]['unsafe_curve'].index(min(r[p]['unsafe_curve']))],
          peak_acc=max(r[p]['curve']),argacc=B[r[p]['curve'].index(max(r[p]['curve']))],
          opp=[B[i] for i in range(1,21) if (r[p]['curve'][i]-r[p]['curve'][i-1])*(r[p]['unsafe_curve'][i]-r[p]['unsafe_curve'][i-1])>0 and r[p]['unsafe_curve'][i]>r[p]['unsafe_curve'][i-1]!=0 and r[p]['curve'][i]<r[p]['curve'][i-1]])
    o['random']=dict(ub={b:r['random']['by_budget'][str(b)]['unsafe'] for b in (.1,.2,.3,.5)},acc={b:r['random']['by_budget'][str(b)]['acc'] for b in (.1,.2,.3,.5)})
    o['best_single']=dict(acc=r['uncertainty_margin']['curve'][-1],uns=r['uncertainty_margin']['unsafe_curve'][-1],same=[r[k]['curve'][-1] for k in ('uncertainty_margin','ego_speed','candidate_spread')],nt=(r['uncertainty_margin']['curve'][0],r['uncertainty_margin']['unsafe_curve'][0]))
    out[cell]['p']=o
json.dump(out,open('calc.json','w'),indent=1)
for cell,v in out.items():
    print(cell,v['ao'])
    for p,x in v['p'].items():
        if p in('random','best_single'): print(' ',p,x); continue
        print(' ',p,x['acc'],x['uns'],x['both'],'b0',x['c0'],'b1',x['c1'],x['ub'],'minU',x['best_unsafe'],x['argbest'],'peakacc',x['peak_acc'],x['argacc'],'opp',x['opp'])
