"""
UC-0A — Complaint Classifier
Production implementation using Google GenAI SDK.
"""
import argparse
import csv
import json
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: Missing required packages.", file=sys.stderr)
    print("Please run: pip install google-genai", file=sys.stderr)
    sys.exit(1)

# Define the structured output schema as a dictionary to avoid Pydantic dependency issues
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {
            "type": "STRING",
            "description": "Must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
        },
        "priority": {
            "type": "STRING",
            "description": "Must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
        },
        "reason": {
            "type": "STRING",
            "description": "Exactly one sentence citing specific words from the description"
        },
        "flag": {
            "type": "STRING",
            "description": "Optional. Set to 'NEEDS_REVIEW' if category is genuinely ambiguous, otherwise empty string."
        }
    },
    "required": ["category", "priority", "reason", "flag"]
}

def get_system_instruction() -> str:
    """Reads system instruction dynamically from agents.md"""
    agents_md_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if os.path.exists(agents_md_path):
        with open(agents_md_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Fallback if agents.md is somehow not present
        return 'role: Complaint Classifier Agent...\n[Fallback]'

SYSTEM_INSTRUCTION = get_system_instruction()

def get_client():
    try:
        return genai.Client()
    except Exception as e:
        return None

def classify_complaint(client, description: str) -> dict:
    """
    Classifies a single citizen complaint row into a category, priority, reason, and flag.
    Reference: skills.md
    """
    if not client:
        raise ValueError("Google GenAI client not initialized.")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=description,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.0,
        ),
    )
    return json.loads(response.text)

def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the categorized data to an output CSV.
    If a row cannot be processed, logs the error, skips the malformed row, and continues processing the rest of the CSV.
    Reference: skills.md
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    if not client:
        print("Warning: genai.Client() failed to initialize. Do you have GEMINI_API_KEY set?", file=sys.stderr)

    print(f"Reading from {input_path}...")
    
    results = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
             print(f"Error: Input file {input_path} is empty or has no headers.", file=sys.stderr)
             sys.exit(1)
        fieldnames = list(reader.fieldnames)
        
        desc_col = next((col for col in fieldnames if col.lower() in ('description', 'complaint', 'text')), fieldnames[0])
        print(f"Using column '{desc_col}' as the complaint description.")

        for i, row in enumerate(reader):
            desc = row.get(desc_col, "").strip()
            print(f"Row {i+1}: {desc[:40]}...")
            
            try:
                if not desc:
                    raise ValueError("Empty description provided.")
                
                classification = classify_complaint(client, desc)
                result = {**row, **classification}
                results.append(result)
            except Exception as e:
                print(f"Error processing row {i+1}: {e}. Skipping malformed row.", file=sys.stderr)
                continue

    if not results:
        print("No rows processed.", file=sys.stderr)
        return

    out_fieldnames = list(fieldnames)
    for col in ["category", "priority", "reason", "flag"]:
        if col not in out_fieldnames:
            out_fieldnames.append(col)

    print(f"Writing to {output_path}...")
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
         print("Warning: GEMINI_API_KEY environment variable is not set. The classifier needs it to contact the LLM.", file=sys.stderr)

    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
