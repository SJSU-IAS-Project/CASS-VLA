import json
D=json.load(open('/home/user/CASS-VLA/out/v3_eval/dev/triggers_v2.json'))['results']
C=json.load(open('calc.json'))
cells=list(D)
P=['plandiscrim','scene_only','candidate_only','uncertainty_margin']
f=lambda x:'not reached' if x is None else f'{x:.2f}'
print('### T1')
print('| cell | always_on acc | always_on unsafe | best single acc (budget 1.0) | best single unsafe |\n|---|---|---|---|---|')
for c in cells:
    a=C[c]['ao'];b=C[c]['p']['best_single'];print(f"| {c} | {a['acc']} | {a['unsafe']} | {b['acc']} | {b['uns']} |")
for k,t in (('acc','accuracy'),('uns','unsafe'),('both','both')):
    print(f'\n### T2 {t}: calls per decision (= budget)')
    print('| cell | '+' | '.join(P)+' |\n|'+'---|'*(len(P)+1))
    for c in cells: print(f'| {c} | '+' | '.join(f(C[c]['p'][p][k]) for p in P)+' |')
print('\n### T3 pct of 3 calls (both)')
for c in cells: print(f'| {c} | '+' | '.join('not reached' if C[c]['p'][p]['both'] is None else f"{C[c]['p'][p]['both']/3*100:.0f}%" for p in P)+' |')
print('\n### T4 unsafe at budgets')
for c in cells:
    print(f"| {c} | {D[c]['plandiscrim']['unsafe_curve'][0]} |"+' | '.join(' '.join(str(D[c][p]['unsafe_curve'][int(b/.05)]) if p!='random' else str(D[c]['random']['by_budget'][str(b)]['unsafe']) for b in (.1,.2,.3,.5)) for p in ['plandiscrim','scene_only','candidate_only','uncertainty_margin','random'])+' |')
print('\n### opposite')
for c in cells:
  for p in P:
    a=D[c][p]['curve'];u=D[c][p]['unsafe_curve'];B=[i*.05 for i in range(21)]
    ops=[(round(B[i],2),round(a[i]-a[i-1],4),round(u[i]-u[i-1],4)) for i in range(1,21) if (a[i]-a[i-1])*(u[i]-u[i-1])>0]
    print(c,p,'acc up&unsafe up or both down steps:',ops)
    print('   argmax acc',B[a.index(max(a))],'argmin unsafe',B[u.index(min(u))],'acc@1',a[-1],'unsafe@1',u[-1])
