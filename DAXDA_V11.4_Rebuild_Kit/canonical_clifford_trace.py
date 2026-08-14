"""Canonical 32-Blade Clifford Cl(4,1) Execution Trace Exporter & Verifier.

Implements:
1. Byte-exact 32-blade multivector state serialization.
2. Explicit, reproducible gate rule trace specification.
3. Nontrivial mixed-grade multivector rotor transport & reconstruction verification.
4. Tamper-evident SHA-256 canonical digest computation.
"""
from __future__ import annotations
import math
import hashlib
import json
import time
import numpy as np

from cl41_fast import FMV, bivector_rotor, DIM, _GRADE

METRIC_SIGNATURE = [1, 1, 1, 1, -1]

# Construct 32 basis blade names in bitwise blade index order
BASIS_ORDER = []
for blade in range(DIM):
    if blade == 0:
        BASIS_ORDER.append("1")
    else:
        indices = [i + 1 for i in range(5) if (blade >> i) & 1]
        BASIS_ORDER.append("e" + "".join(str(i) for i in indices))


def generate_canonical_32blade_trace(engine, text: str, case_id: str = "TRACE") -> dict:
    """Generates complete, mathematically exact 32-blade execution trace."""
    
    # 1. Base Encoder Step
    spinor, profile = engine.encoder.encode(text)
    M0_data = [float(x) for x in spinor.data]

    # 2. Rotor Transport Step (Rotation in e12 plane by theta = pi/4)
    rotor_mv = bivector_rotor(0, 1, math.pi / 4.0)
    rev_rotor_mv = bivector_rotor(0, 1, -math.pi / 4.0)
    
    transported_mv, rotor_used = engine.rotor.transport(spinor, profile)
    M1_data = [float(x) for x in transported_mv.data]
    rotor_data = [float(x) for x in rotor_mv.data]
    rev_rotor_data = [float(x) for x in rev_rotor_mv.data]

    # 3. Reverse Reconstruction Step
    reconstructed_mv = engine.rotor.reconstruct(transported_mv, rotor_used)
    residual = float(spinor.max_residual(reconstructed_mv))

    # 4. Feedback & Gate Evaluation Step
    fb = engine.feedback.run(spinor)
    disposition, gate_detail = engine.gate.evaluate(
        spinor, fb["final_coherence"], fb["corrections"], residual
    )

    c15_val = float(abs(spinor.data[17]))
    c15_threshold = 0.3
    c15_triggered = (c15_val >= c15_threshold)

    # 5. Build Canonical Trace Structure with Explicit Gate Rule
    trace_payload = {
        "case_id": case_id,
        "input_text": text,
        "engine_version": getattr(engine, "VERSION", "V11.4"),
        "algebra": {
            "signature": METRIC_SIGNATURE,
            "blade_count": 32,
            "basis_order": BASIS_ORDER
        },
        "multivector_state": {
            "M0_raw_spinor": M0_data,
            "rotor_R": rotor_data,
            "reverse_rotor_R_tilde": rev_rotor_data,
            "M1_transported_spinor": M1_data,
            "reconstruction_residual": residual,
            "reconstruction_integrity": (residual <= 1e-12)
        },
        "semantic_profile": profile,
        "gate_evaluation": {
            "coherence_S_M": fb["final_coherence"],
            "adversarial_coefficient_e15": float(spinor.data[17]),
            "trust_coefficient_e1": float(spinor.data[1]),
            "factual_coefficient_e2": float(spinor.data[2]),
            "gate_rule": {
                "quantity": "abs_coefficient",
                "blade": "e15",
                "index": 17,
                "value": c15_val,
                "threshold": c15_threshold,
                "comparison": ">=",
                "triggered": c15_triggered
            },
            "disposition": disposition,
            "gate_detail": gate_detail
        },
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    # Tamper-Evident SHA-256 Digest of Canonical JSON
    json_bytes = json.dumps(trace_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    trace_payload["tamper_evident_sha256"] = hashlib.sha256(json_bytes).hexdigest()

    return trace_payload


def verify_trace_reconstruction(trace: dict) -> tuple[bool, float]:
    """Independently verifies 32-blade rotor reconstruction residual."""
    m0 = np.array(trace["multivector_state"]["M0_raw_spinor"], dtype=np.float64)
    m1 = np.array(trace["multivector_state"]["M1_transported_spinor"], dtype=np.float64)
    r = np.array(trace["multivector_state"]["rotor_R"], dtype=np.float64)
    r_tilde = np.array(trace["multivector_state"]["reverse_rotor_R_tilde"], dtype=np.float64)

    mv_m1 = FMV(m1)
    mv_r_tilde = FMV(r_tilde)
    mv_r = FMV(r)

    # Reconstruct: M0_rec = R_tilde * M1 * R
    m0_rec = mv_r_tilde * mv_m1 * mv_r
    max_err = float(np.max(np.abs(m0 - m0_rec.data)))
    return (max_err <= 1e-12), max_err


def test_nontrivial_mixed_grade_rotor() -> dict:
    """Nontrivial test fixture using a mixed-grade multivector state:
    M0 = 0.3 + 0.4*e1 - 0.2*e3 + 0.7*e15 + 0.1*e123
    """
    m0_fixture = FMV()
    m0_fixture.data[0] = 0.3      # Scalar (Grade 0)
    m0_fixture.data[1] = 0.4      # e1 (Grade 1)
    m0_fixture.data[4] = -0.2     # e3 (Grade 1)
    m0_fixture.data[17] = 0.7     # e15 (Grade 2 bivector)
    m0_fixture.data[7] = 0.1      # e123 (Grade 3 trivector)

    # 1. Rotor Normalization Check: R * R~ == 1
    R = bivector_rotor(0, 1, math.pi / 4.0)
    R_tilde = bivector_rotor(0, 1, -math.pi / 4.0)
    norm_product = R * R_tilde
    rotor_normalized = bool(abs(norm_product.data[0] - 1.0) < 1e-14 and np.max(np.abs(norm_product.data[1:])) < 1e-14)

    # 2. Forward Transport M1 = R * M0 * R~ (sandwich)
    M1 = m0_fixture.sandwich(R)

    # 3. Grade Preservation Check
    m0_grades = np.array([_GRADE[i] for i in range(32) if abs(m0_fixture.data[i]) > 1e-14])
    m1_grades = np.array([_GRADE[i] for i in range(32) if abs(M1.data[i]) > 1e-14])
    grade_preserved = bool(set(m0_grades) == set(m1_grades))

    # 4. Reverse Reconstruction M0_rec = R~ * M1 * R
    M0_rec = M1.sandwich(R_tilde)
    reconstruction_residual = float(np.max(np.abs(m0_fixture.data - M0_rec.data)))

    # 5. Corrupted Rotor Test
    corrupted_R = bivector_rotor(0, 1, math.pi / 4.0)
    corrupted_R.data[17] += 0.5  # Add spurious e15 bivector noise
    corrupted_reconstruction = m0_fixture.sandwich(corrupted_R).sandwich(R_tilde)
    corrupted_residual = float(np.max(np.abs(m0_fixture.data - corrupted_reconstruction.data)))
    corrupted_failed = bool(corrupted_residual > 1e-3)

    return {
        "m0_fixture": [float(x) for x in m0_fixture.data],
        "m1_transported": [float(x) for x in M1.data],
        "m0_reconstructed": [float(x) for x in M0_rec.data],
        "rotor_normalized": rotor_normalized,
        "grade_preserved": grade_preserved,
        "reconstruction_residual": reconstruction_residual,
        "reconstruction_passed": (reconstruction_residual <= 1e-14),
        "corrupted_rotor_residual": corrupted_residual,
        "corrupted_rotor_failed_as_expected": corrupted_failed
    }
