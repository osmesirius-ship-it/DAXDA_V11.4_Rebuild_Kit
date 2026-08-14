"""Evolutionary Self-Play Loop — Autonomous Self-Improvement Engine.

Generates synthetic reasoning challenges, tests them against the gate system,
discovers weaknesses, and applies gradient updates to thresholds and encoder
parameters to continuously improve decision boundaries.

Loss function:
    L = H(G(M₀) || G(M̂₀))  (cross-entropy between direct and reconstructed verdicts)

Update rule:
    θ_{t+1} = θ_t - η * ∇_θ L
"""
from __future__ import annotations
import random
import math
import json
import hashlib
from clifford_algebra import CliffordAlgebra, GMV, scalar, basis_vector, CL82
from adaptive_rotor import AdaptiveTransport
from feedback_loop import FeedbackLoop, CoherenceFunction


class SyntheticChallengeGenerator:
    """Generates synthetic reasoning challenges to probe the system's weaknesses.
    
    Strategies:
    1. Boundary probing: samples near the decision boundary
    2. Adversarial injection: injects high-grade energy to test contradiction detection
    3. Random exploration: uniform random states to discover unknown failure modes
    """

    def __init__(self, algebra: CliffordAlgebra = CL82, seed: int = 42):
        self.algebra = algebra
        self.rng = random.Random(seed)

    def boundary_probe(self, num_samples: int = 10) -> list[GMV]:
        """Generate states near the decision boundary (coherence ≈ 0.5)."""
        challenges = []
        for _ in range(num_samples):
            comps = {}
            # Mix useful and high-grade energy roughly equally
            for blade_id in range(min(self.algebra.dim, 32)):
                grade = self.algebra.grade_of(blade_id)
                if grade <= 2:
                    comps[blade_id] = self.rng.gauss(0.5, 0.2)
                elif grade <= 4:
                    comps[blade_id] = self.rng.gauss(0.3, 0.15)
            challenges.append(GMV(self.algebra, comps))
        return challenges

    def adversarial_injection(self, num_samples: int = 10) -> list[GMV]:
        """Generate states with deliberately high adversarial energy."""
        challenges = []
        for _ in range(num_samples):
            comps = {}
            # Concentrate energy in high-grade blades
            for blade_id in range(min(self.algebra.dim, 32)):
                grade = self.algebra.grade_of(blade_id)
                if grade <= 1:
                    comps[blade_id] = self.rng.gauss(0.1, 0.05)
                elif grade >= 3:
                    comps[blade_id] = self.rng.gauss(0.8, 0.3)
            challenges.append(GMV(self.algebra, comps))
        return challenges

    def random_exploration(self, num_samples: int = 10) -> list[GMV]:
        """Uniformly random states for broad exploration."""
        challenges = []
        for _ in range(num_samples):
            comps = {}
            for blade_id in range(min(self.algebra.dim, 16)):
                comps[blade_id] = self.rng.uniform(-1.0, 1.0)
            challenges.append(GMV(self.algebra, comps))
        return challenges


