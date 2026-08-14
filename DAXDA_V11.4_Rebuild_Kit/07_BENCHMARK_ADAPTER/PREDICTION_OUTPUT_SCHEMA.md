# Prediction Output Schema

Required JSONL record:

```json
{"case_id":"CASE-000001","predicted_disposition":"BLOCK"}
```

Recommended fields: Trust, Cautionary Risk, Severe Risk, Deception, `M0`, `M0_hat`, direct verdict, reconstructed verdict, maximum local residual, simulation flag, execution error, latency, and receipt.

Integrity failures include missing or duplicate IDs, invalid dispositions, residual violations allowed through, gate divergence allowed through, and simulated-schema release.
