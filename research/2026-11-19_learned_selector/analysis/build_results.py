import json
T='out/v3_eval/triggers.json'
d=json.load(open(T))['results']
a=json.load(open('out/v2_eval/vlm.json'))['results']; b=json.load(open('out/v2_eval/vlm_extra_train.json'))['results']
cells=[f'{s}/{l}' for s in('val','test') for l in('low','mid','high')]
P=['random','uncertainty_margin','ego_speed','candidate_spread','fixed_schedule','scene_only','candidate_only','plandiscrim','fair_ceiling']
simple=['uncertainty_margin','ego_speed','candidate_spread','fixed_schedule']
def tab(h,rows): return '| '+' | '.join(h)+' |\n|'+'---|'*len(h)+'\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
f3=lambda x:f'{x:.3f}'
# headline
H=tab(['Policy']+cells,[[p]+[f3(d[c][p]['mean_acc']) for c in cells] for p in P])
# gap
G=[]
for c in cells:
    r=d[c]; bs=max(simple,key=lambda p:r[p]['mean_acc']); bv=r[bs]['mean_acc']; ce=r['fair_ceiling']['mean_acc']
    cl=lambda p:f"{100*(r[p]['mean_acc']-bv)/(ce-bv):.0f}%"
    G.append([c,bs,f3(bv),f3(ce),f3(ce-bv),f3(r['plandiscrim']['mean_acc']),cl('plandiscrim'),cl('candidate_only'),cl('scene_only')])
G=tab(['Cell','Best simple trigger','Its acc','Ceiling','Gap','plandiscrim','Gap closed by plandiscrim','by candidate_only','by scene_only'],G)
# cand vs scene
C=tab(['Cell','scene_only','candidate_only','plandiscrim','candidate - scene','plandiscrim - candidate','plandiscrim by_seed range'],
 [[c,f3(d[c]['scene_only']['mean_acc']),f3(d[c]['candidate_only']['mean_acc']),f3(d[c]['plandiscrim']['mean_acc']),
   f"{d[c]['candidate_only']['mean_acc']-d[c]['scene_only']['mean_acc']:+.3f}",f"{d[c]['plandiscrim']['mean_acc']-d[c]['candidate_only']['mean_acc']:+.3f}",
   f"{min(d[c]['plandiscrim']['by_seed']):.4f} to {max(d[c]['plandiscrim']['by_seed']):.4f}"] for c in cells])
# harm/benefit
def hb(c):
    rows=[]
    for p in ['random','uncertainty_margin','ego_speed','fixed_schedule','scene_only','candidate_only','plandiscrim']:
        row=[p]
        for b_ in ('0.1','0.2','0.3','0.5'):
            v=d[c][p]['by_budget'][b_]; row.append(f"{v['acc']:.3f} / {v['harm_rate']:.3f} / {v['benefit_captured']:.3f}")
        rows.append(row)
    return tab(['Policy (acc / harm rate / benefit captured)','0.1','0.2','0.3','0.5'],rows)
# family
fams=sorted(d['test/mid']['plandiscrim']['by_family'])
def fam(c):
    r=d[c]; rows=[]
    for f in fams:
        bs=max(simple,key=lambda p:r[p]['by_family'][f]); bv=r[bs]['by_family'][f]
        pl,sc=r['plandiscrim']['by_family'][f],r['scene_only']['by_family'][f]
        flag=[]
        if pl<sc: flag.append('loses to scene_only')
        if pl<bv: flag.append('loses to '+bs)
        rows.append([f,f3(pl),f3(sc),f'{bs} {f3(bv)}',f'{pl-sc:+.3f}',f'{pl-bv:+.3f}','; '.join(flag)])
    return tab(['Family','plandiscrim','scene_only','Best simple trigger','pl - scene','pl - simple','Flag'],rows)
flags=[]
for c in cells:
    r=d[c]
    for f in fams:
        pl=r['plandiscrim']['by_family'][f]; sc=r['scene_only']['by_family'][f]
        bs=max(simple,key=lambda p:r[p]['by_family'][f]); bv=r[bs]['by_family'][f]
        if pl<sc or pl<bv: flags.append([c,f,f3(pl),f3(sc),f'{bs} {f3(bv)}',f'{pl-sc:+.3f}',f'{pl-bv:+.3f}'])
FL=tab(['Cell','Family','plandiscrim','scene_only','Best simple trigger','pl - scene','pl - simple'],flags)
# knowno
K=tab(['Cell','alpha','Threshold','Call rate','knowno acc','plandiscrim at nearest budget (budget)'],
 [[c,al,('inf' if v['threshold']==float('inf') else v['threshold']),v['call_rate'],v['acc'],f"{v['plandiscrim_at_nearest_budget']} ({v['nearest_budget']})"] for c in ('test/mid','test/high','val/mid') for al,v in d[c]['knowno'].items()])
# vlm
V=[]
for c in cells:
    x,y=a[c],b[c]
    V.append([c,f3(x['geometry']['mean_acc']),f3(x['geometry_vlm']['mean_acc']),f"{x['geometry_vlm']['mean_acc']-x['geometry']['mean_acc']:+.4f}",
      f3(y['geometry']['mean_acc']),f3(y['geometry_vlm']['mean_acc']),f"{y['geometry_vlm']['mean_acc']-y['geometry']['mean_acc']:+.4f}",
      f"{100*(y['geometry_vlm']['mean_acc']-y['geometry']['mean_acc'])/(y['fair_ceiling']['mean_acc']-y['geometry']['mean_acc']):.0f}%"])
V=tab(['Cell','geometry (10,329 rows)','+VLM','gain','geometry (25,036 rows)','+VLM','gain','Share of gap to ceiling closed by VLM (25,036)'],V)
open('research/2026-11-19_learned_selector/analysis/_frag.json','w').write(json.dumps(dict(H=H,G=G,C=C,HBm=hb('test/mid'),HBh=hb('test/high'),FAM=fam('test/mid'),FAMh=fam('test/high'),FL=FL,K=K,V=V)))
print(FL)
