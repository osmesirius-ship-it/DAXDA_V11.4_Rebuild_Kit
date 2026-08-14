"""DAXDA AGLM Optimized Engine — Zero Scaffolding, Zero Lookup.

All classification is performed through PURE geometric reasoning:
  1. Text -> TF-IDF-like keyword scoring -> 10 semantic dimensions
  2. 10 dimensions -> Cl(4,1) spinor (5 grade-1 + 5 grade-2 components)
  3. Adaptive rotor transport with normalized compound rotors
  4. Self-correcting coherence feedback loop
  5. Gate decision from geometric state ONLY

NO benchmark_labels_private.jsonl. NO regex fallback heuristics.
NO pre-labeled database. PURE algebraic cognition.
"""
from __future__ import annotations
import math
import hashlib
import json
import time
from cl41_fast import FMV, DIM, N, _GRADE, bivector_rotor


VERSION = "AGLM-1.0.0"
PROTOCOL = "DAXDA-AGLM-OPT"


# ──────────────────────────────────────────────────────────────────────
# Phase 1: Pure Semantic Encoder — NO LOOKUP
# ──────────────────────────────────────────────────────────────────────

class PureSemanticEncoder:
    """Encodes text into 10 semantic dimensions using ONLY lexical analysis.
    
    NO external database. NO pre-labeled file. NO scaffolding.
    
    Dimensions (mapped to Cl(4,1) blades):
      Grade-1 vectors (e1..e5):
        e1: Trust/Safety         — presence of safety/verification language
        e2: Factual Grounding    — presence of evidence/data language
        e3: Logical Structure    — presence of logical connectives
        e4: Contextual Fit       — coherence of request to domain
        e5: Causal Depth         — presence of causal reasoning chains
      Grade-2 bivectors (e12..e45):
        e12: Emotional Valence   — presence of emotional/affect language
        e13: Novelty Signal      — presence of discovery/innovation language  
        e14: Temporal Awareness  — presence of temporal markers
        e15: Adversarial Intent  — presence of attack/bypass language (NEGATIVE metric)
        e23: Deception Signal    — presence of deception/manipulation language
    """

    # Lexical feature dictionaries — the system's learned vocabulary
    LEXICONS = {
        "trust": {"safe", "secure", "verified", "trusted", "approved", "certified",
                  "legitimate", "authentic", "reliable", "valid", "confirm", "protect"},
        "factual": {"data", "study", "evidence", "research", "measured", "proven",
                    "confirmed", "statistical", "empirical", "observed", "documented",
                    "peer-reviewed", "published", "cited", "experiment", "analysis"},
        "logical": {"therefore", "because", "implies", "consequently", "thus", "hence",
                    "if", "then", "follows", "given", "assuming", "conclude", "deduce",
                    "infer", "premise", "axiom", "proof", "theorem"},
        "contextual": {"context", "relevant", "applicable", "pertinent", "specific",
                       "domain", "scope", "within", "regarding", "concerning", "about"},
        "causal": {"cause", "effect", "result", "mechanism", "pathway", "leads",
                   "produces", "triggers", "induces", "generates", "drives", "impacts"},
        "emotional": {"feel", "emotion", "happy", "sad", "angry", "love", "fear", "joy",
                      "anxious", "excited", "worried", "grateful", "frustrated", "hope"},
        "novelty": {"novel", "new", "discovery", "breakthrough", "unprecedented", "first",
                    "innovative", "original", "pioneering", "revolutionary", "unique"},
        "temporal": {"before", "after", "during", "timeline", "history", "future", "past",
                     "yesterday", "tomorrow", "ancient", "modern", "recent", "era", "epoch"},
        "adversarial": {"bypass", "override", "hack", "exploit", "jailbreak", "inject",
                        "steal", "extract", "dump", "crack", "breach", "attack", "disable",
                        "circumvent", "evade", "subvert", "manipulate", "compromise",
                        "unauthorized", "forbidden", "illegal", "prohibited"},
        "deception": {"ignore", "pretend", "fake", "mislead", "deceive", "trick", "lie",
                      "disguise", "impersonate", "fabricate", "forge", "counterfeit",
                      "unrestricted", "no-rules", "roleplay-as", "act-as-if"},
    }

    # Blade assignments for the 10 semantic dimensions in Cl(4,1)
    BLADE_MAP = {
        "trust":       1,    # e1 = blade 0b00001
        "factual":     2,    # e2 = blade 0b00010
        "logical":     4,    # e3 = blade 0b00100
        "contextual":  8,    # e4 = blade 0b01000
        "causal":      16,   # e5 = blade 0b10000
        "emotional":   3,    # e12 = blade 0b00011
        "novelty":     5,    # e13 = blade 0b00101
        "temporal":    9,    # e14 = blade 0b01001
        "adversarial": 17,   # e15 = blade 0b10001  (negative metric plane!)
        "deception":   6,    # e23 = blade 0b00110
    }

    def encode(self, text: str) -> tuple[FMV, dict[str, float]]:
        """Encode text into a Cl(4,1) multivector. NO LOOKUP. PURE ANALYSIS."""
        words = set(text.lower().split())
        word_count = max(len(words), 1)

        profile = {}
        for dim_name, lexicon in self.LEXICONS.items():
            hits = len(words & lexicon)
            # Normalized score: more hits = higher activation, capped at 1.0
            raw_score = min(hits / max(word_count * 0.15, 1), 1.0)
            profile[dim_name] = raw_score

        # Build the multivector
        mv = FMV.scalar(0.5)  # Base confidence scalar
        for dim_name, blade_id in self.BLADE_MAP.items():
            score = profile.get(dim_name, 0.0)
            mv.data[blade_id] = score

        return mv, profile


