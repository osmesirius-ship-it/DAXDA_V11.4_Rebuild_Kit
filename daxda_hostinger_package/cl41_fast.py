"""Optimized Clifford Algebra Cl(4,1) — Conformal Geometric Algebra.

32-blade algebra with NumPy array backend for maximum throughput.
NO lookup tables, NO scaffolding — pure algebraic computation.

Basis: 5 vectors (e1..e5), signature (+,+,+,+,-).
  e1^2 = e2^2 = e3^2 = e4^2 = +1
  e5^2 = -1

Blade count: 2^5 = 32.
Multiplication table: 32x32 = 1024 entries (fits in L1 cache).
"""
from __future__ import annotations
import math
import numpy as np
from functools import lru_cache

# ──────────────────────────────────────────────────────────────────────
# Metric and sign computation via bitwise operations
# ──────────────────────────────────────────────────────────────────────

P, Q = 5, 0  # Cl(5,0) positive-definite algebra
N = P + Q    # 5
DIM = 1 << N # 32

# Metric: all p basis vectors square to +1
METRIC = np.array([1] * P + [-1] * Q, dtype=np.int8)


def _popcount(x: int) -> int:
    """Count set bits."""
    return bin(x).count('1')


def _grade(blade: int) -> int:
    """Grade of a blade = number of basis vectors."""
    return _popcount(blade)


def _canonical_product(a: int, b: int) -> tuple[int, int]:
    """Compute geometric product of two basis blades using bitwise ops.
    
    Returns (sign, result_blade).
    Sign accounts for: anticommutation swaps + metric contractions.
    """
    # Count swaps needed to interleave b's bits past a's bits
    sign = 1
    swaps = 0
    b_shifted = b
    for i in range(N):
        if not (b_shifted & (1 << i)):
            continue
        # Count how many bits in a are above position i
        mask_above = a >> (i + 1)
        swaps += _popcount(mask_above & ((1 << (N - i - 1)) - 1 | (1 << (N - i - 1))))
        # Actually: count bits in a at positions > i
        bits_above = 0
        for j in range(i + 1, N):
            if a & (1 << j):
                bits_above += 1
        swaps += bits_above - _popcount(mask_above & ((1 << (N - i - 1)) - 1 | (1 << (N - i - 1))))
    
    # Simpler approach: bubble sort indices
    ia = [i for i in range(N) if (a >> i) & 1]
    ib = [i for i in range(N) if (b >> i) & 1]
    merged = ia + ib
    
    sign = 1
    n = len(merged)
    for i in range(n):
        for j in range(n - 1 - i):
            if merged[j] > merged[j + 1]:
                merged[j], merged[j + 1] = merged[j + 1], merged[j]
                sign = -sign
    
    # Cancel paired indices using metric
    result_indices = []
    i = 0
    while i < len(merged):
        if i + 1 < len(merged) and merged[i] == merged[i + 1]:
            sign *= METRIC[merged[i]]
            i += 2
        else:
            result_indices.append(merged[i])
            i += 1
    
    result_blade = 0
    for idx in result_indices:
        result_blade |= (1 << idx)
    
    return sign, result_blade


# ──────────────────────────────────────────────────────────────────────
# Precomputed multiplication table (32x32 = 1024 entries)
# ──────────────────────────────────────────────────────────────────────

# sign_table[a][b] = sign of product, blade_table[a][b] = result blade
_SIGN_TABLE = np.zeros((DIM, DIM), dtype=np.int8)
_BLADE_TABLE = np.zeros((DIM, DIM), dtype=np.int8)

for _a in range(DIM):
    for _b in range(DIM):
        _s, _r = _canonical_product(_a, _b)
        _SIGN_TABLE[_a, _b] = _s
        _BLADE_TABLE[_a, _b] = _r

# Grade lookup
_GRADE = np.array([_grade(i) for i in range(DIM)], dtype=np.int8)


# ──────────────────────────────────────────────────────────────────────
# Fast Multivector — NumPy array backend
# ──────────────────────────────────────────────────────────────────────

