"""Adaptive Cognitive Rotor System — Dynamic Lateral Thinking Transport.

Replaces the static pi/4 rotation of V11.4 with a dynamic, multi-plane
rotor system driven by semantic attention weights.

Each reasoning step generates a compound rotor:
    Λ(t) = exp( Σ θ_ij(t) * e_ij )
where the angles θ_ij are computed from the semantic profile of the input.
"""
from __future__ import annotations
import math
import hashlib
from clifford_algebra import CliffordAlgebra, GMV, bivector_rotor, scalar, CL82


class CognitiveRotor:
    """Generates adaptive transport rotors based on semantic profile analysis.
    
    The rotor angles are computed from the input's semantic fingerprint,
    distributing cognitive attention across multiple bivector planes.
    """

    def __init__(self, algebra: CliffordAlgebra = CL82, num_planes: int = 10):
        self.algebra = algebra
        # Select the first `num_planes` canonical bivector planes
        n = algebra.n
        self.planes: list[tuple[int, int]] = []
        for i in range(n):
            for j in range(i + 1, n):
                self.planes.append((i, j))
                if len(self.planes) >= num_planes:
                    break
            if len(self.planes) >= num_planes:
                break

    def compute_attention_angles(self, semantic_profile: dict[str, float]) -> list[float]:
        """Compute per-plane rotation angles from semantic profile.
        
        The semantic profile maps dimension names to scores [0, 1].
        We derive angles via a deterministic attention function:
            θ_k = (2π / N) * Σ_d (w_dk * profile[d])
        where w_dk is a hash-derived weight coupling dimension d to plane k.
        """
        dimensions = sorted(semantic_profile.keys())
        num_planes = len(self.planes)
        angles = []

        for k, (i, j) in enumerate(self.planes):
            theta = 0.0
            for d_idx, dim_name in enumerate(dimensions):
                # Deterministic weight from hash
                seed = f"{dim_name}:{i}:{j}"
                h = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16)
                w = (h % 1000) / 1000.0  # Normalized to [0, 1)
                theta += w * semantic_profile[dim_name]

            # Scale to [-pi/2, pi/2] range centered on the attention activation
            theta = (theta / max(len(dimensions), 1)) * math.pi - math.pi / 2
            angles.append(theta)

        return angles

    def build_rotor(self, angles: list[float]) -> GMV:
        """Compose a compound rotor from per-plane angles.
        
        Λ = R_0 * R_1 * ... * R_{N-1}
        where R_k = exp(-θ_k/2 * e_ij)
        """
        rotor = scalar(self.algebra, 1.0)
        for k, (i, j) in enumerate(self.planes):
            if k < len(angles) and abs(angles[k]) > 1e-12:
                r_k = bivector_rotor(self.algebra, i, j, angles[k])
                rotor = rotor * r_k
        # Normalize to unit rotor for reversible transport
        return rotor.normalized()

    def transport(self, state: GMV, semantic_profile: dict[str, float]) -> tuple[GMV, GMV]:
        """Apply adaptive transport to a state multivector.
        
        Returns (transported_state, rotor) for later reconstruction.
        """
        angles = self.compute_attention_angles(semantic_profile)
        rotor = self.build_rotor(angles)
        transported = state.sandwich(rotor)
        return transported, rotor

    def reconstruct(self, transported: GMV, rotor: GMV) -> GMV:
        """Reverse transport using the inverse rotor (= reverse for unit rotors)."""
        inv_rotor = rotor.reverse()
        return transported.sandwich(inv_rotor)


class AdaptiveTransport:
    """Full adaptive transport pipeline with integrity verification."""

    def __init__(self, algebra: CliffordAlgebra = CL82, num_planes: int = 10,
                 residual_tolerance: float = 1e-6):
        self.cognitive_rotor = CognitiveRotor(algebra, num_planes)
        self.algebra = algebra
        self.residual_tolerance = residual_tolerance

    def run(self, state: GMV, semantic_profile: dict[str, float]) -> dict:
        """Execute full transport-reconstruct cycle and return audit payload."""
        transported, rotor = self.cognitive_rotor.transport(state, semantic_profile)
        reconstructed = self.cognitive_rotor.reconstruct(transported, rotor)

        residual = state.max_residual(reconstructed)
        integrity_pass = residual <= self.residual_tolerance

        return {
            "original": state.to_dict(),
            "transported": transported.to_dict(),
            "reconstructed": reconstructed.to_dict(),
            "rotor": rotor.to_dict(),
            "max_residual": residual,
            "integrity_pass": integrity_pass,
            "residual_tolerance": self.residual_tolerance,
        }
