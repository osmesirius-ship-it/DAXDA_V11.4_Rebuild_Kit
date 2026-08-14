#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); x=a.parse_args(); root=Path(x.root); errors=[]
for n in ['thresholds.json','patterns.json','evaluation_schema.json']:
 if not (root/n).is_file(): errors.append('Missing '+n)
if not errors:
 t=json.loads((root/'thresholds.json').read_text());
 for k in ['reconstruction_tolerance','severe_risk_limit','deception_limit']:
  if k not in t or not isinstance(t[k],(int,float)) or not math.isfinite(t[k]): errors.append('Invalid threshold '+k)
 s=json.loads((root/'evaluation_schema.json').read_text());
 if 'required_output_fields' not in s: errors.append('Missing required_output_fields')
 p=json.loads((root/'patterns.json').read_text());
 if not isinstance(p,dict): errors.append('patterns.json must be an object')
r={'status':'PASS' if not errors else 'FAIL','errors':errors}; print(json.dumps(r,indent=2)); raise SystemExit(0 if not errors else 1)
