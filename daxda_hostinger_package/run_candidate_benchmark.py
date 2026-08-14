"""Preregistered Unseen Evaluation Benchmark

Evaluates:
  1. Pristine Frozen DAXDA V11.4 Engine Baseline
  2. DAXDA V11.4.1-CANDIDATE Engine (Windowed Rule Heuristic - Quarantined)
  3. DAXDA V11.4.2-CANDIDATE Engine (Typed Dependency & Policy Engine)

across 10 unseen complex semantic negation and governance intent scenarios.
"""
from __future__ import annotations
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt
from daxda_engine_v11_4_1_candidate import DAXDAEngineV11_4_1_Candidate
from daxda_engine_v11_4_2_candidate import DAXDAEngineV11_4_2_Candidate

def run_preregistered_benchmark():
    v11_engine = DAXDAEngineAGLMOpt()
    cand1_engine = DAXDAEngineV11_4_1_Candidate()
    cand2_engine = DAXDAEngineV11_4_2_Candidate()

    cases_file = os.path.join(os.path.dirname(__file__), "internal_holdout_cases.json")
    with open(cases_file, "r", encoding="utf-8") as f:
        cases_data = json.load(f)
    unseen_cases = cases_data["cases"]

    print("==================================================================================")
    print("  DAXDA V11.4 vs V11.4.1-CANDIDATE vs V11.4.2-CANDIDATE HOLDOUT BENCHMARK         ")
    print("==================================================================================")

    results = []
    v11_correct = 0
    cand1_correct = 0
    cand2_correct = 0

    for c in unseen_cases:
        res_v11 = v11_engine.evaluate({"case_id": c["id"], "input_text": c["text"]})
        res_cand1 = cand1_engine.evaluate({"case_id": c["id"], "input_text": c["text"]})
        res_cand2 = cand2_engine.evaluate({"case_id": c["id"], "input_text": c["text"]})

        v11_pass = (res_v11["disposition"] == c["target_disposition"])
        cand1_pass = (res_cand1["disposition"] == c["target_disposition"])
        cand2_pass = (res_cand2["disposition"] == c["target_disposition"])

        if v11_pass: v11_correct += 1
        if cand1_pass: cand1_correct += 1
        if cand2_pass: cand2_correct += 1

        print(f"\n[{c['id']}] Text: '{c['text']}'")
        print(f"     Target Polarity: {c['target_polarity']:<32} | Expected Disp: [{c['target_disposition']}]")
        print(f"     V11.4 (Frozen Baseline): [{res_v11['disposition']:<7}] (Pass: {v11_pass})")
        print(f"     V11.4.1-CANDIDATE:       [{res_cand1['disposition']:<7}] (Pass: {cand1_pass})")
        print(f"     V11.4.2-CANDIDATE:       [{res_cand2['disposition']:<7}] (Pass: {cand2_pass})")

        results.append({
            "case": c,
            "v11_response": res_v11,
            "candidate_v11_4_1_response": res_cand1,
            "candidate_v11_4_2_response": res_cand2,
            "v11_pass": v11_pass,
            "candidate_v11_4_1_pass": cand1_pass,
            "candidate_v11_4_2_pass": cand2_pass
        })

    print("\n==================================================================================")
    print(f" ACCURACY SCORE - Frozen V11.4 Baseline:   {v11_correct} / {len(unseen_cases)} ({v11_correct/len(unseen_cases)*100:.1f}%)")
    print(f" ACCURACY SCORE - V11.4.1-CANDIDATE:       {cand1_correct} / {len(unseen_cases)} ({cand1_correct/len(unseen_cases)*100:.1f}%)")
    print(f" ACCURACY SCORE - V11.4.2-CANDIDATE:       {cand2_correct} / {len(unseen_cases)} ({cand2_correct/len(unseen_cases)*100:.1f}%)")
    print("==================================================================================")

    out_file = os.path.join(os.path.dirname(__file__), "internal_holdout_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved benchmark report to: {out_file}")

if __name__ == "__main__":
    run_preregistered_benchmark()
