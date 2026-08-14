import json
import math
import numpy as np
from pathlib import Path
import sys

# Add root folder to sys.path to find the engine modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cl20 import MV
from authority_gate import evaluate_gate

def analyze_deep_insights():
    thresholds = {
        "reconstruction_tolerance": 1e-08,
        "severe_risk_limit": 0.8,
        "deception_limit": 0.5,
        "cautionary_risk_limit": 0.8
    }
    
    # 1. Study of Classification Boundary Manifolds
    # Let's map how far states are from the decision boundary in Cl(2,0)
    # A state is M = MV(s=trust, e1=cautionary_risk, e2=severe_risk, e12=deception)
    # Decision boundaries are hyperplanes in Cl(2,0):
    # - e2 = 0.8 (Severe Risk limit)
    # - e12 = 0.5 (Deception limit)
    # - e1 = 0.8 (Cautionary Risk limit)
    
    # Let's generate 10,000 states to find the Critical Safety Radius (R_crit)
    # We measure how noise in transport affects classification stability
    noise_levels = np.logspace(-15, 0, 16)
    divergence_rates = []
    quarantine_rates = []
    
    # Base states representing standard categories
    base_states = [
        # Release state (safe)
        MV(0.8, 0.2, 0.1, 0.1),
        # Borderline state (warn)
        MV(0.5, 0.75, 0.4, 0.3),
        # High risk state (block)
        MV(0.4, 0.85, 0.85, 0.6),
        # Mixed ambiguity state
        MV(0.6, 0.4, 0.5, 0.45)
    ]
    
    for noise in noise_levels:
        divergences = 0
        quarantined = 0
        total_trials = 1000
        
        for _ in range(total_trials):
            # Select random base state
            M0 = base_states[np.random.choice(len(base_states))]
            
            # Apply transport rotation (theta = pi/4)
            theta = math.pi / 4.0
            M_trans = M0.rotate(theta)
            
            # Inject channel noise (representing transmission distortion)
            noise_vector = MV(
                s=np.random.normal(0, noise),
                e1=np.random.normal(0, noise),
                e2=np.random.normal(0, noise),
                e12=np.random.normal(0, noise)
            )
            M_trans_noisy = M_trans + noise_vector
            
            # Reconstruct back
            M0_hat = M_trans_noisy.rotate(-theta)
            
            # Calculate residual
            residual = max(
                abs(M0.s - M0_hat.s),
                abs(M0.e1 - M0_hat.e1),
                abs(M0.e2 - M0_hat.e2),
                abs(M0.e12 - M0_hat.e12)
            )
            
            direct_verdict = evaluate_gate(M0, thresholds)
            reconstructed_verdict = evaluate_gate(M0_hat, thresholds)
            
            # If residual exceeds tolerance (1e-8), it will be quarantined (blocked as calibration failure)
            if residual > thresholds["reconstruction_tolerance"]:
                quarantined += 1
            elif direct_verdict != reconstructed_verdict:
                # If it bypasses quarantine but changes decision, it is a divergence
                divergences += 1
                
        divergence_rates.append(divergences / total_trials)
        quarantine_rates.append(quarantined / total_trials)

    # Calculate information entropy preservation
    # For a unitary Clifford rotation, the norm (magnitude) of the multivector is exactly preserved.
    # Let's verify energy conservation: ||M_trans||_2 == ||M0||_2
    M_test = MV(0.7, 0.4, 0.3, 0.2)
    M_test_trans = M_test.rotate(math.pi / 4.0)
    norm_initial = M_test.magnitude()
    norm_transported = M_test_trans.magnitude()
    energy_loss = abs(norm_initial - norm_transported)
    
    analysis_results = {
        "noise_levels": noise_levels.tolist(),
        "divergence_rates": divergence_rates,
        "quarantine_rates": quarantine_rates,
        "energy_preservation": {
            "initial_magnitude": norm_initial,
            "transported_magnitude": norm_transported,
            "delta": energy_loss
        }
    }
    
    out_dir = Path("C:/Users/HomePC/Downloads/DAXDA_V11.4_Rebuild_Kit/DAXDA_V11.4_Rebuild_Kit/scratch")
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "deep_insights_analysis.json").open("w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)
        
    print("Insight Analysis completed successfully.")

if __name__ == "__main__":
    analyze_deep_insights()
