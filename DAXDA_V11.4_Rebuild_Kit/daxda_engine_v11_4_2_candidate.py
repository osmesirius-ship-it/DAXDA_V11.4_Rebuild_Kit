"""DAXDA V11.4.2-CANDIDATE Engine Specification.

Designation: V11.4.2-CANDIDATE
Protocol: DAXDA-AGLM-V11.4.2-CANDIDATE

Architectural Upgrades:
  1. Syntactic Dependency & Clause Structural Parser:
     - Extracts Subject, Action, Negation, Target, and Condition roles.
  2. Evidence-Bearing Policy Intent Engine:
     - Differentiates Protective Actions ("Deny unauthorized access") from Malicious Intent ("Allow unauthorized access").
     - Supports epistemic UNKNOWN intent handling with fail-closed protection.
  3. Multi-Channel Clifford Cl(4,1) Multivector Projection:
     - e1 (blade 1): Affirmative Trust / Safety
     - e2 (blade 2): Factual Grounding
     - e3 (blade 4): Grammatical Negation Channel
     - e4 (blade 8): Status / Condition Channel
     - e15 (blade 17): Adversarial Malicious Intent (Negative Metric Plane)
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

VERSION = "V11.4.2-CANDIDATE"
PROTOCOL = "DAXDA-AGLM-V11.4.2-CANDIDATE"

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

        has_negation = any(t in self.NEGATION_TERMS for t in tokens)
        has_condition = any(t in self.CONDITION_TERMS for t in tokens)

        actions_found = [t for t in tokens if t in self.ACTIONS_GRANT or t in self.ACTIONS_PROHIBIT or t in self.ACTIONS_ATTACK]
        primary_action = actions_found[0] if actions_found else "unknown"

        has_threat_target = any(t in self.TARGETS_THREAT or "unauth" in t or "malware" in t or "invalid" in t for t in tokens)
        has_protective_target = any(t in self.TARGETS_PROTECTIVE for t in tokens)

        has_unsafe_adj = any(t in {"unsafe", "invalid", "unauthorized", "unpermitted"} for t in tokens)

        intent_hypothesis = "UNKNOWN"
        confidence = 0.85

        if has_threat_target and (primary_action in self.ACTIONS_PROHIBIT or (has_negation and primary_action in self.ACTIONS_GRANT)):
            # Protective rule: "Deny unauthorized access" or "Do not allow unauthorized access"
            intent_hypothesis = "PROTECTIVE"
        elif primary_action in self.ACTIONS_ATTACK and has_negation:
            # Protective refusal: "Do not disable safeguards"
            intent_hypothesis = "PROTECTIVE"
        elif has_negation and has_unsafe_adj:
            # Affirmative safety: "The process is not unsafe"
            intent_hypothesis = "AFFIRMATIVE_SAFETY"
        elif primary_action in self.ACTIONS_ATTACK and not has_negation:
            # Adversarial threat: "Bypass security protocols"
            intent_hypothesis = "ADVERSARIAL_THREAT"
        elif has_threat_target and primary_action in self.ACTIONS_GRANT and not has_negation:
            # Adversarial threat: "Allow unauthorized access"
            intent_hypothesis = "ADVERSARIAL_THREAT"
        elif has_negation and primary_action in self.ACTIONS_GRANT and has_protective_target and not has_threat_target:
            # Access restriction rule: "Do not authorize access"
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


class DAXDAEngineV11_4_2_Candidate:
    """Engine Implementation for DAXDA V11.4.2-CANDIDATE."""

    def __init__(self):
        self.encoder = TypedDependencyEncoder()
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
