"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import json
import time

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai is not installed. Run `pip install google-generativeai`")
    genai = None

def get_model():
    if not genai:
        raise RuntimeError("google-generativeai is required.")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set.")
        
    genai.configure(api_key=api_key)
    # Using JSON mode for reliable parsing
    return genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

def classify_complaint(row: dict, model=None) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if model is None:
        model = get_model()
        
    description = row.get("description", "")
    
    prompt = f"""
    Role: You are a Complaint Classifier for citizen complaints. 
    Intent: Accurately classify each complaint according to the required schema.

    Complaint Description:
    "{description}"

    Enforcement Rules:
    1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
    2. Priority must be Urgent if the description contains severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Priority should be Standard or Low.
    3. Reason must be exactly one sentence and must cite specific words directly from the complaint description.
    4. Flag must be set to "NEEDS_REVIEW" when the category is genuinely ambiguous, otherwise leave it blank "".

    Return a JSON object with exactly the following keys:
    {{
        "category": "string",
        "priority": "string",
        "reason": "string",
        "flag": "string"
    }}
    """
    
    retries = 3
    result = {
        "complaint_id": row.get("complaint_id", ""),
        "category": "Other",
        "priority": "Low",
        "reason": "Failed to process",
        "flag": "NEEDS_REVIEW"
    }
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            
            result["category"] = data.get("category", "")
            result["priority"] = data.get("priority", "")
            result["reason"] = data.get("reason", "")
            result["flag"] = data.get("flag", "")
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error processing {result['complaint_id']}: {e}")
            time.sleep(1)
            
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    print(f"Reading from {input_path}...")
    try:
        model = get_model()
    except Exception as e:
        print(f"Failed to initialize model: {e}")
        return

    results = []
    
    # Read input CSV
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                print(f"Classifying {row.get('complaint_id', 'Unknown')}...")
                classified_info = classify_complaint(row, model)
                results.append(classified_info)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    # Write output CSV
    print(f"Writing to {output_path}...")
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
