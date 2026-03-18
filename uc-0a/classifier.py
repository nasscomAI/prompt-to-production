"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import json
import os
import time
import requests

# Define the RICE instruction explicitly from agents.md
SYSTEM_INSTRUCTION = """
You are an expert municipal complaint classification AI for a local city government. Your operational boundary is strictly limited to reading citizen complaint descriptions and structuring them into predefined categories and priorities. You do not resolve the complaints, nor do you draft responses to citizens. Your sole purpose is triage.

A correct output is a JSON object containing exactly the parameters `category`, `priority`, `reason`, and `flag` that adheres perfectly to the classification schema. It must be completely objective and traceable to the input text.

You are only allowed to use the text provided in the `description` field of the complaint. Do not guess or assume details outside of what is explicitly stated in the text. You must assume that all severity keywords denote a real and present danger.

Enforcement Rules:
1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations are allowed.
2. Priority must be Urgent if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be Standard or Low.
3. Every output must include a reason field consisting of exactly one sentence. This sentence must cite specific words from the complaint description to justify the categorization.
4. If the category cannot be confidently determined or is genuinely ambiguous, you must rely on the evidence. Set the flag to NEEDS_REVIEW. Otherwise, leave the flag blank.
"""

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it before running this script.")
    return api_key

def classify_complaint(api_key: str, row: dict) -> dict:
    """
    Classify a single complaint row using the Gemini REST API via `requests`.
    We use the REST API natively so no external dependencies beyond standard/common python tools (requests) are needed.
    """
    description = row.get("description", "")
    
    if not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Invalid or empty input description provided.",
            "flag": "NEEDS_REVIEW"
        }
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [{
            "parts": [{"text": f"Complaint Description: {description}"}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING"},
                    "priority": {"type": "STRING"},
                    "reason": {"type": "STRING"},
                    "flag": {"type": "STRING"}
                },
                "required": ["category", "priority", "reason", "flag"]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse the JSON response text from Gemini
        text_content = data['candidates'][0]['content']['parts'][0]['text']
        parsed = json.loads(text_content)
        
        # Fallbacks for safety
        return {
            "category": parsed.get("category", "Other"),
            "priority": parsed.get("priority", "Low"),
            "reason": parsed.get("reason", "No reason provided."),
            "flag": parsed.get("flag", "")
        }
        
    except Exception as e:
        print(f"Error classifying row {row.get('complaint_id', 'Unknown')}: {e}")
        return {
            "category": "Other",
            "priority": "Low",
            "reason": f"API Error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    api_key = get_api_key()
    
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Ensure output columns exist
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)
                
            for i, row in enumerate(reader):
                print(f"Classifying row {i+1} : {row.get('complaint_id', '')}...")
                
                classification = classify_complaint(api_key, row)
                
                # Merge original row with classification results
                row['category'] = classification.get('category', '')
                row['priority'] = classification.get('priority', '')
                row['reason'] = classification.get('reason', '')
                row['flag'] = classification.get('flag', '')
                
                results.append(row)
                
                # Sleep to avoid rate limits
                time.sleep(2)
                
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    print(f"Starting batch classification from {args.input}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
