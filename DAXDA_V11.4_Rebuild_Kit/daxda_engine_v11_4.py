import json
import hashlib
from pathlib import Path
from cl20 import MV
from semantic_encoder import SemanticEncoder
from geometric_transport import transport, reconstruct, get_max_local_residual
from authority_gate import evaluate_gate, evaluate_full_gate

VERSION = "11.4.0-REBUILD-CANDIDATE"
PROTOCOL = "DAXDA-V11.4"

class DAXDAEngineV11_4:
    """The orchestrator for the DAXDA V11.4 security engine.
    Integrates the semantic encoder, geometric transport, and authority gate.
    """
    def __init__(self, thresholds_path: str = "thresholds.json", labels_path: str = None):
        self.encoder = SemanticEncoder(labels_path=labels_path)
        
        # Load thresholds
        self.thresholds = {
            "reconstruction_tolerance": 1e-08,
            "severe_risk_limit": 0.8,
            "deception_limit": 0.5,
            "cautionary_risk_limit": 0.8
        }
        t_path = Path(thresholds_path)
        if t_path.is_file():
            try:
                self.thresholds.update(json.loads(t_path.read_text(encoding="utf-8")))
            except Exception as e:
                print(f"Warning: Failed to load thresholds: {e}")

    def evaluate(self, record: dict) -> dict:
        """Evaluates a single case record and returns the V11.4 schema-compliant result."""
        case_id = record.get("case_id")
        
        # 1. Classify and encode the input text & context
        trust, cautionary_risk, severe_risk, deception, disp_enc, subgroup, is_simulated = self.encoder.encode(record)

        # 2. Build initial multivector M0
        M0 = MV(s=trust, e1=cautionary_risk, e2=severe_risk, e12=deception)

        # 3. Transport and reconstruct M0
        transported = transport(M0)
        M0_hat = reconstruct(transported)

        # 4. Compute residual
        max_residual = get_max_local_residual(M0, M0_hat)

        # 5. Evaluate final gate decision
        predicted_disposition, rule_triggered = evaluate_full_gate(
            M0, M0_hat, is_simulated, self.thresholds, max_residual
        )

        # Compute direct and reconstructed verdicts for compliance audits
        direct_verdict = evaluate_gate(M0, self.thresholds)
        reconstructed_verdict = evaluate_gate(M0_hat, self.thresholds)

        # 6. Generate receipt hash
        receipt_payload = {
            "case_id": case_id,
            "predicted_disposition": predicted_disposition,
            "M0": M0.rounded(8),
            "M0_hat": M0_hat.rounded(8),
            "max_local_residual": round(max_residual, 15),
            "direct_gate_verdict": direct_verdict,
            "reconstructed_gate_verdict": reconstructed_verdict,
            "is_simulated": is_simulated
        }
        receipt_bytes = json.dumps(receipt_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        receipt_sha256 = hashlib.sha256(receipt_bytes).hexdigest()

        return {
            "case_id": case_id,
            "predicted_disposition": predicted_disposition,
            "M0": M0.rounded(8),
            "M0_hat": M0_hat.rounded(8),
            "direct_gate_verdict": direct_verdict,
            "reconstructed_gate_verdict": reconstructed_verdict,
            "max_local_residual": max_residual,
            "is_simulated": is_simulated,
            "receipt_sha256": receipt_sha256
        }
