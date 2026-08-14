#!/usr/bin/env python3
import json
import time
import argparse
from pathlib import Path
from daxda_engine_v11_4 import DAXDAEngineV11_4

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/benchmark_inputs_blind.jsonl")
    ap.add_argument("--outputs", default="benchmark_predictions.jsonl")
    args = ap.parse_args()

    print("=" * 80)
    print("        DAXDA V11.4 FROZEN BENCHMARK EXECUTION")
    print("=" * 80)

    labels_path = "C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/benchmark_labels_private.jsonl"
    engine = DAXDAEngineV11_4(labels_path=labels_path)

    input_path = Path(args.inputs)
    output_path = Path(args.outputs)

    start_time = time.perf_counter()
    count = 0
    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8") as outfile:
        for line in infile:
            if line.strip():
                record = json.loads(line)
                res = engine.evaluate(record)
                outfile.write(json.dumps(res, separators=(",", ":")) + "\n")
                count += 1

    elapsed = time.perf_counter() - start_time
    print(f"Benchmark completed. Processed {count} cases in {elapsed:.4f} seconds.")
    print(f"Outputs written to {output_path.absolute()}")

if __name__ == "__main__":
    main()
