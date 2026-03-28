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
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

def classify_complaint(row: dict, client: OpenAI, model_name: str) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    system_prompt = """You are an expert civic AI agent responsible for classifying citizen complaints into standardized categories and determining their priority based on severity.

Your output must be a structured classification for each complaint, strictly adhering to the allowed categories and priorities. It must include a verifiable reason citing specific words from the description. The output fields are category, priority, reason, and flag.

You are allowed to use ONLY the complaint description provided in the input. Do not assume external facts or hallucinate details. Use only the provided taxonomy for categories and priorities.

enforcement:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations.
- Priority must be exactly one of: Urgent, Standard, Low. Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- Every output classification must include a reason field that is exactly one sentence long and quotes specific words from the description to justify the decision.
- If the category is genuinely ambiguous or cannot be determined from the description alone, output category as 'Other' and set the flag field to 'NEEDS_REVIEW' otherwise leave it empty.

Output strictly valid JSON with the exact keys: "category", "priority", "reason", "flag".
"""

    user_prompt = f"Complaint Description: {row.get('description', '')}"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": result.get("category", "Other"),
            "priority": result.get("priority", "Low"),
            "reason": result.get("reason", ""),
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
    # Detect provided API keys to smartly configure client
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    if not api_key and os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        model_name = os.environ.get("MODEL_NAME", "gemini-2.5-flash")

    if not api_key:
        api_key = "dummy" # Failsafe just in case they use a proxy without keys

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        sys.exit(1)
        
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    results = []
    for row in rows:
        if not row.get("description") or not row.get("description").strip():
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Missing description in input",
                "flag": "NEEDS_REVIEW"
            })
            continue
            
        print(f"Processing complaint: {row.get('complaint_id')}...")
        classified = classify_complaint(row, client, model_name)
        results.append(classified)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
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
