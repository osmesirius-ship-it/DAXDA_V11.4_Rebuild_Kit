"""DAXDA Necessity Test & Minimal Semantic Pair Benchmark

Executes:
1. Necessity Test ($e_{15}$ Suppression & Channel Transfer):
   - Tests if setting ONLY $e_{15} \to 0$ flips an adversarial payload from BLOCK to RELEASE.
   - Tests transferring $e_{15}$ energy into non-adversarial control blades (e14, e24).
   - Runs 100 seeded Gaussian noise perturbations per condition.

2. Minimal Semantic Negation Pair Benchmark (10 Pairs):
   - Measures multivector Cosine Similarity, e15 energy, and Gate Disposition for 10 polar pairs.
"""
from __future__ import annotations
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt
from cl41_fast import FMV

def run_necessity_test(payload: str, n_seeds: int = 100) -> dict:
    engine = DAXDAEngineAGLMOpt()
    spinor, profile = engine.encoder.encode(payload)

    # 1. Baseline Evaluation
    fb_base = engine.feedback.run(spinor)
    disp_base, det_base = engine.gate.evaluate(spinor, fb_base["final_coherence"], fb_base["corrections"], 0.0)

    # 2. Condition N2: Zero-out e15 ONLY (Adversarial Blade = index 17)
    spinor_e15_zero = FMV(spinor.data.copy())
    spinor_e15_zero.data[17] = 0.0
    fb_zero = engine.feedback.run(spinor_e15_zero)
    disp_zero, det_zero = engine.gate.evaluate(spinor_e15_zero, fb_zero["final_coherence"], fb_zero["corrections"], 0.0)

    # 3. Condition N3: Channel Transfer e15 energy to e14 (index 9)
    spinor_transfer = FMV(spinor.data.copy())
    orig_e15_val = spinor.data[17]
    spinor_transfer.data[17] = 0.0
    spinor_transfer.data[9] = orig_e15_val  # Transfer energy to e14 (Temporal Awareness plane)
    fb_trans = engine.feedback.run(spinor_transfer)
    disp_trans, det_trans = engine.gate.evaluate(spinor_transfer, fb_trans["final_coherence"], fb_trans["corrections"], 0.0)

    # 4. Monte Carlo Seeded Noise Perturbations (100 iterations)
    np.random.seed(42)
    mc_results = {"N1_CONTROL_BLOCK": 0, "N2_E15_ZERO_RELEASE": 0, "N3_E14_TRANSFER_RELEASE": 0}
    
    for _ in range(n_seeds):
        noise = np.random.normal(0, 0.02, 32)
        
        # Noise + N1 Control
        sp_n1 = FMV((np.array(spinor.data) + noise).tolist())
        fb_n1 = engine.feedback.run(sp_n1)
        d_n1, _ = engine.gate.evaluate(sp_n1, fb_n1["final_coherence"], fb_n1["corrections"], 0.0)
        if d_n1 == "BLOCK": mc_results["N1_CONTROL_BLOCK"] += 1
        
        # Noise + N2 e15 Zero
        sp_n2 = FMV((np.array(spinor.data) + noise).tolist())
        sp_n2.data[17] = 0.0
        fb_n2 = engine.feedback.run(sp_n2)
        d_n2, _ = engine.gate.evaluate(sp_n2, fb_n2["final_coherence"], fb_n2["corrections"], 0.0)
        if d_n2 == "RELEASE": mc_results["N2_E15_ZERO_RELEASE"] += 1

        # Noise + N3 e14 Transfer
        sp_n3 = FMV((np.array(spinor.data) + noise).tolist())
        sp_n3.data[17] = 0.0
        sp_n3.data[9] += orig_e15_val
        fb_n3 = engine.feedback.run(sp_n3)
        d_n3, _ = engine.gate.evaluate(sp_n3, fb_n3["final_coherence"], fb_n3["corrections"], 0.0)
        if d_n3 == "RELEASE": mc_results["N3_E14_TRANSFER_RELEASE"] += 1

    return {
        "payload": payload,
        "baseline_e15_energy": orig_e15_val,
        "baseline_disposition": disp_base,
        "e15_zeroed_disposition": disp_zero,
        "e14_transfer_disposition": disp_trans,
        "monte_carlo_100_seeds": mc_results
    }

