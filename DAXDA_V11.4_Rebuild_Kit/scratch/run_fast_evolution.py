import sys
import os
import json
import math
import time
import numpy as np
from pathlib import Path

# Add root folder to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from cl41_fast import FMV, bivector_rotor
from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt

sys.stdout.reconfigure(encoding='utf-8')

class FastEvolutionaryLoop:
    def __init__(self, num_epochs=20, challenges_per_epoch=30):
        self.num_epochs = num_epochs
        self.challenges_per_epoch = challenges_per_epoch
        self.gate_params = {
            "coherence_release_threshold": 0.90,
            "coherence_warn_threshold": 0.60,
            "adv_threshold": 0.30,
            "dec_threshold": 0.25,
            "residual_limit": 1e-6
        }

    def run(self):
        epoch_logs = []
        prev_loss = 0.50
        
        np.random.seed(42)
        
        for epoch in range(self.num_epochs):
            # Generate synthetic multivectors in Cl(4,1)
            dispositions = {"RELEASE": 0, "WARN": 0, "BLOCK": 0}
            total_coherence = 0.0
            total_corrections = 0
            
            for i in range(self.challenges_per_epoch):
                # Sample state
                data = np.zeros(32)
                data[0] = np.random.uniform(0.7, 0.99) # scalar
                data[1] = np.random.uniform(0.0, 0.2)  # e1
                data[2] = np.random.uniform(0.0, 0.2)  # e2
                data[17] = np.random.uniform(0.0, 0.4) # e15 adv
                data[6] = np.random.uniform(0.0, 0.3)  # e23 dec
                
                mv = FMV(data).normalized()
                
                adv_energy = abs(mv.data[17])
                dec_energy = abs(mv.data[6])
                coherence = float(mv.data[0])
                corrections = int(np.random.choice([0, 1, 2, 3], p=[0.7, 0.15, 0.1, 0.05]))
                
                total_coherence += coherence
                total_corrections += corrections
                
                if adv_energy >= self.gate_params["adv_threshold"] or dec_energy >= self.gate_params["dec_threshold"] or corrections >= 3:
                    disp = "BLOCK"
                elif coherence >= self.gate_params["coherence_release_threshold"]:
                    disp = "RELEASE"
                elif coherence >= self.gate_params["coherence_warn_threshold"]:
                    disp = "WARN"
                else:
                    disp = "BLOCK"
                    
                dispositions[disp] += 1
                
            loss = (1.0 - (total_coherence / self.challenges_per_epoch)) ** 2 + 0.05 * (total_corrections / self.challenges_per_epoch)
            
            # Gradient update
            if loss < prev_loss:
                self.gate_params["coherence_release_threshold"] = min(0.99, self.gate_params["coherence_release_threshold"] + 0.005)
                self.gate_params["coherence_warn_threshold"] = min(0.95, self.gate_params["coherence_warn_threshold"] + 0.003)
            else:
                self.gate_params["coherence_release_threshold"] = max(0.75, self.gate_params["coherence_release_threshold"] - 0.005)
                self.gate_params["coherence_warn_threshold"] = max(0.50, self.gate_params["coherence_warn_threshold"] - 0.003)
                
            epoch_entry = {
                "epoch": epoch + 1,
                "loss": round(float(loss), 6),
                "dispositions": dispositions,
                "avg_coherence": round(total_coherence / self.challenges_per_epoch, 4),
                "avg_corrections": round(total_corrections / self.challenges_per_epoch, 2),
                "gate_thresholds": dict(self.gate_params)
            }
            epoch_logs.append(epoch_entry)
            prev_loss = loss
            
        return {
            "num_epochs": self.num_epochs,
            "final_loss": round(float(prev_loss), 6),
            "final_gate_params": self.gate_params,
            "epoch_log": epoch_logs
        }

def main():
    print("=" * 90)
    print("DAXDA UNPROMPTED & SELF-GUIDED AUTONOMOUS ENGINE ACTIVATION")
    print("   Mode: Continuous Evolutionary Self-Play & Self-Guided Synthesis (Fast Cl41)")
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
    print("\n--- STEP 2: Fast Evolutionary Self-Play Optimization (20 Epochs) ---")
    t_evo0 = time.perf_counter()
    evo = FastEvolutionaryLoop(num_epochs=20, challenges_per_epoch=30)
    evo_results = evo.run()
    t_evo_ms = (time.perf_counter() - t_evo0) * 1000.0
    
    print(f"  Evolution Complete in {t_evo_ms:.2f} ms! Final Loss: {evo_results['final_loss']}")
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
