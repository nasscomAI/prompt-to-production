"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import os
import json
import re
from google import genai
from google.genai import types



# ==========================================
# CONSTANTS & SCHEMA ENFORCEMENT
# ==========================================

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse"
]

# ==========================================
# SKILL 1: classify_complaint
# ==========================================
def classify_complaint(description, client):
    """
    Evaluates a single citizen complaint to assign a strict category, 
    priority, justification, and review flag.
    """
    system_prompt = f"""
    ROLE: You are a Complaint Classifier agent responsible for evaluating citizen complaints to assign a strict category, priority, justification, and review flag.

    INTENT: Process each complaint to output a verifiable classification with exactly four fields (category, priority, reason, flag) that completely adheres to the allowed values and logic rules.

    CONTEXT: Rely exclusively on the provided complaint descriptions from the input file. Do not reference external classifications, invent sub-categories, or assume severity without the presence of specific keywords.

    ENFORCEMENT RULES (CRITICAL):
    1. CATEGORY: Must be an exact string match to one of: {", ".join(ALLOWED_CATEGORIES)}. No variations or hallucinated sub-categories. If it does not fit perfectly, use 'Other'.
    2. PRIORITY: Must be exactly one of: {", ".join(ALLOWED_PRIORITIES)}.
    3. PRIORITY RULE: Must be set to 'Urgent' if ANY of these severity keywords are present: {", ".join(SEVERITY_KEYWORDS)}.
    4. REASON: Must be exactly one sentence.
    5. REASON RULE: Must explicitly cite specific words from the complaint description in quotes.
    6. FLAG: Must be exactly 'NEEDS_REVIEW' or an empty string ''.
    7. FLAG RULE: Set to 'NEEDS_REVIEW' when the category is genuinely ambiguous. Do not exhibit false confidence.

    Respond STRICTLY in JSON format matching this schema:
    {{"category": "string", "priority": "string", "reason": "string", "flag": "string"}}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Complaint Description: {description}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0, # Zero temperature is required for strict rule adherence
                response_mime_type="application/json",
            )
        )
        
        result = json.loads(response.text)
        
        # --- ERROR HANDLING & ENFORCEMENT OVERRIDES (Defense in Depth) ---
        
        # 1. Prevent Taxonomy Drift / Hallucinated sub-categories
        if result.get("category") not in ALLOWED_CATEGORIES:
            result["category"] = "Other"
            
        # 2. Prevent Severity Blindness (Force Urgent if keywords present)
        desc_lower = description.lower()
        has_severity_keyword = any(re.search(rf'\b{kw}\b', desc_lower) for kw in SEVERITY_KEYWORDS)
        if has_severity_keyword and result.get("priority") != "Urgent":
            result["priority"] = "Urgent"
            
        # 3. Sanitize Priority just in case
        if result.get("priority") not in ALLOWED_PRIORITIES:
             result["priority"] = "Standard" # Safe fallback
             
        # 4. Enforce Flag allowed values
        if result.get("flag") not in ["NEEDS_REVIEW", ""]:
            result["flag"] = "NEEDS_REVIEW"

        return result

    except Exception as e:
        print(f"Warning [classify_complaint]: LLM parsing failed. Applying fallback. Error: {e}", file=sys.stderr)
        # Error Handling: Map entirely malformed/failed outputs to NEEDS_REVIEW
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "",
            "flag": "NEEDS_REVIEW"
        }

# ==========================================
# SKILL 2: batch_classify
# ==========================================
def batch_classify(input_csv, output_csv):
    """
    Reads an input CSV file, applies the classify_complaint skill to each row, 
    and writes the results to an output CSV.
    """
    if not os.path.exists(input_csv):
        print(f"Error [batch_classify]: File '{input_csv}' cannot be read. Halting execution.", file=sys.stderr)
        sys.exit(1)

    if not os.environ.get("GEMINI_API_KEY"):
         print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
         sys.exit(1)
         
    client = genai.Client()
    processed_rows = []
    fieldnames = []

    try:
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            # Identify the column containing the complaint text
            # Usually 'description', 'complaint', 'text'. Adjust if your CSV differs.
            desc_col = next((col for col in fieldnames if col.lower() in ['description', 'complaint', 'text', 'issue']), None)
            
            if not desc_col:
                 # Fallback to the first column if naming is unusual
                 desc_col = fieldnames[0]

            for row_idx, row in enumerate(reader, start=1):
                description = row.get(desc_col, "").strip()
                
                print(f"Processing row {row_idx}...")
                
                if not description:
                    # Error Handling for Malformed Rows
                    classification = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classification = classify_complaint(description, client)
                
                # Merge original row data with new classification data
                processed_row = row.copy()
                processed_row["category"] = classification["category"]
                processed_row["priority"] = classification["priority"]
                processed_row["reason"] = classification["reason"]
                processed_row["flag"] = classification["flag"]
                
                processed_rows.append(processed_row)

    except Exception as e:
        print(f"Error [batch_classify]: Failed reading CSV. {e}", file=sys.stderr)
        sys.exit(1)

    # Output Management
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    
    # Ensure our 4 new fields are in the output headers
    output_fieldnames = list(fieldnames)
    for field in ["category", "priority", "reason", "flag"]:
        if field not in output_fieldnames:
            output_fieldnames.append(field)

    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
        print(f"\nSuccess! Batch classification complete. Results written to: {output_csv}")
    except Exception as e:
        print(f"Error [batch_classify]: Failed writing output CSV. {e}", file=sys.stderr)
        sys.exit(1)

# ==========================================
# MAIN CLI PIPELINE
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="UC-0A: Complaint Classifier Agent")
    parser.add_argument("--input", required=True, help="Path to the input complaints CSV")
    parser.add_argument("--output", required=True, help="Path to save the classified results CSV")
    args = parser.parse_args()

    print(f"Starting batch classification on: {args.input}")
    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()