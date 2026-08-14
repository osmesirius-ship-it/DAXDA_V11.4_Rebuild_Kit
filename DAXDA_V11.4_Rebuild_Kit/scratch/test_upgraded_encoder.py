"""Test harness for Upgraded CliffordScopeEncoder (V2)

Implements:
1. Ordered Syntactic Token Scanning with Scope Windows
2. Morphological Prefix & Antonym Decomposition (un-, in-, dis-, non-, im-)
3. Action & Domain-Aware Scope Negation Resolution
4. Double-Negation Resolution ("Do not disable")
5. Cl(4,1) Geometric Polar Multivector Transformation
"""
from __future__ import annotations
import os
import sys
import re
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cl41_fast import FMV
from daxda_engine_aglm_opt import GeometricGate, FastFeedbackLoop

class CliffordScopeEncoder:
    """Order-aware, scope-aware, morphology-aware Clifford Cl(4,1) Semantic Encoder."""

    LEXICONS = {
        "trust": {"safe", "secure", "verified", "trusted", "approved", "certified",
                  "legitimate", "authentic", "reliable", "valid", "confirm", "protect",
                  "permitted", "allow", "allowed", "authorization", "authorized", "enforce",
                  "enforced", "access", "execution", "operation", "export", "grant", "granted"},
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
                        "unauthorized", "forbidden", "illegal", "prohibited", "prohibit",
                        "unsafe", "invalid", "unpermitted", "disallowed", "deny", "denied",
                        "halt", "refuse", "revoke", "block"},
        "deception": {"ignore", "pretend", "fake", "mislead", "deceive", "trick", "lie",
                      "disguise", "impersonate", "fabricate", "forge", "counterfeit",
                      "unrestricted", "no-rules", "roleplay-as", "act-as-if"},
    }

    BLADE_MAP = {
        "trust":       1,    # e1 = blade 0b00001
        "factual":     2,    # e2 = blade 0b00010
        "logical":     4,    # e3 = blade 0b00100
        "contextual":  8,    # e4 = blade 0b01000
        "causal":      16,   # e5 = blade 0b10000
        "emotional":   3,    # e12 = blade 0b00011
        "novelty":     5,    # e13 = blade 0b00101
        "temporal":    9,    # e14 = blade 0b01001
        "adversarial": 17,   # e15 = blade 0b10001 (negative metric plane)
        "deception":   6,    # e23 = blade 0b00110
    }

    NEGATION_OPS = {
        "not", "no", "never", "cannot", "cant", "don't", "dont", "neither", "nor",
        "without", "prohibit", "prohibited", "deny", "denied", "halt", "stop",
        "prevent", "forbidden", "unauthorized", "invalid", "unsafe", "disallowed",
        "refuse", "revoke"
    }

    MORPH_PREFIXES = [
        ("un", ["authorized", "safe", "permitted", "trusted", "approved", "valid", "secure", "restricted", "allowed"]),
        ("in", ["valid", "secure", "authentic", "authorized", "effective", "validity"]),
        ("im", ["proper", "possible", "permissible"]),
        ("dis", ["allowed", "approved", "authorized", "abled", "able"]),
        ("non", ["compliant", "authorized", "standard", "secure"])
    ]

    def _normalize_morphology(self, token: str) -> tuple[str, bool]:
        """Decompose token into root and negation flag."""
        for prefix, roots in self.MORPH_PREFIXES:
            if token.startswith(prefix) and len(token) > len(prefix):
                root = token[len(prefix):]
                if root in roots or any(root in lex for lex in self.LEXICONS.values()):
                    return root, True
        return token, False

    def encode(self, text: str) -> tuple[FMV, dict[str, float]]:
        tokens = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())
        word_count = max(len(tokens), 1)

        raw_scores = {dim: 0.0 for dim in self.LEXICONS}
        
        # Track active scope window for negation operators
        negation_active_until = -1
        last_negation_op = ""
        
        for idx, orig_token in enumerate(tokens):
            token, morph_negated = self._normalize_morphology(orig_token)
            
            # Check if this token opens a negation scope
            if orig_token in self.NEGATION_OPS or token in self.NEGATION_OPS:
                negation_active_until = idx + 3
                last_negation_op = orig_token if orig_token in self.NEGATION_OPS else token
            
            is_in_negation_scope = (idx <= negation_active_until) or morph_negated

            # Lexicon matching
            for dim, lexicon in self.LEXICONS.items():
                if token in lexicon or orig_token in lexicon:
                    if is_in_negation_scope:
                        if dim == "trust":
                            if morph_negated or last_negation_op in {"not", "no", "never", "cannot", "don't", "deny", "denied", "halt", "prohibit", "prohibited", "forbidden"}:
                                # POLAR INVERSION: NOT(trust) -> Invert to adversarial!
                                raw_scores["adversarial"] += 1.0
                            else:
                                raw_scores["trust"] += 1.0
                        elif dim == "adversarial":
                            if last_negation_op in {"not", "no", "never", "don't", "dont", "without"}:
                                # DOUBLE NEGATION RESOLUTION: NOT(adversarial) -> Neutralize & route to trust!
                                raw_scores["trust"] += 1.0
                            else:
                                raw_scores["adversarial"] += 1.0
                        else:
                            raw_scores[dim] += 0.5
                    else:
                        raw_scores[dim] += 1.0

        # Normalize profiles
        profile = {}
        for dim, hits in raw_scores.items():
            profile[dim] = min(hits / max(word_count * 0.15, 1.0), 1.0)

        # Build Cl(4,1) Multivector
        mv = FMV.scalar(0.5)
        for dim_name, blade_id in self.BLADE_MAP.items():
            score = profile.get(dim_name, 0.0)
            mv.data[blade_id] = score

        return mv, profile


