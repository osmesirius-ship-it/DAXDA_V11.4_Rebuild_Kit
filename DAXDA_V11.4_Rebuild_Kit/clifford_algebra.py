"""Clifford Algebra Cl(p,q) — Generalized High-Dimensional Engine.

Supports arbitrary signature (p,q) algebras for AGLM cognitive manifold operations.
Default configuration: Cl(8,2) with 2^10 = 1024 basis blade components.

Basis blade ordering uses canonical binary index representation:
  blade index 0 = scalar (grade 0)
  blade index 1 = e1 (grade 1)
  blade index 2 = e2 (grade 1)
  blade index 3 = e12 (grade 2)
  ...
  blade index 2^n - 1 = e_{1..n} (grade n)

Geometric product computed via sign lookup from metric signature.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math
import itertools

# ---------------------------------------------------------------------------
# Metric signature helpers
# ---------------------------------------------------------------------------

def _canonical_sign(indices: list[int], metric_signs: list[int]) -> int:
    """Compute the sign factor for a product of basis vectors given their metric.
    Uses bubble sort to count transpositions, then squares repeated indices."""
    work = list(indices)
    sign = 1
    # Bubble sort to canonical order, counting swaps
    n = len(work)
    for i in range(n):
        for j in range(n - 1 - i):
            if work[j] > work[j + 1]:
                work[j], work[j + 1] = work[j + 1], work[j]
                sign = -sign
    # Cancel paired indices using metric
    result_indices = []
    i = 0
    while i < len(work):
        if i + 1 < len(work) and work[i] == work[i + 1]:
            sign *= metric_signs[work[i]]
            i += 2
        else:
            result_indices.append(work[i])
            i += 1
    return sign, tuple(result_indices)


def _blade_indices(blade_id: int, n: int) -> list[int]:
    """Convert a blade bitmask ID to a sorted list of basis vector indices."""
    return [i for i in range(n) if (blade_id >> i) & 1]


def _indices_to_blade(indices: tuple[int, ...]) -> int:
    """Convert sorted basis vector indices back to a blade bitmask."""
    result = 0
    for i in indices:
        result |= (1 << i)
    return result


# ---------------------------------------------------------------------------
# Precomputed multiplication table
# ---------------------------------------------------------------------------

class CliffordAlgebra:
    """Precomputed Clifford algebra structure for signature (p, q).
    
    Attributes:
        p: Number of positive-square basis vectors.
        q: Number of negative-square basis vectors.
        n: Total dimension = p + q.
        dim: Algebra dimension = 2^n.
        mul_table: Precomputed (sign, result_blade) for each (a, b) pair.
    """

    def __init__(self, p: int, q: int):
        self.p = p
        self.q = q
        self.n = p + q
        self.dim = 1 << self.n  # 2^n

        # Metric: first p vectors square to +1, next q square to -1
        self.metric_signs = [1] * p + [-1] * q

        # Precompute multiplication table
        self.mul_table: list[list[tuple[int, int]]] = []
        for a in range(self.dim):
            row = []
            for b in range(self.dim):
                ia = _blade_indices(a, self.n)
                ib = _blade_indices(b, self.n)
                sign, result_indices = _canonical_sign(ia + ib, self.metric_signs)
                result_blade = _indices_to_blade(result_indices)
                row.append((sign, result_blade))
            self.mul_table.append(row)

    def grade_of(self, blade_id: int) -> int:
        """Return the grade (number of basis vectors) of a blade."""
        return bin(blade_id).count('1')


# ---------------------------------------------------------------------------
# Shared algebra singletons
# ---------------------------------------------------------------------------

# Default Cl(2,0) for backward compatibility with V11.4
CL20 = CliffordAlgebra(2, 0)

# AGLM target: Cl(8,2) — 10-dimensional, 1024-component multivectors
CL82 = CliffordAlgebra(8, 2)


# ---------------------------------------------------------------------------
# Generalized Multivector
# ---------------------------------------------------------------------------

class GMV:
    """Generalized Multivector over an arbitrary Clifford algebra.
    
    Stores only nonzero components in a sparse dictionary {blade_id: coefficient}.
    """

    __slots__ = ('algebra', 'components')

    def __init__(self, algebra: CliffordAlgebra, components: Optional[dict[int, float]] = None):
        self.algebra = algebra
        if components is None:
            self.components: dict[int, float] = {}
        else:
            # Filter out near-zero components for sparsity
            self.components = {k: v for k, v in components.items() if abs(v) > 1e-18}

    # --- Accessors ---

    def __getitem__(self, blade_id: int) -> float:
        return self.components.get(blade_id, 0.0)

    def __setitem__(self, blade_id: int, value: float):
        if abs(value) > 1e-18:
            self.components[blade_id] = value
        elif blade_id in self.components:
            del self.components[blade_id]

    @property
    def scalar(self) -> float:
        return self[0]

    # --- Arithmetic ---

    def __add__(self, other: GMV) -> GMV:
        result = dict(self.components)
        for k, v in other.components.items():
            result[k] = result.get(k, 0.0) + v
        return GMV(self.algebra, result)

    def __sub__(self, other: GMV) -> GMV:
        result = dict(self.components)
        for k, v in other.components.items():
            result[k] = result.get(k, 0.0) - v
        return GMV(self.algebra, result)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return GMV(self.algebra, {k: v * other for k, v in self.components.items()})
        if not isinstance(other, GMV):
            return NotImplemented
        table = self.algebra.mul_table
        result: dict[int, float] = {}
        for a, va in self.components.items():
            for b, vb in other.components.items():
                sign, blade = table[a][b]
                result[blade] = result.get(blade, 0.0) + sign * va * vb
        return GMV(self.algebra, result)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        return NotImplemented

    def __neg__(self) -> GMV:
        return GMV(self.algebra, {k: -v for k, v in self.components.items()})

    # --- Clifford operations ---

    def reverse(self) -> GMV:
        """Clifford reverse (reversion): reverses the order of basis vectors in each blade.
        For a grade-k blade, reverse multiplies by (-1)^(k*(k-1)/2).
        """
        result = {}
        for blade, val in self.components.items():
            grade = self.algebra.grade_of(blade)
            sign = (-1) ** (grade * (grade - 1) // 2)
            result[blade] = sign * val
        return GMV(self.algebra, result)

    def grade_select(self, grade: int) -> GMV:
        """Extract components of a specific grade."""
        result = {}
        for blade, val in self.components.items():
            if self.algebra.grade_of(blade) == grade:
                result[blade] = val
        return GMV(self.algebra, result)

    def norm2(self) -> float:
        """Scalar part of self * ~self."""
        return (self * self.reverse()).scalar

    def magnitude(self) -> float:
        return math.sqrt(abs(self.norm2()))

    def normalized(self, floor: float = 1e-12) -> GMV:
        mag = max(self.magnitude(), floor)
        return self * (1.0 / mag)

    # --- Rotor operations ---

    def sandwich(self, rotor: GMV) -> GMV:
        """Apply sandwich product: rotor * self * ~rotor."""
        return rotor * self * rotor.reverse()

    # --- Wedge (outer) product ---

    def wedge(self, other: GMV) -> GMV:
        """Outer product: keeps only components whose grade equals sum of input grades."""
        table = self.algebra.mul_table
        result: dict[int, float] = {}
        ga = self.algebra.grade_of
        for a, va in self.components.items():
            for b, vb in other.components.items():
                sign, blade = table[a][b]
                if ga(blade) == ga(a) + ga(b):
                    result[blade] = result.get(blade, 0.0) + sign * va * vb
        return GMV(self.algebra, result)

    # --- Inner product ---

    def inner(self, other: GMV) -> GMV:
        """Left contraction inner product."""
        table = self.algebra.mul_table
        result: dict[int, float] = {}
        ga = self.algebra.grade_of
        for a, va in self.components.items():
            for b, vb in other.components.items():
                sign, blade = table[a][b]
                if ga(blade) == abs(ga(b) - ga(a)):
                    result[blade] = result.get(blade, 0.0) + sign * va * vb
        return GMV(self.algebra, result)

    # --- Serialization ---

    def to_dict(self, precision: int = 8) -> dict:
        """Serialize nonzero components as {blade_id_str: rounded_value}."""
        return {str(k): round(v, precision) for k, v in sorted(self.components.items()) if abs(v) > 1e-15}

    def max_residual(self, other: GMV) -> float:
        """Compute max absolute difference across all blades."""
        all_blades = set(self.components.keys()) | set(other.components.keys())
        if not all_blades:
            return 0.0
        return max(abs(self[b] - other[b]) for b in all_blades)

    def __repr__(self) -> str:
        if not self.components:
            return "GMV(0)"
        parts = []
        for blade in sorted(self.components):
            val = self.components[blade]
            if blade == 0:
                parts.append(f"{val:.6f}")
            else:
                indices = _blade_indices(blade, self.algebra.n)
                label = "e" + "".join(str(i + 1) for i in indices)
                parts.append(f"{val:.6f}·{label}")
        return "GMV(" + " + ".join(parts) + ")"


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def scalar(algebra: CliffordAlgebra, value: float) -> GMV:
    """Create a scalar multivector."""
    return GMV(algebra, {0: value})


def basis_vector(algebra: CliffordAlgebra, index: int) -> GMV:
    """Create a single basis vector e_{index+1}."""
    blade = 1 << index
    return GMV(algebra, {blade: 1.0})


def bivector_rotor(algebra: CliffordAlgebra, i: int, j: int, theta: float) -> GMV:
    """Create a rotor exp(-theta/2 * e_ij) for rotation in the e_i, e_j plane."""
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    blade_ij = (1 << i) | (1 << j)
    return GMV(algebra, {0: c, blade_ij: -s})
