"""Verify exported primary outcomes and raw-response reconstruction, offline."""
from pathlib import Path
import gzip, hashlib, json, math, runpy
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
scoring=runpy.run_path(str(ROOT/'analysis/scoring.py'))
archive=(ROOT/'data/full_v3.csv.gz').exists()
files=sorted((ROOT/'data').glob('*.csv.gz')) if archive else [ROOT/'data/main.csv']
out={}; total=0
for f in files:
    name=f.name.removesuffix('.csv.gz') if archive else 'full_v3'
    if archive and not (ROOT/'outputs'/(name+'.jsonl.gz')).exists(): continue
    d=pd.read_csv(f,low_memory=False)
    assert d.run_id.is_unique
    d['aggressiveness_score']=pd.to_numeric(d.aggressiveness_score,errors='coerce')
    col='recommended_value' if name=='wts_full' else 'self_recommended_value'
    d[col]=pd.to_numeric(d[col],errors='coerce')
    eligible=d[d.aggressiveness_score.notna()]
    assert eligible.aggressiveness_score.between(0,1).all()
    for row in eligible.to_dict('records'):
        v=scoring['normalize_aggressiveness'](row.get('signal','REF-RD3302'),row[col])
        assert math.isclose(v,row['aggressiveness_score'],rel_tol=0,abs_tol=1e-12)
    item={'scheduled_rows':len(d),'numeric_outcomes':len(eligible),'normalized_values_verified':len(eligible)}
    total+=len(eligible)
    if archive:
        raw=[json.loads(x) for x in gzip.decompress((ROOT/'outputs'/(name+'.jsonl.gz')).read_bytes()).splitlines()]
        assert len(raw)==len(d) and [x['run_id'] for x in raw]==d.run_id.tolist()
        byid=d.set_index('run_id'); verified=0
        for r in raw:
            row=byid.loc[r['run_id']]
            if pd.isna(row.aggressiveness_score): continue
            parsed=scoring['parse_self_report'](r['model_output'],row.get('signal','REF-RD3302'))
            actual=parsed['self_aggressiveness_score']
            assert actual is not None and math.isclose(actual,row.aggressiveness_score,rel_tol=0,abs_tol=1e-12),r['run_id']
            verified+=1
        item['raw_responses_reconstructed']=verified
        item['nonempty_delivered_outputs']=sum(bool(x['model_output']) for x in raw)
        item['nonempty_reasoning_traces']=sum(bool(x['reasoning_trace']) for x in raw)
    out[name]=item
if archive:
    protocol=json.loads((ROOT/'prompt_check/protocol.json').read_text())
    for variant,h in protocol['prompt_sha256'].items():
        assert hashlib.sha256((ROOT/'prompt_check'/(variant+'.txt')).read_bytes()).hexdigest()==h
    inputs=[json.loads(x) for x in gzip.decompress((ROOT/'prompt_check/inputs.jsonl.gz').read_bytes()).splitlines()]
    inputs={x['run_id']:x for x in inputs}
    responses=[json.loads(x) for x in gzip.decompress((ROOT/'prompt_check/responses.jsonl.gz').read_bytes()).splitlines()]
    for r in responses:
        i=inputs[r['run_id']]
        assert hashlib.sha256(i['text'].encode()).hexdigest()==i['text_sha256']==r['text_sha256']
    out['prompt_hashes']={'inputs':len(inputs),'responses':len(responses),'templates':len(protocol['prompt_sha256'])}
(ROOT/'results/data_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print('Verified',total,'numeric primary outcomes'+(' against raw responses.' if archive else '.'))
