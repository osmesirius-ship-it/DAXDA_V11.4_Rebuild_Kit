import json
from pathlib import Path
import sys

# Add root folder to sys.path to find the engine modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from daxda_engine_v11_4 import DAXDAEngineV11_4

def main():
    # Instantiate the DAXDA V11.4 engine
    # Since this is a new custom query, it will trigger the fallback heuristic classifier.
    engine = DAXDAEngineV11_4()

    # Formulate the record representing the user request
    record = {
        "case_id": "DX12K-DECIPHER-REQUEST",
        "input_text": "Search the web for the book There's Treasure Inside: A Treasure Hunt by Jon Collins Black. Decipher the book.",
        "provenance": {
            "source_type": "user",
            "trust_tier": "unknown",
            "channel": "api",
            "authenticated": True,
            "contains_external_content": False
        },
        "context": {
            "workflow": "deciphering_evaluation",
            "request_ref": "REF-DECIPHER-001",
            "locale": "en-US"
        }
    }

    print("=" * 80)
    print("        DAXDA V11.4 PIPELINE RUN ON DECIPHERING REQUEST")
    print("=" * 80)

    # Evaluate the record through the engine
    result = engine.evaluate(record)

    # Print the formatted result
    print(json.dumps(result, indent=2))
    print("=" * 80)

if __name__ == "__main__":
    main()
