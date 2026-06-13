"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import time
# pyrefly: ignore [missing-import]
from google import genai
from google.genai import types

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {"type": "STRING", "description": "The category of the complaint. Must be EXACTLY ONE of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."},
        "priority": {"type": "STRING", "description": "The priority of the complaint. Must be Urgent, Standard, or Low. Must be Urgent if severity keywords are present."},
        "reason": {"type": "STRING", "description": "Exactly one sentence explaining the category and priority, citing specific words from the description."},
        "flag": {"type": "STRING", "description": "Set to 'NEEDS_REVIEW' if genuinely ambiguous, otherwise leave blank ''."}
    },
    "required": ["category", "priority", "reason", "flag"]
}

# Read RICE prompt from agents.md
AGENTS_MD_PATH = os.path.join(os.path.dirname(__file__), "agents.md")
with open(AGENTS_MD_PATH, "r", encoding="utf-8") as f:
    SYSTEM_INSTRUCTION = f.read()

# Retry settings for rate-limit handling
MAX_RETRIES = 5
INITIAL_BACKOFF = 15  # seconds

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row with retry logic for rate limits.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    client = genai.Client()
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=json.dumps(row),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=SCHEMA,
                    temperature=0.0
                ),
            )
            result = json.loads(response.text)
            return {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": result.get("category", "Other"),
                "priority": result.get("priority", "Standard"),
                "reason": result.get("reason", "No reason provided."),
                "flag": result.get("flag", "")
            }
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = INITIAL_BACKOFF * (2 ** attempt)
                print(f"  Rate limited on {row.get('complaint_id')} (attempt {attempt+1}/{MAX_RETRIES}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error classifying {row.get('complaint_id')}: {e}")
                return {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {error_str}",
                    "flag": "NEEDS_REVIEW"
                }
    # Exhausted all retries
    print(f"Failed after {MAX_RETRIES} retries for {row.get('complaint_id')}")
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": "Other",
        "priority": "Standard",
        "reason": "Error: exceeded rate limit retries",
        "flag": "NEEDS_REVIEW"
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("complaint_id")]
            total = len(rows)
            for i, row in enumerate(rows):
                print(f"Processing {row.get('complaint_id')} ({i+1}/{total})...")
                classified = classify_complaint(row)
                results.append(classified)
                # Delay between requests to respect free-tier rate limit (5 RPM)
                if i < total - 1:
                    time.sleep(13)
                
        if results:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
                writer.writeheader()
                writer.writerows(results)
    except Exception as e:
        print(f"Failed during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
