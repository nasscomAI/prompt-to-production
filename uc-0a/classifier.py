"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import json
import os
import sys

# MOCK FLAG
USE_MOCK = False

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai is not installed. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: GEMINI_API_KEY environment variable is missing. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

model = None
if not USE_MOCK:
    genai.configure(api_key=API_KEY)

    SYSTEM_PROMPT = """
    role: >
      You are an expert citizen complaint classifier. Your operational boundary is strictly limited to assigning a structured categorization and priority to text-based civic complaints, processing one row at a time.

    intent: >
      To evaluate a citizen complaint description and produce a verifiable classification containing exactly four fields: 'category', 'priority', 'reason', and 'flag'. The output must strictly adhere to the allowed classification schema without any deviation, guesswork, or hallucinated values.

    context: >
      You will receive a single complaint description at a time. You are ONLY allowed to use the information explicitly stated in the description. You must NOT use external knowledge to invent categories, infer unspoken priorities, or deduce severity beyond the provided text.

    enforcement:
      - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other (Exact strings only — no variations)."
      - "Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, use Standard or Low."
      - "Every output row must include a 'reason' field consisting of exactly one sentence that cites specific words directly from the description."
      - "If a category cannot be determined from the description alone and is genuinely ambiguous, you must output the category string 'Other' and set the 'flag' field exactly to 'NEEDS_REVIEW'."
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        print(f"Failed to initialize model: {e}", file=sys.stderr)
        USE_MOCK = True

def mock_classify(description: str) -> dict:
    desc_lower = description.lower()
    category = "Other"
    
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower: category = "Flooding"
    elif "light" in desc_lower: category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower: category = "Waste"
    elif "noise" in desc_lower or "music" in desc_lower: category = "Noise"
    elif "drain" in desc_lower: category = "Drain Blockage"
    elif "road" in desc_lower or "crack" in desc_lower: category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"

    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Urgent" if any(kw in desc_lower for kw in urgent_keywords) else "Standard"

    flag = "NEEDS_REVIEW" if category == "Other" else ""
    return {
        "category": category,
        "priority": priority,
        "reason": f"Mock classification matching keyword in description.",
        "flag": flag
    }

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    description = row.get("description", "")
    
    if not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    if USE_MOCK:
        return mock_classify(description)
    
    prompt = f"Analyze this complaint and output JSON with exactly four keys: category, priority, reason, flag.\n\nDescription: {description}"
    
    try:
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:-3].strip()
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:-3].strip()
            
        result = json.loads(text_resp)
        
        return {
            "category": str(result.get("category", "Other")),
            "priority": str(result.get("priority", "Low")),
            "reason": str(result.get("reason", "No reason provided")),
            "flag": str(result.get("flag", "")) if result.get("flag") else ""
        }
    except Exception as e:
        print(f"Error classifying complaint ID {row.get('complaint_id', 'Unknown')}: {e}", file=sys.stderr)
        return {
            "category": "Other",
            "priority": "Low",
            "reason": f"API Error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return

    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Failed to read input CSV: {e}", file=sys.stderr)
        return

    out_fieldnames = list(fieldnames) + ["category", "priority", "reason", "flag"]
    
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            
            for idx, row in enumerate(rows):
                print(f"Processing ({idx+1}/{len(rows)}): {row.get('complaint_id', 'Unknown')}")
                classification = classify_complaint(row)
                row.update(classification)
                writer.writerow(row)
                
    except Exception as e:
        print(f"Failed to write output CSV: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
