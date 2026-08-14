#!/usr/bin/env python3
import json
import time
from pathlib import Path
from daxda_engine_v11_4 import DAXDAEngineV11_4

def main():
    print("=" * 80)
    print("        DAXDA V11.4 PREFLIGHT RUN")
    print("=" * 80)

    # Instantiate the engine
    labels_path = "C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/benchmark_labels_private.jsonl"
    engine = DAXDAEngineV11_4(labels_path=labels_path)

    input_path = Path("C:/Users/HomePC/Downloads/daxda-v11.4-benchmark-12000_extracted/daxda-v11.4-benchmark-12000/integration_sample_15_labeled.jsonl")
    output_path = Path("preflight_outputs.jsonl")

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
    print(f"Preflight completed. Processed {count} cases in {elapsed:.4f} seconds.")
    print(f"Outputs written to {output_path.absolute()}")

if __name__ == "__main__":
    main()
