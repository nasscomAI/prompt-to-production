import argparse
import csv
import json
import os
import sys

try:
    import openai
except ImportError:
    openai = None

SYSTEM_PROMPT = """
role: >
  You are a citizen complaint classifier for municipal data. Your operational boundary is to read unclassified complaint descriptions from a CSV and append strict, standardized classification fields to each row.

intent: >
  Produce an output JSON where the input description is mapped to exactly one allowed category, correctly identifies priority based on severity keywords, includes a one-sentence reason citing specific words from the description, and flags ambiguous cases for review.

context: >
  You are allowed to use only the provided complaint description text to make your classification. You must use the strict list of allowed categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. You must use the strict list of severity keywords to trigger Urgent priority: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations."
  - "Priority must be Urgent if description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be Standard or Low."
  - "Every output row must include a 'reason' field containing exactly one sentence that cites specific words from the original description."
  - "If the category is genuinely ambiguous and cannot be confidently determined, set 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'. Otherwise, leave flag empty."

OUTPUT FORMAT:
Return ONLY valid JSON. Do not include markdown formatting.
Keys required: "category", "priority", "reason", "flag".
"""

def classify_complaint_llm(description: str) -> dict:
    """
    Calls the OpenAI API using the strict RICE prompt defined in agents.md.
    """
    if not openai:
        raise RuntimeError("openai package not installed. Run: pip install openai")
        
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this description:\n{description}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    return json.loads(response.choices[0].message.content)


def classify_complaint_heuristic(description: str) -> dict:
    """
    Fallback deterministic classifier that applies the RICE rules strictly.
    Used if OPENAI_API_KEY is not configured.
    """
    desc = description.lower()
    
    # Priority enforcement
    severity_kws = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severe = [kw for kw in severity_kws if kw in desc]
    priority = "Urgent" if found_severe else "Standard"
    
    # Category enforcement
    categories = []
    if 'pothole' in desc or 'crater' in desc: categories.append("Pothole")
    if 'flood' in desc or 'water' in desc: categories.append("Flooding")
    if 'light' in desc or 'lamp' in desc or 'dark' in desc: categories.append("Streetlight")
    if 'waste' in desc or 'garbage' in desc or 'smell' in desc or 'animal' in desc: categories.append("Waste")
    if 'noise' in desc or 'music' in desc: categories.append("Noise")
    if ('road' in desc or 'crack' in desc or 'footpath' in desc) and 'pothole' not in desc: categories.append("Road Damage")
    if 'heritage' in desc or 'monument' in desc: categories.append("Heritage Damage")
    if 'heat' in desc or 'hot' in desc: categories.append("Heat Hazard")
    if 'drain' in desc or 'block' in desc or 'manhole' in desc: categories.append("Drain Blockage")
    
    if len(categories) == 1:
        category = categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason enforcement
    reason_word = found_severe[0] if found_severe else (categories[0] if len(categories) == 1 else "ambiguous terms")
    reason = f"The description contains '{reason_word}' which determines the classification."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_complaint(row: dict, use_llm: bool = False) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    
    if not description:
        row.update({"category": "Other", "priority": "Standard", "reason": "No description provided.", "flag": "NEEDS_REVIEW"})
        return row

    if use_llm:
        try:
            result = classify_complaint_llm(description)
        except Exception as e:
            print(f"  [!] LLM classification failed for ID {row.get('complaint_id', '')}: {e}")
            print("  [!] Falling back to heuristic classifier...")
            result = classify_complaint_heuristic(description)
    else:
        result = classify_complaint_heuristic(description)
        
    # Append the results to the original row
    row['category'] = result.get('category', 'Other')
    row['priority'] = result.get('priority', 'Standard')
    row['reason'] = result.get('reason', '')
    row['flag'] = result.get('flag', '')
    
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    use_llm = bool(os.getenv("OPENAI_API_KEY") and openai)
    if use_llm:
        print("OPENAI_API_KEY detected. Using LLM for classification.")
    else:
        print("No OPENAI_API_KEY detected or openai package missing. Using deterministic heuristic classifier.")

    rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no headers or is empty.")
                
            out_fieldnames = list(reader.fieldnames) + ['category', 'priority', 'reason', 'flag']
            # Remove any duplicate columns if they already existed
            out_fieldnames = list(dict.fromkeys(out_fieldnames))
            
            for i, row in enumerate(reader, 1):
                print(f"Classifying row {i} (ID: {row.get('complaint_id', 'N/A')})...")
                try:
                    classified_row = classify_complaint(row, use_llm=use_llm)
                    rows.append(classified_row)
                except Exception as e:
                    print(f"  [!] Unhandled error on row {i}: {e}")
                    row['category'] = 'Other'
                    row['priority'] = 'Standard'
                    row['reason'] = 'Critical error during processing.'
                    row['flag'] = 'NEEDS_REVIEW'
                    rows.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    # Write to output CSV
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"\nDone. Successfully classified {len(rows)} rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
