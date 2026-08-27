import argparse
import csv
import json
import os
import google.generativeai as genai

# Read API key from environment
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

generation_config = {
  "temperature": 0.0,
  "response_mime_type": "application/json",
}

system_instruction = """
You are an automated Complaint Classifier. Your operational boundary is strictly limited to reading raw citizen complaint descriptions and assigning predefined classification labels. You do not resolve the complaints or generate new text outside of the required output schema.

A correct output must classify each complaint by returning exactly four fields: 'category', 'priority', 'reason', and 'flag'. The output must adhere strictly to the allowed values and rules without hallucinating categories or missing justifications.

You are only allowed to use the text provided in the citizen complaint description. Do not use external knowledge to infer context. You must strictly use the provided list of exact category strings and severity keywords to determine the classification.

Rules:
- "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations are allowed."
- "Priority must be set to 'Urgent' if any of the following severity keywords are present in the description: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be 'Standard' or 'Low'."
- "Every output row must include a 'reason' field containing exactly one sentence that cites specific words from the description to justify the classification."
- "If the category is genuinely ambiguous or cannot be determined from the description alone, you must set the flag to 'NEEDS_REVIEW' and category to 'Other'. Otherwise, leave the flag blank."

Respond strictly in JSON format matching this schema:
{
  "category": "string",
  "priority": "string",
  "reason": "string",
  "flag": "string"
}
"""

try:
    model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      generation_config=generation_config,
      system_instruction=system_instruction
    )
except Exception as e:
    model = None
    print(f"Failed to initialize model: {e}")

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the 'description' field.
    Returns: dict with appended keys: category, priority, reason, flag
    """
    description = row.get('description', '')
    if not description:
        row['category'] = 'Other'
        row['priority'] = 'Low'
        row['reason'] = 'No description provided.'
        row['flag'] = 'ERROR'
        return row
        
    try:
        if model is None:
            raise ValueError("Model is not initialized.")
            
        response = model.generate_content(f"Complaint description: {description}")
        result = json.loads(response.text)
        
        row['category'] = result.get('category', 'Other')
        row['priority'] = result.get('priority', 'Standard')
        row['reason'] = result.get('reason', '')
        row['flag'] = result.get('flag', '')
    except Exception as e:
        print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
        row['category'] = 'Other'
        row['priority'] = 'Low'
        row['reason'] = f'Error during classification: {str(e)}'
        row['flag'] = 'ERROR'
        
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, doesn't crash on bad rows, produces output even if some fail.
    """
    results = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        # Ensure our required fields are in fieldnames
        for field in ['category', 'priority', 'reason', 'flag']:
            if field not in fieldnames:
                fieldnames.append(field)
                
        for i, row in enumerate(reader):
            print(f"Processing row {i+1}...")
            classified_row = classify_complaint(row)
            results.append(classified_row)
            
    # Ensure directory for output_path exists if nested
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
