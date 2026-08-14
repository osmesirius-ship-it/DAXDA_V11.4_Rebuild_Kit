#!/usr/bin/env python3
import argparse,json
from pathlib import Path
REQ=['semantic_encoder.py','geometric_transport.py','authority_gate.py','daxda_engine_v11_4.py','cl20.py','thresholds.json','patterns.json','evaluation_schema.json','requirements.lock','runtime_manifest.json']
a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); x=a.parse_args(); root=Path(x.root)
missing=[n for n in REQ if not (root/n).is_file()]
print(json.dumps({'status':'PASS' if not missing else 'FAIL','missing_files':missing},indent=2))
raise SystemExit(0 if not missing else 1)
