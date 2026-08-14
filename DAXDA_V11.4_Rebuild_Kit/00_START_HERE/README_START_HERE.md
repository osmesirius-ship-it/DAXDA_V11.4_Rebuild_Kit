# DAXDA V11.4 Independent Rebuild Kit

This packet is for **three independent reviewers** to rebuild and verify the frozen DAXDA V11.4 candidate.

## Target architecture

1. `semantic_encoder.py` — active classifier
2. `geometric_transport.py` — reversible audit transport
3. `authority_gate.py` — immutable gate logic
4. `daxda_engine_v11_4.py` — orchestration
5. `cl20.py` — Clifford support

Core invariant:

`G(M0) == G(M0_hat)`

A mismatch must halt closed as `TRANSPORT_DECISION_DIVERGENCE`.

## Limitation

The exact frozen V11.4 engine files were not supplied in this chat. This package therefore provides the reproducibility protocol, file slots, hash tools, reviewer forms, benchmark adapter, and reporting templates. Replace the marked placeholders with the exact frozen files before calling the result a rebuild.

## What counts as a successful rebuild

- Archive and file hashes verified before execution
- Clean environment used
- Locked dependencies installed without substitution
- Frozen preflight reproduced
- Local reconstruction residuals remain below tolerance
- Direct and reconstructed gate decisions match
- NaN, infinity, calibration failure, and simulated-schema cases fail closed
- Three deterministic repetitions agree
- Deviations and failures remain in the signed report
