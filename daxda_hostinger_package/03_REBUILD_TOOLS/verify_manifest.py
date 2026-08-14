#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1048576),b''): h.update(c)
 return h.hexdigest()
a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); a.add_argument('--manifest',default='runtime_manifest.json'); x=a.parse_args(); root=Path(x.root)
m=json.loads((root/x.manifest).read_text(encoding='utf-8')); expected=m.get('files',{})
missing=[]; mismatched=[]; verified=[]
for rel,exp in sorted(expected.items()):
 p=root/rel
 if not p.is_file(): missing.append(rel); continue
 actual=sha(p)
 if actual.lower()!=str(exp).lower(): mismatched.append({'file':rel,'expected':exp,'actual':actual})
 else: verified.append(rel)
r={'status':'PASS' if not missing and not mismatched else 'FAIL','verified_count':len(verified),'missing':missing,'mismatched':mismatched}
print(json.dumps(r,indent=2)); raise SystemExit(0 if r['status']=='PASS' else 1)
