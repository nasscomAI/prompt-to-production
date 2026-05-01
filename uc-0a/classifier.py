import argparse
import csv
import json
import os
from openai import OpenAI

def get_openai_client():
    return OpenAI()

def classify_complaint(row: dict, client) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    
    prompt = f"""
    You are an expert citizen complaint classifier agent operating on municipal incident reports.
    Your boundary is strict classification: you do not resolve complaints, you only categorize them and assign priority based on fixed schemas.

    Intent:
    Output a valid JSON containing 'category', 'priority', 'reason', and 'flag'.
    The classification must strictly follow the allowed taxonomy and priority rules.

    Context:
    You must classify based solely on the provided complaint description text. Do not use outside knowledge to infer locations or context not present in the text.

    Enforcement Rules:
    - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations.
    - Priority must be 'Urgent', 'Standard', or 'Low'.
    - Priority must be 'Urgent' if any of these severity keywords are present in the description: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
    - Reason must be exactly one sentence and must cite specific words from the description.
    - Flag must be set to 'NEEDS_REVIEW' when the category is genuinely ambiguous, otherwise leave it blank.

    Complaint Description:
    {description}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "complaint_id": row.get("complaint_id"),
            "category": result.get("category", "Other"),
            "priority": result.get("priority", "Low"),
            "reason": result.get("reason", ""),
            "flag": result.get("flag", "")
        }
    except Exception as e:
        print(f"Error classifying row {row.get('complaint_id')}: {e}")
        return {
            "complaint_id": row.get("complaint_id"),
            "category": "Other",
            "priority": "Low",
            "reason": "Error processing",
            "flag": "NEEDS_REVIEW"
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    client = get_openai_client()
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for row in rows:
        classified = classify_complaint(row, client)
        results.append(classified)
        
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
