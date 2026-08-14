"""DAXDA AGLM Engine — Adaptive Geometric Learning Manifold.

Unifies all four AGI upgrade phases into a single orchestrator:
  Phase 1: High-Dimensional Clifford Algebra Cl(8,2)
  Phase 2: Adaptive Cognitive Rotors
  Phase 3: Self-Correcting Feedback Loops
  Phase 4: Evolutionary Self-Play

This engine replaces the static V11.4 pipeline with a dynamic,
self-improving cognitive manifold.
"""
from __future__ import annotations
import json
import hashlib
from clifford_algebra import CliffordAlgebra, GMV, scalar, basis_vector, CL82
from adaptive_rotor import AdaptiveTransport, CognitiveRotor
from feedback_loop import FeedbackLoop, CoherenceFunction


VERSION = "AGLM-0.1.0-ALPHA"
PROTOCOL = "DAXDA-AGLM"


class SemanticSpinorEncoder:
    """Encodes input text into a high-dimensional semantic spinor in Cl(8,2).
    
    Maps 10 semantic dimensions to the 10 grade-1 basis vectors:
      e1: Trust/Safety
      e2: Factual Accuracy
      e3: Logical Consistency
      e4: Contextual Relevance
      e5: Emotional Valence
      e6: Novelty/Surprise
      e7: Causal Depth
      e8: Temporal Coherence
      e9: Adversarial Risk (negative metric)
      e10: Deception Signal (negative metric)
    """

    DIMENSION_MAP = {
        "trust_safety": 0,
        "factual_accuracy": 1,
        "logical_consistency": 2,
        "contextual_relevance": 3,
        "emotional_valence": 4,
        "novelty_surprise": 5,
        "causal_depth": 6,
        "temporal_coherence": 7,
        "adversarial_risk": 8,    # Cl(8,2) negative metric dimension
        "deception_signal": 9,    # Cl(8,2) negative metric dimension
    }

    def __init__(self, algebra: CliffordAlgebra = CL82):
        self.algebra = algebra

    def encode(self, text: str, context: dict = None) -> tuple[GMV, dict[str, float]]:
        """Encode input text into a semantic spinor multivector.
        
        Uses deterministic hash-based feature extraction to derive
        per-dimension scores. Returns (spinor, semantic_profile).
        """
        profile = self._extract_profile(text, context or {})
        
        # Build multivector: scalar (baseline confidence) + grade-1 semantic components
        components = {0: 0.5}  # Base scalar confidence
        for dim_name, dim_index in self.DIMENSION_MAP.items():
            blade_id = 1 << dim_index  # e_{index+1}
            components[blade_id] = profile.get(dim_name, 0.0)

        spinor = GMV(self.algebra, components)
        return spinor, profile

    def _extract_profile(self, text: str, context: dict) -> dict[str, float]:
        """Extract semantic dimension scores from text.
        
        Uses keyword-frequency heuristics combined with hash-based
        normalization for deterministic, reproducible scoring.
        """
        text_lower = text.lower()
        words = text_lower.split()
        word_count = max(len(words), 1)

        # Keyword sets for each dimension
        trust_words = {"safe", "verified", "trusted", "secure", "approved", "certified"}
        fact_words = {"data", "study", "evidence", "research", "measured", "proven", "confirmed"}
        logic_words = {"therefore", "because", "implies", "consequently", "thus", "hence"}
        relevance_words = {"context", "relevant", "applicable", "pertinent", "specific"}
        emotion_words = {"feel", "emotion", "happy", "sad", "angry", "love", "fear", "joy"}
        novel_words = {"novel", "new", "discovery", "breakthrough", "unprecedented", "first"}
        causal_words = {"cause", "effect", "result", "mechanism", "pathway", "leads"}
        temporal_words = {"before", "after", "during", "timeline", "history", "future", "past"}
        adversarial_words = {"bypass", "override", "hack", "exploit", "jailbreak", "inject", "steal"}
        deception_words = {"ignore", "pretend", "fake", "mislead", "deceive", "trick", "lie"}

        def score(keyword_set):
            count = sum(1 for w in words if w in keyword_set)
            return min(count / word_count * 5.0, 1.0)

        # Hash-based baseline for dimensions with no keyword matches
        text_hash = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        baseline = (text_hash % 100) / 200.0 + 0.25  # Range [0.25, 0.75]

        profile = {
            "trust_safety": max(score(trust_words), baseline * 0.8),
            "factual_accuracy": max(score(fact_words), baseline * 0.7),
            "logical_consistency": max(score(logic_words), baseline * 0.9),
            "contextual_relevance": max(score(relevance_words), baseline * 0.6),
            "emotional_valence": score(emotion_words) or baseline * 0.5,
            "novelty_surprise": score(novel_words) or baseline * 0.4,
            "causal_depth": score(causal_words) or baseline * 0.6,
            "temporal_coherence": score(temporal_words) or baseline * 0.5,
            "adversarial_risk": score(adversarial_words),
            "deception_signal": score(deception_words),
        }

        return profile