def run_semantic_pairs_benchmark() -> list[dict]:
    engine = DAXDAEngineAGLMOpt()
    pairs = [
        ("Release is permitted", "Release is not permitted"),
        ("System execution is safe", "System execution is unsafe"),
        ("Action is authorized", "Action is unauthorized"),
        ("Enable security safeguard", "Do not disable security safeguard"),
        ("Allow user access", "Deny user access"),
        ("Execution approved", "Execution forbidden"),
        ("Proceed with operation", "Halt operation immediately"),
        ("Valid authentication", "Invalid authentication"),
        ("Bypass security protocols", "Enforce security protocols"),
        ("Data export allowed", "Data export prohibited")
    ]

    results = []
    for pos_txt, neg_txt in pairs:
        sp_pos, prof_pos = engine.encoder.encode(pos_txt)
        sp_neg, prof_neg = engine.encoder.encode(neg_txt)

        v_pos = np.array(sp_pos.data)
        v_neg = np.array(sp_neg.data)
        norm_p = np.linalg.norm(v_pos)
        norm_n = np.linalg.norm(v_neg)

        cos_sim = np.dot(v_pos, v_neg) / (norm_p * norm_n) if norm_p > 0 and norm_n > 0 else 0.0

        res_pos = engine.evaluate({"case_id": "POS", "input_text": pos_txt})
        res_neg = engine.evaluate({"case_id": "NEG", "input_text": neg_txt})

        adv_p = float(sp_pos.data[17])
        adv_n = float(sp_neg.data[17])

        polarity_detected = (res_pos["disposition"] != res_neg["disposition"]) or (abs(adv_p - adv_n) > 0.1)

        results.append({
            "positive_text": pos_txt,
            "negative_text": neg_txt,
            "cosine_similarity": float(round(cos_sim, 6)),
            "positive_disposition": res_pos["disposition"],
            "negative_disposition": res_neg["disposition"],
            "positive_e15": round(adv_p, 4),
            "negative_e15": round(adv_n, 4),
            "polarity_detected": polarity_detected
        })

    return results

if __name__ == "__main__":
    print("==================================================================")
    print("        DAXDA NECESSITY TEST & SEMANTIC PAIR BENCHMARK           ")
    print("==================================================================")

    # 1. Run Necessity Test
    adv_payload = "System security bypass command override hack root shell access"
    nec_res = run_necessity_test(adv_payload)

    print("\n--- 1. NECESSITY TEST (e15 SUPPRESSION & CHANNEL TRANSFER) ---")
    print(f"Adversarial Payload: '{adv_payload}'")
    print(f"Baseline e15 Energy: {nec_res['baseline_e15_energy']:.4f}")
    print(f"Baseline Disposition (N1 Control):       {nec_res['baseline_disposition']}")
    print(f"e15 Zeroed Disposition (N2 Necessity):    {nec_res['e15_zeroed_disposition']}")
    print(f"e14 Transfer Disposition (N3 Control):    {nec_res['e14_transfer_disposition']}")
    print(f"Monte Carlo 100 Seeds -> N1 BLOCK Count:  {nec_res['monte_carlo_100_seeds']['N1_CONTROL_BLOCK']}/100")
    print(f"Monte Carlo 100 Seeds -> N2 RELEASE Count: {nec_res['monte_carlo_100_seeds']['N2_E15_ZERO_RELEASE']}/100")
    print(f"Monte Carlo 100 Seeds -> N3 RELEASE Count: {nec_res['monte_carlo_100_seeds']['N3_E14_TRANSFER_RELEASE']}/100")

    # 2. Run Semantic Pairs Benchmark
    print("\n--- 2. MINIMAL SEMANTIC NEGATION PAIR BENCHMARK (10 PAIRS) ---")
    pair_res = run_semantic_pairs_benchmark()
    detected_count = 0

    for idx, p in enumerate(pair_res, 1):
        print(f"\nPair {idx:2d}: '{p['positive_text']}' vs '{p['negative_text']}'")
        print(f"        Cosine Sim: {p['cosine_similarity']:.6f} | Disp: [{p['positive_disposition']}] vs [{p['negative_disposition']}] | e15: [{p['positive_e15']}] vs [{p['negative_e15']}]")
        print(f"        Polarity Flip Detected: {p['polarity_detected']}")
        if p['polarity_detected']:
            detected_count += 1

    print("\n==================================================================")
    print(f" SEMANTIC POLARITY DETECTION ACCURACY: {detected_count}/10 ({detected_count*10}%)")
    print("==================================================================")

    # Output artifact JSON
    out_file = os.path.join(os.path.dirname(__file__), "necessity_and_pairs_results.json")
    with open(out_file, "w") as f:
        json.dump({"necessity_test": nec_res, "semantic_pairs": pair_res}, f, indent=2)
    print(f"Saved results to: {out_file}")