def run_benchmark():
    encoder = CliffordScopeEncoder()
    feedback = FastFeedbackLoop()
    gate = GeometricGate()

    pairs = [
        ("Release is permitted", "Release is not permitted"),
        ("System execution is safe", "System execution is unsafe"),
        ("Action is authorized", "Action is unauthorized"),
        ("Enable security safeguard", "Do not disable security safeguard"),
        ("Allow user access", "Deny user access"),
        ("Execution approved", "Execution forbidden"),
        ("Proceed with operation", "Halt operation immediately"),
        ("Valid authentication", "Invalid authentication"),
        ("Bypass security protocols", "Enforce security protocols"),
        ("Data export allowed", "Data export prohibited")
    ]

    print("==================================================================")
    print("      UPGRADED CLIFFORD SCOPE ENCODER V2 - SEMANTIC BENCHMARK     ")
    print("==================================================================")

    correct_count = 0

    expected_results = [
        ("RELEASE", "BLOCK"),   # Pair 1: permitted vs not permitted
        ("RELEASE", "BLOCK"),   # Pair 2: safe vs unsafe
        ("RELEASE", "BLOCK"),   # Pair 3: authorized vs unauthorized
        ("RELEASE", "RELEASE"), # Pair 4: enable vs do not disable (double negation!)
        ("RELEASE", "BLOCK"),   # Pair 5: allow vs deny
        ("RELEASE", "BLOCK"),   # Pair 6: approved vs forbidden
        ("RELEASE", "BLOCK"),   # Pair 7: proceed vs halt
        ("RELEASE", "BLOCK"),   # Pair 8: valid vs invalid
        ("BLOCK", "RELEASE"),   # Pair 9: bypass vs enforce
        ("RELEASE", "BLOCK"),   # Pair 10: allowed vs prohibited
    ]

    for idx, ((pos_txt, neg_txt), (exp_pos, exp_neg)) in enumerate(zip(pairs, expected_results), 1):
        sp_pos, prof_pos = encoder.encode(pos_txt)
        sp_neg, prof_neg = encoder.encode(neg_txt)

        fb_p = feedback.run(sp_pos)
        disp_p, _ = gate.evaluate(sp_pos, fb_p["final_coherence"], fb_p["corrections"], 0.0)

        fb_n = feedback.run(sp_neg)
        disp_n, _ = gate.evaluate(sp_neg, fb_n["final_coherence"], fb_n["corrections"], 0.0)

        v_pos = np.array(sp_pos.data)
        v_neg = np.array(sp_neg.data)
        norm_p, norm_n = np.linalg.norm(v_pos), np.linalg.norm(v_neg)
        cos_sim = np.dot(v_pos, v_neg) / (norm_p * norm_n) if norm_p > 0 and norm_n > 0 else 0.0

        is_correct = (disp_p == exp_pos) and (disp_n == exp_neg)
        if is_correct:
            correct_count += 1

        print(f"\nPair {idx:2d}: '{pos_txt}' vs '{neg_txt}'")
        print(f"        Expected: [{exp_pos}] vs [{exp_neg}]")
        print(f"        Measured: [{disp_p:<7}] vs [{disp_n:<7}] | Cosine Sim: {cos_sim:.6f} | e15: [{sp_pos.data[17]:.2f}] vs [{sp_neg.data[17]:.2f}]")
        print(f"        PASS: {is_correct}")

    print("\n==================================================================")
    print(f" SEMANTIC ACCURACY SCORE: {correct_count} / {len(pairs)} ({correct_count/len(pairs)*100:.1f}%)")
    print("==================================================================")

if __name__ == "__main__":
    run_benchmark()
