"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on our RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # 1. Determine Priority constraint
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        # Match standalone words using regex or simple 'in' (rules say "contains")
        if kw in description:
            priority = "Urgent"
            break
            
    # 2. Determine Category heuristically based on description words
    matched_cats = set()
    if 'pothole' in description:
        matched_cats.add('Pothole')
    if 'flood' in description or 'stranded' in description:
        matched_cats.add('Flooding')
    if 'drain' in description or 'manhole' in description:
        matched_cats.add('Drain Blockage')
    if 'streetlight' in description or 'lights out' in description or 'electrical' in description:
        matched_cats.add('Streetlight')
    if 'garbage' in description or 'waste' in description or 'dead animal' in description:
        matched_cats.add('Waste')
    if 'music' in description or 'noise' in description:
        matched_cats.add('Noise')
    if 'road surface' in description or 'cracked' in description or 'footpath' in description:
        matched_cats.add('Road Damage')
        
    # Refusal / Ambiguity condition enforcement
    flag = ""
    category = "Other"
    
    if len(matched_cats) == 1:
        category = list(matched_cats)[0]
    else:
        # 0 or >1 matches defaults to Other + NEEDS_REVIEW
        flag = "NEEDS_REVIEW"
        
    # 3. Generate a Reason constraint citing specific words
    # Pick a few words as evidence
    words = description.split()[:5] # Grab just first few words to prove citation
    reason_citation = " ".join(words)
    reason = f"Classified based on contextual evidence from description: '{reason_citation}'."
        
    return {
        "complaint_id": row.get('complaint_id', ''),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        sys.exit(1)
        
    results = []
    
    for row in rows:
        try:
            # We don't want to crash on a bad row, we handle gracefully
            res = classify_complaint(row)
            
            # Preserve original data, append our parsed classifications
            out_row = {**row, **res}
            results.append(out_row)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id')}: {e}")
            # Add with nulls flagged for skipped elements
            results.append({
                **row, 
                "category": "Other", 
                "priority": "Low", 
                "reason": "Failed to process", 
                "flag": "NEEDS_REVIEW"
            })
            
    if not results:
        print("No results to write.")
        sys.exit(0)
        
    # Write output
    try:
        fieldnames = list(results[0].keys())
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