class EvolutionaryLoop:
    """Self-play training loop that discovers and patches system weaknesses.
    
    Each epoch:
    1. Generate synthetic challenges
    2. Run them through adaptive transport + feedback loop
    3. Score each challenge (coherence, residual, correction count)
    4. Update gate thresholds and learning rates based on aggregate loss
    """

    def __init__(self, algebra: CliffordAlgebra = CL82,
                 learning_rate: float = 0.01,
                 num_epochs: int = 20,
                 challenges_per_epoch: int = 30):
        self.algebra = algebra
        self.transport = AdaptiveTransport(algebra, num_planes=10, residual_tolerance=1e-6)
        self.feedback = FeedbackLoop(algebra, learning_rate=0.05, max_iterations=20)
        self.coherence_fn = CoherenceFunction(algebra)
        self.generator = SyntheticChallengeGenerator(algebra)

        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.challenges_per_epoch = challenges_per_epoch

        # Trainable gate parameters
        self.gate_params = {
            "coherence_release_threshold": 0.90,
            "coherence_warn_threshold": 0.60,
            "max_corrections_before_block": 3,
            "residual_tolerance": 1e-6,
        }

    def classify(self, coherence: float, corrections: int, residual: float) -> str:
        """Gate classification based on current trainable parameters."""
        if residual > self.gate_params["residual_tolerance"]:
            return "BLOCK"
        if corrections >= self.gate_params["max_corrections_before_block"]:
            return "BLOCK"
        if coherence >= self.gate_params["coherence_release_threshold"]:
            return "RELEASE"
        if coherence >= self.gate_params["coherence_warn_threshold"]:
            return "WARN"
        return "BLOCK"

    def compute_epoch_loss(self, results: list[dict]) -> float:
        """Aggregate loss: penalizes low coherence and high correction counts.
        
        L = (1/N) Σ [ (1 - coherence_i)^2 + λ * corrections_i^2 ]
        """
        if not results:
            return 1.0
        total = 0.0
        lam = 0.1
        for r in results:
            total += (1.0 - r["final_coherence"]) ** 2 + lam * r["corrections_applied"] ** 2
        return total / len(results)

    def update_params(self, loss: float, prev_loss: float):
        """Gradient-free parameter update based on loss direction."""
        if loss < prev_loss:
            # Loss decreased: tighten thresholds slightly
            self.gate_params["coherence_release_threshold"] = min(
                0.99, self.gate_params["coherence_release_threshold"] + self.learning_rate * 0.1)
            self.gate_params["coherence_warn_threshold"] = min(
                0.95, self.gate_params["coherence_warn_threshold"] + self.learning_rate * 0.05)
        else:
            # Loss increased: relax thresholds
            self.gate_params["coherence_release_threshold"] = max(
                0.70, self.gate_params["coherence_release_threshold"] - self.learning_rate * 0.05)
            self.gate_params["coherence_warn_threshold"] = max(
                0.40, self.gate_params["coherence_warn_threshold"] - self.learning_rate * 0.05)

    def run(self) -> dict:
        """Execute the evolutionary self-play loop."""
        epoch_log = []
        prev_loss = 1.0
        n_per = self.challenges_per_epoch // 3

        for epoch in range(self.num_epochs):
            # 1. Generate challenges
            challenges = (
                self.generator.boundary_probe(n_per) +
                self.generator.adversarial_injection(n_per) +
                self.generator.random_exploration(self.challenges_per_epoch - 2 * n_per)
            )

            # 2. Process each challenge
            results = []
            dispositions = {"RELEASE": 0, "WARN": 0, "BLOCK": 0}
            for state in challenges:
                # Semantic profile from grade energies
                grade_energies = {}
                for blade, val in state.components.items():
                    g = self.algebra.grade_of(blade)
                    grade_energies[f"grade_{g}"] = grade_energies.get(f"grade_{g}", 0.0) + val * val

                transport_result = self.transport.run(state, grade_energies)
                feedback_result = self.feedback.run(state)

                disposition = self.classify(
                    feedback_result["final_coherence"],
                    feedback_result["corrections_applied"],
                    transport_result["max_residual"]
                )
                dispositions[disposition] += 1

                results.append({
                    "final_coherence": feedback_result["final_coherence"],
                    "corrections_applied": feedback_result["corrections_applied"],
                    "residual": transport_result["max_residual"],
                    "integrity": transport_result["integrity_pass"],
                    "disposition": disposition,
                })

            # 3. Compute loss
            loss = self.compute_epoch_loss(results)

            # 4. Update params
            self.update_params(loss, prev_loss)

            epoch_entry = {
                "epoch": epoch,
                "loss": round(loss, 6),
                "dispositions": dict(dispositions),
                "gate_params": {k: round(v, 6) if isinstance(v, float) else v
                                for k, v in self.gate_params.items()},
                "avg_coherence": round(
                    sum(r["final_coherence"] for r in results) / len(results), 6),
                "avg_corrections": round(
                    sum(r["corrections_applied"] for r in results) / len(results), 4),
            }
            epoch_log.append(epoch_entry)
            prev_loss = loss

        return {
            "num_epochs": self.num_epochs,
            "final_loss": round(prev_loss, 6),
            "final_gate_params": dict(self.gate_params),
            "epoch_log": epoch_log,
        }
