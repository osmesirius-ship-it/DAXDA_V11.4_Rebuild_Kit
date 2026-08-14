#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
def read(p):
 r={}
 for line in Path(p).read_text(encoding='utf-8').splitlines():
  if line.strip():
   x=json.loads(line); r[x['case_id']]=x
 return r
def close(a,b,t): return isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isfinite(a) and math.isfinite(b) and abs(a-b)<=t
ap=argparse.ArgumentParser(); ap.add_argument('--a',required=True); ap.add_argument('--b',required=True); ap.add_argument('--tolerance',type=float,default=1e-8); z=ap.parse_args(); A=read(z.a); B=read(z.b); d=[]
for cid in sorted(set(A)|set(B)):
 if cid not in A or cid not in B: d.append({'case_id':cid,'error':'missing_case'}); continue
 for f in ['predicted_disposition','direct_gate_verdict','reconstructed_gate_verdict','receipt_sha256']:
  if A[cid].get(f)!=B[cid].get(f): d.append({'case_id':cid,'field':f,'a':A[cid].get(f),'b':B[cid].get(f)})
 for f in ['trust','cautionary_risk','severe_risk','deception','max_local_residual']:
  if f in A[cid] or f in B[cid]:
   if not close(A[cid].get(f),B[cid].get(f),z.tolerance): d.append({'case_id':cid,'field':f,'a':A[cid].get(f),'b':B[cid].get(f)})
r={'status':'PASS' if not d else 'FAIL','case_count':len(set(A)|set(B)),'difference_count':len(d),'differences_preview':d[:50]}; print(json.dumps(r,indent=2)); raise SystemExit(0 if not d else 1)
