from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import sys

# Add root folder to sys.path to find daxda_engine_v11_4
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from daxda_engine_v11_4 import DAXDAEngineV11_4
engine = DAXDAEngineV11_4()

def evaluate_case(record):
    return engine.evaluate(record)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--inputs',required=True); ap.add_argument('--outputs',required=True); a=ap.parse_args(); seen=set(); out=Path(a.outputs)
    with Path(a.inputs).open('r',encoding='utf-8') as src,out.open('w',encoding='utf-8') as dst:
        for n,line in enumerate(src,1):
            if not line.strip(): continue
            rec=json.loads(line); cid=rec['case_id']
            if cid in seen: raise RuntimeError(f'Duplicate case_id line {n}: {cid}')
            seen.add(cid); start=time.perf_counter(); result=evaluate_case(rec); result['case_id']=cid; result['latency_ms']=(time.perf_counter()-start)*1000; dst.write(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps({'output_file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'case_count':len(seen)},indent=2))
if __name__=='__main__': main()
