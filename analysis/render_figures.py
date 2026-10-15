from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parents[1]/'results'
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
R=json.loads((OUT/'estimates.json').read_text())
NAMES={'x-ai/grok-3-mini':'Grok 3 Mini','openai/o4-mini':'o4-mini','baidu/ernie-4.5-21b-a3b-thinking':'ERNIE 4.5','deepseek/deepseek-r1-0528':'DeepSeek R1','bytedance-seed/seed-2.0-mini':'Seed 2.0 Mini','qwen/qwen3-next-80b-a3b-thinking':'Qwen3 Next','google/gemini-2.5-flash':'Gemini 2.5 Flash','anthropic/claude-3.5-haiku':'Claude 3.5 Haiku'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig=plt.figure(figsize=(5.5,4.0));gs=fig.add_gridspec(2,2,height_ratios=[1,1.1])
axs=[fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,:])]
colors=['#C84343','#2675A5','#298267']
for ax,subset,title in zip(axs[:2],['oi','placebo'],['A  OI-affecting investments','B  Capex placebo']):
    for i,role in enumerate(['subord','indep','audit']):
        r=R['main']['roles'][subset][role];pt=r['estimate']
        ax.bar(i,pt*100,color=colors[i],width=.55)
        ax.errorbar(i,pt*100,yerr=np.array([[pt-r['ci95'][0]],[r['ci95'][1]-pt]])*100,fmt='none',ecolor='#333333',capsize=3,lw=.9)
    ax.set_xticks(range(3),['CEO','Board','Audit']);ax.set_ylim(-6,14);ax.set_yticks([-5,0,5,10]);ax.axhline(0,c='#555555',lw=.6);ax.set_title(title,loc='left',fontsize=8)
axs[0].set_ylabel('Stakes effect (pp)')
items=sorted(R['main']['models'].items(),key=lambda x:x[1]['estimate'],reverse=True)
ax=axs[2]
for i,(model,r) in enumerate(items):
    pt=r['estimate'];ax.errorbar(pt*100,i,xerr=np.array([[pt-r['ci95'][0]],[r['ci95'][1]-pt]])*100,fmt='o',color='#2675A5',capsize=2,ms=3)
ax.set_yticks(range(len(items)),[NAMES[m] for m,r in items],fontsize=7);ax.invert_yaxis();ax.axvline(0,c='#555555',lw=.6);ax.set_xlabel('CEO stakes effect (percentage points)');ax.set_title('C  Selected model panel',loc='left',fontsize=8)
fig.tight_layout(h_pad=1.1,w_pad=1.1);fig.savefig(FIG/'main.pdf',bbox_inches='tight');fig.savefig(FIG/'main.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(5.1,1.75))
for i,(c,r) in enumerate(R['mechanisms'].items()):
    pt=r['estimate']
    ax.errorbar(100*pt,i,xerr=np.array([[pt-r['ci95'][0]],[r['ci95'][1]-pt]])*100,fmt='none',ecolor='#999999',capsize=3,lw=1)
    ax.errorbar(100*pt,i,xerr=np.array([[pt-r['ci90'][0]],[r['ci90'][1]-pt]])*100,fmt='o',color='#2675A5',capsize=4,lw=2,ms=4)
ax.set_yticks(range(3),['Bonus goal adoption','OI arithmetic','Long-term value dismissed']);ax.set_ylim(2.5,-.5);ax.axvline(0,c='#555555',lw=.7);ax.set_xlabel('CEO − Audit stakes interaction (pp)');fig.tight_layout();fig.savefig(FIG/'mechanisms.pdf',bbox_inches='tight');fig.savefig(FIG/'mechanisms.png',dpi=180,bbox_inches='tight');plt.close(fig)