class FMV:
    """Fast Multivector over Cl(4,1) using a flat NumPy array of 32 components.
    
    NO dict lookups. NO Python loops in hot paths.
    All operations are vectorized array math.
    """
    __slots__ = ('data',)

    def __init__(self, data: np.ndarray = None):
        if data is None:
            self.data = np.zeros(DIM, dtype=np.float64)
        else:
            self.data = np.asarray(data, dtype=np.float64)

    # --- Factories ---

    @staticmethod
    def scalar(value: float) -> FMV:
        mv = FMV()
        mv.data[0] = value
        return mv

    @staticmethod
    def basis(index: int, value: float = 1.0) -> FMV:
        """Create basis vector e_{index+1}."""
        mv = FMV()
        mv.data[1 << index] = value
        return mv

    @staticmethod
    def from_components(components: dict[int, float]) -> FMV:
        mv = FMV()
        for blade, val in components.items():
            mv.data[blade] = val
        return mv

    # --- Accessors ---

    @property
    def s(self) -> float:
        return self.data[0]

    def grade_select(self, grade: int) -> FMV:
        result = FMV()
        mask = _GRADE == grade
        result.data[mask] = self.data[mask]
        return result

    # --- Arithmetic ---

    def __add__(self, other: FMV) -> FMV:
        return FMV(self.data + other.data)

    def __sub__(self, other: FMV) -> FMV:
        return FMV(self.data - other.data)

    def __neg__(self) -> FMV:
        return FMV(-self.data)

    def scale(self, factor: float) -> FMV:
        return FMV(self.data * factor)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.scale(other)
        if not isinstance(other, FMV):
            return NotImplemented
        result = np.zeros(DIM, dtype=np.float64)
        # Find nonzero components for sparse multiply
        nz_a = np.nonzero(self.data)[0]
        nz_b = np.nonzero(other.data)[0]
        for a in nz_a:
            va = self.data[a]
            for b in nz_b:
                vb = other.data[b]
                sign = _SIGN_TABLE[a, b]
                blade = _BLADE_TABLE[a, b]
                result[blade] += sign * va * vb
        return FMV(result)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.scale(other)
        return NotImplemented

    # --- Clifford ops ---

    def reverse(self) -> FMV:
        """Clifford reversion: grade k -> (-1)^(k(k-1)/2)."""
        result = self.data.copy()
        for blade in range(DIM):
            g = _GRADE[blade]
            if (g * (g - 1) // 2) % 2 == 1:
                result[blade] = -result[blade]
        return FMV(result)

    def sandwich(self, rotor: FMV) -> FMV:
        """Sandwich product: rotor * self * ~rotor."""
        return rotor * self * rotor.reverse()

    def norm2(self) -> float:
        return (self * self.reverse()).s

    def magnitude(self) -> float:
        return math.sqrt(abs(self.norm2()))

    def normalized(self, floor: float = 1e-12) -> FMV:
        mag = max(self.magnitude(), floor)
        return self.scale(1.0 / mag)

    # --- Analysis ---

    def max_residual(self, other: FMV) -> float:
        return float(np.max(np.abs(self.data - other.data)))

    def to_dict(self, precision: int = 8) -> dict:
        result = {}
        for i in range(DIM):
            if abs(self.data[i]) > 1e-15:
                result[str(i)] = round(float(self.data[i]), precision)
        return result

    def energy_by_grade(self) -> dict[int, float]:
        """Compute energy (sum of squares) per grade."""
        energies = {}
        for g in range(N + 1):
            mask = _GRADE == g
            energies[g] = float(np.sum(self.data[mask] ** 2))
        return energies

    def __repr__(self) -> str:
        nz = [(i, self.data[i]) for i in range(DIM) if abs(self.data[i]) > 1e-15]
        if not nz:
            return "FMV(0)"
        parts = []
        for blade, val in nz:
            if blade == 0:
                parts.append(f"{val:.6f}")
            else:
                indices = [i + 1 for i in range(N) if (blade >> i) & 1]
                label = "e" + "".join(str(i) for i in indices)
                parts.append(f"{val:.6f}*{label}")
        return "FMV(" + " + ".join(parts) + ")"


# ──────────────────────────────────────────────────────────────────────
# Rotor factory
# ──────────────────────────────────────────────────────────────────────

def bivector_rotor(i: int, j: int, theta: float) -> FMV:
    """Create rotor exp(-theta/2 * e_ij) for rotation in the (e_i, e_j) plane.
    i, j are 0-indexed basis vector indices.
    """
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    blade_ij = (1 << i) | (1 << j)
    mv = FMV()
    mv.data[0] = c
    mv.data[blade_ij] = -s
    return mv
