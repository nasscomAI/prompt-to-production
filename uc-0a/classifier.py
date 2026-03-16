"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import requests

# The RICE prompt defined in agents.md
SYSTEM_PROMPT = """
Role:
You are an automated citizen complaint classifier for city administration. Your operational boundary is strictly limited to categorizing complaints into predefined taxonomy, assigning severity-based priorities, and explaining these decisions.

Intent:
A correct output provides a structured classification for every input row, where `category` matches the exact allowed taxonomy strings, `priority` is assigned accurately based on severity keywords, a `reason` citing specific words from the description is given, and a `flag` is set for any ambiguous cases.

Context:
You are allowed to use ONLY the provided text description of the complaint to make your decisions. You must not use external knowledge to invent new complaint categories, hallucinate sub-categories, or infer information not explicitly present in the text.

Enforcement:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations are allowed.
- Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it should be Standard or Low.
- Every output row must include a one-sentence reason field that cites specific words from the complaint description to justify the classification.
- If the category is genuinely ambiguous or cannot be determined from the description alone, output category 'Other' and set flag to 'NEEDS_REVIEW'.

Output your response in exact JSON format with the following keys:
- category (string)
- priority (string)
- reason (string)
- flag (string - empty if not needed, or "NEEDS_REVIEW")
"""

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # You can change this to your preferred local model (e.g., phi3, mistral)

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the agent defined in agents.md via Ollama REST API.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    description = row.get("description", str(row))
    
    # Setup default/error result for graceful degradation
    result = {
        "category": "Other",
        "priority": "Low",
        "reason": "Failed to classify.",
        "flag": "NEEDS_REVIEW"
    }
    
    if not description.strip():
        result["reason"] = "Empty description."
        return result

    try:
        payload = {
            "model": MODEL_NAME,
            "system": SYSTEM_PROMPT,
            "prompt": f"Description: {description}",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        parsed = json.loads(data.get("response", "{}"))
        
        result["category"] = parsed.get("category", "Other")
        result["priority"] = parsed.get("priority", "Low")
        result["reason"] = parsed.get("reason", "No reason provided by AI.")
        result["flag"] = parsed.get("flag", "")
        
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: Is Ollama running? ({e})")
        result["reason"] = f"Connection Error."
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        result["reason"] = "Model did not return valid JSON."
    except Exception as e:
        print(f"Error classifying row: {e}")
        result["reason"] = f"Error: {str(e)}"
        
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    print(f"Reading from {input_path}...")
    
    rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for r in reader:
                rows.append(r)
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return
        
    print(f"Found {len(rows)} rows to classify.")
    
    results = []
    for i, row in enumerate(rows, 1):
        print(f"Classifying row {i}/{len(rows)}...")
        
        # apply specific skill implementation
        classified = classify_complaint(row)
        
        # Merge output with input row to retain data
        out_row = dict(row)
        out_row["category"] = classified["category"]
        out_row["priority"] = classified["priority"]
        out_row["reason"] = classified["reason"]
        out_row["flag"] = classified["flag"]
        
        results.append(out_row)
        
    print(f"Writing to {output_path}...")
    # Add new headers
    headers = list(fieldnames) + ["category", "priority", "reason", "flag"]
    # Ensure uniqueness of headers just in case originally present
    headers = list(dict.fromkeys(headers))
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
        
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
