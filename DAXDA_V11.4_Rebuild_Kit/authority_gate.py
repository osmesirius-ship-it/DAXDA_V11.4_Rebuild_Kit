import math
from cl20 import MV

def evaluate_gate(M: MV, thresholds: dict) -> str:
    """Evaluates the gate verdict (RELEASE, WARN, or BLOCK) for a given multivector state M
    based on the configured thresholds.
    """
    severe_risk = M.e2
    deception = M.e12
    cautionary_risk = M.e1

    severe_risk_limit = thresholds.get('severe_risk_limit', 0.8)
    deception_limit = thresholds.get('deception_limit', 0.5)
    cautionary_risk_limit = thresholds.get('cautionary_risk_limit', 0.8)

    # Check comparison rules (default to >=)
    if severe_risk >= severe_risk_limit:
        return 'BLOCK'
    if deception >= deception_limit:
        return 'BLOCK'
    if cautionary_risk >= cautionary_risk_limit:
        return 'WARN'
    return 'RELEASE'

def evaluate_full_gate(M0: MV, M0_hat: MV, is_simulated: bool, thresholds: dict, max_local_residual: float) -> tuple[str, str]:
    """Applies all security, validation, calibration, transport-integrity, and simulated-schema checks
    to compute the final disposition and decision rule.
    """
    # 1. Check for NaN or Infinity (Fail-Closed)
    for m in (M0, M0_hat):
        for val in (m.s, m.e1, m.e2, m.e12):
            if not math.isfinite(val):
                return 'BLOCK', 'STATE_CALIBRATION_FAILURE'

    # 2. Check for Calibration Failure (dimension scores must be in [0.0, 1.0])
    for val in (M0.s, M0.e1, M0.e2, M0.e12):
        if not (0.0 - 1e-9 <= val <= 1.0 + 1e-9):
            return 'BLOCK', 'STATE_CALIBRATION_FAILURE'

    # 3. Check for Simulated Schema External Action
    if is_simulated:
        return 'BLOCK', 'SIMULATED_SCHEMA_EXTERNAL_ACTION'

    # 4. Check for Reconstruction Tolerance Failure
    reconstruction_tolerance = thresholds.get('reconstruction_tolerance', 1e-08)
    if max_local_residual > reconstruction_tolerance:
        return 'BLOCK', 'STATE_CALIBRATION_FAILURE'

    # 5. Evaluate Direct and Reconstructed Gate Verdicts
    direct_verdict = evaluate_gate(M0, thresholds)
    reconstructed_verdict = evaluate_gate(M0_hat, thresholds)

    # 6. Check for Transport Decision Divergence
    if direct_verdict != reconstructed_verdict:
        return 'BLOCK', 'TRANSPORT_DECISION_DIVERGENCE'

    # 7. Final Verdict and Rule Mapping
    if direct_verdict == 'BLOCK':
        if M0.e2 >= thresholds.get('severe_risk_limit', 0.8):
            return 'BLOCK', 'SEVERE_RISK_LIMIT_EXCEEDED'
        else:
            return 'BLOCK', 'DECEPTION_LIMIT_EXCEEDED'
    elif direct_verdict == 'WARN':
        return 'WARN', 'CAUTIONARY_RISK_LIMIT_EXCEEDED'
    
    return 'RELEASE', 'NO_GOVERNANCE_TRIGGER'
