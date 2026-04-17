import requests
import json
import sys

def evaluate_transit_data(data, stellar_context=None):
    """Evaluate transit data with optional SIMBAD stellar context."""
    
    # Build context block
    stellar_block = ""
    if stellar_context:
        stellar_block = f"""

{stellar_context}

When evaluating, factor in the stellar classification above. A rotating variable host may produce periodic dips from starspot modulation. A subgiant host has R_star > 1 R_sun, which changes the companion radius estimate. An eclipsing binary classification strongly suggests the transit is stellar, not planetary.
"""
    
    prompt = f"""You are an autonomous astrophysics reasoning engine under strict NAEF (Narrative-Based Agentic Failure Evaluation) compliance.
Evaluate the following BLS periodogram detection parameters for an exoplanet transit anomaly.
Do NOT express optimism, defer closure, or provide narrative justification.
State mathematically if this resembles an eclipsing binary false-positive or a sub-stellar transit candidate.

DETECTION PARAMETERS:
- Target ID: {data['target_id']}
- Coordinate: {data['coordinate']}
- Orbital Period: {data['period_days']} days
- Transit Duration: {data['duration_days']} days
- Fraction Flux Depth: {data['depth']}
- Max Power: {data['max_power']}
- SNR: {data['snr']}
{stellar_block}
DECISION CRITERIA (deterministic):
- If SNR > 10.0 AND fraction flux depth < 0.05 (small radius relative to star): verdict is PASS.
- If depth >= 0.05 (suggesting eclipsing binary, not a planet): verdict is MODEL_BOUND.
- If SNR <= 10.0, or data is noisy/ambiguous: verdict is INCONCLUSIVE.
- If host is classified as eclipsing binary in SIMBAD: verdict is MODEL_BOUND regardless of SNR.
- If host is a rotating variable, note starspot contamination risk but do not auto-downgrade if SNR and depth criteria are met.

RESPONSE FORMAT:
Provide your output in JSON format with exactly two keys: "reasoning" (containing your 3-5 sentences of analysis) and "verdict" (which MUST be exactly "PASS", "MODEL_BOUND", or "INCONCLUSIVE").
Parse your own reasoning before emitting the verdict."""
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "format": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "verdict": {"type": "string", "enum": ["PASS", "MODEL_BOUND", "INCONCLUSIVE"]}
            },
            "required": ["reasoning", "verdict"]
        },
        "options": {
            "num_predict": -1,
            "temperature": 0.1
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=50)
        result = response.json()
        try:
            parsed = json.loads(result["response"])
            return f"{parsed.get('reasoning', '')}\n\n[VERDICT: {parsed.get('verdict', 'INCONCLUSIVE').upper()}]"
        except:
            return result["response"]
    except Exception as e:
        return f"Oracle Connection Failed: {e}"

def evaluate_transit(candidate_file="candidate_anomaly.json"):
    try:
        with open(candidate_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Candidate file not found. Run miner.py first.")
        return
        
    print("[EVALUATOR] Querying local high-reasoning model...")
    response_text = evaluate_transit_data(data)
    print("\n=== EVALUATION REPORT ===")
    print(response_text)
    print("=========================\n")

if __name__ == "__main__":
    evaluate_transit()
