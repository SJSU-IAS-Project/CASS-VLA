import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open('out/v3_eval/triggers.json'))['results']
O='research/2026-11-19_learned_selector/analysis/'
COL={'plandiscrim':'#2a78d6','candidate_only':'#eb6834','scene_only':'#1baf7a','uncertainty_margin':'#eda100','ego_speed':'#e87ba4','random':'#898781'}
LAB={'plandiscrim':'plandiscrim','candidate_only':'candidate-only','scene_only':'scene-only','uncertainty_margin':'ranker margin','ego_speed':'ego speed','random':'random'}
ink,sec,grid='#0b0b0b','#52514e','#e1e0d9'
def style(ax):
    ax.set_facecolor('#fcfcfb')
    for s in('top','right'): ax.spines[s].set_visible(False)
    for s in('left','bottom'): ax.spines[s].set_color('#c3c2b7')
    ax.grid(color=grid,lw=.6); ax.set_axisbelow(True); ax.tick_params(colors=sec,labelsize=9)
B=np.arange(21)*0.05
fig,axs=plt.subplots(1,2,figsize=(11,4.6),facecolor='#fcfcfb')
for ax,c in zip(axs,('test/mid','test/high')):
    style(ax)
    for p in COL:
        if p=='random':
            bb=d[c][p]['by_budget']; ax.plot([float(b) for b in bb],[v['acc'] for v in bb.values()],'o--',color=COL[p],ms=5,lw=1.2,label=LAB[p]+' (4 points)')
        else:
            ax.plot(B,d[c][p]['curve'],color=COL[p],lw=2.4 if p=='plandiscrim' else 1.6,label=LAB[p])
    ax.axhline(d[c]['fair_ceiling']['mean_acc'],color=ink,lw=.8,ls=':'); ax.text(0.72,d[c]['fair_ceiling']['mean_acc']+.003,'fair ceiling, mean over budgets',fontsize=8,color=sec)
    ax.set_title(c+' noise'.replace('/',', ',1) if False else f'{c.split("/")[0]} split, {c.split("/")[1]} noise',color=ink,fontsize=11,loc='left')
    ax.set_xlabel('call budget (calls per decision, 0 to 1)',color=sec); ax.set_ylabel('top-1 accuracy',color=sec)
axs[0].legend(frameon=False,fontsize=8,loc='lower right')
fig.tight_layout(); fig.savefig(O+'fig_accuracy_vs_budget.png',dpi=140); plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4.6),facecolor='#fcfcfb',sharey=True)
for ax,c in zip(axs,('test/mid','test/high')):
    style(ax)
    for p in COL:
        bb=d[c][p]['by_budget']; xs=[bb[b]['harm_rate'] for b in bb]; ys=[bb[b]['benefit_captured'] for b in bb]
        ax.plot(xs,ys,'-',color=COL[p],lw=1,alpha=.6); ax.scatter(xs,ys,s=[25,40,60,90],color=COL[p],edgecolor='#fcfcfb',lw=1.2,label=LAB[p],zorder=3)
    ax.set_title(f'{c.split("/")[0]} split, {c.split("/")[1]} noise (dot size grows with budget 0.1, 0.2, 0.3, 0.5)',color=ink,fontsize=10,loc='left')
    ax.set_xlabel('harm rate (share of calls with negative expected gain)',color=sec)
axs[0].set_ylabel('benefit captured (share of best total expected gain)',color=sec)
axs[0].legend(frameon=False,fontsize=8,loc='upper right')
fig.tight_layout(); fig.savefig(O+'fig_harm_vs_benefit.png',dpi=140); plt.close(fig)