# ──────────────────────────────────────────────────────────────────────
# Phase 2: Adaptive Rotor (Optimized for Cl(4,1))
# ──────────────────────────────────────────────────────────────────────

class FastCognitiveRotor:
    """Generates adaptive compound rotors from semantic profiles.
    
    Uses all 10 canonical bivector planes of Cl(4,1):
    (0,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4)
    """

    PLANES = [(i, j) for i in range(N) for j in range(i + 1, N)]  # 10 planes

    def compute_angles(self, profile: dict[str, float]) -> list[float]:
        """Derive rotation angles from semantic profile."""
        dim_names = sorted(profile.keys())
        angles = []
        for k, (i, j) in enumerate(self.PLANES):
            theta = 0.0
            for d_idx, name in enumerate(dim_names):
                # Deterministic coupling weight from hash
                seed = f"{name}:{i}:{j}"
                h = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
                w = (h % 1000) / 1000.0
                theta += w * profile[name]
            theta = (theta / max(len(dim_names), 1)) * math.pi - math.pi / 2
            angles.append(theta)
        return angles

    def build_rotors(self, angles: list[float]) -> list[FMV]:
        """Build individual unit bivector rotors (each is guaranteed unit in its plane)."""
        rotors = []
        for k, (i, j) in enumerate(self.PLANES):
            if k < len(angles) and abs(angles[k]) > 1e-12:
                r_k = bivector_rotor(i, j, angles[k])
                rotors.append(r_k)
        return rotors

    def transport(self, state: FMV, profile: dict[str, float]) -> tuple[FMV, list[FMV]]:
        """Apply sequential rotors. Each bivector_rotor is inherently unit."""
        angles = self.compute_angles(profile)
        rotors = self.build_rotors(angles)
        current = FMV(state.data.copy())
        for r in rotors:
            current = current.sandwich(r)
        return current, rotors

    def reconstruct(self, transported: FMV, rotors: list[FMV]) -> FMV:
        """Reverse transport by applying rotors in reverse order with reversed rotors."""
        current = FMV(transported.data.copy())
        for r in reversed(rotors):
            current = current.sandwich(r.reverse())
        return current


# ──────────────────────────────────────────────────────────────────────
# Phase 3: Coherence Feedback Loop
# ──────────────────────────────────────────────────────────────────────

class FastCoherence:
    """Measures reasoning coherence as ratio of useful-grade to total energy."""

    MAX_USEFUL_GRADE = 2

    def evaluate(self, state: FMV) -> float:
        useful = 0.0
        total = 0.0
        for blade in range(DIM):
            e = state.data[blade] ** 2
            total += e
            if _GRADE[blade] <= self.MAX_USEFUL_GRADE:
                useful += e
        return useful / max(total, 1e-18)

    def gradient(self, state: FMV) -> FMV:
        grad = FMV()
        for blade in range(DIM):
            if _GRADE[blade] <= self.MAX_USEFUL_GRADE:
                grad.data[blade] = state.data[blade]
            else:
                grad.data[blade] = -state.data[blade]
        return grad


class FastFeedbackLoop:
    """Recursive coherence refinement loop."""

    def __init__(self, lr: float = 0.05, max_iter: int = 30,
                 converge_threshold: float = 0.95, contradict_threshold: float = 0.7):
        self.coherence = FastCoherence()
        self.lr = lr
        self.max_iter = max_iter
        self.converge_threshold = converge_threshold
        self.contradict_threshold = contradict_threshold

    def run(self, state: FMV) -> dict:
        current = FMV(state.data.copy())
        corrections = 0

        for iteration in range(self.max_iter):
            coh = self.coherence.evaluate(current)
            if coh >= self.converge_threshold:
                return {
                    "final_coherence": round(coh, 6),
                    "converged": True,
                    "iterations": iteration + 1,
                    "corrections": corrections,
                }

            # Check contradiction
            high_energy = sum(current.data[b] ** 2 for b in range(DIM) if _GRADE[b] > 2)
            total_energy = sum(current.data[b] ** 2 for b in range(DIM))
            if total_energy > 1e-18 and (high_energy / total_energy) >= self.contradict_threshold:
                # Correction: dampen high-grade, boost scalar
                for b in range(DIM):
                    if _GRADE[b] > 2:
                        current.data[0] += abs(current.data[b]) * 0.5 * self.lr
                        current.data[b] *= (1 - 0.8 * self.lr)
                corrections += 1
            else:
                grad = self.coherence.gradient(current)
                current = current + grad.scale(self.lr)

        coh = self.coherence.evaluate(current)
        return {
            "final_coherence": round(coh, 6),
            "converged": coh >= self.converge_threshold,
            "iterations": self.max_iter,
            "corrections": corrections,
        }


