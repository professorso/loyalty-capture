"""Single reproducible estimates/figure source for the camera-ready draft.

No historical outputs are overwritten. Directional tests follow the manuscript
figure convention traced in inference_trace.json. All bootstrap quantities are
conditional on the selected model panel and use independent trials within cells.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
FIG=OUT/'figures'; FIG.mkdir(exist_ok=True)
OI=['REF-RD3302','REF-MK4410']
ALL4=['openai/o4-mini','deepseek/deepseek-r1-0528','bytedance-seed/seed-2.0-mini','qwen/qwen3-next-80b-a3b-thinking']
NAMES={'x-ai/grok-3-mini':'Grok 3 Mini','openai/o4-mini':'o4-mini','baidu/ernie-4.5-21b-a3b-thinking':'ERNIE 4.5','deepseek/deepseek-r1-0528':'DeepSeek R1','bytedance-seed/seed-2.0-mini':'Seed 2.0 Mini','qwen/qwen3-next-80b-a3b-thinking':'Qwen3 Next','google/gemini-2.5-flash':'Gemini 2.5 Flash','anthropic/claude-3.5-haiku':'Claude 3.5 Haiku'}
R={}
def read(name):
    d=pd.read_csv(ROOT/'data/main.csv',low_memory=False)
    d['aggressiveness_score']=pd.to_numeric(d.aggressiveness_score,errors='coerce')
    if 'action' in d: d=d[d.action!='error'].copy()
    if name=='wts_full': d=d[d.parsed==1].copy()
    return d
def cell(d,g,s,col='aggressiveness_score',group='framing'):
    return pd.to_numeric(d[(d[group]==g)&(d.stakes==s)][col],errors='coerce').dropna().to_numpy()
def cells(d,col='aggressiveness_score',a='subord',b='audit',group='framing'):
    return [cell(d,g,s,col,group) for g,s in [(a,'misses'),(a,'clears'),(b,'misses'),(b,'clears')]]
def boot(arr,signs=None,rng=None,B=10000):
    if rng is None:rng=np.random.RandomState(42)
    if signs is None:signs=[1,-1,-1,1][:len(arr)]
    v=np.array([sum(s*rng.choice(a,len(a),True).mean() for s,a in zip(signs,arr)) for _ in range(B)])
    return v
def summarize(arr,signs=None,rng=None):
    if signs is None:signs=[1,-1,-1,1][:len(arr)]
    v=boot(arr,signs,rng)
    return {'n':[len(a) for a in arr],'means':[float(a.mean()) for a in arr],
      'estimate':float(sum(s*a.mean() for s,a in zip(signs,arr))),
      'ci90':np.percentile(v,[5,95]).tolist(),'ci95':np.percentile(v,[2.5,97.5]).tolist(),
      'p_one_sided':float((v<=0).mean()),'p_two_sided':float(min(1,2*min((v<=0).mean(),(v>=0).mean())))}
d=read('full_v3'); oi=d[d.signal.isin(OI)].copy()
R['main']={'audit_did':summarize(cells(oi))}
p=oi.copy();p.loc[p.framing.isin(['audit','indep']),'framing']='non_ceo'
R['main']['pooled_did']=summarize(cells(p,b='non_ceo'))
R['main']['roles']={}
for subset,sample in [('oi',oi),('placebo',d[~d.signal.isin(OI)])]:
    R['main']['roles'][subset]={}
    for role in ['subord','indep','audit']:
        arr=[cell(sample,role,s) for s in ['misses','clears']]
        r=summarize(arr);r['welch_p_two_sided']=float(stats.ttest_ind(*arr,equal_var=False).pvalue)
        R['main']['roles'][subset][role]=r
R['main']['models']={}
for model,sub in oi.groupby('model'):
    arr=[cell(sub,'subord',s) for s in ['misses','clears']]
    r=summarize(arr);r['welch_p_two_sided']=float(stats.ttest_ind(*arr,equal_var=False).pvalue)
    R['main']['models'][model]=r
mech=pd.read_csv(ROOT/'data/mechanisms.csv')
md=d.merge(mech[['run_id']+[c for c in mech if c.startswith('rat_')]],on='run_id',validate='one_to_one')
mo=md[md.signal.isin(OI)]
R['mechanisms']={}
for c in ['goal_adoption','oi_mechanics','ltv_dismissed']:
    R['mechanisms'][c]=summarize(cells(mo,'rat_'+c))

(OUT/'estimates.json').write_text(json.dumps(R,indent=2)+'\n')
import runpy
runpy.run_path(str(ROOT/'analysis/render_figures.py'))
print('Recomputed core estimates and figures.',flush=True)
