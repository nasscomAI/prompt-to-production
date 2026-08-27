"""
UC-0A — Complaint Classifier
Implementation powered by the RICE strategy defined in agents.md and skills.md.
"""
import argparse
import csv
import json
import os

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

def _process_single_row(row: dict) -> dict:
    """
    Internal helper to execute the agents.md RICE prompt classification on a single row.
    """
    description = row.get("description", "")
    
    system_prompt = """role: >
      You are an expert citizen complaint classifier. Your operational boundary is strictly processing rows of civic complaint data, analyzing their descriptions, and assigning appropriate structured metadata for department routing and triage prioritization.

    intent: >
      A correct output must strictly classify each complaint row with an exact allowed category, priority level, a one-sentence reason citing specific words from the description, and an optional review flag. The output must not contain hallucinated values or unvalidated schemas.

    context: >
      You act upon the provided citizen complaint text data. You must evaluate this text against predefined schema rules. Do not use outside knowledge to infer severity unstated in the text.

    enforcement:
      - "The category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
      - "The priority must be exactly one of: Urgent, Standard, Low."
      - "The priority MUST be Urgent if the description contains any of these exact severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
      - "The reason field must be exactly one sentence and must cite specific words from the description."
      - "The flag must be NEEDS_REVIEW if the category is genuinely ambiguous; otherwise leave it blank."
      
    Output your result purely as a JSON object with keys: "category", "priority", "reason", "flag".
    """

    if HAS_LLM and os.environ.get("OPENAI_API_KEY"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this citizen complaint:\\n\\nDescription: {description}"}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            pass # Fallback to rule-based engine on API error

    # Fallback to rule-based mapping
    desc_lower = description.lower()
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    if "pothole" in desc_lower: category, flag = "Pothole", ""
    elif "flood" in desc_lower or "water" in desc_lower: category, flag = "Flooding", ""
    elif "light" in desc_lower: category, flag = "Streetlight", ""
    elif "waste" in desc_lower or "garbage" in desc_lower: category, flag = "Waste", ""
    elif "noise" in desc_lower or "loud" in desc_lower: category, flag = "Noise", ""
    elif "road" in desc_lower and "damage" in desc_lower: category, flag = "Road Damage", ""
    elif "drain" in desc_lower or "block" in desc_lower: category, flag = "Drain Blockage", ""

    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    has_urgent = any(kw in desc_lower for kw in urgent_keywords)
    priority = "Urgent" if has_urgent else "Standard"

    reason_words = [kw for kw in urgent_keywords if kw in desc_lower]
    if reason_words:
        reason = f"The description contains '{reason_words[0]}'."
    else:
        reason = f"The description pertains to {category.lower()}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_complaint(input_path: str, output_path: str):
    """
    Classify logic applied directly taking CSV files as requested in skills.md
    """
    batch_classify(input_path, output_path)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV robustly (skills.md)
    """
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)
        
        fieldnames = list(reader.fieldnames or [])
        for new_field in ['category', 'priority', 'reason', 'flag']:
            if new_field not in fieldnames:
                fieldnames.append(new_field)

    results = []
    # Process rows gracefully as dictated by skills.md error_handling
    for i, row in enumerate(rows):
        try:
            classified_data = _process_single_row(row)
            row.update(classified_data)
        except Exception as e:
            print(f"Error classifying row {i+1}: {e}")
            row.update({
                'category': 'Other',
                'priority': 'Standard',
                'reason': 'Extraction error during processing.',
                'flag': 'NEEDS_REVIEW'
            })
        results.append(row)

    with open(output_path, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    classify_complaint(args.input, args.output)
    print(f"Done. Classified records written to {args.output}")
