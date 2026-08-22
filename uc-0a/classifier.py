import argparse
import csv
import json
import os
import time
from dotenv import load_dotenv
from groq import Groq

# Load API key from root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize the Groq client (reads GROQ_API_KEY from environment)
client = Groq(max_retries=3)

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using Groq.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # The strict instructions based directly on our agents.md
    system_prompt = """You are an expert civic operations classifier for a municipal government. Your operational boundary is strictly limited to categorizing citizen complaints into predefined categories and assigning priority levels based on specific keywords.

A correct output must assign exactly one category from the approved list, assign a priority level based strictly on keyword presence, provide a one-sentence reason citing specific words from the description, and apply a NEEDS_REVIEW flag only when genuinely ambiguous.

You are only allowed to use the text provided in the user complaint description. You must not assume facts, infer unstated dangers, or guess locations. You must exclude any external knowledge about city infrastructure.

ENFORCEMENT RULES:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations allowed.
- Priority must be set to 'Urgent' if and only if the description contains one or more of these exact keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be 'Standard' or 'Low'.
- Every output must include a one-sentence 'reason' field that cites the specific words from the description used to determine the category and priority.
- If the category cannot be confidently determined from the description alone, you must output category as 'Other' and set the flag field to 'NEEDS_REVIEW'.

You must return strictly valid JSON with exactly these keys: "category", "priority", "reason", "flag"."""

    description = row.get("description", "").strip()
    
    # Error handling from skills.md
    if not description:
        return {
            "complaint_id": row.get("complaint_id", "unknown"),
            "category": "Other",
            "priority": "Low",
            "reason": "Malformed input row",
            "flag": "NEEDS_REVIEW"
        }

    user_prompt = f"Please classify this complaint: {description}"

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b", # Replaces deprecated llama-3.3-70b-versatile
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0 # Set to 0 so it strictly follows rules without getting "creative"
        )
        
        # Parse the JSON response
        result_content = response.choices[0].message.content
        parsed_result = json.loads(result_content)
        
        # Merge the original ID with the new classification
        return {
            "complaint_id": row.get("complaint_id", "unknown"),
            "category": parsed_result.get("category", "Other"),
            "priority": parsed_result.get("priority", "Low"),
            "reason": parsed_result.get("reason", "Unknown"),
            "flag": parsed_result.get("flag", "")
        }

    except Exception as e:
        print(f"Error classifying row {row.get('complaint_id')}: {e}")
        return {
            "complaint_id": row.get("complaint_id", "unknown"),
            "category": "Other",
            "priority": "Low",
            "reason": "API Error",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str) -> bool:
    """
    Read input CSV, classify each row, write results CSV.
    Returns True on success, False on failure.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return False

    if not rows:
        print("Error: Input file contains no data rows.")
        return False

    results = []
    print(f"Found {len(rows)} complaints. Sending to Groq API...")
    
    for idx, row in enumerate(rows):
        print(f"Processing {idx+1}/{len(rows)}...")
        classified_row = classify_complaint(row)
        results.append(classified_row)
        time.sleep(1)  # 1-second delay prevents rate limits
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    success = batch_classify(args.input, args.output)
    if success:
        print(f"Done. Results written to {args.output}")
    else:
        print("Classification failed. Please check the errors above.")