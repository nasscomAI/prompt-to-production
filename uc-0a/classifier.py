"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import json
import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    sys.exit(1)

_model = None

def get_client():
    global _model
    if _model is not None:
        return _model
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    # Using gemini-2.5-flash as the default model
    model_name = os.environ.get("MODEL_NAME", "gemini-3.1-flash-lite-preview")
    _model = genai.GenerativeModel(model_name)
    return _model

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    model = get_client()
    
    system_prompt = """You are an expert civic AI agent responsible for classifying citizen complaints into standardized categories and determining their priority based on severity.

Your output must be a structured classification for each complaint, strictly adhering to the allowed categories and priorities. It must include a verifiable reason citing specific words from the description. The output fields are category, priority, reason, and flag.

You evaluate raw text where original category and priority_flag columns are explicitly excluded and stripped. You must use ONLY the raw complaint description provided in the input. You are strictly excluded from using external knowledge, guessing missing information, or inventing hallucinated sub-categories not in the taxonomy.

enforcement:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations allowed.
- Priority must be exactly one of: Urgent, Standard, Low. Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- Every output classification must include a reason field that is exactly one sentence long and quotes specific words from the description to justify the decision.
- Refusal condition to prevent false confidence: If the category is genuinely ambiguous or cannot be determined from the description alone, you must refuse to guess. Output category as 'Other' and set the flag field to 'NEEDS_REVIEW'.

Output strictly valid JSON with the exact keys: "category", "priority", "reason", "flag".
"""

    user_prompt = f"Complaint Description: {row.get('description', '')}"

    try:
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        result_text = response.text.strip()
        result = json.loads(result_text)
        
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": result.get("category", "Other"),
            "priority": result.get("priority", "Low"),
            "reason": result.get("reason", "Missing reason"),
            "flag": result.get("flag", "")
        }
    except Exception as e:
        print(f"Error classifying {row.get('complaint_id', 'unknown')}: {e}")
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "System error handling classification",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            input_fieldnames = reader.fieldnames if reader.fieldnames else []
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    results = []
    for row in rows:
        row_result = row.copy()
        if not row.get("description") or not row.get("description").strip():
            row_result.update({
                "category": "Other",
                "priority": "Low",
                "reason": "Missing description in input",
                "flag": "NEEDS_REVIEW"
            })
            results.append(row_result)
            continue
            
        print(f"Processing complaint: {row.get('complaint_id', 'unknown')}...")
        classified = classify_complaint(row)
        for k in ["category", "priority", "reason", "flag"]:
            row_result[k] = classified.get(k, "")
        results.append(row_result)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        out_fields = list(input_fieldnames)
        for f in ["category", "priority", "reason", "flag"]:
            if f not in out_fields:
                out_fields.append(f)
        writer = csv.DictWriter(outfile, fieldnames=out_fields)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")