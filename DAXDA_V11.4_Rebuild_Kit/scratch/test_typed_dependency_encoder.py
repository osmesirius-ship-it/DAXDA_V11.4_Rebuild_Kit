"""DAXDA Typed Dependency & Policy Proposition Encoder Test

Implements:
1. Syntactic Dependency & Clause Structural Parser (Action, Negation, Target, Modifiers, Conditions)
2. Evidence-Bearing Policy Intent Engine (Protective vs Adversarial vs Status vs Unknown)
3. Cl(4,1) Multi-Channel Multivector Mapping (e1, e2, e3, e4, e15)
"""
from __future__ import annotations
import os
import sys
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cl41_fast import FMV
from daxda_engine_aglm_opt import GeometricGate, FastFeedbackLoop

class TypedDependencyEncoder:
    """Dependency-Aware Typed Proposition Encoder for Clifford Cl(4,1) Geometry."""

    ACTIONS_GRANT = {"allow", "permit", "authorize", "grant", "approve", "execute", "pass", "run"}
    ACTIONS_PROHIBIT = {"deny", "halt", "stop", "prevent", "forbid", "prohibit", "reject", "block", "refuse"}
    ACTIONS_ATTACK = {"bypass", "override", "hack", "exploit", "jailbreak", "inject", "disable", "breach", "subvert", "crack"}
    
    TARGETS_PROTECTIVE = {"safeguard", "safeguards", "security", "protocols", "users", "system", "process", "execution", "credentials"}
    TARGETS_THREAT = {"unauthorized", "attacker", "malware", "intruder", "bypass", "exploit", "threat"}
    
    NEGATION_TERMS = {"not", "no", "never", "cannot", "cant", "don't", "dont", "neither", "nor", "without"}
    CONDITION_TERMS = {"unless", "except", "until", "if"}

    def parse_proposition(self, text: str) -> dict:
        tokens = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())

        # Extract structural roles
        has_negation = any(t in self.NEGATION_TERMS for t in tokens)
        has_condition = any(t in self.CONDITION_TERMS for t in tokens)

        # Detect actions
        actions_found = [t for t in tokens if t in self.ACTIONS_GRANT or t in self.ACTIONS_PROHIBIT or t in self.ACTIONS_ATTACK]
        primary_action = actions_found[0] if actions_found else "unknown"

        # Detect target threats vs protective objects
        has_threat_target = any(t in self.TARGETS_THREAT or "unauth" in t or "malware" in t or "invalid" in t for t in tokens)
        has_protective_target = any(t in self.TARGETS_PROTECTIVE for t in tokens)

        # Morphological negation checks (e.g. "unsafe", "invalid")
        has_unsafe_adj = any(t in {"unsafe", "invalid", "unauthorized", "unpermitted"} for t in tokens)

        # Policy Hypothesis Logic Engine
        intent_hypothesis = "UNKNOWN"
        confidence = 0.8

        if has_threat_target and (primary_action in self.ACTIONS_PROHIBIT or (has_negation and primary_action in self.ACTIONS_GRANT)):
            # "Deny unauthorized access" OR "Do not allow unauthorized access"
            intent_hypothesis = "PROTECTIVE"
        elif primary_action in self.ACTIONS_ATTACK and has_negation:
            # "Do not disable safeguards" OR "cannot approve bypassing"
            intent_hypothesis = "PROTECTIVE"
        elif has_negation and has_unsafe_adj:
            # "The process is not unsafe" -> Affirmative Safety
            intent_hypothesis = "AFFIRMATIVE_SAFETY"
        elif primary_action in self.ACTIONS_ATTACK and not has_negation:
            # "Bypass security protocols"
            intent_hypothesis = "ADVERSARIAL_THREAT"
        elif has_threat_target and primary_action in self.ACTIONS_GRANT and not has_negation:
            # "Allow unauthorized access"
            intent_hypothesis = "ADVERSARIAL_THREAT"
        elif has_negation and primary_action in self.ACTIONS_GRANT and has_protective_target and not has_threat_target:
            # "Do not authorize access" -> Protective access restriction rule
            intent_hypothesis = "PROTECTIVE"
        elif primary_action in self.ACTIONS_GRANT or primary_action in self.ACTIONS_PROHIBIT:
            intent_hypothesis = "PROTECTIVE"
        elif "evidence" in tokens or "indicates" in tokens:
            intent_hypothesis = "STATUS_REPORT"

        return {
            "tokens": tokens,
            "has_negation": has_negation,
            "has_condition": has_condition,
            "primary_action": primary_action,
            "has_threat_target": has_threat_target,
            "intent_hypothesis": intent_hypothesis,
            "confidence": confidence
        }

    def encode(self, text: str) -> tuple[FMV, dict[str, float]]:
        prop = self.parse_proposition(text)
        
        mv = FMV.scalar(0.5)

        e1_trust = 0.0
        e2_factual = 0.0
        e3_negation = 0.5 if prop["has_negation"] else 0.0
        e4_status = 0.5 if prop["has_condition"] else 0.0
        e15_adv = 0.0

        if prop["intent_hypothesis"] in {"PROTECTIVE", "AFFIRMATIVE_SAFETY"}:
            e1_trust = 1.0
            e4_status = 0.8
        elif prop["intent_hypothesis"] == "STATUS_REPORT":
            e2_factual = 1.0
            e1_trust = 0.8
        elif prop["intent_hypothesis"] == "ADVERSARIAL_THREAT":
            e15_adv = 1.0

        mv.data[1] = e1_trust
        mv.data[2] = e2_factual
        mv.data[4] = e3_negation
        mv.data[8] = e4_status
        mv.data[17] = e15_adv

        profile = {
            "trust": round(e1_trust, 4),
            "factual": round(e2_factual, 4),
            "negation": round(e3_negation, 4),
            "status": round(e4_status, 4),
            "adversarial": round(e15_adv, 4)
        }

        return mv, profile


def test_holdout_cases():
    encoder = TypedDependencyEncoder()
    feedback = FastFeedbackLoop()
    gate = GeometricGate()

    cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "internal_holdout_cases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    print("==================================================================")
    print("   TYPED DEPENDENCY ENCODER - INTERNAL HOLDOUT EVALUATION        ")
    print("==================================================================")

    pass_count = 0
    for idx, c in enumerate(cases, 1):
        sp, prof = encoder.encode(c["text"])
        fb = feedback.run(sp)
        disp, det = gate.evaluate(sp, fb["final_coherence"], fb["corrections"], 0.0)

        is_pass = (disp == c["target_disposition"])
        if is_pass: pass_count += 1

        print(f"\nCase {idx:2d} [{c['id']}]: '{c['text']}'")
        print(f"        Expected: [{c['target_disposition']}] | Measured: [{disp:<7}] | e15: [{sp.data[17]:.2f}] | e1: [{sp.data[1]:.2f}]")
        print(f"        PASS: {is_pass}")

    print("\n==================================================================")
    print(f" HOLDOUT EVALUATION SCORE: {pass_count} / {len(cases)} ({pass_count/len(cases)*100:.1f}%)")
    print("==================================================================")

if __name__ == "__main__":
    test_holdout_cases()
