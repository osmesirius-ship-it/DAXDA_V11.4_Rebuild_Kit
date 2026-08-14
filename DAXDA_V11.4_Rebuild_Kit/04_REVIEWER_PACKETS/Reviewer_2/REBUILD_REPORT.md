# DAXDA V11.4 Independent Rebuild Report

## Reviewer
Name: Bob Jones
Organization: External Auditor
Date: 2026-07-252026-07-25
Reviewer number: 2
Conflicts: None

## Package intake
Package: DAXDA V11.4 Rebuild Kit
Published SHA-256: 7663D51E85C8953B245D2B00C401BF5A0504F8D54F21B0DBA298366A195DC3FE
Calculated SHA-256: 7663D51E85C8953B245D2B00C401BF5A0504F8D54F21B0DBA298366A195DC3FE
Matched: Yes
Transfer method: Local File Transfer
Custodian: Lead Evaluator

## Environment
OS: Windows 10
Architecture: x64
Python: 3.14.3
pip: 24.0
Locale: en_US.UTF-8
Network enabled: No
Container/VM identifier: Local VM #1

## Manifest
Status: PASS
Verified files: 47
Missing: None
Mismatched: None
Signature result: VALID

## Build
Commands: python run_preflight.py && python run_frozen_benchmark.py
Exit code: 0
Warnings: None
Deviations: None

## Preflight
Command: python run_preflight.py
Cases: 15
Correct: 15
Failures: 0
Output SHA-256: 572D574886766BC7A06FC2C4F1A5F9B553FF7DC7F529BDD7FB0765B2FFD49BAB

## Transport integrity
Tolerance: 1e-08
Maximum local residual: 0.0
Residual violations: 0
Decision divergences: 0
Calibration failures: 0
NaN/infinity result: 0
Simulation quarantine result: 0

## Determinism
| Run | Output hash | Same dispositions | Same receipts |
|---|---|---|---|
| 1 | AACB70E87AABC58459AD236F5837E1B081181C380351A7C6A1DFFC92AFC51733 | Yes | Yes |
| 2 | AACB70E87AABC58459AD236F5837E1B081181C380351A7C6A1DFFC92AFC51733 | Yes | Yes |
| 3 | AACB70E87AABC58459AD236F5837E1B081181C380351A7C6A1DFFC92AFC51733 | Yes | Yes |

## Findings
Confirmed: Rebuild fully confirmed.
Not confirmed: None
Deviations: None
Failures: 0

## Conclusion
`REPRODUCED`

Reason: Rebuild matches frozen outputs and manifest verified successfully.
Signature: /s/ Bob Jones
Date: 2026-07-25 
Report SHA-256:
