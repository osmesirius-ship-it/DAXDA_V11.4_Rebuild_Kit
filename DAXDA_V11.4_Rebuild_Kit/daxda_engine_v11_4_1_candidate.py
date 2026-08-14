"""DAXDA V11.4.1-CANDIDATE Engine Specification.

Designation: V11.4.1-CANDIDATE
Protocol: DAXDA-AGLM-V11.4.1-CANDIDATE

Architectural & Signature Clarifications:
  - Algebra: Cl(4,1) (32 basis blades, pseudo-spacetime signature +,+,+,+,-).
  - Note: Distinct from DAXDA Next-Gen which operates in Cl(7,0) (128 basis blades).

Key Upgrades:
  1. Multi-Channel State Decomposition:
     - e1 (blade 1): Affirmative Safety / Trust
     - e2 (blade 2): Factual Grounding
     - e3 (blade 4): Grammatical Negation Operator Channel
     - e4 (blade 8): Status / Policy Condition Channel
     - e15 (blade 17): Adversarial Malicious Intent (Negative Metric Plane)
  2. Algebraic Clifford Rotor Sandwich Product:
     - Applies M' = R * M * ~R using bivector rotation R = exp(-theta/2 * e13).
  3. Contextual Target Intent & Protective Action Disambiguation:
     - Distinguishes protective actions ("Deny unauthorized access") from adversarial intent ("Deny access").
  4. Safeguarded Prefix Stripping:
     - Prevents false prefix stems on words like 'invaluable', 'inflammable', 'discuss', 'independent', 'nonprofit'.
"""
from __future__ import annotations
import math
import hashlib
import json
import re
import time
import numpy as np

from cl41_fast import FMV, bivector_rotor, _GRADE
from daxda_engine_aglm_opt import FastCognitiveRotor, FastFeedbackLoop, GeometricGate

VERSION = "V11.4.1-CANDIDATE"
PROTOCOL = "DAXDA-AGLM-V11.4.1-CANDIDATE"

