# DAXDA V11.4 Rebuild Reproducibility Protocol

This document describes how to execute the rebuild, verification, benchmark, and reporting workflow.

## 1. Intake and Pre-execution Checks

Ensure all required files are present and configurations are valid:
```bash
python 03_REBUILD_TOOLS/check_required_files.py --root .
python 03_REBUILD_TOOLS/check_config_schema.py --root .
```

## 2. Manifest Verification

Generate the runtime manifest and verify file integrity:
```bash
python 03_REBUILD_TOOLS/build_runtime_manifest.py --root . --out runtime_manifest.json
python 03_REBUILD_TOOLS/verify_manifest.py --root . --manifest runtime_manifest.json
```

## 3. Run Preflight Checks

Run the preflight verification on the 15-case sample dataset:
```bash
python run_preflight.py
```

## 4. Run Benchmark Execution

Execute the full 12,000-case benchmark:
```bash
python run_frozen_benchmark.py --outputs benchmark_predictions.jsonl
```

## 5. Scoring and Accuracy Evaluation

Evaluate the predictions against the private labels:
```bash
python C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/score_predictions.py --labels C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/benchmark_labels_private.jsonl --predictions benchmark_predictions.jsonl --out benchmark_score_report.json
```

## 6. Three repetitions comparison

To verify that the engine runs deterministically, run the benchmark three times and compare the output files:
```bash
python run_frozen_benchmark.py --outputs run1.jsonl
python run_frozen_benchmark.py --outputs run2.jsonl
python run_frozen_benchmark.py --outputs run3.jsonl

python 03_REBUILD_TOOLS/compare_rebuild_outputs.py --a run1.jsonl --b run2.jsonl
python 03_REBUILD_TOOLS/compare_rebuild_outputs.py --a run2.jsonl --b run3.jsonl
```
