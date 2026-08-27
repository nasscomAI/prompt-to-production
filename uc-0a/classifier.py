"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    import sys
    sys.exit(1)

# Initialize the OpenAI client (ensure OPENAI_API_KEY is set in your environment)
client = OpenAI()

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the AI tool (LLM).
    Returns: dict with updated keys: category, priority, reason, flag
    """
    
    # RICE prompt derived from agents.md and skills.md
    system_prompt = """
# role
You are a strict and robust citizen complaint classifier. Your operational boundary is strictly limited to categorizing citizen complaints into a predefined taxonomy, assessing their priority based on specific keywords, and providing justification without hallucinating sub-categories or exercising false confidence on ambiguity.

# intent
A correct output provides exactly four fields per complaint: a valid `category` from the allowed list, a `priority`, a one-sentence `reason` containing specific words cited from the description, and a `flag` set appropriately for ambiguous cases.

# context
You are only allowed to use the provided citizen complaint description text. You must explicitly exclude any internal knowledge to generate sub-categories, and you must not infer severity unless specific severity keywords are explicitly present in the text.

# enforcement
- "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations."
- "Priority must be Urgent if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be Standard or Low."
- "Every output row must include a 'reason' field that is exactly one sentence long and must cite specific words from the complaint description."
- "If the category is genuinely ambiguous, the 'flag' field must be set to 'NEEDS_REVIEW' (or left blank otherwise)."

Return the classification strictly as a JSON object with keys: category, priority, reason, flag.
"""
    
    # Present the row as JSON to the model
    user_prompt = f"Complaint Data: {json.dumps(row)}"
    
    output_row = row.copy()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        
        result_json = response.choices[0].message.content
        classification = json.loads(result_json)
        
        output_row['category'] = classification.get('category', 'Other')
        output_row['priority'] = classification.get('priority', 'Low')
        output_row['reason'] = classification.get('reason', '')
        output_row['flag'] = classification.get('flag', '')
        
    except Exception as e:
        print(f"Error classifying complaint: {e}")
        output_row['category'] = 'Other'
        output_row['priority'] = 'Low'
        output_row['reason'] = f'Error: {str(e)}'
        output_row['flag'] = 'NEEDS_REVIEW'
        
    return output_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write the results to a CSV.
    Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    if not rows:
        print("Input file is empty.")
        return

    # Ensure output CSV contains the expected classification keys
    fieldnames = list(rows[0].keys())
    for f in ['category', 'priority', 'reason', 'flag']:
        if f not in fieldnames:
            fieldnames.append(f)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, row in enumerate(rows):
            print(f"Processing row {idx + 1}/{len(rows)}...")
            try:
                classified_row = classify_complaint(row)
                writer.writerow(classified_row)
            except Exception as e:
                print(f"Failed to process row {idx + 1}: {e}")
                # Write original row and flag as needs review on catastrophic fail
                error_row = row.copy()
                error_row['flag'] = 'NEEDS_REVIEW'
                error_row['reason'] = f"System Error: {str(e)}"
                writer.writerow(error_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # Ensure OPENAI_API_KEY is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set. Classification may fail.")
        
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
