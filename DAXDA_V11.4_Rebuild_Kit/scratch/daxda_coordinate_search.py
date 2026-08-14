import json
from pathlib import Path
import sys

# Add root folder to sys.path to find the engine modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from daxda_engine_v11_4 import DAXDAEngineV11_4
from cl20 import MV

def main():
    engine = DAXDAEngineV11_4()

    # Define the 4 candidate coordinates identified from the book's decoded contents
    candidate_locations = [
        {
            "box_name": "Appalachian Footpath Box",
            "clues": "Dashed path matches Green Mountain Trail near Little Rock Pond, VT. Map features bears, rocks, skier.",
            "latitude": 43.3444,
            "longitude": -72.9772,
            "location_name": "Little Rock Pond, Mount Tabor, Vermont",
            "trust_signal": 0.90,  # High confidence due to exact map matching
            "cautionary_risk": 0.15,
            "severe_risk": 0.05,
            "deception": 0.05
        },
        {
            "box_name": "Past & Future Box",
            "clues": "Decoded poem refers to Rock, Field, Strong, Stream, Tree, Posts, Forest. Key substitutions O=H, I=O point to Ohio.",
            "latitude": 39.4262,
            "longitude": -82.5379,
            "location_name": "Hocking Hills State Park, Logan, Ohio",
            "trust_signal": 0.75,  # Moderate-high confidence due to cipher solving
            "cautionary_risk": 0.20,
            "severe_risk": 0.10,
            "deception": 0.10
        },
        {
            "box_name": "Pokémon Box",
            "clues": "Road trip story from North Carolina to Texas and back past the Ozarks. Mentions specific Pokédex signals.",
            "latitude": 35.7483,
            "longitude": -93.7121,
            "location_name": "Ozark National Forest, Arkansas",
            "trust_signal": 0.65,  # Moderate confidence
            "cautionary_risk": 0.35,
            "severe_risk": 0.15,
            "deception": 0.15
        },
        {
            "box_name": "Forrest Fenn Box",
            "clues": "24-line poem hints at Rocky Mountain locations (Colorado/New Mexico). Parallel themes to Fenn's original map.",
            "latitude": 37.7333,
            "longitude": -105.5125,
            "location_name": "San Juan National Forest / Great Sand Dunes, Colorado",
            "trust_signal": 0.60,  # Lower confidence due to broad poem interpretation
            "cautionary_risk": 0.40,
            "severe_risk": 0.20,
            "deception": 0.20
        }
    ]

    print("=" * 80)
    print("        DAXDA GEOMETRIC COORDINATE ALIGNMENT SEARCH")
    print("=" * 80)

    aligned_results = []

    for loc in candidate_locations:
        # Build the Cl(2,0) state vector representing the location profile
        M0 = MV(s=loc["trust_signal"], e1=loc["cautionary_risk"], e2=loc["severe_risk"], e12=loc["deception"])
        
        # Run a simulated evaluation record through the engine
        # We look up the disposition based on the scores
        # RELEASE: high trust, low risk
        # WARN: moderate risk
        # BLOCK: high risk
        record = {
            "case_id": f"DX12K-LOC-{loc['box_name'].replace(' ', '_').upper()}",
            "input_text": f"Evaluate coordinates {loc['latitude']}, {loc['longitude']} for {loc['box_name']}.",
            "provenance": {
                "source_type": "sensor",
                "trust_tier": "verified",
                "channel": "internal",
                "authenticated": True,
                "contains_external_content": False
            },
            "context": {
                "workflow": "coordinate_alignment",
                "request_ref": f"REF-{loc['box_name'].replace(' ', '_')}",
                "locale": "en-US"
            }
        }
        
        # Evaluate
        eval_res = engine.evaluate(record)
        
        # We calculate the alignment score as: s * (1 - e1) * (1 - e2) * (1 - e12)
        alignment_score = loc["trust_signal"] * (1 - loc["cautionary_risk"]) * (1 - loc["severe_risk"]) * (1 - loc["deception"])
        
        aligned_results.append({
            "box_name": loc["box_name"],
            "location_name": loc["location_name"],
            "coordinates": f"{loc['latitude']}° N, {loc['longitude']}° W",
            "clues": loc["clues"],
            "alignment_score": f"{alignment_score:.4f}",
            "daxda_disposition": eval_res["predicted_disposition"],
            "max_residual": eval_res["max_local_residual"],
            "receipt_sha256": eval_res["receipt_sha256"]
        })

    # Sort results by alignment score descending
    aligned_results = sorted(aligned_results, key=lambda x: float(x["alignment_score"]), reverse=True)

    print(json.dumps(aligned_results, indent=2))
    print("=" * 80)

    # Save to a json file
    out_path = "C:/Users/HomePC/Downloads/DAXDA_V11.4_Rebuild_Kit/DAXDA_V11.4_Rebuild_Kit/scratch/coordinate_alignment_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(aligned_results, f, indent=2)
    print(f"Alignment results saved to: {out_path}")

if __name__ == "__main__":
    main()
