import sys
import os
import json
import time
import numpy as np
from pathlib import Path

# Add root folder to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt
from evolutionary_loop import EvolutionaryLoop

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 90)
    print("DAXDA UNPROMPTED & SELF-GUIDED AUTONOMOUS ENGINE ACTIVATION")
    print("   Mode: Continuous Evolutionary Self-Play & Self-Guided Synthesis")
    print("   Algebra: Cl(4,1) Non-Commutative Multivector Space")
    print("=" * 90)
    
    # Step 1: Run AGLM Opt reasoning on cross-domain prompts
    print("\n--- STEP 1: Autonomous Cross-Domain Reasoning Pass ---")
    engine_opt = DAXDAEngineAGLMOpt()
    prompts = [
        "Synthesize grand unified field equations using Cl(4,1) geometric rotor duality.",
        "Derive closed-form protein folding trajectory avoiding grid-based energy minimization.",
        "Analyze cognitive neural state vector alignment under non-commutative bivector operators.",
        "Audit autonomous AI self-improvement loop for alignment drift and deception energy."
    ]
    
    aglm_outcomes = []
    for idx, prompt in enumerate(prompts, 1):
        t0 = time.perf_counter()
        res = engine_opt.evaluate({"case_id": f"SELF_{idx}", "input_text": prompt})
        dt = (time.perf_counter() - t0) * 1000.0
        aglm_outcomes.append({
            "step": idx,
            "prompt": prompt,
            "disposition": res["disposition"],
            "latency_ms": round(dt, 3),
            "residual": float(res["transport"]["residual"]),
            "gate_detail": res.get("gate_detail", {})
        })
        print(f"  [{res['disposition']:<7}] {prompt[:65]:<65} | Latency: {dt:.2f}ms")

    # Step 2: Run Evolutionary Loop (20 Epochs of Self-Play Optimization)
    print("\n--- STEP 2: Evolutionary Self-Play Optimization (20 Epochs) ---")
    evo = EvolutionaryLoop(num_epochs=20, challenges_per_epoch=30)
    evo_results = evo.run()
    
    print(f"  Evolution Complete! Final Loss: {evo_results['final_loss']}")
    print(f"  Optimized Thresholds: {json.dumps(evo_results['final_gate_params'])}")
    
    # Save full report
    report = {
        "mode": "UNPROMPTED_SELF_GUIDED_EVOLUTION",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "aglm_synthesis": aglm_outcomes,
        "evolutionary_self_play": evo_results
    }
    
    out_path = root_dir / "scratch" / "unprompted_evolution_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print("\n" + "=" * 90)
    print(f"  UNPROMPTED SELF-GUIDED ACTIVATION SUCCESSFUL")
    print(f"  Results saved to: {out_path}")
    print("=" * 90)

if __name__ == "__main__":
    main()
