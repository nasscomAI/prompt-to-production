"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import logging
import os
import time

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Attempt to configure GenAI if installed
if HAS_GENAI:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the AI model, enforced with programmatic rules.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "")
    
    result = {
        "category": "Other",
        "priority": "Standard",
        "reason": "Processing failed.",
        "flag": "NEEDS_REVIEW"
    }

    if not HAS_GENAI or not os.environ.get("GEMINI_API_KEY"):
        # Fallback local programmatic classifier if no API key is set
        desc_lower = description.lower()
        if "pothole" in desc_lower: result["category"] = "Pothole"
        elif "flood" in desc_lower or "rain" in desc_lower: result["category"] = "Flooding"
        elif "light" in desc_lower: result["category"] = "Streetlight"
        elif "waste" in desc_lower or "garbage" in desc_lower: result["category"] = "Waste"
        elif "music" in desc_lower or "noise" in desc_lower: result["category"] = "Noise"
        else: result["category"] = "Other"
        
        result["reason"] = f"Classified based on keywords in description: {description[:30]}..."
        result["flag"] = ""
    else:
        system_instruction = """
You are a Complaint Classifier Agent responsible for categorizing citizen complaints into predefined taxonomies, assigning accurate priority levels, and safely flagging ambiguous inputs.
intent: Output a verifiable classification for each complaint row that strictly adheres to the provided schema, assigns correct priority based on severity keywords, and provides cited justification to prevent taxonomy drift and severity blindness.

ENFORCEMENT RULES:
- category: exactly match one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
- priority: exactly one of [Urgent, Standard, Low]. MUST be Urgent if keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present.
- reason: exactly one sentence. MUST cite specific words directly from the complaint description.
- flag: strictly 'NEEDS_REVIEW' when the category is genuinely ambiguous (applies to multiple categories or lacks clear details). Otherwise empty string "".

Return ONLY a valid JSON object with keys "category", "priority", "reason", "flag".
"""
        prompt = f"Complaint: {description}"
        try:
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            result["category"] = data.get("category", "")
            result["priority"] = data.get("priority", "")
            result["reason"] = data.get("reason", "")
            result["flag"] = data.get("flag", "")
        except Exception as e:
            logging.error(f"LLM Classification failed for row: {e}")
            result["flag"] = "NEEDS_REVIEW"

    # --- ENFORCEMENT SKILLS (Error Handling / Failsafe) ---
    
    # 1. Taxonomy drift: Reject any category not in the allowed list
    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        
    # 2. Severity blindness: Force priority to Urgent if keywords detected
    desc_lower = description.lower()
    if any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS):
        result["priority"] = "Urgent"

    # 3. Missing justification / reason check
    if not result["reason"] or len(result["reason"].split('.')) < 1:
        result["flag"] = "NEEDS_REVIEW"

    # Ensure validity of priority
    if result["priority"] not in {"Urgent", "Standard", "Low"}:
        result["priority"] = "Standard"

    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        logging.error(f"invalid_file: Could not read input file {input_path}")
        return

    results = []
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames or [])
            
            # Prepare output fields
            out_fields = ["category", "priority", "reason", "flag"]
            for field in out_fields:
                if field not in fieldnames:
                    fieldnames.append(field)

            for row in reader:
                try:
                    # classify_complaint is resilient
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    logging.error(f"row_processing_error: {e}")
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = "Processing crashed."
                    row["flag"] = "NEEDS_REVIEW"
                
                results.append(row)
                if HAS_GENAI and os.environ.get("GEMINI_API_KEY"):
                    time.sleep(1) # simple rate limit for API

        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
         logging.error(f"invalid_file: file read or processing error -> {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    if HAS_GENAI and not os.environ.get("GEMINI_API_KEY"):
        logging.warning("GEMINI_API_KEY not found. Running in local programmatic fallback mode.")
        
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