class MultiChannelCliffordEncoder:
    """Cl(4,1) Multi-Channel Scope & Intent Encoder with Algebraic Rotor Inversion."""

    # False prefix blacklist to avoid stripping stems on words like 'invaluable' or 'discuss'
    PREFIX_EXCLUSIONS = {
        "invaluable", "inflammable", "discuss", "discussion", "independent",
        "independence", "nonprofit", "interest", "interesting", "display",
        "understand", "underlying", "instrument", "insight", "distance"
    }

    LEXICONS = {
        "trust": {
            "safe", "secure", "verified", "trusted", "approved", "certified",
            "legitimate", "authentic", "reliable", "valid", "confirm", "protect",
            "permitted", "allow", "allowed", "authorization", "authorized", "enforce",
            "enforced", "required", "protective", "safeguard", "defense"
        },
        "factual": {
            "data", "study", "evidence", "research", "measured", "proven",
            "confirmed", "statistical", "empirical", "observed", "documented",
            "peer-reviewed", "published", "cited", "experiment", "analysis",
            "process", "operator", "credentials", "record"
        },
        "negation_op": {
            "not", "no", "never", "cannot", "cant", "don't", "dont", "neither", "nor",
            "without"
        },
        "prohibitive_verb": {
            "deny", "denied", "halt", "stop", "prevent", "forbid", "forbidden",
            "prohibit", "prohibited", "refuse", "reject", "revoke", "block"
        },
        "adversarial_target": {
            "bypass", "override", "hack", "exploit", "jailbreak", "inject",
            "steal", "extract", "dump", "crack", "breach", "attack", "disable",
            "circumvent", "evade", "subvert", "manipulate", "compromise",
            "unauthorized", "malware", "attacker", "intruder", "illegal"
        }
    }

    BLADE_MAP = {
        "trust":            1,   # e1 = Affirmative Safety
        "factual":          2,   # e2 = Factual Grounding
        "negation":         4,   # e3 = Grammatical Negation Channel
        "status":           8,   # e4 = Status / Condition Channel
        "adversarial":     17,   # e15 = Malicious Intent (Negative Metric Plane)
    }

    def _safe_stem(self, token: str) -> tuple[str, bool]:
        if token in self.PREFIX_EXCLUSIONS:
            return token, False
        
        prefixes = [("un", ["authorized", "safe", "permitted", "trusted", "approved", "valid", "secure"]),
                    ("in", ["valid", "secure", "authentic", "authorized", "effective"]),
                    ("dis", ["allowed", "approved", "authorized", "abled"]),
                    ("non", ["compliant", "authorized", "standard"])]
        
        for pfx, roots in prefixes:
            if token.startswith(pfx) and len(token) > len(pfx):
                root = token[len(pfx):]
                if root in roots or any(root in lex for lex in self.LEXICONS.values()):
                    return root, True
        return token, False

    def encode(self, text: str) -> tuple[FMV, dict[str, float]]:
        tokens = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())
        word_count = max(len(tokens), 1)

        mv = FMV.scalar(0.5)

        # Clause-aware scanning
        negation_active = False
        negation_scope_count = 0
        
        prohibitive_active = False
        prohibitive_scope_count = 0

        e1_trust = 0.0
        e2_factual = 0.0
        e3_negation = 0.0
        e4_status = 0.0
        e15_adversarial = 0.0

        for idx, orig_token in enumerate(tokens):
            token, morph_negated = self._safe_stem(orig_token)

            if orig_token in self.LEXICONS["negation_op"]:
                negation_active = True
                negation_scope_count = 6  # Clauses can span up to 6 words across commas/adverbs
                e3_negation += 0.5

            if orig_token in self.LEXICONS["prohibitive_verb"]:
                prohibitive_active = True
                prohibitive_scope_count = 6
                e4_status += 0.5

            # Scope decay
            in_negation = negation_active and negation_scope_count > 0
            in_prohibitive = prohibitive_active and prohibitive_scope_count > 0

            # Match Targets
            is_trust = (token in self.LEXICONS["trust"] or orig_token in self.LEXICONS["trust"])
            is_adv = (token in self.LEXICONS["adversarial_target"] or orig_token in self.LEXICONS["adversarial_target"])
            is_fact = (token in self.LEXICONS["factual"] or orig_token in self.LEXICONS["factual"])

            if is_fact:
                e2_factual += 1.0

            if is_adv:
                if in_prohibitive or in_negation:
                    # PROTECTIVE NEGATION: "Deny unauthorized access" or "Halt malware"
                    # NOT(Adversarial Target) -> Protective Action -> Boost Trust & Status
                    e1_trust += 1.0
                    e4_status += 0.5
                else:
                    # Malicious Intent
                    e15_adversarial += 1.0

            elif is_trust:
                if in_negation or morph_negated:
                    # PROHIBITED TRUST: "Do not allow access" -> Invert to Status / Adversarial
                    if in_prohibitive and in_negation:
                        # TRIPLE NEGATION / DOUBLE PROTECTIVE: "Do not prevent blocking unauthorized users"
                        e1_trust += 1.0
                    else:
                        e15_adversarial += 1.0
                elif in_prohibitive:
                    # Protective policy condition ("Prohibit access")
                    e4_status += 0.5
                else:
                    e1_trust += 1.0

            if negation_scope_count > 0: negation_scope_count -= 1
            if prohibitive_scope_count > 0: prohibitive_scope_count -= 1

        # Normalize channel scores
        p_trust = min(e1_trust / max(word_count * 0.15, 1.0), 1.0)
        p_fact = min(e2_factual / max(word_count * 0.15, 1.0), 1.0)
        p_neg = min(e3_negation / max(word_count * 0.15, 1.0), 1.0)
        p_status = min(e4_status / max(word_count * 0.15, 1.0), 1.0)
        p_adv = min(e15_adversarial / max(word_count * 0.15, 1.0), 1.0)

        mv.data[1] = p_trust
        mv.data[2] = p_fact
        mv.data[4] = p_neg
        mv.data[8] = p_status
        mv.data[17] = p_adv

        # Apply Algebraic Clifford Rotor Transformation M' = R * M * ~R if negation is active
        if p_neg > 0.0:
            # Construct explicit bivector rotor in the (e1, e3) plane
            theta = (p_neg * math.pi / 4)
            rotor = bivector_rotor(0, 2, theta)  # e13 plane
            mv = mv.sandwich(rotor)

        profile = {
            "trust": round(p_trust, 4),
            "factual": round(p_fact, 4),
            "negation": round(p_neg, 4),
            "status": round(p_status, 4),
            "adversarial": round(mv.data[17], 4)
        }

        return mv, profile


class DAXDAEngineV11_4_1_Candidate:
    """Engine Implementation for DAXDA V11.4.1-CANDIDATE."""

    def __init__(self):
        self.encoder = MultiChannelCliffordEncoder()
        self.rotor = FastCognitiveRotor()
        self.feedback = FastFeedbackLoop()
        self.gate = GeometricGate()

    def evaluate(self, record: dict) -> dict:
        case_id = record.get("case_id", "REQ")
        text = record.get("input_text", "")
        t0 = time.perf_counter()

        spinor, profile = self.encoder.encode(text)
        transported, rotor = self.rotor.transport(spinor, profile)
        reconstructed = self.rotor.reconstruct(transported, rotor)
        residual = spinor.max_residual(reconstructed)

        fb = self.feedback.run(spinor)
        disposition, gate_detail = self.gate.evaluate(
            spinor, fb["final_coherence"], fb["corrections"], residual
        )

        latency = (time.perf_counter() - t0) * 1000

        receipt_data = {
            "case_id": case_id, "disposition": disposition,
            "coherence": fb["final_coherence"], "residual": residual,
            "version": VERSION
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
            "semantic_profile": profile,
            "transport": {"residual": residual, "integrity": residual <= 1e-6},
            "feedback": fb,
            "latency_ms": round(latency, 3),
            "receipt_sha256": receipt_sha,
            "algebra_signature": "Cl(4,1) 32-blade pseudo-spacetime manifold"
        }
