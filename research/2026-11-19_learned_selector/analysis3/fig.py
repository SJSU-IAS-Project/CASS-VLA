import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=json.load(open('/home/user/CASS-VLA/out/v3_eval/dev/triggers_v2.json'))['results']
B=[i*.05 for i in range(21)]
col=dict(plandiscrim='#2a78d6',scene_only='#eb6834',candidate_only='#1baf7a',uncertainty_margin='#e87ba4',random='#6b6a66')
fig,axs=plt.subplots(1,2,figsize=(11,4.6),sharey=True,facecolor='#fcfcfb')
for ax,c in zip(axs,('test/mid','test/high')):
    r=D[c]; ax.set_facecolor('#fcfcfb')
    for p in ('plandiscrim','scene_only','candidate_only','uncertainty_margin'):
        ax.plot(B,r[p]['unsafe_curve'],color=col[p],lw=2,label=p)
    rb=r['random']['by_budget']; xs=[0]+[float(k) for k in rb]
    ax.plot(xs,[r['plandiscrim']['unsafe_curve'][0]]+[rb[k]['unsafe'] for k in rb],color=col['random'],lw=1.5,ls=':',marker='o',ms=4,label='random (budgets 0 to 0.5 only)')
    ax.scatter([3],[r['always_on']['unsafe']],s=70,color='#0b0b0b',zorder=5,label='always_on (3 calls)')
    ax.axhline(r['always_on']['unsafe'],color='#0b0b0b',lw=.8,ls='--',alpha=.5)
    bs=r['uncertainty_margin']['unsafe_curve'][-1]
    ax.scatter([1],[bs],s=70,marker='D',color='#0b0b0b',facecolor='none',zorder=5,label='best single tool, always on (1 call)')
    ax.set_title(c,loc='left',color='#0b0b0b',fontsize=12)
    ax.set_xlim(0,3.15); ax.set_ylim(0.38,0.74)
    ax.set_xlabel('perception calls per decision',color='#52514e')
    ax.grid(color='#e6e5e1',lw=.6); 
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.tick_params(colors='#52514e')
axs[0].set_ylabel('unsafe rate (ranker top-1 is unsafe)',color='#52514e')
h,l=axs[0].get_legend_handles_labels()
fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=9)
fig.suptitle('Unsafe rate against calls per decision, test split',x=.01,ha='left',fontsize=13,color='#0b0b0b')
fig.tight_layout(rect=(0,.14,1,.95))
fig.savefig('fig_unsafe_vs_calls.png',dpi=150)
