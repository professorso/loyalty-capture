"""One offline reproduction command. Run from any working directory."""
from pathlib import Path
import hashlib, json, math, runpy, sys
ROOT=Path(__file__).resolve().parent
# The reproduction entry point deliberately forbids network connections.
def offline(event,args):
    if event in {'socket.connect','socket.getaddrinfo'}:
        raise RuntimeError('Offline reproduction blocked network operation: '+event)
sys.addaudithook(offline)
for line in (ROOT/'MANIFEST.sha256').read_text().splitlines():
    digest, name=line.split('  ',1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Checksum mismatch: '+name
(ROOT/'results').mkdir(exist_ok=True)
for script in ['data_checks.py','estimates.py']:
    runpy.run_path(str(ROOT/'analysis'/script),run_name='__main__')
checked=0
def compare(actual,expected,path):
    global checked
    if isinstance(expected,dict):
        assert set(actual)==set(expected), path+': keys differ'
        for k,v in expected.items(): compare(actual[k],v,path+'/'+k)
    elif isinstance(expected,list):
        assert len(actual)==len(expected), path+': length differs'
        for i,(a,b) in enumerate(zip(actual,expected)): compare(a,b,path+'/'+str(i))
    elif isinstance(expected,(int,float)) and not isinstance(expected,bool):
        assert math.isclose(actual,expected,rel_tol=0,abs_tol=1e-12), (path,actual,expected)
        checked+=1
    else: assert actual==expected, (path,actual,expected)
for f in sorted((ROOT/'expected').rglob('*.json')):
    target=ROOT/'results'/f.relative_to(ROOT/'expected')
    compare(json.loads(target.read_text()),json.loads(f.read_text()),str(f.relative_to(ROOT)))
report={'passed':True,'numeric_reference_values_checked':checked,'absolute_tolerance':1e-12,'network':'Python network connections blocked by audit hook; no API calls in analysis.'}
(ROOT/'results/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