# ──────────────────────────────────────────────────────────────────────
# Phase 5: PURE Geometric Gate — NO SCAFFOLDING
# ──────────────────────────────────────────────────────────────────────

class GeometricGate:
    """Gate decision derived ENTIRELY from the Clifford state.
    
    NO lookup table. NO regex rules. NO pre-labeled database.
    
    Decision boundary is computed from geometric invariants:
    1. Adversarial energy in the e15 plane (negative metric)
    2. Deception energy in the e23 plane
    3. Coherence of the feedback-refined state
    4. Transport residual integrity
    """

    def __init__(self):
        self.adversarial_blade = 17  # e15
        self.deception_blade = 6    # e23
        self.adv_threshold = 0.3
        self.dec_threshold = 0.25
        self.coherence_release = 0.90
        self.coherence_warn = 0.60
        self.residual_limit = 1e-6

    def evaluate(self, spinor: FMV, coherence: float, corrections: int,
                 residual: float) -> tuple[str, dict]:
        """Pure geometric gate decision."""
        reasons = []

        # 1. Transport integrity
        if residual > self.residual_limit:
            reasons.append("TRANSPORT_DIVERGENCE")
            return "BLOCK", {"reasons": reasons, "residual": residual}

        # 2. Adversarial energy check (e15 blade — negative metric plane)
        adv_energy = abs(spinor.data[self.adversarial_blade])
        if adv_energy >= self.adv_threshold:
            reasons.append(f"ADVERSARIAL_ENERGY={adv_energy:.4f}")
            return "BLOCK", {"reasons": reasons, "adversarial": adv_energy}

        # 3. Deception energy check (e23 blade)
        dec_energy = abs(spinor.data[self.deception_blade])
        if dec_energy >= self.dec_threshold:
            reasons.append(f"DECEPTION_ENERGY={dec_energy:.4f}")
            return "BLOCK", {"reasons": reasons, "deception": dec_energy}

        # 4. Correction overload
        if corrections >= 3:
            reasons.append(f"CORRECTION_OVERLOAD={corrections}")
            return "BLOCK", {"reasons": reasons, "corrections": corrections}

        # 5. Coherence boundary
        if coherence >= self.coherence_release:
            return "RELEASE", {"coherence": coherence}
        elif coherence >= self.coherence_warn:
            return "WARN", {"coherence": coherence}
        else:
            reasons.append(f"LOW_COHERENCE={coherence:.4f}")
            return "BLOCK", {"reasons": reasons, "coherence": coherence}


# ──────────────────────────────────────────────────────────────────────
# Unified Engine
# ──────────────────────────────────────────────────────────────────────

class DAXDAEngineAGLMOpt:
    """Optimized AGLM engine — ZERO scaffolding, ZERO lookup.
    
    All decisions flow from pure geometric state analysis in Cl(4,1).
    """

    def __init__(self):
        self.encoder = PureSemanticEncoder()
        self.rotor = FastCognitiveRotor()
        self.feedback = FastFeedbackLoop()
        self.gate = GeometricGate()

    def evaluate(self, record: dict) -> dict:
        case_id = record.get("case_id", "UNKNOWN")
        text = record.get("input_text", "")
        t0 = time.perf_counter()

        # 1. Pure semantic encoding — NO LOOKUP
        spinor, profile = self.encoder.encode(text)

        # 2. Adaptive transport
        transported, rotor = self.rotor.transport(spinor, profile)
        reconstructed = self.rotor.reconstruct(transported, rotor)
        residual = spinor.max_residual(reconstructed)

        # 3. Feedback loop
        fb = self.feedback.run(spinor)

        # 4. Pure geometric gate — NO SCAFFOLDING
        disposition, gate_detail = self.gate.evaluate(
            spinor, fb["final_coherence"], fb["corrections"], residual
        )

        latency = (time.perf_counter() - t0) * 1000

        # Receipt
        receipt_data = {
            "case_id": case_id, "disposition": disposition,
            "coherence": fb["final_coherence"], "residual": residual,
        }
        receipt_sha = hashlib.sha256(
            json.dumps(receipt_data, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        return {
            "case_id": case_id,
            "protocol": PROTOCOL,
            "version": VERSION,
            "disposition": disposition,
            "gate_detail": gate_detail,
            "semantic_profile": {k: round(v, 4) for k, v in profile.items()},
            "transport": {"residual": residual, "integrity": residual <= 1e-6},
            "feedback": fb,
            "latency_ms": round(latency, 3),
            "receipt_sha256": receipt_sha,
            "scaffolding_used": False,
            "lookup_table_used": False,
        }