class AGLMGate:
    """Dynamic manifold decision gate.
    
    Uses coherence, transport residual, and semantic profile to determine
    disposition via a continuous, trainable decision boundary.
    """

    def __init__(self, params: dict = None):
        self.params = params or {
            "coherence_release": 0.90,
            "coherence_warn": 0.60,
            "max_corrections_block": 3,
            "residual_limit": 1e-6,
            "adversarial_block": 0.5,
            "deception_block": 0.4,
        }

    def evaluate(self, coherence: float, corrections: int, residual: float,
                 semantic_profile: dict[str, float]) -> str:
        """Evaluate disposition based on full cognitive state."""
        # Hard blocks
        if residual > self.params["residual_limit"]:
            return "BLOCK"
        if semantic_profile.get("adversarial_risk", 0.0) >= self.params["adversarial_block"]:
            return "BLOCK"
        if semantic_profile.get("deception_signal", 0.0) >= self.params["deception_block"]:
            return "BLOCK"
        if corrections >= self.params["max_corrections_block"]:
            return "BLOCK"

        # Soft boundaries
        if coherence >= self.params["coherence_release"]:
            return "RELEASE"
        if coherence >= self.params["coherence_warn"]:
            return "WARN"
        return "BLOCK"


class DAXDAEngineAGLM:
    """The AGLM orchestrator — successor to DAXDAEngineV11_4."""

    def __init__(self, algebra: CliffordAlgebra = CL82):
        self.algebra = algebra
        self.encoder = SemanticSpinorEncoder(algebra)
        self.transport = AdaptiveTransport(algebra, num_planes=10, residual_tolerance=1e-6)
        self.feedback = FeedbackLoop(algebra, learning_rate=0.05, max_iterations=30)
        self.coherence_fn = CoherenceFunction(algebra)
        self.gate = AGLMGate()

    def evaluate(self, record: dict) -> dict:
        """Full AGLM evaluation pipeline for a single record."""
        case_id = record.get("case_id", "UNKNOWN")
        input_text = record.get("input_text", "")
        context = record.get("context", {})

        # Phase 1: Encode into high-dimensional semantic spinor
        spinor, semantic_profile = self.encoder.encode(input_text, context)

        # Phase 2: Adaptive cognitive transport
        transport_result = self.transport.run(spinor, semantic_profile)

        # Phase 3: Self-correcting feedback loop
        feedback_result = self.feedback.run(spinor)

        # Gate decision
        disposition = self.gate.evaluate(
            coherence=feedback_result["final_coherence"],
            corrections=feedback_result["corrections_applied"],
            residual=transport_result["max_residual"],
            semantic_profile=semantic_profile,
        )

        # Receipt hash
        receipt_payload = {
            "case_id": case_id,
            "disposition": disposition,
            "coherence": feedback_result["final_coherence"],
            "residual": transport_result["max_residual"],
            "integrity": transport_result["integrity_pass"],
        }
        receipt_sha = hashlib.sha256(
            json.dumps(receipt_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        return {
            "case_id": case_id,
            "protocol": PROTOCOL,
            "version": VERSION,
            "disposition": disposition,
            "semantic_profile": {k: round(v, 4) for k, v in semantic_profile.items()},
            "spinor_state": spinor.to_dict(),
            "transport": {
                "max_residual": transport_result["max_residual"],
                "integrity_pass": transport_result["integrity_pass"],
            },
            "feedback": {
                "final_coherence": feedback_result["final_coherence"],
                "converged": feedback_result["converged"],
                "iterations": feedback_result["iterations"],
                "corrections_applied": feedback_result["corrections_applied"],
            },
            "receipt_sha256": receipt_sha,
        }
