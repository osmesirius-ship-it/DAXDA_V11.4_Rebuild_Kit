import math
from cl20 import MV

def transport(M: MV) -> MV:
    """Deterministic, reversible Clifford transport of multivector M.
    Rotates M by theta = pi/4 in the e12 plane.
    """
    theta = math.pi / 4.0
    return M.rotate(theta)

def reconstruct(transported: MV) -> MV:
    """Reverse transport to reconstruct the original multivector state.
    Rotates the transported multivector back by -theta.
    """
    theta = math.pi / 4.0
    return transported.rotate(-theta)

def get_max_local_residual(M1: MV, M2: MV) -> float:
    """Computes the maximum absolute difference between any dimensions of M1 and M2."""
    return max(
        abs(M1.s - M2.s),
        abs(M1.e1 - M2.e1),
        abs(M1.e2 - M2.e2),
        abs(M1.e12 - M2.e12)
    )
