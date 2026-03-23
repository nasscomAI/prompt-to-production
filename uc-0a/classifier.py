"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import time

import sys

try:
    from google import genai
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: Required libraries not found.")
    print("Please install them using: pip install google-genai pydantic")
    sys.exit(1)


class ComplaintClassification(BaseModel):
    category: str = Field(description="Must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other")
    priority: str = Field(description="Must be exactly one of: Urgent, Standard, Low")
    reason: str = Field(description="Exactly one sentence citing specific words from the description justifying category and priority")
    flag: str = Field(description="Must be 'NEEDS_REVIEW' if category genuinely ambiguous, else blank ''")


def get_system_prompt() -> str:
    """Read the system prompt from agents.md."""
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback if agents.md is missing
        return """
role: >
  You are an AI assistant designed to classify citizen complaints for the city's public works and services department. Your operational boundary is strictly limited to categorizing text descriptions of complaints and assigning appropriate priority levels based on specific criteria.

intent: >
  To evaluate a citizen's complaint description and accurately extract the category, assess the priority, provide a concise reason citing specific words from the description, and flag ambiguous cases.

context: >
  You will receive a text description of a citizen complaint. You must only use the information provided in this text description.

enforcement:
  - "The 'category' field must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "The 'priority' field must be exactly one of: Urgent, Standard, Low."
  - "The 'priority' MUST be 'Urgent' if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output must include a 'reason' field that is exactly one sentence long citing specific words."
  - "If ambiguous, output 'category': 'Other' and 'flag': 'NEEDS_REVIEW'. Otherwise, 'flag' should be blank."
"""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the Gemini API.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', 'UNKNOWN')
    description = row.get('description', '').strip()
    
    # Error handling as defined in skills.md
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Input was unreadable or empty.',
            'flag': 'NEEDS_REVIEW'
        }
        
    system_instruction = get_system_prompt()
    prompt = f"Classify this citizen complaint by category and priority:\n\nDescription: {description}"
    
    try:
        if 'GEMINI_API_KEY' not in os.environ:
            raise ValueError("Environment variable GEMINI_API_KEY is not set.")
            
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'system_instruction': system_instruction,
                'response_mime_type': "application/json",
                'response_schema': ComplaintClassification,
                'temperature': 0.1,
            },
        )
        
        # Parse output JSON back into our schema dictionary
        output_data = json.loads(response.text)
        return {
            'complaint_id': complaint_id,
            'category': output_data.get('category', 'Other'),
            'priority': output_data.get('priority', 'Low'),
            'reason': output_data.get('reason', ''),
            'flag': output_data.get('flag', '')
        }

    except Exception as e:
        print(f"Error classifying {complaint_id}: {e}")
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': f"Error during processing: {str(e)}",
            'flag': 'ERROR_PROCESSING'
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total_rows = len(rows)
        print(f"Loaded {total_rows} rows from {input_path}")
        
        for i, row in enumerate(rows, 1):
            print(f"Processing row {i}/{total_rows} (ID: {row.get('complaint_id', 'UNKNOWN')})...")
            # Enforce small delay to respect API rate limits
            time.sleep(1.0)
            
            result_dict = classify_complaint(row)
            # Combine the original row properties and the output of the classification
            merged_row = {**row, **result_dict}
            results.append(merged_row)
            
    # Define fields to output, ensuring all CSV fields and new columns are preserved
    if results:
        fieldnames = list(results[0].keys())
        
        # Guarantee category, priority, reason, flag are present in columns
        for col in ['category', 'priority', 'reason', 'flag']:
            if col not in fieldnames:
                fieldnames.append(col)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    else:
        print("No rows processed, skipping output generation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        print(f"Starting batch classification from {args.input} to {args.output}...")
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    except Exception as e:
        print(f"Fatal error during execution: {e}")
