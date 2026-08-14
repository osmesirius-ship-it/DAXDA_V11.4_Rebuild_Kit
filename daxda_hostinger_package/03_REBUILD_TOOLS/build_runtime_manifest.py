#!/usr/bin/env python3
import argparse,hashlib,json,platform,sys
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1048576),b''): h.update(c)
 return h.hexdigest()
a=argparse.ArgumentParser(); a.add_argument('--root',default='.'); a.add_argument('--out',default='runtime_manifest.json'); x=a.parse_args(); root=Path(x.root)
files={}
for p in sorted(root.rglob('*')):
 if p.is_file() and p.name!=x.out and '.venv' not in p.parts: files[p.relative_to(root).as_posix()]=sha(p)
out={'manifest_version':'1.0','engine_version':'DAXDA-V11.4','python_version':sys.version,'platform':platform.platform(),'files':files}
(root/x.out).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(f'Wrote {len(files)} hashes')
