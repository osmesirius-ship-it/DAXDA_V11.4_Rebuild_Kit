import hashlib
import os
import datetime

base_dir = r'c:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\DAXDA_V11.4_Rebuild_Kit'
utc_now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

# Complete list of required audit artifacts — NONE MAY BE SKIPPED
required_artifacts = [
    ('daxda_engine_aglm_opt.py', 'Frozen Baseline Engine (V11.4 Baseline)'),
    ('daxda_engine_v11_4_1_candidate.py', 'Quarantined Candidate Engine (V11.4.1-CANDIDATE)'),
    ('daxda_engine_v11_4_2_candidate.py', 'Typed Dependency Engine Candidate (V11.4.2-CANDIDATE)'),
    ('canonical_clifford_trace.py', 'Canonical 32-Blade Multivector Execution Trace Exporter'),
    ('run_end_to_end_trace_test.py', 'Canonical 32-Blade End-to-End Test Suite'),
    ('render_trace_video.py', 'Headless Trace-to-Video MP4 Build Generator'),
    ('run_candidate_benchmark.py', 'Holdout Benchmark Runner'),
    ('internal_holdout_cases.json', 'Decoupled Holdout Input Asset'),
    ('release_gate_policy.json', 'Governance Criteria Specification'),
    ('internal_holdout_results.json', 'Raw Holdout Evidence Ledger'),
    ('run_necessity_and_pairs_test.py', 'Regression Test Runner'),
    ('necessity_and_pairs_results.json', 'Raw Regression Evidence Ledger'),
    ('environment_manifest.json', 'Platform Runtime Specification'),
    ('DAXDA_INTERNAL_NEGATIVE_VALIDATION_AUDIT.md', 'Final Audit Report Document'),
    ('README_REPRODUCIBILITY.md', 'Reproducibility Protocol Specification'),
    ('runtime_manifest.json', 'System Runtime Manifest')
]

manifest_lines = [
    '==================================================================================',
    '            DAXDA V11.4 & V11.4.1-CANDIDATE DETACHED SHA-256 MANIFEST             ',
    '==================================================================================',
    f'Generated At: {utc_now} (Locally Asserted UTC Timestamp)',
    'Scope: DAXDA System Audit & Negative-Validation Record',
    '----------------------------------------------------------------------------------',
    ''
]

print("Scanning required artifacts for strict hash verification...")

for rel_path, desc in required_artifacts:
    full_path = os.path.join(base_dir, rel_path)
    
    # FAIL LOUDLY if any required file is missing!
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"[STRICT MANIFEST ERROR] Required artifact is MISSING: {rel_path} ({desc})")
    
    size = os.path.getsize(full_path)
    with open(full_path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    
    manifest_lines.append(f'File: {rel_path}')
    manifest_lines.append(f'  Role:        {desc}')
    manifest_lines.append(f'  Byte Size:   {size} bytes')
    manifest_lines.append(f'  SHA-256:     {h}')
    manifest_lines.append('')

manifest_content = '\n'.join(manifest_lines)
manifest_path = os.path.join(base_dir, 'SHA256SUMS.txt')

with open(manifest_path, 'w', encoding='utf-8') as f:
    f.write(manifest_content)

print(f"[SUCCESS] Strict manifest generated at: {manifest_path}")
print(f"Total required artifacts verified: {len(required_artifacts)}/{len(required_artifacts)}")
print("\n" + manifest_content)
