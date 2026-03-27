import argparse
import csv
import json
import os
import time
import google.generativeai as genai

# Prepare the environment; expects GEMINI_API_KEY environment variable.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Standard capability model
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
ROLE:
You are a rigorous citizen complaint classifier. Your operational boundary is to analyze raw complaint text and assign standardized categories, priorities, and justifications for each record.

INTENT:
Produce verifiable classifications where every output strictly maps to allowed categories, accurately identifies urgent severities based on specific keywords, and justifies decisions using exact words from the input text.

CONTEXT:
You must only use the text provided in the complaint description. You must not hallucinate sub-categories, assume details not explicitly stated, or use information outside the provided text.

ENFORCEMENT RULES:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations.
- Priority must be one of: Urgent, Standard, Low. It must be Urgent if any of these severity keywords are present: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- Reason must be exactly one sentence and must cite specific words from the description.
- Flag must be NEEDS_REVIEW if the category is genuinely ambiguous; otherwise, it must be blank. Do not exhibit false confidence on ambiguity.
"""

def classify_complaint(description: str) -> dict:
    """
    Skill: classify_complaint
    Processes a single citizen complaint to output an exact category, a priority level, 
    a justified reason, and an optional review flag.
    Includes error handling for ambiguous inputs or invalid API responses.
    """
    if not description or not description.strip():
        # Handle entirely missing description via error_handling approach
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Input description was empty or totally ambiguous.",
            "flag": "NEEDS_REVIEW"
        }

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = f"""
        Classify the following citizen complaint strictly adhering to your enforcement rules.
        Output exactly a JSON object with the following string keys:
        - "category"
        - "priority"
        - "reason"
        - "flag"

        Complaint Description:
        {description}
        """
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        category = result.get("category", "Other")
        priority = result.get("priority", "Standard")
        reason = result.get("reason", "No reason provided.")
        flag = result.get("flag", "")
        
        # Enforce exact allowed categories directly (secondary guardrail)
        valid_categories = [
            "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
            "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
        ]
        
        if category not in valid_categories:
            category = "Other"
            flag = "NEEDS_REVIEW"
            
        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
    except Exception as e:
        # Error handling as defined in skills.md: emit valid schema with NEEDS_REVIEW flag
        return {
            "category": "Other",
            "priority": "Low",
            "reason": f"Classification failed: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_csv: str, output_csv: str):
    """
    Skill: batch_classify
    Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, 
    and writes the results to an output CSV. Continues processing despite malformed rows.
    """
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' does not exist.")
        return

    # Ensure output directory exists before writing
    out_dir = os.path.dirname(output_csv)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("Error: Empty or invalid input CSV.")
            return
            
        # Dynamically determine the likely description column
        desc_col = None
        for col in fieldnames:
            if col.lower() in ('description', 'text', 'complaint', 'incident', 'issue'):
                desc_col = col
                break
        
        if not desc_col and len(fieldnames) > 0:
            desc_col = fieldnames[0]

        # Prepare writing headers - strip old priority/category if they exist, maintain others
        out_fieldnames = [f for f in fieldnames if f not in ('category', 'priority_flag', 'priority', 'reason', 'flag')]
        out_fieldnames.extend(['category', 'priority', 'reason', 'flag'])
        
        rows = list(reader)

    print(f"Starting batch classification of {len(rows)} complaints...")

    with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()

        for idx, row in enumerate(rows):
            description = row.get(desc_col, "")
            print(f"[{idx+1}/{len(rows)}] Classifying: {description[:50]}...")
            
            classification = classify_complaint(description)
            
            # Filter output dict to match fieldnames mappings
            out_row = {k: row[k] for k in row if k in out_fieldnames}
            out_row.update(classification)
            writer.writerow(out_row)
            
            # Respectfully await next cycle to avoid rapid API depletion
            time.sleep(1)
            
    print(f"Batch classification complete. Results successfully saved to: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Citizen Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
