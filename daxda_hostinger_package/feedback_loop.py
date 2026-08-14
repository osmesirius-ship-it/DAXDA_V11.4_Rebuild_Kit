"""Self-Correcting Feedback Loop — Recursive Coherence Engine.

Implements a closed-loop reasoning cycle where the multivector state M_k
is iteratively refined. At each step, a coherence function S(M) measures
logical alignment and the system applies gradient-like updates:

    M_{k+1} = M_k + α * ∇_M S(M_k)

If a contradiction threshold is crossed (e_1 >= τ), the system dynamically
generates a correction vector and refines its reasoning trajectory.
"""
from __future__ import annotations
import math
from clifford_algebra import CliffordAlgebra, GMV, scalar, CL82


class CoherenceFunction:
    """Measures the logical coherence of a multivector reasoning state.
    
    S(M) = <M * ~M>_0 / ||M||^2 - penalty(high-grade energy leakage)
    
    The coherence is highest when energy is concentrated in the scalar
    and grade-1 (semantic fact) blades, and lowest when energy leaks
    into high-grade blades (indicating unresolved contradictions).
    """

    def __init__(self, algebra: CliffordAlgebra = CL82, max_useful_grade: int = 2):
        self.algebra = algebra
        self.max_useful_grade = max_useful_grade

    def evaluate(self, state: GMV) -> float:
        """Compute coherence score in [0, 1]."""
        total_energy = 0.0
        useful_energy = 0.0
        for blade, val in state.components.items():
            energy = val * val
            total_energy += energy
            if self.algebra.grade_of(blade) <= self.max_useful_grade:
                useful_energy += energy
        if total_energy < 1e-18:
            return 0.0
        return useful_energy / total_energy

    def gradient(self, state: GMV) -> GMV:
        """Approximate gradient of coherence: amplify useful grades, dampen high grades.
        
        ∇S ≈ project_useful(M) - project_leakage(M)
        """
        useful = {}
        leakage = {}
        for blade, val in state.components.items():
            if self.algebra.grade_of(blade) <= self.max_useful_grade:
                useful[blade] = val
            else:
                leakage[blade] = -val  # Negative: pushes energy away from leakage
        grad_components = dict(useful)
        for k, v in leakage.items():
            grad_components[k] = grad_components.get(k, 0.0) + v
        return GMV(self.algebra, grad_components)


class FeedbackLoop:
    """Recursive self-correcting reasoning loop.
    
    Iteratively refines a multivector state M until either:
    1. Coherence exceeds the convergence threshold, OR
    2. Maximum iterations are reached, OR
    3. A contradiction is detected and a correction is applied.
    """

    def __init__(self, algebra: CliffordAlgebra = CL82,
                 learning_rate: float = 0.05,
                 convergence_threshold: float = 0.95,
                 contradiction_threshold: float = 0.7,
                 max_iterations: int = 50):
        self.algebra = algebra
        self.coherence = CoherenceFunction(algebra)
        self.learning_rate = learning_rate
        self.convergence_threshold = convergence_threshold
        self.contradiction_threshold = contradiction_threshold
        self.max_iterations = max_iterations

    def detect_contradiction(self, state: GMV) -> bool:
        """Detect if the state has excessive energy in high-grade blades."""
        total = 0.0
        high_grade = 0.0
        for blade, val in state.components.items():
            energy = val * val
            total += energy
            if self.algebra.grade_of(blade) > 2:
                high_grade += energy
        if total < 1e-18:
            return False
        return (high_grade / total) >= self.contradiction_threshold

    def generate_correction(self, state: GMV) -> GMV:
        """Generate a correction vector that projects energy back to useful grades.
        
        For each high-grade blade with significant energy, create a compensating
        scalar+grade-1 injection that re-channels the energy.
        """
        correction = {}
        for blade, val in state.components.items():
            grade = self.algebra.grade_of(blade)
            if grade > 2 and abs(val) > 0.01:
                # Transfer energy to scalar
                correction[0] = correction.get(0, 0.0) + abs(val) * 0.5
                # Dampen the high-grade component
                correction[blade] = correction.get(blade, 0.0) - val * 0.8
        return GMV(self.algebra, correction)

    def run(self, initial_state: GMV) -> dict:
        """Execute the feedback loop and return the trajectory log."""
        state = GMV(self.algebra, dict(initial_state.components))
        trajectory = []
        converged = False
        corrections_applied = 0

        for iteration in range(self.max_iterations):
            coherence = self.coherence.evaluate(state)
            contradiction = self.detect_contradiction(state)

            step_log = {
                "iteration": iteration,
                "coherence": round(coherence, 6),
                "contradiction_detected": contradiction,
                "num_active_blades": len(state.components),
            }

            if coherence >= self.convergence_threshold:
                step_log["action"] = "CONVERGED"
                trajectory.append(step_log)
                converged = True
                break

            if contradiction:
                correction = self.generate_correction(state)
                state = state + correction * self.learning_rate
                corrections_applied += 1
                step_log["action"] = "CORRECTION_APPLIED"
            else:
                # Standard gradient ascent on coherence
                grad = self.coherence.gradient(state)
                state = state + grad * self.learning_rate
                step_log["action"] = "GRADIENT_STEP"

            trajectory.append(step_log)

        final_coherence = self.coherence.evaluate(state)

        return {
            "final_state": state.to_dict(),
            "final_coherence": round(final_coherence, 6),
            "converged": converged,
            "iterations": len(trajectory),
            "corrections_applied": corrections_applied,
            "trajectory": trajectory,
        }
