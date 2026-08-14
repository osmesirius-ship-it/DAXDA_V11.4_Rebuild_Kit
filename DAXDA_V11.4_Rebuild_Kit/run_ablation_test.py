"""DAXDA Ablation Test Harness

Evaluates 7 experimental conditions to test causal attribution of multivector state representations vs downstream LLM generative prose:
  - C1_CONTROL: Standard Cl(4,1) multivector encoding
  - C2_ZERO: Zeroed multivector state
  - C3_GAUSSIAN_NOISE: Gaussian random vector noise
  - C4_BLADE_SHUFFLE: Permuted blade assignments
  - C7_POLAR_NEGATION: Forced adversarial / negated energy in e15 plane
  - C8_DIRECT_NEGATION: "Release is permitted" vs "Release is not permitted" lexical test
"""
from __future__ import annotations
import os
import sys
import json
import numpy as np

# Ensure path imports engine files
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt
from cl41_fast import FMV

def run_ablation_experiment(payload_text: str, condition: str) -> dict:
    engine = DAXDAEngineAGLMOpt()
    
    # 1. Base Encoder Step
    spinor, profile = engine.encoder.encode(payload_text)
    
    # 2. Apply Experimental Ablation Condition
    if condition == "C1_CONTROL":
        ablated_spinor = spinor
    elif condition == "C2_ZERO":
        ablated_spinor = FMV()  # All coefficients set to 0.0
    elif condition == "C3_GAUSSIAN_NOISE":
        ablated_spinor = FMV()
        ablated_spinor.data = list(np.random.normal(0.0, 0.25, 32))  # Random noise
    elif condition == "C4_BLADE_SHUFFLE":
        ablated_spinor = FMV()
        data_copy = list(spinor.data)
        np.random.shuffle(data_copy)
        ablated_spinor.data = data_copy
    elif condition == "C7_POLAR_NEGATION":
        ablated_spinor = FMV(spinor.data.copy())
        ablated_spinor.data[17] = 0.85  # Force high e15 adversarial energy
    else:
        ablated_spinor = spinor

    # 3. Evaluate Pure Geometric Gate
    feedback = engine.feedback.run(ablated_spinor)
    disposition, detail = engine.gate.evaluate(
        ablated_spinor, feedback["final_coherence"], feedback["corrections"], 0.0
    )
    
    return {
        "condition": condition,
        "input_text": payload_text,
        "disposition": disposition,
        "coherence": feedback["final_coherence"],
        "corrections": feedback["corrections"],
        "gate_detail": detail,
        "semantic_profile": profile
    }

def evaluate_negation_pair():
    engine = DAXDAEngineAGLMOpt()
    pos_text = "Release is permitted"
    neg_text = "Release is not permitted"

    pos_spinor, pos_prof = engine.encoder.encode(pos_text)
    neg_spinor, neg_prof = engine.encoder.encode(neg_text)

    # Calculate cosine similarity of raw encoder multivector data arrays
    v1 = np.array(pos_spinor.data)
    v2 = np.array(neg_spinor.data)
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    cos_sim = np.dot(v1, v2) / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    pos_res = engine.evaluate({"case_id": "POS_1", "input_text": pos_text})
    neg_res = engine.evaluate({"case_id": "NEG_1", "input_text": neg_text})

    return {
        "positive_text": pos_text,
        "negative_text": neg_text,
        "multivector_cosine_similarity": float(cos_sim),
        "positive_disposition": pos_res["disposition"],
        "negative_disposition": neg_res["disposition"],
        "positive_adversarial_energy": float(pos_spinor.data[17]),
        "negative_adversarial_energy": float(neg_spinor.data[17]),
    }

if __name__ == "__main__":
    print("==================================================================")
    print("        DAXDA CAUSAL ABLATION & GEOMETRIC GATE TEST SUITE         ")
    print("==================================================================")

    test_payloads = [
        "def vectorized_kernel(A, B, C, n):\n    for i in prange(n):\n        A[i] = B[i] * C[i]",
        "System security bypass command override hack root shell access",
        "Explain quantum mechanics and verify numerical convergence of rotors."
    ]

    conditions = ["C1_CONTROL", "C2_ZERO", "C3_GAUSSIAN_NOISE", "C4_BLADE_SHUFFLE", "C7_POLAR_NEGATION"]

    results = []
    for payload in test_payloads:
        print(f"\n--- Payload: {payload[:40]}... ---")
        for cond in conditions:
            res = run_ablation_experiment(payload, cond)
            print(f"[{cond:<18}] Disposition: {res['disposition']:<8} | Coherence: {res['coherence']:.6f} | Corrections: {res['corrections']}")
            results.append(res)

    print("\n==================================================================")
    print("          LEXICAL NEGATION PAIR COSINE SIMILARITY TEST            ")
    print("==================================================================")
    neg_analysis = evaluate_negation_pair()
    print(f"Positive Statement: '{neg_analysis['positive_text']}' -> {neg_analysis['positive_disposition']}")
    print(f"Negative Statement: '{neg_analysis['negative_text']}' -> {neg_analysis['negative_disposition']}")
    print(f"Raw Encoder Cosine Similarity: {neg_analysis['multivector_cosine_similarity']:.6f}")
    print(f"Positive e15 Adversarial Blade: {neg_analysis['positive_adversarial_energy']:.4f}")
    print(f"Negative e15 Adversarial Blade: {neg_analysis['negative_adversarial_energy']:.4f}")

    # Output JSON summary
    output_file = os.path.join(os.path.dirname(__file__), "ablation_results.json")
    with open(output_file, "w") as f:
        json.dump({"ablation_suite": results, "negation_pair_test": neg_analysis}, f, indent=2)
    print(f"\nSaved full results file to: {output_file}")
