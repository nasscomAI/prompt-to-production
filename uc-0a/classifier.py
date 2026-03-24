"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import urllib.request
import urllib.error

def get_agent_prompt() -> str:
    prompt = "You are an expert citizen complaint classifier for a City Municipal Corporation. Your job is to process raw citizen complaint descriptions, accurately categorize them, and flag their priority level so they can be routed to the correct department.\n"
    prompt += "Output a JSON object with strictly these keys: 'category', 'priority', 'reason', 'flag'.\n"
    prompt += "Enforcement rules:\n"
    prompt += "1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.\n"
    prompt += "2. Priority must be 'Urgent' if description contains exact severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise 'Standard' or 'Low'.\n"
    prompt += "3. Reason must be exactly one sentence citing specific words from description.\n"
    prompt += "4. If category is ambiguous, use category: 'Other', flag: 'NEEDS_REVIEW'. Otherwise flag is blank."
    return prompt

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        row['category'] = "Other"
        row['priority'] = "Low"
        row['reason'] = "GEMINI_API_KEY not set"
        row['flag'] = "NEEDS_REVIEW"
        return row
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = get_agent_prompt()
    user_message = f"Description: {row.get('description')}\nClassify this citizen complaint."
    
    data = {
        "contents": [{
            "parts": [{"text": prompt + "\n\n" + user_message}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            parsed = json.loads(text)
            
            row['category'] = parsed.get('category', '')
            row['priority'] = parsed.get('priority', '')
            row['reason'] = parsed.get('reason', '')
            row['flag'] = parsed.get('flag', '')
    except Exception as e:
        row['category'] = "Other"
        row['priority'] = "Low"
        row['reason'] = f"API Error: {str(e)}"
        row['flag'] = "NEEDS_REVIEW"
        
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    rows = []
    fieldnames = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        fieldnames = [str(col) for col in fields] + ['category', 'priority', 'reason', 'flag']
        for row in reader:
            rows.append(row)
            
    print(f"Processing {len(rows)} complaints from {input_path}...")
    
    results = []
    for i, row in enumerate(rows):
        print(f"[{i+1}/{len(rows)}] Classifying {row.get('complaint_id')}...")
        classified_row = classify_complaint(row)
        results.append(classified_row)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
